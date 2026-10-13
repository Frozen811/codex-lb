# Verification: five transport and delivery contracts

Client date: 2026-10-10. Source HEAD: `7e3779ffaea1a27c29710a7d496e8fa037131f98`, branch `main`. Exactly five selected records were initially `НЕ ПРОВЕРЕНО`: UP-PR-1084, UP-PR-2472, UP-PR-2457, UP-PR-2075 and UP-PR-1903. Current upstream metadata is recorded in [upstream-snapshot.json](upstream-snapshot.json). No commit, push, PR, merge, release or deployment.

## Contract mapping

| Record | Local result |
| --- | --- |
| UP-PR-1084 | Existing local-selector provenance is independently verified. Producer-generated 30/300-second hints fail through HTTP 503 `no_accounts` with one selection and no capacity wait on canonical and HTTP slash aliases. Canonical WebSocket emits one 503 `no_accounts` error; the unregistered WS slash alias closes 1000 without selection. Existing selection helpers preserve genuine upstream recovery, workspace spend-cap recovery and bounded hard-owner waiting. |
| UP-PR-2472 | Existing native give-up preserves the internal marker through retry gates, emits one retryable terminal with the canonical hint first, removes the internal marker/DONE, and closes the lease-holding stream chain. No-marker EOF, local refusals and non-native errors retain their behavior. Current native public-boundary, retry-wrapper and generator/lease regressions pass. |
| UP-PR-2457 | Existing typed Windows route parity is independently verified. 1231/1232 trigger account-neutral shared-transport recovery; connector provenance permits same-account retry, while raw failures do not replay. 64/121 retain endpoint/account attribution and do not rotate shared clients. Message-only lookalikes, DNS, POSIX and retired-generation controls pass. |
| UP-PR-2075 | Existing post-output/buffered frameless losses remain account-neutral, fail as valid SSE and forbid replay. Eventless-window signals, explicit non-clean close frames and protocol-invalid messages retain their policy. Native/live adapter provenance and three HTTP SSE failure paths pass. |
| UP-PR-1903 | Fixed aggregate live output accounting: all bridge queues and waiting producers share 256 MiB. Rejected async/nowait payloads do not leak; cancellation, shutdown, detach, drain and abandoned-queue finalization release capacity. Aggregate overflow yields accepted prefix, one failure and EOS, permits another same-session turn, and does not write account errors or close the shared upstream. Existing per-queue 32 MiB/4096-event caps and five-second delivery stall limit are retained. |

## Reproduction and correction

Before runtime edits, the new unit tests produced **8 failed, 2 passed** ([red.xml](red.xml)). The failures show absent multi-queue admission, uncounted blocked producers, oversized first-event bypass and missing downstream overflow failure. The two initial controls checked nowait rejection cleanup and queue abandonment. The final abandonment test also checks rejection while the abandoned queue remains live; another regression verifies blocked-to-queued ownership transfer.

Runtime edits affect only `queues.py` and `upstream_events.py`. Payload accounts reserve synchronously, pending reservations release idempotently, and queue finalization owns only its byte account. Aggregate exhaustion uses the existing downstream backpressure path with `stream_incomplete`; time-based stalls keep `stream_idle_timeout`.

The first new route run had **1 failed, 9 passed** because its assertion included the backend's legitimate `codex.keepalive` event. The harness now filters keepalives before asserting response lifecycle order and adds an explicit native-originator case. No runtime change was needed for that harness correction. [new-routes.xml](new-routes.xml) retains the earlier result; [queue-routes-final.xml](queue-routes-final.xml) is the complete final green aggregate for new regressions and adjacent queue contracts.

Additional WebSocket coverage uses the repository's standard firewall/API-key stand-ins to reach real selection. Testing the WS trailing slash exposed the existing unregistered route, rather than a selector regression: canonical cases passed, both slash cases closed during the handshake. [websocket-slash-observation.xml](websocket-slash-observation.xml) retains that observation. The final test asserts this existing boundary explicitly; registering a new WS alias is outside these five repairs.

## Exact checks

All pytest runs use `uv run --frozen pytest`, `-q --tb=short`, `--timeout-method=thread`, and a JUnit output in this change directory. Unit timeout is 30 seconds; existing integration timeout is 60 seconds. New-route aggregate timeout is 30 seconds.

