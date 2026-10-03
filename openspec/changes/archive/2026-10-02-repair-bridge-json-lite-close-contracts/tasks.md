## 1. Route and adapter regressions

- [x] 1.1 Verify multiline upstream error, lifecycle and tool events through public HTTP routes, including native payloads and CRLF.
- [x] 1.2 Verify Lite normalization through bridge routes, direct HTTP and fallback, and reject untrusted Lite signals.
- [x] 1.3 Reproduce typed aiohttp size error through adapter and HTTP routes; preserve exact code 1009 and verify settlement, account reuse and other-code controls.

## 2. Completion

- [x] 2.1 Run focused suites, Ruff and relevant static gates; record actual command results and scenario mapping in verification.md.
- [x] 2.2 Perform a second source/scenario review, synchronize specs/context and pass strict OpenSpec validation.
- [x] 2.3 Update exactly UP-PR-2530/2531/2539 registry entries and finding summary with evidence; archive only after all tasks pass.
