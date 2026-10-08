# Verification: bounded browser-smoke installation

Date: 2026-10-08, Europe/Kiev. Baseline: `f247f7ecbd99a2493fe60ca8b89523339277b7d0`, local and remote fork main, clean worktree. The user's standing authorization includes commit/push to `Frozen811/codex-lb:main` and following complete CI on the published SHA.

## Fresh cloud failure evidence

[CI #80](https://github.com/Frozen811/codex-lb/actions/runs/37664647751), attempt 1, finished `cancelled`. Its matrix contained **33 successful jobs**, the cancelled [Dashboard browser smoke](https://github.com/Frozen811/codex-lb/actions/runs/37664647751/job/112940979013), and one failed CI Required aggregate. Separate Windows Startup Regression, Release guards, and Simplicity budgets succeeded.

The browser log proves cache restoration completed, then Playwright entered OS dependency setup at `2026-10-07T18:10:34Z`. Ubuntu APT metadata acquisition emitted its last progress at `18:10:53Z`; the next output was cancellation at `2026-10-08T00:11:41Z`. The job had no configured timeout and reached the platform's six-hour default. This was APT setup, not a failure in the product browser tests: those tests never ran in the cancelled job. Temp files from the previous chat turn had been cleaned, so fresh API evidence was retained under `.git/codex-ci-evidence/` instead.

## Reproduction and change

Two new workflow regressions failed before the edit: the absent explicit browser job deadline defaulted to 360 minutes, and the APT configuration step was absent. The edited workflow:

- bounds the browser job to 20 minutes and its existing Playwright installation step to 10 minutes;
- installs a runner-local APT configuration with `Acquire::Retries "2"`, `Acquire::http::Timeout "30"`, and `Acquire::https::Timeout "30"`;
- retains `install --with-deps chromium` on cache hits, the real smoke command, existing job conditions, and the CI Required dependency;
- adds no continue-on-error, no skip/bypass, and no production setting or code.

## Local validation

| Validation | Result |
|---|---|
| `uv run pytest -q tests/unit/test_ci_workflow_required_checks.py tests/unit/test_github_ci_scripts.py tests/unit/test_fork_automation_scope.py tests/unit/test_postgres_ci_allowlist.py --tb=short --show-capture=no` | 74 PASS, no skips/xfails |
| Scoped Ruff check /format and `ty check` on the edited test file | PASS |
| Exact workflow configuration shell executed in disposable `ubuntu:24.04`; `apt-config dump` verified all three acquisition settings | PASS |
| Strict OpenSpec 1.11.0 change validation | PASS |
| Strict main OpenSpec validation | 68/68 PASS |
| Simplicity budgets and whitespace | PASS |

The Ubuntu image digest was `sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55`. The root-only container used a sudo shim to execute the identical configuration command; the real APT parser read the resulting `/etc/apt/apt.conf.d/` file. Input was passed as UTF-8 bytes with Linux line endings, avoiding Windows subprocess text-mode CRLF conversion. The container used no host mount and was removed automatically. This proves configuration loading, not the actual GitHub mirror network or platform deadline enforcement; the required new cloud run supplies that evidence.

## Completeness, correctness, and coherence

One added requirement with two scenarios is synchronized with the main github-automation spec and stable context. Regression checks bind finite job/step bounds, mandatory installation, normal smoke execution, and aggregate dependency. The APT runtime check validates the actual generated file through the operating-system parser. Only CI setup policy, focused tests, OpenSpec/context, and registry evidence change. All 338 source rows remain byte-identical; no sixth task is selected.

The failed/cancelled #80 result is historical. The published APT fix is `83026fba1c96636c5d71129392d23a8172365663`; it is included in the final source SHA `3205f09fa7dbd1de0d44f17c7dff5d8e138d8604`. [CI #83](https://github.com/Frozen811/codex-lb/actions/runs/37728331547), attempt1, passed all 35/35 jobs including real browser setup/smoke; separate Windows/release guards/simplicity bring the result to 39/39 applicable jobs. [Publication evidence](../2026-10-08-preserve-ready-websocket-receive-on-handoff/publication.md) records exact source/ref identity and all workflow links.
