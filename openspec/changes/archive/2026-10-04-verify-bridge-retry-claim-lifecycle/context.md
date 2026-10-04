# Bridge retry verification and cancellation ownership

This local batch processes exactly UP-ISSUE-2273, UP-ISSUE-2272 and UP-ISSUE-2271. The first two already have source implementations. Their verification now includes loopback upstream frames, public HTTP aliases, real durable SQLite rows, interpreted frames and negative eligibility cases.

For example, a terminal containing only `incomplete_details.reason = stream_incomplete` contributes one eligible strike. A distinct dispatched request contributes a second and opens the durable cooldown. Replaying the stored terminal adds no send or strike. Proof-gated full-history replay remains an existing permitted recovery route; the circuit is not a blanket ban on all traffic. Native stored-operation replay retains its existing downstream lifecycle and is not certified as a universal terminal-payload replay contract by this batch.

A persisted cooldown whose deadline has elapsed does not create a phantom local transition. A local cooldown already observed before expiry keeps its actual transition and permits one local half-open probe. Repeated durable loads leave that active lease owned by its request.

Submission previously awaited a claim directly, so caller cancellation after commit could discard the receipt. It now owns a scheduler task bounded across key-lock acquisition and the DB call, defers cancellation, attaches the receipt and attempts undispatched fenced release. Cleanup itself is cancellation-deferred. A new row's inserted epoch is retained, and the repository reads the receipt inside its write transaction before commit so a successor cannot substitute its own receipt.

Durable release does not clear process-local probes. The existing submission finalizer already returns the exact local lease token it owns. Repeating that operation in the durable helper without the local token erased replacement state even after a failed durable CAS.

The local implementation uses existing settings, schema and timeout. Crash abandonment/reclamation, uncertain DB timeout outcomes, generation rollback ABA and ordinary-success/newer-claim settlement policy remain open parts of UP-ISSUE-2271. No PostgreSQL/MySQL migration/runtime, live provider, cloud checks, release or production evidence is claimed.
