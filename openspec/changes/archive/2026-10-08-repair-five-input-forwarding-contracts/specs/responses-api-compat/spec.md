## ADDED Requirements

### Requirement: Completed client tool-search pairs survive fresh replay

After a verified replay prefix, the proxy MUST retain completed client-owned tool_search_call/tool_search_output pairs and their loaded tool definitions. Fresh replay MUST remove their response-owned item IDs while preserving exact call IDs. Loaded declarations MUST be account-neutral function/custom tools, optionally inside one namespace; defer_loading MUST be boolean when present, including rejection of explicit null. Missing or malformed tools, failed/server execution, hosted/MCP declarations, unknown fields and nested namespaces MUST fail closed. JSON-schema property names MUST NOT be treated as live account references. Existing top-level declared-tool allowlists MUST remain unchanged. Durable transcript overlap MUST identify search calls by call ID and canonical query arguments and outputs by call ID and declared tool type/name identities, recursively through one loaded namespace; recording IDs and dictionary key order MUST NOT prevent recognition of a restated pair.

#### Scenario: Completed loaded tools reach a replacement account
- **WHEN** a verified HTTP or WebSocket full resend contains a completed client search pair and safe loaded declarations
- **THEN** the replacement request retains both items and their declarations without response-owned IDs

#### Scenario: Unsafe search output remains owner-bound
- **WHEN** a search output contains server execution, failed status, hosted tools, malformed declarations or nested namespaces
- **THEN** the proxy rejects account-neutral replay and does not dispatch to another account

#### Scenario: Restated tool-search history is not dispatched twice
- **WHEN** a client restates a durable search pair with reordered argument keys and without owner-assigned item IDs
- **THEN** relocation recognizes the same pair and forwards each retained call/output exactly once with its loaded declarations

### Requirement: Async tool identities survive anchored intervening turns

Both Responses transports MUST track function/custom calls marked with boolean async=true independently from synchronous pending calls. Anchored intervening turns MUST synthesize interrupted outputs only for synchronous calls. Later outputs MUST complete only matching exact nonblank call IDs with the matching call type. Account rebind, denied-anchor retirement and mismatched durable rehydration MUST clear async state. Replay MUST validate known fields, markers, ownership and complete settled async evidence before excluding asynchronous calls from synchronous manifest comparison. A persisted synchronous pending call MUST NOT become asynchronous through client mutation. Durable transcript overlap MUST distinguish synchronous and asynchronous call identities while treating an absent marker and boolean false as the same synchronous mode.

#### Scenario: Mixed pending calls receive only one interrupted output
- **WHEN** an anchored response emits one async function/custom call and one synchronous call and the next turn omits their outputs
- **THEN** only the synchronous call receives an interrupted output and the async identity remains available for its delayed typed output

#### Scenario: Invalid async evidence prevents alternate dispatch
- **WHEN** a replay has a nonboolean marker, missing/blank call ID, wrong output type, unsafe settled prefix or async marker conflicting with the durable synchronous manifest
- **THEN** account-neutral recovery fails closed

#### Scenario: Owner retirement clears outstanding async work
- **WHEN** continuity retires its anchor or changes owning account or durable anchor
- **THEN** prior async calls cannot suppress interrupted completion on the new owner

#### Scenario: A changed async marker does not erase durable evidence
- **WHEN** a restated call changes its marker between synchronous and asynchronous modes
- **THEN** transcript overlap does not treat the altered call as identical evidence

## MODIFIED Requirements

### Requirement: Verified full resend can recover from selection-time owner loss

An HTTP bridge request MAY move from an unavailable continuity owner to another account only after a typed pre-visible `continuity_owner_unavailable` account-selection result, which the HTTP bridge maps to `previous_response_owner_unavailable`, and positive durable proof that the request contains the complete retained input history. A missing durable owner is not a selector result and MUST fail closed without replay. The durable row MUST provide a positive input-item count and full fingerprint, and the corresponding raw prefix of the incoming list-shaped input MUST match both before any projection occurs.

After the raw prefix proof, the service MUST construct a deterministic plaintext projection by omitting `reasoning` and completed `web_search_call` items while retaining validated completed client-owned `tool_search_call` / `tool_search_output` pairs and removing upstream `id` fields from every retained input item. Retained `internal_chat_message_metadata_passthrough` MUST contain only a nonblank string `turn_id` when present. The projected suffix after the projected prefix MUST contain a completed assistant `output_text` or `refusal` boundary with nonblank content followed by nonblank fresh text, valid fresh file/image input, or a matching typed delayed async tool output. The suffix MAY contain multiple intervening turns only when every non-final user-input sequence is followed by another completed assistant boundary and the final sequence ends in fresh input. Direct synchronous intrinsic calls MAY precede an assistant boundary only when terminal completed or failed outputs settle every represented synchronous call in order. Validated function/custom calls with boolean `async: true` MAY remain unresolved across completed assistant boundaries; their matching typed delayed outputs MUST retain exact nonblank IDs and all call/output validation evidence. A call at the end of the verified raw prefix MAY be settled by its matching output at the start of the suffix. A direct-call/output sequence alone MUST NOT prove completeness because the persisted metadata does not identify omitted parallel calls. A matching prefix followed only by new user input, empty content, tool-call-only output, in-progress or partial retained output, duplicate or unmatched calls, unresolved synchronous calls, malformed async evidence, or misordered synchronous call output MUST fail closed.

