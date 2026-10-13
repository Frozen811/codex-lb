## Why

Five unverified source records describe HTTP bridge admission, creation ownership, transcript backlog and temporary capacity handling. Creation failure still leaves a predecessor task running, and late-anchor reservation reconciliation leaves the request's local admission estimate behind the persisted reservation.

## What Changes

- Cancel the owned creator when a creation slot fails, including an already completed waiter, without cancelling a replacement, handoff or the current task.
- Keep the local usage budget consistent with successful late-anchor reservation reconciliation before dispatch or lease reacquisition.
- Independently verify stale closed-handoff recovery, fair continuous transcript flushing and bounded, replay-safe capacity recovery at their product boundaries.
- Update exactly UP-ISSUE-2090, UP-ISSUE-1758, UP-ISSUE-1799, UP-PR-2303 and UP-ISSUE-1935 with local evidence and explicit source-policy limits.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: creation failure owns cancellation and late-anchor budgets remain consistent across durable and local admission.

## Impact

Runtime edits are limited to `app/modules/proxy/_service/http_bridge/helpers.py`, `app/modules/proxy/_service/api_key_usage.py` and the local-admission error branch in `app/modules/proxy/_service/http_bridge/request_submit.py`. New coverage lives in `tests/unit/test_bridge_admission_contracts.py` and `tests/integration/test_bridge_admission_contracts.py`; existing bridge, API-key, transcript and retry suites supply additional boundary evidence. Spec/context and `issues-check.md` are synchronized. No schema, configuration, frontend or publication change is planned.
