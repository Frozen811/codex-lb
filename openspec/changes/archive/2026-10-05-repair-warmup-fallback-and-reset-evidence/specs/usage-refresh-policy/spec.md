## ADDED Requirements

### Requirement: Sliding idle warmup claims use the stable cycle

For idle quota deadlines that slide with the evaluation clock, staggered idle warmup MUST schedule non-zero account slots against the stable epoch cycle of the observed short-window duration. Slot zero MUST use the same stable cycle when consecutive usage observations show the deadline advancing with the observation clock; a fixed deadline MUST retain its existing phase. The durable claim MUST identify the scheduling cycle and MUST prevent another idle send for the account within that cycle even if the upstream reset deadline moves beyond timestamp jitter tolerance and idle cooldown is zero.

#### Scenario: Moving deadline cannot duplicate a cycle claim
- **WHEN** two refresh evaluations observe the same account inside its stable idle slot with different sliding reset deadlines
- **THEN** at most one idle warmup is sent and the persisted claim identifies the stable cycle end

#### Scenario: Next cycle admits a new claim
- **WHEN** the account reaches its slot in the next stable cycle with a fresh idle sample
- **THEN** a new idle warmup may be sent under a distinct cycle claim

#### Scenario: Fixed upstream deadlines retain their phase
- **WHEN** an idle primary deadline is fixed rather than sliding
- **THEN** slot evaluation and the durable cycle claim remain anchored to that fixed deadline
