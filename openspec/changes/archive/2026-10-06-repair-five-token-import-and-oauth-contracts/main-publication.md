# Main publication preparation

Date: 2026-10-06, Europe/Kiev. The user explicitly requested a commit in main and waiting until CI completes successfully. Publication target is **Frozen811/codex-lb:main**, remote `fork`; `origin` is upstream and is not a publication target.

The ready working tree contains the token-import/OAuth batch (UP-ISSUE-1413 / 1130 / 2442 / 2064 / 2076) and the preserved, verified voice/continuity batch (UP-PR-2562 / 2572 / 2575 / 2581 / 2583). Both complete packages, their archived OpenSpec artifacts and registry records are included. Existing partials/public/provider/platform/production limits remain unchanged.

Fresh GitHub repository/ref verification confirmed the fork default branch main, push permission and remote/local base `6ad699833b4b1c45c402eab5babbd8bf749a3754`. This is a direct user-requested main publication, without a PR, release or deployment action.

Full-repository Ruff check and format passed (1471 files). Full ty initially found one nullable argument in the new rejected-token test; an explicit assertion fixes the typing and clarifies its fixture contract. Full ty then passed. All 22 rejected-token cases passed after that adjustment. Full frontend ESLint and TypeScript passed with pinned Bun 1.3.14. Proxy architecture, cancellation, timing, settings 98/98, migration topology and simplicity gates passed. Earlier focused runtime/spec/browser evidence remains in the two verification reports.

The publication manifest records every intended source/evidence file, raw SHA-256 and Git blob identity. It excludes itself to avoid a circular fingerprint. Staged content is checked against the manifest before commit; push is ordinary fast-forward. Remote main must equal the new commit afterward.

Cloud success is not asserted by this preparation note. The exact pushed SHA, workflow/job outcomes and GitHub links are checked after publication and reported only when the complete main CI run and other applicable checks have completed successfully. Full Linux/SQL/container matrix validation belongs to that cloud run; the earlier local POSIX skip remains historical.
