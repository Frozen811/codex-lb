## ADDED Requirements

### Requirement: Completed Images results own trailing event precedence

For non-streaming generation and editing, including fan-out subcalls, the first captured `response.completed` MUST determine the returned image output and captured image-tool usage. The collector MUST drain the remainder of the stream for finalization while ignoring subsequent SSE events. Before a completion is captured, upstream `response.incomplete`, `response.failed`, and `error` MUST retain the existing OpenAI-compatible failure response.

#### Scenario: Incomplete event follows completed image

- **WHEN** a completed image with usage is followed by `response.incomplete`
- **THEN** the completed image and original usage are returned
- **AND** the remaining stream is drained before returning

#### Scenario: Incomplete event precedes completion

- **WHEN** an image stream emits `response.incomplete` before any completion
- **THEN** the existing image-generation failure is returned and the public reservation is released

## REMOVED Requirements

### Requirement: Internal host selection

**Reason**: This duplicate requires Luna, contradicting the existing image-compatible Sol/Astra/5.5 host selection requirement.
**Migration**: Use the existing Image generation is implemented as a Responses tool adapter requirement; public image model IDs and runtime host selection remain unchanged.
