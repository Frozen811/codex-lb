## ADDED Requirements

### Requirement: Accounts inventory distributions
The Accounts page MUST display plan and status distributions for all loaded accounts, including paused, deactivated and reauthentication-required accounts. Counts and percentages MUST remain independent of list search, filtering and pagination. Legends MUST be keyboard accessible, and empty data MUST have a distinct no-data state.

#### Scenario: Filtered inventory
- **WHEN** an operator filters the account list
- **THEN** distribution totals and category counts continue to reflect every loaded account

#### Scenario: Empty or unavailable inventory
- **WHEN** the account read succeeds with no accounts
- **THEN** distributions show zero and no data
- **AND** a failed initial read shows its error instead of a successful empty distribution

### Requirement: Optional compact API-key inventory
The APIs page MUST retain its default detail view and provide a persisted optional compact list. The compact list MUST support name, status, request count, expiry and last-used sorting, pagination, selected-key details and combined search/status/unused filters. Unknown numeric/date values MUST sort last in either direction. Read-only sessions MUST retain inspection without mutation controls. Unavailable browser storage MUST NOT prevent switching views.

#### Scenario: Recorded usage determines unused keys
- **WHEN** unused filtering is enabled
- **THEN** keys with a recorded last use or positive request/token/cost usage are excluded
- **AND** the overview and filter agree on whether a key has recorded usage

#### Scenario: Read-only paginated compact list
- **WHEN** a read-only operator opens a key on the second page of the compact list
- **THEN** its details are inspectable and mutation actions remain unavailable

### Requirement: Reset-credit expiry warning
An account with positive available reset credits MUST display an accessible warning in its count badge when its nearest valid expiry is later than now and at most 72 hours away. The warning MUST honor the existing count and expiry visibility settings, update without a data refetch and release its timer when hidden or unmounted. Zero credits and missing, invalid or elapsed expiry MUST NOT display the warning.

#### Scenario: Live warning boundary
- **WHEN** the nearest expiry enters the next 72 hours while the list remains open
- **THEN** the warning appears without a refetch and disappears after expiry

#### Scenario: Warning visibility
- **WHEN** either badge setting is disabled or the available count is zero
- **THEN** the warning is absent

### Requirement: Status and remaining-quota account sorting
The Accounts sort selector MUST offer both directions for status and remaining 5-hour, weekly and monthly quota while preserving existing defaults and sort modes. Active-first status order MUST be active, paused, rate-limited, quota-exceeded, reauthentication-required and deactivated. Missing or non-finite quota MUST remain last in either direction; zero MUST remain a known exhausted value. Equal values MUST resolve deterministically using existing reset, label and account-identifier ties. Sorting MUST preserve input data, filters and explicit selection.

#### Scenario: Known zero and unknown quota
- **WHEN** accounts with zero, positive and unknown remaining quota are sorted in either direction
- **THEN** unknown values are last and zero participates as a known value

#### Scenario: Explicit selection survives sorting
- **WHEN** the operator changes a sort mode while an account is selected
- **THEN** the selected account identifier is preserved and the rendered list follows the chosen order

## MODIFIED Requirements

### Requirement: Accounts list orders by next reset
When reset time soonest-first is selected, the Accounts page account list SHALL order accounts by the earliest upcoming quota reset timestamp among the rendered quota windows. Accounts without any reset timestamp SHALL sort after accounts with a reset timestamp. When reset timestamps are equal or unavailable, the list MAY fall back to a stable text-based order.

#### Scenario: Earlier reset sorts first
- **WHEN** reset time soonest-first is selected and two accounts have different upcoming visible quota reset times
- **THEN** the earlier-reset account appears before the later-reset account

### Requirement: Accounts list supports explicit sort modes

The Accounts page account list SHALL expose sort modes for reset time
soonest-first, reset time latest-first, account name ascending, and account name
descending, most reset credits, status in both directions, and remaining 5h, weekly and monthly quota in both directions. The default sort mode SHALL remain most reset credits. The
same selected sort mode SHALL apply to both the rendered account list and the
page-level selected-account fallback.

#### Scenario: Most reset credits remains the default

- **WHEN** the account list renders without an explicit sort mode
- **THEN** accounts with more available reset credits sort first
- **AND** equal counts use soonest valid credit expiry, then the existing deterministic reset, label and identifier ties

#### Scenario: Reset latest sorts finite resets descending

- **WHEN** a user selects reset time latest-first
- **THEN** accounts with later upcoming visible quota resets sort before
  accounts with earlier upcoming visible quota resets
- **AND** accounts without an upcoming visible reset timestamp sort after
  accounts with finite upcoming reset timestamps

#### Scenario: Name sort modes order by account label

- **WHEN** a user selects account name ascending or descending
- **THEN** the account list orders accounts by display name, email, or account
  identifier in the selected direction
