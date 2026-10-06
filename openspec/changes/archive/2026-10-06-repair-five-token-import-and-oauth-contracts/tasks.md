## 1. Establish and repair credential contracts

- [x] 1.1 Capture exactly five initial registry rows and prior dirty hashes; verify no selected record is already closed.
- [x] 1.2 Reproduce blank access imports and whitespace optional-token misclassification through API/DB tests, then fix shared validation and verify red/green results.
- [x] 1.3 Reproduce forced and expired non-refreshable preflight; fix and verify no upstream refresh/request dispatch while opaque credentials remain usable.
- [x] 1.4 Verify PAT import, dashboard auth status, export/restore, and pinned usage/probe behavior with isolated SQLite and API tests.
- [x] 1.5 Add PAT paste mode to the existing dashboard import dialog; verify metadata, masking, duplicate-submit/cancel/error handling, file-batch preservation and before/after browser screenshots.

## 2. Verify rejected-credential routing and callback publishing

- [x] 2.1 Verify token_expired failed repair and token_revoked failover on both Responses HTTP route families; verify repeated requests exclude the rejected generation, repair clears the block and hard ownership fails closed.
- [x] 2.2 Reproduce default Compose callback publishing; remove it and add explicit loopback overlay, verified by Compose rendering and configuration regressions.
- [x] 2.3 Synchronize Docker guidance and OpenSpec/context; verify normative delta sync and strict MkDocs/OpenSpec validation.

## 3. Close the bounded batch

- [x] 3.1 Run focused subsystem tests and applicable Ruff/format/type/architecture/cancellation/timing/settings/simplicity checks; record exact results and residuals in verification.md.
- [x] 3.2 Review requirement/scenario coverage, complete verification and verify all prior dirty paths are preserved before archive.
- [x] 3.3 Update exactly five registry rows and summary/evidence, reread saved records and confirm every other source row is unchanged.
