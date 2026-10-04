from __future__ import annotations

import asyncio
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.clients import proxy as core_proxy
from app.core.config.key_fingerprint import (
    EncryptionKeyFingerprintMismatchError,
    compute_encryption_key_fingerprint,
    verify_encryption_key_fingerprint,
)
from app.core.config.settings import Settings, get_settings
from app.core.crypto import TokenEncryptor, get_or_create_key
from app.core.utils.time import utcnow
from app.db.models import Account, RequestLog, RuntimeSentinel
from app.db.session import SessionLocal
from app.modules.proxy import service as proxy_service
from app.modules.telemetry import api as telemetry_api
from app.modules.telemetry import sender as telemetry_sender
from app.modules.telemetry.consent import TelemetryConsentStore
from app.modules.telemetry.schemas import TelemetryOptOut, TelemetrySnapshot
from app.modules.telemetry.sender import TelemetrySender
from tests.integration.test_proxy_chat_completions import _make_auth_json

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def isolated_transmission_lock(monkeypatch):
    monkeypatch.setattr(telemetry_sender, "_TRANSMISSION_LOCK", None)


@pytest.mark.asyncio
@pytest.mark.parametrize("phase", ["register", "activate", "snapshot"])
@pytest.mark.parametrize("outcome", ["complete", "cancel", "failure", "timeout"])
async def test_dashboard_disable_orders_complete_snapshot_protocol(async_client, monkeypatch, phase, outcome):
    entered = asyncio.Event()
    release = asyncio.Event()
    opted_out = asyncio.Event()
    observed: list[str] = []
    gated = False
    collector_key = None

    async def collect(request):
        nonlocal gated, collector_key
        body = await request.read()
        payload = json.loads(body)
        operation = request.match_info["operation"]
        if operation == "register":
            collector_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(payload["public_key"]))
        else:
            assert collector_key is not None
            collector_key.verify(bytes.fromhex(request.headers["X-Signature"]), body)
            if operation == "optout":
                assert payload["occurred_at"].endswith("Z")
        observed.append(operation)
        if operation == phase and not gated:
            gated = True
            entered.set()
            await release.wait()
            if outcome == "failure":
                return web.Response(status=503)
        if operation == "optout":
            opted_out.set()
        return web.Response(status=200)

    app = web.Application()
    app.router.add_post("/v1/{operation}", collect)
    async with TestServer(app) as collector:
        monkeypatch.delenv("CODEX_LB_TELEMETRY_ENABLED", raising=False)
        monkeypatch.setenv("CODEX_LB_TELEMETRY_ENDPOINT", str(collector.make_url("")))
        get_settings.cache_clear()
        if outcome == "timeout":
            monkeypatch.setattr(telemetry_sender, "_TIMEOUT_SECONDS", 0.5)
        preview = await async_client.get("/api/settings/telemetry")
        assert preview.status_code == 200
        snapshot = TelemetrySnapshot.model_validate(preview.json()["preview"]["metrics"])
        snapshot_task = asyncio.create_task(TelemetrySender().send_snapshot(snapshot))
        disable_task = None
        try:
            await asyncio.wait_for(entered.wait(), 2)
            disable_task = asyncio.create_task(async_client.put("/api/settings/telemetry", json={"enabled": False}))
            try:
                await asyncio.wait_for(asyncio.shield(disable_task), 0.1)
            except TimeoutError:
                pass
            else:
                pytest.fail(f"dashboard disable committed during in-flight {phase}")
            if outcome == "cancel":
                snapshot_task.cancel()
            if outcome != "timeout":
                release.set()
            await asyncio.gather(snapshot_task, return_exceptions=True)
            release.set()
            response = await asyncio.wait_for(disable_task, 2)
            assert response.status_code == 200 and response.json()["active"] is False
            await asyncio.wait_for(opted_out.wait(), 2)
            await asyncio.gather(*tuple(telemetry_api._OPT_OUT_TASKS))
            assert observed[-1] == "optout"
            before = observed.copy()
            await TelemetrySender().send_snapshot(snapshot)
            assert observed == before
            async with SessionLocal() as session:
                assert (await TelemetryConsentStore(session).resolve()).active is False
        finally:
            release.set()
            for task in [snapshot_task, disable_task, *tuple(telemetry_api._OPT_OUT_TASKS)]:
                if task is not None and not task.done():
                    task.cancel()
            await asyncio.gather(
                *[task for task in [snapshot_task, disable_task, *tuple(telemetry_api._OPT_OUT_TASKS)] if task],
                return_exceptions=True,
            )


