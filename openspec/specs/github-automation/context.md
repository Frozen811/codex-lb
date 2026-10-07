# Context: github-automation

## Conservative PR area detection

The area detector validates the API's file inventory against the event's changed-file count before using it to skip expensive checks. Rename origins are additional filter inputs, not extra changed-file records. Missing counts, malformed/duplicate entries, pagination cycles, API failures or the documented 3000-file API ceiling select the full suite using the existing CI workflow path. Workflow, selector, shared API helper and line-ending policy edits also select every area.

Nix consumes application/configuration sources, frontend inputs, README/LICENSE and the two dashboard build helpers. Its filter includes those inputs rather than only flake/lock files. For example, moving `app/example.py` into `docs/example.py` still runs backend, Docker and Nix checks; editing an ordinary docs page stays selective. More CI on shared inputs is preferred to a successful placeholder check that never validates the affected package.

Reference: [GitHub PR files API](https://docs.github.com/en/rest/pulls/pulls#list-pull-requests-files). Requirement: [CI area detection includes complete change evidence](spec.md#requirement-ci-area-detection-includes-complete-change-evidence).

Normative requirements live in [`spec.md`](./spec.md). This document currently
covers the Simplicity budgets check and the Release guards workflow; the
codex-review label-sync machinery is summarized in the spec's Purpose.

## Simplicity budgets check

### Purpose

Make the simplicity effort self-enforcing. The `contribution-simplicity`
principles and the docs-site diet (`user-documentation`) shrink the entry-point
documents; the budgets check is the mechanical gate that keeps them shrunk.
Budgets live in data (`.github/simplicity-budgets.toml`) so every increase is a
one-line, reviewable diff rather than an argument.

### Decisions

- **Separate workflow, never ci.yml.** The workflow triggers on
  `labeled`/`unlabeled` so a just-applied override label re-evaluates the check
  immediately. Adding those types to ci.yml would re-run the entire sharded CI
  matrix on every `🤖 codex: ok` label sync from `codex-review-labels.yml`
  (15-minute cron + `workflow_run`). The standalone budget job costs seconds.
- **Labels are fetched live from the API, not the event payload.** Fork PR
  payloads and re-runs of old runs can carry a stale or empty label set; the
  workflow queries `/issues/<n>/labels` at run time (permissions:
  `pull-requests: read`) and passes the result to the script via `PR_LABELS`.
- **No `paths:` filter.** The job is cheap, and a required check behind a
  workflow-level paths filter would leave non-matching PRs pending forever
  (ci.yml solves this with the dorny-filter placeholder pattern — overkill
  here).
- **Stdlib-only script, plain `python3`.** Matches the
  `scripts/guard_beta_release.py` convention: runs before any dependency
  install; `tomllib` is stdlib on the runner's Python 3.12.
- **All-contributors block excluded from README counts.** The generated table
  between the `ALL-CONTRIBUTORS-LIST:START/END` markers is bot-managed, not
  hand-written complexity; counting it would make the line budget
  arithmetically impossible.
- **Exit 2 on missing nav target.** The nav budget reads `CORE_NAV_ITEMS` from
  `app-header.tsx`; the checker refuses to pass silently when the configured
  array vanishes, forcing any nav refactor to repoint `[core_nav]` in its own
  diff. Intentional coupling, not an accident. The same fail-loud exit 2
  covers a missing or malformed `.github/simplicity-budgets.toml` and an
  unclosed `ALL-CONTRIBUTORS-LIST` block (whose tail would otherwise be
  silently excluded from the count).

### Label caveats (operational)

- **Re-run after labeling works.** Because the label set is fetched live at run
  time, adding `simplicity-budget-approved` and then re-running the failed run
  picks it up; applying/removing the label also fires a fresh
  `labeled`/`unlabeled` run on its own. The failure message says exactly this.
- **merge_group and push carry no labels.** The override is a review-time
  acknowledgment only. If a PR would leave `main` over budget, the label cannot
  save the merge queue or the post-merge push run: the budget number in
  `.github/simplicity-budgets.toml` must be raised in the same diff.
  Alternative considered and rejected: skipping the check on `merge_group`
  would launder an over-budget `main` into green required checks.
- **Enforcement chain when merges bypass the queue.** With a plain required
  `pull_request` check, a maintainer-labeled over-budget PR can merge without
  the TOML bump; the very next push run on `main` then goes red, which is the
  intended alarm, not a gap: the label is restricted to maintainers, and the
  documented policy is that they either bump the TOML in the same diff or fix
  the exceedance immediately after. Hard pre-merge enforcement of the
  main-never-over-budget invariant requires routing merges through the merge
  queue (the `merge_group` run carries no labels by construction).
- **Label creation is out of band**:
  `gh label create simplicity-budget-approved` once, by a maintainer. Applying
  it is a deliberate approval act; no automation assigns it.

### Rollout

- Add `Simplicity budgets` to the required-checks ruleset only after one green
  run on `main` (GitHub cannot require a context that has never reported). It
  does not join ci.yml's `ci-required` aggregate — cross-workflow `needs` is
  impossible and the label triggers must stay out of ci.yml.

### Non-goals / deferred

- `README.zh-CN.md` is unbudgeted (banner-only treatment); a `[readme_zh]`
  section is a two-line follow-up if needed.
- A settings-count budget for `app/core/config` would need the app import
  graph (not stdlib-only) — deferred to the simplicity backlog.
- Docs-site pages are intentionally unbudgeted: depth is supposed to move
  there.

## Release guards workflow

### Purpose

`release-guards.yml` runs `scripts/guard_beta_release.py --mode pr` and
`scripts/guard_stable_release.py` for pull requests. The beta guard reads the
release PR body (checked validation checklist + exact head SHA), so it must
re-run when the body is edited. Those two jobs used to live in `ci.yml`, which
therefore had to subscribe to `pull_request: edited`.

### Decisions

- **Separate workflow, never ci.yml — same reasoning as Simplicity budgets.**
  `ci.yml` uses a per-ref concurrency group with `cancel-in-progress: true`, so
  every PR title/body edit cancelled the in-flight matrix and re-queued ~30
  jobs for an unchanged head. On 2026-09-08 eight campaign PRs each lost at
  least one run this way (runs 34216592285, 34216916484, 34217216971,
  34218615301, 34223748971, 34223782953, 34225099491, 34226177365,
  34226719090 all show `cancelled` for the head that later went green) and the
  runner queue was starved for hours. Agents finalizing descriptions after a
  push and review bots rewriting summaries both PATCH the body. The guards are
  stdlib-only and finish in seconds, so re-running them per edit is free.
- **Remove `edited` from ci.yml instead of skipping jobs on it.** A
  `github.event.action != 'edited'` condition would still create a new run in
  which every heavy job reports `skipped`; branch protection reads the newest
  check run per context and treats skipped as satisfied, so a body-only edit
  could turn a red or untested head green. Not triggering at all leaves the
  head's existing check runs authoritative. `tests/unit/test_ci_workflow_required_checks.py`
  pins both halves of this decision.
- **Check context names unchanged.** `Beta release guard` and
  `Stable release guard` report exactly as before. They no longer feed
  `CI Required` (cross-workflow `needs` is impossible). Neither the guards nor
  `CI Required` are in the `protect main` ruleset today, so no enforcement was
  removed; the publish-time guard in `publish-beta-release.yml` is the hard
  gate for tags. To make the beta guard a pre-merge hard gate, require
  `Beta release guard` in the ruleset directly.
- **`push`/`merge_group` kept.** The guards are no-ops without a
  `pull_request` payload, but keeping the events preserves parity with the old
  placement and gives the contexts a report on `main` (a context that has never
  reported cannot be added to the ruleset).

### Failure modes

- A base-branch retarget also arrives as `edited`; it now re-runs only the
  guards. A push or manual re-run refreshes the matrix, and the merge queue
  runs the full suite regardless.
- If the guards ever need the matrix result, do not fold them back into
  `ci.yml`; gate on the separate contexts instead.

## Windows startup regression

The Windows workflow runs for main pushes, pull-request source updates, merge-group candidates and manual dispatches, with one stable job and read-only contents permission. No workflow path filter can leave this candidate untested. Changes to PR text do not restart it. Pinned checkout/setup actions, Python 3.13 and Bun 1.3.14 match the tested release tooling.

It checks memory monitoring, architecture diagnostics and launcher contracts, builds dashboard assets and a wheel, installs into a fresh environment under RUNNER_TEMP, and invokes the shared release smoke outside the checkout. PowerShell checks each native-command exit before proceeding. The smoke uses temporary storage and a random loopback port, checks runtime/distribution/source identity, readiness and HTML/JS/CSS, and terminates its process tree.

Example: an import-only check would miss an unusable lifespan or missing dashboard assets; the installed-wheel smoke fails those candidates. A manual run on published main is baseline evidence only, and the fork release gate requires a successful automatic main-push run at the exact candidate SHA. This is startup/package coverage; real Codex routing, OAuth and Windows network transport still need their own tests.

## Changed OpenSpec validation

Issue #2032 exposed that canonical-only validation accepts malformed active deltas. The required OpenSpec job also runs `.github/scripts/validate_changed_openspec.py` against GitHub event revisions. PR selection uses the merge base and event head, while validation runs in the normal merge checkout. A target-only invalid change added after a PR branches does not enter that PR's validation set.

Full history makes the merge base available. Disabling rename detection includes both old and new paths; surviving folders are validated, fully removed folders and archive paths are skipped. Strict validation is limited to touched active folders because unrelated legacy deltas can still be invalid. Validator arguments terminate options before the folder name, so a folder named `--help` cannot skip validation.

## Parallel test execution

Pytest uses `-n auto --dist=loadfile`: a file retains serial ordering while
independent files overlap. Automatic concurrency respects CPU affinity, Linux
cgroup quotas and available memory, including Windows GlobalMemoryStatusEx.
Workers resolve database URLs before application imports and keep encryption
keys in their own temporary directory. SQLite uses writable `/dev/shm` on Linux
or the platform temporary directory. PostgreSQL/MySQL use disposable databases
with a run-specific worker suffix; the controller provisions and removes them,
including databases belonging to crashed workers. The test user needs create/drop
permission, and MySQL CI grants only the test namespace. A killed controller can
leave abandoned test databases. DDL and multi-session commits remain real rather
than being hidden by an unconditional rollback fixture.

Hypothesis `local` and deterministic `ci` profiles use 50 examples; `thorough`
uses 500. Explicit per-test budgets remain intact. Vitest uses isolated threads
with bounded concurrency and resets mocks, timers, handlers and mutable browser
state. Multipart tests install Node Blob/File before loading Undici's request
constructors. Modal interaction waits for Radix's pointer-ready layer.

The first full cloud run exposed another scheduling assumption in the API-key
integration flow: a visible create button can still be disabled while its data
loads, and table updates can precede release of a closing modal's pointer lock.
Those tests now wait for the enabled button, interactive dialog layer and modal
removal before continuing. Dialog queries are scoped to the active modal, and
typing avoids artificial per-character timer delays. Assertions, the 15-second
test timeout and the 70% coverage thresholds remain unchanged.

The CRUD integration flow enters complete names with a paste interaction so
coverage does not rerender the full form once per character. Creation and
editing/deletion are independent flows with fresh mock state, retaining all
behavioral assertions within the existing timeout. Their visited lazy route is
imported before test execution so cold coverage transforms do not consume the
interaction budget; the real App and route guards still run. Live-reset tests
freeze the domain freshness clock during their 240-write history-retention
exercise, then advance it explicitly for the expiry assertion. PostgreSQL query
plan assertions run after the parallel database slice, avoiding concurrent
transaction/visibility effects on VACUUM and planner costs; all plan assertions
remain mandatory. Windows release smoke waits up to 15 seconds for transient
sharing violations during temporary storage cleanup after process termination.
Other cleanup errors and locks that remain past the deadline still fail smoke.

Issue-labeler contract cases share one module-scoped Node execution with a
60-second process deadline. Each event receives fresh labels, API mocks and
context, and each parameterized assertion still checks the real workflow script.
This removes eight redundant runtime startups and allows a cold Node process to
start under parallel runner load without relying on a ten-second timing budget.

The six integration-core shards use recorded file durations when supplied and
static estimates otherwise. All runners use the same snapshot; JUnit artifacts
can refresh it after a complete run. Verification prevents duplicate, missing
or empty assignments. The frontend producer publishes one dashboard artifact
for pytest, Playwright and packaging consumers. PR frontend checks omit coverage;
main/merge-queue checks retain it. Required pytest placeholder contexts survive
a skipped producer. Local build reuse hashes source, configuration and public
assets, then validates dashboard completeness before reusing the bundle.
The unit CI slice pins Helm 3.19.0 for deployment checks, matching the verified
local tool version rather than relying on the runner image's tool inventory.

PowerShell and Linux can run the same direct commands:

```powershell
uv sync --dev --frozen
uv run --no-project python -m scripts.build_test_dashboard
uv run --no-sync pytest -n auto --dist=loadfile tests/unit
uv run --no-sync python .github/scripts/pytest_shards.py --shard-count 6 --verify
```

## MySQL CI sharding

The MySQL selection lives in `.github/pytest-mysql-targets.txt`: whole files and
specific nodes retain the previous suite's scope, including its root-level API
file and unit-test node. The sharder groups selections by file, estimates only
selected functions for partial files, and assigns the heaviest group to the
lightest of three runners. Recorded durations override estimates. Every runner
uses the same manifest and duration snapshot; each has its own MySQL 8.4 service
and retains disposable xdist worker databases. Verification rejects empty,
missing, duplicate and cross-runner file assignments.

`make test-mysql` still runs the complete selection. `make test-mysql-1`,
`make test-mysql-2` and `make test-mysql-3` run individual shards. Each CI shard
uploads `mysql-durations-N` containing `mysql-N.xml`. Refresh the shared history
after all shards finish, then commit it for the next run:

```bash
uv run --no-sync python .github/scripts/pytest_shards.py --suite mysql \
  --durations-file .github/pytest-mysql-durations.json \
  --update-from-junit .test-results/mysql-1.xml .test-results/mysql-2.xml .test-results/mysql-3.xml
uv run --no-sync python .github/scripts/pytest_shards.py --suite mysql --shard-count 3 --verify
```

PowerShell can select a shard and pass the resulting arguments directly to
pytest without Make or Bash substitution. The configured test user needs the
existing create/drop grants for the isolated worker database namespace:

```powershell
$env:CODEX_LB_TEST_DATABASE_URL = "mysql+asyncmy://codex_lb:codex_lb@127.0.0.1:3306/codex_lb"
$mysqlTests = @(uv run --no-sync python .github/scripts/pytest_shards.py --suite mysql --shard-count 3 --shard-index 1)
uv run --no-sync pytest -n auto --dist=loadfile @mysqlTests
```

The compatibility context `Tests (pytest, MySQL)` requires a successful matrix;
failure, skip or cancellation fails it. `CI Required` waits for both the matrix
and compatibility aggregate. Backend-unrelated pull requests retain successful
placeholder contexts for all three shards. Runtime goals are measured against
GitHub timestamps after publishing, rather than asserted as timing-sensitive
tests; queueing and other suites can determine the workflow's critical path.

Cloud verification caught host-dependent paths in new sharder test fixtures;
selectors and duration keys in those fixtures now use `as_posix()` on every
platform, matching the versioned manifest. It also exposed two older timing
assumptions under parallel runner load. Browser containment assertions retry
the complete geometry check within their existing ten-second expectation
deadline after each viewport resize; persistent overflow still fails. The
bridge continuation test selects startup versus streamed failure using a probe
window equal to its unchanged ten-second request deadline (or zero for the
streamed branch), so a half-second scheduling delay cannot select the wrong
branch. HTTP status, terminal event, reservation, ownership and layout
assertions remain intact; production timing settings are unchanged.

## Quality checks within the fast CI budget

The mandatory pipeline retains its suites, three MySQL runners and existing
normal property budgets. Virtual-clock checks cover bridge startup errors at
2s minus/plus 1ms and cancellation before/after stream handoff, with quiescence
asserted before teardown. Server-database race tests park both independent
sessions after reading a reserved row, then release them together to exercise
its conditional ownership claim. SQLite keeps its real writer serialization:
a barrier inside that section would itself deadlock. Admission and terminal
replay assert the durable quota and reservation state.

Selected SSE, balancer and OpenAI request properties use `property_settings`.
Explicit budgets (including 8, 30 and 100) stay unchanged in regular runs;
`thorough` raises selected budgets to at least 500. Explicit edge examples run
in both modes. The separate `Extended Property Tests` workflow runs at 02:23
UTC or by manual dispatch, records the seed/commit before testing, prints
Hypothesis statistics and uploads seed metadata, JUnit and hidden failure
evidence on success or failure. It does not gate `CI Required`; discovered
bugs should become deterministic mandatory regressions.

For example, reproduce an artifact's seed against its recorded commit:

```powershell
uv sync --dev --frozen
uv run --no-sync pytest -n auto --dist=loadfile -m extended_property --hypothesis-profile=thorough --hypothesis-seed 20261007 tests/unit/test_sse.py tests/unit/test_balancer_fuzz.py tests/unit/test_openai_requests.py
```

The previous successful full pipeline was 6m20s. Cloud runtime is measured
again after publication; scheduled exploration has its own duration and does
not replace or shorten the full mandatory suite.

The second cloud attempt at `ee090bc6` exposed a pre-existing Firewall flow
interaction timeout under coverage (15 seconds), while all backend jobs passed.
The test now preloads the real Settings route outside its interaction body,
pastes an IP once rather than rerendering per character, and scopes the removal
query to Firewall. Its assertions additionally check the mock's persisted
add/remove state. Diagnostic plan/run MSW handlers were missing from Advanced
settings; typed deterministic fixtures and real-client contract checks now
cover them. Unknown requests still fail. This follow-up keeps the original
timeouts, coverage thresholds, real routes and file parallelism.

Focused reproduction: `cd frontend && bun run test src/__integration__/firewall-flow.test.tsx src/features/cache-probe/api.test.ts src/test/mocks/handler-coverage.test.ts`.
The full main coverage gate remains `make frontend-test`.
