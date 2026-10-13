## Why

Five unverified registry records cover source compaction, CPA discovery and continuation ownership. The fork intentionally refuses source compaction, but CPA discovery has only unused helpers and cannot discover or persist a catalog.

## What Changes

- Implement opt-in `catalogMode: cli_proxy_api` using the inference-authenticated Codex catalog, with bounded refresh, durable last-good rows and unavailable identity retention.
- Fence stale refreshes against operator edits, preserve manual model pauses, and keep native registry and recorded continuation owners authoritative.
- Independently verify existing compact refusal and continuation cleanup; record the original forwarding proposal as incompatible with the fork's current compact contract.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `model-source-routing`: durable, bounded automatic discovery and unavailable routing.

## Impact

Model-source ORM/schema/service/repository/catalog, a discovery worker integrated into the existing model refresh scheduler, source refusal and continuity helpers, one forward migration, focused tests and exactly five issues-check rows. No new environment setting, dependency, frontend navigation or deployment change.
