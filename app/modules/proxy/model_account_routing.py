from __future__ import annotations

import json
import logging
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.db.models import Account
    from app.modules.accounts.repository import AccountsRepository

from app.modules.proxy.load_balancer import AccountSelection

logger = logging.getLogger(__name__)

# In-memory registry for strict model-to-account routes
_MODEL_ACCOUNT_ROUTES: dict[str, str] = {}
_CONFIG_FILE_CACHE: dict[str, tuple[float, dict[str, str]]] = {}

MODEL_ACCOUNT_ROUTING_HEADER = "x-codex-model-account-routing"
DEFAULT_CONFIG_PATH = Path("config/model_account_routing.json")


def normalize_model_slug(model: str | None) -> str:
    if not model or not isinstance(model, str):
        return ""
    return model.strip().lower()


def register_model_account_route(model: str, target: str) -> None:
    norm = normalize_model_slug(model)
    if norm and target.strip():
        _MODEL_ACCOUNT_ROUTES[norm] = target.strip()


def set_model_account_routes(routes: Mapping[str, str]) -> None:
    _MODEL_ACCOUNT_ROUTES.clear()
    for model, target in routes.items():
        register_model_account_route(model, target)


def get_model_account_routes() -> dict[str, str]:
    return dict(_MODEL_ACCOUNT_ROUTES)


def clear_model_account_routes() -> None:
    _MODEL_ACCOUNT_ROUTES.clear()
    _CONFIG_FILE_CACHE.clear()


def parse_model_account_routing_header(header_val: str | None) -> dict[str, str]:
    if not header_val or not isinstance(header_val, str):
        return {}
    cleaned = header_val.strip()
    if not cleaned:
        return {}
    if cleaned.startswith("{") and cleaned.endswith("}"):
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                return {normalize_model_slug(k): str(v).strip() for k, v in parsed.items() if k and v}
        except Exception:
            pass
    # Support comma-separated key-value pairs: "gpt-5.6-sol=acc1,gpt-5.6-luna=acc2"
    result: dict[str, str] = {}
    for part in cleaned.split(","):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            norm_k = normalize_model_slug(k)
            val = v.strip()
            if norm_k and val:
                result[norm_k] = val
    return result


def _load_config_file_routes(path: Path = DEFAULT_CONFIG_PATH) -> dict[str, str]:
    try:
        if not path.is_file():
            return {}
        mtime = path.stat().st_mtime
        cached = _CONFIG_FILE_CACHE.get(str(path))
        if cached is not None and cached[0] == mtime:
            return cached[1]
        data = json.loads(path.read_text(encoding="utf-8"))
        routes: dict[str, str] = {}
        if isinstance(data, dict):
            for k, v in data.items():
                norm = normalize_model_slug(k)
                if norm and isinstance(v, str) and v.strip():
                    routes[norm] = v.strip()
        _CONFIG_FILE_CACHE[str(path)] = (mtime, routes)
        return routes
    except Exception as exc:
        logger.debug("Failed reading model account routing config %s: %s", path, exc)
        return {}


def resolve_model_account_target(
    model: str | None,
    *,
    headers: Mapping[str, str] | None = None,
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> str | None:
    norm_model = normalize_model_slug(model)
    if not norm_model:
        return None

    # 1. Check request header
    if headers:
        for k, v in headers.items():
            if k.lower() == MODEL_ACCOUNT_ROUTING_HEADER:
                header_routes = parse_model_account_routing_header(v)
                if norm_model in header_routes:
                    return header_routes[norm_model]

    # 2. Check in-memory registered routes
    if norm_model in _MODEL_ACCOUNT_ROUTES:
        return _MODEL_ACCOUNT_ROUTES[norm_model]

    # 3. Check config file
    file_routes = _load_config_file_routes(config_path)
    if norm_model in file_routes:
        return file_routes[norm_model]

    return None


def find_matching_account(target: str, accounts: Iterable[Account]) -> Account | None:
    if not target or not isinstance(target, str):
        return None
    cleaned = target.strip()
    cleaned_lower = cleaned.lower()

    # Exact ID match
    for acc in accounts:
        if acc.id == cleaned:
            return acc
    # Exact email match
    for acc in accounts:
        if acc.email == cleaned or (acc.email and acc.email.lower() == cleaned_lower):
            return acc
    # Exact alias match
    for acc in accounts:
        if acc.alias == cleaned or (acc.alias and acc.alias.lower() == cleaned_lower):
            return acc
    # ChatGPT account ID match
    for acc in accounts:
        if acc.chatgpt_account_id == cleaned:
            return acc

    return None


@dataclass(slots=True)
class ModelRoutingOverride:
    preferred_account_id: str | None
    fallback: bool
    required: bool
    single_id: str | None
    strategy: str
    error: AccountSelection | None = None


async def apply_model_account_routing(
    *,
    model: str | None,
    headers: Mapping[str, str] | None,
    preferred_account_id: str | None,
    fallback_on_preferred_account_unavailable: bool,
    required_preferred_account: bool,
    single_account_routing_id: str | None,
    routing_strategy: str = "default",
    accounts_repo: AccountsRepository | None = None,
    repo_factory: Any = None,
    excluded_account_ids_set: set[str],
    scoped_account_ids: set[str] | None,
) -> ModelRoutingOverride:
    default_res = ModelRoutingOverride(
        preferred_account_id=preferred_account_id,
        fallback=fallback_on_preferred_account_unavailable,
        required=required_preferred_account,
        single_id=single_account_routing_id,
        strategy=routing_strategy,
    )
    if not model or required_preferred_account:
        return default_res

    target_spec = resolve_model_account_target(model, headers=headers)
    if target_spec is None:
        return default_res

    if accounts_repo is not None:
        all_pool_accounts = await accounts_repo.list_accounts()
    elif repo_factory is not None:
        async with repo_factory() as repos:
            all_pool_accounts = await repos.accounts.list_accounts()
    else:
        all_pool_accounts = []
    target_account = find_matching_account(target_spec, all_pool_accounts)
    if target_account is None:
        default_res.error = AccountSelection(
            account=None,
            error_message=f"Configured strict model routing account '{target_spec}' for model '{model}' does not exist",
            error_code="model_account_not_found",
        )
        return default_res

    if target_account.id in excluded_account_ids_set:
        default_res.error = AccountSelection(
            account=None,
            error_message=f"Strict model routing target account '{target_spec}' for model '{model}' is unavailable",
            error_code="model_account_unavailable",
        )
        return default_res

    if scoped_account_ids is not None and target_account.id not in scoped_account_ids:
        default_res.error = AccountSelection(
            account=None,
            error_message=f"Strict model routing target account '{target_spec}' is outside the API key account scope",
            error_code="model_account_scope_mismatch",
        )
        return default_res

    return ModelRoutingOverride(
        preferred_account_id=target_account.id,
        fallback=False,
        required=True,
        single_id=target_account.id,
        strategy="single_account",
    )
