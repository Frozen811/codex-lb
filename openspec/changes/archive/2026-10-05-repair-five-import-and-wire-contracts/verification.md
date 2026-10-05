# Five registry records: verification and publication preparation

Date: 2026-10-05, Europe/Kiev. Base HEAD: `f987d08e69978ee6452c4e5997b11e80a81ba5f2`.
Selected exactly five initially unverified records: UP-PR-2564, UP-ISSUE-2511,
UP-PR-2517, UP-PR-2519 and UP-ISSUE-2302. Their bodies were read from GitHub;
PR heads inspected: `e20b57c0b6aba41a16a5e06bd728442c6948a585`,
`74ed0e74cdae725f97e2dd4ebee796d4fd6581f9`,
`a4bad7db5c680c3515d9048128d687ed6642b493`, respectively. All sources were open.

## Completeness, correctness and coherence

| Record | Result and evidence |
| --- | --- |
| UP-PR-2564 | Ported the focused public import dialog and its regression tests. Added a synchronous guard against overlapping submissions. One active request, ordered success, failed/unattempted suffix retry and dismissal protection pass. Accounts flow verifies the existing multipart endpoint and error/retry behavior. Chromium verifies actual filenames on the wire, Escape/close/outside guards, mobile/desktop layout and absence of overflow. Existing authorization remains in the unchanged Accounts actions and import API. |
| UP-ISSUE-2511 | Existing implementation independently verified through `test_plan_json_contracts.py`: three import aliases and five refresh cases use the actual API, loopback usage upstream and persisted SQLite. Unknown plan and conflicting workspace are rejected; credentials and identity remain unchanged. Canonical Prolite capacity and Pro-equivalent eligibility pass. |
| UP-PR-2517 | Existing family mapping independently verified through persisted request logs and TelemetrySnapshotBuilder. Two interactive CLI rows plus one exec row become 75% codex-cli; an unknown client becomes 25% other and its private name is absent from the serialized snapshot. Full telemetry module passes. |
| UP-PR-2519 | Existing complete-frame parser independently verified with real loopback WebSocket connections through both Responses routes and trailing-slash equivalents, LF/CRLF/CR boundaries, and errors before/after response.created. Public v1 gives precommit HTTP 400 or one postcommit terminal; Codex backend preserves its existing eager SSE error envelope and DONE marker. Every case completes within a five-second request bound. |
| UP-ISSUE-2302 | Existing translated names verified for all eight controls in both create and edit dialogs, with keyboard Space and visible-label click restoring the initial value. Shared form IDs now use per-form identifiers to avoid cross-form label collisions. |

All seven implementation/completion tasks and both normative requirements are
covered. Implementation follows the existing single-file mutation and shared form,
adds no settings, migration or dependency, and stores no credentials in browser
storage. The change retains the upstream focused dialog/test structure; its
additional guarding, full Accounts flow, browser wire/dismissal probes and
persisted telemetry/real WebSocket probes are local adaptations.

## Reproduction and passing checks

- Before implementation: dialog suite **2 failed, 1 passed**, proving lost second
  file and missing suffix retry. After implementation: the three-file frontend
  selection below **20 passed**, including the overlapping submission probe.
- `cd frontend; node node_modules/vitest/vitest.mjs run src/features/accounts/components/import-dialog.test.tsx src/__integration__/accounts-flow.test.tsx src/features/model-sources/components/model-source-edit-dialog.test.tsx`: **20 passed**.
- `uv run pytest tests/integration/test_five_verified_contracts.py tests/unit/test_telemetry_snapshot.py tests/unit/test_plan_types.py tests/integration/test_plan_json_contracts.py -k 'not chat_json' -q --tb=short`: **60 passed, 48 deselected**, one existing Starlette deprecation warning. The deselected Chat JSON cases belong to the preceding verified package and remain included in full CI.
- `uv run pytest tests/unit/test_sse.py tests/unit/test_plan_types.py tests/unit/test_usage.py tests/unit/test_telemetry_snapshot.py -q --tb=short`: **124 passed**, one existing deprecation warning. Counts overlap the selection above.
- Chromium `node node_modules/@playwright/test/cli.js test --config browser-smoke/import-contracts.config.ts`: **2 passed** before and **2 passed** after, at 1440 and 390px. Screenshots in `screenshots/` contain synthetic data and were visually inspected.
- Full frontend ESLint, TypeScript build and Vite production build pass.
- `uv run ruff check app tests`, `uv run ruff format --check app tests`, `uv run ty check`, proxy architecture, cancellation safety, timing seam and settings-tier checks pass.
- Strict change validation and all **68/68** main OpenSpec capabilities pass before archive. Archive synchronizes the two additions to the owning main capability.

The first route-test iteration incorrectly expected HTTP 400 on the Codex backend,
which intentionally commits eager SSE. Assertions were corrected to its existing
documented envelope. Accounts flow uses MSW's multipart request headers and
ordered responses; actual multipart filenames are verified in Chromium, avoiding
jsdom's File/body streaming limitation. Neither correction changes production
contracts or hides a product failure.

## Preservation and publication scope

Initial 148 dirty/untracked files were backed up with SHA256 fingerprints. Before
registry/spec synchronization, 144 remain byte-identical; the four intended shared
files are the three locales and frontend context. The shared locales retain every
previous inventory key. Only these five additional source rows are updated by this
batch; the other 333 records retain their prior statuses and evidence.

The user subsequently explicitly authorized publishing all three earlier five-item
packages as well as this batch, directly to the fork's main branch. The three
earlier archived verification reports retain their historical local results and
limitations. This artifact documents local completion; exact publication SHA and
full GitHub CI outcome must be verified separately after push. Real hosted
providers, production and public release artifacts are not certified by these
local tests. Broader PR 2065 remains separate.

Final preservation readback after verified archive: 142 of the 148 prior files remain byte-identical. Exactly six intended shared files changed: registry, frontend spec/context and three locales. The other 333 source rows are byte-identical to the initial snapshot. Both delta requirement blocks match the main spec exactly, all tasks are checked, archive exists, and strict main validation remains 68/68. Publication now includes all four explicitly authorized five-item packages.
