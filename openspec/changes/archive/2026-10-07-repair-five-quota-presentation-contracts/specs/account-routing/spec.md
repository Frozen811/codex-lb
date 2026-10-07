## ADDED Requirements

### Requirement: Monthly quota support is independent of its credit estimate
Team monthly quota SHALL continue to participate in account routing, background recovery, usage freshness and planner warmup freshness when its monthly credit estimate is unknown. Removing an unmeasured monthly credit estimate SHALL NOT discard monthly quota observations or release an explicit exhaustion hold. Existing ordinary-plan handling of unsupported historical monthly rows SHALL remain unchanged.

#### Scenario: Team exhaustion without a monthly credit estimate
- **GIVEN** a Team account has an explicit quota-exhausted hold and fresh exhausted monthly usage
- **WHEN** its fallback reset elapses and account selection evaluates it repeatedly
- **THEN** it remains unavailable and its observed monthly reset or lack of reset metadata is preserved

#### Scenario: Available monthly quota recovers Team
- **GIVEN** a Team account has exhausted monthly quota and no measured monthly credit capacity
- **WHEN** fresh monthly usage proves available quota after its hold
- **THEN** it may recover according to the existing cooldown and recovery gates

#### Scenario: Fresh Team monthly usage avoids redundant polling
- **WHEN** a Team account has fresh monthly usage and no short-window observation
- **THEN** existing freshness rules may use the monthly observation without requiring a numeric credit estimate
