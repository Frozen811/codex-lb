# Full CI follow-up

Publication commit `9236bae3e12711066e463d3192e848b9d968ea46` includes the four
explicitly authorized five-record packages. The first full run is
[CI 37348954280](https://github.com/Frozen811/codex-lb/actions/runs/37348954280).

## Failure reproduction and correction

The independent Docs workflow failed strict MkDocs validation on two links in
`docs/routing.md` pointing outside its documentation tree. Both now point to the
owning OpenSpec capability on the fork's main branch, consistent with the other
spec links in the published docs. `uv run --group docs mkdocs build --strict`
reproduced the two warnings before correction and passes after correction.

Unit CI reported **2 failed, 12604 passed, 8 skipped, 1 xfailed**. The failed tests
asserted pre-repair behavior in the earlier auth/input package:

- `test_chat_response_format_json_object_keeps_json_instruction_in_input` still
  expected the developer directive hoisted into top-level instructions. It now
  checks both developer entries, their exact order/content, the empty instruction
  default and the unchanged JSON format, matching the already synchronized
  Responses contract and existing real Chat wire regression.
- The old remote-admin test asserted the removed role-specific twelve-hour cap.
  Its replacement checks both admin and operator at one hour, exactly thirty
  days and one second above thirty days, including matching cookie Max-Age and
  session-store lifetime. It retains the remote cap above thirty days and aligns
  with the existing normative absolute-lifetime policy.

`uv run pytest tests/unit/test_chat_request_mapping.py tests/unit/test_dashboard_auth_api.py -q --tb=short --show-capture=no`
passes **72 tests**, with one existing Starlette deprecation warning. These
corrections change test expectations and documentation links; production behavior
and the four batches' normative contracts are unchanged. No CI job, coverage
gate, skip condition or workflow matrix is weakened. The final publication must
receive a fresh full CI result; initial successes alone do not certify its head.

## Resume audit on 2026-10-06

The interrupted run finished with **25 successful jobs and 4 failed jobs**. The
two additional failures are the integration-core aggregate and CI Required;
their underlying cause is one failure in integration-core-2, with **1468 passed
and 19 skipped**. MySQL and the other two integration-core shards passed.

`test_repeated_eventless_lineage_recovers_without_poisoned_anchor` received
`bridge_instance_mismatch` while its artificial response-created timeout,
downstream eventless watchdog and stuck-gate retirement all shared a 100ms
boundary. The exact CI ownership failure did not reproduce in the isolated case
or the original full 27-case module. Injecting reconnect latency also passed; no
production ownership fix is inferred from that experiment.

The final fixture isolates the intended downstream watchdog: it retains 100ms
stream-idle, gives response-created recovery one second and gate retirement two
seconds, and retains a five-second outer request bound with a ten-second service
budget. Raising the downstream watchdog instead selected the different upstream
missing-response-created terminal in a diagnostic run, so that approach was
discarded. All original error-code, send-count, full-history, anchor removal,
queue cleanup and durable reservation assertions remain intact. No production
code or workflow is changed by this fixture correction.

Fresh combined verification:
`uv run pytest tests/integration/test_bridge_continuation_contracts.py tests/unit/test_chat_request_mapping.py tests/unit/test_dashboard_auth_api.py -q --tb=short --show-capture=no`
reports **99 passed**, one existing Starlette deprecation warning, in 37.31s.
Strict docs build, Ruff/format/ty, proxy architecture, cancellation safety,
timing seams and all 68 OpenSpec capabilities pass. These results justify the
next full CI attempt; they do not substitute for its actual final status.
