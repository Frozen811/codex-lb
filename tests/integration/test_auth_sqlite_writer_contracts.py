from __future__ import annotations

import asyncio
import contextvars
import socket

import pytest
from httpx import AsyncClient
from sqlalchemy import event, text

import app.modules.oauth.service as oauth
from app.db.session import SessionLocal, engine, sqlite_writer_section

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("operation", ["login", "oauth"])
async def test_authentication_survives_a_busy_local_sqlite_writer(
    async_client: AsyncClient, monkeypatch: pytest.MonkeyPatch, unused_tcp_port: int, operation: str
) -> None:
    if engine.dialect.name != "sqlite":
        pytest.skip("SQLite local-writer admission contract")
    if operation == "login":
        setup = await async_client.post("/api/dashboard-auth/password/setup", json={"password": "password123"})
        assert setup.status_code == 200
        await async_client.post("/api/dashboard-auth/logout", json={})
    monkeypatch.setattr(oauth, "OAUTH_CALLBACK_PORT", unused_tcp_port)

    def short_busy_timeout(connection, *_args) -> None:
        cursor = connection.cursor()
        try:
            cursor.execute("PRAGMA busy_timeout=10")
        finally:
            cursor.close()

    event.listen(engine.sync_engine, "checkout", short_busy_timeout)
    task: asyncio.Task | None = None
    try:
        with socket.socket() as occupied:
            occupied.bind(("127.0.0.1", unused_tcp_port))
            occupied.listen()
            async with sqlite_writer_section():
                async with SessionLocal() as holder:
                    await holder.execute(text("UPDATE rate_limit_attempts SET id = id WHERE 1 = 0"))
                    if operation == "login":
                        call = async_client.post("/api/dashboard-auth/password/login", json={"password": "password123"})
                    else:
                        call = async_client.post("/api/oauth/start", json={"forceMethod": "browser"})
                    task = asyncio.create_task(call, context=contextvars.Context())
                    await asyncio.sleep(0.2)
                    assert not task.done(), "authentication failed before the local writer released its transaction"
                    await holder.rollback()
            response = await asyncio.wait_for(task, 3)
            assert response.status_code == 200, response.text
            if operation == "login":
                assert response.json()["authenticated"] is True
            else:
                payload = response.json()
                assert payload["method"] == "browser"
                status = await async_client.get("/api/oauth/status", params={"flowId": payload["flowId"]})
                assert status.status_code == 200 and status.json()["status"] == "pending"
    finally:
        event.remove(engine.sync_engine, "checkout", short_busy_timeout)
        if task is not None:
            await asyncio.gather(task, return_exceptions=True)
        await oauth._OAUTH_STORE.reset()
