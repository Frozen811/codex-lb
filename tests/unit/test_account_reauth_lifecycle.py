from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.core.auth.refresh import RefreshError
from app.db.models import Account, AccountStatus
from app.modules.accounts.auth_manager import AuthManager

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_reauth_required_emits_audit_event() -> None:
    repo = AsyncMock()
    auth_manager = AuthManager(repo=repo)

    account = Account(
        id="acc-test-reauth",
        email="test@example.com",
        status=AccountStatus.ACTIVE,
        access_token_encrypted=b"enc_acc",
        refresh_token_encrypted=b"enc_ref",
        last_refresh=100.0,
    )

    repo.get_by_id_fresh.return_value = account
    repo.update_status_if_current.return_value = True

    exc = RefreshError(
        code="token_invalidated",
        message="Token was invalidated",
        is_permanent=True,
    )

    from app.modules.accounts.auth_manager import _refresh_token_material_fingerprint

    attempted_fp = _refresh_token_material_fingerprint(auth_manager._encryptor, account.refresh_token_encrypted)

    with patch("app.core.audit.service.AuditService.log_async") as mock_log:
        await auth_manager._handle_permanent_refresh_failure(
            account=account,
            exc=exc,
            attempted_fingerprint=attempted_fp,
            deadline=None,
        )

        assert account.status == AccountStatus.REAUTH_REQUIRED
        assert mock_log.called
        call_args = mock_log.call_args
        assert call_args[0][0] == "account_reauth_required"
        details = call_args[1]["details"]
        assert details["account_id"] == "acc-test-reauth"
        assert details["email"] == "test@example.com"
        assert details["code"] == "token_invalidated"


@pytest.mark.asyncio
async def test_persist_conflict_emits_audit_event() -> None:
    repo = AsyncMock()
    auth_manager = AuthManager(repo=repo)

    account = Account(
        id="acc-conflict",
        email="conflict@example.com",
        status=AccountStatus.ACTIVE,
        access_token_encrypted=b"enc_acc",
        refresh_token_encrypted=b"enc_ref",
        last_refresh=100.0,
    )

    repo.get_by_id_fresh.return_value = account
    repo.update_status_if_current.return_value = True

    with patch("app.core.audit.service.AuditService.log_async") as mock_log:
        await auth_manager._flag_persist_conflict_reauth(
            account=account,
            consumed_plaintext="old-token",
            expected_refresh_token_encrypted=b"enc_ref",
            deadline_elapsed=True,
        )

        assert account.status == AccountStatus.REAUTH_REQUIRED
        assert mock_log.called
        call_args = mock_log.call_args
        assert call_args[0][0] == "account_reauth_required"
        details = call_args[1]["details"]
        assert details["account_id"] == "acc-conflict"
        assert details["code"] == "token_persist_conflict"
