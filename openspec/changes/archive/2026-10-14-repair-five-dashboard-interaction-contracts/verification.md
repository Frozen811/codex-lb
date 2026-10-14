# Verification: five dashboard interaction contracts

Date: 2026-10-14, Europe/Kiev. Initial HEAD:
`cfc939cc69e6534996365a348b74eaf414283f34`, main. Exactly five initially
НЕ ПРОВЕРЕНО rows: UP-ISSUE-2418, UP-ISSUE-1946, UP-PR-2464,
UP-PR-2377 and UP-DISC-1820. Initial 102 dirty files were snapshotted before edits.

## Results by row

| Row | Result and boundary |
| --- | --- |
| UP-ISSUE-2418 | **Partial.** Existing one-time-code autocomplete, numeric input, stable label/name and outside-interaction protection independently pass component and real Chromium replacement-input tests. The native input event submits exactly one `234567` verification request without paste. No runtime OTP change was needed. The reported macOS Chrome + Apple Passwords extension interaction was not available and remains open. |
| UP-ISSUE-1946 | **Verified / closed locally.** Existing account-list containment passes at 320, 768 and 1440 pixels with 31 synthetic long names/emails. The document has no horizontal overflow, account rows have bounded internal scrolling, the last row remains selectable, and Add account stays outside the row scroller. No layout change was needed. |
| UP-PR-2464 | **Fixed / closed locally.** Added missing Compact/enter-fullscreen/exit-fullscreen translations in en/ko/zh-CN and corrected the accessible fullscreen action. Component tests verify localized state. The browser verifies ascending/descending/reset order in each compact column, stable column membership and connected row nodes, persisted Compact mode after reload, URL-backed fullscreen and preservation of `overviewTimeframe=1d`. |
| UP-PR-2377 | **Fixed / closed locally.** Consent failures now appear inline with an accessible alert, alongside the existing toast; the previous dialog itself omitted the error. Updated the concise category/exclusion/default-activation summary in all three locales. Component and browser coverage confirms collapsed exact preview, equal actions, failed disable without dismissal, retry success, and Escape dismissal remembered across reload without another preview aggregation. Backend consent defaults and payload are unchanged. |
| UP-DISC-1820 | **Fixed explanation / closed locally under the existing policy.** The previous warning implied long admin sessions without describing the locality guard. All locales now explain permitted local access, the normal 12-hour LAN/remote/proxy limit above 30 days, and existing-cookie expiry. Real authentication API tests persist both original discussion values (876000 and 8760000 hours), verify cookie Max-Age plus embedded absolute expiry for captured loopback versus LAN peers, change the saved setting without extending the issued cookie, reuse immediately before expiry, then receive 401 after expiry. This does not grant indefinite LAN sessions. |

## Final verification

**205 distinct final test cases passed: 144 frontend, 54 backend, 7 Chromium.**
The JUnit selections contain zero failures/errors/skips; browser final production
selection has seven passes, no retries. Earlier executions are not counted again.

- Frontend: 12 files, **144 passed**, 32.61s. Selected OTP/AuthGate, Accounts
  list/page, dashboard list/page/toggle/preferences, telemetry dialog/settings/flow
  and session settings. Invocation and JUnit are in the raw evidence directory.
- Backend: `uv run pytest -q tests/integration/test_dashboard_interaction_contracts.py
  tests/unit/test_dashboard_session_ttl.py tests/unit/test_dashboard_auth_api.py
  tests/unit/test_dashboard_auth_password_service.py
  tests/integration/test_five_registry_contracts.py::test_remote_admin_cookie_honors_configured_absolute_lifetime
  --tb=short --maxfail=3`: **54 passed**, 24.91s, disposable SQLite. The new
  ASGI harness uses the production raw-socket-peer capture primitive before
  invoking the real application; it does not mock the TTL resolver.
- Production browser: `bun x playwright test --config
  browser-smoke/dashboard-interactions.config.ts`: **7 passed**, 12.9s,
  against the final Vite production build and synthetic API fixtures.
- Production build including TypeScript, scoped ESLint, repository Ruff/format,
  scoped authentication ty, proxy architecture, cancellation, timing seams,
  settings tiers, migration topology, static migration safety, simplicity budgets
  and `git diff --check`: passed. Existing graph has 276 revisions and one head;
  no migration was added, and runtime migration durations were not measured.
- Strict delta validation and strict canonical OpenSpec: passed, **68/68** specs.

Existing warning boundaries: the frontend selection logs an unhandled mock request
for `GET /api/settings/runtime/connect-address`; it has no failing test. Backend
selection reports the existing Starlette/AnyIO BlockingPortal deprecation. No
claim of warning-free tests or a full-repository pytest run is made.

## Regression and harness history

The first component run had 3 failures/13 passes: two actual product regressions
(missing fullscreen labels and absent inline consent error), plus an incorrect
test label (`Verification code` instead of `TOTP code`). Corrected pre-fix selection
had 2 failures/10 passes, confirming the missing view labels and session-policy
explanation while the real replacement-input component case passed.

The initial backend selection had 2 failures/52 passes because its supposed local
request omitted the server raw-peer capture and used a non-local Host. Correcting
both to match deployed ingress made the same production locality policy pass;
no backend runtime change was made. The initial browser fullscreen assertions
entered through `/`, whose redirect dropped the test query. The final test uses
the canonical `/dashboard` URL and a valid timeframe. An intermediate frontend
aggregate had 1 failure/140 passes because an assertion expected one copy of text
shared by the description and warning; the final assertion accepts both.

## Review, scope and evidence

The source/test/spec diff was reviewed. Requirements map to public components and
the canonical authentication API; context records decisions and external limits.
No new setting, dependency, schema, navigation item, README section or changelog
entry was introduced. Discovery used a refreshed code graph, focused traces and
current source; Serena excludes frontend files, so frontend reads/edits used the
graph and native tools. Some dynamic React graph edges were checked in source.

All **101 unrelated initial dirty files** remain byte-identical. The shared
issues-check.md changes affect only the five chosen source rows plus this batch's
summary/journal; other **354** source rows remain byte-identical. Saved row status,
queue arithmetic and SHA256 preservation results are in [closure.json](closure.json).
Queue: **359 = 222 local closures + 9 partial + 2 not applicable + 126 unverified**.
All previous partials, F-045 and CI-04 remain unchanged.

Screenshots were captured before and after, including account containment at
320/768/1440 pixels, fullscreen, OTP, consent error and session-policy copy. The
320-pixel account capture and consent error capture were visually inspected.

Raw logs, JUnit, before/after PNGs and initial snapshots:
`C:/Users/ext/.codex/visualizations/2026/10/14/01a139d9-9ca7-7ad3-8968-4fabac587f80/five-dashboard-contracts/`.

Practical limits: macOS Apple Passwords remains unverified and that source row is
partial. Live providers, distributed deployments, physical browser cookie
retention over long periods, PostgreSQL/MySQL execution, cloud CI and public
artifacts are outside this local evidence. No commit, push, PR, merge, release or
deployment was performed.
