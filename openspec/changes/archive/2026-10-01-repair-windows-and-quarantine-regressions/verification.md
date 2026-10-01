# Verification: repair-windows-and-quarantine-regressions

## Completeness

8/8 tasks complete for local implementation and evidence recording. The three declared capabilities are synced with main specs. The remaining publication/cloud verification is explicitly recorded as an operational prerequisite, not falsely marked executed.

## Correctness

- F-005: deterministic durable-first Responses route reproduction failed with `1599.960518360138 == 700.0` before helper fix, matching the failing assertion/value class in historical integration-core-1. The helper now reports local evidence expiry. Both orderings and partial failures retain the original terminal deadline/ownership assertions. 69 quarantine integration cases pass; production quarantine unchanged.
- F-011: 10 baseline Windows failures resolved; 16 diagnostics tests pass, including both platform path flavors and absolute identity outside the root. Architecture thresholds and continued independent failure reporting preserved.
- F-008: all four source-validation events configured on Windows with read-only permissions. Local frontend/wheel build, fresh no-cache/copy installation and installed CLI outside checkout passed version/source parity, readiness, HTML/JS/CSS and cleanup. Missing/non-success/stale/PR-only workflow evidence rejects fork publication. 93 release/portability/launcher tests pass.
- Total focused tests: 178 passed. No full repository suite launched.
- Ruff check/format for six changed Python files, scoped ty for checker/gate, actionlint 1.7.12 for both workflows, architecture and simplicity pass. Strict change validation and 68 main specs pass. git diff --check passes.

## Coherence

Small checker formatting fix, shared fixture repair and workflow/gate changes match the design. No new config, dependency, behavior version or database migration. Main proxy-architecture/github-automation/release-management specs and contexts are synchronized. Changelog untouched; previous local edits preserved.

## Evidence limitations

Actual manual Windows run https://github.com/Frozen811/codex-lb/actions/runs/36874316285 passed at published main `7ec39f82709ee1ca4c00489a8d5fc301d49320ed`, confirmed by API. It ran the old import-only smoke, not the edited workflow. New exact-source automatic Windows/cloud quarantine runs await source publication. This change is locally verified; no cloud merge/release readiness asserted. No commits, push, tags, registry publication or deployment performed. Release remains blocked by actual-source prerequisites.

No local correctness/coherence blockers remain. OpenSpec CLI instructions warn about the pre-existing unknown `context_docs` rules artifact; strict validations themselves pass.
