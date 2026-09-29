## 1. Implementation

- [x] 1.1 Extract only complete JSON parsing and SSE framing; no Lite/image changes.
- [x] 1.2 Baseline route returned upstream_request_timeout instead of unsupported_value; formatting and real-route regressions pass after the fix.
- [x] 1.3 Update native parity and lifecycle parser-spy tests; HTTP SSE parser remains unchanged.

## 2. Validation

- [x] 2.1 Targeted/SSE/drain: 137 passed; overlapping bridge: 20 passed. Native wire: 6 skipped without helper binary. Ruff/format, typing, architecture/cancellation/timing, strict change and 65 main specs passed.
- [x] 2.2 Independently based on beta.9; only parser code, synthetic regressions, and this change.
