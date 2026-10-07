## 1. Boundary repair and regression coverage

- [x] 1.1 Reproduce malformed reset metadata at terminal and typed parsing boundaries.
- [x] 1.2 Preserve finite resets and ignore invalid values without changing reset-horizon policy.
- [x] 1.3 Cover malformed metadata through the real streaming Responses route and typed WebSocket health parsing.
- [x] 1.4 Cover request-content echo protection through the real Responses route.

## 2. Verify the exact five contracts

- [x] 2.1 UP-PR-2449: code-less terminal frames bench last/visible accounts, rotate neutral requests, and refresh usage.
- [x] 2.2 UP-PR-2439: client terminal reset metadata and original quota terminals survive exhausted or failed replay.
- [x] 2.3 UP-PR-2440: absolute/relative reset metadata reaches direct WebSocket and HTTP bridge health after keyed settlement.
- [x] 2.4 UP-PR-2403: usage classification, burst distinction, and model-capacity account exclusion remain coherent.
- [x] 2.5 UP-PR-2391: pool bounds, eligibility probe, original failures, and deadline terminal rendering satisfy the library contract.

## 3. Complete the authorized local package

- [x] 3.1 Run focused tests, lint/type/architecture checks, and strict OpenSpec validation.
- [x] 3.2 Synchronize main spec/context and verify completeness/correctness/coherence before archive.
- [x] 3.3 Update and reread exactly five registry rows and evidence; preserve all other source rows.
- [x] 3.4 Prepare the verified local-main commit scope with git diff --check and explicit staged-path review.
