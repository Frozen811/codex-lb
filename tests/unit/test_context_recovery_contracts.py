from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
from sqlalchemy import update

from app.db.models import HttpBridgeOperationRecord
from app.modules.proxy.durable_bridge_repository import DurableBridgeRepository
from app.modules.proxy.replay_safety import project_durable_transcript_for_account_neutral_fresh_replay
from tests.unit.test_bridge_ring_lifecycle import _claim
from tests.unit.test_bridge_ring_lifecycle import async_session_factory as _session_factory_fixture

pytestmark = pytest.mark.unit
async_session_factory = _session_factory_fixture


def _event(event_type, **fields):
    return f"data: {json.dumps({'type': event_type, **fields})}\n\n"


def _answer():
    return {
        "id": "msg_answer",
        "type": "message",
        "role": "assistant",
        "status": "completed",
        "content": [{"type": "output_text", "text": "answer"}],
    }


def _project(events):
    turn = SimpleNamespace(
        operation=SimpleNamespace(
            request_text=json.dumps({"input": [{"role": "user", "content": "first"}]}),
            response_id="resp_root",
            parent_response_id=None,
            event_spool_complete=True,
        ),
        events=events,
    )
    return project_durable_transcript_for_account_neutral_fresh_replay(
        [turn],
        anchor_response_id="resp_root",
        current_payload={"previous_response_id": "resp_root", "input": [{"role": "user", "content": "next"}]},
    )


@pytest.mark.parametrize(
    "defect",
    ["missing-done", "wrong-done-id", "wrong-terminal-id", "null-output", "missing-output-item", "wrong-output"],
)
def test_reconstruction_rejects_incomplete_or_conflicting_terminal_evidence(defect):
    answer = _answer()
    events = [
        _event("response.created", response={"id": "resp_root"}),
        _event("response.output_item.added", output_index=0, item={**answer, "status": "in_progress"}),
    ]
    if defect != "missing-done":
        done = {**answer, "id": "msg_other"} if defect == "wrong-done-id" else answer
        events.append(_event("response.output_item.done", output_index=0, item=done))
    response = {"id": "resp_other" if defect == "wrong-terminal-id" else "resp_root", "output": [answer]}
    if defect == "null-output":
        response["output"] = None
    elif defect == "missing-output-item":
        response["output"] = [{**answer, "id": "msg_other"}]
    elif defect == "wrong-output":
        response["output"] = [{**answer, "content": [{"type": "output_text", "text": "changed"}]}]
    events.append(_event("response.completed", response=response))

    assert _project(events) is None


@pytest.mark.parametrize("terminal_type", ["response.completed", "response.incomplete"])
@pytest.mark.parametrize("with_output", [False, True])
def test_reconstruction_accepts_matching_completed_item_material(terminal_type, with_output):
    answer = _answer()
    response = {"id": "resp_root"}
    if with_output:
        response["output"] = [answer]
    events = [
        _event("response.created", response={"id": "resp_root"}),
        _event("response.output_item.added", output_index=0, item={**answer, "status": "in_progress"}),
        _event("response.output_item.done", output_index=0, item=answer),
        _event(terminal_type, response=response),
    ]

    result = _project(events)

    assert result is not None
    assert [item.get("content") for item in result.payload["input"]] == ["first", answer["content"], "next"]


def test_reconstruction_does_not_mix_abandoned_attempt_output():
    answer = _answer()
    abandoned = {**answer, "id": "msg_abandoned"}
    events = [
        _event("response.created", response={"id": "resp_abandoned"}),
        _event("response.output_item.added", output_index=0, item=abandoned),
        _event("response.failed", response={"id": "resp_abandoned"}),
        _event("response.created", response={"id": "resp_root"}),
        _event("response.completed", response={"id": "resp_root", "output": [answer]}),
    ]

    assert _project(events) is not None


