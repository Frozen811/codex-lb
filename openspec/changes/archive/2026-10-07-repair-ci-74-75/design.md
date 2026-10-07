## Context

See proposal.md for the two observed CI failures. The shared dashboard CopyButton already owns its feedback timer; the OAuth-local control has different styling, a two-second feedback duration and pointer blur behavior, so replacing it with the shared visual component would alter unrelated UX.

## Goals / Non-Goals

Own the local control's asynchronous work and retain container scan evidence. Do not change clipboard utilities, frontend timeouts, vulnerability severity policy, repository security settings or report-upload failure semantics.

## Decisions

- Follow the shared copy control's mounted-ref and timer-ref lifecycle pattern locally. Cancel the previous reset on each success, clear it during unmount, and guard both clipboard resolution and rejection before feedback.
- Run the blocking table scan first. Run SARIF generation with `always()` after a successful Docker build, retain a successfully generated report with the pinned upload-artifact action, and publish only successfully generated SARIF under the existing trusted-event condition.
- Keep upload errors blocking. CI #75's log ends at "Uploading results" without an error or annotation; Code Scanning analyses for prior main commits are present, so disabled permissions are not established. A new exact-SHA cloud run is needed to establish recovery.

## Risks / Trade-offs

- GitHub Security availability can still fail CI; retaining the report and evaluating vulnerabilities first preserves evidence without hiding that failure.
- Fake timers also observe dialog focus timers; regression cases advance those before measuring the copy control's pending resets.
