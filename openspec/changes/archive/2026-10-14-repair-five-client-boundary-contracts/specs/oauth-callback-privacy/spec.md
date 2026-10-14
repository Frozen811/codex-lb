## ADDED Requirements

### Requirement: OAuth network failures are sanitized and terminal

Direct OAuth authorization-code exchange and device-code startup MUST translate client connection failures, payload transport failures and timeouts into a stable transport_error with a sanitized message that excludes URLs, codes, verifiers and network exception text. Device startup MUST return the existing structured dashboard 502 envelope. Browser callbacks MUST show the safe error page and persist an error state visible to polling, while honoring a concurrently committed success. Manual callbacks MUST return the existing structured error envelope. Caller cancellation MUST propagate and release owned transport resources.

#### Scenario: Browser exchange cannot connect

- **WHEN** the token request raises a client connection failure
- **THEN** the callback shows a sanitized failure and polling returns terminal error without a raw 500

#### Scenario: Device startup transport failure

- **WHEN** a device-code request fails at the transport boundary
- **THEN** startup returns dashboard 502 with transport_error and no exception details

#### Scenario: OAuth exchange is cancelled

- **WHEN** the caller cancels during the outbound exchange
- **THEN** cancellation propagates and the session context releases its owned resources
