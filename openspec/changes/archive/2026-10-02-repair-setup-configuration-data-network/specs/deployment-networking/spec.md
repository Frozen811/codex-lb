## ADDED Requirements

### Requirement: Setup endpoints distinguish listeners from reachable addresses

Remote deployment guidance MUST distinguish bind hosts from client destinations, host loopback from container loopback, bridge service DNS from host-published DB ports, and the HTTP listener on 2455 from the separate temporary OAuth callback listener on 1455. It MUST explain Docker Desktop host access, Linux host-gateway prerequisites, WSL addressing limits, port collisions and separate inbound readiness versus outbound DNS/TLS checks.

#### Scenario: Application container connects to a host or sibling database

- **WHEN** an operator configures a database outside the application container
- **THEN** the guide selects a shared-network service name or an explicitly reachable host endpoint
- **AND** does not direct that connection to the application's own loopback address

#### Scenario: Client on another machine

- **WHEN** a client accesses a LAN or remote deployment
- **THEN** its URL uses the server address and published HTTP port
- **AND** the instructions do not use `0.0.0.0` as a client destination or assume that publishing 1455 starts an OAuth listener
