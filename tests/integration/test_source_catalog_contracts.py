from __future__ import annotations

import json

import pytest
from httpx import AsyncClient

from app.core.types import JsonValue
from tests.integration.model_source_helpers import _create_model_source

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "instructions",
    [" \tПравила 日本語\r\n  Keep spacing.\n", "", " \t\r\n", None, True, 7, 1.5, [], {"text": "policy"}],
)
async def test_persisted_source_instructions_update_both_catalog_views(
    async_client: AsyncClient, instructions: JsonValue
) -> None:
    metadata: dict[str, JsonValue] = {
        "base_instructions": instructions,
        "multi_agent_version": "v99",
        "experimental_supported_tools": ["custom"],
        "supports_search_tool": True,
        "source_request_overrides": {"temperature": 0.1},
    }
    source_id = await _create_model_source(
        async_client,
        name="stored-policy",
        model="policy-source-model",
        base_url="http://127.0.0.1:9/v1",
        supports_responses=True,
        raw_metadata_json=json.dumps(metadata),
    )

    async def check_catalogs(expected: str) -> None:
        for path in ("/backend-api/codex/models", "/v1/models?client_version=0.159.3"):
            response = await async_client.get(path, follow_redirects=False)
            assert response.status_code == 200, response.text
            entry = next(item for item in response.json()["models"] if item["slug"] == "policy-source-model")
            assert entry["base_instructions"] == expected
            for key in ("multi_agent_version", "experimental_supported_tools", "supports_search_tool"):
                assert entry[key] == metadata[key]
            assert "source_request_overrides" not in entry
            assert "token-stored-policy" not in response.text

    await check_catalogs(instructions if isinstance(instructions, str) else "")
    latest = "\n Updated политика 日本語.\t\r\n"
    metadata["base_instructions"] = latest
    update = await async_client.patch(
        f"/api/model-sources/{source_id}",
        json={
            "models": [
                {
                    "model": "policy-source-model",
                    "supportsTools": True,
                    "maxOutputTokens": 1024,
                    "rawMetadataJson": json.dumps(metadata),
                }
            ]
        },
    )
    assert update.status_code == 200, update.text
    stored = await async_client.get("/api/model-sources/")
    assert stored.status_code == 200
    source = next(item for item in stored.json()["sources"] if item["id"] == source_id)
    assert json.loads(source["models"][0]["rawMetadataJson"]) == metadata
    await check_catalogs(latest)
