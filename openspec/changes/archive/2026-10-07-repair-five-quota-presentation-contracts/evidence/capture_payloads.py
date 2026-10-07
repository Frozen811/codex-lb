"""Capture synthetic account summaries from the current implementation."""

from __future__ import annotations

import json
import sys
from datetime import timedelta
from pathlib import Path

from app.core.crypto import TokenEncryptor
from app.core.utils.time import naive_utc_to_epoch, utcnow
from app.db.models import Account, AccountStatus, UsageHistory
from app.modules.accounts.mappers import _account_to_summary

now = utcnow()
encryptor = TokenEncryptor()
account = Account(
    id="monthly-team",
    email="monthly@example.com",
    plan_type="team",
    status=AccountStatus.ACTIVE,
)
primary = UsageHistory(
    account_id=account.id,
    window="primary",
    used_percent=24.0,
    window_minutes=43800,
    reset_at=naive_utc_to_epoch(now + timedelta(days=30)),
    recorded_at=now,
)
secondary = UsageHistory(account_id=account.id, window="secondary", used_percent=0.0, window_minutes=0, recorded_at=now)
summary = _account_to_summary(
    account=account,
    primary_usage=primary,
    secondary_usage=secondary,
    monthly_usage=None,
    request_usage=None,
    additional_quotas=None,
    limit_warmup=None,
    encryptor=encryptor,
    include_auth=False,
)
target = Path(__file__).parent / f"{sys.argv[1]}-payload.json"
target.write_text(json.dumps(summary.model_dump(mode="json", by_alias=True), indent=2) + "\n")
