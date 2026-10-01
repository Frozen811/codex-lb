# Batch evidence and operational limits

Audit IDs: F-005, F-011, F-008 in root issues-check.md.

F-005 originally failed in Linux CI with `local_deadline=1599.989` against `700.0`, while the isolated Windows file passed. An explicit durable-first load before the local arm reproduces `1599.9605` on Windows. Persistence yields, so another reader can adopt poison before the local weak failure; the helper returned the aggregate deadline. It now returns the local evidence expiry and the route regression checks both orderings, durable load failure/retry, alias registration failure, settlement failure, and replacement ownership. No production quarantine semantics were changed or assertions relaxed.

F-011's baseline was 10 failures/4 passes. Forward-slash diagnostic rendering now covers existing errors and explicit PureWindowsPath/PurePosixPath within/outside-root identity.

F-008: a manual baseline workflow completed successfully on published SHA `7ec39f82709ee1ca4c00489a8d5fc301d49320ed`: https://github.com/Frozen811/codex-lb/actions/runs/36874316285. It ran the old memory tests and create_app import only. The revised workflow has not run in GitHub because local source changes are unpublished. Local Windows validation built and installed a fresh wheel and passed source/version parity, readiness and HTML/JS/CSS. It does not prove Windows upstream transport or real-account routing.

No source commit/push, release, registry publication or deployment in this batch. Release remains blocked until actual exact-source main-push prerequisites pass. Strict local verification and archival do not assert cloud readiness.
