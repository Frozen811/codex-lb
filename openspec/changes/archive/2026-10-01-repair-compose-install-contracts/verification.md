# Verification — repair-compose-install-contracts

## Completeness

All 11 tasks complete. Scope is INSTALL-01/03/05 installation contracts; no public alias publication is claimed. Source checkout remains uncommitted on main 7ec39f82709ee1ca4c00489a8d5fc301d49320ed with earlier local batches preserved.

## Correctness

| Requirement/scenario | Evidence |
|---|---|
| Server-only source selection despite cached history | Baseline normal Compose up selected historical GHCR image. Fixed normal up replaced deliberately seeded old local image, matched checkout websocket source bytes and served readiness/assets. `pull_policy: build`, local image name, focused config regression. |
| No URL defaults to SQLite | Production and each enabled development DB profile started without app URL on isolated SQLite volumes. |
| Explicit profile backend and documentation | PostgreSQL 18.6 and MySQL 8.4.11 app engine used service DNS, actual SQL dialect/database, no SQLite store on fresh remote data volume. Two app generations retained remote setting and key; migration schema check passed. docs/database.md supplies URLs, wait and recreation commands. |
| Authenticated DB health | Baseline ping/isready and PG loopback trust reproduced false positives. SQL probes succeed with correct access; wrong password and nonexistent DB fail. PostgreSQL uses container HOSTNAME to avoid initdb loopback trust. |
| External PostgreSQL/TLS | Non-TLS and verify-full source-built Compose installs passed readiness/assets and schema checks. TLS runtime SQL confirmed pg_stat_ssl.ssl=true. Bad password, bad DNS, mismatched certificate hostname and untrusted CA exited nonzero before readiness. |
| Persistence and recovery | Remote settings/key survived app recreation. PostgreSQL pg_dump/pg_restore into another DB with original app key passed app/schema/readiness. Separate DB container recreation retained SQL state and app reconnected. |
| Public artifact identity | Anonymous empty-config digest pull, fresh OCI source/platform/version facts. Historical digest non-root named-bridge readiness/assets and data/key recreation passed. Runtime 1.25.0-beta.9 differs from OCI 1.25.1; no installed project metadata or built-in HEALTHCHECK. README/source docs distinguish channels. |
| Upgrade profile | Synthetic PG16 root volume, offline readable backup, ordinary PG18 legacy guard refusal, pinned one-shot helper, healthy PG18.6 with retained synthetic row. |

## Coherence

Three normative requirements synced into deployment-installation; purpose/rationale/examples/failure modes in context.md. Existing installation instructions corrected without new README headings or settings, changelog edits, version bumps or changes to fixed user volume names. Existing simplicity budget remains 221/225 README lines, 10/10 headings. Source and historical public image publication remain distinct.

## Checks

- 22 focused unit tests passed, one existing Starlette deprecation warning.
- Ruff check and format check on three changed test files passed.
- Architecture and simplicity checkers and git diff --check passed.
- Strict delta and 68 main specifications passed, zero failed.
- Final audit container/network/volume name selections empty. Temporary scripts and logs retained under C:/Users/ext/AppData/Local/Temp/codex-lb-install-batch5-20261001.

## Findings and boundaries

No incomplete implementation requirements within this change. Full details and intermediate harness failures in issues-check.md §19; F-019/020/021 locally corrected. F-010 public aliases and F-007 broad claims remain open. The public digest is historical, not proof of shipped checkout fixes. No real accounts/OAuth/Codex traffic, remote production endpoint, MySQL TLS, ARM64 or production-size upgrade proof. PG16 tar backup was readable but not restored; actual PostgreSQL logical dump restore was tested separately. No new cloud CI execution or publication. Latest exact-source published main CI 36761400788 remains failure.
