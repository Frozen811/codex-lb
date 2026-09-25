from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.db.models import Account
from app.modules.proxy.model_account_routing import (
    apply_model_account_routing,
    clear_model_account_routes,
    find_matching_account,
    get_model_account_routes,
    normalize_model_slug,
    parse_model_account_routing_header,
    register_model_account_route,
    resolve_model_account_target,
    set_model_account_routes,
)


@pytest.fixture(autouse=True)
def clean_registry():
    clear_model_account_routes()
    yield
    clear_model_account_routes()


def test_normalize_model_slug():
    assert normalize_model_slug("  GPT-5.6-sol ") == "gpt-5.6-sol"
    assert normalize_model_slug(None) == ""
    assert normalize_model_slug("") == ""


def test_parse_model_account_routing_header():
    # JSON syntax
    header_json = json.dumps({"GPT-5.6-sol": "acc-1", "gpt-5.6-luna": "acc-2"})
    assert parse_model_account_routing_header(header_json) == {
        "gpt-5.6-sol": "acc-1",
        "gpt-5.6-luna": "acc-2",
    }

    # Comma-separated key-value syntax
    header_kv = "gpt-5.6-sol = acc-1 , gpt-5.6-luna=acc-2"
    assert parse_model_account_routing_header(header_kv) == {
        "gpt-5.6-sol": "acc-1",
        "gpt-5.6-luna": "acc-2",
    }

    # Empty or invalid
    assert parse_model_account_routing_header("") == {}
    assert parse_model_account_routing_header(None) == {}


def test_registry_routes():
    register_model_account_route("gpt-5.6-sol", "acc-target-1")
    assert get_model_account_routes() == {"gpt-5.6-sol": "acc-target-1"}

    set_model_account_routes({"gpt-5.6-luna": "acc-target-2"})
    assert get_model_account_routes() == {"gpt-5.6-luna": "acc-target-2"}


def test_resolve_model_account_target_precedence(tmp_path: Path):
    config_file = tmp_path / "model_account_routing.json"
    config_file.write_text(json.dumps({"gpt-5.6-sol": "acc-file"}), encoding="utf-8")

    register_model_account_route("gpt-5.6-sol", "acc-registered")

    # File only
    assert resolve_model_account_target("gpt-5.6-sol", config_path=config_file) == "acc-registered"

    # Header overrides registered and file
    headers = {"x-codex-model-account-routing": "gpt-5.6-sol=acc-header"}
    assert (
        resolve_model_account_target("gpt-5.6-sol", headers=headers, config_path=config_file)
        == "acc-header"
    )

    # Registered overrides file
    clear_model_account_routes()
    assert resolve_model_account_target("gpt-5.6-sol", config_path=config_file) == "acc-file"


def test_find_matching_account():
    acc1 = MagicMock(spec=Account)
    acc1.id = "acc-uuid-1"
    acc1.email = "alice@example.com"
    acc1.alias = "alice-personal"
    acc1.chatgpt_account_id = "org-chatgpt-1"

    acc2 = MagicMock(spec=Account)
    acc2.id = "acc-uuid-2"
    acc2.email = "bob@example.com"
    acc2.alias = "bob-work"
    acc2.chatgpt_account_id = "org-chatgpt-2"

    accounts = [acc1, acc2]

    assert find_matching_account("acc-uuid-1", accounts) is acc1
    assert find_matching_account("alice@example.com", accounts) is acc1
    assert find_matching_account("Alice@Example.Com", accounts) is acc1
    assert find_matching_account("bob-work", accounts) is acc2
    assert find_matching_account("org-chatgpt-2", accounts) is acc2
    assert find_matching_account("non-existent", accounts) is None


@pytest.mark.asyncio
async def test_apply_model_account_routing_matching():
    acc1 = MagicMock(spec=Account)
    acc1.id = "acc-uuid-1"
    acc1.email = "alice@example.com"
    acc1.alias = "alice-personal"
    acc1.chatgpt_account_id = "org-chatgpt-1"

    repo = MagicMock()
    repo.list_accounts = AsyncMock(return_value=[acc1])

    register_model_account_route("gpt-5.6-sol", "acc-uuid-1")

    # Successful match
    res = await apply_model_account_routing(
        model="gpt-5.6-sol",
        headers=None,
        preferred_account_id=None,
        fallback_on_preferred_account_unavailable=True,
        required_preferred_account=False,
        single_account_routing_id=None,
        routing_strategy="least_utilized",
        accounts_repo=repo,
        excluded_account_ids_set=set(),
        scoped_account_ids=None,
    )
    assert res.error is None
    assert res.preferred_account_id == "acc-uuid-1"
    assert res.fallback is False
    assert res.required is True
    assert res.strategy == "single_account"
    assert res.single_id == "acc-uuid-1"


@pytest.mark.asyncio
async def test_apply_model_account_routing_failures():
    acc1 = MagicMock(spec=Account)
    acc1.id = "acc-uuid-1"
    acc1.email = "alice@example.com"
    acc1.alias = "alice-personal"
    acc1.chatgpt_account_id = "org-chatgpt-1"

    repo = MagicMock()
    repo.list_accounts = AsyncMock(return_value=[acc1])

    # 1. Target account does not exist
    register_model_account_route("gpt-5.6-sol", "missing-acc")
    res1 = await apply_model_account_routing(
        model="gpt-5.6-sol",
        headers=None,
        preferred_account_id=None,
        fallback_on_preferred_account_unavailable=True,
        required_preferred_account=False,
        single_account_routing_id=None,
        routing_strategy="least_utilized",
        accounts_repo=repo,
        excluded_account_ids_set=set(),
        scoped_account_ids=None,
    )
    assert res1.error is not None
    assert res1.error.error_code == "model_account_not_found"

    # 2. Target account excluded
    register_model_account_route("gpt-5.6-sol", "acc-uuid-1")
    res2 = await apply_model_account_routing(
        model="gpt-5.6-sol",
        headers=None,
        preferred_account_id=None,
        fallback_on_preferred_account_unavailable=True,
        required_preferred_account=False,
        single_account_routing_id=None,
        routing_strategy="least_utilized",
        accounts_repo=repo,
        excluded_account_ids_set={"acc-uuid-1"},
        scoped_account_ids=None,
    )
    assert res2.error is not None
    assert res2.error.error_code == "model_account_unavailable"

    # 3. Target account outside scoped_account_ids
    res3 = await apply_model_account_routing(
        model="gpt-5.6-sol",
        headers=None,
        preferred_account_id=None,
        fallback_on_preferred_account_unavailable=True,
        required_preferred_account=False,
        single_account_routing_id=None,
        routing_strategy="least_utilized",
        accounts_repo=repo,
        excluded_account_ids_set=set(),
        scoped_account_ids={"acc-uuid-2"},
    )
    assert res3.error is not None
    assert res3.error.error_code == "model_account_scope_mismatch"
