## Overview

`database-migrations` capability defines how codex-lb evolves schema safely across fresh installs, partially migrated legacy DBs, and ongoing branch development.

## Scope and Non-Goals

- Scope:
  - Runtime startup migration behavior
  - Legacy history bootstrap/remap behavior
  - Revision naming and head governance
  - CI migration guardrails
- Non-goals:
  - Designing rollback SQL for every migration
  - Supporting alternate revision ID formats
  - Maintaining compatibility with unknown third-party Alembic revisions

## Key Decisions

- Alembic is the runtime SSOT for migrations.
- Revision IDs use `YYYYMMDD_HHMMSS_slug` for readability and merge-conflict reduction.
- Legacy IDs are auto-remapped at startup to avoid manual DB patching during cutover.
- CI checks both policy (head/naming) and drift in one command path.
- Schema upgrades and stamps are serialized across processes by a cross-process migration lock (see Operational Notes); losing replicas wait, re-inspect, and skip when the schema is already at head.
- `alembic_version` revisions unknown to the running build are reported as schema-ahead ("not known to this build") rather than "behind Alembic head".

## Constraints

- Legacy `schema_migrations` rows are historical input only.
- One migration executor at a time is enforced by the migration lock (`run_upgrade`/`stamp_revision` paths); direct `alembic` CLI invocations bypass it and remain the operator's responsibility.
- Unsupported `alembic_version` IDs fail fast to avoid silent divergence, with direction-correct diagnostics (schema-ahead vs schema-behind).
- Startup also verifies post-upgrade schema drift before the app begins normal work.

## Failure Modes and Mitigations

- Multiple Alembic heads caused by parallel branches:
  - Mitigation: CI fails; add merge revision before merge/release.
- Legacy revision IDs still present in operator DB:
  - Mitigation: startup auto-remap of known IDs.
- Unknown revision IDs in `alembic_version`:
  - Mitigation: explicit startup failure + manual operator intervention.
- Drift between metadata and migrated schema:
  - Mitigation: CI unified migration check blocks merge.
  - Runtime mitigation: startup drift check logs explicit diffs and fails startup when `database_migrations_fail_fast=true`.

## Operational Notes

- Startup path:
  - (SQLite integrity check, optional SQLite backup) -> acquire migration lock -> inspect state (skip if already at head) -> bootstrap legacy `schema_migrations` -> remap legacy Alembic IDs -> `upgrade head` -> release lock -> schema drift check
- Migration lock (serializes `run_upgrade` and `stamp_revision` across replicas):
  - PostgreSQL: session-level `pg_try_advisory_lock(hashtext('codex_lb:migrations'))` polled every 2s on a dedicated AUTOCOMMIT connection held for the whole upgrade; released explicitly and automatically on holder death. Caveat: transaction-pooling proxies (PgBouncer in transaction mode) break session advisory locks — point `CODEX_LB_DATABASE_URL` at the database directly, or at a session-pooling endpoint, if replicas migrate on startup.
  - File-backed SQLite: an exclusive `BEGIN IMMEDIATE` write transaction on a sentinel SQLite file `<db_path>.migrate-lock` adjacent to the database. The sentinel is created on first use and intentionally never deleted (a harmless zero-row SQLite file); OS-level SQLite locks vanish on process death. Caveat: on NFS this inherits SQLite's known NFS locking unreliability — no worse than the main database itself.
  - In-memory SQLite: no-op (the database is process-private).
  - Direct `alembic upgrade` (bypassing `python -m app.db.migrate`) does not take the lock; `alembic_version` capacity bootstrap uses `CREATE TABLE IF NOT EXISTS` as defense-in-depth, but out-of-band invocations should still be serialized by the operator.
- Lock timeout tuning:
  - `CODEX_LB_DATABASE_MIGRATION_LOCK_TIMEOUT_SECONDS` (default 300, matching `wait-for-head`) bounds how long a replica waits for a peer's migration. On timeout the error names the lock and this setting; the startup path honors `database_migrations_fail_fast`, the CLI always exits non-zero. Raise it for deployments whose migrations legitimately run long.
