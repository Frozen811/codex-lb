from __future__ import annotations

import asyncio

# Limits for the HTTP bridge stream event queue
_HTTP_BRIDGE_STREAM_QUEUE_LIMIT = 4096
_HTTP_BRIDGE_STREAM_QUEUE_BYTES_LIMIT = 32 * 1024 * 1024  # 32 MiB


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

    def put_nowait(self, item: str | None) -> None:
        if self._closed:
            raise asyncio.CancelledError("HTTP bridge event queue is closed")
        size = _http_bridge_event_payload_size(item)
        if size and not self.empty() and self.queued_bytes + size > self._max_bytes:
            raise asyncio.QueueFull
        super().put_nowait(item)

    async def put(self, item: str | None) -> None:
        size = _http_bridge_event_payload_size(item)
        while (
            (self._maxsize > 0 and self.qsize() >= self._maxsize)
            or (self._max_bytes > 0 and not self.empty() and size and self.queued_bytes + size > self._max_bytes)
        ):
            if self._closed:
                raise asyncio.CancelledError("HTTP bridge event queue is closed")
            loop = (
                getattr(self, "_loop", None)
                or getattr(self, "_get_loop", lambda: None)()
                or asyncio.get_running_loop()
            )
            getter = loop.create_future()
            self._putters.append(getter)
            try:
                await getter
            except Exception:
                self._clean_up_cancelled_putter(getter)
                raise
            if self._putters and (
                (self._maxsize > 0 and self.qsize() >= self._maxsize)
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

    def close(self) -> None:
        """Cancel any waiting putters and getters when the queue is detached/closed."""
        self._closed = True
        for putter in list(self._putters):
            if not putter.done():
                putter.cancel()
        for getter in list(self._getters):
            if not getter.done():
                getter.cancel()


def _new_http_bridge_event_queue(
    *,
    max_events: int = _HTTP_BRIDGE_STREAM_QUEUE_LIMIT,
    max_bytes: int = _HTTP_BRIDGE_STREAM_QUEUE_BYTES_LIMIT,
) -> _HTTPBridgeEventQueue:
    return _HTTPBridgeEventQueue(max_events=max_events, max_bytes=max_bytes)
