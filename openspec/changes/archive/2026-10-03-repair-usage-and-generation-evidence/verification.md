# Verification: UP-PR-2504 / UP-PR-2521 / UP-PR-2444

Verified on 2026-10-03 against working-tree changes on
`f52adb7274c96c0702e19aa02eabd4f1c7556231`. Existing uncommitted batches were
present before this work; their 108 unrelated tracked diff blocks are byte-for-byte
unchanged against the pre-edit snapshot. No commit, push, release or deployment.

## UP-PR-2504: cache-write accounting

The existing implementation is confirmed by real local HTTP and WebSocket
upstreams carrying native Codex responses through `POST /v1/responses` and the
Python transport. The native Rust helper is disabled only in these socket tests
to select the independently controlled transport.

The 24 native cases combine both transports, three JSON encodings and four write
counts: missing, negative, 50,000 and excessive 200,000. With 100,000 input tokens
and 20,000 cached reads, writes occupy only the remaining input partition.
Normal-rate recorded costs are respectively 0.8212, 0.8212, 0.9462 and 1.0212 USD
including 24 output tokens. The tests check:

- Actual upstream receives one request for the assigned account.
- RequestLog retains the raw nullable write count; missing writes settle as zero
  in new reservation accounting, preserving existing behavior.
- Finalized reservations and cost-limit microdollars agree with the independently
  calculated price, and a repeated finalization does not charge again.
- Request-log API components agree with the persisted total; the following
  request hits its cost limit before any second upstream dispatch.
- Existing integration tests separately confirm the 100,000-write Astra example
  (1.25 USD), migration history preservation and missing-cost repair.
- Six further tests cover automation compact, limit warm-up and quota planner
  warm-up/probe write propagation, including reservation/no-reservation paths.

## UP-PR-2521: optional source telemetry

Existing parsing and persistence are independently confirmed by 20 new API-path
tests using real local upstreams and an isolated database. Chat Completions and
Responses run with streaming and non-streaming delivery. Missing, boolean,
int32-overflowing and known reasoning counts retain their correct unknown/known
meaning. Invalid cached counts cannot become a discount. Individually valid
timings whose sum exceeds int32 remain unavailable.

Multiline CRLF SSE is written across a CR/LF and a UTF-8 code-point boundary.
Chat source bytes remain exact; Responses preserves output/usage through its
existing public envelope. A valid limited request finalizes 13 tokens exactly
once. Non-streaming invalid total counts fail with HTTP 502 / `usage_unavailable`,
release reservations and leave limit counters at zero. Source rows keep
subscription-only output sample fields null, and valid source timings appear as
`legacy_estimate`, never as qualified local generation measurements.

The full source forwarding unit suite additionally tests every chunk boundary,
numeric/timing bounds and byte retention; the baseline existing API telemetry
tests also passed in the initial targeted run.

## UP-PR-2444 / F-052: output sampling defect and repair

Before the fix, the two key-spacing/escaping unit regressions failed. A real
HTTP upstream routed through `/v1/responses` also recorded first non-reasoning
output at 1,000 ms instead of its observed 500 ms. The lexical scanner searched
for an exact `"delta":` substring and could also use unrelated nested keys.

The verbatim observer now reuses the shared structured content classifier and
the existing parsed SSE carrier. All four field-spacing/escaping/nested-field
unit cases pass. A cached-carrier test forbids another JSON decode. Numeric
decoder limits in plain-string metadata and a simulated recursion-limit error
skip optional sampling without interrupting relay.

Across the 24 real socket cases, reasoning at 125 ms remains TTFT, first actual
text is 500 ms, the second output chunk is 750 ms and upstream terminal is
1,000 ms. Two seconds of post-terminal cleanup yield total latency 3,000 ms.
The database, request-log API and daily reports agree on two output chunks and
`(24 - 4) / ((1000 - 500) / 1000) = 40 TPS`, with one qualified daily sample.
Relayed canonical second-delta bytes retain upstream JSON spacing/escaping.
Report sample/median/filter coverage and the timing migration also pass.

## Executed checks

- Main focused suite: **460 passed** in 81.62 s. Files: `test_pricing.py`,
  `test_pricing_catalog.py`, `test_model_sources_forwarding.py`,
  `test_response_timing.py`, `test_request_log_virtual_time.py`,
  `test_reports_repository.py`, new `test_usage_generation_contracts.py`,
  `test_reports_api.py`, `test_cost_backfill.py`, timing migration,
  cache-write migration, API-key cache-write HTTP stream/non-stream regression,
  and two existing verbatim relay regressions.
- Background cache-write cases: **6 passed** in 1.94 s, disjoint from that suite.
- After adding decoder-limit protection and completing test fixtures:
  `test_response_timing.py` + `test_usage_generation_contracts.py`:
  **74 passed** in 37.53 s, including the two additional guard tests.
  Overlapping reruns are not added to the first suite's count; the combined
  distinct test coverage is 468 cases.
- Ruff check and format check for all three changed Python files: PASS.
- `ty check app/modules/proxy/_service/response_timing.py`: PASS.
- Proxy architecture, cancellation safety and timing seam scripts: PASS.
- CI-pinned OpenSpec 1.11.0 strict validation: change PASS, **68/68** main specs
  PASS. Delta and main requirement/scenario blocks match exactly.
- Focused `git diff --check`: PASS.

The sole pytest warning is the existing Starlette/AnyIO BlockingPortal
deprecation. A draft recursion-depth test assumed a decoder boundary that was
not active in this test environment; its final deterministic decoder-error
fixture passes. This was a test assumption, not an additional product defect.

## Final source fingerprints

SHA-256 of the verified Python files:

| File | SHA-256 |
|---|---|
| `app/modules/proxy/_service/response_timing.py` | `433b6f8f0829786f3e7c45f5e52460f342a072d292ba300c2d77c0910f693277` |
| `tests/unit/test_response_timing.py` | `08d6c4dc961684bea860382584eeb3fe287c0889909996dff1e4d72af329f205` |
| `tests/integration/test_usage_generation_contracts.py` | `2da77385629eecd933b345494f227ea289d1e82d78e8666cc3e7d16e9604c1d8` |

## Completeness, correctness and coherence

All implementation and verification tasks are complete. Both added normative
scenarios map to unit regressions and the actual native HTTP/WebSocket route
matrix. Existing settlement/owner behavior is observed, not replaced. The patch
removes a duplicate classifier, adds no configuration/dependency/schema/UI
surface and leaves prices and published migrations unchanged. No unresolved
critical or warning finding in this bounded local review.

The three registry items are locally closed. Hosted incidents, current-head
cloud gates, packaged Rust-helper behavior, PostgreSQL runtime and newly
published artifacts remain outside this local evidence; no such results are
claimed or silently closed.
