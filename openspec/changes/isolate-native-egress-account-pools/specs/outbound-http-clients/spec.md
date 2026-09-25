# outbound-http-clients Specification Delta: Isolate Native Egress Account Pools

## Requirements

### Requirement: Native egress isolates HTTP/2 connection pools by account pool key

The native egress client and helper MUST accept an optional `pool_key` on each HTTP request. When provided, the helper MUST key its internal HTTP/2 client connection pools using `pool_key` alongside proxy and timeout configuration, ensuring requests with distinct pool keys use separate connection pools and do not share underlying HTTP/2 TCP/TLS sockets.

#### Scenario: Distinct accounts use separate HTTP/2 connection pools
- **WHEN** requests for Account A and Account B are dispatched through the native egress client
- **AND** Account A and Account B have different `pool_key` values
- **THEN** the helper uses distinct client instances and separate HTTP/2 connections for Account A and Account B
- **AND** a transport drop or connection reset on Account A's socket does not terminate in-flight streams on Account B's socket.

#### Scenario: Requests without pool key preserve backward compatibility
- **WHEN** a request is dispatched without specifying `pool_key`
- **THEN** the helper defaults `pool_key` to `None` and services the request using the default shared pool key.
