from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.core.auth import AuthFile, AuthTokens, claims_from_auth
from app.db.models import Account
from app.modules.accounts.auth_manager import AuthManager, RefreshError
from app.modules.accounts.mappers import _build_auth_status


def test_claims_from_auth_with_access_token_and_metadata():
    auth = AuthFile(
        tokens=AuthTokens(
            access_token="token-xyz-123",
            id_token=None,
            refresh_token=None,
        ),
        email="corp-user@example.com",
        plan_type="enterprise",
        account_id="chatgpt-corp-org",
    )
    claims = claims_from_auth(auth)
    assert claims.email == "corp-user@example.com"
    assert claims.plan_type == "enterprise"
    assert claims.account_id == "chatgpt-corp-org"


def test_build_auth_status_non_refreshable():
    # Account with empty decrypted refresh token
    encryptor = MagicMock()
    encryptor.decrypt.side_effect = lambda val: "" if val == b"empty" else "some-token"

    account = MagicMock(spec=Account)
    account.refresh_token_encrypted = b"empty"
    account.id_token_encrypted = b""
    account.access_token_encrypted = b"token"
    account.access_token_expires_at = None
    account.last_refresh_at = None
    account.refresh_failure_count = 0
    account.refresh_error = None
    account.refresh_error_code = None

    status = _build_auth_status(account, encryptor)
    assert status.refresh.state == "non_refreshable"


@pytest.mark.asyncio
async def test_auth_manager_perform_refresh_fails_fast_on_non_refreshable():
    repo = MagicMock()
    manager = AuthManager(repo=repo)
    manager._encryptor = MagicMock()
    manager._encryptor.decrypt.return_value = ""

    account = MagicMock(spec=Account)
    account.id = "acc-non-refreshable"
    account.refresh_token_encrypted = b"empty"

    with pytest.raises(RefreshError) as exc_info:
        await manager._perform_refresh(account, refresh_token_encrypted=account.refresh_token_encrypted)

    assert exc_info.value.code == "non_refreshable_account"
    assert exc_info.value.is_permanent is True


@pytest.mark.asyncio
async def test_auth_manager_ensure_fresh_skips_non_refreshable():
    repo = MagicMock()
    manager = AuthManager(repo=repo)
    manager._encryptor = MagicMock()
    manager._encryptor.decrypt.return_value = ""

    account = MagicMock(spec=Account)
    account.id = "acc-non-refreshable"
    account.refresh_token_encrypted = b"empty"
    account.chatgpt_account_id = "already-set"

    # Should return account unchanged without performing refresh
    res = await manager.ensure_fresh(account)
    assert res is account