@pytest.mark.parametrize("value", ["bad", "", "2026-99-03T12:00:00Z", "12345", 12345])
def test_opt_out_rejects_malformed_timestamp(value):
    with pytest.raises(ValidationError):
        TelemetryOptOut(app_version="1.0", instance_id="test-instance", occurred_at=value)


@pytest.mark.parametrize(
    "value",
    [
        "2026-10-03T15:00:00+03:00",
        datetime(2026, 10, 3, 12),
        datetime(2026, 10, 3, 15, tzinfo=timezone(timedelta(hours=3))),
    ],
)
def test_opt_out_timestamp_is_canonical_utc(value):
    event = TelemetryOptOut(app_version="1.0", instance_id="test-instance", occurred_at=value)
    assert json.loads(event.model_dump_json())["occurred_at"] == "2026-10-03T12:00:00Z"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("raw", "family"),
    [
        ("codex_cli_rs", "codex-cli"),
        ("codex", "codex-cli"),
        ("codex-cli", "codex-cli"),
        ("codex_exec", "codex-cli"),
        ("codex-tui", "codex-cli"),
        ("Codex Desktop", "codex-desktop"),
        ("codex desktop", "codex-desktop"),
        ("codex_chatgpt_desktop", "codex-desktop"),
        ("codex_atlas", "codex-desktop"),
        ("private-client-name", "other"),
        (None, "other"),
    ],
)
async def test_persisted_client_groups_reach_real_preview(async_client, monkeypatch, raw, family):
    monkeypatch.delenv("CODEX_LB_TELEMETRY_ENABLED", raising=False)
    get_settings.cache_clear()
    async with SessionLocal() as session:
        session.add(
            RequestLog(
                request_id="client-family-contract",
                requested_at=utcnow(),
                model="gpt-5.4",
                status="success",
                useragent_group=raw,
                input_tokens=2,
                output_tokens=1,
                latency_ms=100,
            )
        )
        await session.commit()
    response = await async_client.get("/api/settings/telemetry?include_preview=true")
    assert response.status_code == 200, response.text
    usage = response.json()["preview"]["metrics"]["usage_7d"]
    assert usage["clients"] == {family: 1.0}
    assert usage["clients_other_ratio"] == (1.0 if family == "other" else 0.0)
    if raw == "private-client-name":
        assert raw not in json.dumps(response.json()["preview"])


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/v1/responses", "/v1/chat/completions"])
@pytest.mark.parametrize("stream", [True, False])
@pytest.mark.parametrize(
    ("useragent", "family"),
    [
        ("codex_cli_rs/0.118.0", "codex-cli"),
        ("codex_exec/0.118.0", "codex-cli"),
        ("codex/0.118.0", "codex-cli"),
        ("codex-cli/0.118.0", "codex-cli"),
        ("Codex Desktop/1.0", "codex-desktop"),
        ("private-client-name/0.1", "other"),
    ],
)
async def test_proxy_client_useragent_persists_into_telemetry_preview(
    async_client, monkeypatch, path, stream, useragent, family
):
    monkeypatch.delenv("CODEX_LB_TELEMETRY_ENABLED", raising=False)
    get_settings.cache_clear()
    imported = await async_client.post(
        "/api/accounts/import",
        files={
            "auth_json": (
                "auth.json",
                json.dumps(_make_auth_json("telemetry-wire-owner", "wire@example.invalid")),
                "application/json",
            )
        },
    )
    assert imported.status_code == 200
    requests = []

    async def upstream(request):
        requests.append(await request.json())
        events = [
            {"type": "response.output_text.delta", "delta": "ok"},
            {
                "type": "response.completed",
                "response": {
                    "id": "resp_telemetry_client",
                    "status": "completed",
                    "model": "gpt-5.2",
                    "output": [
                        {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "ok"}]}
                    ],
                    "usage": {"input_tokens": 2, "output_tokens": 1},
                },
            },
        ]
        return web.Response(
            text="".join(f"data: {json.dumps(event)}\n\n" for event in events), content_type="text/event-stream"
        )

    app = web.Application()
    app.router.add_post("/codex/responses", upstream)
    monkeypatch.setattr(core_proxy, "discover_native_egress_client", lambda: None)
    async with TestServer(app) as server, aiohttp.ClientSession() as session:

        async def stream_local(payload, headers, access_token, account_id, **kwargs):
            async for event in core_proxy.stream_responses(
                payload,
                headers,
                access_token,
                account_id,
                base_url=str(server.make_url("/")),
                session=session,
                upstream_stream_transport_override="http",
            ):
                yield event

        monkeypatch.setattr(proxy_service, "core_stream_responses", stream_local)
        payload = {"model": "gpt-5.2", "stream": stream}
        if path == "/v1/responses":
            payload["input"] = "hi"
        else:
            payload["messages"] = [{"role": "user", "content": "hi"}]
        response = await async_client.post(path, headers={"User-Agent": useragent}, json=payload)
        assert response.status_code == 200, response.text
        assert len(requests) == 1
    async with SessionLocal() as session:
        log = (await session.execute(select(RequestLog))).scalar_one()
        assert log.useragent == useragent
        assert log.useragent_group == useragent.split("/", 1)[0]
    preview = await async_client.get("/api/settings/telemetry?include_preview=true")
    assert preview.status_code == 200
    usage = preview.json()["preview"]["metrics"]["usage_7d"]
    assert usage["clients"] == {family: 1.0}
    assert usage["clients_other_ratio"] == (1.0 if family == "other" else 0.0)
    assert useragent not in json.dumps(preview.json()["preview"])


