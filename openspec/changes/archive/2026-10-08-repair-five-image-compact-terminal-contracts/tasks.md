## 1. Image contracts

- [x] 1.1 Reproduce oversized malformed-base64 classification and unsupported-sibling precedence in unit and both public Responses routes; record red-before results.
- [x] 1.2 Repair the length shortcut without full-segment copy/decode; verify legal oversized rejection, exact decoded-size reporting, connection reuse, rollback and close-1009 cases.

## 2. Compact and terminal contracts

- [x] 2.1 Verify source compaction refusal before selection/admission/reservation/dispatch on canonical and trailing-slash routes, enabled and disabled sources, and API-key source scope.
- [x] 2.2 Verify default and explicit compact budgets, per-request overrides, independent SSE idle deadline and automation claim derivation with focused tests.
- [x] 2.3 Verify one terminal, settlement-before-health, continued queued writes and cancellation propagation when post-terminal health persistence fails.

## 3. Completion

- [x] 3.1 Run focused suites and applicable lint/type/architecture/strict OpenSpec checks; save exact commands and residuals in verification.md.
- [x] 3.2 Sync the normative spec and stable context; verify and archive the completed change.
- [x] 3.3 Update exactly five registry rows and the latest summary; reread saved statuses, compare the other 333 source rows and all prior dirty files against the backup.
