# Responses API Compatibility Context

## Collaboration namespaces on model sources

The [source tool-filtering contract](spec.md#requirement-source-routed-responses-tools-are-capability-filtered)
uses a nonblank string `multi_agent_version` as an explicit namespace opt-in,
including future versions. `{"multi_agent_version":" v99 "}` therefore keeps
the client's complete `collaboration` namespace and nested schemas. Missing,
blank or non-string declarations stay conservative; explicit
`experimental_supported_tools: ["namespace"]` also permits namespaces.
This declaration does not enable source WebSocket transport or modify the
source's instructions, and clients using a pinned catalog need to refresh it.

Choice filtering follows the tools that survived. For example, if a source
keeps `shell` but drops `collaboration`, a forced
`{"type":"function","namespace":"collaboration","name":"spawn_agent"}`
is removed. In an `allowed_tools` choice, that entry is pruned while the bare
`shell` entry and `mode` remain. Previously the dangling function choice could
make an otherwise repaired request fail upstream. A declared namespace keeps
the namespaced function choice intact.

Recording loopback upstreams verify both Responses routes and slash variants,
including schemas, choices and hosted-tool include pruning. Real provider
collaboration behavior and public/cloud artifacts require separate evidence.

## Standalone search ingress

The [search alias requirement](spec.md#requirement-standalone-search-ingress-aliases-are-slash-equivalent)
covers canonical Codex, `/v1` and duplicated Codex-prefix paths. For example,
`POST /v1/alpha/search/?tag=a&tag=b` dispatches directly to `codex/alpha/search`
with the original bytes and both query values. Previously the slash form hit
the catch-all route and returned 405 rather than reaching search.

Hidden slash routes reuse the control handler and its authentication, scope,
media-type replacement and error normalization. Local HTTP upstream tests
verify gzip decoding and a single Content-Type field; native routed transport
tests cover JSON/SDP casing and bodyless removal. These checks use synthetic
search output and do not establish live hosted search or public image parity.

## Purpose and Scope

This capability implements OpenAI-compatible behavior for `POST /v1/responses`, including request validation, streaming events, non-streaming aggregation, and OpenAI-style error envelopes. The scope is limited to what the ChatGPT upstream can provide; unsupported features are explicitly rejected.

See `openspec/specs/responses-api-compat/spec.md` for normative requirements.

## Bounded fallback after subscription owner lookup misses

The [hard continuity ownership requirement](spec.md#requirement-hard-continuity-owner-lookup-fails-closed)
distinguishes possible historical ownership from current routing eligibility.
The fork's community continuity patch and upstream issue
[#2274](https://github.com/Soju06/codex-lb/issues/2274) motivated this clarification.
Candidate rows are copied while the repository session is open so later reads
do not depend on expired ORM state. Shared resolution belongs to the service
support domain; required-owner admission still belongs to account selection.

For example, a key assigned only to A can pin A after a successful lookup miss
even when unrelated B exists. For a scope containing active A and paused B,
the same miss is ambiguous: pausing B does not establish A's ownership. A sole
paused candidate can be identified but still fails normal admission. Codex
affinity does not establish ownership for an arbitrary previous-response ID,
including on a reused socket. Model-source transport handling remains governed
by its separate source-routing contract.

The regression tests use real session teardown and public HTTP, compact and
direct WebSocket paths. These tests do not establish the cause of observed
quota depletion after Pause or verify a published Docker tag; those require
independent client, request-log and artifact evidence.

## Rationale and Decisions

- **Responses as canonical wire format:** Internally we treat Responses as the source of truth to avoid divergent streaming semantics.
- **Strict validation:** Required fields and mutually exclusive fields are enforced up front to match official client expectations.
- **Cursor alias compatibility:** Cursor UI model labels may append reasoning or speed suffixes to GPT-5 slugs; those are normalized to canonical upstream fields before forwarding.
- **No truncation support:** Requests that include `truncation` are rejected because upstream does not support it.
- **Compact as a separate contract:** Standalone compact is treated as a canonical opaque context-window contract, not as a variant of buffered normal `/responses`.

## Constraints

- Public-contract SSE filtering uses the `response.*` and `error` families, so
  diagnostics such as `responsesapi.websocket_timing` cannot interrupt strict
  client event deserializers. For example, a timing diagnostic between a text
  delta and `response.completed` is removed while both standard events remain.
  Native Codex requests retain vendor events; OpenAI-shaped backend requests
  follow public filtering. This does not normalize string-valued
  `response.instructions` or establish full IntelliJ compatibility (Refs #1934).

- Upstream limitations determine available modalities, tool output, and overflow handling.
- `store=true` is rejected; responses are not persisted.
- `include` values must be on the documented allowlist.
- `truncation` is rejected.
- `previous_response_id` is forwarded when `conversation` is absent, but the `conversation + previous_response_id` conflict remains rejected.
- HTTP `/v1/responses` and HTTP `/backend-api/codex/responses` now use a server-side upstream websocket session bridge by default so repeated compatible requests can keep upstream response/session continuity without forcing clients onto the public websocket route.
- Codex-affinity HTTP bridge sessions can optionally use a conservative first-request prewarm (`generate=false`), but that behavior stays behind an explicit switch so production defaults do not pay an extra upstream request unless operators opt in. The switch is the dashboard setting `http_responses_session_bridge_codex_prewarm_enabled` (Settings → Advanced → Session bridge), resolved from the settings-cache snapshot before a session's prewarm lock; its `CODEX_LB_*` environment variable is a deprecated alias that applies only while the dashboard value is unset.
- When operators configure a multi-instance bridge ring, deterministic owner enforcement now applies only to hard continuity keys such as `x-codex-turn-state` and explicit session headers. Prompt-cache-derived bridge keys remain stable for local reuse, but in gateway-safe mode a non-owner replica may tolerate that locality miss and create or reuse a local session instead of failing with `bridge_instance_mismatch`.
- Codex-facing websocket routes now advertise `x-codex-turn-state` during websocket accept and honor client-provided turn-state on reconnect so routing can stay sticky at turn granularity even when the public websocket reconnects.
- HTTP responses routes now also return `x-codex-turn-state` headers so clients that persist response headers can promote later HTTP requests from prompt-cache affinity to stronger Codex-session continuity.
- `/v1/responses/compact` keeps a final-JSON contract and preserves the raw upstream `/codex/responses/compact` payload shape as the canonical next context window instead of rewriting it through buffered `/codex/responses` streaming.
- Compact transport failures fail closed with respect to semantics: no surrogate `/codex/responses` fallback and no local compact-window reconstruction.
- Compact transport may use bounded same-contract retries only for safe pre-body transport failures and `401 -> refresh -> retry`.
- `/v1/responses/compact` is supported only when the upstream implements it.
- `prompt_cache_key` affinity on OpenAI-style routes is intentionally bounded by a dashboard-managed freshness window, unlike durable backend `session_id` or dashboard sticky-thread routing.
- Codex-native direct websocket `/backend-api/codex/responses` treats upstream `previous_response_id` as an ephemeral anchor. If that anchor goes stale, the proxy masks raw upstream details and emits the sanitized canonical `previous_response_not_found` classifier so compatible Codex clients can retry with full local history and no `previous_response_id`. The upstream Codex socket has emitted this condition both with the canonical code and as a parameterless `invalid_request_error` carrying ``Invalid `previous_response_id`.``; both shapes use the same recovery policy.
- Upstream Responses WebSockets use transport ping/pong control frames to detect a black-holed connection without confusing valid application-event silence with an idle turn. Direct and routed connections reuse `proxy_downstream_websocket_idle_timeout_seconds` for this zero-config liveness budget.
- A post-send liveness timeout is delivery-ambiguous. It remains account-neutral, is never transparently replayed, and retires the affected upstream socket so a client retry opens a fresh route without risking duplicated model work or tool side effects.
- An HTTP SSE first-event `stream_idle_timeout` is also account-neutral for health writes. The request may still exclude that account and fail over, but idle silence must not increment `error_count` or move the account into probe/drain.
- HTTP bridge settlement ownership is explicit: `closed` rejects new work but does not imply that a submitter owns existing siblings. Only a liveness-failed send claims whole-deque settlement under the lifecycle lock; otherwise the reader remains responsible for settling pending requests when the transport dies.
- A DRAINING durable row with a live lease is still owned. Foreign `claim_live_session` and local session create must not steal it, including when forced recovery would otherwise run because the owner endpoint is missing; expired or ownerless DRAINING rows remain recoverable.
- Hard-affinity retry-circuit evidence is request-lifecycle evidence: retirement counts only while the bridge still owns an eventless pending request. Idle no-pending retirement remains observable but neutral, so routine socket churn cannot manufacture the first strike for a later real timeout.

## Fast Mode and Service Tiers

codex-lb accepts the OpenAI/Codex `service_tier` field on Responses and Chat
Completions compatible routes. The legacy `fast` spelling is accepted as an
alias and is forwarded upstream as the canonical `priority` tier.

Fast Mode is request-level intent, not a local speed guarantee. The upstream
Codex backend decides the actual tier for each completed response. codex-lb
therefore records three separate values in request logs:

- `requestedServiceTier`: what the client or API key asked for, after alias
  normalization.
- `actualServiceTier`: what upstream reported in the completed response, when
  upstream included it.
- `serviceTier`: the effective billable tier. This uses `actualServiceTier`
  when present and falls back to `requestedServiceTier` only when upstream omits
  the actual tier.

If a request is sent with `service_tier: "fast"` or `service_tier: "priority"`
and the completed row shows `requestedServiceTier: "priority"` but
`actualServiceTier: "default"`, codex-lb forwarded the priority request and
upstream chose the default tier. That can happen even when websocket transport
is active.

For OpenCode or Codex-compatible clients, enable Fast Mode by sending a
Responses request with:

```json
{
  "service_tier": "priority"
}
```

Clients that expose Fast Mode as `fast` may keep using that spelling; codex-lb
normalizes it to `priority` before forwarding.

### Ultrafast Processing

The [OpenAI Responses API reference](https://developers.openai.com/api/reference/resources/responses/methods/create)
documents `ultrafast` as an access-controlled processing tier currently
available for `gpt-5.6-sol`. codex-lb forwards this canonical value unchanged;
it does not grant Ultrafast access by itself.

Account eligibility comes from live or retained per-account upstream catalog
metadata. The bundled bootstrap catalog deliberately does not advertise
Ultrafast. If no account advertises the tier, an explicit Ultrafast request
cannot select an eligible account; API-key enforcement follows the existing
model-capability fallback when the model itself does not advertise the tier.

Send a Responses request with:

```json
{
  "model": "gpt-5.6-sol",
  "input": "Summarize the change.",
  "service_tier": "ultrafast"
}
```

After completion, verify that the response reports
`service_tier: "ultrafast"`. Request logs retain `ultrafast` in the requested,
actual, and effective billable tier fields when upstream confirms it.

### Operator Fast Mode prohibition

Operators can enable the Routing setting `prohibitFastMode` when qualified
Codex harness model aliases such as `gpt-5.6-sol-xhigh-fast` must run at the
normal OpenAI tier. The alias still supplies its canonical model and reasoning
effort, but does not derive `service_tier: "priority"`. This policy does not
rewrite an explicit client tier or an API-key-enforced tier; see
`openspec/specs/fast-mode-policy/context.md` for scope and operating notes.

API keys can also force the tier for traffic that uses that key. Set the key's
enforced service tier to `priority` or `fast`; both values are stored and
returned as `priority`.

To verify a completed Fast Mode request:

1. `Transport` should be `WS` if you are verifying the websocket Codex path.
2. `requestedServiceTier` should be `priority` when the client requested Fast
   Mode or the API key enforced it.
3. `actualServiceTier` is the upstream result. `default` means upstream did not
   grant priority for that response.

This distinction matters for quota and cost accounting: codex-lb prices the
request from the effective billable `serviceTier`, not from the requested tier
when upstream reports a different actual tier.

## Include Allowlist (Reference)

- `code_interpreter_call.outputs`
- `computer_call_output.output.image_url`
- `file_search_call.results`
- `message.input_image.image_url`
- `message.output_text.logprobs`
- `reasoning.encrypted_content`
- `web_search_call.action.sources`

## Failure Modes

- **Stream ends without terminal event:** Emit `response.failed` with `stream_incomplete`.
- **Upstream error / no accounts:** Non-streaming responses return an OpenAI error envelope with 5xx status.
- **Compact upstream transport/client failure:** Retry only inside `/codex/responses/compact` when the failure is safely retryable; otherwise return an explicit upstream error without surrogate fallback.
- **HTTP bridge session closes or expires:** The next compatible HTTP `/v1/responses` or `/backend-api/codex/responses` request recreates a fresh upstream websocket bridge session; continuity is guaranteed only within the lifetime of one active bridged session.
- **Multi-instance routing without bridge owner policy:** if operators do not configure a bridge ring or front-door affinity, continuity can still fragment across replicas. With a configured bridge ring, hard continuity keys landing on a non-owner replica are proxy-forwarded to the owner replica; the proxy fails closed only when the owner endpoint or ring membership cannot be resolved or the forward signature fails authentication. Gateway-safe prompt-cache requests may accept locality misses and continue locally instead of forwarding.
- **Codex websocket reconnects:** Reconnect continuity now depends on the client replaying the accepted `x-codex-turn-state`; generated turn-state is emitted on accept for backend Codex routes and echoed back when the client already supplies one.
- **Codex websocket stale previous-response anchors:** Direct backend Codex websocket stale-anchor failures are either replayed transparently from a self-contained full resend or surfaced as a sanitized `response.failed` whose `response.error.code` is `previous_response_not_found`; the error omits `param`, the raw upstream envelope, and the missing `resp_...` id. A connect-time failure uses the same code directly at `error.code`. This includes the parameterless upstream message ``Invalid `previous_response_id`.``. OpenAI-compatible `/v1/responses` websocket clients continue to receive generic `stream_incomplete` masking.
- **Websocket handshake forbidden/not-found:** Auto transport now fails loud on `403` / `404` instead of silently hiding the websocket regression behind HTTP fallback.
- **Upstream websocket stops answering pings:** Pending direct-WebSocket and HTTP-bridge work fails with `upstream_websocket_liveness_timeout`; the account remains healthy and the request is not replayed because upstream acceptance is unknown.
- **Repeated eventless bridge failures:** Two consecutive request-affecting pre-response failures can open the hard-key cooldown. A successful terminal response clears the state; an idle close followed by one real timeout remains only one strike.
- **Invalid request payloads:** Return 4xx with `invalid_request_error`.

## Error Envelope Mapping (Reference)

- 401 → `invalid_api_key`
- 403 → `insufficient_permissions`
- 404 → `not_found`
- 429 → `rate_limit_exceeded`
- 5xx → `server_error`

## Examples

Non-streaming request/response:

```json
// request
{ "model": "gpt-5.1", "input": "hi" }
```

```json
// response
{ "id": "resp_123", "object": "response", "status": "completed", "output": [] }
```

Cursor-style model alias request:

```json
{ "model": "gpt-5.4-mini-high", "input": "hi" }
```

This forwards upstream as `model: "gpt-5.4-mini"` with `reasoning.effort: "high"`.

Retry-circuit accounting example: an idle bridge closes with `pending=0`, then
the next request times out before `response.created`. The idle close is logged
but contributes no failure; the timeout is the first strike. Only another
consecutive eventless pending failure may open the repeated-failure cooldown.

Stale-anchor recovery example: a reconnect sends a tool-output delta with a
recent `previous_response_id`, and upstream answers
``{"type":"error","status":400,"error":{"type":"invalid_request_error","message":"Invalid `previous_response_id`."}}``.
Because the delta cannot stand alone, codex-lb returns a sanitized
`previous_response_not_found` signal on the Codex-native route so the client can
retry once with full local history. If the original request already contained a
self-contained full resend, codex-lb instead reconnects and replays that body
without the rejected anchor.

## Previous-response replay owner fencing

Removing a stale continuation anchor does not make every retained body
portable. Encrypted reasoning, account-scoped items, file references, and
durable bridge operation identities remain owned by the account that first
received them. The proxy records that dispatch owner and requires it on later
HTTP streaming, HTTP bridge, and direct WebSocket selections.

For example, if account A first receives encrypted reasoning and then returns a
pre-visible Trusted Access or authentication failure, account B must never
receive the retained ciphertext. One forced token refresh may replay the body
on account A; permanent failure or owner unavailability fails closed.

Verified recovery installs a replacement body and updates owner state
atomically. A canonical account-neutral replacement clears the owner and may
use normal failover. A verified nonneutral replacement, including a
Responses-Lite full resend, may replay only on the same owner and preserves the
fence.

HTTP bridge tracing archive IDs do not pin neutral requests. A real durable
`operation_id` does pin the request until an explicit operation-rebind path
replaces that identity. Existing file pins and API-key settlement-before-health
ordering remain independent invariants.

Streaming selection authorizes owner compatibility before opening upstream, but
persists a new owner only after dispatch is observed. A transport failure that
is positively classified as pre-dispatch therefore leaves the body unowned and
eligible for its first real dispatch on another account. Ambiguous failures
remain owner-bound.

## Known Client Integrations (Reference)

Third-party agents that consume the `/v1` Responses surface documented by this
capability (rendered guide: `docs/client-setup.md`). These are configuration
examples against the existing contract, not separate compatibility surfaces:

- **OpenCode** — built-in `openai` provider with a `baseURL` override; uses the
  Responses API path so `encrypted_content` / multi-turn reasoning state is
  preserved (Chat Completions custom providers drop it).
- **OpenClaw** — custom provider with `"api": "openai-responses"` against
  `/v1`; Codex-native provider builds may target `/backend-api/codex` instead.
- **Hermes Agent** (Nous Research) — named custom provider with
  `api_mode: codex_responses` against `/v1`; the responses transport carries
  reasoning state across turns like the OpenCode path.

New client guides added to `docs/client-setup.md` should stay configuration-only
examples of this contract; anything needing new proxy behavior requires its own
OpenSpec change first.

## Pre-Visible Authentication Recovery

An HTTP 401 first gets the existing same-account refresh attempt. If authentication
cannot be repaired, complete unanchored text/tool history can move to another
account after known bookkeeping is projected out and the entire replacement passes
the canonical replay predicate. Successful refresh keeps the original body. Files,
turn state, previous responses, legacy ownership, opaque compaction, hosted results,
and unresolved tool calls cannot be discarded for recovery. For example, expired
access plus `invalid_grant` can move a complete transcript from A to B; a pinned
file request stays on A and surfaces the authentication failure. Existing
previous-response error mapping is unchanged. Reservations settle before deferred
authentication health writes, including cancellation and replacement failure.

## Operational Notes

- Pre-release: run unit/integration tests and optional OpenAI client compatibility tests.
- Smoke tests: stream a response, validate non-stream responses, and verify error envelopes.
- Post-deploy: monitor `no_accounts`, `upstream_unavailable`, compact retry attempts, and compact failure phases, especially on direct compact requests.
- Post-deploy: monitor HTTP bridge reuse/create/evict/reconnect counts and any `previous_response_not_found` or queue-saturation errors on `/v1/responses` and `/backend-api/codex/responses`.
- Post-deploy: monitor `capacity_exhausted_active_sessions`, Codex-session bridge reuse/evict counts, websocket handshake 403/404 rates after the narrower auto-fallback policy, and backend Codex HTTP vs websocket cache-ratio gaps.
- When tracing compact incidents, confirm that request logs and upstream logs show direct `/codex/responses/compact` usage without surrogate `/codex/responses` fallback.
- Post-deploy: monitor `no_accounts`, `stream_incomplete`, and `upstream_unavailable`.
- Post-deploy: monitor `upstream_websocket_liveness_timeout`; recurring failures indicate a host route, VPN, proxy, or intermediary that black-holes established WebSockets.
- Post-deploy: correlate retry-circuit `opened`, `half_open`, and `reset` events with bridge `pending` and `response_events_seen` diagnostics. An idle `pending=0` retirement must not precede an immediate two-failure cooldown.
- Post-deploy: monitor `previous_response_not_found` on `/backend-api/codex/responses`; recurring spikes show repeated continuity failures, which may come from malformed client identifiers, server-side invalidation, or connection lifecycle. Clients should perform the documented full-context retry without `previous_response_id`. Investigate socket-lifecycle remediation only when a separate close-reason, reconnect, or transport diagnostic correlates with the failures.
- Websocket/Codex CLI tier verification runbook: `openspec/specs/responses-api-compat/ops.md`


## HTTP continuation promotion

Healthy native HTTP requests use normal policy. The proxy cannot infer every
client-local WebSocket failure from HTTP alone; it uses its existing 60-second
upstream-connect failure marker as concrete failure evidence. Operator HTTP
pins and size bypasses remain effective. The image bypass keeps requests off the
HTTP session bridge but no longer pins the upstream transport, which is resolved
by ordinary precedence; an `input_image` request keeps upstream HTTP only when
its payload exceeds the WebSocket frame budget or still carries an external
image URL. External-URL detection for that decision recurses the whole input, so
a URL nested inside a tool-output array keeps the pin even though the image
inliner never rewrites it — that is the case where the URL is still external at
the upstream. The inliner and the bridge's post-inline guard still read only
top-level `input_image` items and one level of `content`; closing that is a
separate change. No new retry/session registry.

History-only locality is soft, scoped by the bridge's full API-key identifier,
and hashes the complete first user item plus instructions and model. No client
prompt cache field is overwritten. Identical initial prompts may share an idle
connection, but neither histories nor response anchors are merged; the complete
request is sent each time. Existing hard-continuity paths retain their guarded
incremental replay. Conversation IDs get their own hashed locality and are never
combined with an injected previous_response_id.

Chat keeps the existing stream conversion/usage/error/cleanup pipeline and uses
the bridge only after the source-routing branch. Backend stream=false retains
its native non-streaming upstream contract. No claimed latency percentage:
connection reuse is measured separately from admission and successful transport.

For example, a Chat client sending `[user(task), assistant(answer), user(next)]`
without session headers can open a bridge connection. Appending the next
assistant/user pair reuses that connection while sending the entire new history.
The same initial task under a different API key selects a separate connection.

Chat binds existing settlement ownership signals while advancing its bridged
stream. Predispatch failures and cancellation release origin-owned reservations;
accepted or delivery-ambiguous owner forwards retain their settlement owner.
Context bindings do not span yields because startup probes and consumers may
advance the stream from different tasks.

## HTTP response ownership before delivery

An HTTP response can expose its upstream ID before the detached request-log write finishes. The stream now publishes each authoritative lifecycle ID to the existing bounded process cache before delivering that event, beginning with `response.created` when present. An immediate follow-up can resolve the selected account while the original stream or its log write is still pending. This is same-process owner readiness; it does not promise that an unfinished response is already usable by the upstream provider.

The cache retains its existing API-key partition, session-first lookup and same-key fallback. Durable lookup and unknown-owner rejection remain the miss path. Publication adds no synchronous persistence barrier, registry or cross-replica readiness guarantee, and does not strengthen session identifiers into a new authorization boundary.

Local failure events and locally assigned response IDs are separate facts. `ParsedSseBlock.is_local` identifies generated events; `response_id_is_local` excludes a generated ID even when SDK normalization wraps a real upstream error. These flags remain outside serialized event bytes and survive parsed-payload reattachment. Thus an oversized-frame failure cannot invent an upstream owner, while a real upstream error with a locally assigned ID remains a valid event for timing. The shared HTTP/direct/routed WebSocket normalizer and this provenance contract are owned here; HTTP timing consumes them through the owner dependency. Existing durable-log behavior is unchanged. See the [ownership requirement](spec.md#requirement-observed-http-response-ids-publish-same-process-ownership-before-delivery).

Canonical background JSON acknowledgements with status `queued` or `in_progress` carry the same authoritative response identity as SSE lifecycle events. The lifecycle parser includes both, and the HTTP relay keeps queued events on the parsed path. For example, a two-account request receiving a queued acknowledgement can immediately route a same-process continuation to its known account while its originating log is pending. An in-progress event following token output has the same ownership behavior. The provider still decides whether unfinished work can be continued.

## Owner-forward SSE framing

The [owner-forward framing contract](spec.md#requirement-owner-forward-http-streams-preserve-sse-event-boundaries)
uses the canonical CR/LF separator detector while retaining the bridge's own
scheduler and request budget. For example, a created event ending in
`\r\n\r\n` followed by a completed event now reaches the origin as two events
before EOF. A trailing CR can dispatch immediately; the following LF, if any,
belongs to that ending rather than the next event.

Malformed UTF-8 decodes as U+FFFD, including final unterminated bytes; downstream
JSON validation still applies. Valid multi-byte UTF-8 split across chunks was
already buffered safely and remains intact. Ordinary owners emit LF, making
this compatibility hardening for the receiver. No migration, operator setting,
account-selection change, or new event-size policy is involved.

## Detached retirement sweep deadline

Issue #2149 bounds aggregate detached-session lock waiting during request finalization. A sweep shares five seconds: if its first attempt consumes three seconds, the next receives two, and later attempts stop at expiry. Deferred generations remain tracked for later requests and their lifecycle owners. The deadline does not cancel resource-close owners or replace their existing close timeout.

## Multiline bridge frames, Lite payloads and message-size evidence

The [complete-document framing](spec.md#requirement-http-bridge-preserves-complete-websocket-json-documents), [Lite tool-call serialization](spec.md#requirement-responses-lite-signals-serialize-tool-calls) and [close-1009 contract](spec.md#requirement-websocket-close-1009-is-terminal-and-account-neutral) apply at the final upstream/relay boundary. LF/CRLF formatting is JSON whitespace, not an SSE delimiter inside an upstream WebSocket message. Parsed output-item events are reserialized after any duplicate-tool rewrite; other unchanged single-line frames retain the existing fast path.

For example, a pretty error whose parameter is `parallel_tool_calls` reaches the client as that error without a two-minute eventless timeout. A body-derived Lite request sends `parallel_tool_calls=false` and `reasoning.context=all_turns`; inbound client headers do not create Lite trust.

aiohttp can report its own reader limit as `ERROR(WebSocketError(1009))` rather than a received close frame. Preserve this typed size evidence before generic transport recovery so an oversized message produces `payload_too_large` and releases the turn instead of penalizing the account or replaying the request. Other protocol codes retain their existing behavior. This classification does not change the configured message-size limit and makes no claim that switching accounts could repair the oversized message.

The loopback wire tests use a bounded client reader and actual aiohttp socket traffic. They establish local transport and route behavior only; public artifacts, deployed services and real upstream/client traffic require separate evidence.

## Direct WebSocket terminal provenance and selected owners

A missing close code is insufficient evidence of a transport ending. The direct
adapter marks incomplete close handshakes; the routed adapter checks closed socket
state while excluding typed protocol errors. Native I/O failure and the specific
ResetWithoutClosingHandshake variant carry transport phase; other native protocol
failures retain protocol phase. The direct relay uses this positive evidence with
the existing frame-less classifier. Output and sequence progress still govern
replay safety independently of health attribution.

For example, an already-dispatched owner's `usage_limit_reached` error with status
429, `param=input` and reset metadata reaches both direct WebSocket routes intact
when replay is unsafe. Finalization settles usage, hands off the log and writes
health once. A file-pinned body that cannot be prepared for account switch follows
the same terminal path. Pre-dispatch owner refusal keeps its existing contract.

Bounded inline PNG/JPEG images already retain bridge connections under the
default admission policy. Text/image/text and an output-free overload recovery
are verified on v1 and backend HTTP routes. Unsupported shapes, explicit rollback,
per-image and frame budgets retain their documented boundaries; production
overload percentages and real provider image acceptance remain external evidence.

## Direct native failures and admission cleanup

The [direct-native cleanup contract](spec.md#requirement-direct-native-stream-failures-release-admission-ownership) covers the HTTP path with the session bridge disabled. Nested iterator closure already propagates through the native adapter; independent route tests now verify actual account stream/response-create pressure, helper request state, persisted logs and API-key reservations rather than simulated counters.

At a stream cap of one, two consecutive failed requests must each return pressure to zero before another request is submitted. The third successful request is admitted without restart. The tests use the source-built native helper and controlled origin EOF, aborted bodies and aborted pre-header requests, across v1/backend routes, stream/non-stream modes and native Codex headers. Backend stream=false uses its existing JSON upstream contract; v1 non-stream requests still collect their upstream stream. Native committed-body failures keep their existing missing-terminal behavior.

For example, a body abort releases both account admission kinds and settles/releases the reservation; a following successful terminal finalizes the next reservation. Normal endpoint health/backoff handling remains active. This bounded sequence avoids interpreting an intentional health cooldown after a longer error streak as a leaked concurrency lease. No helper EOF is treated as evidence that replay is safe, and no production or real-client certification is inferred from loopback tests.

## Bridge continuation boundary verification

The [boundary requirement](spec.md#requirement-bridge-continuation-boundaries-preserve-actionable-outcomes) brings together the public outcomes checked for upstream issues 2493, 2465 and 2455. Existing runtime mechanisms already implement these paths; route evidence, historical descriptions and test boundaries need to stay aligned with them.

A refused continuation has two delivery boundaries. A local denied-anchor fence reached before response commitment returns the structured HTTP 502 continuity error. Once a response has begun and keepalives have reached the client, the same failure ends with one SSE terminal. An account-owned item prevents unsafe fresh replay without preventing truthful terminal delivery. Only an eligible full-history request can benefit from retirement of a conclusively denied anchor.

For example, a warmed native backend session receives response.created, then response.in_progress keepalives, and finally a masked stream_incomplete failure when its injected anchor is denied. The persisted log keeps previous_response_not_found as upstream evidence; the external response carries neither the raw anchor nor a private synthetic marker. Canonical and trailing-slash routes have the same result.

A silent lineage follows bounded retry/circuit and quarantine ownership. A later portable full transcript can establish a fresh lineage without the poisoned anchor. Delta-only, account-owned inputs and ambiguous operation checkpoints retain their stricter continuity rules; restarting an arbitrary thread on another account or duplicating an active journal claim is not authorized by silence alone. The real-origin scenario uses two distinct silent logical turns and then retries the last full body after the poison boundary; dedicated journal/fence controls supplement it.

Payload-budget fallback uses API-key-scoped durable count/fingerprint evidence and agreement with the resolved owner before releasing turn-state affinity. A real HTTP 429 from that owner can then settle its attempt and move to another eligible account. Another API key, a wrong prefix, missing output, an explicit anchor, account-owned state or conflicting owner evidence cannot use that grant. Tests use actual SQLite reservations and zero remaining account pressure.

An image/tool request sent through the operator HTTP bypass still passes through the final Responses-Lite payload preparation. Serial tool calls, all_turns reasoning context, image bytes, tool definitions and the derived Lite HTTP header are checked at the local HTTP origin. Normal non-Lite and bridge JSON controls are covered separately.

The unsafe full-resend unit fixture must replace both durable lookup and owner-retirement boundaries: a partial mock otherwise opens a real repository without its schema. The retirement double returns false and checks the expected owner, preserving the original refusal assertions. Real-DB integration tests continue to cover runtime ownership.

This evidence uses local WebSocket/HTTP origins and shortened test-only time budgets. It establishes route, payload, settlement and cleanup contracts; vendor overload percentages, real client behavior, published packages, cloud CI and production remain separate scopes. See the [verified change](../../changes/archive/2026-10-04-repair-bridge-terminal-lineage-failover/verification.md).
# Inline-image reuse and unary control media types

The image-bypass requirement includes the implemented bounded PNG/JPEG
exception from `allow-bounded-inline-images-on-bridge`. The previous blanket
wording could imply a raw fallback for every image even while default admission
retained the thread's bridge connection. The exception preserves image bytes,
history and prompt-cache identity; the existing bounded pre-created retry policy
and original budget still apply to an unacknowledged create. An invalid-image terminal settles admission and
allows a later text request on the same account. The existing explicit false
rollback and HTTP/failure fallback policies remain available.

For example, text → a valid inline PNG → text with the PNG in history can use
one local upstream socket. With the two-second test request budget, a silent
image create is sent once and leaves no reserved usage row. The existing
long-budget regression permits the initial attempt plus one pre-created retry,
then terminates; this batch preserves that policy. Real local sockets prove
these transport and settlement properties; they do not prove vendor image
validation, cache hit percentages or the historical #903 provider incident.

Unary control requests retain a single media type for nonempty JSON or SDP.
An empty POST is normalized to no body before transport dispatch, because
removing its header alone can let an HTTP library generate a replacement media
type for empty bytes. For example, a zero-byte standalone-search POST has no
upstream `Content-Type`, while a nonempty `application/sdp` payload retains that
value and its bytes. See the owning [spec](spec.md) for normative requirements.


# Bridge retry verification and cancellation ownership

This local batch processes exactly UP-ISSUE-2273, UP-ISSUE-2272 and UP-ISSUE-2271. The first two already have source implementations. Their verification now includes loopback upstream frames, public HTTP aliases, real durable SQLite rows, interpreted frames and negative eligibility cases.

For example, a terminal containing only `incomplete_details.reason = stream_incomplete` contributes one eligible strike. A distinct dispatched request contributes a second and opens the durable cooldown. Replaying the stored terminal adds no send or strike. Proof-gated full-history replay remains an existing permitted recovery route; the circuit is not a blanket ban on all traffic. Native stored-operation replay retains its existing downstream lifecycle and is not certified as a universal terminal-payload replay contract by this batch.

A persisted cooldown whose deadline has elapsed does not create a phantom local transition. A local cooldown already observed before expiry keeps its actual transition and permits one local half-open probe. Repeated durable loads leave that active lease owned by its request.

Submission previously awaited a claim directly, so caller cancellation after commit could discard the receipt. It now owns a scheduler task bounded across key-lock acquisition and the DB call, defers cancellation, attaches the receipt and attempts undispatched fenced release. Cleanup itself is cancellation-deferred. A new row's inserted epoch is retained, and the repository reads the receipt inside its write transaction before commit so a successor cannot substitute its own receipt.

Durable release does not clear process-local probes. The existing submission finalizer already returns the exact local lease token it owns. Repeating that operation in the durable helper without the local token erased replacement state even after a failed durable CAS.

The local implementation uses existing settings, schema and timeout. Crash abandonment/reclamation, uncertain DB timeout outcomes, generation rollback ABA and ordinary-success/newer-claim settlement policy remain open parts of UP-ISSUE-2271. No PostgreSQL/MySQL migration/runtime, live provider, cloud checks, release or production evidence is claimed.


## Scheduled cleanup and downstream delivery verification (2026-10-04)

See the normative requirements in [spec.md](spec.md) and the [verification report](../../changes/archive/2026-10-04-verify-bridge-cleanup-quarantine-backpressure/verification.md).

This change independently handles exactly UP-ISSUE-2270, UP-ISSUE-2268 and UP-ISSUE-2266 from issues-check.md. Their upstream bodies were refreshed on 2026-10-04; original author claims in ISSUES.md are historical and are not test evidence.

Scheduled cleanup now compares timestamp, generation and count. For example, an old row at epoch 1 with count 2 that receives a lagging-clock strike becomes count 3 at the same epoch; the old DELETE must miss and that candidate must wait for the next scheduled pass. Keyset pagination uses constant cursor storage and does not retry changed candidates within that pass. Tests reach the actual leader cleanup method and the real SQLite/PostgreSQL/MySQL rows; the precise interleaving is injected before DELETE on the cleanup connection.

Quarantine already retains worker-wide monotonic numbering and session ownership. Tests inject an initial strike or replacement session during completion's actual awaited circuit settlement. A pruned entry is recreated with a new generation, and a late completion leaves it intact. This change does not redesign the existing overflow policy: the registry cap can retain active poison entries above its nominal cap, while weaker entries remain evictable. That policy is separate from the verified stale-clear ownership contract.

Live output still uses the existing per-stream 32 MiB/4096-event queue, including its lone oversized event exception. A pending producer holds at most the current event for this shared-reader path. Saturation now has an independent five-second delivery bound; it does not affect model idle gaps while there is room. Resumption before expiry preserves all six test deltas in order. On expiry, already accepted output is drained before one synthetic failure. End-of-stream signalling occupies no additional payload/event slot, so a saturated accepted completion is not turned into a failure by its sentinel.

Cancellation and write errors explicitly close the ASGI body iterator and the nested bridge generator. Python 3.13 Queue.shutdown releases detached payloads and wakes producers with QueueShutDown; cancellation of the producer itself still propagates, and its waiter is removed. Repeated cancellation of response cleanup is deferred through the existing scheduler helper. Reservations settle through their existing owners; delivery failure does not add an account-health penalty.

This is a per-stream HTTP bridge contract, not a fixed process-wide RSS ceiling. Native helper buffers, total replay spool memory, real provider/client traffic, cloud gates and public artifacts are separate scopes. No settings, database columns, release or production changes are introduced.


## Independent transcript backlog verification (2026-10-04)

Eligible nonterminal events drain in bounded fair passes; the loop yields before each next pass. For example, 320 events with batch size 32 require ten writes without nine interval waits. Other operations each get a batch opportunity; a failed optional spool does not stall their backlog. Closing operations, queue limits and shutdown retain their existing behavior. Deterministic tests count wait cycles and verify order and failure isolation. Real SQLite checks verify 320 events followed by one completed terminal in rows_v1 and chunks_v2 and reject a stale owner epoch. Fake-writer timings isolate scheduling and do not establish production speedup. See [verification](../../changes/archive/2026-10-04-verify-sqlite-history-reports-transcript/verification.md).

## Local bridge refusal and successor verification (2026-10-04)

See [spec.md](spec.md) and the [verification report](../../changes/archive/2026-10-04-repair-bridge-refusal-transition-terminal/verification.md). This batch concerns exactly UP-ISSUE-2389, UP-ISSUE-2388 and UP-ISSUE-2033. The per-producer verdicts live in the archived refusal-audit.md.

Model-transition recovery already preserves the downstream token for reversible alias registration while clearing parent identity from submission. A real balancer conflict between required owner A and a sticky owner B creates one child. The next request with the same token resolves to B even when its history includes reasoning output. Existing protected recovery aliases, rollback, cancellation and second-conflict fences remain in place. No further model-transition runtime rewrite was needed.

Local provenance is independent of error code and replay permission. For example, an anchored stale-generation refusal retains HTTP 503, upstream_request_timeout and its retry hint; it now reaches the native client as a structured refusal, or one terminal plus DONE after commitment. This does not grant raw-HTTP replay. Mixed reconnect, prewarm and post-dispatch producers retain their transport classification. New submit fences require proof that the request has not previously attempted a send or observed response events or a replay.

Post-terminal exception containment already existed. A real-settlement probe found an unanchored keyed failure could start health persistence while its reservation was still reserved. The shared settlement helper now waits whenever account-error health is pending, so the health callback observes committed settlement. Ordinary health failure is logged without another terminal. Successful requests keep their existing asynchronous settlement path.

No configuration, schema or deployment is added. The evidence is scoped to ASGI routes, loopback upstreams, real SQLite settlement and injected metadata/CAS/lease failure conditions. Actual clients/providers, PostgreSQL/MySQL runtime, distributed races, cloud gates, public artifacts and production are separate scopes.
# Post-output abrupt bridge drops (2026-10-04)

The superseded `Abrupt eventless upstream websocket drops remain account-neutral` requirement was removed because it contradicted its later replacement. The active `Abrupt upstream websocket drops remain account-neutral` requirement separates account-health attribution from replay safety. A frame-less ending after text or a buffered reasoning prelude still returns one `stream_incomplete` without replay or per-drop health writes, and does not enter the eventless failure signal. Authored 1011 closes and protocol-invalid binary frames retain their penalty.

The real loopback WebSocket regression waits until the service has processed model output before dropping the transport, so it exercises post-output behavior rather than racing unread bytes. Source/Windows evidence is local; hosted-provider, native macOS and production coverage require their own execution evidence.

## Developer input and chained history

Responses history inherited through previous_response_id contains input; top-level instructions are turn-specific. Developer messages therefore stay in input, preserving content and order. A first turn containing developer reference data key-17=34620 followed by a previous_response_id lookup keeps that reference in upstream-owned history. Supplying empty instructions when absent preserves validation without moving the message. System messages still normalize into instructions, and JSON-object mode keeps its required instruction in input with an accepted role. Lite bundles and typed directives retain their existing rules. Compact serialization retains developer content too.

The local regression server models input inheritance and forgets instructions; it exercises actual HTTP forwarding and the downstream WebSocket route with a controlled upstream adapter. It does not establish hosted-provider persistence or reconnect replay guarantees, which have separate ownership contracts. See [the input requirement](spec.md#requirement-non-message-system-and-developer-input-items-are-preserved). Pressure units and the zero-score fallback are described in [account-routing context](../account-routing/context.md#lease-pressure-units-and-fallback-evidence).

## Empty prewarm and same-owner agent reconnect evidence

The [prewarm requirement](spec.md#requirement-empty-websocket-prewarm-context-survives-replay-classification) keeps empty `generate=false` context separate from generated-turn progress. For example, a prewarm can contain tools and developer rules, while its first user turn contains only two new messages. Those two messages cannot justify deleting the prewarm anchor. A fingerprint-matching full prefix can pass classification; changed rules cannot. Replayed prewarms retain the response identifier already shown to the client.

The [agent follow-up requirement](spec.md#requirement-durable-same-owner-replay-preserves-agent-follow-ups) validates opaque subagent input only within a durable same-owner proof. A retained assistant answer, or the exact persisted tool-call/output manifest, proves the boundary before the new agent message. Only trailing valid messages are omitted from the proof view; dispatch preserves all original identifiers, reasoning, ciphertext and order. Unknown shapes, omitted parallel calls and missing outputs do not prove context. Fresh and quarantined requests remain pinned even when the anchor is removed; account-neutral recovery still rejects agent messages.

Public HTTP and WebSocket regressions use controlled upstream adapters and real local persistence where applicable. They cover pre-visible recovery, refusal after visible output, operation fences and unavailable owners. They do not establish hosted-provider persistence or live Desktop behavior.

## Terminal append ownership and CCodex identities

[Bounded terminal delivery](spec.md#requirement-terminal-append-remains-owned-after-bounded-delivery-wait) stops waiting at its bound while the batcher continues to own the database append. Cancelling a SQLite statement can leave a deferred-close handle holding the writer slot. Fallback settlement preserves the terminal outcome; the settlement-phase and attempt fences prevent late persistence from authorizing replay or clearing a replacement attempt. For example, a blocked terminal write can finish after delivery while a second connection subsequently acquires BEGIN IMMEDIATE. Shutdown retains its existing task cleanup policy.

The [CCodex identity contract](spec.md#requirement-ccodex-gateway-identities-preserve-native-fingerprints) recognizes the two stock-app-server gateway identities through the existing shared classifier. A request with `User-Agent: ccodex-internal/0.159.3` retains its supplied client version on HTTP and WebSocket. Unknown lookalikes and continuity headers alone remain non-native. This is source compatibility, not a stable release or hosted-provider validation claim.

## Opaque extension nesting guard

Extra request fields (including nested request controls) use the same iterative 200-container guard as passthrough input/tools. This avoids a serialization failure after a deep extension was accepted; for example, a 300-level `extension` receives HTTP 400 naming that field. Values within the limit retain their original JSON objects during validation. Current locked dependencies also pass the historical accepted-boundary selection; that alone did not prove extensions safe. Regression and local-only verification: [five-contract evidence](../../changes/archive/2026-10-07-verify-five-depth-and-quota-contracts/verification.md).

## Quota failure metadata and request-error messages

The [reset metadata contract](spec.md#requirement-invalid-upstream-reset-metadata-does-not-interrupt-quota-failures) keeps malformed upstream metadata from breaking terminal rendering or leaking non-finite JSON. Each field is filtered independently. For example, `resets_at: NaN` with `resets_in_seconds: 432000` retains the relative reset for account health and omits the invalid absolute value. The account-health consumer still owns horizon validation; finite values and existing numeric-string parser compatibility are preserved. A synthetic terminal adds no relative reset, while a propagated failure can retain one supplied upstream.

The [usage-limit classification contract](spec.md#requirement-usage-limit-messages-classify-as-account-rate-limits) lets code-less frames provide account exhaustion evidence. An `invalid_request_error` can quote the user's request, so a usage-limit phrase there cannot bench an otherwise healthy account. The negative product-path control preserves that request error and keeps both candidate accounts active. Local synthetic routes and persistence establish this behavior; real upstream incidents, cloud CI, and production require separate evidence.

## Owned terminal during post-submit cooldown

The [owned terminal requirement](spec.md#requirement-post-submit-cooldown-preserves-an-owned-upstream-terminal) protects the interval between reader settlement ownership and downstream publication. A reason-only `response.incomplete` can open the durable circuit while its queue remains empty and no response-created event has been counted. That is an already-admitted terminal, so replacing it with an admission 503 loses the upstream result. The claimed settlement phase covers the early interval; the upstream-terminal timestamp covers later settlement completion. New requests without that terminal evidence retain the existing cooldown refusal and detach cleanup.

For example, the second incomplete can durably raise the failure count to two, pause before publication, then reach the post-submit circuit read. It must still reach the original client; duplicate receipt replay does not dispatch again and reservations settle. Admission and existing verified stale-anchor recovery rules for later requests remain unchanged. Deterministic real-route tests synchronize this interval on canonical and equivalent endpoints; they establish local synthetic behavior and do not certify live upstream incidents.
