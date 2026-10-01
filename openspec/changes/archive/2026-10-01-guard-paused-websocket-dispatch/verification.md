# Verification: guard-paused-websocket-dispatch

Date: 2026-10-01. Base HEAD: 7ec39f82709ee1ca4c00489a8d5fc301d49320ed; this change builds on the prior uncommitted continuity fix. No commit, push, workflow dispatch or deployment.

## Completeness

All 6 tasks are complete. The CLI synchronized the added account-routing requirement and archived the change as 2026-10-01-guard-paused-websocket-dispatch. Final post-sync strict validation: **68 main specs passed, 0 failed**.

Proposal, design, context, delta spec and implementation are present. The final account marker check is in the direct WebSocket response.create send path. It follows admission awaits and precedes dispatch binding/sent timestamp. The existing ProxyResponseError handler removes only the unsent pending state and releases its API-key reservation and create admission. No selected-account health penalty or shared-socket retirement is added.

## Correctness

Before the guard, a real Pause API returned 200 and the next /v1/responses socket turn emitted response.created instead of response.failed. This reproduced new post-Pause dispatch independently of the user's uncertain quota observation.

| Scenario | Evidence |
|---|---|
| Pause between socket turns | test_websocket_pause_blocks_new_dispatch_on_open_socket, between_turns: two ingress routes x fresh/anchored turns |
| Pause after selection during waits | Same test, first_connect and create_admission: actual account create lease and public Pause; no additional upstream frame |
| Shared socket preserves existing response | Same test, inflight: new turn refused; prior response still completes with its original ID; socket stays open |
| Peer/deleted snapshot marks | Same test, peer_pause and deleted_snapshot: native refreshed snapshot refuses stale ACTIVE account without a process-local mark |
| Cleanup and ownership | All 24 cases verify actual key reservation rows have no reserved entries and contain a released row; the last acquired create lease was released; no reconnect to another account |
| Normal reuse | Sequential reuse test still checks both dispatch-owner snapshots and exact payloads. The stub now produces each response after its corresponding send and seeds the fictional owner in the routing snapshot |

Final direct WebSocket integration file: **212 passed**. Passthrough + Codex usage + cross-replica invalidation integration files: **111 passed**. Focused ownership/admission unit set: **8 passed**. These three sets are nonoverlapping: **331 passed** in this block. Ruff app/tests, changed-file format, architecture and simplicity checks pass. Strict delta validation passes; post-sync main spec validation is recorded in issues-check.md.

## Coherence and verification corrections

The existing marker is reused with no new cache, DB read, setting, schema, health write or routing reassignment. Existing error codes and terminal cleanup remain in effect. Unrelated already-sent work stays on its account.

Transport-only tests mock accounts outside the DB. Their initial empty startup snapshot is explicitly left unseeded in a file-scoped fixture; later refreshes retain native missing-account behavior. Real-state tests seed and refresh the actual cache, including peer-only Pause and deletion, so this fixture does not bypass the new routing assertions.

An intermediate 203-pass/1-fail WebSocket run exposed a sequential stub that delivered the second response before sending the second request. Its original ownership assertions were retained, response batches were synchronized to sends, and a real routing account was seeded. The final whole-file run passed.

An intermediate neighboring run produced 101 passes/10 logging failures because the command's log_level=ERROR option filtered the INFO/DEBUG records those tests assert. Re-running without that override passed all 111 tests. These failed runs are not reported as passing.

## Limits

The user's clarified case was local quota exhaustion with about 11% remaining in the panel; version and Pause timing are uncertain. Current user-level config points generation at 127.0.0.1:2455/backend-api/codex and has no top-level chatgpt_base_url. The installed desktop package is 26.928.3736.0; that does not establish the version at incident time. Port 2455 has no listener. The default local store.db, read with SQLite mode=ro/query_only, has no accounts, request logs or Pause events, and cannot be matched to the submitted incident.

The repo documents distinct generation and usage endpoints; its captured client behavior is Codex 0.157.0. Current official configuration reference confirms separate provider/backend keys and user-level placement, but does not itself establish quota display behavior for this installed app. INC-01, INC-08 and INC-10 therefore remain open pending actual client/server request correlation. Account credentials and encryption keys were not read, and the client config was not modified. This change does not cancel already-sent work or prove quota cannot change after Pause.

Official reference: https://learn.chatgpt.com/docs/config-file/config-reference
