## Context

Helm schema-gated installs need a migration writer before the application becomes Ready. A post-install hook is delayed until readiness by Helm 3 `--wait`. Existing external secrets can also provide only the DB URL while the encryption-key Secret is chart-managed, making the previous pre-install hook premature.

## Goals / Non-Goals

Goals: install the fork, preserve schema gates and single-writer install migration behavior, validate actual package startup, and make remote setup reproducible.
Non-goals: publish artifacts, change schemas, install a system service on the user's machine, or certify unexecuted platforms/OAuth/provider integrations.

## Decisions

- Fresh external installs needing generated or materialized app credentials use a regular migration Job. Helm creates it alongside Secrets and the StatefulSet, so the schema gate stays closed until migration succeeds. Existing app credentials retain the pre-install hook; bundled mode retains startup migration and upgrade-only Jobs.
- Upgrades keep pre-upgrade hooks. Ordinary install Jobs use the same name and are replaced by the existing before-hook-creation policy on upgrade. No concurrent app startup migration is enabled for external modes.
- Helm defaults select `frozen811/codex-lb`; source instructions build/load an explicitly selected local image instead of claiming historical public aliases contain new fixes. Nix quick starts use the fork checkout and a dedicated guide explains pinned remote refs.
- Document nginx with HTTP/1.1 upgrades, buffering disabled and the original Host preserved. Keep remote bootstrap/API-key controls; remove the unshipped systemd unit assumption.

## Risks / Trade-offs

- Bundled PostgreSQL depends on third-party chart/image availability: record actual failures and distinguish them from application installs.
- Existing deployments can require an operator-controlled stop before destructive schema upgrades. Helm rollback does not downgrade the database.
- Nix verification on x86_64 Linux cannot certify Darwin/ARM64. A running reverse proxy cannot prove real Codex generation without an account.

## Migration Plan

Render and test before applying to a disposable namespace. For existing releases retain DB/key backups and the documented replica drain ordering. No production release is performed by this change.
