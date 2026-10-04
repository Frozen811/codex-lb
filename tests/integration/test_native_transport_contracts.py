from __future__ import annotations

import asyncio
import contextlib
import errno
import ipaddress
import json
import ssl
from collections.abc import AsyncIterator
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone

import aiohttp
import h2.config
import h2.connection
import h2.events
import pytest
import zstandard
from aiohttp import web
from aiohttp.client_reqrep import ConnectionKey
from aiohttp.test_utils import TestServer
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from sqlalchemy import select

from app.core.clients import http as http_clients
from app.core.clients import proxy as core_proxy
from app.core.clients.native_egress import NativeEgressRequest
from app.core.openai.requests import ResponsesRequest
from app.core.resilience import network_recovery
from app.core.utils.sse import parse_sse_data_json
from app.db.models import Account, AccountStatus, ApiKeyUsageReservation, RequestLog
from app.db.session import SessionLocal
from app.dependencies import get_proxy_service_for_app
from app.modules.proxy import service as proxy_service
from tests.integration import test_native_sse_egress as native_sse
from tests.integration.model_source_helpers import _enable_api_key_auth
from tests.integration.test_native_sse_egress import (
    _finish_chunks,
    _serve_http,
    _start_chunked_response,
    _write_chunk,
)
from tests.integration.test_proxy_transient_retry import _import_account, _success_sse_event

pytestmark = pytest.mark.integration
native_worker = native_sse.native_worker


def _created(response_id: str) -> bytes:
    return (
        "data: "
        + json.dumps({"type": "response.created", "response": {"id": response_id, "status": "in_progress"}})
        + "\n\n"
    ).encode()


@dataclass
class _H2Origin:
    url: str = ""
    connections: dict[str, list[int]] = field(default_factory=dict)
    active: dict[str, tuple[h2.connection.H2Connection, asyncio.StreamWriter, int]] = field(default_factory=dict)
    started: dict[str, asyncio.Event] = field(default_factory=lambda: {key: asyncio.Event() for key in ("a", "b")})
    hold: bool = False
    requests: list[tuple[list[tuple[str, str]], bytes]] = field(default_factory=list)
    stream_window: int | None = None
    connection_window: int | None = None

    async def complete(self, account: str) -> None:
        connection, writer, stream_id = self.active[account]
        connection.send_data(stream_id, _success_sse_event(f"resp_{account}").encode(), end_stream=True)
        writer.write(connection.data_to_send())
        await writer.drain()


