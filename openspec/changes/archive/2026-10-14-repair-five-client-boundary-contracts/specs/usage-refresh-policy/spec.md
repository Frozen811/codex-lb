## ADDED Requirements

### Requirement: Weekly-only Pro Lite probes recover available quota safely

The service MUST canonicalize self_serve_business_prolite to prolite and recognize a weekly-only primary window of 10080 minutes with an empty zero-duration secondary window. A successful operator probe followed by available quota MUST clear a stale rate_limited hold, including an old future reset deadline after an early credit reset. Exhausted or failed probes MUST retain the hold. Background refresh MUST retain a real unexpired 429 cooldown, and concurrent operator status changes MUST win the existing compare-and-set. Canonical plan and model eligibility MUST remain available after recovery.

#### Scenario: Early weekly reset and accepted probe

- **WHEN** a rate-limited Pro Lite account has a future persisted reset and a successful probe observes available weekly-only quota
- **THEN** the account becomes active, cooldown markers clear, plan becomes prolite and the supported model remains eligible

#### Scenario: Failed or exhausted probe

- **WHEN** a weekly-only account has a failed probe or fresh exhausted usage
- **THEN** the account retains its rate-limited hold

#### Scenario: Concurrent pause wins recovery

- **WHEN** an operator pauses the account while fresh weekly usage is fetched
- **THEN** recovery preserves the pause
