## 1. Quarantine provenance (F-005)

- [x] 1.1 Reproduce the failing durable/local evidence ordering deterministically at the Responses route and identify the source of the 1600 deadline.
- [x] 1.2 Repair the cause while preserving local evidence and partial-failure semantics; verify provenance, race and recovery-origin integration tests.

## 2. Architecture diagnostics (F-011)

- [x] 2.1 Normalize diagnostic paths and verify existing parse/threshold failures plus Windows/POSIX and outside-root paths.

## 3. Windows Actions (F-008)

- [x] 3.1 Automate Windows checks and isolated installed-wheel readiness/assets smoke; verify workflow structure, actionlint and actual local Windows startup.
- [x] 3.2 Require exact-source Windows main-push success for fork publication; verify rejection cases through release-gate tests.
- [x] 3.3 Inspect actual Actions evidence and record whether it evaluates published baseline or edited source; no unexecuted workflow claims.

## 4. Final verification

- [x] 4.1 Run focused tests, Ruff, strict OpenSpec and relevant repository gates; record outcomes and limits in issues-check.
- [x] 4.2 Sync normative requirements/context, verify completion and archive the locally verified change.
