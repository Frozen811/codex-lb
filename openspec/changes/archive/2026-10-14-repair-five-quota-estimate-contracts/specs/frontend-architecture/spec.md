## MODIFIED Requirements

### Requirement: Dashboard displays estimated dollar value of full weekly limits

Dashboard overview and projections SHALL expose equivalent per-account full-week
USD estimates based on matched cost and increasing usage-percent observations
inside one current weekly reset epoch. The estimate SHALL equal interval cost
times 100 divided by the interval's usage percentage-point change. It MUST NOT
use pooled usage percentages or dashboard timeframe activity totals. Unknown
costs, resets, non-monotonic samples, insufficient observations or zero changes
SHALL suppress an estimate. The UI SHALL label estimates by account and explain
that they are API-price equivalents rather than guaranteed allowances. Legacy
fleet dollar estimate fields SHALL remain null.
The account estimate list SHALL use bounded internal scrolling when it exceeds
the card's visible list area.

#### Scenario: Timeframe-independent account estimate
- **WHEN** one account consumes 10 percentage points and 4 USD between matched observations
- **THEN** both endpoints estimate its full weekly API-price equivalent as 40 USD
- **AND** choosing a different overview timeframe leaves that estimate unchanged

#### Scenario: Large account pool
- **WHEN** the card receives 101 account estimates
- **THEN** the list remains bounded and its last estimate can be reached by scrolling

## ADDED Requirements

### Requirement: API-owned Pro reference capacity

Weekly pace responses SHALL expose the current Pro weekly estimate. The frontend
SHALL use that value for Pro-account equivalents and MUST NOT embed another Pro
capacity constant. Missing or zero reference capacity SHALL suppress equivalents.

#### Scenario: Operator overrides Pro capacity
- **WHEN** a valid Pro weekly override is active
- **THEN** backend and frontend equivalents use that override on the next request
