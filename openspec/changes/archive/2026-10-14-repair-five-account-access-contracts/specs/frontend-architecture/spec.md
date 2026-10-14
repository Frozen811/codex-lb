## ADDED Requirements

### Requirement: Account credential identity text stays within the viewport

Account list/detail and credential export dialogs MUST contain long account names, email addresses and upstream identifiers at mobile and desktop widths. Long identity strings MUST wrap or truncate within their own content boundaries without widening the document or making export actions unreachable. Credential export dialogs MUST constrain their height to the viewport and allow scrolling when their content exceeds that height.

#### Scenario: Long identity in account export
- **WHEN** the operator views and exports an account with a long email and upstream identifier at a 390px viewport
- **THEN** the document has no horizontal overflow
- **AND** the export dialog's download and close actions remain reachable.
