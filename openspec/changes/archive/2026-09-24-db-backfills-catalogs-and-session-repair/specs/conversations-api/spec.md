# conversations-api Specification Delta

## Requirements

### Requirement: Targeted Codex session metadata repair

The Codex session repair and retag CLI tool MUST support targeted single-session repair:
1. The tool SHALL accept an explicit session target via `--session-id` or `--thread-id` to avoid full directory traversals when repairing individual corrupted sessions.
2. The tool SHALL create rollback evidence before mutation, preferring hard-links for JSONL files on the same volume with safe file copy fallbacks.
3. The tool SHALL verify metadata consistency after repair and report modified, skipped, and restored session counts.

#### Scenario: Single session targeted repair
- **WHEN** `codex-lb codex-sessions retag --session-id <id> --to <provider>` is run
- **THEN** only metadata matching the specified session is inspected and updated
- **AND** a rollback backup is preserved before write
