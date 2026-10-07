## 1. Correct the accelerated failure fixture

- [x] 1.1 Reproduce the healthy-control failure with delayed independent queue puts on all three routes.
- [x] 1.2 Restore the ordinary control timeout after the stalled queue closes; verify the same delayed cases pass.
- [x] 1.3 Run the complete delivery/quarantine integration file, related unit tests, Ruff, type checks, and strict OpenSpec validation.

## 2. Prepare fork-main publication

- [x] 2.1 Record CI #78 failure, publication authority, local evidence, and verify that all 338 source rows are unchanged from the verified five-task commit.
- [x] 2.2 Verify/archive this test-only change and review the complete staged patch before commit and push to Frozen811/codex-lb:main.
