# Context

Five selected registry rows concern local session metadata repair and existing client setup examples. The repair implementation was absent: only retag flags existed. The ordinary search and Astra examples already satisfy the imported proposals and are independently parsed rather than rewritten.

For example, a session's JSONL header can say `openai` while `state_5.sqlite` says `codex-lb`. Preview reports the mismatch; a confirmed repair to `codex-lb` snapshots and rewrites only the header, leaving the transcript and `config.toml` untouched. The SQLite row is skipped because it already has the requested tag.

SQLite rollout paths avoid unrelated directory traversal for indexed targeted lookup. Older schemas require filename discovery; bounded header reads remain limited to 64 KiB. The existing whole-home retag planning/progress work from the previous operator-data batch is reused and revalidated, not replaced.

Repair requires one unambiguous header plus identified SQLite counterparts with supported tags. It refuses unsupported or missing evidence rather than treating it as safe to mutate. File identities and selected provider/rollout values are rechecked across backup and rewrite boundaries, including WAL-backed value changes.

The operator closes Codex and chooses `--to`; the tool does not modify provider selection. JSON mode requires `--yes` and keeps stdout results separate from stderr progress. Backup/rewrite use existing retag primitives, including JSONL hard-link/copy and SQLite snapshot/copy fallback.

There is no cross-file transaction. On partial failure, backups remain and the error identifies the retained location. Automatic rollback would overwrite external writers, so restoration is manual and the guide explains its scope. Verification is synthetic Windows/local evidence, not a live Codex home, native Docker/WSL, provider, cloud, release or production claim.
