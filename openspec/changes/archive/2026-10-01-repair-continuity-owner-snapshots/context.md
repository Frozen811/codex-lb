## Purpose and scope

This change addresses audit F-001 through F-004 and reviews the additional community patch. Its normative contract is in [the delta spec](specs/responses-api-compat/spec.md); the existing architecture ratchets remain in [proxy-architecture](../../specs/proxy-architecture/spec.md).

## Evidence and decisions

On 2026-10-01, baseline 7ec39f82 produced 6 passed / 3 failed in the focused owner-miss set, including real DetachedInstanceError on HTTP Responses and compact. The architecture checker reported 3037 lines against 3021 and compact's forbidden cross-domain import. The provided patch's runtime cloning direction is valid; its test expectation changes require the explicit scoped fallback contract recorded here.

## Example and failure modes

For a key assigned only to account A, unrelated account B does not create ambiguity. A lookup miss can pin A, then normal admission can permit or reject it. For a key assigned A and B, pausing B does not prove that A owns a response; that request remains ambiguous. A listing exception is a refusal, not permission to select freely.

## Operational limits

No live account traffic or production restart is part of verification. Docker latest currently identifies f622c563, while hardened.3 identifies deed76ba; neither represents these local edits. Routing after a Codex update and observed quota depletion after Pause need separate client/log/timestamp evidence.
