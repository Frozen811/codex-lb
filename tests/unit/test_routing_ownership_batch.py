from __future__ import annotations

import time
from copy import deepcopy
from types import SimpleNamespace
from typing import cast

import pytest

import app.modules.proxy.load_balancer as balancer_module
from app.core.types import JsonValue
from app.db.models import AccountStatus
from app.modules.proxy._service.streaming.helpers import _is_account_neutral_request_rejection
from app.modules.proxy.account_cache import AccountSelectionCache
from app.modules.proxy.load_balancer import AccountConcurrencyCaps, RuntimeState
from app.modules.proxy.replay_safety import responses_payload_has_only_encrypted_account_scoped_state
from tests.unit.test_load_balancer_contract import _account, _balancer

pytestmark = pytest.mark.unit


def _body(item_type: str = "reasoning") -> dict[str, JsonValue]:
    return {
        "model": "gpt-5.1",
        "input": [
            {"type": item_type, "id": "retained", "encrypted_content": "opaque"},
            {"role": "user", "content": "next"},
        ],
    }


@pytest.mark.parametrize("item_type", ["reasoning", "compaction"])
def test_ciphertext_classification_preserves_the_complete_body(item_type: str) -> None:
    payload = _body(item_type)
    original = deepcopy(payload)
    assert responses_payload_has_only_encrypted_account_scoped_state(payload)
    assert payload == original


@pytest.mark.parametrize(
    "boundary",
    [
        "file",
        "image_file",
        "container",
        "vector_store",
        "unknown_item",
        "unknown_cipher_field",
        "summary_reference",
        "summary_shape",
        "cipher_type",
        "empty_cipher",
        "unfinished",
        "nested_cipher",
        "conversation",
        "anchor",
        "unknown_control",
        "hosted_tool",
        "unsettled_tool",
        "owned_message",
        "malformed_type",
    ],
)
def test_ciphertext_exception_refuses_other_scoped_or_unknown_state(boundary: str) -> None:
    payload = _body()
    items = cast(list[JsonValue], payload["input"])
    cipher = cast(dict[str, JsonValue], items[0])
    if boundary == "file":
        items.append({"type": "input_file", "file_id": "opaque"})
    elif boundary == "image_file":
        items.append({"type": "input_image", "file_id": "opaque"})
    elif boundary in {"container", "vector_store"}:
        cipher[f"{boundary}_id"] = "opaque"
    elif boundary == "unknown_item":
        items.append({"type": "unknown_retained", "state": "opaque"})
    elif boundary == "unknown_cipher_field":
        cipher["owner_extension"] = "opaque"
    elif boundary == "summary_reference":
        cipher["summary"] = [{"type": "summary_text", "text": "known", "file_id": "opaque"}]
    elif boundary == "summary_shape":
        cipher["summary"] = {"text": "not a list"}
    elif boundary == "cipher_type":
        cipher["encrypted_content"] = {"state": "opaque"}
    elif boundary == "empty_cipher":
        cipher["encrypted_content"] = ""
    elif boundary == "unfinished":
        cipher["status"] = "in_progress"
    elif boundary == "nested_cipher":
        items[0] = {"role": "user", "content": [{"type": "input_text", "text": "next", "encrypted_content": "opaque"}]}
    elif boundary == "conversation":
        payload["conversation"] = "conv_owned"
    elif boundary == "anchor":
        payload["previous_response_id"] = "resp_owned"
    elif boundary == "unknown_control":
        payload["unrecognized_state"] = "opaque"
    elif boundary == "hosted_tool":
        payload["tools"] = [{"type": "file_search", "vector_store_ids": ["vs_owned"]}]
    elif boundary == "unsettled_tool":
        items.append({"type": "function_call", "call_id": "pending", "name": "read", "arguments": "{}"})
    elif boundary == "owned_message":
        items.append({"role": "assistant", "id": "msg_owned", "content": "answer"})
    elif boundary == "malformed_type":
        items.append({"type": [], "content": "unknown"})
    original = deepcopy(payload)
    assert not responses_payload_has_only_encrypted_account_scoped_state(payload)
    assert payload == original


@pytest.mark.parametrize("status", [None, 400, 401, 429, 500])
@pytest.mark.parametrize("code", ["invalid_encrypted_content", "invalid_request_error"])
def test_encrypted_rejection_neutrality_requires_payload_failure_status(status: int | None, code: str) -> None:
    assert _is_account_neutral_request_rejection(
        code=code,
        http_status=status,
        message="The reasoning content cannot be decrypted",
    ) is (status in (None, 400))


@pytest.mark.asyncio
@pytest.mark.parametrize("boundary", ["active", "paused", "excluded", "cap"])
async def test_backed_off_hard_owner_preserves_other_admission_gates(
    monkeypatch: pytest.MonkeyPatch, boundary: str
) -> None:
    monkeypatch.setattr(balancer_module, "get_settings", lambda: SimpleNamespace(circuit_breaker_enabled=False))
    monkeypatch.setattr(balancer_module, "set_normal", lambda: None)
    monkeypatch.setattr(balancer_module, "set_degraded", lambda _reason: None)
    owner, sibling = _account("bounded-owner"), _account("healthy-sibling")
    if boundary == "paused":
        owner.status = AccountStatus.PAUSED
    balancer, _, _, _ = _balancer([owner, sibling], AccountSelectionCache(ttl_seconds=60))
    last_error = time.time() - 1.0
    balancer._runtime[owner.id] = RuntimeState(error_count=5, last_error_at=last_error)
    caps = AccountConcurrencyCaps(response_create_limit=1, stream_limit=1)
    occupied = (
        await balancer.acquire_account_lease(owner.id, kind="stream", concurrency_caps=caps)
        if boundary == "cap"
        else None
    )
    try:
        selected = await balancer.select_account(
            required_account_id=owner.id,
            required_continuity_owner=True,
            lease_kind="stream",
            concurrency_caps=caps,
            exclude_account_ids={owner.id} if boundary == "excluded" else None,
        )
        if boundary == "active":
            assert selected.account is not None and selected.account.id == owner.id
            await balancer.release_account_lease(selected.lease)
            assert balancer._runtime[owner.id].error_count == 5
            assert balancer._runtime[owner.id].last_error_at == last_error
        else:
            assert selected.account is None
            assert selected.lease is None
    finally:
        await balancer.release_account_lease(occupied)
    assert await balancer.account_pressure_snapshot(owner.id) == (0, 0, 0.0)
    assert await balancer.account_pressure_snapshot(sibling.id) == (0, 0, 0.0)
