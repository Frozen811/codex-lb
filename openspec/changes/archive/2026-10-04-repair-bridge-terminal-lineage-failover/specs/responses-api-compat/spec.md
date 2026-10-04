## ADDED Requirements

### Requirement: Bridge continuation boundaries preserve actionable outcomes

HTTP Responses ingress MUST preserve exactly one actionable outcome for a rejected proxy-injected continuation anchor: a structured HTTP refusal before commitment or a terminal SSE failure after commitment, including after a keepalive. A subsequent eligible full-history retry MUST NOT re-inject an anchor whose denial has been conclusively retired. Full-history payload-budget fallback MUST permit pre-output quota failover only when API-key-scoped durable metadata verifies the retained transcript prefix and the resolved owner agrees. Incomplete transcripts, explicit anchors, files, account-owned state, forwarded requests and owner conflicts MUST NOT gain cross-account replay permission from the size bypass.

#### Scenario: Local refusal precedes commitment
- **WHEN** a native HTTP Responses request reaches a local denied-anchor fence before the SSE body is committed
- **THEN** the client receives the structured HTTP 502 continuity refusal and owned request resources are finalized

#### Scenario: Upstream rejects a proxy anchor after commitment
- **WHEN** a native HTTP Responses stream receives a keepalive and upstream subsequently rejects a proxy-injected anchor without a safe fresh replay
- **THEN** the client receives exactly one actionable terminal SSE failure and owned request resources are finalized
- **AND** a following eligible full-history request does not receive a conclusively retired denied anchor again

#### Scenario: Verified payload fallback recovers from quota
- **WHEN** an over-budget unanchored full transcript matches API-key-scoped durable evidence and its owner returns a pre-output quota rejection
- **THEN** another eligible account can serve the request with no stale turn-state affinity
- **AND** an incomplete transcript, conflicting owner, explicit anchor, file or forwarded request cannot use this permission

#### Scenario: Durable proof stays inside its key and owner scope
- **WHEN** a payload-budget fallback presents a turn-state alias from another API key or durable proof whose owner disagrees with the resolved continuity owner
- **THEN** the fallback does not grant account-neutral quota failover

#### Scenario: Silent sticky lineage admits a fresh safe retry
- **WHEN** consecutive eventless attempts exhaust the bounded retry policy and a subsequent eligible logical turn supplies verified portable full history
- **THEN** recovery can send a fresh upstream lineage without the poisoned anchor
- **AND** delta-only retries retain their continuity protection
- **AND** an identical request whose operation journal remains ambiguous does not gain duplicate-dispatch permission

#### Scenario: Image tools use a compatible Lite payload
- **WHEN** an image and tool request reaches the Responses-Lite upstream through bridge bypass
- **THEN** the final upstream payload uses serial tool calls while preserving the image and permitted tool definitions
