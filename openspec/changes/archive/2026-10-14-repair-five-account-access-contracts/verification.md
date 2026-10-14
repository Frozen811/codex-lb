# Five account access contracts - verification, 2026-10-14

Initial HEAD: cfc939cc69e6534996365a348b74eaf414283f34, main. Initial snapshot contains 201 dirty/untracked files. Exactly five initially unverified source rows are owned: UP-ISSUE-1132, UP-DISC-636, UP-DISC-1593, UP-ISSUE-1919 and UP-DISC-884. UP-PR-1938 was examined during selection but explicitly replaced before implementation because its 68-file atomic encrypted-bundle feature is a separate concern; its registry row is unchanged. No commit, push, PR, merge, release, production migration or deployment was performed.

## Results and evidence boundary

| Row | Local result |
|---|---|
| UP-ISSUE-1132 | Existing account list/detail horizontal containment independently verified with long names/email/workspace values at 390/768/1440px. Found and fixed a related export-dialog viewport defect: its fixed dialog could exceed mobile height and leave Download outside the viewport. Explicit identity wrapping and bounded internal scrolling restore reachable Download/Close controls. |
| UP-DISC-636 | Existing export action independently verified on the actual built Accounts page. Fixed access-only export validation/rendering: null or omitted optional ID/refresh tokens no longer fail Zod or crash the dialog, missing-token copy controls are omitted, and downloaded JSON retains absent credentials. Full OAuth and OpenCode behavior continue to pass existing tests. |
| UP-DISC-1593 | Fixed opaque credential export/import identity loss by preserving explicit email, plan, workspace ID/label and seat metadata in Codex auth output. Real API imports keep two members of one workspace and the same email in another workspace separate. Targeted OAuth mismatches are rejected and a matching seat alone is replaced. This proves local identity and reauthentication isolation; live sign-outs or conversation continuation across account/workspace switching are not established. |
| UP-ISSUE-1919 | Existing Guardian/AuthManager behavior independently verified; no extra runtime change was needed. Greater-than-twelve-hour idle keepalive is separate from request freshness, active/paused admission and backoff are bounded, dynamic replicas require leadership, and stale failures cannot overwrite new credentials. Context and the registry correct the misleading inference that current Guardian removed the idle threshold. The reported daily Advanced Account Security session loss is not reproduced or claimed globally fixed. |
| UP-DISC-884 | Existing headless provider API-key flow independently verified using authorized source creation, encrypted storage, redacted list responses and actual /v1/responses dispatch through a disposable upstream without any subscription account. Access-only account export is repaired separately. Operator context explains Model Sources versus Business/PAT import: API credentials do not transfer subscription quota or bypass upstream SMS/security/entitlement gates. |

All five rows receive explicit local status with this exact evidence and retain provider/production residuals. The encrypted portable account-bundle proposal is not imported or marked verified.

## Completeness, correctness and coherence

The implementation preserves explicit identity only in the Codex-format auth object; OpenCode retains its provider-keyed output. Metadata field names match AuthFile import aliases. Frontend nullable tokens match the existing backend contract without generating credentials. Export authorization, no-cache headers and secret-free audit events remain covered by existing API regressions. No new setting, database revision or navigation entry was introduced. Two requirement deltas and five capability contexts are synchronized; the repository's 71 canonical specs validate strictly.

## Red/green and product checks

Before edits, the new real API round-trip failed because codexAuthJson had no email. Its two independent identity/source cases already passed. Both new frontend cases failed with four nullable-token Zod errors. The original built browser failed all three access-only export cases because no dialog opened. Standard OAuth export at 390px then reproduced a separate genuine defect: Download remained outside the viewport and its click/download timed out. The standard 768/1440px controls passed. These baseline failures are not counted as accepted passing tests.

Final accepted tests contain **168 distinct PASS**: 131 backend, 31 frontend and six browser scenarios. No accepted failures, skips or xfails remain. Repeated green runs and baseline controls are counted once. Test storage is initialized by tests/runtime.py through conftest before application engine imports; all credentials, accounts, keys and upstream payloads are synthetic.

