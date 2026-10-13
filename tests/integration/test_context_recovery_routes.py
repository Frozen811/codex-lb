from __future__ import annotations

import asyncio
import json
from typing import cast

import pytest
import pytest_asyncio
from sqlalchemy import select

import app.modules.proxy.service as proxy_module
from app.core.clients.proxy_websocket import UpstreamWebSocketMessage
from app.core.types import JsonValue
from app.db.models import HttpBridgeOperationRecord, HttpBridgeSessionRecord
from app.db.session import SessionLocal
from app.dependencies import get_proxy_service_for_app
from app.modules.proxy.replay_safety import project_durable_transcript_for_account_neutral_fresh_replay
from tests.integration.test_http_responses_bridge import (
    _AcceptedOutputFreeCapacityErrorUpstreamWebSocket,
    _collect_sse_events,
    _FakeBridgeUpstreamWebSocket,
    _get_account,
    _import_account,
    _install_bridge_settings,
    _install_two_account_bridge_failover,
)

pytestmark = pytest.mark.integration


async def _flush_operations(service):
    async with SessionLocal() as session:
        operation_ids = (await session.scalars(select(HttpBridgeOperationRecord.operation_id))).all()
    for operation_id in operation_ids:
        await service._http_bridge_operation_event_batcher.flush_operation(operation_id=operation_id)


@pytest_asyncio.fixture
async def root_bridge(async_client, app_instance, monkeypatch):
    _install_bridge_settings(monkeypatch, enabled=True)
    account_id = await _import_account(async_client, "context-owner", "context-owner@example.com")
    owner = await _get_account(account_id)
    upstream = _FakeBridgeUpstreamWebSocket("resp_context")
    service = get_proxy_service_for_app(app_instance)

    async def ensure_fresh(self, account, *, force=False, timeout_seconds):
        return account

    async def connect(*args, **kwargs):
        return upstream

    monkeypatch.setattr(proxy_module.ProxyService, "_ensure_fresh_with_budget", ensure_fresh)
    monkeypatch.setattr(proxy_module, "connect_responses_websocket", connect)
    try:
        yield upstream, service, owner
    finally:
        async with service._http_bridge_lock:
            sessions = list(service._http_bridge_sessions.values())
            service._http_bridge_sessions.clear()
            service._http_bridge_turn_state_index.clear()
            service._http_bridge_previous_response_index.clear()
        for session in sessions:
            await service._close_http_bridge_session(session)


@pytest.mark.parametrize(
    "path", ["/backend-api/codex/responses", "/backend-api/codex/responses/", "/v1/responses", "/v1/responses/"]
)
async def test_root_and_child_are_durably_reconstructable_at_http_routes(async_client, root_bridge, path):
    upstream, service, owner = root_bridge
    headers = {"x-codex-session-id": "context-chain"}
    developer = {"role": "developer", "content": [{"type": "input_text", "text": "Remember key-17 = 34620."}]}
    first_input = [developer, {"role": "user", "content": "Remember the key."}]
    first = await _collect_sse_events(
        async_client,
        path,
        json_body={"model": "gpt-5.1", "instructions": "Follow the rules.", "input": first_input, "stream": True},
        headers=headers,
    )
    first_response_id = first[-1]["response"]["id"]
    second = await _collect_sse_events(
        async_client,
        path,
        json_body={
            "model": "gpt-5.1",
            "instructions": "Follow the rules.",
            "previous_response_id": first_response_id,
            "input": [{"role": "user", "content": "What was key-17?"}],
            "stream": True,
        },
        headers=headers,
    )
    await _flush_operations(service)
    frames = [json.loads(frame) for frame in upstream.sent_text]
    assert "codex_lb_operation_id" not in frames[0].get("client_metadata", {})
    assert frames[0]["input"] == first_input
    assert frames[0]["instructions"] == "Follow the rules."
    transcript = await service._durable_bridge.get_replayable_transcript(response_id=second[-1]["response"]["id"])
    assert transcript is not None and len(transcript) == 2
    assert transcript[0].operation.parent_response_id is None
    assert transcript[0].operation.account_id == owner.id
    assert transcript[1].operation.parent_response_id == first_response_id
    rebuilt = project_durable_transcript_for_account_neutral_fresh_replay(
        transcript,
        anchor_response_id=second[-1]["response"]["id"],
        current_payload={"model": "gpt-5.1", "input": [{"role": "user", "content": "Continue."}]},
    )
    assert rebuilt is not None
    rebuilt_input = rebuilt.payload["input"]
    assert isinstance(rebuilt_input, list) and rebuilt_input[0] == developer


