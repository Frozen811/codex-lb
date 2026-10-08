# Final source publication and successful CI #85

Verified on 2026-10-08, Europe/Kiev, from fresh GitHub Actions API results and remote main readback.

The final tested source SHA is [`5fd5b8141a13bde635ba0b38b283c6c81009a4ee`](https://github.com/Frozen811/codex-lb/commit/5fd5b8141a13bde635ba0b38b283c6c81009a4ee), fast-forward published to `Frozen811/codex-lb:main`. It contains the original five-task package and all resumed APT, terminal, receive-ownership, and caller-scope repairs. Local HEAD and remote main matched that SHA when recorded; the worktree was clean.

| Workflow | Exact run | Attempt | Result |
|---|---|---|---|
| CI | [#85 /37774897114](https://github.com/Frozen811/codex-lb/actions/runs/37774897114) | 1 | SUCCESS, 35/35 jobs |
| Windows Startup Regression | [37774896901](https://github.com/Frozen811/codex-lb/actions/runs/37774896901) | 1 | SUCCESS, 1/1 |
| Release guards | [37774896889](https://github.com/Frozen811/codex-lb/actions/runs/37774896889) | 1 | SUCCESS, 2/2 |
| Simplicity budgets | [37774897066](https://github.com/Frozen811/codex-lb/actions/runs/37774897066) | 1 | SUCCESS, 1/1 |

**39/39 applicable jobs succeeded**. All unit, integration-core shards/aggregate, integration-bridge, e2e, PostgreSQL, MySQL shards/aggregate, migration, frontend/coverage/browser, package, Docker/Trivy, Rust, Nix, and Helm jobs passed; `CI Required` passed. No applicable matrix job was failed, cancelled, or skipped. Three upstream-only release checks were skipped by their existing repository guards.

The earlier #83 success remains exact-head history. The documentation-only #84 result exposed the 75-second out-of-scope-owner polling bug and incomplete Settings fake; it was not treated as green. The scoped-out-owner selector/API regressions, 497 balancer tests and 43 sticky API tests passed locally, followed by this new full matrix on the source repair SHA.

The original five source records retain their qualified local closures, now with current publication/CI evidence. Other 333 rows and the 106 closed /7 partial /225 unverified counts are preserved. This does not certify live hosted-provider incidents, a release, or production deployment.

A documentation-only follow-up records this successful source result in the registry. Its own push-triggered CI is followed separately; this document retains the exact source SHA that implemented the fixes.
