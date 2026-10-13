# AGENTS

## Environment

- Python: `>=3.13` via `uv` (`uv sync --frozen`; interpreter at `.venv/bin/python`)
- GitHub auth for git/API is available via env vars: `GITHUB_USER`, `GITHUB_TOKEN` (PAT). Do not hardcode or commit tokens.
- For authenticated git over HTTPS in automation, use: `https://x-access-token:${GITHUB_TOKEN}@github.com/<owner>/<repo>.git`

## Code Conventions

The `/project-conventions` skill is auto-activated on code edits (PreToolUse guard).

| Convention | Location | When |
|-----------|----------|------|
| Code Conventions (Full) | `/project-conventions` skill | On code edit (auto-enforced) |
| Git Workflow | `.agents/conventions/git-workflow.md` | Commit / PR |

## Workflow (OpenSpec-first)

This repo uses **OpenSpec as the primary workflow and SSOT** for change-driven development.

### How to work (default)

1) Find the relevant spec(s) in `openspec/specs/**` and treat them as source-of-truth.
2) If the work changes behavior, API/CLI/dashboard/operator/compatibility contracts, routing, or schema: create an OpenSpec change in `openspec/changes/**` first (proposal -> tasks).
3) Implement the tasks; keep code + specs in sync (update `spec.md` as needed).
4) Validate specs locally: `openspec validate --specs`
5) When done: verify + archive the change (do not archive unverified changes).

### Source of Truth

- **Specs/Design/Tasks (SSOT)**: `openspec/`
  - Active changes: `openspec/changes/<change>/`
  - Main specs: `openspec/specs/<capability>/spec.md`
  - Archived changes: `openspec/changes/archive/YYYY-MM-DD-<change>/`

## Documentation & Release Notes

- **OpenSpec is the SSOT for feature/behavior documentation.** User-facing rendering lives under `docs/` (the published docs pages), and each spec-governed page MUST link back to the owning `openspec/specs/<capability>/` entry. Do not create `docs/` content that has no OpenSpec counterpart, and do not add feature docs as new README sections. Keep normative requirements in `openspec/specs/<capability>/spec.md` and free-form rationale in the capability's `context.md` (or change-level context under `openspec/changes/<change>/context.md`).
- **Do not edit `CHANGELOG.md` directly.** Leave changelog updates to the release process; record change notes in OpenSpec artifacts instead.

### Documentation Model (Spec + Context)

- `spec.md` is the **normative SSOT** and should contain only testable requirements.
- Use `openspec/specs/<capability>/context.md` for **free-form context** (purpose, rationale, examples, ops notes).
- If context grows, split into `overview.md`, `rationale.md`, `examples.md`, or `ops.md` within the same capability folder.
- Change-level notes live in `openspec/changes/<change>/context.md` or `notes.md`, then **sync stable context** back into the main context docs.

Prompting cue (use when writing docs):
"Keep `spec.md` strictly for requirements. Add/update `context.md` with purpose, decisions, constraints, failure modes, and at least one concrete example."

### Commands (recommended)

- Start a change: `/opsx:new <kebab-case>`
- Create artifacts (step): `/opsx:continue <change>`
- Create artifacts (fast): `/opsx:ff <change>`
- Implement tasks: `/opsx:apply <change>`
- Verify before archive: `/opsx:verify <change>`
- Sync delta specs → main specs: `/opsx:sync <change>`
- Archive: `/opsx:archive <change>`

## Contributing & Merge Gates