@pytest.mark.parametrize("tool_type", ["function_call", "custom_tool_call"])
@pytest.mark.parametrize("echo_call", [False, True])
async def test_root_tool_output_reconstruction_contains_exactly_one_pair(
    async_client, root_bridge, tool_type, echo_call, monkeypatch
):
    upstream, service, _ = root_bridge
    call = {
        "type": tool_type,
        "id": "tool_item",
        "call_id": "call_context",
        "name": "check",
        "arguments" if tool_type == "function_call" else "input": "{}",
        "status": "completed",
    }
    original_send = upstream.send_text

    async def send_tool(text):
        if upstream.sent_text:
            return await original_send(text)
        upstream.sent_text.append(text)
        response_id = "resp_context_1"
        for event in [
            {"type": "response.created", "response": {"id": response_id, "status": "in_progress"}},
            {"type": "response.output_item.added", "output_index": 0, "item": {**call, "status": "in_progress"}},
            {"type": "response.output_item.done", "output_index": 0, "item": call},
            {"type": "response.completed", "response": {"id": response_id, "status": "completed", "output": [call]}},
        ]:
            await upstream._messages.put(UpstreamWebSocketMessage("text", text=json.dumps(event)))

    monkeypatch.setattr(upstream, "send_text", send_tool)
    headers = {"x-codex-session-id": "context-tool-chain"}
    root_input = [{"role": "developer", "content": "Keep these rules."}, {"role": "user", "content": "Check."}]
    first = await _collect_sse_events(
        async_client,
        "/v1/responses",
        json_body={"model": "gpt-5.1", "instructions": "", "input": root_input, "stream": True},
        headers=headers,
    )
    output = {"type": f"{tool_type}_output", "call_id": "call_context", "output": "done"}
    second_input = [*root_input, {**call, "id": "echoed_item"}, output] if echo_call else [output]
    second = await _collect_sse_events(
        async_client,
        "/v1/responses",
        json_body={
            "model": "gpt-5.1",
            "instructions": "",
            "previous_response_id": first[-1]["response"]["id"],
            "input": second_input,
            "stream": True,
        },
        headers=headers,
    )
    await _flush_operations(service)
    response_id = second[-1]["response"]["id"]
    transcript = await service._durable_bridge.get_replayable_transcript(response_id=response_id)
    assert transcript is not None and len(transcript) == 2
    rebuilt = project_durable_transcript_for_account_neutral_fresh_replay(
        transcript,
        anchor_response_id=response_id,
        current_payload={"model": "gpt-5.1", "input": [{"role": "user", "content": "Continue."}]},
    )
    assert rebuilt is not None
    rebuilt_input = rebuilt.payload["input"]
    assert isinstance(rebuilt_input, list) and all(isinstance(item, dict) for item in rebuilt_input)
    items = cast(list[dict[str, JsonValue]], rebuilt_input)
    assert sum(item.get("type") == tool_type for item in items) == 1
    assert sum(item.get("type") == f"{tool_type}_output" for item in items) == 1
    assert items[:2] == root_input
    assert next(item for item in items if item.get("type") == f"{tool_type}_output") == output


async def test_reconstruction_refuses_a_parent_from_another_key_scope(async_client, root_bridge):
    _, service, _ = root_bridge
    body = {"model": "gpt-5.1", "instructions": "", "input": "first", "stream": True}
    first = await _collect_sse_events(async_client, "/v1/responses", json_body=body)
    parent_id = first[-1]["response"]["id"]
    second = await _collect_sse_events(
        async_client, "/v1/responses", json_body={**body, "previous_response_id": parent_id, "input": "next"}
    )
    await _flush_operations(service)
    async with SessionLocal() as session:
        parent = await session.scalar(
            select(HttpBridgeOperationRecord).where(HttpBridgeOperationRecord.response_id == parent_id)
        )
        assert parent is not None
        other_session = HttpBridgeSessionRecord(
            id="foreign-scope-session",
            session_key_kind="session_header",
            session_key_value="foreign-scope",
            session_key_hash="a" * 64,
            api_key_scope="foreign-api-key",
        )
        session.add(other_session)
        await session.flush()
        parent.session_id = other_session.id
        await session.commit()
    assert await service._durable_bridge.get_replayable_transcript(response_id=second[-1]["response"]["id"]) is None