- Multi-replica deployment contract:
  - Either keep `database_migrate_on_startup=true` on every replica (the lock makes concurrent boots safe: one replica applies, the rest wait and skip), or disable it and run a dedicated migration Job while app replicas use `python -m app.db.migrate wait-for-head` before starting.
- CLI checks:
  - `codex-lb-db check` validates head count, revision naming/filename policy, and schema drift.
- Emergency toggle:
  - `CODEX_LB_DATABASE_ALEMBIC_AUTO_REMAP_ENABLED=false` disables auto-remap.

## September overflow and transport merge

The subscription-overflow and transport-sentinel revisions both descended from
the quota-warmup revision. A forward merge joins them without changing their
operations. An upgrade from one parent applies the other parent normally;
downgrading only the merge restores both parent stamps while preserving both
schemas and their data. This is not a rollback to a build that knows only one
branch. See the [repair context](../../changes/merge-overflow-transport-migration-heads/context.md).

## Example

Branch A and B each create migration revisions in parallel. After merge, CI detects multiple heads and fails. The resolver adds a merge revision, reruns CI, and proceeds. During deployment, a DB still storing old `013_add_dashboard_settings_routing_strategy` in `alembic_version` is auto-remapped to `20260225_000000_add_dashboard_settings_routing_strategy` before upgrade.

## Revision progress and guarded rollback recovery

Online Alembic runs emit start and executed/failed records for each revision,
with direction and elapsed seconds. Alembic retains its migration selection,
version ledger and transaction ownership; temporary iterator instrumentation is
restored after success or failure. `Executed` describes completion of a step,
not the commit of an enclosing transaction. No-op runs produce no invented
revision progress. The migration CLI enables stderr logging and preserves its
stdout result, for example `current_revision=20261007_000000_add_account_quota_limit`.

These progress records omit SQL, parameters, URLs, descriptions and exception
messages. Existing outer error diagnostics are separate. A failed revision
propagates its original exception and prevents later steps from executing.

If a rollback image encounters an unknown ledger revision, the ordinary refusal
now includes conditional recovery guidance. Metadata-only stamping is applicable
only after schema/data compatibility is independently verified, all migration
transactions have ended, and the database backup and matching encryption key
are recoverable. Use a build containing both recorded and target revisions
against the same database. Stamping never reverses schema or data, and an older
build cannot stamp a revision absent from its scripts. After any authorized
recovery, check migration policy, schema drift and application behavior before
resuming traffic. The command does not perform these operator decisions for you.

For example, restoring an old image against a newer database still fails. The
operator can restore its paired snapshot or inspect compatibility from a newer
build; the diagnostic itself performs no repair or stamp.

## Existing quota storage during ledger recovery

