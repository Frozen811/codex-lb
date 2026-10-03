from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from hashlib import sha256

import pytest
from aiohttp import web

from app.core.auth import refresh as refresh_module
from app.core.auth.refresh import RefreshError
from app.core.crypto import TokenEncryptor
from app.core.utils.time import utcnow
from app.db.models import Account, AccountStatus
from app.db.session import SessionLocal
from app.modules.accounts.auth_manager import AuthManager
from app.modules.accounts.repository import AccountsRepository

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@pytest.mark.parametrize("private_first", [False, True])
@pytest.mark.parametrize(
    ("code", "status", "expected_code", "permanent"),
    [
        ("refresh_token_revoked", 401, "refresh_token_revoked", False),
        ("refresh_token_invalidated", 401, "refresh_token_invalidated", True),
        ("refresh_token_expired", 400, "refresh_token_expired", True),
        ("QA_PROVIDER_CODE\nforged-log", 503, "other", False),
        (None, 429, "http_429", False),
    ],
)
async def test_refresh_http_failure_is_correlatable_without_provider_content(
    async_client, monkeypatch, caplog, unused_tcp_port, private_first, code, status, expected_code, permanent
) -> None:
    encryptor = TokenEncryptor()
    account = Account(
        id=f"QA_PRIVATE_ACCOUNT-{expected_code}-{private_first}",
        email="qa-private@example.invalid",
        plan_type="plus",
        access_token_encrypted=encryptor.encrypt("QA_ACCESS"),
        refresh_token_encrypted=encryptor.encrypt("QA_REFRESH"),
        id_token_encrypted=encryptor.encrypt("QA_ID_TOKEN"),
        last_refresh=utcnow(),
        status=AccountStatus.ACTIVE,
    )
    ciphertexts = (account.access_token_encrypted, account.refresh_token_encrypted, account.id_token_encrypted)
    started = asyncio.Event()
    release = asyncio.Event()
    calls = 0

    async def fail_refresh(request: web.Request) -> web.Response:
        nonlocal calls
        payload = await request.json()
        assert payload["grant_type"] == "refresh_token"
        assert payload["refresh_token"] == "QA_REFRESH"
        calls += 1
        started.set()
        await asyncio.wait_for(release.wait(), timeout=5)
        return web.json_response({"error": {"code": code, "message": "QA_PROVIDER_BODY"}}, status=status)

    @asynccontextmanager
    async def fresh_repository() -> AsyncIterator[AccountsRepository]:
        async with SessionLocal() as session:
            yield AccountsRepository(session)

    upstream = web.Application()
    upstream.router.add_post("/oauth/token", fail_refresh)
    runner = web.AppRunner(upstream, access_log=None)
    tasks: list[asyncio.Task[Account]] = []
    await runner.setup()
    try:
        await web.TCPSite(runner, "127.0.0.1", unused_tcp_port).start()
        monkeypatch.setattr(refresh_module, "AUTH_BASE_URL", f"http://127.0.0.1:{unused_tcp_port}")
        async with SessionLocal() as session:
            session.add(account)
            await session.commit()

        async with fresh_repository() as first_repo, fresh_repository() as second_repo:
            first = await first_repo.get_by_id_fresh(account.id)
            second = await second_repo.get_by_id_fresh(account.id)
            assert first is not None and second is not None
            first_manager = AuthManager(
                first_repo, refresh_repo_factory=fresh_repository, redact_sensitive_details=private_first
            )
            second_manager = AuthManager(
                second_repo, refresh_repo_factory=fresh_repository, redact_sensitive_details=not private_first
            )
            with caplog.at_level(logging.WARNING):
                tasks.append(asyncio.create_task(first_manager.ensure_fresh(first, force=True)))
                try:
                    await asyncio.wait_for(started.wait(), timeout=5)
                except TimeoutError:
                    if tasks[0].done():
                        tasks[0].result()
                    raise
                tasks.append(asyncio.create_task(second_manager.ensure_fresh(second, force=True)))
                await asyncio.sleep(0)
                release.set()
                results = await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=5)
            assert calls == 1
            assert all(isinstance(result, RefreshError) and result.code == (code or "http_429") for result in results)

        warnings = [record for record in caplog.records if "OAuth refresh attempt failed" in record.getMessage()]
        assert len(warnings) == 1
        diagnostic = warnings[0].getMessage()
        assert f"account_ref={sha256(account.id.encode()).hexdigest()[:16]}" in diagnostic
        assert f"code={expected_code} permanent={permanent} transport=False" in diagnostic
        assert warnings[0].exc_info is None
        for sentinel in (
            account.id,
            account.email,
            "QA_ACCESS",
            "QA_REFRESH",
            "QA_ID_TOKEN",
            "QA_PROVIDER_BODY",
            "QA_PROVIDER_CODE",
            "forged-log",
        ):
            assert sentinel not in caplog.text
        async with fresh_repository() as repo:
            stored = await repo.get_by_id_fresh(account.id)
            assert stored is not None
            assert stored.status == (AccountStatus.REAUTH_REQUIRED if permanent else AccountStatus.ACTIVE)
            assert (
                stored.access_token_encrypted,
                stored.refresh_token_encrypted,
                stored.id_token_encrypted,
            ) == ciphertexts
    finally:
        release.set()
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await runner.cleanup()
