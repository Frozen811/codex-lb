## Why

The registry marks targeted session repair as implemented, but the CLI only exposes provider retagging. Operators cannot inspect JSONL/SQLite disagreement or explicitly repair one session with fresh identity checks. Three client-example rows also lack independent evidence.

## What Changes

- Add read-only `codex-sessions preview` and explicitly confirmed, ID-scoped `repair` for `openai` and `codex-lb` metadata.
- Reuse bounded metadata reads, streaming rewrite and existing backup facilities; reject ambiguous, unsupported, missing and stale targets.
- Verify five ordinary search-capability blocks and Astra examples without changing model catalog, protocol, provider selection or client configuration.
- Close exactly UP-ISSUE-1636, UP-PR-2323, UP-ISSUE-2311, UP-ISSUE-2498 and UP-PR-2516 in verified local scope.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `conversations-api`: read-only mismatch inspection and safe targeted metadata repair.
- `user-documentation`: ordinary provider examples declare supported standalone search consistently.

## Impact

`app/cli.py`, new `app/codex_sessions_repair.py`, focused CLI tests, `tests/unit/test_client_setup_examples.py`, `docs/conversations.md`, and owning OpenSpec specs/context. Existing retag code is reused. No dependencies, server settings, migration, dashboard navigation or README section changes.
