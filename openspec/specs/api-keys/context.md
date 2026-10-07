# API Keys Context

See `openspec/specs/api-keys/spec.md` for normative requirements.

## Request-aware reservation estimate

The admission budget for token and `cost_usd` limits (Requirement
"Request-aware API-key usage reservations") sizes the input side from the
forwarded request payload: `min(utf8_length(serialized_payload_minus_caps), 8192)`.
Two implementation notes keep that value exact while avoiding redundant work on
the hot path:

- **Shared dump.** `ResponsesRequest.to_payload()` is deterministic, so the
  HTTP bridge prepare path computes it once and threads the same dict through
  client-metadata derivation, the forwarded `response.create` frame and
  `estimate_api_key_request_usage(payload, upstream_payload=...)`. The budget,
  frame bytes and input fingerprints are byte-identical to computing each stage
  from its own dump. When the prepare path rewrites the request (replayed
  side-effect tool-call dedupe under `previous_response_id`) the caller's dump
  is discarded and recomputed from the rewritten request, so the forwarded
  frame never carries un-deduped input. Callers that do not hold a dump keep
  the default single-argument form.
- **Early-exit serialization.** Because the estimate is capped at 8192 bytes,
  the estimator returns the cap as soon as it is proven: an `instructions`
  string of 8192+ characters alone suffices (a JSON string literal is never
  shorter than its character count), otherwise the payload is streamed through
  the same `sort_keys`/`ensure_ascii=False` encoder and stopped once 8192 bytes
  have been produced. Sub-cap payloads still yield the exact serialized length.
  The opaque-context checks (`previous_response_id`, `conversation`, file or
  image references) run before either shortcut, so the conservative `None`
  budget is unchanged.

Edge: a lone surrogate (`"\ud800"`) anywhere in the payload used to raise
`UnicodeEncodeError` (HTTP 500) from the full dump. It now raises only when it
sits in a chunk that is actually UTF-8 encoded, i.e. within the first ~8 KiB of
serialized output and not inside a string literal that the length shortcuts
(`instructions` >= 8192 chars, or a single chunk that alone covers the
remaining budget) prove the cap without encoding. Surrogates skipped that way
yield the 8192 cap like any other large payload.

## Estimated usage-share policy

`usage_share_percent` is an optional API-key policy, not an `ApiKeyLimit` counter. `ApiKeysService` builds the current rough estimate while producing `ApiKeyData`, so HTTP authentication reuses the normal API-key cache and direct WebSocket policy refresh uses the same projection code. The estimate has no independent ledger, reservation, scheduler, or cache.

The estimator combines current long-window account usage with the key's proportional request demand over those account windows. Assigned keys use their assigned account pool; unscoped keys use the eligible global pool. For monthly-capacity plans, a later weekly-duration quota explicitly reported in the primary slot supersedes older monthly residue; an ordinary secondary row never does. Missing evidence is surfaced as account ids on the policy snapshot rather than guessed as zero.

## Effective tier and microdollar settlement

The [monetary settlement contract](spec.md#requirement-effective-ultrafast-tier-settles-exact-monetary-limits) uses the response's effective tier and the same cached-read/write partition as request logs. Decimal rate products avoid subtracting one microdollar at integral boundaries through a float USD roundtrip. Genuine fractions are still truncated.

For example, 32 input and 7 output Astra Ultrafast tokens settle 4020 microdollars. A response confirming default is priced at default even when the request asked for Ultrafast. Finalization remains idempotent and exhausting a cost limit prevents the next dispatch; no subscription credits or historical non-NULL request costs are rewritten.

## Images in dashboard model selection

The [image model selection contract](spec.md#requirement-supported-image-models-in-key-model-selection) shares the request validator's supported identifiers with the dashboard picker. Typed entries carry image-only metadata, no reasoning options and native ownership. Adapter entries remain available with an empty native registry, and built-in image identifiers take precedence over colliding catalog/source identifiers.

For example, an administrator can create a key allowing `gpt-image-2` and later replace its allowlist with `gpt-image-1-mini`. Both selections persist through the existing key APIs. The dashboard is a configuration catalog, so it additionally exposes these adapters; the public Responses catalog retains its native filtering. Automations filter out image-only entries because they use text generation. Dashboard-read authorization is unchanged, and no provider probe is needed to populate the picker.

## Usage controls and observation windows

The [credit override contract](spec.md#requirement-credit-windows-are-display-only-overrides) makes the existing Codex display values explicit. There is no reliable model/tier credit conversion, so normal traffic does not accrue this counter and an exhausted credit override cannot reject traffic. Token and cost rules remain enforced budgets; existing credit values and `/v1/usage` stay readable.

For example, selecting 30 days on the API-key page fetches both usage totals and the trend with `days=30`, using distinct cache entries and labels. The lifetime inventory and overview retain their lifetime scope. Retention limits the available history; changing the window cannot restore deleted logs.

Bulk reset preserves credentials and request history. If two selected keys are reset and one fails, the failed key's name and error remain visible and that key remains selected for retry. Successful keys leave the selection and their counters refresh through the existing list invalidation.
