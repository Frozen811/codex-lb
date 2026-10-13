## ADDED Requirements

### Requirement: Operator account quota caps bound every selection fallback
An account with a configured usage cap SHALL be excluded when any observed standard quota reaches that cap, including during error-backoff fallback and upstream standard-quota exemption. A zero cap SHALL exclude the account even without usage observations. Clearing the cap SHALL restore normal selection semantics.

#### Scenario: Backoff cannot bypass an operator cap
- **WHEN** a capped account is in error backoff and its observed usage reaches the cap
- **THEN** the selector SHALL NOT choose it as a fallback.

#### Scenario: Upstream quota exemption retains the operator cap
- **WHEN** selection bypasses standard upstream quota eligibility
- **THEN** an account at its operator cap SHALL still be excluded.

#### Scenario: Zero cap and cleared cap
- **WHEN** the operator sets a zero cap then clears it
- **THEN** the account SHALL be excluded at zero and SHALL return to ordinary admission after clearing.
