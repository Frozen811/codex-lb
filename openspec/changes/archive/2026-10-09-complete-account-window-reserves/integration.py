"""Prepare the reviewed three-way integration without changing app files."""

import json
import re
from pathlib import Path

root = Path(__file__).parent
plan = json.loads((root / "merge-plan.json").read_text())
work = Path(plan["staging_dir"])
pattern = r"^<<<<<<< current\n(.*?)^\|\|\|\|\|\|\| upstream-base\n(.*?)^=======\n(.*?)^>>>>>>> upstream\n"

for name in plan["conflicts"]:
    path = work / "result" / name
    contents = path.read_text(encoding="utf-8")
    counter = [0]

    def resolve(match):
        index = counter[0]
        counter[0] += 1
        current, base, upstream = match.groups()
        if not base.strip():
            return current + upstream
        if name == "app/core/balancer/logic.py":
            return upstream
        if name == "app/core/usage/refresh_scheduler.py":
            return current.replace(
                "                    previous_plan_types=",
                "                    usage_limit_secondary=after_secondary,\n"
                "                    usage_limit_monthly=after_monthly,\n"
                "                    previous_plan_types=",
            )
        if name.endswith("accounts/repository.py"):
            return current.replace("from sqlalchemy import and_,", "from sqlalchemy import Float, and_,")
        if name.endswith("accounts/service.py"):
            return upstream
        if name.endswith("sticky_selection.py"):
            if index == 0:
                return "            [*(budget_safe_states or best_health_drain_states), *usage_limit_blocked],\n"
            return current + (
                "        terminal_pool = ([*selection_pool, *usage_limit_blocked] "
                "if len(preferred_states) == len(best_health_states) else selection_pool)\n"
            )
        if name.endswith("streaming/retry.py"):
            return current.replace(
                "selection.error_code == USAGE_LIMIT_REACHED",
                "selection.error_code in {USAGE_LIMIT_REACHED, ACCOUNT_USAGE_LIMIT_REACHED_ERROR_CODE}",
            )
        if name.endswith("_service/warmup.py"):
            if index == 0:
                return "from contextlib import aclosing\nfrom dataclasses import dataclass, replace\n"
            if index == 1:
                return current + (
                    "from app.core.balancer.logic import ACCOUNT_USAGE_LIMIT_REACHED_ERROR_CODE, "
                    "ACCOUNT_USAGE_LIMIT_REACHED_ERROR_MESSAGE\n"
                )
            if index == 2:
                return current
        if name.endswith("websocket/mixin.py") and index == 2:
            return current
        if name.endswith("proxy/load_balancer.py") and index == 2:
            return upstream
        if name.endswith("proxy/service.py"):
            return current
        if name.endswith("quota_planner/warmup.py"):
            return upstream.replace(
                'usage_core.capacity_for_plan(account.plan_type, "monthly") is not None',
                "usage_core.supports_monthly_quota(account.plan_type)",
            )
        if name.endswith("usage/repository.py"):
            return current.replace(
                "from app.db.models import Account,", "from app.db.models import Account, AccountStatus,"
            )
        if name.endswith("usage/updater.py"):
            return upstream.replace(
                "usage_written = bool(entries)", "usage_written = any(_usage_entry_written(entry) for entry in entries)"
            ).replace(
                "await self._recover_quota_status_from_usage(account, "
                "primary=primary, secondary=secondary, monthly=monthly)",
                "await self._recover_quota_status_from_usage(account, primary=primary, secondary=secondary, "
                "monthly=monthly, probe_verified=probe_verified)",
            )
        if name.startswith("tests/") and name.endswith(
            ("test_proxy_utils.py", "test_proxy_websocket_model_source_guard.py")
        ):
            return current
        return current + upstream

    contents = re.sub(pattern, resolve, contents, flags=re.M | re.S)
    assert not re.search(r"^([<=>|])\1{6}", contents, re.M), name
    if name == "app/core/balancer/logic.py":
        contents = contents.replace(
            "_known_expired_reauth(state, current)", "_reauth_credentials_unavailable(state, current)"
        ).replace(
            "if state.status == AccountStatus.DEACTIVATED:\n            continue",
            "if state.blocks_routing:\n            continue",
        )
        previous = Path(name).read_text(encoding="utf-8")
        start = previous.index("        if state.quota_limit_percent is not None")
        end = previous.index("        if state.error_count >= ERROR_BACKOFF_THRESHOLD:", start)
        position = contents.index("        if state.error_count >= ERROR_BACKOFF_THRESHOLD:")
        contents = contents[:position] + previous[start:end] + contents[position:]
    path.write_text(contents, encoding="utf-8")

print("All staging conflict blocks resolved.")
