from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest

from app.db.models import AccountStatus
from app.modules.proxy.account_cache import RoutingAvailabilityCache
from tests.unit.test_metrics import _fake_prometheus_client_module, _load_metrics_modules

pytestmark = pytest.mark.unit


@pytest.fixture
def prometheus_env(monkeypatch: pytest.MonkeyPatch) -> Any:
    prometheus_module, _ = _load_metrics_modules(monkeypatch, prometheus_client_module=_fake_prometheus_client_module())
    return prometheus_module


def test_record_account_metrics_populates_all_statuses(prometheus_env: Any) -> None:
    prometheus_env.record_account_metrics({})

    for status in AccountStatus:
        child = prometheus_env.accounts_total.samples.get((("status", status.value),))
        assert child is not None, f"Expected sample for status {status.value}"
        assert child.value == 0.0

    assert prometheus_env.accounts_available.root.value == 0.0


def test_record_account_metrics_with_accounts_and_unavailable_marks(prometheus_env: Any) -> None:
    statuses = {
        "acc-1": AccountStatus.ACTIVE,
        "acc-2": AccountStatus.ACTIVE,
        "acc-3": AccountStatus.RATE_LIMITED,
        "acc-4": AccountStatus.QUOTA_EXCEEDED,
        "acc-5": AccountStatus.DEACTIVATED,
    }

    # All active accounts are available initially
    prometheus_env.record_account_metrics(statuses, routing_unavailable_ids=())
    assert prometheus_env.accounts_total.samples[(("status", "active"),)].value == 2.0
    assert prometheus_env.accounts_total.samples[(("status", "rate_limited"),)].value == 1.0
    assert prometheus_env.accounts_total.samples[(("status", "quota_exceeded"),)].value == 1.0
    assert prometheus_env.accounts_total.samples[(("status", "deactivated"),)].value == 1.0
    assert prometheus_env.accounts_total.samples[(("status", "paused"),)].value == 0.0
    assert prometheus_env.accounts_total.samples[(("status", "reauth_required"),)].value == 0.0
    assert prometheus_env.accounts_available.root.value == 2.0

    # If acc-1 is routing unavailable, available accounts count drops to 1
    prometheus_env.record_account_metrics(statuses, routing_unavailable_ids={"acc-1"})
    assert prometheus_env.accounts_total.samples[(("status", "active"),)].value == 2.0
    assert prometheus_env.accounts_available.root.value == 1.0


@pytest.mark.asyncio
async def test_routing_availability_cache_updates_metrics(prometheus_env: Any) -> None:
    cache = RoutingAvailabilityCache()

    mock_db_accounts = [
        ("acc-1", AccountStatus.ACTIVE, None),
        ("acc-2", AccountStatus.ACTIVE, None),
        ("acc-3", AccountStatus.PAUSED, None),
    ]

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=SimpleNamespace(all=lambda: mock_db_accounts))
    mock_session.close = AsyncMock()
    mock_session.in_transaction = lambda: False
    mock_session.info = {}

    def _session_factory():
        return mock_session

    cache._session_factory = _session_factory

    await cache.refresh_from_db()

    assert prometheus_env.accounts_total.samples[(("status", "active"),)].value == 2.0
    assert prometheus_env.accounts_total.samples[(("status", "paused"),)].value == 1.0
    assert prometheus_env.accounts_available.root.value == 2.0

    # Mark acc-1 unavailable
    cache.mark_unavailable("acc-1")
    assert prometheus_env.accounts_available.root.value == 1.0

    # Clear acc-1 unavailable
    cache.clear_unavailable("acc-1")
    assert prometheus_env.accounts_available.root.value == 2.0

    # Reset cache
    cache.reset()
    assert prometheus_env.accounts_available.root.value == 0.0
    assert prometheus_env.accounts_total.samples[(("status", "active"),)].value == 0.0


def test_record_account_metrics_noop_when_prometheus_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    prometheus_module, _ = _load_metrics_modules(monkeypatch, prometheus_client_module=None)
    assert prometheus_module.PROMETHEUS_AVAILABLE is False
    assert prometheus_module.accounts_total is None
    assert prometheus_module.accounts_available is None

    # Must not raise
    prometheus_module.record_account_metrics({"acc-1": AccountStatus.ACTIVE})
