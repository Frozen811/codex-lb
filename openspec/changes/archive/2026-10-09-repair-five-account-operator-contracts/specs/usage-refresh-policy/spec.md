## MODIFIED Requirements

### Requirement: Reset-confirmed limit warm-up

The system SHALL support an optional limit warm-up mechanism that is disabled by default. When enabled globally and for an account, background usage refresh MAY send one minimal upstream Responses request after it confirms that a selected quota window moved into a newly available reset window. Eligibility SHALL depend on a real reset transition, the configured post-reset availability gate and an inclusive pre-reset usage floor. The public `limit_warmup_exhausted_threshold_percent` setting SHALL default to zero and SHALL require the reset evidence before sample to meet a configured positive floor. Zero SHALL accept every otherwise eligible confirmed reset.

Background usage refresh MUST complete any applicable blocked-status reconciliation before warm-up evaluation. Candidate evaluation and the sender's fresh preflight check MUST both require the account to be `active`; paused, deactivated, `reauth_required`, `rate_limited`, and `quota_exceeded` accounts MUST NOT receive warm-up traffic. When a reset-confirmed recovery uses persisted transition evidence, warm-up SHALL reuse that same before/after pair so the new account/window/reset tuple enters the ordinary durable deduplication path.

The configured `limit_warmup_cooldown_seconds` SHALL gate only staggered idle warm-up candidates. It MUST NOT suppress a reset-confirmed candidate for a distinct account/window/reset tuple, which remains protected by the durable atomic attempt claim for that tuple.

#### Scenario: Zero threshold permits a real reset regardless of prior usage
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

### Requirement: Confirmed paid-to-Free transitions warm the new monthly window

When background usage refresh confirms that an opted-in active account changed
from a recognized paid plan to `free`, and that confirming refresh writes a
fresh monthly usage sample with a reset deadline and enough available quota for
the configured warm-up threshold, the system SHALL attempt one long-window
warm-up for that monthly quota window. With a zero pre-reset usage floor, eligibility MUST NOT depend on the usage percentage reported before the plan change. With a positive floor, a prior monthly observation MUST exist and meet that floor.

The plan-transition exception SHALL apply only to an actual paid-to-Free change
confirmed by the refresh that wrote the monthly sample. It MUST NOT apply to a
single unconfirmed Free observation, an account that was already Free, or a
monthly sample left over from an earlier refresh. Ordinary same-window reset
detection MUST remain unchanged. The durable warm-up identity SHALL remain the
account, canonical `monthly` window, and monthly reset deadline. The confirming
monthly sample MUST report `used_percent < 100`; the configured minimum-
available threshold MAY impose a stricter lower usage limit.

#### Scenario: Confirmed paid-to-Free transition warms fresh monthly quota

- **GIVEN** an active opted-in account whose stored plan is a recognized paid plan
- **WHEN** background usage refresh confirms its transition to `free`
- **AND** that confirming refresh writes a monthly sample with a reset deadline and enough available quota
- **THEN** the system attempts one warm-up identified by the account, `monthly` window, and monthly reset deadline

#### Scenario: Zero floor does not gate plan-transition warm-up

- **GIVEN** an active opted-in paid account with a zero pre-reset usage floor whose previous selected quota sample was not exhausted
- **WHEN** background usage refresh confirms its transition to `free` and writes an eligible fresh monthly sample
- **THEN** the system attempts the monthly warm-up regardless of the previous usage percentage

#### Scenario: One unconfirmed Free observation does not warm

- **GIVEN** an active opted-in account whose stored plan is a recognized paid plan
- **WHEN** one background usage refresh reports `free` without satisfying downgrade confirmation
- **THEN** no plan-transition warm-up is attempted

#### Scenario: Already-Free account does not use the plan-transition exception

- **GIVEN** an active opted-in account whose stored plan was already `free`
- **WHEN** background usage refresh writes its first monthly sample without confirming a plan change
- **THEN** no plan-transition warm-up is attempted

#### Scenario: Stale monthly history does not warm after a plan change

- **GIVEN** an active opted-in account whose transition from a paid plan to `free` is confirmed
- **WHEN** the latest monthly sample predates the confirming refresh
- **THEN** no plan-transition warm-up is attempted

#### Scenario: Existing durable identity deduplicates the transition warm-up

- **GIVEN** a warm-up attempt already exists for an account, `monthly` window, and monthly reset deadline
- **WHEN** the same confirmed paid-to-Free transition is evaluated again
- **THEN** no second warm-up request is sent for that durable identity

## ADDED Requirements

### Requirement: Reset threshold activation preserves historical settings
The public reset-confirmed warm-up threshold SHALL accept finite values from zero through 100 inclusive, default to zero and persist in a new active column. The migration SHALL initialize existing active thresholds to zero without modifying historical legacy threshold values or defaults. Dashboard numeric validation SHALL accept explicit zero and reject empty input. Paid-to-Free transition warm-up with a positive floor SHALL require a matching prior monthly observation meeting the floor; missing or wrong-window prior observations SHALL NOT qualify.

#### Scenario: Inclusive usage floor
- **WHEN** a real reset has before usage 49 or 50 percent and the configured floor is 50 percent
- **THEN** only the 50 percent reset SHALL qualify.

#### Scenario: Preserved legacy settings
- **WHEN** a database with a historical legacy threshold is upgraded
- **THEN** its active threshold SHALL be zero and its legacy value SHALL remain unchanged.

#### Scenario: Paid-to-Free missing monthly baseline
- **WHEN** a paid-to-Free monthly transition has no prior monthly observation and a positive threshold
- **THEN** warm-up SHALL be skipped.

#### Scenario: Zero threshold input
- **WHEN** an operator supplies explicit zero or an empty dashboard threshold input
- **THEN** zero SHALL be accepted and empty input SHALL be rejected.

#### Scenario: Migration ledger was rewound
- **WHEN** the active threshold column already exists with the expected non-null floating schema and zero default
- **THEN** upgrade SHALL preserve its configured values without adding the column again.

#### Scenario: Existing threshold column is incompatible
- **WHEN** the existing active threshold column is nullable or has an incompatible type or default
- **THEN** upgrade SHALL fail explicitly without silently accepting the incompatible schema.
