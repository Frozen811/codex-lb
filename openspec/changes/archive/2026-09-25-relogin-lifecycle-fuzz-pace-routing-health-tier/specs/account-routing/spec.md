# account-routing Specification Delta

## ADDED Requirements

### Requirement: Health-tier dominance over budget-safe routing

In budget-safe account selection (`_select_account_preferring_budget_safe`), health tiers MUST strictly dominate budget thresholds. The preferred pool of accounts below the budget threshold MUST be computed from the highest available health tier (`_best_health_tier_states`), preventing degraded, cooling-down, or backoff accounts from leapfrogging healthy accounts simply because they have lower usage.

#### Scenario: Healthy account above budget threshold preferred over degraded account below threshold
- **GIVEN** Account A is in `HEALTH_TIER_HEALTHY` with usage above the budget threshold
- **AND** Account B is in a lower health tier (`HEALTH_TIER_PROBING` or cooldown) with usage below the budget threshold
- **WHEN** budget-safe account selection runs
- **THEN** Account A is selected because its health tier strictly dominates Account B

#### Scenario: Budget-safe preference applies within the same health tier
- **GIVEN** Account A and Account B are both in `HEALTH_TIER_HEALTHY`
- **AND** Account A is below the budget threshold while Account B is above it
- **WHEN** budget-safe account selection runs
- **THEN** Account A is selected as budget-safe

### Requirement: Pace-aware routing across reset boundaries

The load balancer SHALL compute pace deviation (`actual_used_pct - expected_used_pct`) based on elapsed time within each account's quota reset window (`calculate_pace_deviation`). When routing across multiple eligible accounts, the system SHALL support prioritizing accounts running behind pace (possessing pace surplus) over accounts running hot ahead of schedule, guiding cumulative fleet usage to land smoothly on reset boundaries.

#### Scenario: Account behind pace prioritized over account ahead of pace
- **GIVEN** Account A and Account B have identical total quota
- **AND** Account A is running behind pace (usage below expected schedule for its window)
- **AND** Account B is running ahead of pace (usage above expected schedule for its window)
- **WHEN** pace-aware selection evaluates candidates
- **THEN** Account A is prioritized to receive traffic
