from __future__ import annotations

import asyncio
import socket

import pytest
from aiohttp import web

from app.modules.oauth.service import OAuthCallbackServer

pytestmark = pytest.mark.unit


async def _handler(_request: web.Request) -> web.Response:
    return web.Response(text="synthetic callback")


@pytest.mark.asyncio
async def test_callback_bind_failure_releases_initialized_runner(unused_tcp_port):
    with socket.socket() as occupied:
        occupied.bind(("127.0.0.1", unused_tcp_port))
        occupied.listen()
        server = OAuthCallbackServer(_handler, port=unused_tcp_port)
        try:
            with pytest.raises(OSError):
                await server.start()
            assert server._runner is None
            assert server._site is None
        finally:
            await server.stop()
    # Failure did not leave a zombie site; the same object can retry the port.
    await server.start()
    await server.stop()


@pytest.mark.asyncio
async def test_callback_start_cancellation_cleans_runner(monkeypatch):
    reached_bind = asyncio.Event()

    async def blocked_start(_site):
        reached_bind.set()
        await asyncio.Event().wait()

    monkeypatch.setattr(web.TCPSite, "start", blocked_start)
    server = OAuthCallbackServer(_handler, port=0)
    task = asyncio.create_task(server.start())
    try:
        await asyncio.wait_for(reached_bind.wait(), timeout=2)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert server._runner is None
        assert server._site is None
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        await server.stop()
