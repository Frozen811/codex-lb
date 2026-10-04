## MODIFIED Requirements

### Requirement: Typed Windows transport failures recover without unsafe replay

The service MUST classify local DNS resolver failures, host-route failures, and typed Windows route failures 1231 and 1232 separately from account-specific upstream failures. Classification MUST come from typed exception provenance or an already-preserved stable internal code, not from arbitrary message text. Windows peer resets 64 and transport timeouts 121 MUST NOT establish process-wide network loss by themselves. A Windows route classification MUST NOT by itself prove that dispatch did not occur. Only typed pre-dispatch connection failures MAY be replayed automatically. When such a route failure affects the current shared outbound HTTP client, subsequent callers MUST use a replacement client while active leases remain valid. The selected account's health MUST remain unchanged for process-wide route failures.

#### Scenario: Ambiguous Windows route failure retires transport without replay

- **WHEN** an HTTP operation raises a typed OSError with winerror 1231 or 1232
- **AND** no connector provenance proves that dispatch did not begin
- **THEN** the failed shared generation is eligible for retirement
- **AND** the selected account's health remains unchanged
- **AND** the failed request is not automatically replayed

#### Scenario: Windows connector route failure can retry safely

- **WHEN** a typed connector failure contains an OSError with winerror 1231 or 1232
- **THEN** recovery MAY retry the request on the same account within its deadline

#### Scenario: Windows message text does not establish provenance

- **WHEN** an exception message contains a Windows route error number
- **AND** its typed winerror field is absent
- **THEN** it does not enter Windows route recovery

#### Scenario: Windows peer reset and timeout preserve endpoint attribution

- **WHEN** an exception contains winerror 64 or 121 without DNS or route-loss provenance
- **THEN** it does not enter process-network recovery
- **AND** it retains the existing endpoint/account failure handling

## ADDED Requirements

### Requirement: Native stream transport diagnostics survive settlement

When a native HTTP Responses request fails before response headers or during body consumption, the persisted request log MUST retain its typed failure phase, transport exception category and observed upstream HTTP status when present. Diagnostic metadata MUST NOT be added to client SSE payloads or establish new replay eligibility. Existing cancellation and explicit terminal-error classifications MUST retain precedence.

#### Scenario: Body failure preserves the observed response status

- **WHEN** the native helper receives HTTP 200 and then fails while reading the response body
- **THEN** the request log records the body-read failure phase, native transport exception category and observed HTTP 200
- **AND** the client receives its existing transport failure contract

#### Scenario: Ambiguous request failure has no invented HTTP status

- **WHEN** a native POST is dispatched but the connection fails before response headers
- **THEN** the request log records the request failure phase without inventing an upstream HTTP status
- **AND** that missing response head does not authorize replay

### Requirement: Native HTTP transport pools isolate accounts

Native direct Responses HTTP requests MUST partition persistent connection pools by the selected upstream account identity. Requests for the same account with compatible transport options MAY reuse connections. A connection failure in one account's pool MUST NOT terminate another account's active stream. A response-head or body-read failure alone MUST NOT authorize replay of an ambiguously dispatched request.

#### Scenario: One account connection fails while another is active

- **WHEN** two accounts stream concurrently to the same HTTP/2 origin through the native helper
- **AND** the origin aborts one account's connection
- **THEN** the other account's stream can complete on its own connection
- **AND** the failed account's ambiguously dispatched request is not replayed

#### Scenario: Compatible requests retain same-account connection reuse

- **WHEN** consecutive successful native HTTP requests use the same account and compatible transport options
- **THEN** their established connection can be reused
- **AND** another account uses a separate connection pool
