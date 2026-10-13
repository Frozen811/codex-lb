## MODIFIED Requirements

### Requirement: Targeted Codex session metadata repair

The CLI MUST provide read-only `codex-sessions preview` for JSONL and SQLite provider disagreement and `codex-sessions repair --session-id ID --to PROVIDER` for one explicit session. Preview and repair MUST support `openai` and `codex-lb`, preserve transcript bytes, unrelated sessions and `config.toml`, and MUST NOT change provider selection. Repair MUST require confirmation, preserve rollback evidence before mutation, recheck selected identities and provider values, verify resulting consistency, and report modified and skipped counts and the backup location. Ambiguous headers, absent counterparts, unsupported tags, missing IDs, unsafe paths and stale targets MUST fail explicitly. Partial failures MUST retain backups and identify that changes may be partial. Preview MUST NOT create backups or temporary database copies. JSON results MUST remain separate from optional stderr JSONL progress.

#### Scenario: Single session targeted repair
- **WHEN** a confirmed repair selects a session whose JSONL and SQLite provider tags disagree
- **THEN** only that session's planned tags are updated to the explicit supported provider
- **AND** a rollback backup is preserved before write
- **AND** the command verifies the resulting tags and preserves transcript bytes and client configuration

#### Scenario: Read-only mismatch preview
- **WHEN** an operator previews a session without write confirmation
- **THEN** its JSONL and SQLite provider tags and repair eligibility are reported
- **AND** no metadata, backup or temporary copy is written

#### Scenario: Target lookup uses indexed rollout paths
- **WHEN** a selected SQLite thread has a rollout path inside the selected Codex home
- **THEN** targeted discovery reads that file without traversing unrelated session directories
- **AND** its metadata ID must match the selected session ID

#### Scenario: Unsupported or ambiguous repair target
- **WHEN** selected metadata has unsupported tags, conflicting IDs, multiple JSONL headers, missing counterparts or a path outside the selected home
- **THEN** repair refuses before mutation

#### Scenario: Planned target changes during backup
- **WHEN** selected file identity or provider values change after planning
- **THEN** repair refuses further writes and retains its backup with an explicit partial-change diagnostic

#### Scenario: Machine-readable CLI output
- **WHEN** an operator selects JSON output and JSONL progress
- **THEN** stdout contains one result JSON object and stderr contains phase progress JSON objects
