## Verification: repair-audit-and-ci-evidence

Date: 2026-10-02. Baseline checkout HEAD: `f52adb7274c96c0702e19aa02eabd4f1c7556231`; implementation is an uncommitted working-tree delta on top of the pre-existing INSTALL-12/13/14 changes. No new cloud CI, publication or deployment is claimed.

## Completeness and correctness

Five changed requirements, thirteen scenarios; all implementation/scenario mappings are covered as below. All seven tasks are complete; requirements/context synchronized to main specs and the verified change archived. No critical or warning-level implementation divergence identified.

| Requirement | Evidence |
|---|---|
| CI area detection includes complete change evidence | Detector CLI regressions in `test_github_ci_scripts.py`: rename origin, two-page response, incomplete count, missing/invalid count, API 3000-file ceiling, malformed/duplicate entries, malformed rename, pagination cycle, later-page API outage, full selection for selector/workflow/line-ending policy edits, Nix package inputs, selective ordinary docs and empty PR. |
| Documentation site builds strictly and deploys from main | `test_fork_automation_scope.py` checks fork identity, pinned metadata action, main-only Pages read and enablement disabled, strict build and scoped deployment permissions. Actual strict rendered builds pass with default fork URL and `https://docs.example.test/custom/codex-lb/`; emitted canonical, edit and spec links checked in generated HTML. A disposable broken internal link is rejected with exit 1; deployment condition unchanged. |
| Docs pages link their governing OpenSpec capability | All owning-spec tree/blob links under docs target the fork, including root spec index. Settings reference generator remains in sync via `test_settings_reference.py`; regeneration does not restore upstream ownership. Upstream issue/author links remain attributed to their original owner. |
| Verification claims identify their evidence scope | Independent regex recount confirms distinct `(type, number)` URL records: 120 issues, 128 PRs, 49 discussions = 297. Historical category sums are 158/184. README and community completion/quality totals removed, historical markers explicitly attributed, audit remains open. No current-open-GitHub-count inference or aggregate verified-fix count is invented. |
| Upstream release automation has repository-scoped cleanup | Workflow regressions check upstream cleanup repository condition plus failure/cancellation eligibility and upstream publisher/beta/metadata guards. Existing independent fork publisher/source-gate/withdrawal tests pass. |

## Validation

- Baseline reproduction: new detector/workflow regressions produced **33 failed, 15 passed** before implementation. These were expected failures establishing the defects, not hidden final failures.
- Final focused tests: `test_github_ci_scripts.py`, `test_fork_automation_scope.py`, `test_ci_workflow_required_checks.py`, `test_fork_release_publication.py`, `test_settings_reference.py`: **143 passed**. One existing Starlette/AnyIO deprecation warning.
- Ruff check/format on the four modified Python files: **PASS**.
- Actual MkDocs strict renders for default and custom test base URLs: **PASS**; fork edit/spec links and canonical URLs checked in generated HTML.
- Simplicity budgets: README **222/225**, headings **10/10**, env **47/60**, core nav **5/5**, root **0/0**, unchanged thresholds.
- Change strict validation: CI-pinned `@fission-ai/openspec@1.11.0` **PASS**. Archive synchronized three added and two modified requirements; all **68 main specs strict PASS** after archive. `git diff --check` **PASS**.

## Coherence and limits

The detector still exposes the same seven CLI outputs; incomplete evidence selects real checks instead of successful skip placeholders. No new application setting, navigation item, README top-level section or changelog edit. README line/heading budgets unchanged.

Live read-only GitHub evidence: Pages is workflow-based; its API reports `http://extr3me.me/codex-lb/`, no configured cname and HTTPS enforcement false. The default fork Pages URL redirected to that HTTP endpoint and the fetched published HTML still contained upstream edit links. Direct HTTPS to the custom host failed. These account-level settings and deployed HTML were not mutated: the source fix governs the next docs build. The HTTPS/custom-domain issue remains open external deployment work.

Upstream release-please/beta/metadata skips are intentional, not failures to fix by enabling upstream publishing. The fix confines upstream cleanup to its owner while preserving the independent fork publisher. No workflow dispatch, commit, push, merge, tag, release or registry publication was performed.

The 297 source records are an inventory, not 297 independently verified fixes. Detailed source-author issue claims remain historical until separately checked in issues-check.md. Full original-issue behavior verification and existing artifact/architecture/platform limitations remain open.
