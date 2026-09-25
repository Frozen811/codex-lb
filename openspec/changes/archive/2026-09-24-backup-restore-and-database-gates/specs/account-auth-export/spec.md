# account-auth-export Specification Delta

## Requirements

### Requirement: Full account backup export and restore

The account service SHALL support full account backup export and restore operations.
An operator with `ACCOUNTS_EXPORT` permission SHALL be able to call `POST /api/accounts/backup/export` to download a complete backup JSON payload containing all configured accounts, decrypted credentials, and account metadata.
An operator with `ACCOUNTS_WRITE` permission SHALL be able to call `POST /api/accounts/backup/restore` with a backup JSON payload to restore accounts into the system.

The system SHALL record audit events for backup export (`accounts_backup_exported`) and backup restore (`accounts_backup_restored`) without persisting decrypted credential material in audit logs.

#### Scenario: Full account backup export produces complete accounts archive
- **GIVEN** multiple active and paused accounts exist in the database
- **WHEN** an authenticated operator calls `POST /api/accounts/backup/export`
- **THEN** the response contains all configured accounts with decrypted token structures and metadata
- **AND** `Cache-Control: no-store` headers are set
- **AND** an `accounts_backup_exported` audit event is recorded without raw credentials

#### Scenario: Full account backup restore restores accounts idempotently
- **GIVEN** a valid backup export payload containing accounts
- **WHEN** an authenticated operator calls `POST /api/accounts/backup/restore`
- **THEN** accounts are restored or updated in the database
- **AND** the response reports the number of restored, updated, and failed accounts
- **AND** an `accounts_backup_restored` audit event is recorded
