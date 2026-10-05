## Why

Three unverified registry tasks concern quota warm-up: UP-ISSUE-1895, UP-ISSUE-1976, and UP-ISSUE-1975. The compact fallback still sends an unsupported output limit and can report premature EOF as success; sliding idle deadlines can change the durable deduplication key within one stable cycle.

## What Changes

- Require an actual completed fallback response and omit unsupported output limits.
- Use the stable idle cycle for both slot scheduling and durable deduplication, including slot zero.
- Independently verify persisted live-reset recovery across fresh-poll skips, restarts, and duplicate workers.
- Close exactly these three registry rows with scoped local evidence.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `proxy-warmup`: plain fallback payload compatibility and terminal success evidence.
- `usage-refresh-policy`: stable sliding-cycle claims and durable live-reset evaluation.

## Impact

Warm-up API submission, limit warm-up scheduling, focused integration tests, and OpenSpec context. No new dependencies, settings, database revisions, or dashboard controls. Existing opt-in defaults and account ownership remain in effect.
