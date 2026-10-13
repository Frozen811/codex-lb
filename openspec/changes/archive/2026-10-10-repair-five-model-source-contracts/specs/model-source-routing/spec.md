## ADDED Requirements

### Requirement: Automatic source discovery is durable and bounded

Sources SHALL default to manual catalog mode. An operator SHALL be able to opt a Responses-capable source into `cli_proxy_api` mode using the existing dashboard API. The proxy MUST automatically fetch the source's inference-authenticated `/models` Codex catalog with a client version even when no subscription accounts exist. Refresh MUST use no more than four concurrent workers and a shared five-second budget, reject redirects and bodies exceeding 1 MiB, and accept only complete typed snapshots with at most 1000 unique bounded model identities. Missing or malformed snapshots MUST preserve all last-good durable rows. Catalog metadata MUST remain a provider claim and MUST NOT include secrets.

Successful refresh MUST update model metadata, retain omitted identities as unavailable, restore returning identities, and preserve independently disabled models. Native subscription identities MUST retain registry precedence. Unavailable source requests MUST return `503 model_source_unavailable` before native admission. Recorded native continuation owners MUST remain authoritative when an overlapping source becomes disabled or unavailable. Operator changes and newer refresh claims MUST fence stale results. Each worker MUST own its database sessions and cancellation MUST reclaim all spawned workers and HTTP leases.

#### Scenario: Opt-in discovery works without subscription accounts
- **WHEN** an enabled Responses source selects cli_proxy_api mode and the scheduled refresh receives a valid catalog
- **THEN** the discovered metadata appears in public and Codex catalogs and Responses dispatch reaches that source

#### Scenario: Invalid or unreachable discovery retains the last catalog
- **WHEN** catalog refresh is unreachable, redirects, exceeds bounds or contains any malformed or duplicate model
- **THEN** durable last-good models and their availability remain unchanged

#### Scenario: Omission and restoration preserve identity and manual pauses
- **WHEN** a valid catalog omits a previously discovered model and later restores it
- **THEN** the same stored identity becomes unavailable then available without changing its operator enablement
- **AND** an omitted source identity returns model_source_unavailable without native fallback

#### Scenario: Configuration edits fence an in-flight refresh
- **WHEN** an operator edits or deletes the source or a newer worker claims refresh before an older result is applied
- **THEN** the older result cannot overwrite models or re-enable that source

#### Scenario: Native precedence and continuation ownership survive source outage
- **WHEN** a native model collides with a source or a recorded native owner continues after the source is disabled or unavailable
- **THEN** existing subscription precedence and owner routing remain authoritative

#### Scenario: Refresh cancellation owns worker cleanup
- **WHEN** refresh is cancelled while multiple sources are fetching
- **THEN** all workers and HTTP leases are reclaimed and incomplete snapshots are not published
