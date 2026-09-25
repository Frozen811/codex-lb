from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.api_keys.repository import ApiKeyUsageTotals
from app.modules.api_keys.schemas import ApiKeyUsageResponse
from app.modules.api_keys.service import ApiKeysService

pytestmark = pytest.mark.unit

_NOW = datetime(2026, 9, 25, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.get_by_id = AsyncMock()
    repo.usage_7d = AsyncMock()
    repo.trends_by_key = AsyncMock(return_value=[])
    return repo


@pytest.mark.asyncio
async def test_get_key_usage_custom_days(mock_repo):
    service = ApiKeysService(mock_repo)

    mock_key = MagicMock()
    mock_key.id = "key-123"
    mock_repo.get_by_id.return_value = mock_key

    mock_repo.usage_7d.return_value = ApiKeyUsageTotals(
        total_tokens=1000,
        total_cost_usd=0.05,
        total_requests=10,
        cached_input_tokens=200,
        account_costs=[],
    )

    # Test 30 days
    result = await service.get_key_usage("key-123", days=30)
    assert result is not None
    assert result.key_id == "key-123"
    assert result.days == 30
    assert result.total_tokens == 1000
    assert result.total_cost_usd == 0.05

    # Check mock call arguments for since and until
    call_args = mock_repo.usage_7d.call_args[0]
    assert call_args[0] == "key-123"
    since, until = call_args[1], call_args[2]
    # difference should be approximately 30 days
    assert abs((until - since).total_seconds() - 30 * 86400) < 10

    # Test 7d backwards compatibility
    result_7d = await service.get_key_usage_7d("key-123")
    assert result_7d is not None
    assert result_7d.days == 7


@pytest.mark.asyncio
async def test_get_key_usage_not_found(mock_repo):
    service = ApiKeysService(mock_repo)
    mock_repo.get_by_id.return_value = None

    result = await service.get_key_usage("non-existent", days=14)
    assert result is None


@pytest.mark.asyncio
async def test_get_key_trends_custom_days(mock_repo):
    service = ApiKeysService(mock_repo)

    mock_key = MagicMock()
    mock_key.id = "key-123"
    mock_repo.get_by_id.return_value = mock_key

    result = await service.get_key_trends("key-123", days=14)
    assert result is not None
    assert result.key_id == "key-123"

    call_args = mock_repo.trends_by_key.call_args[0]
    assert call_args[0] == "key-123"
    since, until = call_args[1], call_args[2]
    assert abs((until - since).total_seconds() - 14 * 86400) < 10


def test_api_key_usage_response_schema():
    resp = ApiKeyUsageResponse(
        key_id="key-abc",
        days=30,
        total_tokens=5000,
        total_cost_usd=1.23,
        total_requests=42,
        cached_input_tokens=1000,
        account_costs=[],
    )
    assert resp.key_id == "key-abc"
    assert resp.days == 30
    data = resp.model_dump()
    assert data["days"] == 30
