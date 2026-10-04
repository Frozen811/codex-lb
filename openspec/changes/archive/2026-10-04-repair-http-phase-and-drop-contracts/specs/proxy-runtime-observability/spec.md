## ADDED Requirements

### Requirement: HTTP upstream phases use observed event provenance

HTTP Responses request logs and existing phase-latency metric observations MUST measure first upstream activity and `response.created` independently from the post-admission attempt start. Valid zero observations MUST be retained. A keepalive, comment-only block, or locally generated event MUST NOT populate an upstream phase. A real upstream event with a locally synthesized response ID MUST still count as upstream activity. Unobserved phases MUST remain null. Observation MUST preserve lazy forwarding and verbatim later output without adding a blocking persistence barrier or new metric labels.

#### Scenario: Admission is excluded and distinct upstream phases persist
- **WHEN** a request waits 500 ms for admission and then observes metadata at 250 ms, created at 500 ms and content at 1000 ms after attempt start
- **THEN** the persisted queue, first-event, created and first-token values are respectively 500, 250, 500 and 1000 ms
- **AND** existing phase metrics observe the same phases

#### Scenario: Local failure and keepalives do not manufacture observations
- **WHEN** the stream contains only keepalives and a local failure before any upstream event
- **THEN** the first-event and created phases remain null and their metric observations are absent

#### Scenario: Upstream failure with local response ID remains observable
- **WHEN** a real upstream error is normalized with a synthesized local response ID at attempt offset zero
- **THEN** the first-event phase is zero and the unobserved created phase remains null
