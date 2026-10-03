## ADDED Requirements

### Requirement: Image fan-out preserves completed usage through partial failures

For non-streaming image generations and edits with `n > 1`, the service MUST transfer the single public API-key reservation exactly once using the sum of captured image-tool usage from successful subcalls, even when another subcall fails or the caller cancels. If no subcall succeeds, the reservation MUST be released exactly once. Internal subcalls MUST NOT own that public reservation. Caller cancellation MUST cancel and drain all outstanding subcalls before propagating, including repeated cancellation during cleanup. Request-log rewriting failures MUST NOT prevent completed usage settlement. Unexpected subcall exceptions MUST produce a generic OpenAI error without exposing exception text.

#### Scenario: Partial upstream failure
- **WHEN** one image subcall succeeds and another fails
- **THEN** the public response surfaces the first subcall error and the successful image-tool usage is settled exactly once

#### Scenario: Cancellation after a successful subcall
- **WHEN** the caller cancels after one subcall succeeds while another is pending
- **THEN** the pending subcall is cancelled and drained, successful usage is settled, and caller cancellation propagates

#### Scenario: Cancellation before any success
- **WHEN** all image subcalls are pending when the caller cancels
- **THEN** all subcalls are cancelled and drained and the reservation is released exactly once

#### Scenario: Request-log failure after generation
- **WHEN** successful subcalls have captured image-tool usage and request-log rewriting fails
- **THEN** the successful usage has already transferred to its sole settlement owner

#### Scenario: Unexpected subcall exception
- **WHEN** an image subcall raises an unexpected exception
- **THEN** the error response contains a generic internal error and omits the exception text
