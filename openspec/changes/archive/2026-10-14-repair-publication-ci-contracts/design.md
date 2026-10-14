## Context

See proposal.md. Legacy bootstrap and replay tests create a schema from current ORM metadata, then reconcile an older Alembic ledger. That schema already includes sticky timing even though the additive revision is still pending. The adjacent source-catalog revision already checks column existence.

## Goals / Non-Goals

Preserve existing settings and credentials through startup reconciliation. Keep the same migration revision, parent, default and downgrade. Historical upstream revisions, routing policy and deployment configuration remain outside this repair.

## Decisions

Inspect `dashboard_settings` and skip the additive DDL when the timing column exists. This preserves operator-selected values and works across SQLite, PostgreSQL and MySQL. A later corrective revision cannot repair an earlier failing upgrade; the newly introduced revision is still in its initial CI verification and has not shipped in a release.

Parameterize the real migration roundtrip for both missing and precreated timing storage. Run the already-failing legacy startup and whole-chain replay suites. Make restored-store subprocess failures expose stderr while keeping their existing assertions.

Apply an idle lifetime minimum only when incoming affinity supplies a child TTL. Ordinary turn-state alias reuse must keep its existing Codex lifetime promotion. API-key test doubles must declare assignment-scope state. Request-log snapshots must include subscription-pool upstream options, and the existing PostgreSQL live-facet test must keep its model/API-key/status scope when new upstream probes are captured.

The Rust TLS dependency update is one patch version in the workspace manifest and its checksum/version in Cargo.lock. Keep the audit policy and enabled features intact.

SQLite can choose the visibility-leading index for a paired-facet NULL probe and scan every row even when the prefix has no NULL counterpart. First ask the existing pair index whether any raw NULL pair exists, using only its equality prefix. Only a positive result runs the original visibility probe. Results, soft-delete filtering and the unchanged VM-operation ceiling remain authoritative; the extra bounded query is confined to SQLite.

## Risks / Trade-offs

An existing incompatible column still belongs to the startup schema-drift guard; the existence check must not rewrite it. Local SQLite evidence cannot establish MySQL or PostgreSQL execution, so hosted CI remains required.
