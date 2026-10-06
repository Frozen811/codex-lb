## ADDED Requirements

### Requirement: Docker OAuth callback publishing is opt-in

Default development and server-only Compose services and basic Docker bridge run examples MUST NOT publish host port 1455. Docker instructions MUST provide device-code and manual-callback login options and an explicit opt-in callback mapping bound only to host loopback. Opt-in publishing MUST preserve the ordinary HTTP port and MUST NOT claim to start a callback listener by publishing a port.

#### Scenario: Native client signs in alongside default Docker setup
- **WHEN** an operator selects default Compose or the basic Docker bridge command
- **THEN** the configuration does not reserve host port 1455
- **AND** the native client can acquire its own callback port independently

#### Scenario: Operator opts into direct browser callbacks
- **WHEN** the operator selects the documented callback override for either Compose setup
- **THEN** container port 1455 is published on host `127.0.0.1:1455` while port 2455 remains published
- **AND** the instructions explain the client port collision and temporary listener requirement