When authoring or merging a PR (as a human contributor, a collaborator,
or an AI assistant acting on behalf of either), the binding workflow is
in [`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md). The sections
an AI assistant most often needs are:

- [Merge gates](.github/CONTRIBUTING.md#merge-gates) — CI green +
  actionable CodeRabbit findings addressed + `mergeable=CLEAN` +
  OpenSpec change folder for behavior changes + `Fixes #N` /
  `Closes #N` for issue cover + the six simplicity rules
  (PRINCIPLES.md P1-P6; see
  [Simplicity gates](.github/CONTRIBUTING.md#simplicity-gates)).
- [Collaborator rules](.github/CONTRIBUTING.md#collaborator-rules) —
  no self-merge by default; large PRs get split (≈1-concern per PR,
  ~800 net lines / scoped capability ceiling).
- [Bus factor escape hatch](.github/CONTRIBUTING.md#bus-factor-escape-hatch)
  — self-merge allowed after **14 days** with all gates met and a
  comment invoking the clause.

An assistant preparing a merge MUST verify the gates against the
actual GitHub state (status check rollup, current-head CodeRabbit review
threads, `mergeable` field) rather than asserting them from local history.
Local `uv run pytest` / `uv run ruff` / `codex review --base origin/main`
are encouraged but not substitutes for the cloud gates.

## PR Readiness / Review Trapdoors

These rules encode recurring review blockers observed across codex-lb PRs.

- Follow the OpenSpec-first workflow above for behavior changes. Run strict
  change and canonical-spec validation before calling a PR ready; code/tests
  alone do not satisfy this gate.
- CodeRabbit review state must come from current-head GitHub evidence.
  Unresolved, non-outdated actionable review threads block readiness until
  their findings are fixed or explicitly addressed or dismissed in-thread;
  a top-level summary does not override active thread evidence.
- Proxy failover and retry patches must prove account ownership and settlement
  invariants. File-pinned requests must not cross accounts; API-key reservations
  must settle before error-health writes; excluded accounts must actually leave
  the selection loop; idle disconnects must not mark otherwise healthy accounts
  unhealthy; security/trusted-access routing must degrade only along the
  documented path.
- Async, fan-out, and session-lifecycle patches must prove task ownership and
  cleanup. Do not share one `AsyncSession` across concurrent tasks; cancel or
  await spawned tasks on failure; preserve finalization/settlement paths after
  partial errors; bound fan-out; and test partial-failure behavior, not only
  the all-success path.
- Database migrations must prove Alembic graph and data hygiene. New revisions
  must sit on the current intended parent with a single-head upgrade path, have
  downgrade/upgrade coverage where the project expects it, and include
  historical-row backfills or compatibility handling when new fields affect
  existing data. Fetch `main` and run `make lint`
  (`scripts/check_migration_topology.py`) after adding a revision: it fails on a
  forked graph, on a revision whose parent `main` has already built on, and on a
  timestamp slot another revision already took.
- Issue-resolving PRs must name the exact `Fixes #N` / `Closes #N`, or state
  that they are partial. Keep PRs one concern wide. Revive stale work by making
  a focused branch on current `main`; do not drag an old broad/conflicted branch
  forward unless the maintainer explicitly wants that shape.
- Bug fixes need regression coverage at the externally failing product path:
  route, bridge, websocket, CLI, schema, dashboard UI, or migration path as
  applicable. Helper-only tests are not enough when the failing surface is
  elsewhere.
- Compatibility work must verify canonical and equivalent paths, trailing slash
  behavior, external error envelopes, env-var semantics, and response-schema
  contracts. Update OpenSpec/context and tests together so docs cannot promise
  behavior the code does not implement.
- Simplicity gates are a merge gate (`PRINCIPLES.md` +
  [CONTRIBUTING.md Simplicity gates](.github/CONTRIBUTING.md#simplicity-gates)).
  New features must default off or work zero-config; new `CODEX_LB_*` settings
  need a why-not-a-default justification in the PR body; README top-level
  sections, `.env.example`, and dashboard core-nav items are budgeted per
  `.github/simplicity-budgets.toml` and exceptions need the maintainer-applied
  `simplicity-budget-approved` label; feature documentation goes to `docs/` +
  openspec (never new README sections); dashboard-visible PRs include
  before/after screenshots.

## Astra Prompt Guidance & Agent Execution

When acting as an AI coding assistant (such as GPT-6 Astra or other frontier models) in this repository:

- **Autonomy & Decisiveness**: Do not pause for intermediate conversational confirmation on planned or agreed implementation steps. Complete code edits, test additions, and spec synchronization end-to-end.
- **Bounded Ownership**: Complete the requested scope, preserve unrelated dirty work, and record any remaining limitations. An explicitly sized `issues-check.md` batch owns exactly that number of selected rows; update and reread their evidence before reporting completion. Commit, push, merge, release and deployment require the user's authorization; local verification does not establish hosted CI or production results.
- **Scope-Bounded Verification**: Run focused, targeted tests covering the modified subsystem (e.g. `uv run pytest tests/unit/test_<area>.py`) and linters (`uv run ruff check`) rather than launching expansive full-repository test suites for minor changes.
- **Test Database Isolation**: `tests/conftest.py` configures disposable test storage through `tests/runtime.py` before importing application modules that initialize database engines. Preserve this order in new harnesses and subprocess tests. Run documented test commands and fix failures caused by the requested change without seeking approval for each run; never substitute an application or production database for a test fixture.
- **Request-Path Coverage**: Cover each affected public HTTP, native WebSocket and HTTP-bridge entrypoint, including applicable aliases, external error envelopes and partial-failure cleanup. Use the changed transport's existing regression suites; helper-only assertions do not prove a failing product path.
- **Simplicity Alignment**: Follow the repository simplicity gates (P1–P6) without introducing unnecessary configuration surface. Apply the OpenSpec and documentation model above.

These ownership and verification boundaries follow [OpenAI's Astra prompting guidance](https://developers.openai.com/api/docs/guides/latest-model#prompting-best-practices) and [guidance on maintaining agent instructions](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra). Repository-specific workflow and merge gates remain authoritative.
