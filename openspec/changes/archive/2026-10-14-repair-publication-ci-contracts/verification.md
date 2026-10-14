# Local verification

- Migration/startup/lifecycle/restore slice: `test_migrations.py`, `test_dashboard_users_schema.py`, `test_account_window_reserve_migration.py`, `test_affinity_observation_migration.py`, `test_lifecycle_history_batch.py`, `test_startup_bridge_cleanup.py`, `test_setup_process.py`, and the parameterized timing roundtrip: **111 passed, 11 skipped**. Skips are explicitly MySQL/PostgreSQL-only paths. Existing reflection and AnyIO deprecation warnings remain visible.
- Rust workspace all-target tests: **33 passed** after the rustls 0.23.46 patch. Rust formatting, all-feature Clippy with denied warnings, and the release native-egress build succeeded.
- Ruff, formatting, ty, migration topology and static migration safety succeeded. The graph remains single-head at `20261014_000000_add_sticky_reallocation_timing`.
- Final combined migration-unit/bridge/child HTTP/SQLite facet/repository slice: **55 passed, 1 skipped**. The skip is the PostgreSQL-only plan test. Both SQLite layouts keep the existing 20,000-operation ceiling. Parent alias reuse and API-key isolation pass; child reuse is covered through all four HTTP aliases.

Completeness: replay, bridge retention and bounded legacy facets have matching implementation and regression evidence. Correctness: existing timing values, parent retention, child caps and row visibility are preserved. Coherence: the same revision/parent and unchanged dependency features are retained; canonical requirements/context are synchronized during archive. No critical local verification finding remains.

The unchanged SQLite VM ceiling exposed a missing-NULL status probe that used 40,000 operations under visibility predicates. Per-statement diagnostics identified the query; a raw prefix-presence guard now precedes that visibility check. The operation ceiling is not raised. A broad local migration-unit run also includes a POSIX permission-mode assertion that Windows cannot satisfy; the four hosted migration regressions are rerun separately, while Linux permission coverage remains owned by hosted CI.

Hosted MySQL, PostgreSQL plans, Linux process behavior and cargo-deny advisory results are separately verified by publication CI; these local results do not establish those environments. No production database or server was used.
