## Why

Scheduled retry-circuit cleanup can delete protection after only its failure detail changes. Five unverified registry entries also need current, independently executed evidence for scheduled cleanup, quarantine provenance, probe ownership and incomplete-terminal accounting.

## What Changes

- Fence scheduled purge on the selected null-safe failure detail as well as timestamp, admission generation and failure count (UP-PR-2280).
- Add database regression/control coverage for detail-only updates, NULL transitions and mixed batches without reselecting changed candidates.
- Verify existing session/generation quarantine cleanup and local provenance through real HTTP completion races (UP-PR-2276 and UP-PR-2345).
- Verify existing half-open admission/return and reason-only incomplete accounting with focused lifecycle and product-route tests (UP-PR-1962 and UP-PR-2278).
- Close exactly these five local registry scopes with explicit evidence and external limits.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: extend Retry Circuit Scheduled Purge Fencing to include null-safe failure detail and its detail-only race scenarios.

## Impact

Implementation: `app/modules/proxy/durable_bridge_repository.py`.
New regression suites: `tests/integration/test_retry_cleanup_batch.py` and `tests/unit/test_retry_cleanup_contracts.py`.
SSOT: `openspec/specs/responses-api-compat/spec.md` and its `context.md`.
Evidence and status: this change folder and `issues-check.md`.
Existing bridge retry/quarantine implementations and their tests are inspected and verified; changes there require a reproduced defect within these five entries. No settings, schema, dashboard, dependency or wire-format changes are planned.