1. `uv run pytest -q tests/integration/test_account_access_contracts.py tests/integration/test_account_auth_export.py tests/integration/test_accounts_backup_and_quota.py tests/integration/test_accounts_api.py tests/unit/test_account_backup_restore.py --tb=short --maxfail=3 --show-capture=no --junitxml=accounts-final.xml`: 33 PASS, 28.90s.
2. `uv run pytest -q -n 1 --dist=loadfile tests/unit/test_auth_guardian.py tests/integration/test_auth_guardian_multi_replica.py tests/unit/test_account_reauth_lifecycle.py tests/unit/test_auth_manager.py --tb=short --maxfail=3 --show-capture=no --junitxml=guardian-final.xml`: 92 PASS, 10.40s, exit 0. The first sequential run had 92 passing cases but exit 1 during Windows temporary SQLite-file cleanup (WinError32); that run is not accepted as green. The documented xdist worker invocation isolates process-owned handles and completes cleanup. No production database or harness rule was changed.
3. `uv run pytest -q tests/integration/test_oauth_flow.py -k 'targeted_reauth or keeps_same_email_distinct_upstream_identities' --tb=short --maxfail=2 --show-capture=no --junitxml=oauth.xml`: six PASS, 57 deselected, 2.49s. Deselection is the stated bounded OAuth scope, not a skip or whole-suite claim.
4. Vitest selections for account-access-contracts, auth-export-dialog, account-detail and account-list: 31 PASS, four files, final 6.67s. Includes old exports that omit metadata/optional tokens, valid access-only downloads, full OAuth and OpenCode previews/copies/downloads.
5. `node node_modules/@playwright/test/cli.js test --config browser-smoke/account-access.config.ts`: six PASS, final 10.6s. Both credential modes at 390/768/1440px cover list/detail width, dialog width, actual download/close, absent refresh-copy controls and no page errors. Production build is used. Before/after captures were visually inspected on mobile/desktop; viewport screenshots after Download confirm reachable actions. Synthetic downloaded JSON was checked for expected identity and optional credentials.

Existing Starlette/AnyIO alias deprecation and occasional SQLite lifetime-lock teardown warnings remain documented. Browser/Vite retains the existing SWC suggestion and NO_COLOR/FORCE_COLOR warning. The initial browser harness lacked a /health/ready stub; it was added for the final runs, without weakening export assertions.

## Static verification and residual

- Repository Ruff check/format PASS (1576 Python files); scoped ty PASS.
- Accounts TypeScript and scoped ESLint PASS; production Vite build PASS.
- Full frontend `tsc -b --force` remains exit 1 with three existing TS2741 errors in reports-page.test.tsx at lines 148/878/914, whose fixture literals omit upstreams. Temporarily restoring this batch's frontend files to their initial bytes reproduces exactly the same output; current source was restored with hash checks. Baseline/final full type outputs are byte-identical. This unrelated Reports fixture debt is not a sixth selected task and is not silently marked green.
- Proxy architecture, cancellation safety, timing seams, settings tiers, migration topology and static migration-duration safety PASS. Existing topology is 276 revisions and the 20261014 sticky-timing head; no revision was added and no runtime migration duration is claimed.
- Simplicity PASS: settings98/98, README218/225, headings10/10, env54/60, nav5/5 and tracked root extras0/0.
- Pinned OpenSpec1.11.0 strict change validation and canonical validation71/71 PASS. Synced delta requirement blocks occur once in their owning specs.
- Full own diff reviewed; `git diff --check` and saved-row/preservation proof are recorded in closure.json.

## Artifacts and practical limits

JUnit reports, test logs, build log, baseline/final type errors, scoped type configuration, synthetic downloads, screenshots and own diff are saved at C:/Users/ext/.codex/visualizations/2026/10/14/01a13b45-2ddd-7731-a621-fe301c3e46d1/account-access/. closure.json records exact selected-row readback and SHA256 preservation of unrelated initial dirty paths. All 354 unselected source rows are unchanged. Existing hunks in shared schema/spec/context/registry files remain intact.

Evidence is local Windows/Python, disposable SQLite, Chromium and synthetic upstreams. Live provider account/security/session policies, cross-workspace conversation continuity, real API billing/entitlement, PostgreSQL/MySQL execution, hosted CI and production are not established. Previous partials, F-045 and CI-04 retain their status.
