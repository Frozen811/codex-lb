## 1. Reproduce and repair

- [x] 1.1 Reproduce under constrained Linux startup/SIGTERM and identify the owning coroutine with sanitized pool traces.
- [x] 1.2 Add a real ring-registration barrier regression and demonstrate its cancellation failure before code changes.
- [x] 1.3 Add cooperative ring stop/wake behavior using the existing bounded stop helper; verify barrier, smoke, idle/retry and deadline controls.

## 2. Verify and publish

- [x] 2.1 Run focused lifespan/background-stop tests, Linux real-process regressions and static/architecture checks; record exact evidence.
- [x] 2.2 Sync normative requirement and stable context, strictly validate and confirm all local artifacts are ready for archive.
- [x] 2.3 Record publication authorization and local evidence, with exact-head cloud CI retained as the separate final user-completion gate.
