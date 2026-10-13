## Scope and example

Exactly five selected records: UP-ISSUE-1898, UP-ISSUE-2563, UP-ISSUE-2574, UP-ISSUE-2582 and UP-ISSUE-1304. The initial selection considered UP-PR-2579, but it was replaced before implementation by UP-ISSUE-1304; generation migration is not part of this package.

For example, a root containing developer rules and a user request emits a function call. A child containing its function_call_output must reconstruct one copy of the rules, request, call, output and answer after the owner's socket expires. A delta after an empty prewarm cannot make the same claim when it omits the prewarm prefix.

## Decisions and constraints

Reuse operation/event storage and the existing account-neutral projector. Keep developer messages in input, preserve same-owner encrypted agent messages, and retain the owned downstream receive through handoff. Do not infer cross-account permission from an encrypted full resend.

Root identity is local to the transcript ledger and adds no upstream operation tag; anchored tags retain their existing behavior. A disarmed send attempt remains ambiguous and cannot be replayed. Prewarm prefix proof and transport permission are independent: a matching full prefix may recover after a coded clean close, while a frameless account-neutral drop still terminates without replay.

The agent route matrix adds an alternate account before reconnect, intentionally invalidating selection data. The owning "Sticky admission observes policy changes during persistence" requirement in `openspec/specs/account-routing/spec.md` permits a named selection_state_changed refusal. The client test retries at most three times, asserting that each such refusal made no upstream connection or frame before retry. Other errors retain their normal negative-control handling.

## Failure modes

Missing root, mismatched response, unfinished item, missing parent, changed prefix, unknown manifest and unavailable opaque-context owner all refuse reconstruction. Terminal-only complete outputs are legitimate; omission of output can be repaired from complete done frames only.

## Verification boundary

Local route/socket stand-ins and isolated databases only. Registry closure must cite exact saved evidence and retain external limitations. Initial files are backed up with a hash manifest under the task-specific temporary directory.
