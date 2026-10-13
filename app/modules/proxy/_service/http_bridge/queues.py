from __future__ import annotations

import asyncio
import collections
import weakref
from dataclasses import dataclass
from typing import Callable

# Limits for the HTTP bridge stream event queue
_HTTP_BRIDGE_STREAM_QUEUE_LIMIT = 4096
_HTTP_BRIDGE_STREAM_QUEUE_BYTES_LIMIT = 32 * 1024 * 1024  # 32 MiB
_HTTP_BRIDGE_STREAM_PROCESS_BYTES_LIMIT = 256 * 1024 * 1024
_HTTP_BRIDGE_DOWNSTREAM_STALL_TIMEOUT_SECONDS = 5.0


class _HTTPBridgePayloadBudgetExceeded(asyncio.QueueFull):
    """The process cannot retain another live downstream payload."""


@dataclass
class _HTTPBridgePayloadBudget:
    used_bytes: int = 0


_HTTP_BRIDGE_PAYLOAD_BUDGET = _HTTPBridgePayloadBudget()


@dataclass
class _HTTPBridgePayloadAccount:
    budget: _HTTPBridgePayloadBudget
    retained_bytes: int = 0

    def reserve(self, size: int) -> None:
        if self.budget.used_bytes + size > _HTTP_BRIDGE_STREAM_PROCESS_BYTES_LIMIT:
            raise _HTTPBridgePayloadBudgetExceeded
        self.budget.used_bytes += size
        self.retained_bytes += size

    def release(self, size: int) -> None:
        self.budget.used_bytes -= size
        self.retained_bytes -= size

    def clear(self) -> None:
        self.release(self.retained_bytes)


@dataclass(eq=False)
class _HTTPBridgePayloadReservation:
    account: _HTTPBridgePayloadAccount
    size: int
    released: bool = False

    def release(self) -> None:
        if not self.released:
            self.released = True
            self.account.release(self.size)


def _http_bridge_event_payload_size(item: object) -> int:
    """Queued payload bytes of one HTTP bridge event (UTF-8 bytes)."""
    if isinstance(item, str):
        return len(item.encode("utf-8"))
    return 0


class _HTTPBridgeEventQueue(asyncio.Queue[str | None]):
    """``asyncio.Queue`` bounded by both an event cap and a queued-bytes budget.

    Items are either SSE text blocks (``str``) or terminal sentinels (``None``).
    A zero-byte item (such as ``None``) is always accepted if the event cap has room.
    A lone large chunk can exceed the per-queue cap, but not the process budget.
    """

    _putters: collections.deque[asyncio.Future[None]]
    _getters: collections.deque[asyncio.Future[None]]
    _get_loop: Callable[[], asyncio.AbstractEventLoop]
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
        self._payload_account = _HTTPBridgePayloadAccount(_HTTP_BRIDGE_PAYLOAD_BUDGET)
        self._waiting_payloads: set[_HTTPBridgePayloadReservation] = set()
        # The finalizer owns only the account, so it does not keep this queue alive.
        weakref.finalize(self, self._payload_account.clear)

    def put_nowait(self, item: str | None) -> None:
        if self._closed:
            raise asyncio.QueueShutDown
        size = _http_bridge_event_payload_size(item)
        if size and not self.empty() and self.queued_bytes + size > self._max_bytes:
            raise asyncio.QueueFull
        super().put_nowait(item)

    async def put(self, item: str | None) -> None:
        if self._closed:
            raise asyncio.QueueShutDown
        size = _http_bridge_event_payload_size(item)
        self._payload_account.reserve(size)
        reservation = _HTTPBridgePayloadReservation(self._payload_account, size)
        self._waiting_payloads.add(reservation)
        try:
            while (self.maxsize > 0 and self.qsize() >= self.maxsize) or (
                self._max_bytes > 0 and not self.empty() and size and self.queued_bytes + size > self._max_bytes
            ):
                if self._closed:
                    raise asyncio.QueueShutDown
                loop = self._get_loop()
                waiter = loop.create_future()
                self._putters.append(waiter)
                try:
                    await waiter
                except BaseException:
                    waiter.cancel()
                    try:
                        self._putters.remove(waiter)
                    except ValueError:
                        pass
                    if not self.full() and not waiter.cancelled():
                        self._wakeup_next(self._putters)
                    raise
                if self._closed:
                    raise asyncio.QueueShutDown
                if self._putters and (
                    (self.maxsize > 0 and self.qsize() >= self.maxsize)
                    or (
                        self._max_bytes > 0 and not self.empty() and size and self.queued_bytes + size > self._max_bytes
                    )
                ):
                    self._wakeup_next(self._putters)
            # Transfer to queued ownership synchronously without double counting.
            reservation.release()
            self.put_nowait(item)
        finally:
            reservation.release()
            self._waiting_payloads.discard(reservation)

    def _put(self, item: str | None) -> None:
        self._payload_account.reserve(_http_bridge_event_payload_size(item))
        super()._put(item)
        self.queued_bytes += _http_bridge_event_payload_size(item)

    def _get(self) -> str | None:
        item = super()._get()
        size = _http_bridge_event_payload_size(item)
        self.queued_bytes -= size
        self._payload_account.release(size)
        return item

    def shutdown(self, immediate: bool = False) -> None:
        self._closed = True
        for reservation in self._waiting_payloads:
            reservation.release()
        super().shutdown(immediate=immediate)

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
