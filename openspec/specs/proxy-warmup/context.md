# Compact warmup fallback

The normative behavior is in [spec.md](spec.md). A compact 404 triggers one minimal plain Responses call pinned to the same selected account. Other HTTP errors retain the original failure path; replaying an accepted response is outside this fallback.

The plain producer omits max_output_tokens, matching operator probes. The common transport already filters unsupported fields, so an unsupported producer field alone is not evidence that the wire request is broken. Completion is established by response.completed, and the fallback closes its iterator before releasing account capacity. A consumer adapter that returns silently must not manufacture a completed response.

For example, response.completed with usage 5 input and 3 output tokens produces those exact request-log counts. The same completed event without usage produces null token fields. Previously that case manufactured 1 input and 1 output token; no usage estimate is needed for warmup traffic.

Local HTTP-server tests cover compact 404, non-404 refusal, EOF, authored failure/incomplete, missing usage, and Force Probe payloads. Separate adapter tests cover silent exhaustion and explicit iterator closure. These controls do not certify a live provider, a published package, or production. See the [2026-10-05 verification](../../changes/archive/2026-10-05-repair-warmup-fallback-and-reset-evidence/verification.md).
