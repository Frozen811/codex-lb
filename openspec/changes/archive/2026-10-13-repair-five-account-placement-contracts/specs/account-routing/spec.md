## ADDED Requirements

### Requirement: Fresh child placement uses lineage proof across transport stage hints

When the operator enables parent-account diversification, a child request participating in Codex thread affinity and proven account-neutral and fresh by its lineage and payload SHALL prefer an eligible account other than its known parent's account. A transport's `follow_up` hint caused solely by child thread headers MUST NOT suppress this placement preference. If no alternative is eligible, selection MUST retry with the original exclusions within the original deadline. Established child affinity, explicit required account ownership and API-key scope MUST remain authoritative. The feature MUST remain disabled by default.

#### Scenario: Fresh child thread with follow-up transport hint
- **WHEN** a fresh child has parent lineage, no child mapping or required owner, and the bridge labels it follow_up
- **THEN** enabled diversification selects another eligible account before considering the parent

#### Scenario: No eligible alternative
- **WHEN** all accounts other than the eligible parent are unavailable
- **THEN** advisory diversification allows selection of the parent within the same deadline

#### Scenario: Established child retains its account
- **WHEN** the child already has a compatible affinity mapping
- **THEN** parent diversification does not replace that mapping

### Requirement: Strict model routes preserve transport and ownership constraints

HTTP Responses, compact, native Responses WebSocket and HTTP bridge requests SHALL enforce configured strict model routes, including request-header overrides, before upstream dispatch. A strict target conflicting with a required stored-object, file or established socket owner MUST fail closed with `model_account_owner_conflict`; it MUST NOT move account-owned data to the configured target. An unavailable strict target MUST report `model_account_unavailable` without selecting another account. Retained bridge reuse MUST honor the same target and API-key scope.

#### Scenario: Request header selects an account across transports
- **WHEN** a request supplies a model routing header targeting an eligible account
- **THEN** its selected upstream account is the header target, overriding a different configured model route

#### Scenario: Strict model route conflicts with a required owner
- **WHEN** a mapped model targets an account different from the required request owner
- **THEN** the request fails with model_account_owner_conflict before upstream dispatch

#### Scenario: Unavailable target does not fall back
- **WHEN** a strict target is unavailable and another account is healthy
- **THEN** the request fails with model_account_unavailable and dispatches to neither account

#### Scenario: Retained bridge cannot bypass strict target
- **WHEN** a request with a strict route reaches a retained bridge belonging to another account
- **THEN** reuse cannot dispatch to that account; required continuity fails closed, while account-neutral fresh placement selects the strict target
