from __future__ import annotations

from pathlib import Path

import pytest
from cryptography.fernet import Fernet

from app.core.config.settings import get_settings
from app.core.openai.requests import ResponsesRequest
from app.modules.proxy.http_bridge_forwarding import (
    HTTPBridgeForwardContext,
    build_owner_forward_headers,
    parse_forwarded_request,
)

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "key_mode", ["env_distinct_files", "env_missing_files", "env_invalid_files", "file_only", "mismatch"]
)
@pytest.mark.parametrize("signature_version", [None, "2"])
def test_bridge_key_precedence_across_replica_settings(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    key_mode: str,
    signature_version: str | None,
):
    shared_key = Fernet.generate_key()
    origin_file, owner_file = tmp_path / "origin.key", tmp_path / "owner.key"
    if key_mode == "file_only":
        origin_file.write_bytes(shared_key)
        owner_file.write_bytes(shared_key)
    elif key_mode != "env_missing_files":
        origin_file.write_bytes(b"invalid-file-key" if key_mode == "env_invalid_files" else Fernet.generate_key())
        owner_file.write_bytes(
            b"another-invalid-file-key" if key_mode == "env_invalid_files" else Fernet.generate_key()
        )
    original_files = {p: p.read_bytes() for p in (origin_file, owner_file) if p.exists()}
    payload = ResponsesRequest(model="gpt-5.4", input="hi", instructions="hi")
    context = HTTPBridgeForwardContext(
        origin_instance="origin",
        target_instance="owner",
        codex_session_affinity=True,
        downstream_turn_state="turn",
        client_ip="192.0.2.5",
        signature_version=signature_version,
    )
    monkeypatch.setenv("CODEX_LB_ENCRYPTION_KEY_FILE", str(origin_file))
    if key_mode == "file_only":
        monkeypatch.delenv("CODEX_LB_ENCRYPTION_KEY", raising=False)
    else:
        monkeypatch.setenv("CODEX_LB_ENCRYPTION_KEY", shared_key.decode())
    get_settings.cache_clear()
    try:
        signed_headers = build_owner_forward_headers(headers={}, payload=payload, context=context)
        # A fresh settings object represents a receiver with its own key-file path.
        monkeypatch.setenv("CODEX_LB_ENCRYPTION_KEY_FILE", str(owner_file))
        if key_mode == "mismatch":
            monkeypatch.setenv("CODEX_LB_ENCRYPTION_KEY", Fernet.generate_key().decode())
        get_settings.cache_clear()
        forwarded, error = parse_forwarded_request(signed_headers, payload=payload, current_instance="owner")
        if key_mode == "mismatch":
            assert forwarded is None
            assert error is not None
            assert error.status_code == 400
            assert error.payload["error"]["code"] == "bridge_forward_invalid"
        else:
            assert error is None
            assert forwarded is not None
            assert forwarded.context.origin_instance == "origin"
            assert forwarded.context.client_ip == "192.0.2.5"
        assert {p: p.read_bytes() for p in (origin_file, owner_file) if p.exists()} == original_files
    finally:
        get_settings.cache_clear()
