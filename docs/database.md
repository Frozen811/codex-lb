# Database

Migration behavior is defined by the [database-migrations specification](https://github.com/Frozen811/codex-lb/blob/main/openspec/specs/database-migrations/spec.md).

SQLite is the default database backend and needs no configuration. PostgreSQL and MySQL are optional via `CODEX_LB_DATABASE_URL` (for example `postgresql+asyncpg://codex_lb:codex_lb@127.0.0.1:5432/codex_lb` or `mysql+asyncmy://codex_lb:codex_lb@127.0.0.1:3306/codex_lb`).

## Data paths

| Environment | Path |
|-------------|------|
| Local / uvx | `~/.codex-lb/` |
| Docker | `/var/lib/codex-lb/` |

`CODEX_LB_DATA_DIR` moves the default SQLite DB, key and archive paths together. Explicit `CODEX_LB_DATABASE_URL`, `CODEX_LB_ENCRYPTION_KEY_FILE` or `CODEX_LB_CONVERSATION_ARCHIVE_DIR` paths remain independent. Relative filesystem paths resolve from the process working directory. Use absolute paths in services and containers.

The application user needs a writable data directory and SQLite parent directory (SQLite also writes WAL/SHM sidecars), a readable key and a writable archive directory when archiving is enabled. New key files use mode `0600` on Unix. Named Docker volumes inherit the image directory's ownership; arbitrary bind mounts and Kubernetes volumes must grant the runtime UID access. Do not solve a mount permission error by running the application as root or making the key world-readable. A read-only key Secret is valid when it already contains the matching key; its parent needs write access only when generating a missing key.

## Backup, restore and rollback

Retain the **database and matching encryption key together**, plus enabled archive/spool storage and the launch configuration. A Docker volume survives container recreation; removing the volume removes its data. Avoid `docker compose down -v` for an installation you want to retain. Copying the application data directory does **not** back up PostgreSQL or MySQL. Those databases need a separate dump/snapshot. A pre-migration SQLite backup contains the database only, not the key.

Stop application writers before the following rehearsal. Keep the original store intact. For SQLite, use its backup API instead of copying only a live `store.db`, which can omit committed WAL data. Set `SQLITE_SOURCE` to the effective database file, and choose a new empty backup destination:

```bash
export SQLITE_SOURCE=/absolute/data/store.db
export SQLITE_BACKUP=/absolute/backup/store.db
python - <<'PY'
import os, sqlite3
from contextlib import closing
from pathlib import Path
source = Path(os.environ["SQLITE_SOURCE"])
backup = Path(os.environ["SQLITE_BACKUP"])
if not source.is_file() or backup.exists():
    raise SystemExit("Source must exist and backup destination must be new")
backup.parent.mkdir(parents=True, exist_ok=True)
with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as src:
    with closing(sqlite3.connect(backup)) as dst:
        src.backup(dst)
        dst.execute("PRAGMA journal_mode=DELETE")
backup.chmod(0o600)
PY
```

Copy the effective encryption key into that protected backup separately, including an external key file or Secret. If an explicit key value is used, retain it in your secret store. Back up enabled archives and the configured HTTP bridge spool directory too; they can contain private conversation data.

PostgreSQL example, using `PGHOST`, `PGPORT`, `PGUSER` and a protected `PGPASSFILE` (or the equivalent connection service). Use client tools compatible with the database major version. The restore database must be empty and dedicated to the rehearsal:

```bash
pg_dump --format=custom --no-owner --no-acl --file=codex-lb.dump codex_lb
createdb codex_lb_restore
pg_restore --exit-on-error --no-owner --no-acl --dbname=codex_lb_restore codex-lb.dump
```

MySQL example, with connection credentials in a protected option file. Grant the rehearsal identity access to a new empty database; the example assumes the local profile's database charset/collation. Stop all writers; use InnoDB and compatible server/tool versions:

```bash
mysqldump --defaults-extra-file=/protected/mysql.cnf --single-transaction \
  --no-tablespaces --set-gtid-purged=OFF codex_lb > codex-lb.sql
mysql --defaults-extra-file=/protected/mysql.cnf \
  -e 'CREATE DATABASE codex_lb_restore CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci'
mysql --defaults-extra-file=/protected/mysql.cnf codex_lb_restore < codex-lb.sql
```

Restore into a separate directory/database with its matching key. For SQLite, copy the standalone snapshot as the new `store.db` in an empty directory; do not combine it with old WAL/SHM files. Point `CODEX_LB_DATA_DIR`, the DB URL and any independent key/archive paths at the rehearsal. Start with the backup's original executable version, run `codex-lb-db check`, then verify readiness, dashboard settings, account inventory and credential decryptability without printing credentials. A regenerated or unrelated key fails the default fingerprint check; restore the original key instead of bypassing the guard. Successful readiness alone does not establish that a real upstream account works.

Before upgrading, retain the old executable/image identity and a fresh database/key snapshot. Binary or Helm rollback does not reverse schema/data changes: restore the matching pre-upgrade snapshot with the old executable and a compatible database server major version. Do not point an older executable at a newer database and assume it will downgrade safely. Switching a DB URL to PostgreSQL/MySQL selects a different store; it does not copy SQLite accounts/settings.

Online migrations report revision starts and executed/failed elapsed time on stderr. `Executed` means a step finished; an enclosing transaction may still need to commit. The CLI keeps its existing stdout result. Progress records contain revision identity and direction, omitting SQL, URLs, parameters and exception text.

An unknown-revision failure includes conditional metadata-stamping guidance. Use it only after verifying schema and data compatibility with the rollback image, ending migration transactions, and retaining a recoverable database backup and matching encryption key. Run `codex-lb-db stamp <revision>` from a build containing both the recorded and target revisions against the same database. Stamping changes only the migration ledger; it does not roll back schema or data. An older build cannot stamp an unknown revision. Check migration policy, schema drift and application behavior before resuming traffic.

## PostgreSQL via Docker Compose

The Docker Compose `postgres` profile uses the Postgres 18 image and mounts the named data volume at
`/var/lib/postgresql`, the parent of the image's versioned `PGDATA` directory. The `postgres` and
`postgres-upgrade` profiles live in the root
[`docker-compose.yml`](https://github.com/Frozen811/codex-lb/blob/main/docker-compose.yml)
(`docker-compose.prod.yml` defines only the source-built `server`, with SQLite
by default or optional external PostgreSQL).

Profiles start the database only: enabling `postgres` does not automatically
switch the application away from SQLite. For a containerized backend, create
`.env.local` in the checkout with this development-only URL:

```dotenv
CODEX_LB_DATABASE_URL=postgresql+asyncpg://codex_lb:codex_lb@postgres:5432/codex_lb
```

```bash
docker compose --profile postgres up -d --wait postgres
docker compose --profile postgres up -d --build --force-recreate server frontend
```

The profile's health probe runs authenticated SQL against the application
database. Start the database and wait before the application. Use service DNS
`postgres` from the backend container; use `127.0.0.1:5432` for a host-side
client. Changing `.env.local` needs application recreation, not just `restart`.
Do not enable both database profiles for a single application. The supplied
credentials are for local development; use an existing external database with
your own credentials for production. Keep the application volume for its
encryption key and back up the SQL database separately.

## Upgrading Postgres 16 → 18

Existing Postgres 16 compose volumes must be upgraded before the Postgres 18 container starts:

```bash
docker compose --profile postgres stop postgres
docker run --rm -v codex-lb-postgres-data:/var/lib/postgresql -v "$PWD:/backup" alpine \
  tar -C /var/lib/postgresql -czf /backup/codex-lb-postgres-data-before-pg18.tgz .
docker compose --profile postgres-upgrade run --rm postgres-upgrade
docker compose --profile postgres up -d postgres
```

The `postgres-upgrade` profile runs `pg_upgrade` in one-shot mode against the same named volume and exits after the
data directory has been upgraded to the Postgres 18 layout. Because that helper mounts and rewrites the operator's
database volume, Compose pins the helper image by digest; refresh and review the digest deliberately when changing the
helper image tag. Keep the backup until the application has started and `codex-lb-db check` succeeds against the
upgraded database.

The normal `postgres` service refuses to start when it detects the old root-level `PG_VERSION` file from a pre-18
Compose volume. If that guard fires, run the `postgres-upgrade` profile above before starting Postgres again.
It also refuses nested `/var/lib/postgresql/data` directories that still report a pre-18 major version, because those
layouts need an explicit pg_upgrade before the Postgres 18 container can safely open them.

## MySQL

MySQL is optional via `CODEX_LB_DATABASE_URL` (for example
`mysql+asyncmy://codex_lb:codex_lb@127.0.0.1:3306/codex_lb`). The application connects with `asyncmy`; Alembic
migrations run the same URL over `pymysql`. MySQL 8.0.13+ with InnoDB and `utf8mb4` is required (CI and the
reference rehearsal run `mysql:8.4`).

The schema is emitted for MySQL:

- unbounded string columns become sized `VARCHAR`s derived from production maxima, so every index key stays
  inside MySQL's 3072-byte `utf8mb4` limit;
- long text (model-registry snapshots, error traces) uses `MEDIUMTEXT` (16 MiB);
- text columns that carry keys (response ids, password hashes, sticky-session keys) are promoted to sized
  `VARCHAR`s;
- literal defaults on text columns are emitted in MySQL's expression form (`DEFAULT ('x')`), which MySQL
  accepts where the plain literal form is rejected;
- statements that read their own target table (batched retention deletes, the account-deletion drain, and the
  quota-planner claim) are rewritten through materialised derived tables to stay clear of MySQL error 1093.
- datetime columns are emitted as `DATETIME(6)` (with `DEFAULT CURRENT_TIMESTAMP(6)` where the models declare a
  server-side default), because MySQL's plain `DATETIME` rounds Python-supplied microseconds away -- limit
  windows, rollup watermarks and lease deadlines are compared against Python-computed instants, so MySQL has to
  round-trip them the way SQLite and PostgreSQL do;
- floating-point columns are emitted as `DOUBLE`: MySQL's bare `FLOAT` is 4-byte single precision, while the
  aggregates compared against raw recomputations (cost/token sums) assume 8-byte precision;
- rollup dimension columns that carry the `U+001F` sentinel encoding use a binary collation, because MySQL's
  default `utf8mb4_0900_ai_ci` treats the sentinel as ignorable and would fold `''` into `NULL`;
- bucket arithmetic floors the division explicitly, since MySQL's signed `CAST` rounds where SQLite truncates
  and PostgreSQL floors;
- an account marked for deletion records its `delete_history` variant in its own conditional statement before
  the marker update: MySQL evaluates a multi-column `UPDATE`'s `SET` list against the row as it stands, so a
  `CASE` reading a column the same statement writes would take the wrong branch;
- same-email account merges and same-identity reauth upserts serialize on exclusive `runtime_sentinels` row
  locks keyed by the same derivations PostgreSQL uses for its advisory locks
  (`advisory_lock_key('merge-email', email)`, `account_identity_lock_key(chatgpt_account_id)`, and the
  deterministic account id), acquired in sorted order: MySQL has no transaction-scoped advisory lock, and
  two concurrent imports could otherwise both insert (two rows for one email with merging enabled, or two
  rows for one upstream identity under reauth, which promises one).

The cross-process migration lock uses MySQL's own named lock (`GET_LOCK`/`RELEASE_LOCK`) on a dedicated
connection, mirroring the PostgreSQL advisory lock. Named locks are **server-wide, not per-database**: two
`upgrade` runs for different databases on one server still serialize against each other, which is exactly the
intent for a schema mutex and worth knowing when running several test databases side by side.

`docker compose --profile mysql up -d mysql` starts a local MySQL 8.4 with the `codex_lb` database.

To use it from the containerized backend, set this development-only URL in
`.env.local`, then wait for the database and recreate the application:

```dotenv
CODEX_LB_DATABASE_URL=mysql+asyncmy://codex_lb:codex_lb@mysql:3306/codex_lb
```

```bash
docker compose --profile mysql up -d --wait mysql
docker compose --profile mysql up -d --build --force-recreate server frontend
```

Host-side clients use `127.0.0.1:3306`. MySQL health requires a successful
authenticated `SELECT 1` on the selected database: `mysqladmin ping` alone
also succeeds on access-denied, as documented in the
[MySQL manual](https://dev.mysql.com/doc/refman/8.4/en/mysqladmin.html).
Neither profile migrates data from an existing SQLite installation.

### Sizing the server

Size InnoDB deliberately. A profile for a database of up to ~5 GiB:

```ini
[mysqld]
innodb_buffer_pool_size = 6G
innodb_buffer_pool_instances = 6
innodb_redo_log_capacity = 1G
innodb_flush_log_at_trx_commit = 1
max_connections = 200
tmp_table_size = 256M
max_heap_table_size = 256M
slow_query_log = 1
long_query_time = 0.5
```

Run the buffer pool at roughly 1.2-1.5x the working set on a dedicated server; keep
`innodb_flush_log_at_trx_commit = 1` for crash safety.

### Testing against MySQL

```bash
MYSQL_TEST_DATABASE_URL='mysql+asyncmy://codex_lb:codex_lb@127.0.0.1:3306/codex_lb' make test-mysql
MYSQL_TEST_DATABASE_URL='mysql+asyncmy://codex_lb:codex_lb@127.0.0.1:3306/codex_lb' make migration-check-mysql
```

The matching CI jobs (`test-mysql`, `migration-check-mysql`) run against a `mysql:8.4` service.

`MYSQL_PYTEST_TARGETS` covers the portable PostgreSQL list plus the MySQL-clean integration files beyond it
(99 targets, including the MySQL named-lock cases), so the MySQL job covers every integration that can run
there rather than a curated subset. Tests that genuinely require PostgreSQL semantics (advisory-lock
interleavings, query-plan assertions, `reloptions` tuning) are skipped with that reason in their summary
line.

---

*Specs: [database-backends](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/database-backends) · [database-migrations](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/database-migrations) · [deployment-installation](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/deployment-installation)*
