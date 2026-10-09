## ADDED Requirements

### Requirement: Whole-home retag planning is bounded to provider metadata

Provider-retag planning MUST read at most 64 KiB per session JSONL file, recognize only a leading canonical session_meta record or consecutive leading legacy provider records, and ignore provider-like fields in transcript content. It MUST reject malformed or oversized initial metadata before writes. Planning MUST use one grouped provider-count query per eligible SQLite database and reuse the plan for summaries. Confirmed writes MUST preserve opaque transcript bytes, create backups before mutation, verify planned targets and report retained backup paths on partial failure. Dry runs MUST not mutate files or create backups.

#### Scenario: Large opaque transcript stays outside planning and rewriting
- **WHEN** a session contains a supported leading provider header followed by a large transcript including provider-like fields
- **THEN** planning reads at most 64 KiB and confirmed rewriting changes only the recognized metadata
- **AND** transcript bytes and unrelated files remain unchanged

#### Scenario: Invalid initial metadata prevents mutation
- **WHEN** initial provider metadata is malformed or exceeds the fixed header limit
- **THEN** the command fails before backup or mutation

#### Scenario: Grouped counts and planned verification avoid home rescans
- **WHEN** whole-home retag plans eligible state databases and executes its plan
- **THEN** it uses one grouped planning count per database and verifies only planned files and rows
- **AND** summaries derive from that plan

### Requirement: Retag progress does not interrupt owned writes

The retag CLI MUST support opt-in --progress-json events on stderr with phase, completed and total fields, while preserving its stdout summary. A closed progress pipe MUST disable progress and permit the operation to finish successfully. Backup, rewrite, verification and completion progress MUST reflect completed file/database units; failures MUST retain and identify available backups.

#### Scenario: Machine-readable progress preserves summary
- **WHEN** confirmed retag uses --progress-json
- **THEN** stderr contains parseable phase events and stdout retains the human summary

#### Scenario: Progress consumer closes early
- **WHEN** the progress pipe closes during planning or writing
- **THEN** subsequent progress is disabled and successful data work still exits successfully
