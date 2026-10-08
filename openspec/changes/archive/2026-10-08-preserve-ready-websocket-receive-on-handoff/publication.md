# Completed resumed repairs and exact-head CI

Verified on 2026-10-08, Europe/Kiev, with fresh GitHub Actions API evidence and remote-ref readback.

## Published fixes

| Commit | Result |
|---|---|
| [`83026fba1c96636c5d71129392d23a8172365663`](https://github.com/Frozen811/codex-lb/commit/83026fba1c96636c5d71129392d23a8172365663) | Bounded APT acquisition and browser installation/job deadlines; resolves the six-hour CI #80 setup stall. |
| [`e684963f7d6eafa86727447fc636e1726348c22a`](https://github.com/Frozen811/codex-lb/commit/e684963f7d6eafa86727447fc636e1726348c22a) | Preserves an owned/observed incomplete terminal during post-submit cooldown; resolves CI #81's real terminal race. |
| [`3205f09fa7dbd1de0d44f17c7dff5d8e138d8604`](https://github.com/Frozen811/codex-lb/commit/3205f09fa7dbd1de0d44f17c7dff5d8e138d8604) | Retains ready downstream receives during WebSocket handoff; resolves CI #82's lost queued-turn race. |

All were fast-forward pushed to `Frozen811/codex-lb:main`. The final tested source SHA, remote main, and local HEAD matched `3205f09fa7dbd1de0d44f17c7dff5d8e138d8604` when this result was recorded. The worktree was clean.

## Complete cloud gates on the final source SHA

| Workflow | Exact run | Attempt | Result |
|---|---|---|---|
| CI | [#83 /37728331547](https://github.com/Frozen811/codex-lb/actions/runs/37728331547) | 1 | SUCCESS, 35/35 jobs |
| Windows Startup Regression | [37728331549](https://github.com/Frozen811/codex-lb/actions/runs/37728331549) | 1 | SUCCESS, 1/1 |
| Release guards | [37728331558](https://github.com/Frozen811/codex-lb/actions/runs/37728331558) | 1 | SUCCESS, 2/2 |
| Simplicity budgets | [37728331554](https://github.com/Frozen811/codex-lb/actions/runs/37728331554) | 1 | SUCCESS, 1/1 |

**39/39 applicable jobs succeeded**. CI includes all six integration-core shards and their aggregate, unit, integration-bridge, e2e, PostgreSQL, all three MySQL shards and their aggregate, all migration checks, frontend coverage/build/browser smoke, package, Docker/Trivy, Rust, Nix, Helm lint/smoke, and `CI Required`. None of these jobs was skipped, cancelled, or failed.

Three upstream-only Release Please/beta-sync checks were skipped by their existing `Soju06/codex-lb` repository guards. The unsuccessful #80/#81/#82 runs remain historical; final success comes from the new full #83 matrix on the exact source SHA, not from isolated or repeated tests.

## Registry and verification scope

Local repair evidence is retained in this change and the sibling [APT setup](../2026-10-08-bound-browser-smoke-dependency-installation/verification.md) and [terminal race](../2026-10-08-preserve-owned-terminal-on-cooldown-race/verification.md) changes. OpenSpec requirements/context are synchronized, all changes were verified before archive, and the existing three-second handoff regression bound was retained.

The original five records remain qualified local closures with publication/CI evidence. This result does not certify a hosted-provider incident, release, or production deployment. No sixth source task was selected. A documentation-only follow-up commit records these successful implementation gates in the registry; its own push-triggered CI is followed separately without replacing this exact-head source evidence.
