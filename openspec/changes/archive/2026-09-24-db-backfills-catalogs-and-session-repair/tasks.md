# Tasks for Resumable DB Backfills, Model Source Catalog Discovery, Weekly Automations Preset, and Targeted Session Repair

## Tasks
- [x] 1. Implement `app/db/backfill.py` with batched backfill execution, progress logging, and update `20260722_000000_backfill_request_log_useragent_families.py` <!-- id: task-db-backfill -->
- [x] 2. Implement CLIProxyAPI catalog discovery, snapshot caching, and unavailable model retention in `app/modules/model_sources/catalog.py` <!-- id: task-cpa-catalogs -->
- [x] 3. Implement weekly-window prestart preset in `app/modules/automations/` <!-- id: task-weekly-prestart -->
- [x] 4. Implement targeted session repair and hard-link rollback backups in `app/codex_sessions_retag.py` and `app/cli.py` <!-- id: task-session-repair -->
- [x] 5. Add unit and integration tests for all four features <!-- id: task-batch-39-tests -->
- [x] 6. Sync specs, validate OpenSpec, and archive <!-- id: task-batch-39-sync -->
