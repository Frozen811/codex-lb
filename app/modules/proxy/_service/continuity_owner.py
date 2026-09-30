"""Continuity owner fallback resolution for previous_response_id lookup misses."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.api_keys.service import ApiKeyData
    from app.modules.proxy.load_balancer import LoadBalancer

logger = logging.getLogger(__name__)


async def resolve_continuity_owner_candidate(
    load_balancer: LoadBalancer,
    *,
    api_key: ApiKeyData | None = None,
) -> str | None:
    """Resolve a single continuity owner candidate on an owner-lookup miss.

    When previous_response_id owner lookup misses, single-account pools and
    scoped keys can unambiguously pin the only possible owner. If there are multiple
    candidates, zero candidates, or listing fails, returns None so callers fail closed.
    """
    try:
        candidates = await load_balancer.list_continuity_owner_candidates(api_key=api_key)
    except Exception:
        logger.warning("Failed to list continuity owner candidates on lookup miss", exc_info=True)
        return None
    if len(candidates) == 1:
        return candidates[0].id
    return None
