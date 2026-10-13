# Model Source Routing — Context

## Purpose

Capability-based routing and accounting for OpenAI-compatible model sources,
including field-preserving embeddings forwarding.

This capability keeps source selection separate from subscription-account
routing: embeddings traffic is served only by sources that declare the
embeddings capability, while Responses/chat/audio continue to use their own
capability gates. Field presence (including explicit nulls) is preserved on
embeddings forwards so compatible sources see the same payload shape the
client sent.

## CPA discovery in the fork

`catalogMode` defaults to `manual`. The dashboard API accepts `cli_proxy_api`
only for a Responses-capable source. The existing leader model refresh tick
reads its inference-authenticated `/models?client_version=...` catalog, including
when no subscription accounts exist. Initial discovery can wait up to the existing
five-minute cadence. Four workers share five seconds and a 1 MiB response bound.

The database is the last-good snapshot. A valid omission changes `isAvailable`
without deleting the model row; restoration preserves its ID and operator
`isEnabled` value. Catalog metadata describes provider claims rather than proven
tool or reasoning support. Unknown metadata and secrets are discarded. Failed,
malformed, oversized or redirected catalogs preserve the last-good rows.

For example, create a source with `supportsResponses: true`,
`catalogMode: cli_proxy_api`, an inference URL/key and an empty model list. After
the next tick, discovered models appear in public and Codex catalogs. An omitted
model returns `503 model_source_unavailable` without subscription fallback. Native
registry identities and recorded native continuation owners retain precedence.

Operator edits invalidate in-flight refresh revisions. Replace discovered model
rows only after switching the source to manual mode; this avoids removing retained
identities accidentally. Existing manually paused rows stay paused during discovery.
Disable the whole source to pause discovery and serving. Re-enabling uses the next
scheduled tick. Native Responses WebSocket source forwarding and live CPA/provider
acceptance are separate contracts. Source remote compaction continues to follow the
fork's [clean refusal contract](../responses-api-compat/spec.md); the historical
forwarding proposal is not implemented by discovery.
