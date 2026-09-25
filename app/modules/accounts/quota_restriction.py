from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# In-memory registry for per-account quota limit restrictions (percentage 0.0 - 100.0)
_ACCOUNT_QUOTA_RESTRICTIONS: dict[str, float] = {}


def set_account_quota_restriction(account_id: str, limit_percent: float | None) -> None:
    """Set or clear a custom quota percentage limit for an account."""
    if not account_id:
        return
    if limit_percent is None:
        _ACCOUNT_QUOTA_RESTRICTIONS.pop(account_id, None)
        logger.info("Cleared quota limit restriction for account_id=%s", account_id)
    else:
        clamped = max(0.0, min(100.0, float(limit_percent)))
        _ACCOUNT_QUOTA_RESTRICTIONS[account_id] = clamped
        logger.info("Set quota limit restriction for account_id=%s to %.1f%%", account_id, clamped)


def get_account_quota_restriction(account_id: str) -> float | None:
    """Get the configured quota limit percentage for an account, if any."""
    return _ACCOUNT_QUOTA_RESTRICTIONS.get(account_id)


def get_all_account_quota_restrictions() -> dict[str, float]:
    """Return all configured account quota limit restrictions."""
    return dict(_ACCOUNT_QUOTA_RESTRICTIONS)


def clear_account_quota_restrictions() -> None:
    """Clear all configured account quota limit restrictions."""
    _ACCOUNT_QUOTA_RESTRICTIONS.clear()


def is_account_quota_restricted(
    account_id: str,
    used_percent: float | None,
    secondary_used_percent: float | None = None,
) -> bool:
    """Check if an account has exceeded its configured quota limit restriction."""
    if not account_id:
        return False
    limit = _ACCOUNT_QUOTA_RESTRICTIONS.get(account_id)
    if limit is None:
        return False
    if used_percent is not None and used_percent >= limit:
        return True
    if secondary_used_percent is not None and secondary_used_percent >= limit:
        return True
    return False
