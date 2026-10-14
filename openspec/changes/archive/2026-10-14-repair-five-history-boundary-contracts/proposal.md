## Why

Five unverified registry records cover continuation classification, eventless streams, destructive history slimming, compaction-boundary stickiness and pre-visible image/quota recovery. A consumed tool call can still authorize a later orphan output, and ordinary sticky-thread requests currently opt into reallocation just like compaction.

## What Changes

- Match tool outputs to unconsumed preceding call occurrences when classifying a full resend (UP-ISSUE-2269).
- Add persisted `stickyReallocationTiming=after_compaction` as an operator opt-in; keep `immediate` as the compatible historical/default mode. Preserve hard owners and failure recovery (UP-ISSUE-986).
- Verify eventless bridge termination and cooldown retirement (UP-ISSUE-1942).
- Verify item-preserving historical artifact slimming and local rejection instead of transcript omission (UP-ISSUE-568).
- Verify inline-image quota recovery for status and event errors, portable retained history and owner-bound refusal (UP-ISSUE-1924).
- Update exactly these five registry rows with their supported evidence and explicit limits.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: occurrence-aware continuation classification and verified history/quota boundaries.
- `sticky-session-operations`: opt-in soft-affinity timing defers budget-pressure reallocation until explicit compaction.

## Impact

Focused support/affinity/selection changes, one dashboard database column and forward migration, settings API, disposable SQLite/PostgreSQL/MySQL and HTTP/WS regression coverage, owning specs/context and issues-check.md. No environment field, dependency or public publication. Timing is stored through the existing settings management API; no dashboard UI control is added.
