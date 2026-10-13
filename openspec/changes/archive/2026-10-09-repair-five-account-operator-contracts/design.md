## Context
See proposal.md. Import returns a local identity derived from credentials and workspace metadata. Bulk redemption currently recreates credit identities after the account helper invalidates cache. Reset warm-up retains an operator control backed by an inactive legacy value.

## Goals / Non-Goals
Preserve account-owned state and existing API compatibility. Full upstream reserved-credit accounting, portable password encryption, production and provider verification are outside these local contracts.

## Decisions
- Apply only explicitly supplied backup metadata to the returned account ID; retain workspace identity; restore paused state without reactivating accounts paused by import routing policy. Explicit false and null values are meaningful.
- Check operator quota caps before backoff admission and independently of upstream standard-quota exemption. Reuse existing selector and cache invalidation.
- Fetch authoritative remaining credits through the existing account route after each successful bulk consume, with generation fencing. Never fabricate IDs or assume the consumed credit occupied the first position of an older snapshot.
- Map the public threshold attribute to a new active column initialized to zero. Keep the legacy mapped column, values and published migrations untouched. One new migration with a non-null zero server default handles existing rows across dialects.
- Apply the inclusive threshold to reset evidence's before sample and to matching monthly history on paid-to-Free transitions; retain current post-reset availability and sender safety checks.

## Risks / Trade-offs
Extra account-bound reads between bulk consumes can fail; preserve partial counts and return a per-account error. An operator opting into a positive warm-up floor intentionally reduces eligible resets. Live server databases and visual browser evidence remain separate from local SQLite/DDL and component tests.

## Migration Plan
Upgrade the single-head graph; add the active zero-default column while retaining legacy data. Downgrade removes only the new column; upgrading again resets the active policy to zero. No live database is modified by this task.

A compatible active column surviving a rewound ledger is verified and reused without changing its current value. Incompatible nullable/type/default shapes fail explicitly. Paid-to-Free zero-floor semantics are preserved; positive floors require a matching monthly baseline.
