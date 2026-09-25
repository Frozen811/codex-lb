# sticky-session-operations Specification Delta

## ADDED Requirements

### Requirement: Subagent prompt-cache affinity TTL

The system SHALL bound prompt-cache and thread-scoped sticky session TTL for short-lived child subagents. When a request carries subagent lineage indicators (such as `x-parent-session-id`, `x-openai-subagent`, or `x-codex-parent-thread-id`), the effective prompt-cache affinity TTL MUST NOT exceed 300 seconds (`SUBAGENT_PROMPT_CACHE_MAX_AGE_SECONDS`), bounding the lease and session lifetime to avoid exhausting stream leases for short-lived subagent tasks.

#### Scenario: Subagent request receives bounded 300s prompt cache TTL
- **WHEN** a request arrives with an `x-parent-session-id`, `x-openai-subagent`, or `x-codex-parent-thread-id` header
- **AND** prompt-cache or thread affinity is enabled with a default TTL greater than 300 seconds (e.g. 3600s)
- **THEN** the resolved affinity policy uses a maximum age of 300 seconds

#### Scenario: Non-subagent request receives full configured prompt cache TTL
- **WHEN** a request arrives without subagent headers
- **THEN** the resolved affinity policy uses the configured `openai_cache_affinity_max_age_seconds`
