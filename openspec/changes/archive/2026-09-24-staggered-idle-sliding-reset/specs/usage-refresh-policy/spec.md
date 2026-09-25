## MODIFIED Requirements

### Requirement: Reset-confirmed limit warm-up

The system SHALL support an optional limit warm-up mechanism that is disabled by default. When enabled globally and for an account, background usage refresh MAY send one minimal upstream Responses request after it confirms that a selected quota window moved into a newly available reset window. Eligibility SHALL depend on a real reset transition and the configured post-reset availability gate, not on whether the previous window was exhausted. The legacy `limit_warmup_exhausted_threshold_percent` setting MUST NOT gate reset-confirmed eligibility.

Background usage refresh MUST complete any applicable blocked-status reconciliation before warm-up evaluation. Candidate evaluation and the sender's fresh preflight check MUST both require the account to be `active`; paused, deactivated, `reauth_required`, `rate_limited`, and `quota_exceeded` accounts MUST NOT receive warm-up traffic. When a reset-confirmed recovery uses persisted transition evidence, warm-up SHALL reuse that same before/after pair so the new account/window/reset tuple enters the ordinary durable deduplication path.

The configured `limit_warmup_cooldown_seconds` SHALL gate only staggered idle warm-up candidates. It MUST NOT suppress a reset-confirmed candidate for a distinct account/window/reset tuple, which remains protected by the durable atomic attempt claim for that tuple.

#### Scenario: Warm-up follows a real reset regardless of prior usage
- **GIVEN** limit warm-up is enabled globally and for an active account
- **AND** the account's previous usage sample for a selected window reports any usage below or at exhaustion
- **WHEN** background usage refresh records a newer sample that proves a real reset for that window and satisfies the configured availability gate
- **THEN** the system sends at most one warm-up request for that account/window/reset tuple

#### Scenario: Staggered idle cooldown does not suppress a distinct reset tuple
- **GIVEN** an account has a recent warm-up attempt inside `limit_warmup_cooldown_seconds`
- **AND** background usage refresh confirms a different selected account/window/reset tuple
- **WHEN** reset-confirmed warm-up evaluates the new tuple
- **THEN** the staggered idle cooldown MUST NOT suppress that candidate
- **AND** the durable attempt claim MUST still prevent another send for an already claimed identical tuple

#### Scenario: Warm-up is skipped unless reset is confirmed
- **GIVEN** limit warm-up is enabled globally and for an account
- **WHEN** background usage refresh records a newer available sample without a real selected-window reset transition
- **THEN** the system MUST NOT send a reset-confirmed warm-up request for that sample

#### Scenario: Warm-up is not triggered by upstream reset_at timestamp jitter
- **GIVEN** limit warm-up is enabled globally and for an account
- **WHEN** background usage refresh records a newer sample whose `reset_at` advanced by less than 60 seconds as upstream timestamp jitter
- **THEN** the system MUST NOT send a warm-up request for that account/window/reset tuple

#### Scenario: Warm-up is opt-in and safe by default
- **GIVEN** background usage refresh is preparing to evaluate limit warm-up candidates
- **WHEN** global limit warm-up is disabled
- **OR** the account is not opted in
- **THEN** background usage refresh MUST NOT send warm-up traffic

#### Scenario: Warm-up uses fresh opt-in state after usage refresh
- **GIVEN** an account was loaded before a background usage refresh cycle
- **AND** the account's limit warm-up opt-in changes while the refresh cycle is running
- **WHEN** the scheduler evaluates warm-up candidates after writing usage samples
- **THEN** the scheduler MUST evaluate the latest persisted opt-in value rather than the stale in-session account object

#### Scenario: Warm-up respects unsafe account states
- **WHEN** an account is paused, deactivated, `reauth_required`, rate-limited, quota-exceeded, or in an auth-refresh failure path
- **THEN** limit warm-up MUST NOT send traffic for that account

