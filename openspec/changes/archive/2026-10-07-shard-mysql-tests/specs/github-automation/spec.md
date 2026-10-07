## ADDED Requirements

### Requirement: MySQL tests partition across three isolated CI runners

The MySQL CI suite MUST use three deterministic shards from one canonical
file/node selection shared with the complete local test target. Every selected
test MUST belong to exactly one shard, with no omissions, duplicates or empty
shards. Selectors from the same file MUST stay on the same runner and retain
file-based xdist scheduling and isolated worker databases. Recorded file
durations MUST take precedence when supplied; otherwise selected-test estimates
MUST account for test parametrization and database/migration work. A partial
file selection MUST NOT expand into the entire file.

Each shard MUST upload its own JUnit report. The CI required gate MUST wait for
all three runners, and a failed, skipped or cancelled MySQL matrix MUST fail
the compatibility context `Tests (pytest, MySQL)`.

#### Scenario: All MySQL selections execute

- **WHEN** the MySQL suite is partitioned into three shards
- **THEN** their selections form exactly the complete local suite
- **AND** selectors from one file appear in one shard only

#### Scenario: One MySQL runner fails

- **WHEN** any MySQL shard fails
- **THEN** the MySQL compatibility aggregate and CI Required fail
- **AND** the other shards can finish because fail-fast is disabled

#### Scenario: A pull request does not change backend paths

- **WHEN** backend tests are not selected
- **THEN** all three shard contexts report success through placeholder steps
- **AND** the compatibility aggregate succeeds without downloading a skipped build
