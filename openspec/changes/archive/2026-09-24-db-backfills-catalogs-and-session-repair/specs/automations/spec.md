# automations Specification Delta

## Requirements

### Requirement: Verified weekly-window prestart preset

The automations subsystem SHALL provide an opt-in preset (`weekly_prestart`) that activates an unstarted secondary/weekly quota window for idle accounts and verifies activation.
1. When triggered, the prestart job SHALL inspect candidate accounts and select those whose secondary window has not started (e.g. `reset_at` is null or zero).
2. For each unstarted account, the runner SHALL execute a minimal probe or completion request to initiate the upstream rolling 7-day quota window.
3. The job SHALL refresh usage and verify that the weekly window has been successfully opened.

#### Scenario: Prestart starts and verifies unstarted weekly window
- **GIVEN** an active account whose secondary weekly window has not yet started
- **WHEN** the `weekly_prestart` automation runs for that account
- **THEN** a minimal warm-up request is issued to the upstream
- **AND** refreshed usage confirms the secondary window deadline is initialized
