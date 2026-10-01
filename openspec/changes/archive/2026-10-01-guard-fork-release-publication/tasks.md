## 1. Source and version gates

- [x] 1.1 Implement exact-source fork publication gate and prove missing/red/pending/stale CI refusals with focused tests and live read-only rejection.
- [x] 1.2 Align managed versions and verify `scripts.verify_release_version --tag v1.25.1` plus existing version/guard tests.

## 2. Artifact publishing

- [x] 2.1 Replace ungated publisher, verify job dependency and pre-login ordering with workflow tests; serialize and withdraw incomplete releases.
- [x] 2.2 Add archive/version/source/frontend verification and isolated package/image smoke checks; prove corrupt/mismatched packages fail and valid local builds pass.

## 3. Evidence and documentation

- [x] 3.1 Record historical package/image identity, limitations and local verification in issues-check.md and release-management context.
- [x] 3.2 Run focused tests, lint, simplicity and strict OpenSpec validation; sync and archive only after verification. Record that cloud execution and release remain pending.
