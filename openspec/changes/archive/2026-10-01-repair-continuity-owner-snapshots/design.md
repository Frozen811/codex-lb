## Context

See proposal.md for the regression. Upstream issue [#2274](https://github.com/Soju06/codex-lb/issues/2274) separates possible ownership from current routing eligibility. The fork already implements that exception, but its old spec and two integration tests prohibit even a sole scoped owner. Real repository teardown expires returned SQLAlchemy rows; mock-only helper tests miss the failure.

## Goals / Non-Goals

**Goals:** keep typed Account snapshots usable across teardown, reconcile the bounded fallback contract, and restore architectural gates with externally exercised regression coverage.

**Non-Goals:** implement the rest of #2274, change bridge takeover, cancel existing work on Pause, publish artifacts, or resolve the quarantine CI failure.

## Decisions

- Use the existing clone_row within the open repository context. Returning live ORM rows reproduces the failure; changing session-wide expiry behavior would affect unrelated consumers. Keep normal required-owner admission separate from historical candidate enumeration.
- Type the scope as ApiKeyData and read its declared fields. Empty explicit assignment remains empty; candidate selection ignores health, quota, model and plan.
- Move fallback resolution into the existing service support module, which compact, streaming and WebSocket already depend on. Delete the now unused continuity_owner module instead of retaining a compatibility shim with no real consumers.
- Move required continuity-owner policy validation into the existing private sticky_selection module using SelectionInputsProtocol. Preserve the load_balancer helper import surface through an explicit alias and retain existing error codes. Architecture thresholds remain unchanged.
- Adapt the supplied patch's public forwarding tests, then independently add real session rollback/close coverage, ambiguity, empty scope, paused-owner admission and direct WebSocket coverage. A mocked clone-identity assertion alone is insufficient.
- Enforce direct WebSocket refusal on ambiguous/listing-error subscription ownership even when Codex affinity is enabled. New public tests reproduced unpinned dispatch in that existing exception; affinity cannot establish previous-response ownership. Existing model-source HTTP fallback remains separate.

## Risks / Trade-offs

- A sole candidate is a bounded inference, not persisted owner evidence. It cannot bypass admission or override conflicting file/turn ownership; test those refusal paths.
- Candidate snapshots do not freeze account status for dispatch. Existing selector reads remain authoritative; the broader Pause boundary/race investigation stays in INC-08.
- A source test pass does not verify the released image. Record Docker revisions/digests separately and leave cloud checks pending until an authorized commit/push exists.

## Migration Plan

No database or configuration migration. Verify locally before any separately authorized publication; roll back by reverting the focused code/spec change if deployment later reveals a regression.
