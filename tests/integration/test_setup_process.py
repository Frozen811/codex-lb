"""Exercise setup through fresh CLI processes and real HTTP with disposable stores."""

from __future__ import annotations

import json
import os
import shutil
import socket
import sqlite3
import subprocess
import sys
import time
from collections.abc import Iterator
from contextlib import closing, contextmanager
from datetime import datetime
from pathlib import Path

import httpx
import pytest
from cryptography.fernet import Fernet
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.crypto import TokenEncryptor
from app.db.models import Account, AccountStatus

pytestmark = pytest.mark.integration
_ROOT = Path(__file__).resolve().parents[2]


def _environment(data_dir: Path) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("CODEX_LB_")}
    for name in ("HOST", "PORT", "SSL_CERTFILE", "SSL_KEYFILE", "UVICORN_TIMEOUT_KEEP_ALIVE", "UVICORN_WS_MAX_SIZE"):
        env.pop(name, None)
    env.update(
        PYTHONPATH=str(_ROOT),
        CODEX_LB_DATA_DIR=str(data_dir),
        CODEX_LB_ENV_FILE=str(data_dir.parent / "absent.env"),
        CODEX_LB_UPSTREAM_BASE_URL="https://example.invalid/backend-api",
    )
    return env


@contextmanager
def _server(data_dir: Path, *, fallback: str = "4") -> Iterator[httpx.Client]:
    with socket.socket() as reserved:
        reserved.bind(("127.0.0.1", 0))
        port = reserved.getsockname()[1]
    env = _environment(data_dir)
    env["CODEX_LB_PROXY_ACCOUNT_RESPONSE_CREATE_LIMIT"] = fallback
    log_file = data_dir.parent / f"server-{port}.log"
    with log_file.open("w", encoding="utf-8") as logs:
        process = subprocess.Popen(
            [sys.executable, "-m", "app.cli", "--host", "127.0.0.1", "--port", str(port)],
            cwd=data_dir.parent,
            env=env,
            stdout=logs,
            stderr=subprocess.STDOUT,
        )
        try:
            with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=2, trust_env=False) as client:
                deadline = time.monotonic() + 40
                while time.monotonic() < deadline:
                    assert process.poll() is None, "CLI exited before readiness; inspect isolated server log"
                    try:
                        if client.get("/health/ready").status_code == 200:
                            break
                    except httpx.TransportError:
                        pass
                    time.sleep(0.1)
                else:
                    pytest.fail("CLI did not reach readiness within 40 seconds")
                yield client
        finally:
            process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def _assert_account(data_dir: Path) -> None:
    # A relocated installation reads its store in a fresh interpreter too.
    # Keep the rehearsal reader independent from the snapshot-creating process.
    subprocess.run(
        [
            sys.executable,
            "-c",
            """
from contextlib import closing
import sqlite3
from app.core.config.settings import get_settings
from app.core.crypto import TokenEncryptor
settings = get_settings()
with closing(sqlite3.connect(settings.data_dir / 'store.db')) as connection:
    row = connection.execute(
        'SELECT status, access_token_encrypted, refresh_token_encrypted FROM accounts WHERE id = ?',
        ('setup-fixture',),
    ).fetchone()
    assert row is not None and row[0] == 'paused'
    encryptor = TokenEncryptor()
    assert encryptor.decrypt(row[1]) == 'synthetic-access'
    assert encryptor.decrypt(row[2]) == 'synthetic-refresh'
""",
        ],
        cwd=data_dir.parent,
        env=_environment(data_dir),
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_cli_sqlite_restart_and_paired_restore(tmp_path: Path) -> None:
    data_dir = tmp_path / "original"
    with _server(data_dir) as client:
        assert client.get("/api/settings").json()["proxyAccountResponseCreateLimit"] == 4
        response = client.put("/api/settings", json={"proxyAccountResponseCreateLimit": 9})
        assert response.status_code == 200
        assert response.json()["proxyAccountResponseCreateLimitOverride"] == 9
    key = (data_dir / "encryption.key").read_bytes()
    encryptor = TokenEncryptor(key=key)
    engine = create_engine(f"sqlite:///{data_dir / 'store.db'}")
    try:
        with Session(engine) as session:
            session.add(
                Account(
                    id="setup-fixture",
                    email="setup@example.invalid",
                    plan_type="plus",
                    access_token_encrypted=encryptor.encrypt("synthetic-access"),
                    refresh_token_encrypted=encryptor.encrypt("synthetic-refresh"),
                    id_token_encrypted=encryptor.encrypt("synthetic-id"),
                    last_refresh=datetime(2026, 1, 1),
                    status=AccountStatus.PAUSED,
                )
            )
            session.commit()
    finally:
        engine.dispose()
    with _server(data_dir, fallback="6") as client:
        payload = client.get("/api/settings").json()
        assert payload["proxyAccountResponseCreateLimit"] == 9
        assert payload["proxyAccountResponseCreateLimitEnvironmentValue"] == 6
        response = client.get("/api/accounts")
        assert response.status_code == 200
        assert "setup-fixture" in json.dumps(response.json())
    assert (data_dir / "encryption.key").read_bytes() == key
    _assert_account(data_dir)

    restored = tmp_path / "restored"
    restored.mkdir()
    with (
        closing(sqlite3.connect(data_dir / "store.db")) as source,
        closing(sqlite3.connect(restored / "store.db")) as destination,
    ):
        source.backup(destination)
        destination.execute("PRAGMA journal_mode=DELETE")
    shutil.copy2(data_dir / "encryption.key", restored / "encryption.key")
    with _server(restored, fallback="7") as client:
        assert client.get("/api/settings").json()["proxyAccountResponseCreateLimit"] == 9
        assert "setup-fixture" in client.get("/api/accounts").text
        response = client.put("/api/settings", json={"proxyAccountResponseCreateLimit": None})
        assert response.status_code == 200
        assert response.json()["proxyAccountResponseCreateLimit"] == 7
    _assert_account(restored)

    # The database's existing fingerprint must refuse an unrelated valid key.
    (restored / "encryption.key").write_bytes(Fernet.generate_key())
    failed = subprocess.run(
        [sys.executable, "-m", "app.cli", "--port", "0"],
        cwd=tmp_path,
        env=_environment(restored),
        capture_output=True,
        text=True,
        timeout=40,
    )
    assert failed.returncode != 0
    assert "Encryption key mismatch" in failed.stderr


@pytest.mark.parametrize("from_env", [False, True])
def test_negative_keep_alive_cli_does_not_create_store(tmp_path: Path, from_env: bool) -> None:
    data_dir = tmp_path / "never-created"
    env = _environment(data_dir)
    args = [] if from_env else ["--timeout-keep-alive", "-1"]
    if from_env:
        env["UVICORN_TIMEOUT_KEEP_ALIVE"] = "-1"
    failed = subprocess.run(
        [sys.executable, "-m", "app.cli", *args],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert failed.returncode != 0
    assert "must be non-negative" in failed.stderr
    assert not data_dir.exists()
