## Why

The full main CI rerun exposed a Firewall integration timeout at the unchanged
15-second limit. A focused cold coverage run passes but takes 14.12 seconds in
total. Settings also requests the cache-probe API without a registered MSW
handler. These checks need less harness overhead and complete API fixtures.

## What Changes

- Preload the real lazy Settings route before timed interactions, scope Firewall
  queries and paste the complete IP while retaining add/remove and route checks.
- Register typed, deterministic cache-probe plan/run handlers and verify their
  API schemas through the real client and MSW transport.
- Keep file parallelism, assertions, timeouts and coverage thresholds unchanged.

## Impact

Frontend test harness and GitHub automation verification context only.
