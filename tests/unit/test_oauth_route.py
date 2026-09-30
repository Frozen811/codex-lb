from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.modules.oauth.service import _oauth_route

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_oauth_route_passes_intended_account_id_to_resolver():
    with (
        patch("app.modules.oauth.service.resolve_upstream_route", new_callable=AsyncMock) as mock_resolve,
        patch("app.modules.oauth.service._has_active_proxy_bindings", new_callable=AsyncMock) as mock_has_bindings,
    ):
        mock_has_bindings.return_value = True
        mock_resolve.return_value = None

        await _oauth_route(intended_account_id="acc-target-123")

        mock_resolve.assert_awaited_once()
        _, kwargs = mock_resolve.call_args
        assert kwargs["account_id"] == "acc-target-123"
        assert kwargs["scope"] == "account"
        assert kwargs["strict"] is None
        # _has_active_proxy_bindings should not even be called when intended_account_id is supplied
        mock_has_bindings.assert_not_called()


@pytest.mark.asyncio
async def test_oauth_route_new_login_keeps_bootstrap_rule():
    with (
        patch("app.modules.oauth.service.resolve_upstream_route", new_callable=AsyncMock) as mock_resolve,
        patch("app.modules.oauth.service._has_active_proxy_bindings", new_callable=AsyncMock) as mock_has_bindings,
    ):
        mock_has_bindings.return_value = True
        mock_resolve.return_value = None

        await _oauth_route()

        mock_resolve.assert_awaited_once()
        _, kwargs = mock_resolve.call_args
        assert kwargs["account_id"] is None
        assert kwargs["scope"] == "bootstrap"
        assert kwargs["strict"] is True
        mock_has_bindings.assert_awaited_once()
