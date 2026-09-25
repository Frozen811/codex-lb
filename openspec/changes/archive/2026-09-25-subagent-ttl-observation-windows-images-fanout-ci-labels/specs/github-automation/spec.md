# github-automation Specification Delta

## ADDED Requirements

### Requirement: Reconcile issue and PR status labels upon activity

The repository SHALL provide workflow automation to reconcile status labels on issues and pull requests when new comments or responses occur. When an issue or pull request carrying the `needs-info` label receives a new comment from a non-bot user (such as the author/reporter providing follow-up details), the automation MUST automatically remove `needs-info` (and `stale` if present) and assign `triage` (for issues) or `awaiting-review` (for PRs) so the item is no longer marked as waiting on the reporter.

#### Scenario: Reporter comments on an issue with needs-info
- **GIVEN** an open issue has label `needs-info`
- **WHEN** the issue reporter or non-bot user submits a comment
- **THEN** `needs-info` is removed from the issue
- **AND** `stale` is removed if present
- **AND** `triage` is added if neither `triage` nor `awaiting-review` is present

#### Scenario: Bot comment does not clear needs-info
- **GIVEN** an open issue has label `needs-info`
- **WHEN** an automated bot leaves a comment
- **THEN** `needs-info` is preserved
