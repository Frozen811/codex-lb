# Verification: repair-continuity-owner-snapshots

Date: 2026-10-01 (Europe/Kiev). Baseline: 7ec39f82709ee1ca4c00489a8d5fc301d49320ed plus local working-tree changes. No fixing commit or new cloud CI exists.

## Completeness

The proposal, delta spec, design, context, implementation and focused regression coverage are present. Candidate lifetime, typed scope, service-domain boundaries and required-owner policy extraction are implemented. Audit results and publication limits are recorded in issues-check.md. After local verification, the CLI synchronized the modified requirement and archived the change as 2026-10-01-repair-continuity-owner-snapshots. Post-sync strict validation passed for all 68 main specs. All 10 tasks are complete.

## Correctness

| Contract/scenario | Implementation and verification |
|---|---|
| Readable owner candidates after teardown | list_continuity_owner_candidates clones within the real repository session; test_candidate_snapshots_survive_real_repository_teardown verifies the original row is expired/detached while the returned snapshot remains readable |
| Sole owner and scoped key | Public HTTP stream/non-stream and compact forwarding tests; test_v1_responses_owner_miss_forwards_to_sole_assigned_account covers a real key and unrelated account |
| Empty scope and listing/attribute errors | Real-session empty scope; real key loses its assigned account while another account remains; public HTTP/compact/WS refusal tests; resolver exception and attribute failure unit tests |
| Model/routing eligibility cannot infer ownership | Unfiltered repository list; active plus paused ambiguity tested across HTTP/compact/direct WS |
| Paused sole candidate cannot dispatch | Public HTTP, compact and WS use real paused account state and actual selection; no upstream callback executes. Existing compact no_accounts 503 envelope is preserved |
| Codex affinity cannot bypass unknown-owner refusal | Direct WS initial ambiguity/listing error, plus ambiguous_reuse on a previously opened healthy socket; the second anchored request never reaches upstream |
| Known owner priority/conflicts/open owner socket | Existing owner/conflict/select-account unit tests and transport regressions, including recorded previous-response owner, same-owner selector bypass, file/turn-state conflicts and scoped restart refusal |
| Owner/ring errors | Existing error paths remain unchanged; fallback is reached after a successful lookup miss and catches listing/attribute errors. Bridge takeover/source transport policy is outside this change |
| Architecture | Resolver is owned by service support; policy validation is owned by private sticky selection using SelectionInputsProtocol. No deleted-module consumers remain; checker passes at 3021/3021 lines without changed thresholds |

Successful nonoverlapping focused sets: continuity unit 11, ownership/selection unit 233, HTTP/WS integration 76, sticky/OpenAI compatibility integration 13: **333 passed**. Unit sets use mocked upstreams plus explicit real session teardown; integration sets use real test DB and public routes with controlled transport stubs. Ruff app/tests and changed-file format checks pass, architecture check passes, simplicity budgets pass, delta validation passes, 68 main specs validate strictly before sync. Final post-sync spec validation is recorded in the audit completion entry.

## Coherence

The #2274 bounded inference is documented rather than silently changing test expectations. The original patch is adapted, with real session and public-surface proof beyond its mocked clone test. Old transport-only fixtures explicitly provide a sole possible owner when exercising upstream error normalization with an unknown anchor; actual ambiguous and empty pools have separate negative coverage. Source-model transport guards, settlement and ownership conflicts retain their existing paths. Candidate enumeration does not claim to freeze account status or cancel previously started work after Pause.

The refreshed graph confirms compact, streaming retry and direct WebSocket depend on support.resolve_continuity_owner_candidate. A spurious graph edge from logger.warning to an unrelated frontend translation symbol was disregarded after reading the actual source; no frontend change is involved.

## Remaining evidence and unrelated findings

- No critical local issue remains in this change's runtime scope. No claim of PR/release readiness: current GitHub CI still reports failure on the old HEAD; current-head cloud checks and actual artifact validation require a separately authorized commit/push and release workflow.
- Windows diagnostic tests independently produce 4 passed / 10 failed because unchanged checker paths use backslashes. Both the checker and its diagnostic test file were compared to HEAD and are unchanged. Record F-011 separately; do not treat the broader interrupted/failing test runs as green.
- A 35-second test timeout interrupted a sticky scope-restart test with its existing 75-second request budget; the unmodified test passed separately in 76.19 seconds with a 100-second harness limit.
- Quarantine F-005, Docker tag mismatch F-010 and publication gate F-006 remain open. Routing/Pause incidents INC-01/INC-08 need live client/log/measurement correlation. MySQL/PostgreSQL and published-image runs have not been repeated for this local patch.
