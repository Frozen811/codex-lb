## Context

Root turns currently skip operation registration; existing event spooling therefore cannot reconstruct their children. The existing account-neutral projector reads terminal output but does not require every observed added item to have a done frame. Developer input, empty prewarm prefix proofs, same-owner agent resends and WebSocket receive ownership already have implementations and specs.

## Goals / Non-Goals

Goals: capture roots with existing storage, validate complete replay evidence, and verify five selected records at current public boundaries.

Non-goals: dispatch-generation migration, new snapshot columns, mixed-version deployment, publication or live provider validation. Preserve existing unrelated dirty work.

## Decisions

- Use existing operation/event storage instead of activating the unused transcript-core snapshot fields. Root fingerprints include the durable session and request identity so identical independent roots do not acquire the global anchored-request deduplication identity.
- Share a pure terminal materializer between transcript loading and account-neutral projection. Require matching identities and observed lifecycle completion; allow a terminal-only complete answer or omitted terminal output with complete done frames.
- Require the parent chain to remain inside one authorization scope. Account ownership remains governed by existing replay projection and dispatch policies.
- Retain all owner/admission/size/cleanup fences by extending the existing registration path, rather than introducing a second root path.
- Await registration through the existing cancellation-deferral helper so its committed receipt reaches interruption cleanup. For independently permitted output-free root retries, drain/discard predecessor lifecycle writes and retain the same operation identity through an owner-fenced reset. An acknowledged predecessor needs its captured response ID; an unacknowledged one needs no response ID or spool. Parent anchors and completed operations refuse reset. The root ledger does not itself grant replay permission, and roots add no wire operation tag or frame-budget overhead.
- Existing corrections receive route and negative-control evidence; do not rewrite working code merely because its source issue row is stale.

## Risks / Trade-offs

- Additional root ledger writes add persistence work. Existing batchers and retention bound storage; focused tests cover interrupted registration and repeats.
- Old transcripts lacking roots or complete lifecycle evidence become ineligible. Refuse recovery instead of fabricating history.
- Synthetic upstream tests prove local contracts, not live provider, Desktop or multi-replica behavior.
