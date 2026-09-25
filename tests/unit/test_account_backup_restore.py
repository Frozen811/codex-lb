from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.auth import AuthFile, AuthTokens
from app.db.models import Account, AccountStatus
from app.modules.accounts.schemas import (
    AccountBackupItem,
    AccountBackupRestoreRequest,
    CodexAuthTokens,
)
from app.modules.accounts.service import AccountsService


@pytest.mark.asyncio
async def test_accounts_service_export_backup():
    repo = AsyncMock()
    encryptor = MagicMock()
    encryptor.decrypt.side_effect = lambda val: (
        "decrypted-" + val.decode() if isinstance(val, bytes) else "decrypted"
    )

    acc1 = MagicMock(spec=Account)
    acc1.id = "acc-active"
    acc1.email = "active@example.com"
    acc1.alias = "primary-work"
    acc1.plan_type = "team"
    acc1.status = AccountStatus.ACTIVE
    acc1.routing_policy = "normal"
    acc1.limit_warmup_enabled = True
    acc1.chatgpt_account_id = "chatgpt-1"
    acc1.access_token_encrypted = b"access1"
    acc1.refresh_token_encrypted = b"refresh1"
    acc1.id_token_encrypted = b"id1"
    acc1.created_at = datetime.now(timezone.utc)
    acc1.delete_requested_at = None

    acc_deleted = MagicMock(spec=Account)
    acc_deleted.id = "acc-deleted"
    acc_deleted.delete_requested_at = datetime.now(timezone.utc)
    acc_deleted.status = AccountStatus.DEACTIVATED

    repo.list_accounts.return_value = [acc1, acc_deleted]

    service = AccountsService(repo=repo)
    service._encryptor = encryptor

    backup = await service.export_backup()

    assert backup.version == "1.0"
    assert backup.account_count == 1
    assert len(backup.accounts) == 1

    item = backup.accounts[0]
    assert item.id == "acc-active"
    assert item.email == "active@example.com"
    assert item.alias == "primary-work"
    assert item.plan_type == "team"
    assert item.limit_warmup is True
    assert item.tokens is not None
    assert item.tokens.access_token == "decrypted-access1"
    assert item.tokens.refresh_token == "decrypted-refresh1"
    assert item.tokens.id_token == "decrypted-id1"
    assert item.tokens.account_id == "chatgpt-1"


@pytest.mark.asyncio
async def test_accounts_service_restore_backup():
    repo = AsyncMock()
    service = AccountsService(repo=repo)
    service.import_account = AsyncMock()
    service.set_account_alias = AsyncMock()
    service.set_routing_policy = AsyncMock()
    service.set_limit_warmup_enabled = AsyncMock()

    tokens = CodexAuthTokens(
        access_token="tok-123",
        refresh_token="ref-123",
        id_token="id-123",
        account_id="chatgpt-acc-1",
    )
    item_valid = AccountBackupItem(
        id="acc-1",
        email="user1@example.com",
        alias="work-account",
        plan_type="pro",
        status="active",
        routing_policy="priority",
        limit_warmup=True,
        tokens=tokens,
    )
    item_no_tokens = AccountBackupItem(
        id="acc-2",
        email="user2@example.com",
        tokens=None,
    )

    # Let item 3 raise an error
    tokens_error = CodexAuthTokens(
        access_token="tok-err",
        refresh_token="ref-err",
        account_id="chatgpt-acc-err",
    )
    item_err = AccountBackupItem(
        id="acc-3",
        email="err@example.com",
        tokens=tokens_error,
    )

    async def _mock_import(auth: AuthFile):
        if auth.tokens.access_token == "tok-err":
            raise ValueError("Upstream auth rejected")
        return MagicMock()

    service.import_account.side_effect = _mock_import

    payload = AccountBackupRestoreRequest(
        accounts=[item_valid, item_no_tokens, item_err],
    )
    res = await service.restore_backup(payload)

    assert res.restored_count == 1
    assert res.skipped_count == 1
    assert res.failed_count == 1
    assert res.success is False
    assert len(res.errors) == 1
    assert "Upstream auth rejected" in res.errors[0]

    service.import_account.assert_any_call(
        AuthFile(
            tokens=AuthTokens(
                access_token="tok-123",
                refresh_token="ref-123",
                id_token="id-123",
            ),
            email="user1@example.com",
            plan_type="pro",
            account_id="chatgpt-acc-1",
        )
    )
    service.set_account_alias.assert_called_once_with("acc-1", "work-account")
    service.set_routing_policy.assert_called_once_with("acc-1", "priority")
    service.set_limit_warmup_enabled.assert_called_once_with("acc-1", True)
