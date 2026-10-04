## Context

See proposal.md. File-backed SQLite already uses indexed per-account capped probes; PostgreSQL uses lateral probes, while fallback reads trim in Python. SQLite LIMIT -1 silently removes the cap. Report rollups and continuous transcript drain loops already exist and need independent boundary coverage.

## Goals / Non-Goals

Goals: prove the three selected contracts, prevent invalid cap values before dialect dispatch, and publish only this package's diff to the requested fork main. Non-goals: database migration, production load certification, external providers, process-wide memory budgets or unrelated dirty repairs.

## Decisions

- Reject a non-integer or negative cap with ValueError. Zero remains valid. Validate once at the repository entry point rather than duplicating per-dialect guards or silently converting a malformed input.
- Exercise reports through ASGI and real SQLite with bulk Core inserts. Measure both raw and folded histories and assert public totals, speed metrics and cache behavior. Timing is diagnostic evidence, not a universal performance promise.
- Use a deterministic fake writer to count background wait cycles and interleave operations; use the real durable repository separately to verify ordered persistence and terminal fencing. Preserve the existing batcher runtime when those checks pass.
- Save fingerprints of prior dirty files and construct staged overlapping documents from HEAD plus this package's edits. Verify the staged tree separately so prior dirty repairs cannot supply hidden dependencies.

## Risks / Trade-offs

- Dense test fixtures cost setup time; bound them to one issue-scale case and keep elapsed time out of correctness assertions.
- Recent-floor exemptions can return more than the cap; explicitly verify that behavior instead of promising a global bound.
- Rollups retain totals after pruning, but exact short-window speeds require retained raw samples; document that existing limitation.
- A negative internal cap now fails early instead of returning inconsistent or unbounded data. No normal dashboard caller uses a negative cap.
