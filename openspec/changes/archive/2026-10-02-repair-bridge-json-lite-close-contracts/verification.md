# Verification: bridge JSON, Lite tools and close 1009

Date: 2026-10-02. Base HEAD: `f52adb7274c96c0702e19aa02eabd4f1c7556231`.
Scope: exactly UP-PR-2530, UP-PR-2531 and UP-PR-2539 from issues-check.md.
Existing unrelated working-tree changes were preserved. No commit, push,
release, deployment or public artifact verification was performed.

## Result

| Dimension | Result |
|---|---|
| Completeness | 6/6 tasks; 3 requirements; 9 scenarios mapped below |
| Correctness | 207 focused tests passed, including actual loopback HTTP/WebSocket traffic |
| Coherence | Existing adapter/relay ownership retained; five production lines added; no settings, dependencies or migrations |

UP-PR-2530 and UP-PR-2531 already had working source fixes. Added broader
product-path evidence. UP-PR-2539 had a genuine adapter gap: aiohttp's
ERROR(WebSocketError(1009)) lost its size evidence before relay classification.
The typed exact-code exception now becomes the existing close-1009 shape
before generic network recovery.

## Red-before / green-after

Before the adapter change, valid regressions in
test_routed_adapter_preserves_only_typed_message_size_error plus
test_http_bridge_close_1009.py gave **7 failed, 9 passed**.
One adapter failure and six HTTP cases demonstrated the missing close code,
503/stream_incomplete replacement and pre-created replay. Other protocol codes
and received-close cases passed. After the five-line fix: **16 passed**.

The final combined suite passed after test-harness review. Intermediate harness
failures (missing bridge identity, supported synthesized text deltas and
keepalive events) were corrected and are not product defects.

## Scenario mapping

| Delta scenario | Evidence |
|---|---|
| Formatted upstream error is terminal | test_http_bridge_multiline_json.py::test_formatted_error_settles_without_retry_and_next_turn_recovers; compact/pretty/CRLF, metadata-first, native payload, slash routes and next-turn recovery |
| Formatted lifecycle and tool items survive | test_formatted_success_delivers_complete_output_items; message/function_call items, Unicode/newline preservation, native/text parity and terminal output; test_bridge_contract_wire.py actual LF/CRLF sockets |
| Lite bridge request reaches upstream serialized | test_responses_lite_parallel_tools.py; 3 paths × Lite/non-Lite × omitted/null/true/false, input/cache/reasoning and outgoing marker |
| Lite direct HTTP and fallback agree | test_bridge_contract_wire.py::test_lite_direct_http_and_handshake_fallback_preserve_wire_contract; actual POST bytes/header, GET426 then POST, 16 combinations; existing core-client Lite tests |
| Untrusted marker remains non-Lite | test_untrusted_marker_does_not_disable_parallel_calls plus non-Lite actual HTTP/header cases |
| Single account rejects the message size | test_http_bridge_close_1009.py before-output cases; received close and adapter error, no exclusion/health, same-account recovery; actual oversized socket cases |
| Close after output | HTTP bridge after-output matrix plus test_direct_websocket_close_1009.py; one terminal error, no repeated partial output/replay |
| Other disconnects are unchanged | exact-code unit matrices, typed 1002/1006/1011 controls and ordinary routed/direct disconnect tests with existing health behavior |
| Reader reports a typed size error | aiohttp regression and actual reader max_msg_size=1024 against a 4096-byte message; reservations terminal, pending queue empty, create gate released, next valid request succeeds |

## Final focused test command

```powershell
uv run pytest -q --tb=short --show-capture=no tests/integration/test_http_bridge_multiline_json.py tests/integration/test_responses_lite_parallel_tools.py tests/integration/test_http_bridge_close_1009.py tests/integration/test_direct_websocket_close_1009.py tests/integration/test_bridge_contract_wire.py tests/unit/test_responses_lite_parallel_calls.py tests/unit/test_websocket_close_1009.py tests/unit/test_ws_close_1009_classification.py tests/unit/test_proxy_websocket_client.py tests/unit/test_proxy_http_bridge.py::test_http_bridge_reader_preserves_routed_aiohttp_close_code tests/unit/test_proxy_http_bridge.py::test_http_bridge_reader_maps_ordinary_websocket_receive_failure_to_stream_incomplete tests/unit/test_proxy_utils.py::test_relay_upstream_websocket_ordinary_receive_failure_is_stream_incomplete_and_penalized tests/unit/test_proxy_utils.py::test_stream_responses_derives_lite_http_header_from_additional_tools tests/unit/test_proxy_utils.py::test_stream_responses_uses_websocket_transport_and_marks_lite_payload
```

**207 passed**, 84.13 seconds, one existing Starlette/AnyIO deprecation warning.
This is the combined count, not a sum of overlapping intermediate runs.

## Static validation and second review

- Ruff check/format: all six changed Python files passed.
- `uv run ty check app/core/clients/proxy_websocket.py`: passed.
- Proxy architecture, cancellation safety and proxy timing seam scripts: passed.
- `.github/scripts/check_simplicity_budgets.py`: passed (README218/225,
  headings10/10, env54/60, core nav5/5, root entries0/0).
- `npx --yes @fission-ai/openspec@1.11.0 validate --specs --strict`:
  **68 passed, 0 failed**.
- Strict validation of repair-bridge-json-lite-close-contracts: passed.

A second source/scenario review was performed without a separate reviewer
agent. Checked type/exact-code binding, return before generic network rotation
and reuse of terminal cleanup. Ordinary liveness errors, other protocol codes
and raw recovery retain existing behavior. Actual socket tests reach the bridge
using a cache identity; supported keepalives and synthesized text were recognized
without relaxing payload assertions. Matched all nine scenarios against final
tests; synchronized two added and one modified requirement with the main spec.

No critical findings or uncovered delta scenarios remain in this local scope.
Cloud CI, public wheel/image/release, live deployment, real OpenAI traffic and
real Codex client sessions remain outside this batch's evidence.