@pytest.mark.asyncio
async def test_environment_key_import_and_independent_instance_readback(async_client, monkeypatch, tmp_path):
    raw_key = Fernet.generate_key()
    blocked_parent = tmp_path / "not-a-directory"
    blocked_parent.write_text("unusable key path")
    key_file = blocked_parent / "encryption.key"
    monkeypatch.setenv("CODEX_LB_ENCRYPTION_KEY", f"  {raw_key.decode()}\n")
    monkeypatch.setenv("CODEX_LB_ENCRYPTION_KEY_FILE", str(key_file))
    get_settings.cache_clear()
    assert get_settings().encryption_key == raw_key.decode()

    auth = _make_auth_json("stateless-key-owner", "stateless@example.invalid")
    response = await async_client.post(
        "/api/accounts/import", files={"auth_json": ("auth.json", json.dumps(auth), "application/json")}
    )
    assert response.status_code == 200, response.text
    async with SessionLocal() as session:
        account = await session.get(Account, response.json()["accountId"])
        assert account is not None
        ciphertext = account.access_token_encrypted
        assert ciphertext != b"access-token"
        assert TokenEncryptor().decrypt(ciphertext) == "access-token"
        assert TokenEncryptor(key=raw_key).decrypt(account.refresh_token_encrypted) == "refresh-token"
    get_settings.cache_clear()
    assert TokenEncryptor().decrypt(ciphertext) == "access-token"
    assert get_or_create_key() == raw_key
    assert compute_encryption_key_fingerprint() == compute_encryption_key_fingerprint_for(raw_key)
    assert not key_file.exists()

    sentinel_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    try:
        async with sentinel_engine.begin() as connection:
            await connection.run_sync(RuntimeSentinel.__table__.create)
        sentinel_sessions = async_sessionmaker(sentinel_engine)
        await verify_encryption_key_fingerprint(sentinel_sessions, mode="enforce")
        await verify_encryption_key_fingerprint(sentinel_sessions, mode="enforce")
        monkeypatch.setenv("CODEX_LB_ENCRYPTION_KEY", Fernet.generate_key().decode())
        get_settings.cache_clear()
        with pytest.raises(EncryptionKeyFingerprintMismatchError) as mismatch:
            await verify_encryption_key_fingerprint(sentinel_sessions, mode="enforce")
        assert "use the same CODEX_LB_ENCRYPTION_KEY value" in str(mismatch.value)
        assert raw_key.decode() not in str(mismatch.value)
        assert get_settings().encryption_key not in str(mismatch.value)
        with pytest.raises(InvalidToken):
            TokenEncryptor().decrypt(ciphertext)
        async with sentinel_sessions() as session:
            stored = await session.scalar(select(RuntimeSentinel.value))
            assert stored == compute_encryption_key_fingerprint_for(raw_key)
    finally:
        await sentinel_engine.dispose()