@pytest.fixture
async def h2_origin(tmp_path, monkeypatch) -> AsyncIterator[_H2Origin]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "native-loopback-test")])
    now = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]), critical=False)
        .sign(key, hashes.SHA256())
    )
    root_path = tmp_path / "ca.pem"
    root_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    cert = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "native-loopback-origin")]))
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]), critical=False)
        .sign(key, hashes.SHA256())
    )
    cert_path = tmp_path / "origin.pem"
    key_path = tmp_path / "origin.key"
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(
        key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    )
    monkeypatch.setenv("SSL_CERT_FILE", str(root_path))
    monkeypatch.setenv("SSL_CERT_DIR", str(tmp_path))
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_path, key_path)
    context.set_alpn_protocols(["h2"])
    origin = _H2Origin()
    tasks: set[asyncio.Task] = set()
    writers: set[asyncio.StreamWriter] = set()
    connection_ids: list[int] = []

    async def serve(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        task = asyncio.current_task()
        assert task is not None
        tasks.add(task)
        writers.add(writer)
        connection_id = len(connection_ids)
        connection_ids.append(connection_id)
        connection = h2.connection.H2Connection(h2.config.H2Configuration(client_side=False, header_encoding="utf-8"))
        accounts: dict[int, str] = {}
        request_headers: dict[int, list[tuple[str, str]]] = {}
        bodies: dict[int, bytearray] = {}
        try:
            assert writer.get_extra_info("ssl_object").selected_alpn_protocol() == "h2"
            connection.initiate_connection()
            writer.write(connection.data_to_send())
            await writer.drain()
            while data := await reader.read(65536):
                for event in connection.receive_data(data):
                    if isinstance(event, h2.events.RequestReceived):
                        accounts[event.stream_id] = dict(event.headers)["chatgpt-account-id"]
                        request_headers[event.stream_id] = event.headers
                        bodies[event.stream_id] = bytearray()
                    elif isinstance(event, h2.events.DataReceived):
                        connection.acknowledge_received_data(event.flow_controlled_length, event.stream_id)
                        bodies[event.stream_id].extend(event.data)
                    elif isinstance(event, h2.events.RemoteSettingsChanged):
                        origin.stream_window = connection.remote_settings.initial_window_size
                    elif isinstance(event, h2.events.WindowUpdated) and event.stream_id == 0:
                        origin.connection_window = connection.outbound_flow_control_window
                    elif isinstance(event, h2.events.StreamEnded):
                        origin.requests.append((request_headers[event.stream_id], bytes(bodies[event.stream_id])))
                        account = accounts[event.stream_id]
                        origin.connections.setdefault(account, []).append(connection_id)
                        origin.active[account] = connection, writer, event.stream_id
                        connection.send_headers(
                            event.stream_id, [(":status", "200"), ("content-type", "text/event-stream")]
                        )
                        connection.send_data(event.stream_id, _created(f"resp_{account}"))
                        if origin.hold:
                            origin.started[account].set()
                        else:
                            connection.send_data(
                                event.stream_id, _success_sse_event(f"resp_{account}").encode(), end_stream=True
                            )
                writer.write(connection.data_to_send())
                await writer.drain()
        except (ConnectionError, ssl.SSLError):
            pass
        finally:
            writers.discard(writer)
            writer.close()
            with contextlib.suppress(ConnectionError, ssl.SSLError):
                await writer.wait_closed()
            tasks.discard(task)

    server = await asyncio.start_server(serve, "127.0.0.1", 0, ssl=context)
    origin.url = f"https://127.0.0.1:{server.sockets[0].getsockname()[1]}"
    try:
        yield origin
    finally:
        server.close()
        await server.wait_closed()
        for writer in tuple(writers):
            writer.close()
        for task in tuple(tasks):
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


@pytest.mark.asyncio
async def test_native_http2_wire_json_compression_and_identity(h2_origin, native_worker, monkeypatch):
    monkeypatch.setattr(core_proxy, "resolve_http_proxy_from_env", lambda _url: None)
    payload = ResponsesRequest(model="gpt-5.1", instructions="", input="wire profile", stream=True)
    headers = {"user-agent": "codex_cli_rs/0.150.1", "originator": "codex_cli_rs", "version": "0.150.1"}
    for _ in range(2):
        async with aiohttp.ClientSession() as session:
            result = [
                event
                async for event in core_proxy.stream_responses(
                    payload,
                    headers,
                    "synthetic-token",
                    "a",
                    base_url=h2_origin.url,
                    session=session,
                    native_egress_client=native_worker,
                    upstream_stream_transport_override="http",
                    raise_for_status=True,
                )
            ]
            assert any("response.completed" in event for event in result)
    assert len(h2_origin.requests) == 2
    first_headers, first_body = h2_origin.requests[0]
    emitted = dict(first_headers)
    assert emitted["content-encoding"] == "zstd"
    decoded = zstandard.ZstdDecompressor().decompress(first_body)
    assert json.loads(decoded)["input"] == payload.input
    assert emitted["content-length"] == str(len(first_body))
    assert emitted["authorization"] == "Bearer synthetic-token"
    assert emitted["user-agent"] == headers["user-agent"]
    assert "accept-encoding" not in emitted and "connection" not in emitted and "x-request-id" not in emitted
    assert all(name == name.lower() for name, _ in first_headers)
    assert h2_origin.requests[1][1] == first_body
    assert h2_origin.stream_window == 2 * 1024 * 1024
    assert h2_origin.connection_window == 5 * 1024 * 1024


@pytest.mark.asyncio
@pytest.mark.parametrize("compressed", [False, True], ids=["opaque-body", "stale-encoding-headers"])
async def test_native_body_representation_is_explicit(h2_origin, native_worker, compressed):
    body = b'{"input":"exact bytes \\u2603"}'
    headers = {"chatgpt-account-id": "a", "content-type": "application/json"}
    if compressed:
        headers.update({"Content-Encoding": "identity", "Content-Length": "99999"})
    response = await native_worker.request(
        NativeEgressRequest(
            method="POST",
            url=h2_origin.url + "/codex/responses",
            headers=headers,
            body=body,
            compress_json=compressed,
        )
    )
    async with response:
        assert b"response.completed" in await response.read()
    emitted_headers, emitted_body = h2_origin.requests[0]
    emitted = dict(emitted_headers)
    if compressed:
        assert emitted["content-encoding"] == "zstd"
        assert zstandard.ZstdDecompressor().decompress(emitted_body) == body
    else:
        assert "content-encoding" not in emitted
        assert emitted_body == body
    assert emitted["content-length"] == str(len(emitted_body))
    assert "Content-Encoding" not in emitted and "Content-Length" not in emitted


@pytest.mark.asyncio
@pytest.mark.parametrize("partitioned", [True, False], ids=["account-pools", "shared-pool-control"])
async def test_real_native_http2_account_isolation_and_reuse(h2_origin, native_worker, monkeypatch, partitioned):
    monkeypatch.setattr(core_proxy, "resolve_http_proxy_from_env", lambda _url: None)
    if not partitioned:
        original_request = native_worker.request

        async def shared_pool_request(request):
            return await original_request(replace(request, pool_key=None))

        monkeypatch.setattr(native_worker, "request", shared_pool_request)

    async def stream(account):
        async with aiohttp.ClientSession() as session:
            return [
                block
                async for block in core_proxy.stream_responses(
                    ResponsesRequest(model="gpt-5.1", instructions="", input="pool isolation", stream=True),
                    {},
                    "synthetic-token",
                    account,
                    base_url=h2_origin.url,
                    session=session,
                    native_egress_client=native_worker,
                    upstream_stream_transport_override="http",
                    raise_for_status=True,
                )
            ]

    for _ in range(2):
        assert any("response.completed" in block for block in await stream("a"))
    assert len(set(h2_origin.connections["a"])) == 1
    h2_origin.hold = True
    a = asyncio.create_task(stream("a"))
    b = asyncio.create_task(stream("b"))
    try:
        await asyncio.wait_for(asyncio.gather(*(event.wait() for event in h2_origin.started.values())), timeout=5)
        assert (h2_origin.active["a"][1] is not h2_origin.active["b"][1]) == partitioned
        h2_origin.active["a"][1].transport.abort()
        failed = await asyncio.wait_for(a, timeout=5)
        assert not any("response.completed" in block for block in failed)
        assert any("native upstream response body failed" in block for block in failed)
        if partitioned:
            assert not b.done()
            await h2_origin.complete("b")
            assert any("response.completed" in block for block in await asyncio.wait_for(b, timeout=5))
        else:
            peer_failure = await asyncio.wait_for(b, timeout=5)
            assert not any("response.completed" in block for block in peer_failure)
            assert any("native upstream response body failed" in block for block in peer_failure)
        assert h2_origin.connections["a"] == [0, 0, 0]
        assert h2_origin.connections["b"] == [int(partitioned)]
    finally:
        for task in (a, b):
            if not task.done():
                task.cancel()
        await asyncio.gather(a, b, return_exceptions=True)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "winerror,pre_dispatch", [(1231, False), (1232, False), (1231, True), (1232, True), (64, False), (121, False)]
)
async def test_windows_route_recovery_retires_real_shared_generation(
    async_client, app_instance, monkeypatch, winerror, pre_dispatch
):
    owner = await _import_account(async_client, "windows-owner", "windows@example.invalid")
    attempts: list[aiohttp.ClientSession] = []
    upstream_bodies: list[dict] = []

    async def upstream(request):
        upstream_bodies.append(await request.json())
        return web.Response(text=_success_sse_event(), content_type="text/event-stream")

    application = web.Application()
    application.router.add_post("/codex/responses", upstream)
    monkeypatch.setattr(core_proxy, "discover_native_egress_client", lambda: None)
    monkeypatch.setattr(network_recovery, "backoff_seconds", lambda _attempt: 0)
    original_post = aiohttp.ClientSession.post

    async with TestServer(application) as server, http_clients.lease_http_session() as failed_session:

        def post(session, url, **kwargs):
            attempts.append(session)
            if len(attempts) == 1:
                error = OSError(errno.EINVAL, "synthetic Windows route loss")
                error.winerror = winerror
                if pre_dispatch:
                    error = aiohttp.ClientConnectorError(
                        ConnectionKey("127.0.0.1", server.port, False, False, None, None, None), error
                    )
                raise error
            return original_post(session, url, **kwargs)

        monkeypatch.setattr(aiohttp.ClientSession, "post", post)

        def actual_stream(payload, headers, token, account_id, **kwargs):
            return core_proxy.stream_responses(
                payload,
                headers,
                token,
                account_id,
                base_url=str(server.make_url("/")),
                upstream_stream_transport_override="http",
                raise_for_status=True,
            )

        monkeypatch.setattr(proxy_service, "core_stream_responses", actual_stream)
        response = await async_client.post(
            "/backend-api/codex/responses", json={"model": "gpt-5.1", "input": "hi", "stream": True}
        )
        replacement = http_clients.get_http_client().session
        route_loss = winerror in {1231, 1232}
        assert (replacement is not failed_session) == route_loss
        assert not failed_session.closed
        assert attempts[0] is failed_session
        assert len(attempts) == (2 if pre_dispatch else 1)
        assert len(upstream_bodies) == int(pre_dispatch)
        if pre_dispatch:
            assert attempts[1] is replacement
            assert "response.completed" in response.text
        elif route_loss:
            assert "proxy_network_unavailable" in response.text
        else:
            assert "upstream_unavailable" in response.text
            assert "proxy_network_unavailable" not in response.text
        service = get_proxy_service_for_app(app_instance)
        assert await service.drain_persistence_tasks(timeout_seconds=5)
        runtime = service._load_balancer._runtime[owner]
        if route_loss:
            assert runtime.error_count == 0 and runtime.last_error_at is None
        assert await service._load_balancer.account_pressure_snapshot(owner) == (0, 0, 0.0)
        async with SessionLocal() as database:
            account = await database.get(Account, owner)
            assert account is not None and account.status == AccountStatus.ACTIVE
            logs = list(await database.scalars(select(RequestLog)))
            assert len(logs) == 1 + int(pre_dispatch)
            assert all(log.account_id == owner for log in logs)
            if not pre_dispatch:
                assert logs[0].error_code == ("proxy_network_unavailable" if route_loss else "upstream_unavailable")
    if route_loss:
        async with asyncio.timeout(2):
            while not failed_session.closed:
                await asyncio.sleep(0)
    else:
        assert not failed_session.closed


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True])
@pytest.mark.parametrize("outcome", ["eof", "body_failure", "head_failure"])
@pytest.mark.parametrize(
    "path,native_client",
    [
        ("/v1/responses", False),
        ("/backend-api/codex/responses", False),
        ("/backend-api/codex/responses", True),
    ],
)
async def test_native_direct_failures_release_real_admission_and_reservations(
    async_client, app_instance, monkeypatch, native_worker, stream, outcome, path, native_client
):
    await _enable_api_key_auth(async_client)
    owner = await _import_account(async_client, "lease-owner", "lease@example.invalid")
    settings = await async_client.put(
        "/api/settings",
        json={
            "proxyAccountResponseCreateLimit": 1,
            "proxyAccountStreamLimit": 1,
            "proxyAccountStreamRecoveryReserve": 0,
            "upstreamStreamTransport": "http",
        },
    )
    assert settings.status_code == 200
    created = await async_client.post(
        "/api/api-keys/",
        json={
            "name": "native-cleanup",
            "assignedAccountIds": [owner],
            "limits": [{"limitType": "total_tokens", "limitWindow": "weekly", "maxValue": 10000}],
        },
    )
    assert created.status_code == 200
    key = created.json()["key"]
    headers = {"Authorization": f"Bearer {key}"}
    if native_client:
        headers.update({"originator": "codex_cli_rs", "User-Agent": "codex_cli_rs/0.116.0"})
    calls: list[dict] = []

    async def upstream(reader, writer, head, body):
        payload = json.loads(body)
        calls.append(payload)
        if len(calls) <= 2 and outcome == "head_failure":
            writer.transport.abort()
            return
        upstream_stream = payload.get("stream", True)
        await _start_chunked_response(
            writer, content_type="text/event-stream" if upstream_stream else "application/json"
        )
        if len(calls) <= 2:
            await _write_chunk(writer, _created(f"resp_{len(calls)}") if upstream_stream else b'{"id":')
            if outcome == "eof":
                await _finish_chunks(writer)
            else:
                writer.transport.abort()
        else:
            completed = _success_sse_event("resp_after_failures")
            if upstream_stream:
                await _write_chunk(writer, _created("resp_after_failures"))
                await _write_chunk(writer, completed.encode())
            else:
                response = parse_sse_data_json(completed)["response"]
                response["status"] = "completed"
                await _write_chunk(writer, json.dumps(response).encode())
            await _finish_chunks(writer)

    monkeypatch.setattr(core_proxy, "resolve_http_proxy_from_env", lambda _url: None)
    service = get_proxy_service_for_app(app_instance)
    async with _serve_http(upstream) as base_url:

        def actual_stream(payload, headers, token, account_id, **kwargs):
            return core_proxy.stream_responses(
                payload,
                headers,
                token,
                account_id,
                base_url=base_url,
                upstream_stream_transport_override="http",
                native_egress_client=native_worker,
                raise_for_status=True,
                failure_trace=kwargs.get("failure_trace"),
            )

        monkeypatch.setattr(proxy_service, "core_stream_responses", actual_stream)
        for index in range(3):
            try:
                response = await async_client.post(
                    path,
                    headers=headers,
                    json={"model": "gpt-5.1", "input": "cleanup", "stream": stream},
                )
            except core_proxy.ProxyResponseError as exc:
                assert native_client and stream and index < 2
                assert exc.payload["error"]["code"] == "stream_incomplete"
                response = None
            if response is not None:
                assert "account_stream_cap" not in response.text
                assert "failure_phase" not in response.text
                assert "native_transport_error" not in response.text
            assert await service.drain_persistence_tasks(timeout_seconds=5)
            assert await service._load_balancer.account_pressure_snapshot(owner) == (0, 0, 0.0)
            assert not native_worker._streams
            async with SessionLocal() as database:
                reservations = list(await database.scalars(select(ApiKeyUsageReservation)))
                assert len(reservations) == index + 1
                assert all(row.status in {"released", "finalized"} for row in reservations)
                logs = list(await database.scalars(select(RequestLog)))
                assert len(logs) == index + 1
                if index < 2 and outcome != "eof":
                    assert logs[-1].failure_phase == ("body_read" if outcome == "body_failure" else "request")
                    assert logs[-1].failure_detail == "native_transport_error"
                    assert logs[-1].failure_exception_type == "NativeEgressTransportError"
                    assert logs[-1].upstream_status_code == (200 if outcome == "body_failure" else None)
            if index < 2:
                if response is not None:
                    assert "response.completed" not in response.text
                    assert response.status_code in {200, 502}
            elif stream:
                assert response is not None
                assert any(
                    event.get("type") == "response.completed"
                    for block in response.text.split("\n\n")
                    if (event := parse_sse_data_json(block)) is not None
                )
            else:
                assert response is not None
                assert response.status_code == 200, response.text
                assert response.json()["id"] == "resp_after_failures"
    assert len(calls) == 3