The service MUST validate the complete projected request after removing `previous_response_id`; it MUST reject nonblank conversation or prompt handles, remaining encrypted content, compaction, opaque account-scoped file/container/vector handles, nonportable file schemes, hosted, MCP, program-mediated, or unknown call or tool-choice state, unknown top-level fields, unknown or malformed top-level reasoning configuration, malformed message/content shapes, and tool outputs without exactly one matching intrinsic call. Assistant messages MUST contain only supported output parts, while user, system, and developer messages MUST contain only supported input parts. Inline data images and HTTP(S) file/image content MAY remain eligible. Eligible declared tools, tool choices, and retained direct calls MUST be shape-validated, account-neutral, and self-contained. Web-search filters, context size, and approximate location MUST use only the recognized nested fields and value types. An apply-patch call MUST use exactly one representation: a recognized structured `operation` with its exact discriminated fields, a nonblank legacy `patch`, or a nonblank legacy `input`.

For an eligible replay, the service MUST remove `previous_response_id`, strip every downstream session/turn alias, clear hard affinity, exclude the unavailable owner, prevent initial bridge-owner forwarding, and submit the complete projected request through a fresh server-namespaced recovery lane. It MUST NOT replay after downstream-visible output. Selection policy conflicts, authentication/connection failures after selection, incomplete history, or any unsafe request state MUST remain fail-closed. A planning-stage rejection for an unsafe or unprovable bridge continuation MUST preserve its existing 404 `bridge_previous_response_not_found` envelope; a typed selector-time owner-unavailable rejection MUST retain its 502 `previous_response_owner_unavailable` envelope. Neither rejection SHALL permit dispatch to a replacement account without positive replay proof.

#### Scenario: Client-supplied full resend moves from A to B

- **GIVEN** account A owns a completed previous response and its durable row stores the completed input count and fingerprint
- **AND** a follow-up supplies that previous response plus an account-neutral full resend whose retained prefix matches both values
- **WHEN** required-owner selection returns typed `continuity_owner_unavailable` before output
- **THEN** the bridge removes the previous-response anchor and all stale affinity headers
- **AND** excludes account A and submits the complete fresh request once on account B
- **AND** the next turn for the recovered task remains on account B

#### Scenario: Proxy-injected anchor protects an equivalent full resend

- **GIVEN** a hard durable alias resolves a completed response and the incoming full resend matches its retained count and fingerprint
- **AND** the proxy injects that response as the reattach anchor
- **WHEN** required-owner selection returns typed `continuity_owner_unavailable` before output
- **THEN** the same fresh-replay rules apply after the injected anchor is removed

#### Scenario: Verified resend contains owner-bound reasoning

- **GIVEN** a verified full resend contains encrypted reasoning, server-assigned item IDs, and completed web or tool-search bookkeeping
- **AND** its retained assistant and direct-tool content is otherwise complete and portable
- **WHEN** required-owner selection returns typed `continuity_owner_unavailable` before output
- **THEN** the bridge omits reasoning and completed web-search bookkeeping, retains validated client tool-search pairs and loaded definitions, and strips upstream item identities
- **AND** no encrypted content or upstream item identity is sent to account B
- **AND** the validated plaintext projection is submitted once on account B

#### Scenario: Retained request contains account-scoped state

- **GIVEN** a full resend contains a conversation or prompt handle, compaction, encrypted content outside an omitted reasoning item, an opaque account-scoped file/container/vector handle, a nonportable file scheme, hosted or MCP call or tool-choice state, an unknown call type, or an unmatched tool output
- **WHEN** its required owner is unavailable
- **THEN** the request fails closed with the rejection envelope of the stage that refused replay
- **AND** none of that state is sent to another account

#### Scenario: Request shape is not completely understood

- **GIVEN** a purported full resend contains an unknown top-level field or malformed/unknown message content
- **WHEN** its required owner is unavailable
- **THEN** replay eligibility fails closed
- **AND** the service does not infer portability from the retained fingerprint alone

#### Scenario: Matching input prefix omits the prior response output

- **GIVEN** the incoming input prefix matches the durable count and fingerprint
- **AND** the suffix contains only a new user message, a direct-call/output sequence without a later completed assistant boundary, partial retained output, or unresolved direct calls
- **WHEN** the required owner is unavailable
- **THEN** replay eligibility fails closed with the rejection envelope of the stage that refused replay
- **AND** the proxy does not drop the previous-response anchor or send the incomplete transcript to another account

#### Scenario: Owner was selected before a later failure

- **GIVEN** the required owner was selected successfully
- **WHEN** refresh, authentication, WebSocket connection, transport, or timeout fails before output
- **THEN** the request keeps that ordinary failure classification
- **AND** the service does not activate cross-account full-resend recovery

#### Scenario: Durable continuity row has no account owner

- **GIVEN** a durable continuity row proves retained input but has no account owner
- **WHEN** the request is evaluated before account selection
- **THEN** the bridge returns `previous_response_owner_unavailable`
- **AND** it does not treat the missing owner as a typed selector miss or replay on another account

#### Scenario: Failure occurs after visible output

- **WHEN** any part of a response has become downstream-visible
- **THEN** the service does not replay the request on another account
- **AND** it terminates through the existing partial-output failure contract