def compute_encryption_key_fingerprint_for(key: bytes) -> str:
    return "sha256:" + hashlib.sha256(key).hexdigest()


def test_environment_key_explicit_overrides_and_blank_file_fallback(monkeypatch, tmp_path):
    environment, file_key, explicit = (Fernet.generate_key() for _ in range(3))
    default_path = tmp_path / "default.key"
    override_path = tmp_path / "override.key"
    override_path.write_bytes(file_key)
    monkeypatch.setenv("CODEX_LB_ENCRYPTION_KEY", environment.decode())
    monkeypatch.setenv("CODEX_LB_ENCRYPTION_KEY_FILE", str(default_path))
    get_settings.cache_clear()
    assert get_or_create_key(override_path) == file_key
    encrypted = TokenEncryptor(key_file=override_path).encrypt("file-selected")
    assert Fernet(file_key).decrypt(encrypted) == b"file-selected"
    encrypted = TokenEncryptor(key=explicit, key_file=override_path).encrypt("bytes-selected")
    assert Fernet(explicit).decrypt(encrypted) == b"bytes-selected"
    assert compute_encryption_key_fingerprint(override_path) == compute_encryption_key_fingerprint_for(file_key)
    assert not default_path.exists()
    monkeypatch.setenv("CODEX_LB_ENCRYPTION_KEY", " \n ")
    get_settings.cache_clear()
    fallback = get_or_create_key()
    assert default_path.read_bytes() == fallback
    assert TokenEncryptor().decrypt(TokenEncryptor().encrypt("fallback")) == "fallback"


def test_invalid_environment_key_fails_settings(monkeypatch):
    monkeypatch.setenv("CODEX_LB_ENCRYPTION_KEY", "not-a-fernet-key")
    with pytest.raises(ValidationError, match="valid 32-byte"):
        Settings(_env_file=None)


def test_stateless_environment_key_across_fresh_processes(tmp_path):
    key = Fernet.generate_key()
    blocked = tmp_path / "blocked"
    blocked.write_text("no key file allowed")
    ciphertext = tmp_path / "credential.bin"
    environment = {
        **os.environ,
        "CODEX_LB_ENCRYPTION_KEY": key.decode(),
        "CODEX_LB_ENCRYPTION_KEY_FILE": str(blocked / "key"),
        "CREDENTIAL_PATH": str(ciphertext),
    }
    writer = """
import os
from pathlib import Path
from app.core.crypto import TokenEncryptor
Path(os.environ['CREDENTIAL_PATH']).write_bytes(TokenEncryptor().encrypt('synthetic-process-token'))
"""
    reader = """
import os
from pathlib import Path
from app.core.crypto import TokenEncryptor
assert TokenEncryptor().decrypt(Path(os.environ['CREDENTIAL_PATH']).read_bytes()) == 'synthetic-process-token'
"""
    for script in (writer, reader):
        result = subprocess.run(
            [sys.executable, "-c", script], env=environment, capture_output=True, text=True, timeout=15, check=False
        )
        assert result.returncode == 0, result.stderr
    assert not (blocked / "key").exists()
