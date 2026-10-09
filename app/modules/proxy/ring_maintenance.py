from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

from app.core.clock import Scheduler

logger = logging.getLogger(__name__)


async def run_ring_maintenance_phase(
    operation: Callable[[], Awaitable[None]],
    *,
    stop: asyncio.Event,
    interval_seconds: float,
    phase: str,
    scheduler: Scheduler,
) -> None:
    """One cooperative owner per optional phase, independent of ring renewal.

    A slow invocation stays owned and cannot overlap another pass. Ordinary
    failures retry after the cadence; stopping wakes an idle owner immediately.
    The lifespan owns this task and drains it before database disposal.
    """
    while not stop.is_set():
        try:
            await operation()
        except Exception:
            logger.warning("HTTP bridge maintenance failed phase=%s", phase, exc_info=True)
        if stop.is_set():
            return
        try:
            await scheduler.wait_for(stop.wait(), timeout=interval_seconds)
        except TimeoutError:
            continue
