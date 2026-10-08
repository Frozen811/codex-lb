## Context

See proposal.md for the five-record boundary. Source base is 8369ec720c5ac935f7a64fe3f30aa1cbc323f5e5 on clean main. Current upstream PR 2429 head 54887e6d52d8d5479850e836acb36fb6e17fd9f6 supersedes its original shared-policy proposal. Dashboard copy already promises twelve hours.

## Goals / Non-Goals

Preserve existing request-time eight-day freshness, guardian settlement, per-account claims, quota precedence and operator authority. Avoid new probe schemas, settings, migrations and duplicating already-correct rejection/reset implementations.

## Decisions

- Guardian uses one fixed twelve-hour predicate for initial admission and fresh-row recheck. Strict greater-than preserves the documented age boundary; UTC normalization permits aware and naive timestamps. Existing leadership, six-hour scan cadence, batching and force=True exchange remain intact.
- Remove the bare-credit-flag early return from the shared usage quota helper. Keep secondary exhaustion ahead of primary exhaustion when no spendable credits exist. Selection and account mappers already call this helper.
- Preflight fallback stays outside singleflight so forced callers retain failure. A deletion-marked persisted row must not become a usable fallback, even if its access token has a future expiry.
- Verify rejection races, HTTP retry ownership and settlement using existing integration suites and retained-reset recovery using real ingestion/scheduler tests. Additional production edits require a reproduced failure inside these five records.

## Risks / Trade-offs

- Twelve-hour guardian work runs more often than the incorrect eight-day implementation: existing bounded concurrency, leader guard and backoff contain work.
- Both exhausted windows retain quota_exceeded rather than inventing new primary precedence: pin this explicitly in tests/specs.
- Concurrent deletion can happen after refresh warning persistence: re-read the persisted marker before adopting a fallback.
- Synthetic provider tests and SQLite evidence cannot certify live accounts, distributed PostgreSQL/MySQL behavior or new cloud CI.

## Migration Plan

No schema or dependency changes. Deployment and rollback are source replacements governed by a separately authorized publication workflow.
