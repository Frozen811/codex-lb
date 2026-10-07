## Why

Fork CI #78 at `6ca0f6f059a9dfaf26b69a582f2db7e2f75469c5` failed in `integration-core-1` because the paused-delivery test applied its artificial 100 ms stall timeout to an independent healthy request. Two downstream-stall warnings confirm that the control inherited the accelerated failure condition under CI load.

## What Changes

- Keep the stalled consumer's 100 ms failure injection and bounded cleanup assertions.
- Restore the ordinary delivery timeout before sending the independent healthy control.
- Simulate a 150 ms enqueue scheduling delay for the independent control, making the former fixture defect reproducible without CI load.
- Record publication authority and local verification; publish the fix and follow full CI on its exact SHA.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This is a test-fixture correction; production behavior and normative requirements are unchanged. `.openspec.yaml` explicitly sets `skip_specs: true`.

## Impact

Only `tests/integration/test_bridge_cleanup_delivery_contracts.py`, this change's artifacts, and publication evidence in `issues-check.md`. No source rows, production code, settings, CI gates, dependencies, or migrations change.
