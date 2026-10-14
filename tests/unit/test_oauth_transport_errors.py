from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

import aiohttp
import pytest

from app.core.clients import oauth

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["exchange_authorization_code", "request_device_code"])
@pytest.mark.parametrize("failure", [aiohttp.ClientConnectionError, aiohttp.ClientPayloadError, TimeoutError])
async def test_direct_oauth_transport_errors_are_sanitized(monkeypatch, operation, failure):
    released = []

    class Session:
        def post(self, *args, **kwargs):
            raise failure("private-url?code=secret&verifier=private")

    @asynccontextmanager
    async def lease(session):
        try:
            yield Session()
        finally:
            released.append(True)

    monkeypatch.setattr(oauth, "lease_http_session", lease)
    kwargs = {"code": "synthetic", "code_verifier": "synthetic"} if operation == "exchange_authorization_code" else {}
    with pytest.raises(oauth.OAuthError) as error:
        await getattr(oauth, operation)(allow_direct_egress=True, **kwargs)
    assert error.value.code == "transport_error"
    assert error.value.message == "Unable to connect to the OAuth server. Please try again."
    assert released == [True]


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["exchange_authorization_code", "request_device_code"])
async def test_direct_oauth_cancellation_propagates_and_releases_session(monkeypatch, operation):
    released = []

    class Session:
        def post(self, *args, **kwargs):
            raise asyncio.CancelledError

    @asynccontextmanager
    async def lease(session):
        try:
            yield Session()
        finally:
            released.append(True)

    monkeypatch.setattr(oauth, "lease_http_session", lease)
    kwargs = {"code": "synthetic", "code_verifier": "synthetic"} if operation == "exchange_authorization_code" else {}
    with pytest.raises(asyncio.CancelledError):
        await getattr(oauth, operation)(allow_direct_egress=True, **kwargs)
    assert released == [True]
