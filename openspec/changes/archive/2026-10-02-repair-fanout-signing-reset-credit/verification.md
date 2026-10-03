# Verification: INC-04-FANOUT / INC-05-SIGNING / INC-06-RESET

Date: 2026-10-02. Scope: current Windows working tree, exactly these three audit tasks. Existing uncommitted work was retained. No migration, setting, dependency, or live infrastructure change was needed.

## Completeness and correctness

| Requirement | Implementation and independent observable evidence |
| --- | --- |
| Completed fan-out usage survives partial errors | `images_fanout.py` aggregates successful results and transfers the sole public reservation before log rewriting. Actual generations and edits HTTP requests with real API-key reservations persist 7 input + 13 output + 2 cached input tokens per successful subcall, even when a sibling returns 502 or raises. |
| Cancellation owns and drains children | Explicit service-scheduler tasks and shared-future waits isolate caller cancellation. Both routes test cancellation before/after a successful subcall and repeated cancellation during child cleanup, settlement handoff, or release. Every child finishes cleanup; one settlement or release occurs; database quota equals completed usage. |
| Logging and error privacy | Injected model-log rewriting failure preserves a successful combined response and finalized quota. Unexpected subcall errors return a generic OpenAI 500 with no injected private exception marker. |
| Configured bridge key precedence | Ten signed sender/receiver cases reload independent settings with two primary signature versions. Environment key overrides distinct, absent, and invalid file keys without creating/changing files. File-only shared keys work; a mismatched environment key returns 400 `bridge_forward_invalid`. Production bridge signing already had the fix and was retained. |
| Missing target reset identity refuses dispatch | 36 real authenticated HTTP cases: canonical, WHAM, and Codex backend prefixes; both slash forms; explicit/default/auto credit selection; NULL/empty persisted target identity. Each returns 401 `invalid_api_key` / `authentication_error`, consumes no credit, starts no post-redemption refresh, and preserves the credit snapshot. Production refusal already had the fix and was retained. |
| Valid pooled reset keeps target credentials | Existing real route regression uses a distinct encrypted target token and verifies the dispatched token, target ChatGPT account ID, original redemption ID, and refresh of both accounts. |

## Baseline failure evidence

Before the fan-out repair, `tests/integration/test_image_fanout_settlement.py` reported **6 failed, 6 passed**. Both generations and edits leaked the injected unexpected exception text, raised on model-log rewrite failure before settlement, and released the reservation after a successful subcall when the caller cancelled. Existing ordinary partial-error cases passed; these newly demonstrated gaps were not fixed by weakening those assertions.

## Checks

- Final combined image/bridge/Codex usage/fan-out/reset suite: **241 passed** in 151.83 seconds. Command: `uv run pytest tests/integration/test_image_fanout_settlement.py tests/integration/test_proxy_images.py tests/integration/test_codex_usage_api.py tests/unit/test_bridge_configured_key.py tests/unit/test_images_fanout.py tests/unit/test_http_bridge_forwarding.py tests/unit/test_reset_credits_redeem.py -q --tb=short --show-capture=no`.
- Additional strengthened cached-token fan-out route suite: **20 passed**; distinct target-token consume regression: **1 passed**. These assertions were added after the combined runner loaded its tests; both final test revisions passed separately.
- The fan-out unit mocks explicitly use `REAL_SCHEDULER`, matching the production timing seam; no production scheduler fallback was weakened to accommodate mocks.
- Ruff check and format check for all five affected Python files: PASS.
- `uv run ty check app/modules/proxy/images_fanout.py`: PASS.
- Proxy architecture, cancellation safety, and proxy timing-seam checks: PASS.
- Strict OpenSpec change validation: PASS.
- Archive synchronized all three normative blocks exactly with their main specs; `openspec validate --specs --strict`: **68 passed, 0 failed**. All six implementation/verification tasks are complete and the three registry rows plus the five-fix summary are synchronized.

## Coherence and boundaries

The final source was reviewed against each delta scenario and the existing settlement contract. Cancellation is propagated after cleanup and usage handoff; no second settlement owner reaches internal Responses calls. The implementation uses the existing scheduler and cancellation-deferral collaborators and keeps fan-out bounded by existing request validation. Optional request-log failure cannot release already settled usage.

The three capabilities have normative deltas and stable context with concrete examples. Public packages/images, deployed multi-replica infrastructure, cloud CI, real upstream generation, and real credit redemption are separate unverified scopes. All upstream inputs in these tests are inert stubs; persisted usage and external error envelopes are observed independently through HTTP and the test database. No reviewer subagent was used. Other incident tasks, especially OAuth and the historical quota incident, remain open.
