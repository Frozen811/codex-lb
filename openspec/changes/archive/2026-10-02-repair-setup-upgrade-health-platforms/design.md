## Context

See proposal.md. The checkout's origin is Soju06 and fork is Frozen811; COMMUNITY_RELEASE pulls origin. Public package/image versions are historical and differ from runtime/source identity. Readiness checks DB and bridge state, deliberately excluding upstream and assets. Internal drain currently trusts projected client address; the outer middleware already captures raw peer and locality resolver considers forwarded evidence.

## Goals / Non-Goals

Goals: local-control provenance fix, concrete repeatable update/rollback and failure evidence, consolidated truthful platform guidance.

Non-goals: production restart, publishing/updating public tags, replacing user stores, universal downgrade support, new auth/config surface or unobserved platform certification.

## Decisions

- Reuse captured socket peer and export the existing forwarded-hint predicate for internal control. Require raw and projected loopback provenance and reject nonempty forwarded caller hints, so trusting raw loopback alone cannot admit a reverse-proxy user. These controls are for direct loopback preStop/operator calls, not the dashboard proxy. Keep readiness payload/contracts and shutdown timing intact.
- Replace implicit origin pull with explicit fork URL/full-SHA selection and clean-tree checks; do not modify this shared checkout's Git state to rehearse that command.
- Exercise historical/current-source container runtime against an isolated SQLite store, paired snapshot rollback and separately named image identities. Current-source rehearsal can reuse a dependency image but must label source mounting or overlay layers and avoid claiming a new public release.
- Add health/failure/coverage sections to existing guides linked to owning OpenSpec. Keep normative behavior in specs and dated evidence/limitations in context and audit registry.

## Risks / Trade-offs

- Historical image may require real source migration from old schema; preserve pre-upgrade store and identify the exact old image before crossing it.
- Windows process termination is not Linux SIGTERM. Run Linux signal checks in disposable containers/WSL and keep native platform claims scoped.
- Local unit Request fixtures must represent captured provenance, Host and headers; no production fallback from missing capture.
