## Context

The dispatch wrapper establishes payload ownership after any yielded output or an ambiguous failure. Existing quota recovery can project redundant reasoning from a complete transcript, but rejects compaction. File clients already carry typed phase/replay evidence, and the balancer already threads hard-owner backoff admission through sticky and unbound paths.

## Goals / Non-Goals

Add the missing ciphertext-only rejection exception and verify all five selected source contracts. No provider-state portability claim, migration repair, new retry loop, setting, or release action is part of this change.

## Decisions

- Classify only known top-level reasoning/compaction ciphertext items; reject unknown fields and validate their remainder. Validate the rest with the existing strict whole-request predicate. This avoids discarding unknown ownership state along with an encrypted item.
- Re-evaluate against the current request at dispatch. Existing replay projection can replace the body, so an initial cached classification could become stale.
- Retained reasoning in a proven bypass full resend uses the existing strict auth-recovery projection to validate known fields and retain the answer. Prepare a candidate against API-key-scoped durable proof, but activate it only after pre-visible quota evidence or persisted quota owner loss. The initial body and aliases remain intact; retiring a turn-state owner also re-derives affinity after removing aliases so the old hard key cannot block the replacement. A different request body or existing dispatch owner cannot activate the candidate.
- A rejection before the first yielded line can prevent a new payload owner. Existing owners and preferred/file/turn-state gates remain authoritative; no general owner reset is introduced.
- Reuse the existing bounded selection, deferred health/settlement, and lease cleanup. Track only diagnostic provenance, and keep ciphertext out of logging.
- Test product paths with real ASGI routing/SQLite and controlled upstream adapters, plus deterministic classifier boundaries. Verify existing file, model, backoff, and durable-history tests rather than transplant upstream branches and their unrelated migrations.

## Risks / Trade-offs

- Ciphertext may be account-specific: the replacement's rejection remains visible and health-neutral, with a provenance diagnostic.
- Overly broad classification could release unknown ownership: use known-item shape validation and negative product-path controls.
- Prior dirty work shares registry/spec files: preserve baseline copies and compare unaffected files/rows before closure.

## Migration Plan

No schema migration. Source deployment and rollback follow normal release processes outside this locally authorized task.
