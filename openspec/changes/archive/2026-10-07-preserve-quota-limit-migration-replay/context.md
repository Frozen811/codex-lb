# Quota migration replay verification

Base: `8d5f9e99ce33687893200f8676838d04d924cf82`, following the CI #74/#75 repair.
[Full CI #76](https://github.com/Frozen811/codex-lb/actions/runs/37645052511)
completed all 35 jobs. Frontend coverage, Docker, Trivy publication and Windows
Startup passed, but bootstrap tests on SQLite/PostgreSQL/MySQL failed with
duplicate `quota_limit_percent` columns; required aggregates correctly failed.

The normal migration runner now recognizes only the exact published quota-only
revision when its nullable Float column without a default already exists. It
resolves the upgrade target before applying ancestors, runs those ancestors,
then records the quota-only revision and completes the original target. For
example, a 37.5% restriction and encrypted credentials survive a rewound or
missing ledger; dropped facet indexes are recreated before that stamp. An
incompatible column produces an explicit error. No published migration file or
backup implementation changed.

## Local evidence

- Before the runner fix, the first six new replay/incompatible-schema cases
  failed; the original upgrade/downgrade case passed.
- `uv run --no-sync pytest -q tests/integration/test_account_quota_limit_migration.py tests/integration/test_affinity_identity_migration.py tests/integration/test_affinity_observation_migration.py tests/integration/test_startup_bridge_cleanup.py tests/integration/test_dashboard_users_schema.py`: **42 passed**.
- `uv run --no-sync pytest -q tests/unit/test_db_migrate.py tests/integration/test_migrations.py`: **121 passed, 11 database-specific skipped, 1 failed**. The only failure is `test_create_sqlite_pre_migration_backup_preserves_source_mode`: Windows reports `0666` after `chmod(0600)`. Its backup code and test are unchanged; a separate single-case run reproduced this platform limitation. This local aggregate is not green. PostgreSQL/MySQL cases require cloud evidence.
- Scoped Ruff check/format and `ty check` for both modified Python files passed.
- Proxy architecture, cancellation safety and timing seam checks passed.
- Migration topology passed: 272 revisions, one unchanged head `20261007_000000_add_account_quota_limit`; published migration files compare unchanged against the original base `664c8b98f949329707e5cb4c62ab9ab522f26bcb`.
- Main specs and context are synced; strict OpenSpec validation passed all **68** capabilities and the change.

The change's local completeness/correctness/coherence checks cover every task
and all four scenarios. The POSIX backup residual is outside these edits and is
retained explicitly. A new full Linux CI run and the separate Windows workflow
must certify the follow-up's exact pushed SHA; production remains outside scope.
