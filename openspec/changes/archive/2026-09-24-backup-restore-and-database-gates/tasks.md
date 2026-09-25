# Tasks for Account Backup/Restore, Limit Restriction, and Database Migration Gates

## Tasks
- [x] 1. Add schemas and service methods for full account backup export and restore in `app/modules/accounts/schemas.py` and `app/modules/accounts/service.py` <!-- id: task-backup-restore-service -->
- [x] 2. Expose backup export and restore endpoints in `app/modules/accounts/api.py` with audit logging <!-- id: task-backup-restore-api -->
- [x] 3. Implement account limit restriction registry and balancer integration in `app/modules/accounts/quota_restriction.py`, `service.py`, and `api.py` <!-- id: task-quota-restriction -->
- [x] 4. Implement SQLite-to-PostgreSQL migration path verification script in `scripts/verify_sqlite_to_postgres_migration.py` <!-- id: task-verify-sqlite-migration -->
- [x] 5. Implement production-scale migration duration check script in `scripts/check_migration_durations.py` <!-- id: task-check-migration-durations -->
- [x] 6. Add comprehensive unit and integration tests for backup/restore, quota restriction, and migration gates <!-- id: task-batch-38-tests -->
- [x] 7. Sync delta specs to main specs and validate OpenSpec <!-- id: task-openspec-sync -->
