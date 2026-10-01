## 1. Baseline and contract

- [x] 1.1 Refresh fork HEAD, Actions and Docker manifest/labels; record exact SHAs and digests in audit evidence.
- [x] 1.2 Reproduce owner-miss failures and architecture violations; verify the #2274 scope contract against the supplied patch and existing OpenSpec.
- [x] 1.3 Define the bounded fallback in delta specs and design/context before editing code; validate the change strictly.

## 2. Implementation and regressions

- [x] 2.1 Clone typed candidate rows before repository teardown; prove unscoped, scoped and explicitly empty scopes using a real SQLAlchemy session.
- [x] 2.2 Move shared resolution into service support and required-owner validation into the existing private selection domain; verify architecture gates without raising thresholds.
- [x] 2.3 Adapt patch HTTP/compact forwarding tests and scoped test seam; verify ambiguity, paused-owner refusal and listing failure on public routes.
- [x] 2.4 Add direct WebSocket fallback coverage and verify owner pinning plus the unchanged previous-response anchor.

## 3. Verification and records

- [x] 3.1 Run focused continuity/ownership transport regressions, Ruff and architecture checks; report unrelated failures separately.
- [x] 3.2 Verify scenario-to-test mapping, sync the spec/context and archive only after strict validation and completed local verification.
- [x] 3.3 Update issues-check.md with local results, artifact mismatch and pending cloud/release evidence; ensure its root allowlist entry is present without committing or publishing.
