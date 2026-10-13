"""Bounded discovery of inference-authenticated Codex model catalogs."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import cast

import aiohttp
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import select, update
from sqlalchemy.engine import CursorResult

from app.core.clients.codex_version import get_codex_version_cache
from app.core.clients.http import lease_model_source_session
from app.core.crypto import TokenEncryptor
from app.db.models import ModelSource, ModelSourceModel
from app.db.session import detach_session_objects, get_background_session
from app.modules.model_sources.repository import ModelSourcesRepository

logger = logging.getLogger(__name__)
_MAX_BODY_BYTES = 1_048_576
_REFRESH_SECONDS = 5.0


class CatalogReasoningLevel(BaseModel):
    model_config = ConfigDict(strict=True)
    effort: str = Field(min_length=1, max_length=64)
    description: str | None = Field(default=None, max_length=4096)


class CatalogModel(BaseModel):
    model_config = ConfigDict(strict=True)
    slug: str = Field(min_length=1, max_length=255, pattern=r"^\S+$")
    display_name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=4096)
    context_window: int = Field(gt=0, le=2**31 - 1)
    max_tokens: int | None = Field(default=None, gt=0, le=2**31 - 1)
    input_modalities: list[str] = Field(default_factory=lambda: ["text"], max_length=16)
    supports_parallel_tool_calls: bool = False
    supported_reasoning_levels: list[CatalogReasoningLevel] = Field(default_factory=list, max_length=32)
    default_reasoning_level: str | None = Field(default=None, max_length=64)
    supports_reasoning_summaries: bool = False

    def apply(self, row: ModelSourceModel) -> None:
        row.display_name = self.display_name
        row.context_window = self.context_window
        row.max_output_tokens = self.max_tokens
        row.supports_streaming = True
        row.supports_tools = self.supports_parallel_tool_calls
        row.supports_vision = "image" in self.input_modalities
        metadata = self.model_dump(mode="json", exclude_none=True)
        metadata["supports_reasoning"] = bool(self.supported_reasoning_levels) or self.supports_reasoning_summaries
        row.raw_metadata_json = json.dumps(metadata, separators=(",", ":"))
        row.is_available = True


class SourceCatalog(BaseModel):
    model_config = ConfigDict(strict=True)
    models: list[CatalogModel] = Field(max_length=1000)

    @model_validator(mode="after")
    def unique_models(self) -> SourceCatalog:
        if len({model.slug for model in self.models}) != len(self.models):
            raise ValueError("Duplicate catalog identity")
        return self


async def _claim_source(source_id: str) -> ModelSource | None:
    async with get_background_session() as session:
        source = await ModelSourcesRepository(session).get_by_id(source_id)
        if (
            source is None
            or not source.is_enabled
            or not source.supports_responses
            or source.catalog_mode != "cli_proxy_api"
        ):
            return None
        revision = source.catalog_revision
        claimed = await session.execute(
            update(ModelSource)
            .where(ModelSource.id == source_id, ModelSource.catalog_revision == revision)
            .values(catalog_revision=revision + 1)
            .execution_options(synchronize_session=False)
        )
        if cast(CursorResult, claimed).rowcount != 1:
            return None
        await session.refresh(source)
        detach_session_objects(session)
        await session.commit()
        return source


async def _apply_catalog(source: ModelSource, catalog: SourceCatalog) -> bool:
    async with get_background_session() as session:
        claimed = await session.execute(
            update(ModelSource)
            .where(
                ModelSource.id == source.id,
                ModelSource.catalog_revision == source.catalog_revision,
                ModelSource.catalog_mode == "cli_proxy_api",
                ModelSource.is_enabled.is_(True),
                ModelSource.supports_responses.is_(True),
            )
            .values(catalog_revision=ModelSource.catalog_revision + 1)
        )
        if cast(CursorResult, claimed).rowcount != 1:
            return False
        current = await ModelSourcesRepository(session).get_by_id(source.id)
        assert current is not None
        existing = {model.model: model for model in current.models}
        for row in current.models:
            row.is_available = False
        for model in catalog.models:
            row = existing.get(model.slug)
            if row is None:
                row = ModelSourceModel(source_id=source.id, model=model.slug, is_enabled=True)
                session.add(row)
            model.apply(row)
        await session.commit()
        return True


async def refresh_source_catalog(source_id: str) -> None:
    try:
        source = await _claim_source(source_id)
        if source is None:
            return
        headers = {"Accept": "application/json"}
        if source.api_key_encrypted is not None:
            headers["Authorization"] = f"Bearer {TokenEncryptor().decrypt(source.api_key_encrypted)}"
        version = get_codex_version_cache().cached_version_or_default()
        async with lease_model_source_session() as client:
            async with client.get(
                f"{source.base_url}/models",
                params={"client_version": version},
                headers=headers,
                allow_redirects=False,
                timeout=aiohttp.ClientTimeout(total=_REFRESH_SECONDS),
            ) as response:
                if response.status != 200:
                    raise ValueError("Catalog status")
                body = bytearray()
                async for chunk in response.content.iter_chunked(65536):
                    body.extend(chunk)
                    if len(body) > _MAX_BODY_BYTES:
                        raise ValueError("Catalog bound")
                catalog = SourceCatalog.model_validate_json(bytes(body))
        await _apply_catalog(source, catalog)
    except Exception:
        # Never emit credentials, URL, response bodies or validation inputs.
        logger.warning("Source catalog refresh failed source_id=%s", source_id)


async def refresh_source_catalogs() -> None:
    async with get_background_session() as session:
        result = await session.execute(
            select(ModelSource.id).where(ModelSource.catalog_mode == "cli_proxy_api", ModelSource.is_enabled.is_(True))
        )
        source_ids = iter(result.scalars().all())

    async def worker() -> None:
        for source_id in source_ids:
            await refresh_source_catalog(source_id)

    try:
        async with asyncio.timeout(_REFRESH_SECONDS):
            async with asyncio.TaskGroup() as group:
                for _ in range(4):
                    group.create_task(worker())
    except TimeoutError:
        logger.warning("Source catalog refresh budget exhausted")
