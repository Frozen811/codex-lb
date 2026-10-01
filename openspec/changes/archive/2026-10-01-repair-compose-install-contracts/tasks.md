## 1. Public image (INSTALL-01)

- [x] 1.1 Refresh anonymous manifest/source/platform evidence; pull and start by digest, check readiness/assets and persistent data after recreate.
- [x] 1.2 Correct existing fork image instructions, upstream mismatches and historical-image/update boundaries without claiming public fixes shipped.

## 2. Database profiles (INSTALL-03)

- [x] 2.1 Verify PostgreSQL and MySQL profile startup and explicit application URL selection; prove profiles alone retain SQLite.
- [x] 2.2 Replace availability-only health probes with authenticated SQL; demonstrate rejection for invalid credentials/database.
- [x] 2.3 Verify migrations/readiness, persisted remote settings and key retention after recreate; document service DNS and host URLs.
- [x] 2.4 Rehearse the pinned PostgreSQL 16 to 18 upgrade helper with offline backup, legacy guard and retained synthetic data.

## 3. Server-only Compose (INSTALL-05)

- [x] 3.1 Prove historical image selection, then make source builds explicit with a local image name and test actual default startup.
- [x] 3.2 Verify optional no-env SQLite and external PostgreSQL, failed credentials/network, and application recreation.
- [x] 3.3 Verify TLS migrations/runtime SQL and certificate rejection, SQL dump/restore with the original app key, and database recreation/reconnection.

## 4. Closure

- [x] 4.1 Run focused checks, strict OpenSpec and update issues-check with evidence and remaining publication boundaries.
- [x] 4.2 Sync requirements/context, verify and archive locally.
