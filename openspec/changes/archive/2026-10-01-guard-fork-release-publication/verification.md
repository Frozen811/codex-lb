# Verification: guard-fork-release-publication

## Completeness

All six implementation tasks completed locally. Three added normative requirements map to source gating, archive/image identity and publication/failure ordering. Root installation audit section 15 covers the user's expanded scope without marking untested installation paths complete.

## Correctness

- Exact-source gates: 54 new cases within 115 passing focused release tests cover supported channels/tags, newest failed/pending/cancelled/skipped runs, wrong SHA/event/branch/path, tag/main movement, current-attempt CI aggregate, release metadata/assets/version regression, CLI refusal outputs, archive corruption/worktree/version drift, startup reset/early server exit and publisher reachability/order. Source verifier used live read-only API: current main 7ec39f82 refused its completed/failure CI.
- Versions: all six managed fields verify as 1.25.1; existing release/beta/stable tests pass. No release version bump or publication.
- Artifact identity: final uv build produced 3,400,427-byte wheel and 4,430,777-byte sdist with exact app/frontend/managed-source parity; zero .kilo worktree entries. Historical public sdist contains 5967 such entries and historical packages contain runtime 1.25.0-beta.9 under metadata 1.25.1.
- Installation: clean wheel and separately rebuilt no-cache sdist passed installed distribution/runtime/source hashes, CLI outside checkout, temporary DB and readiness/dashboard/JS/CSS. A cached installation's NUL-filled main.py was rejected; root cause remains unknown. Windows spawned launcher/interpreter cleanup now succeeds.
- Image: main Dockerfile built linux/amd64; image 95f4eb8ff34bfb2aadef80bec672d172dda1f94ee4349532496e99937740cae4 reports 1.25.1 and explicit local-uncommitted revision. Temp-container smoke passed with tmpfs and random loopback port. This is local source evidence, not a released source SHA.
- Workflow: actionlint 1.7.12 passed; actions pinned, gate dependency and pre-login recheck tested; no upload clobber, exact tags before stable aliases, failure/cancellation cleanup reachable. Optional shellcheck/pyflakes were disabled in actionlint; Python verified with Ruff.

## Coherence and limits

No application settings, schema/migrations, threshold weakening or upstream publishing introduced. Canonical release preparation/review/soak requirements remain applicable. Source gate is conservative about main movement and refuses unknown evidence. GitHub/GHCR are not transactional; cleanup cannot undo all registry writes or lock future CI/main changes.

Ruff, scoped ty, architecture and simplicity checks passed. Four intermediate ty diagnostics in test fixtures were corrected; the new file was rerun with 54 passing cases (part of the 115-case set). Strict change validation passed before archive; after sync/archive all 68 main specs passed strict validation. No critical local implementation gaps found. Cloud workflow execution, registry pushes, published-artifact install, actual Codex/OAuth/network/DB/platform matrix and release recovery remain unverified and explicitly recorded in issues-check.md. Current red cloud CI prevents release; no commits/push/tags/dispatch/releases/deployment performed. Automated policy review blocked housekeeping removal of two earlier failed-smoke temporary directories; they remain, distinct from successful final process/container cleanup.