@pytest.mark.parametrize(
    "defect", [None, "parent", "acknowledged", "terminal", "response", "event-bytes", "spool", "epoch", "owner"]
)
async def test_root_replay_rebind_is_fenced_by_owner_and_absent_acceptance(async_session_factory, defect):
    async with async_session_factory() as session:
        repository = DurableBridgeRepository(session)
        claim = await _claim(repository, instance_id="root-owner")
        operation = await repository.record_operation(
            operation_id="root-rebind",
            session_id=claim.id,
            instance_id="root-owner",
            owner_epoch=claim.owner_epoch,
            request_fingerprint="f" * 64,
            account_id="acc-1",
            model="gpt-5.4",
            parent_response_id=None,
            request_text='{"input":"root"}',
        )
        assert operation is not None
        changes = {}
        if defect == "parent":
            changes["parent_response_id"] = "resp_parent"
        elif defect == "acknowledged":
            changes["state"] = "acknowledged"
        elif defect == "terminal":
            changes["state"] = "completed"
        elif defect == "response":
            changes["response_id"] = "resp_accepted"
        elif defect == "event-bytes":
            changes["event_bytes"] = 5
        elif defect == "spool":
            assert await repository.append_operation_event(
                operation_id="root-rebind",
                session_id=claim.id,
                instance_id="root-owner",
                owner_epoch=claim.owner_epoch,
                event_text="orphaned-spool",
                max_bytes=1024,
            )
            changes["event_bytes"] = 0
        if changes:
            await session.execute(
                update(HttpBridgeOperationRecord)
                .where(HttpBridgeOperationRecord.operation_id == "root-rebind")
                .values(**changes)
            )
            await session.commit()
        rebound = await repository.restart_root_operation_for_replay(
            operation_id="root-rebind",
            session_id=claim.id,
            instance_id="other-owner" if defect == "owner" else "root-owner",
            owner_epoch=claim.owner_epoch + (1 if defect == "epoch" else 0),
            account_id="acc-1",
            model="gpt-5.4",
            request_text='{"input":"root","client_metadata":{"codex_installation_id":"new-installation"}}',
        )
        assert rebound is (defect is None)
        retained = await repository.get_operation(operation_id="root-rebind")
        assert retained is not None
        assert retained.operation_id == operation.operation_id
        assert retained.recovery_dispatch_count == 0


@pytest.mark.parametrize("defect", [None, "response", "terminal", "parent", "epoch"])
async def test_output_free_root_restart_requires_captured_acceptance(async_session_factory, defect):
    async with async_session_factory() as session:
        repository = DurableBridgeRepository(session)
        claim = await _claim(repository, instance_id="root-owner")
        operation = await repository.record_operation(
            operation_id="accepted-root",
            session_id=claim.id,
            instance_id="root-owner",
            owner_epoch=claim.owner_epoch,
            request_fingerprint="e" * 64,
            account_id="acc-1",
            model="gpt-5.4",
            parent_response_id=None,
            request_text='{"input":"root"}',
        )
        assert operation is not None and operation.request_text is not None
        assert await repository.update_operation(
            operation_id=operation.operation_id,
            session_id=claim.id,
            instance_id="root-owner",
            owner_epoch=claim.owner_epoch,
            state="completed" if defect == "terminal" else "acknowledged",
            response_id="resp_old",
        )
        assert await repository.append_operation_event(
            operation_id=operation.operation_id,
            session_id=claim.id,
            instance_id="root-owner",
            owner_epoch=claim.owner_epoch,
            event_text=_event("response.created", response={"id": "resp_old"}),
            max_bytes=1024,
        )
        if defect == "parent":
            await session.execute(
                update(HttpBridgeOperationRecord)
                .where(HttpBridgeOperationRecord.operation_id == operation.operation_id)
                .values(parent_response_id="resp_parent")
            )
            await session.commit()
        restarted = await repository.restart_root_operation_for_replay(
            operation_id=operation.operation_id,
            session_id=claim.id,
            instance_id="root-owner",
            owner_epoch=claim.owner_epoch + (1 if defect == "epoch" else 0),
            account_id="acc-1",
            model="gpt-5.4",
            request_text=operation.request_text,
            expected_response_id="resp_wrong" if defect == "response" else "resp_old",
        )
        assert restarted is (defect is None)
        if restarted:
            retained = await repository.get_operation(operation_id=operation.operation_id)
            assert retained is not None and retained.state == "submitted" and retained.response_id is None
            assert not retained.event_spool_complete
            assert await repository.get_operation_events(operation_id=operation.operation_id) == []
            assert not await repository.restart_root_operation_for_replay(
                operation_id=operation.operation_id,
                session_id=claim.id,
                instance_id="root-owner",
                owner_epoch=claim.owner_epoch,
                account_id="acc-1",
                model="gpt-5.4",
                request_text=operation.request_text,
                expected_response_id="resp_old",
            )
