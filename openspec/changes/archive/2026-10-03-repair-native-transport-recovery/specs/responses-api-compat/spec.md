## ADDED Requirements

### Requirement: Direct native stream failures release admission ownership

When a direct HTTP Responses request terminates without an upstream terminal event, the proxy MUST close its iterator chain and release account stream and response-create admission ownership before teardown completes. Its API-key reservation MUST settle or release through the existing terminal cleanup. Subsequent requests MUST be admitted under the configured account cap without requiring process restart. Stream and non-stream request modes MUST preserve their existing external error contracts.

#### Scenario: Repeated missing-terminal failures do not wedge the account cap

- **WHEN** direct native HTTP requests repeatedly end without a terminal event at account stream limit one
- **THEN** each failed request releases its admission ownership and API-key reservation
- **AND** a later successful request is admitted without restart

#### Scenario: Native body transport failure releases admission ownership

- **WHEN** a native direct HTTP stream fails during body consumption
- **THEN** the nested transport stream closes during request cleanup
- **AND** no stream or response-create admission ownership remains for that request
