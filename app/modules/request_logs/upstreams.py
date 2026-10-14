from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ModelSource, RequestLog
from app.modules.request_logs.schemas import RequestLogUpstreamOption

SUBSCRIPTION_POOL = "subscription_pool"


async def resolve_upstream_options(
    session: AsyncSession, source_ids: list[str], *, has_subscription: bool
) -> list[RequestLogUpstreamOption]:
    options = [RequestLogUpstreamOption(id=SUBSCRIPTION_POOL, type="subscription_pool")] if has_subscription else []
    sources = (
        (
            await session.execute(
                select(ModelSource.id, ModelSource.name, ModelSource.kind).where(ModelSource.id.in_(source_ids))
            )
        ).all()
        if source_ids
        else []
    )
    current = {row.id: (row.name, row.kind) for row in sources}
    for source_id in source_ids:
        metadata = current.get(source_id)
        persisted_kind = None
        if metadata is None:
            persisted_kind = (
                await session.execute(
                    select(RequestLog.model_source_kind)
                    .where(RequestLog.model_source_id == source_id, RequestLog.deleted_at.is_(None))
                    .order_by(RequestLog.requested_at.desc(), RequestLog.id.desc())
                    .limit(1)
                )
            ).scalar_one_or_none()
        options.append(
            RequestLogUpstreamOption(
                id=source_id,
                type="model_source",
                display_name=metadata[0] if metadata else None,
                model_source_kind=metadata[1] if metadata else persisted_kind,
                is_deleted=metadata is None,
            )
        )
    return options
