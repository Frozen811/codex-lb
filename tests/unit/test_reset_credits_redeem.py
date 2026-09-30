from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.requests import Request

from app.core.exceptions import ProxyAuthError
from app.modules.proxy.api import (
    ConsumeRateLimitResetCreditRequest,
    codex_consume_rate_limit_reset_credit,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_codex_consume_rate_limit_reset_credit_rejects_target_without_chatgpt_account_id():
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/backend-api/rate_limit_reset_credits/consume",
        "headers": [(b"content-type", b"application/json")],
        "state": {"codex_usage_identity_account_id": "caller-acc"},
    }
    request = Request(scope)

    mock_credentials = MagicMock()
    mock_credentials.access_token_encrypted = b"dummy"
    mock_credentials.chatgpt_account_id = None

    with (
        patch("app.modules.proxy.api._find_target_reset_credit_account", return_value=("target-acc", "req-123")),
        patch(
            "app.modules.proxy.api._ensure_v1_reset_credit_account_fresh",
            new_callable=AsyncMock,
            return_value=mock_credentials,
        ),
        patch("app.modules.proxy.api.TokenEncryptor.decrypt", return_value="decrypted-token"),
        patch(
            "app.modules.proxy.api._required_capability_http_transport_denial",
            new_callable=AsyncMock,
            return_value=None,
        ),
    ):
        with pytest.raises(ProxyAuthError, match="Target account has no ChatGPT account ID"):
            await codex_consume_rate_limit_reset_credit(
                request=request,
                payload=ConsumeRateLimitResetCreditRequest(redeem_request_id="req-123"),
                api_key=None,
            )
