from __future__ import annotations

import asyncio
import base64
from typing import cast

import pytest

from app.core.clients import native_egress as native

pytestmark = pytest.mark.unit


class Helper:
    def __init__(self, events):
        self.events = events
        self.aborts = 0
        self.finishes = 0

    async def _send_command(self, process, generation, command):
        self.events.put_nowait({"type": "websocket_sent", "command_id": command["command_id"]})
        if command["type"] == "websocket_close":
            self.events.put_nowait({"type": "websocket_close", "code": 1000, "reason": ""})

    async def _abort_request(self, *args):
        self.aborts += 1

    async def _cancel_request(self, *args):
        pass

    def _finish_request(self, *args):
        self.finishes += 1


def socket(events):
    helper = Helper(events)
    ws = native.NativeEgressWebSocket(
        status=101,
        headers=(),
        client=cast(native.SubprocessNativeEgressClient, helper),
        process=cast(asyncio.subprocess.Process, object()),
        request_id="burst",
        generation=1,
        events=events,
    )
    return ws, helper


def event(kind, text):
    if kind == "binary":
        return {"type": "websocket_binary", "data": base64.b64encode(text.encode()).decode()}
    if kind == "interpreted":
        return {
            "type": "websocket_responses_text",
            "text": text,
            "event_type": "response.output_text.delta",
            "payload": {"delta": text},
            "payload_response_id": "resp_burst",
            "sequence_number": 1,
        }
    return {"type": "websocket_text", "text": text}


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["text", "binary", "interpreted"])
@pytest.mark.parametrize("count", [65, 256])
async def test_burst_keeps_fifo_and_ack_progress_before_consumer_receives(kind, count):
    events = asyncio.Queue()
    for index in range(count):
        events.put_nowait(event(kind, f"кадр-{index}"))
    ws, helper = socket(events)
    try:
        await asyncio.wait_for(ws.send_text("request"), timeout=1)
        assert helper.aborts == 0
        for index in range(count):
            frame = await asyncio.wait_for(ws.receive(), timeout=1)
            assert (frame.data.decode() if kind == "binary" else frame.text) == f"кадр-{index}"
        assert ws._queued_message_bytes == 0
    finally:
        await ws.close()
    assert helper.finishes == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["text", "binary", "interpreted"])
async def test_byte_overflow_retains_accepted_frames_and_finalizes_once(monkeypatch, kind):
    monkeypatch.setattr(native, "_NATIVE_WEBSOCKET_MESSAGE_QUEUE_BYTES_LIMIT", 8)
    events = asyncio.Queue()
    events.put_nowait(event(kind, "я" * 3))  # UTF-8 bytes, and interpreted payload has two copies.
    events.put_nowait(event(kind, "я" * 3))
    ws, helper = socket(events)
    await asyncio.wait_for(ws._pump_task, timeout=1)
    assert (await ws.receive()).kind in ("text", "binary")
    with pytest.raises(native.NativeEgressTransportError) as failure:
        await ws.receive()
    assert failure.value.failure_phase == "consumer_backpressure"
    assert helper.aborts == helper.finishes == 1
    assert ws._queued_message_bytes == 0
    await ws.close()
    assert helper.finishes == 1


@pytest.mark.asyncio
async def test_message_cap_is_finite_and_preserves_prior_frames(monkeypatch):
    monkeypatch.setattr(native, "_NATIVE_WEBSOCKET_MESSAGE_QUEUE_LIMIT", 4)
    events = asyncio.Queue()
    for index in range(5):
        events.put_nowait(event("text", str(index)))
    ws, helper = socket(events)
    await asyncio.wait_for(ws._pump_task, timeout=1)
    assert [(await ws.receive()).text for _ in range(4)] == ["0", "1", "2", "3"]
    with pytest.raises(native.NativeEgressTransportError):
        await ws.receive()
    assert helper.aborts == helper.finishes == 1


@pytest.mark.asyncio
async def test_overflow_fails_an_actual_pending_send(monkeypatch):
    monkeypatch.setattr(native, "_NATIVE_WEBSOCKET_MESSAGE_QUEUE_BYTES_LIMIT", 8)
    events = asyncio.Queue()
    events.put_nowait(event("text", "123456"))
    events.put_nowait(event("text", "123456"))
    ws, helper = socket(events)
    with pytest.raises(native.NativeEgressTransportError) as failure:
        await asyncio.wait_for(ws.send_text("request"), timeout=1)
    assert failure.value.failure_phase == "consumer_backpressure"
    assert ws._pending == {}
    await ws._pump_task
    assert helper.aborts == helper.finishes == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("terminal", ["reader_failure", "cancel"])
async def test_terminal_failure_releases_pending_sender(terminal):
    events = asyncio.Queue()
    ws, helper = socket(events)
    future = asyncio.get_running_loop().create_future()
    ws._pending["waiting"] = future
    if terminal == "cancel":
        await asyncio.sleep(0)
        ws._pump_task.cancel()
    else:
        events.put_nowait(native.NativeEgressTransportError("helper failed", failure_phase="helper_process"))
    await asyncio.gather(ws._pump_task, return_exceptions=True)
    with pytest.raises(native.NativeEgressTransportError):
        await future
    assert helper.finishes == 1
    await ws.close()


@pytest.mark.asyncio
async def test_lone_large_frame_is_accepted_and_drain_releases_byte_budget(monkeypatch):
    monkeypatch.setattr(native, "_NATIVE_WEBSOCKET_MESSAGE_QUEUE_BYTES_LIMIT", 8)
    events = asyncio.Queue()
    events.put_nowait(event("text", "x" * 100))
    ws, helper = socket(events)
    assert (await ws.receive()).text == "x" * 100
    events.put_nowait(event("text", "next"))
    assert (await ws.receive()).text == "next"
    assert ws._queued_message_bytes == 0
    await ws.close()
    assert helper.aborts == 0 and helper.finishes == 1
