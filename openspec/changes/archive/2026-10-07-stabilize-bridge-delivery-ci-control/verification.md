# Verification: healthy delivery control under CI scheduling load

Date: 2026-10-07, Europe/Kiev. Baseline and published five-task package: `6ca0f6f059a9dfaf26b69a582f2db7e2f75469c5` on `Frozen811/codex-lb:main`.

## Publication and first cloud result

The user explicitly clarified that committing to `main` means committing and pushing to the GitHub fork and following CI to full success. The five-task package was fast-forward pushed; `git ls-remote fork refs/heads/main` matched its exact SHA. GitHub reported the authenticated account has push/admin permissions, the branch has no protection enforcement, and no effective branch rules apply.

[CI #78](https://github.com/Frozen811/codex-lb/actions/runs/37661140822), attempt 1, completed with **32 successful /3 failed jobs**. The primary failure was [integration-core-1](https://github.com/Frozen811/codex-lb/actions/runs/37661140822/job/112929082151): `test_real_bridge_paused_delivery_has_bounded_cleanup[stall-/v1/responses]` expected the independent request to complete, but it received `response.failed`. The other failures were the integration-core and CI Required aggregate gates. Unit, bridge, PostgreSQL, all MySQL shards, Docker, frontend coverage/browser, Rust, Nix and Helm jobs succeeded. Separate Windows Startup Regression, Release guards, and Simplicity budgets workflows succeeded. Upstream-only Release Please and beta-sync workflows were skipped by their fork guards.

The cloud log recorded two downstream-stall warnings, one for the intentionally paused consumer and another for the independently draining control. The fixture's artificial 100 ms timeout applied to both. The isolated unmodified paused-delivery selection passed 12/12 locally, confirming why a plain retry would not establish the fixture's correctness.

## Reproduction and repair

Injecting 150 ms inside only the independent queue's `put` made the same healthy-control assertion fail on all three routes: `/v1/responses`, `/v1/responses/`, and `/backend-api/codex/responses` (**3 failed** before the repair). The test now proves the injected delay actually ran.

After the intentionally paused queue closes under its unchanged 100 ms injection, the independent control restores the fixture's existing normal ten-second idle allowance. Production enqueue still has its unchanged five-second cap. No application source or workflow gate changed. All original assertions remain: bounded slots/bytes, queue closure, one timeout terminal, independent success while the first client stays paused, no retained putters/bytes, settled reservations, drained persistence, zero account pressure, and ACTIVE health.

## Local validation

```text
uv run pytest -q tests/integration/test_bridge_cleanup_delivery_contracts.py tests/unit/test_bridge_cleanup_delivery_contracts.py tests/unit/test_http_bridge_event_queue.py --tb=short --show-capture=no
46 passed, no skips/xfails

uv run ruff check tests/integration/test_bridge_cleanup_delivery_contracts.py
uv run ruff format --check tests/integration/test_bridge_cleanup_delivery_contracts.py
uv run ty check tests/integration/test_bridge_cleanup_delivery_contracts.py
all passed

OpenSpec 1.11.0 strict change validation: PASS
OpenSpec 1.11.0 strict main-spec validation: 68/68 PASS
```

The CLI was run from the verified local npm cache after `npx` package resolution stalled; its package metadata confirms version 1.11.0. Existing Starlette/AnyIO deprecation warnings remain.

## Completeness and scope

This is a test-only repair with explicit `skip_specs: true`; normative requirements and production behavior are unchanged. The reproduction binds the former global timeout misuse; the same delayed control passes after restoring its normal allowance. All 338 source registry rows remain byte-identical to the verified five-task commit. Their combined SHA256 is `65c9c8fb25c85745a30d7175f2c6b02c25ff87ac2e96b9dbe7be8ccae26923aa`. No sixth task was selected.

The fixing commit is discovered with `git log -1 --format=%H -- openspec/changes/archive/2026-10-07-stabilize-bridge-delivery-ci-control/verification.md`. A new complete CI run on that exact pushed SHA is required; the failed #78 result and local focused passes do not substitute for that run. This report is a pre-publication snapshot; final cloud status is read directly from GitHub after publication.
