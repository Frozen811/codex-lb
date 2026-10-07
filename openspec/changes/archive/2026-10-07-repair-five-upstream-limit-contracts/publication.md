# Fork-main publication and complete CI

Verified on 2026-10-07, Europe/Kiev, using fresh GitHub Actions API results and `git ls-remote fork refs/heads/main`.

## Published implementation

- Five-task package: [`6ca0f6f059a9dfaf26b69a582f2db7e2f75469c5`](https://github.com/Frozen811/codex-lb/commit/6ca0f6f059a9dfaf26b69a582f2db7e2f75469c5).
- CI fixture repair: [`c50159869f3275f8f6c0541cabcc27cefeba68d1`](https://github.com/Frozen811/codex-lb/commit/c50159869f3275f8f6c0541cabcc27cefeba68d1).
- Repository and branch: `Frozen811/codex-lb:main`; both commits were fast-forward pushed.
- The remote main SHA, local HEAD, and tested head SHA all matched `c50159869f3275f8f6c0541cabcc27cefeba68d1` when this result was recorded; the worktree was clean.

## Exact-head cloud evidence

| Workflow | Run | Attempt | Result |
|---|---|---|---|
| CI | [#79, 37662810349](https://github.com/Frozen811/codex-lb/actions/runs/37662810349) | 1 | SUCCESS, all 35/35 jobs |
| Windows Startup Regression | [37662810149](https://github.com/Frozen811/codex-lb/actions/runs/37662810149) | 1 | SUCCESS, 1/1 job |
| Release guards | [37662810448](https://github.com/Frozen811/codex-lb/actions/runs/37662810448) | 1 | SUCCESS, 2/2 jobs |
| Simplicity budgets | [37662810229](https://github.com/Frozen811/codex-lb/actions/runs/37662810229) | 1 | SUCCESS, 1/1 job |

The 35 CI jobs include `CI Required`, all six integration-core shards and their aggregate, all three MySQL shards and their aggregate, PostgreSQL, SQLite/PostgreSQL/MySQL migration checks, unit/bridge/e2e, frontend coverage/build/browser checks, package, Docker/Trivy, Rust, Nix, Helm lint, and Helm smoke. Every job completed with `success`; none were failed, cancelled, or skipped. Across the four applicable workflows, **39/39 jobs succeeded**.

Three other check runs were `skipped`: upstream-only Release Please and the push/workflow-run beta-sync invocations. Their repository guards restrict them to `Soju06/codex-lb`; they are not substitutes for, or skips within, the successful fork CI matrix.

The first run [#78](https://github.com/Frozen811/codex-lb/actions/runs/37661140822) was unsuccessful and remains historical. Its single primary fixture defect and two failed aggregates were resolved by the focused repair described in [CI repair verification](../2026-10-07-stabilize-bridge-delivery-ci-control/verification.md). Final success was established by the new complete #79 run, not by rerunning the isolated failing case.

## Registry and remaining scope

Exactly UP-PR-2449, UP-PR-2439, UP-PR-2440, UP-PR-2403, and UP-PR-2391 retain their supported local closures and now link to this publication/CI evidence. Other source rows and the 106 closed /7 partial /225 unverified counts remain unchanged. Local and cloud checks do not certify live provider incidents, production deployment, a release, or the deferred fleet-runtime scope.

This document records the successful CI of the implementation and fixture-repair SHA. A subsequent documentation-only commit records these results in the registry; its own push-triggered CI is followed separately without changing this exact-head historical evidence.
