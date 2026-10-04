## 1. Windows route recovery (UP-ISSUE-2456)

- [x] 1.1 Add red-before tests for typed 1231/1232 and endpoint-attributed 64/121; run the focused Windows classification and route tests.
- [x] 1.2 Correct the Windows error set; verify safe same-account connector retry, unsafe replay refusal, real shared-client retirement and account health neutrality.

## 2. Native account isolation and cleanup (UP-ISSUE-2471 / UP-ISSUE-2470)

- [x] 2.1 Verify real helper HTTP/2 connections are separate across accounts and reused within an account; abort one connection and require the peer to complete.
- [x] 2.3 Preserve typed native failure diagnostics through the service log boundary; verify body-read phase/detail/exception/status in the real database without altering SSE bytes or authorizing replay.
- [x] 2.2 Verify actual Responses routes after repeated native EOF/body failures release real account admission state and API-key reservations, allowing later success at cap one.

## 3. Completion

- [x] 3.1 Sync owning specs/context, run focused Python/Rust tests, lint/format and strict OpenSpec validation (split-process final coverage; aggregate instability recorded).
- [x] 3.2 Review requirements against observed evidence, preserve unrelated changes, update all three registry rows and summary, then archive the verified change with explicit residual scope.
