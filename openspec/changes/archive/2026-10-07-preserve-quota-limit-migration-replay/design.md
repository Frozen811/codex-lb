## Context

See proposal.md. Existing recovery already re-stamps retired dashboard credentials from durable evidence, then replays subsequent ancestors. The newest quota migration adds a column unconditionally, so schemas with a lost or rewound ledger now fail at that final DDL.

## Goals / Non-Goals

Preserve account data and every migration ancestor. Keep published revisions immutable and make no general guesses about migration completion from arbitrary columns.

## Decisions

Use Alembic's existing upgrade-plan resolver under the migration lock to resolve the target before any intermediate upgrade changes the ledger. Only when the exact quota-only revision is pending and its column has the expected nullable Float shape with no default, upgrade to its single parent, stamp that revision and complete the originally resolved plan. Missing columns follow the original command; incompatible columns fail before this reconciliation writes. Existing legacy and credential-ledger normalization runs first, as before. This avoids editing the published revision or stamping unrelated ancestors from column evidence.

## Risks / Trade-offs

- Column presence cannot prove any earlier migration ran: apply all ancestors normally before the stamp.
- Relative targets depend on the initial ledger: save the planned final revision before the intermediate command.
- Existing integration tests intentionally remove or rewind ledgers; retain them as product-path regression coverage on all supported databases.
