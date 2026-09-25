# account-quota-presentation Specification

## Purpose
Governs how account quota windows are presented across the dashboard when an account does not fit the paid 5h/7d shape. Free accounts report a single monthly window, and rendering it as weekly produced wrong bars, trends, donut totals, and assigned-account badges. This capability keeps monthly-only accounts labelled as such, omits zero-credit accounts from window totals they cannot contribute to, and keeps quota refreshes visually stable.

## Requirements

### Requirement: Monthly-only account quota surfaces

When an account's normalized quota model is monthly-only, account-facing quota surfaces SHALL present only the monthly window and MUST NOT render synthetic 5h or 7d bars for that account.

#### Scenario: Account surfaces show only monthly quota
- **WHEN** an account summary carries a normalized monthly quota window with no normalized 5h or 7d windows
- **THEN** the account card, account list row, and account detail usage panel show a single `Monthly` quota bar
- **AND** those surfaces do not render `5h` or `Weekly` bars for that account

### Requirement: Free-account overview quota hides 5h and 7d semantics

Overview and aggregate quota surfaces SHALL treat normalized monthly-only free-account quota as a 30d window and MUST NOT present that account as a weekly-only or dual-window account.

#### Scenario: Overview uses monthly semantics for free accounts
- **WHEN** overview data includes a free account with only a normalized monthly quota window
- **THEN** the overview account quota display shows only the 30d window for that account
- **AND** the account and API navigation progress logic uses monthly-only quota state for that account

### Requirement: Monthly quota remains visible in recent-trend displays

The account usage trend SHALL preserve the recent 7-day trend timeframe while identifying monthly-only quota lines as monthly quota.

#### Scenario: Monthly account trend labels the monthly line
- **WHEN** an account trend view renders a monthly-only free account
- **THEN** the trend legend identifies the quota line as `Monthly`
- **AND** the trend view still identifies itself as a 7-day trend

### Requirement: Zero-credit assigned accounts are omitted from 5h and weekly donut totals

Aggregate quota donuts SHALL omit assigned accounts whose visible assigned credits for the corresponding donut are zero.

#### Scenario: Zero-credit account does not contribute to donut totals
- **WHEN** an assigned account has zero visible credits for a 5h or weekly donut calculation
- **THEN** that account is excluded from the corresponding donut total and legend contributions

### Requirement: Account quota refreshes preserve visual continuity

Account-facing quota surfaces MUST retain the last valid percentage when a
refresh briefly reports an unknown or non-finite value. They MUST keep the
corresponding quota row mounted for the same bounded hold and MUST NOT render
the unknown refresh state as zero. When a later valid percentage arrives, the
visible number and bar MUST ease from the displayed value to the new value at
0.1 percent display resolution. Reduced-motion preferences MUST update the
value without animation. Raw percentages used by sorting and routing MUST stay
unchanged.

#### Scenario: Temporary unknown value does not drain the bar

- **GIVEN** an account quota row displays a valid remaining percentage
- **WHEN** a refresh temporarily reports that percentage as unknown or non-finite
- **THEN** the account card, account list row, and account detail usage panel keep the last valid percentage visible
- **AND** the quota row remains mounted
- **AND** the bar does not drain to zero

#### Scenario: Fresh percentage replaces the held value smoothly

- **GIVEN** an account quota row is displaying a valid or held percentage
- **WHEN** a later refresh reports a different valid percentage
- **THEN** the displayed number and bar ease to the fresh percentage
- **AND** the visible number can change in 0.1 percent increments
- **AND** the raw percentage used by sorting and routing is unchanged

#### Scenario: Reduced motion skips the transition

- **GIVEN** the user prefers reduced motion
- **WHEN** a fresh valid percentage replaces the displayed percentage
- **THEN** the quota surface displays the fresh percentage without animation

### Requirement: Observed monthly quota is independent of plan capacity
The system SHALL normalize a lone primary quota of 40320 through 46080 minutes inclusive as monthly, whether its secondary window is absent or a zero-duration placeholder. Poll and live ingestion SHALL apply the same classification. Account summaries SHALL retain observed monthly duration and remaining percentage regardless of plan credit capacity, and SHALL leave unknown credit estimates null. A newer valid short or weekly quota sample SHALL supersede an older monthly sample for a plan without monthly credit capacity.

#### Scenario: Team monthly observation
- **WHEN** a Team account reports a lone primary quota of 43200 or 43800 minutes with 96 percent used
- **THEN** its summary exposes 4 percent monthly remaining and the observed duration
- **AND** it exposes no synthetic primary or secondary quota and no invented monthly credits

#### Scenario: Zero-duration secondary placeholder
- **WHEN** a monthly primary observation includes a secondary window with zero duration
- **THEN** it is normalized to monthly only

#### Scenario: Paid plan upgrade
- **WHEN** a plan without monthly credit capacity has short or weekly quota observed after its monthly quota
- **THEN** the summary uses the newer short or weekly quota and omits the stale monthly quota

#### Scenario: Ordinary and out-of-band windows
- **WHEN** primary duration is 300, 10080, 40319 or 46081 minutes, or a positive-duration secondary exists
- **THEN** monthly-only normalization does not replace those windows

### Requirement: Faithful account trend series
The account trend chart SHALL preserve every distinct observation instant and SHALL linearly interpolate missing window samples between observations using elapsed time and SHALL hold the last observed value after the final observation. Values before the first observation SHALL remain unknown; actual zero observations SHALL be preserved. Legends SHALL list only available series. Monthly-account long-window tooltips SHALL use monthly labels.

#### Scenario: Different observation timestamps
- **GIVEN** a primary observation and a monthly observation have different timestamps
- **WHEN** the chart combines the series
- **THEN** both observations SHALL be retained and each missing counterpart SHALL interpolate between surrounding observations, retain its last observed value if no later observation exists, or remain unknown if no earlier observation exists.

#### Scenario: Equivalent instants with different UTC offsets
- **GIVEN** quota observations and a scheduled value refer to the same instant using different UTC offsets
- **WHEN** the chart combines the series
- **THEN** it SHALL show one point at that instant with each observed and scheduled value available.

#### Scenario: Monthly-only trend
- **GIVEN** only monthly observations exist
- **THEN** the chart SHALL show Monthly without a 5-hour legend and SHALL label its long-window tooltip Monthly.

### Requirement: Account-scoped quota presentation state
Smoothed quota values and known-window state SHALL reset when the selected account changes.

#### Scenario: Switching quota shapes
- **GIVEN** a dual-window account was selected
- **WHEN** the operator selects a different monthly-only account
- **THEN** only the new account's monthly quota SHALL be shown, without retained 5-hour or weekly values.

### Requirement: Codex Desktop usage preserves caller plan identity while pooling quota

When responding to Codex Desktop and Codex CLI usage endpoints (`/api/codex/usage`, `/backend-api/wham/usage`, and `/backend-api/codex/usage`), the proxy SHALL retain the signed-in caller's account `plan_type` while returning the aggregate quota windows, limits, and availability across the eligible account pool.

#### Scenario: Signed-in account retains plan identity with pooled capacity
- **GIVEN** a signed-in ChatGPT account with plan type `plus`
- **AND** another account in the pool with plan type `pro`
- **WHEN** Codex Desktop requests usage via `/api/codex/usage` or `/backend-api/wham/usage`
- **THEN** the returned payload `plan_type` reports `plus`
- **AND** the `rate_limit` details reflect aggregate pool utilization and availability
