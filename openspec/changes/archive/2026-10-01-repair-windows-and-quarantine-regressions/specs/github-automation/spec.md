## ADDED Requirements

### Requirement: Windows startup is checked automatically

The Windows startup regression workflow SHALL run on main pushes, pull-request source updates, merge-group events and manual dispatches with read-only repository permissions. It MUST test platform portability and architecture diagnostics on a Windows runner and smoke-test an installed wheel outside the checkout using isolated storage. The smoke MUST observe successful readiness, dashboard HTML, JavaScript and CSS rather than only importing the application.

#### Scenario: Main receives a source update

- **WHEN** a commit is pushed to main
- **THEN** Windows startup checks run automatically for that commit
- **AND** startup or asset failures fail the workflow

#### Scenario: Pull request or merge queue candidate is evaluated

- **WHEN** a pull-request source update or merge-group event occurs
- **THEN** Windows startup checks evaluate that candidate without repository write permissions
