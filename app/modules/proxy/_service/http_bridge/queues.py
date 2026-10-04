from __future__ import annotations

import asyncio
import collections
from typing import Callable

# Limits for the HTTP bridge stream event queue
_HTTP_BRIDGE_STREAM_QUEUE_LIMIT = 4096
_HTTP_BRIDGE_STREAM_QUEUE_BYTES_LIMIT = 32 * 1024 * 1024  # 32 MiB
_HTTP_BRIDGE_DOWNSTREAM_STALL_TIMEOUT_SECONDS = 5.0


def _http_bridge_event_payload_size(item: object) -> int:
    """Queued payload bytes of one HTTP bridge event (UTF-8 bytes)."""
    if isinstance(item, str):
        return len(item.encode("utf-8"))
    return 0


class _HTTPBridgeEventQueue(asyncio.Queue[str | None]):
    """``asyncio.Queue`` bounded by both an event cap and a queued-bytes budget.

    Items are either SSE text blocks (``str``) or terminal sentinels (``None``).
    A zero-byte item (such as ``None``) is always accepted if the event cap has room.
    An event arriving at an empty queue is always accepted so a lone large chunk never fails.
    """

    _putters: collections.deque[asyncio.Future[None]]
    _getters: collections.deque[asyncio.Future[None]]
    _wakeup_next: Callable[[collections.deque[asyncio.Future[None]]], None]

    def __init__(
        self,
        *,
        max_events: int = _HTTP_BRIDGE_STREAM_QUEUE_LIMIT,
        max_bytes: int = _HTTP_BRIDGE_STREAM_QUEUE_BYTES_LIMIT,
    ) -> None:
        super().__init__(maxsize=max_events)
        self._max_bytes = max_bytes
        self.queued_bytes = 0
        self._closed = False
        self._failure_event: str | None = None

    def put_nowait(self, item: str | None) -> None:
        if self._closed:
            raise asyncio.QueueShutDown
        size = _http_bridge_event_payload_size(item)
        if size and not self.empty() and self.queued_bytes + size > self._max_bytes:
            raise asyncio.QueueFull
        super().put_nowait(item)

    async def put(self, item: str | None) -> None:
        size = _http_bridge_event_payload_size(item)
        while (self.maxsize > 0 and self.qsize() >= self.maxsize) or (
            self._max_bytes > 0 and not self.empty() and size and self.queued_bytes + size > self._max_bytes
        ):
            if self._closed:
                raise asyncio.QueueShutDown
            loop = (
                getattr(self, "_loop", None) or getattr(self, "_get_loop", lambda: None)() or asyncio.get_running_loop()
            )
            getter = loop.create_future()
            self._putters.append(getter)
            try:
                await getter
            except BaseException:
                getter.cancel()
                try:
                    self._putters.remove(getter)
                except ValueError:
                    pass
                if not self.full() and not getter.cancelled():
                    self._wakeup_next(self._putters)
                raise
            if self._closed:
                raise asyncio.QueueShutDown
            if self._putters and (
                (self.maxsize > 0 and self.qsize() >= self.maxsize)
                or (self._max_bytes > 0 and not self.empty() and size and self.queued_bytes + size > self._max_bytes)
            ):
                self._wakeup_next(self._putters)
        return self.put_nowait(item)

    def _put(self, item: str | None) -> None:
        super()._put(item)
        self.queued_bytes += _http_bridge_event_payload_size(item)

    def _get(self) -> str | None:
        item = super()._get()
        self.queued_bytes -= _http_bridge_event_payload_size(item)
        return item

    async def get(self) -> str | None:
        try:
            return await super().get()
        except asyncio.QueueShutDown:
            failure_event = self._failure_event
            self._failure_event = None
            return failure_event

    def fail(self, event: str) -> None:
        """Retain accepted output, then deliver one bounded failure terminal."""
        if self._closed:
            return
        self._closed = True
        self._failure_event = event
        self.shutdown(immediate=False)

    def finish(self) -> None:
        """End after accepted output without a producer waiting on a sentinel."""
        self._closed = True
        self.shutdown(immediate=False)

    def close(self) -> None:
        """Release detached output and wake producers without reader cancellation."""
        self._closed = True
        self._failure_event = None
        self.shutdown(immediate=True)


def _new_http_bridge_event_queue(
    *,
    max_events: int = _HTTP_BRIDGE_STREAM_QUEUE_LIMIT,
    max_bytes: int = _HTTP_BRIDGE_STREAM_QUEUE_BYTES_LIMIT,
) -> _HTTPBridgeEventQueue:
    return _HTTPBridgeEventQueue(max_events=max_events, max_bytes=max_bytes)
