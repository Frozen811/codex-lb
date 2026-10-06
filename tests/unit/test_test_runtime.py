from __future__ import annotations

import asyncio
import multiprocessing
import os
from pathlib import Path

import pytest
from sqlalchemy.engine import make_url

from tests.runtime import automatic_worker_count, create_test_storage, worker_database_name

pytestmark = pytest.mark.unit


def _spawn_asgi_probe(connection) -> None:
    """Top-level target, importable by Windows' fresh-interpreter spawn."""
    from httpx import ASGITransport, AsyncClient

    from app.core.config.settings import get_settings
    from app.main import create_app

    async def probe() -> int:
        async with AsyncClient(transport=ASGITransport(app=create_app()), base_url="http://testserver") as client:
            return (await client.get("/health")).status_code

    connection.send((get_settings().database_url, asyncio.run(probe())))
    connection.close()


def test_spawned_asgi_client_inherits_isolated_database() -> None:
    context = multiprocessing.get_context("spawn")
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(target=_spawn_asgi_probe, args=(sender,))
    process.start()
    sender.close()
    try:
        assert receiver.poll(30), "Spawned ASGI client did not finish"
        database_url, status = receiver.recv()
        assert database_url == os.environ["CODEX_LB_DATABASE_URL"]
        assert status == 200
        process.join(10)
        assert process.exitcode == 0
    finally:
        if process.is_alive():
            process.terminate()
            process.join(10)
        receiver.close()


def test_sqlite_workers_never_use_an_explicit_shared_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw4")
    monkeypatch.setenv("CODEX_LB_TEST_DATABASE_URL", f"sqlite+aiosqlite:///{tmp_path / 'shared.db'}")
    # Restore both URL overrides when the test exits.
    monkeypatch.setenv("CODEX_LB_DATABASE_URL", os.environ["CODEX_LB_DATABASE_URL"])
    first = create_test_storage()
    second = create_test_storage()
    try:
        assert first.database_url != second.database_url
        assert "shared.db" not in first.database_url
        database_path = make_url(first.database_url).database
        assert database_path is not None
        assert Path(database_path).parent == first.path
    finally:
        first.close()
        second.close()


def test_worker_database_names_isolate_workers_and_simultaneous_runs() -> None:
    names = {
        worker_database_name("codex-lb", run_id, worker) for run_id in ("a" * 12, "b" * 12) for worker in ("gw0", "gw1")
    }
    assert len(names) == 4
    assert all(len(name) < 64 and "-" not in name for name in names)
    with pytest.raises(ValueError):
        worker_database_name("codex_lb", "a" * 12, "gw0; DROP DATABASE other")


def test_automatic_worker_count_is_positive_and_cpu_bounded() -> None:
    assert 1 <= automatic_worker_count() <= (os.process_cpu_count() or 1)
