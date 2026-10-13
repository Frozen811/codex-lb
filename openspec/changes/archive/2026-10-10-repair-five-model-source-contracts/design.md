## Context

See proposal.md. CPA helpers have no runtime caller. Main specs already require configure-once discovery. Source rows and background model refresh provide the existing persistence and scheduling boundaries.

## Goals / Non-Goals

Implement durable discovery without a new scheduler, environment setting or provider dependency. Preserve the fork's compact refusal; remote source compact forwarding and live CPA acceptance are outside this change.

## Decisions

- Add manual/default and cli_proxy_api catalog modes, a monotonically incremented catalog revision and model availability separate from operator enablement. Manual pauses survive omission/restoration.
- The existing leader model-refresh tick runs discovery even with no subscription accounts. Four workers share five seconds; each request has a 1 MiB body limit and rejects redirects. Catalogs contain at most 1000 unique, bounded, typed Codex model claims.
- Claim and apply use the durable revision. Every operator mutation increments it in SQL, preventing stale configuration or overlapping fetches from overwriting current rows. Workers own separate sessions; HTTP fetches hold no database transaction. Last-good rows are the persistent snapshot.
- Native catalog collisions retain existing precedence. Disabled/unavailable source identities still block native fallback. Continuation reconciliation runs before source denial, including when a source has become unavailable.
- Use one forward migration on the current fork head; never import the upstream PR's merge revisions.

## Risks / Trade-offs

Provider metadata is a claim, not runtime proof. The existing five-minute tick means initial discovery can wait up to one interval. Invalid, oversized or unreachable catalogs retain existing data. Live provider acceptance remains separate evidence.

## Migration Plan

Backfill existing sources as manual and models as available. Verify upgrade, replay, downgrade/re-upgrade and schema drift on disposable databases. Keep source credentials and child identities intact.
