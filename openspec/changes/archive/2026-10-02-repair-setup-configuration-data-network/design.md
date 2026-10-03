## Context

See proposal.md. Settings already selects module-root dotenv paths at import time, supports ordered explicit env files and preserves non-NULL dashboard overrides. Compose injects `.env.local` as process environment; its project `.env` primarily supplies interpolation. The CLI parser accepts a negative keep-alive timeout. Docker runtime uses UID 1000 and a persistent application directory. External SQL databases store account ciphertext and settings separately from encryption material.

## Goals / Non-Goals

Goals: accurate setup contracts, rejection of a demonstrably invalid listener value, and independently observed persistence/restore evidence.

Non-goals: new config surface, automatic database migration between backends, production store mutations, publishing artifacts, OAuth login or live upstream account use, TLS/WS transport certification (SETUP-05/06/07).

## Decisions

- Preserve existing discovery; document explicit `CODEX_LB_ENV_FILE` for relocated Python installs instead of changing package behavior to ingest unrelated launch-directory files.
- Extend the existing CLI timeout parser with a lower bound; zero disables idle reuse immediately and stays supported.
- Add fresh-interpreter configuration tests and a real CLI SQLite persistence/restore regression. Rehearse PostgreSQL/MySQL using disposable databases and source-mounted Docker runtime with the existing dependency environment; historical image contents are not counted as current source evidence.
- Use SQLite backup API for a consistent snapshot; restore with the matching key. For external SQL use backend-native dump/import tools into an empty isolated database. Restore the backup with its original executable first; upgrades are a separate forward operation.
- Add endpoint and failure-diagnostic tables to existing owning guides; keep `.env.example` settings budget unchanged.

## Risks / Trade-offs

- Docker Desktop is the available container host; Linux host-gateway/host networking and physical LAN/WSL network switching need distinct evidence and will be marked as unexecuted where applicable.
- External SQL backup requires DB tooling and protected credentials. Examples use environment/connection files and exclude real operator data.
- Full downgrade support is outside scope. Restoring a prior binary requires its paired pre-upgrade snapshot and compatible backend major version.