#### Scenario: Reset recovery completes before warm-up
- **GIVEN** an opted-in Free account is `rate_limited` and has qualifying monthly reset evidence
- **WHEN** marker-guarded recovery succeeds
- **THEN** the scheduler first persists the account as `active` and clears its block markers
- **AND** only then may it evaluate the same monthly reset tuple for warm-up

#### Scenario: Recovery race prevents warm-up from stale evidence
- **GIVEN** reset evidence makes a blocked account appear recoverable
- **AND** a concurrent write changes its status or block markers before recovery persists
- **WHEN** the recovery compare-and-set misses
- **THEN** the stale scheduler snapshot remains ineligible for warm-up

#### Scenario: Sender rejects an account re-blocked after candidate creation
- **GIVEN** an active account produced a valid warm-up candidate
- **AND** the account becomes blocked before upstream warm-up traffic begins
- **WHEN** the sender reloads the account state
- **THEN** it does not send the warm-up request

#### Scenario: Warm-up attempts are durable and deduplicated
- **WHEN** multiple refresh workers observe the same account/window/reset candidate
- **THEN** the database permits at most one persisted attempt for that tuple
- **AND** later refresh cycles skip that tuple after a prior attempt exists

#### Scenario: Persisted recovery evidence shares the warm-up tuple
- **GIVEN** a scheduler restart causes recovery to use a persisted monthly before/after transition
- **WHEN** the recovered active account reaches warm-up evaluation
- **THEN** warm-up derives the candidate from that same transition's new reset deadline
- **AND** an existing attempt for the account/monthly/reset tuple prevents another send

#### Scenario: Staggered idle warm-up pre-starts rolling primary windows
- **GIVEN** limit warm-up and staggered idle warm-up are enabled globally
- **AND** multiple active accounts are opted into limit warm-up
- **AND** an opted-in account has a healthy idle short-window primary usage sample (any sample reporting a duration over 24 hours is not eligible) with `used_percent` at or below the configured `limit_warmup_idle_threshold_percent`
- **AND** no prior warm-up attempt places the account inside the configured cooldown
- **AND** the usage sample was refreshed for the current cycle
- **WHEN** background usage refresh evaluates that account inside its deterministic stagger slot
- **THEN** the system MUST attempt to send one minimal upstream warm-up request for that account's current rolling-window cycle, whose length is the account's observed primary window duration (defaulting to 300 minutes when duration metadata is missing)
- **AND** the system MUST NOT send another staggered idle warm-up for that same account/cycle tuple
- **AND** account slots MUST be spread deterministically across the account's rolling window so restarts do not align all opted-in accounts into the same phase

#### Scenario: Staggered idle slots remain reachable when reset deadline slides with now
- **GIVEN** multiple active opted-in accounts participate in staggered idle warm-up
- **AND** upstream rate limit reports a sliding reset deadline that continuously advances with the current evaluation clock
- **WHEN** background usage refresh evaluates each account inside its designated slot
- **THEN** non-zero staggered idle slots MUST evaluate their elapsed slot phase against a stable cycle start so that all account slots remain reachable and are not starved by the sliding reset timestamp

#### Scenario: Staggered idle warm-up is skipped for accounts with real usage
- **GIVEN** staggered idle warm-up is enabled globally
- **AND** an active opted-in account has a short-window primary usage sample with `used_percent` above the configured `limit_warmup_idle_threshold_percent`
- **WHEN** background usage refresh evaluates that account
- **THEN** the system MUST NOT send staggered idle warm-up traffic for that account

#### Scenario: Staggered idle warm-up remains opt-in
- **GIVEN** limit warm-up is enabled globally and for an account
- **AND** staggered idle warm-up is disabled
- **WHEN** background usage refresh observes an idle short-window primary sample that is not a reset-confirmed transition
- **THEN** limit warm-up MUST NOT send synthetic traffic for that idle sample
