## Context
The current fork has a scalar quota cap and a verified dirty repair package. Published PR #1528 implements shared admission and reserve display on a different migration history.

## Goals / Non-Goals
Finish the remaining reserve contract, preserve the other four tasks and omit publication and unrelated CI/dependency updates.

## Decisions
Reuse upstream policy evaluation, authoritative owner snapshot, atomic configuration update and transport/warm-up gates. Merge with strict reauth rejection, terminal cleanup, retained reset evidence and warm-up fallback. Retain legacy quota-limit API and backup compatibility. Add one forward migration and backfill existing positive caps, preserving legacy values for downgrade. Retain the fork's observed monthly-window semantics and writer serialization.

## Risks / Trade-offs
Final authorization requires realistic owner/usage fixtures; preserve product assertions when adapting test doubles. Verify the subsystem slices and prior package. Local tests do not certify provider/production/cloud or unavailable server databases.

## Attribution
Adapted from NikitaMGrimm/codex-lb at caf31b77a4ef85047459635e956fdd62f7fbd7ce (upstream PR #1528); aaravrav is credited there for the complementary reserve design. Merge plan and preserved hashes are retained with this change.


## Fork-specific decisions verified during integration

Unavailable lower-health peers do not select the health tier, but their hard-block evidence remains available for bounded backoff fallback. Final owner snapshots include legacy zero caps and revoked-credential reasons. Usable warning reauth remains supported by manual warm-up. Retry budget is eight; stale admissions still authorize the final owner and release every lease. Existing cap-zero error now uses the canonical policy HTTP 429 envelope. MySQL uses UPDATE plus a locked projection in the same transaction. Browser scenes use synthetic example.invalid data and both baseline/current UI, with local Vite helpers stopped after capture.
