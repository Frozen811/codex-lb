## Context

Fan-out uses one public API-key reservation and separate internal Responses calls. The current gather handles ordinary partial failures but releases the reservation on cancellation, losing already completed subcall usage. It also awaits model-log rewriting before transferring settlement ownership. Signing already calls the configured key resolver; reset consume already refuses a missing target workspace ID.

## Goals / Non-Goals

Goals: preserve completed usage and owned task cleanup; prove environment-over-file signing and missing-target refusal at external ingress. Non-goals: real credit redemption, external services, release publication, and changes to the upstream pool policy.

## Decisions

- Keep explicit child tasks so cancellation can cancel outstanding subcalls, drain them, and inspect successful results. Use the existing cancellation-deferral utility for mandatory drain and settlement. Propagate cancellation after settlement ownership transfers.
- Aggregate captured image tokens before awaiting any log work. Transfer the sole reservation before rewriting request log models; logging failure cannot release completed usage.
- Keep generic exception responses bounded and free of raw exception text.
- Retain existing bridge and reset production implementations unless regressions reveal a defect. Exercise real signed headers and receiver verification after settings cache changes, and authenticated reset routes with real persisted accounts.

## Risks / Trade-offs

Cancellation waits for cooperative child cleanup and critical reservation handoff. Existing upstream budgets and tracked persistence drain remain authoritative; no extra runtime settings are introduced. Successful images completed before cancellation are charged even though the client does not receive a combined image response.
