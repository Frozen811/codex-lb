## Context

See proposal.md. Existing retag helpers already bound leading metadata reads to 64 KiB, preserve the transcript tail through streaming replacement, snapshot SQLite and prefer JSONL hard links. They do not provide mismatch preview or a fresh, verified repair plan.

## Goals / Non-Goals

Use one typed inspection model and the existing backup/rewrite primitives. Preserve all preceding dirty work. Do not repair a live Codex home, alter authentication or provider selection, modify protocol/catalog/pricing, or publish this batch.

## Decisions

- Add a dedicated repair module and CLI entrypoints. Preview opens SQLite read-only and never uses the retag copy fallback.
- Resolve targeted JSONL paths from SQLite rollout paths where available; otherwise discover filenames and read bounded matching headers only. Global preview reads bounded headers.
- Require one unambiguous JSONL header and at least one identified SQLite counterpart with supported provider values. Explicit `--to` chooses the canonical tag; no tag is guessed.
- Check containment, file identity and selected values before and after backup and before mutation. Reuse existing snapshots, streaming replacement and ID-qualified SQLite updates. Refuse ambiguous or unsupported inputs.
- Emit JSON stdout separately from progress stderr; reuse the existing retag progress pipe handling.
- Client examples already meet the three imported source proposals. Verify parsed values and contextual guidance independently; avoid changing working examples solely to create a diff.

## Risks / Trade-offs

Repair is not an atomic transaction across JSONL and SQLite. Codex must be closed; failures preserve a backup and report partial changes for manual recovery. Identity checks reduce stale-plan mistakes but cannot synchronize with an uncooperative external writer. Filename discovery is required when an older SQLite schema lacks rollout paths. Native WSL/Docker/live-home behavior remains outside synthetic Windows verification.
