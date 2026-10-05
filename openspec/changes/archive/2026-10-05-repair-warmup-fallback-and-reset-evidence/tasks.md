## 1. Reproduce the three product paths

- [x] 1.1 Add real HTTP fallback success/failure and Force Probe payload controls for UP-ISSUE-1895; verify with the wire module.
- [x] 1.2 Add real SQLite sliding-cycle deduplication and next-cycle controls for UP-ISSUE-1976; verify all 12 service cases.
- [x] 1.3 Run live ingestion/scheduler restart/freshness/duplicate-worker controls for UP-ISSUE-1975; verify the 29-case module.

## 2. Repair and verify

- [x] 2.1 Require fallback terminal completion and preserve absent usage; omit unsupported producer field and verify route/adapter controls.
- [x] 2.2 Persist stable cycle claims and apply the stable slot phase to proven sliding slot zero; verify fixed-window controls.
- [x] 2.3 Run focused tests, static checks, strict OpenSpec validation, and inspect final diff; record exact commands/results in verification.md.

## 3. Finish the requested batch

- [x] 3.1 Sync main specs/context, record scoped evidence, close and reread exactly the three registry rows.
- [x] 3.2 Verify artifact completeness and confirm archive readiness with strict validation and spec-sync readback.
