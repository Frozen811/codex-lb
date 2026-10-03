## 1. INC-04-FANOUT

- [x] 1.1 Add external image-route regressions for partial failure, unexpected exception, log failure, and cancellation; demonstrate failing baseline cases.
- [x] 1.2 Preserve completed usage, drain owned children, and defer cancellation through reservation handoff; verify targeted fan-out and image-route tests.

## 2. INC-05-SIGNING

- [x] 2.1 Verify sender/receiver key precedence with independent settings and file paths, shared file-only keys, missing files, and mismatched keys; run signed-forward regressions.

## 3. INC-06-RESET

- [x] 3.1 Exercise missing target identity on all external aliases and slash variants with persisted accounts; assert 401 and no consumption/snapshot mutation/refresh, and retain valid-target coverage.

## 4. Verification and registry

- [x] 4.1 Run focused regression suites, Ruff, type checks where applicable, and strict OpenSpec validation; document scenario evidence.
- [x] 4.2 Sync capability context/specs, verify and archive the change, and mark exactly INC-04/05/06 locally closed with evidence and publication boundaries in issues-check.md.
