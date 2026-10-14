## ADDED Requirements

### Requirement: Opt-in sticky budget reallocation waits for explicit compaction

The settings API MUST persist `stickyReallocationTiming` as `immediate` or `after_compaction`, reject other values and preserve the stored mode when updates omit it. New and historical rows MUST default to `immediate`. This timing policy MUST gate the pressure-triggered reallocation scenarios of the typed sticky-session requirement. In `after_compaction` mode, ordinary Responses turns using soft prompt-cache or sticky-thread affinity MUST retain an eligible mapped account despite sticky budget pressure. Explicit compact requests MUST permit pressure-based reallocation to an eligible healthier account. Hard response, file and turn-state ownership MUST remain authoritative, including at compaction. Actual owner unavailability and safe pre-visible failure recovery MUST retain their existing rules. Default `immediate` mode MUST retain the existing pressure behavior.

#### Scenario: Ordinary sticky-thread turn retains its pressured owner
- **WHEN** an ordinary turn uses deferred soft-affinity mode and its active owner exceeds the sticky pressure threshold
- **AND** another eligible account has lower pressure
- **THEN** the turn stays on the existing owner and does not rebind the mapping

#### Scenario: Explicit compact can move a soft sticky thread
- **WHEN** the same soft sticky thread in deferred mode sends an explicit compact request
- **AND** its owner exceeds the sticky pressure threshold while another account is below it
- **THEN** compact selects the healthier account and updates the soft mapping

#### Scenario: Hard compaction ownership is preserved
- **WHEN** compact carries a required response, file or turn-state owner
- **THEN** that owner constrains selection and the soft policy does not override it

#### Scenario: Default prompt-cache routing retains immediate pressure behavior
- **WHEN** a request uses default immediate timing
- **THEN** the existing pressure-reallocation policy remains in effect

#### Scenario: Timing updates are validated and survive partial changes
- **WHEN** an operator selects `after_compaction`, then updates unrelated settings
- **THEN** the selected mode persists
- **AND** an invalid timing value is rejected without changing the stored mode

#### Scenario: Historical rows keep compatible routing during upgrade
- **WHEN** a database containing existing settings upgrades to the timing revision
- **THEN** existing rows receive `immediate` and retain all unrelated setting values