The [quota recovery contract](spec.md#requirement-quota-restriction-storage-survives-ledger-recovery)
handles a schema with an existing quota restriction column and a missing or
rewound Alembic ledger. The published quota-only revision stays immutable.
Under the migration lock, recovery resolves the original upgrade plan, checks
for a nullable Float column without a server default, applies pending ancestors,
then records just the quota-only revision without duplicate DDL. Existing legacy
and retired-credential normalization still run first. Incompatible quota storage
fails before this reconciliation proceeds; arbitrary ancestors are not inferred
from one column's presence.

For example, an account with a 37.5% restriction retains that value and its
encrypted credentials after loss of the ledger. A `+1` target from the quota
revision's parent ends at the same resolved revision. Missing facet indexes
still get rebuilt by their pending ancestor before the quota stamp. Ordinary
installs without the column execute the original additive migration.

## Fork account reserves completed on 2026-10-09

The prior scalar-only partial status is superseded by the completed reserve integration. Shared and duration-matched 5-hour/weekly caps use the canonical fresh-data evaluator; disabled settings retain saved percentages, while removal clears them. Provider remaining stays in provider units; reserved and usable quota are shown separately, and weekly burn remains provider-scaled. A 20% reserve with 54% consumption gives 46% provider remaining and 26% usable quota.

The fork adds a single forward revision on its verified reset-threshold head. Legacy positive scalar values seed the shared policy and zero remains a hard denial. The legacy API updates the shared policy; the reserve API can disable/remove it. Backup carries the shared and override values. MySQL updates use the transaction-held row lock and projection instead of UPDATE RETURNING.

Fresh owner authorization retains strict revoked-credential handling and usable reauth warning behavior for manual warm-up. Selection retries are bounded at eight to let local and persisted invalidation echoes settle, with final current-owner refusal and complete lease cleanup under continuing churn. Foreground ranking ignores unavailable peers when choosing the best health tier but retains their hard-block evidence for canonical backoff fallback.

Code and tests are adapted from NikitaMGrimm's upstream PR #1528 at caf31b77a4ef85047459635e956fdd62f7fbd7ce; aaravrav is credited there for complementary reserve presentation. No old migration or prior archived evidence is rewritten. Local verification is separate from live providers, server backends and publication. See [requirements](spec.md).

## Synthetic migration timing and September lineage

The duration gate combines conservative raw-SQL checks with actual database execution. The static command is stdlib-only and runs in the existing lint path. It resolves literal/annotated assignments, concatenation and statically resolvable f-strings; all possible assigned values are considered. Explicit primary-key range parameters provide a supported batch proof; unrelated LIMIT text, negative predicates and correlated subqueries do not. Arbitrary dynamic SQL and SQLAlchemy expression trees still need actual execution evidence.

Run `uv run python -m scripts.benchmark_migrations --base-ref latest-stable --output timings.json` with `MIGRATION_BENCHMARK_SERVER_URL` identifying a disposable test PostgreSQL server. The runner creates a fresh random database, migrates the baseline schema, generates three million synthetic request logs by default and measures each pending revision through the ordinary runner. Fixture generation and baseline setup are excluded from revision timings. `--rows` and `--budget-seconds` adjust the fixture and the default thirty-second budget without adding application settings. A no-op baseline reports zero seeded rows and no invented timings.

For example, a revision that executes a 200 ms sleep under a 10 ms statement budget fails with a private exception type, the failed revision's elapsed time and a non-zero exit. JSON remains available even on failure, and cleanup removes only the runner's newly created database. A missing server, unknown baseline or cleanup failure remains a failed benchmark. The workflow publishes timing artifacts and a job summary for scheduled, migration-path and manual runs; its checked-in configuration is distinct from an observed hosted run or required branch-protection status.

The September pair remains `20260914_000000_add_scim_tokens` and `20260914_000000_drop_subscription_overflow_schema`, joined by the published `20260918_000000_merge_scim_and_overflow_heads`. The rejected restamping proposal is not needed for single-head behavior and would orphan published ledgers. Only that exact pair after convergence receives the collision exemption. An extra member or a new collision still fails, even after an empty merge. Both-parent ledgers, merge reversal and unrelated populated rows have independent local regression coverage. See [requirements](spec.md).

Synthetic timings depend on hardware, distribution and selected revision range; they do not prove production timing, PostgreSQL 16 hosted behavior or every historical migration's performance. Background data phases belong to the separate open proposal and are not established by this gate.

## Sticky timing replay compatibility

Legacy bootstrap and whole-chain replay can start with tables built from current ORM metadata while the Alembic ledger predates the timing revision. Adding the column again fails on SQLite, PostgreSQL and MySQL. The newly introduced timing revision therefore inspects storage before additive DDL, following the adjacent source-catalog migration's approach. Revision identity, parent and downgrade remain intact; historical upstream revisions are not rewritten.

For example, a settings row already holding `after_compaction` retains that value when its older ledger upgrades to head. A row without timing storage receives `immediate`. Existence alone does not certify an incompatible precreated column: the normal startup drift guard still rejects a divergent schema. Real roundtrip, legacy startup and credential-preservation tests cover this behavior; local SQLite results and hosted server-backend results remain separate evidence. See [requirements](spec.md).
