## Decisions

Use `pull_policy: build` and `codex-lb:local` for server-only source installation so `up` cannot silently prefer a cached old release or relabel a local build as an official release. Keep SQLite as the no-env default. External PostgreSQL selection remains the existing `CODEX_LB_DATABASE_URL` contract.

Profiles start database services only. Avoid automatic backend inference, competing profiles or new env settings: document explicit URL selection and backend recreation after env changes. Probe authenticated SQL with the application user/database, using existing DB service env values at container runtime.

Treat public tags as historical artifacts, identify source revision and runtime version independently, and use a registry digest in historical-image instructions. Public aliases remain open until the release gates permit a fresh publication.

## Verification

Use disposable networks, loopback random ports and explicit isolated volume names. Check actual application migrations, readiness/assets, remote SQL state and encryption key persistence after recreation. Test invalid credentials/unreachable DB without changing user data. Record tested platform and source/public differences.
