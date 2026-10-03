## ADDED Requirements

### Requirement: Internal drain controls require captured local caller provenance

Internal drain start, stop and status routes MUST require a captured loopback socket peer and a locally resolved caller. A projected loopback address alone MUST NOT authorize those routes. Remote users forwarded through a loopback proxy and requests without captured socket provenance MUST receive HTTP 403 without changing or revealing drain state. Direct local preStop/operator calls MUST retain existing deadline, reversible drain and committed-shutdown behavior.

#### Scenario: Untrusted socket projects loopback

- **WHEN** a remote socket supplies loopback forwarding headers accepted by the projection layer
- **THEN** internal drain controls return HTTP 403
- **AND** shutdown admission/deadline state does not change

#### Scenario: Remote user traverses a loopback proxy

- **WHEN** the socket proxy is loopback but its forwarded caller is remote or identity hints conflict
- **THEN** internal drain controls refuse access

#### Scenario: Direct local lifecycle control

- **WHEN** a captured local caller invokes drain start/stop/status directly
- **THEN** existing local control and monotonic deadline semantics remain available
