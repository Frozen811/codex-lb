# Baseline negative control

Base: `94c9a8c24cc0dfdd4c5bce00aa1c46e6bc9d9b6d`. All six changed runtime files were temporarily replaced by HEAD bytes, tests retained, then restored in finally.

Command: `uv run pytest -q tests/integration/test_bridge_refusal_transition_terminal.py -k backend and (local_refusal or creation_refusal or health_failure) --tb=line --show-capture=no --disable-warnings`

24 failed, 6 passed, 53 deselected, 1 warning in 35.56s

- tests/integration/test_bridge_refusal_transition_terminal.py::test_native_local_refusal_is_delivered_before_dispatch[cooldown-/backend-api/codex/responses-False]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_native_local_refusal_is_delivered_before_dispatch[cooldown-/backend-api/codex/responses-True]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_native_local_refusal_is_delivered_before_dispatch[generation-/backend-api/codex/responses-False]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_native_local_refusal_is_delivered_before_dispatch[generation-/backend-api/codex/responses-True]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_native_local_refusal_is_delivered_before_dispatch[retiring-/backend-api/codex/responses-False]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_native_local_refusal_is_delivered_before_dispatch[retiring-/backend-api/codex/responses-True]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_native_local_refusal_is_delivered_before_dispatch[unregistered-/backend-api/codex/responses-False]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_native_local_refusal_is_delivered_before_dispatch[unregistered-/backend-api/codex/responses-True]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_native_local_refusal_is_delivered_before_dispatch[reconnect-/backend-api/codex/responses-False]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_native_local_refusal_is_delivered_before_dispatch[reconnect-/backend-api/codex/responses-True]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_native_local_refusal_is_delivered_before_dispatch[late_closed-/backend-api/codex/responses-False]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_native_local_refusal_is_delivered_before_dispatch[late_closed-/backend-api/codex/responses-True]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_native_local_refusal_is_delivered_before_dispatch[lease_race-/backend-api/codex/responses-False]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_native_local_refusal_is_delivered_before_dispatch[lease_race-/backend-api/codex/responses-True]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_creation_refusal_sites_preserve_native_error[parallel-/backend-api/codex/responses-False]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_creation_refusal_sites_preserve_native_error[parallel-/backend-api/codex/responses-True]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_creation_refusal_sites_preserve_native_error[handoff-/backend-api/codex/responses-False]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_creation_refusal_sites_preserve_native_error[handoff-/backend-api/codex/responses-True]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_creation_refusal_sites_preserve_native_error[owner-/backend-api/codex/responses-False]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_creation_refusal_sites_preserve_native_error[owner-/backend-api/codex/responses-True]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_creation_refusal_sites_preserve_native_error[ring-/backend-api/codex/responses-False]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_creation_refusal_sites_preserve_native_error[ring-/backend-api/codex/responses-True]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_health_failure_after_real_settlement_preserves_one_terminal[False-later_event-/backend-api/codex/responses]
- tests/integration/test_bridge_refusal_transition_terminal.py::test_health_failure_after_real_settlement_preserves_one_terminal[False-raised_error-/backend-api/codex/responses]
