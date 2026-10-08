# Complete fork-main publication and CI

Date: 2026-10-08, Europe/Kiev. The user explicitly authorized committing every local uncommitted path to fork main and taking full CI to success.

## Published source

- Base: `8369ec720c5ac935f7a64fe3f30aa1cbc323f5e5`.
- All original **77** paths, including the three local packages: `71c5332ca24666455aa6836f0bd05f9e8b304cc2`.
- Runtime/test/portability repair: **`cab6493b0a3cbeb6241fb455caee17dde8ddb270`**. Local HEAD, `git ls-remote fork refs/heads/main` and live GitHub branch state matched. Checkout was clean before this final evidence/archive update.

No initial local work was omitted. Auth/credit, image/compact/terminal and input/forwarding packages are included. Source rows were not silently closed beyond the already completed 15 items.

## Complete current-head cloud gate

[CI #88](https://github.com/Frozen811/codex-lb/actions/runs/37821930906), attempt **1**, head **`cab6493b0a3cbeb6241fb455caee17dde8ddb270`**, completed **SUCCESS: 35/35 jobs**, all individually completed successfully, including **CI Required**. The complete push-to-main matrix covered frontend lint/types/build/tests and real browser smoke; Python lint/types/unit/all six integration shards/bridge/E2E; PostgreSQL, three MySQL shards and their aggregates; OpenSpec; Rust tests/audit; Docker; Nix; Helm lint and kind smoke; packaging and attribution. [Machine-readable exact evidence](cloud-evidence.json) contains every job ID/status/URL.

Additional applicable workflows all succeeded: [Windows Startup Regression](https://github.com/Frozen811/codex-lb/actions/runs/37821930900) (**1** job), [Release guards](https://github.com/Frozen811/codex-lb/actions/runs/37821931286) (**2** jobs), [Simplicity budgets](https://github.com/Frozen811/codex-lb/actions/runs/37821931931) (**1** job). Total: **39/39 applicable jobs successful**.

Release Please and Sync Beta Release PR were skipped because their workflows are restricted to the upstream repository. Docs did not trigger on this repair push because no docs path changed; its first publication run completed successfully. These conditions do not stand in for any missing required CI job. Expected test-level skips for incompatible database backends, optional/native probes and existing platform controls remain explicit in the logs; job success does not claim live-provider or production acceptance.

## Failure history retained

[CI #87](https://github.com/Frozen811/codex-lb/actions/runs/37818859876) completed failure, 25/35 success, on the first publication. Its six typing diagnostics, stale Edu/compact/inventory expectations and real blank async-ID retry defect were repaired, not hidden or marked successful. Windows catalog CRLF and directory fsync plus the real-clock regression were also repaired locally without changing provenance or production budgets. Disjoint local acceptance: **579 PASS**, full ty/Ruff/format/static checks and strict 68/68 OpenSpec/MkDocs PASS.

The final archive/evidence commit changes only OpenSpec documents and registry metadata; runtime and tests remain exactly the source validated above. Its source SHA is reproducible with `git log -1 --format=%H -- openspec/changes/archive/2026-10-08-repair-local-verification-portability/publication.md`. A complete follow-up main CI is monitored on that final metadata commit before reporting task completion.

The original source queue remains **338 records: 121 local closures, 7 partial, 210 unverified**. Existing F-045/CI-04 and public/provider/production residuals remain scoped independently. No release, tag or deployment was performed.