| Selection | Result |
| --- | --- |
| `tests/unit/test_network_recovery.py tests/unit/test_http_client.py tests/unit/test_proxy_api_responses_contract.py` | **153 PASS**; [network-native-api.xml](network-native-api.xml), matching `.log`. |
| `tests/unit/test_proxy_utils.py tests/unit/test_streaming_retry_virtual_time.py tests/unit/test_proxy_websocket_client.py -k 'recovery_sleep or native_codex_stream or native_giveup or native_stream_with_retry or synthetic_transport or windows or raw_route or native_direct_adapter or transport_ending or abnormal_close or keepalive_timeout'` | **38 PASS**, 1510 deselected; [transport-utils.xml](transport-utils.xml), matching `.log`. |
| `tests/unit/test_proxy_http_bridge.py -k 'capacity_wait or local_selector or frameless or abrupt_drop or protocol_error_without_transport or non_clean_close_frame or buffered_reasoning_prelude or reader_failure_classifies'` | **36 PASS**, 1060 deselected; [bridge-unit.xml](bridge-unit.xml), matching `.log`. |
| `tests/integration/test_proxy_transient_retry.py -k 'windows or native_codex or process_network or raw_route'` | **8 PASS**, 127 deselected; [transport-routes.xml](transport-routes.xml), matching `.log`. |
| `tests/integration/test_http_responses_bridge.py -k 'stream_failure_remains_valid_sse or retry_hint_is_terminal or capacity_wait or denied_anchor_refusal'` | **9 PASS**, 228 deselected; [bridge-routes.xml](bridge-routes.xml), matching `.log`. |
| `tests/integration/test_transport_delivery_routes.py tests/unit/test_transport_delivery_contracts.py tests/unit/test_http_bridge_event_queue.py tests/unit/test_bridge_cleanup_delivery_contracts.py` | **51 PASS**; [queue-routes-final.xml](queue-routes-final.xml), matching `.log`. |
| Four changed Python files: scoped Ruff, format check and ty | All PASS; [static.log](static.log). |
| Architecture, cancellation, timing seams, settings tiers, migration topology and simplicity scripts | All PASS; [guards.log](guards.log). 98/98 setting fields; existing 274-revision single head preserved. No settings or migration added. |
| OpenSpec 1.11.0 strict change and main-spec validation | Change PASS; **68/68 specs PASS**; [openspec-change.log](openspec-change.log), [openspec-specs.log](openspec-specs.log). |
| Distinct final JUnit identities | **295 PASS**, no failures/errors/skips/xfails. Earlier queue passes overlap the final aggregate and are not counted again. |
| Saved source-row readback, prior-file hashes, spec prefix preservation and whitespace | [closure.json](closure.json); exactly five rows changed and all other 333 source rows retained. |

## Scope and residuals

Verification dimensions: completeness **10/10 tasks**; correctness **1/1 added requirement and 4/4 scenarios** covered by multi-queue/waiting-producer, cancellation/detach, finalization/transfer and existing long-idle stall regressions; coherence follows the synchronous-account and retained-prefix design. No critical local implementation or scenario gap remains. Main delta and stable context are synced before archival.

This closes the five records in verified local fork scope. Four runtime corrections already existed and were independently verified; the missing aggregate live-payload bound was implemented. The budget measures admitted live UTF-8 queued/waiting payload, excluding bounded terminal metadata, completed replay/spool storage, writer buffers, interpreter overhead and total process RSS.

Typed Windows exceptions, adapter stand-ins, synthetic upstreams and current HTTP/ASGI/WebSocket paths were exercised. HTTP slash aliases are registered; the backend Responses WS slash alias remains unregistered and its handshake rejection is an explicit negative control. Real host network transitions, native Rust helper execution, live upstream/provider behavior, production throughput, distributed replicas and current cloud/public gates were not exercised. Upstream numeric delivery-stall and native bridge acceptance remain upstream decisions. The existing five-second local fork bound is retained; no new external acceptance is claimed. No full-repository test-suite or production claim is made.

The initial 251 dirty files were saved under `C:/Users/ext/AppData/Local/Temp/codex-five-transport-20261010`; its hash manifest is [initial-manifest.json](initial-manifest.json). The registry is the only initially dirty file edited by this batch; the other 250 must remain byte-identical. Main spec/context baseline prefixes must remain byte-identical with only this requirement/context appended.