async def test_independent_identical_roots_do_not_replay_or_merge(async_client, root_bridge):
    upstream, service, _ = root_bridge
    body = {"model": "gpt-5.1", "instructions": "Return OK.", "input": "same prompt", "stream": True}
    for _ in range(2):
        await _collect_sse_events(async_client, "/v1/responses", json_body=body)
    await _flush_operations(service)
    async with SessionLocal() as session:
        operations = (await session.scalars(select(HttpBridgeOperationRecord))).all()
    assert len(upstream.sent_text) == len(operations) == 2
    assert len({operation.operation_id for operation in operations}) == 2
    assert all(operation.parent_response_id is None and operation.state == "completed" for operation in operations)


async def test_accepted_root_replay_keeps_a_complete_child_chain(async_client, root_bridge, monkeypatch):
    upstream, service, owner = root_bridge
    alternate_id = await _import_account(async_client, "context-alternate", "context-alternate@example.com")
    alternate = await _get_account(alternate_id)
    failing = _AcceptedOutputFreeCapacityErrorUpstreamWebSocket()
    connected, _ = _install_two_account_bridge_failover(
        monkeypatch, first_account=owner, second_account=alternate, upstreams=[failing, upstream]
    )
    body = {
        "model": "gpt-5.1",
        "instructions": "",
        "input": [{"role": "user", "content": "First."}],
        "prompt_cache_key": "accepted-root-chain",
        "stream": True,
    }
    first = await _collect_sse_events(async_client, "/v1/responses", json_body=body)
    assert first[-1]["type"] == "response.completed"
    assert connected == [owner.chatgpt_account_id, alternate.chatgpt_account_id]
    response_id = first[-1]["response"]["id"]
    await _flush_operations(service)
    root = await service._durable_bridge.get_replayable_transcript(response_id=response_id)
    assert root is not None and len(root) == 1
    assert root[0].operation.account_id == alternate.id
    second = await _collect_sse_events(
        async_client,
        "/v1/responses",
        json_body={**body, "previous_response_id": response_id, "input": [{"role": "user", "content": "Next."}]},
    )
    await _flush_operations(service)
    transcript = await service._durable_bridge.get_replayable_transcript(response_id=second[-1]["response"]["id"])
    assert transcript is not None and len(transcript) == 2
    assert transcript[0].operation.operation_id == root[0].operation.operation_id


@pytest.mark.parametrize("failure", ["owner-fenced", "exception"])
async def test_root_registration_refusal_does_not_dispatch(async_client, root_bridge, monkeypatch, failure):
    upstream, service, _ = root_bridge

    async def refuse(**kwargs):
        if failure == "exception":
            raise RuntimeError("persistence unavailable")
        return None

    monkeypatch.setattr(service._durable_bridge, "record_operation", refuse)
    response = await async_client.post(
        "/v1/responses", json={"model": "gpt-5.1", "instructions": "Return OK.", "input": "new root", "stream": True}
    )
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "bridge_continuity_persistence_failed"
    assert upstream.sent_text == []
    async with SessionLocal() as session:
        assert (await session.scalars(select(HttpBridgeOperationRecord.state))).all() == []


async def test_cancelled_root_registration_cleans_up_its_committed_receipt(async_client, root_bridge, monkeypatch):
    upstream, service, _ = root_bridge
    register = service._durable_bridge.record_operation
    committed = asyncio.Event()
    deliver = asyncio.Event()

    async def delayed_receipt(**kwargs):
        receipt = await register(**kwargs)
        assert receipt is not None and receipt.created
        committed.set()
        await deliver.wait()
        return receipt

    monkeypatch.setattr(service._durable_bridge, "record_operation", delayed_receipt)
    task = asyncio.create_task(
        async_client.post(
            "/v1/responses", json={"model": "gpt-5.1", "instructions": "", "input": "cancel root", "stream": True}
        )
    )
    try:
        await asyncio.wait_for(committed.wait(), timeout=5)
        task.cancel()
        await asyncio.sleep(0)
        task.cancel()
        deliver.set()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(task, timeout=5)
    finally:
        deliver.set()
        if not task.done():
            task.cancel()
        await asyncio.gather(task, return_exceptions=True)
    assert upstream.sent_text == []
    async with SessionLocal() as session:
        assert (await session.scalars(select(HttpBridgeOperationRecord))).all() == []
