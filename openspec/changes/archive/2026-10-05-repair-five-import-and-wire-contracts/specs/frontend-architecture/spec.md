## ADDED Requirements

### Requirement: Account auth imports support ordered retryable batches

The Accounts import dialog SHALL allow one or more auth JSON files and SHALL send each file sequentially through the existing single-file import API in selection order. Successful files MUST leave the pending selection. A failure MUST stop dispatch and retain exactly the failed and unattempted files for retry. While any batch is running, file selection, repeated submission, Escape, outside dismissal and the close control MUST NOT interrupt or duplicate the batch. The dialog SHALL clear and close after all selected files succeed. Existing account authorization and per-file refresh behavior MUST remain in effect. Filenames SHALL be displayed as text without rendering file contents.

#### Scenario: Ordered successful import

- **WHEN** an operator selects three auth files and submits
- **THEN** each file is sent once in order, with at most one active import
- **AND** the dialog closes with an empty pending selection after the third success

#### Scenario: Partial failure retains only pending files

- **WHEN** the second file fails after the first file succeeds
- **THEN** the third file has not been sent and only the second and third files remain selected
- **AND** retry starts with the second file and never reimports the first file

#### Scenario: Busy batch cannot be dismissed or repeated

- **WHEN** an import is pending and the operator attempts Escape, outside click, close or resubmission
- **THEN** the batch stays open and continues without overlapping imports
- **AND** changing the file selection is disabled

### Requirement: Model Source capability controls expose their translated names

Every capability checkbox in Model Source create and edit forms MUST expose a programmatic name matching its translated visible label. Clicking the label and pressing Space on a focused checkbox SHALL toggle the same capability. Each rendered form SHALL associate its labels with its own controls.

#### Scenario: Named controls in both forms

- **WHEN** either create or edit is opened
- **THEN** every capability checkbox can be found by its role and translated name
- **AND** label click and keyboard Space change that control's checked state
