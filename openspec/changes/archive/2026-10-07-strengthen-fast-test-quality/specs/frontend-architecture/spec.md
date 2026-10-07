## ADDED Requirements

### Requirement: Responsive charts preserve viewport containment during resize

Dashboard sparklines SHALL remain clipped to their responsive containers while
the chart library updates its measured dimensions. A viewport change MUST NOT
introduce document-level horizontal scrolling through a stale chart width.
Request tables SHALL retain their local horizontal scrolling.

#### Scenario: Dashboard changes from mobile to desktop columns

- **WHEN** the viewport changes between supported mobile and desktop widths
- **AND** a sparkline has not yet adopted the responsive container's new width
- **THEN** the chart remains within that container
- **AND** the document does not gain horizontal overflow
