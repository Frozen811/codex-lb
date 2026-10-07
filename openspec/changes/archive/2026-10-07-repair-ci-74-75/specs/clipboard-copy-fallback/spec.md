## ADDED Requirements

### Requirement: Copy feedback belongs to the mounted control

OAuth copy controls MUST cancel pending feedback resets when unmounted and MUST ignore clipboard success or failure arriving after unmount. Repeated successful copies MUST restart the existing two-second feedback interval without leaving earlier reset timers active. Browser and device flows MUST preserve their existing clipboard fallback and keyboard or pointer focus behavior.

#### Scenario: Dialog closes during copied feedback
- **WHEN** an OAuth copy control unmounts during its copied feedback interval
- **THEN** its pending reset is cancelled without a later state update

#### Scenario: Clipboard completes after dialog closes
- **WHEN** a pending clipboard operation succeeds or fails after its OAuth control unmounts
- **THEN** no feedback timer, state update or failure toast is produced

#### Scenario: User copies again before feedback expires
- **WHEN** another successful copy occurs before the two-second interval expires
- **THEN** copied feedback remains visible until two seconds after the latest successful copy
