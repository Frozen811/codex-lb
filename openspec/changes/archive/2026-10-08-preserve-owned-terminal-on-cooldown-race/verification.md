# Verification: owned terminal survives post-submit cooldown

Date: 2026-10-08, Europe/Kiev. Baseline: `83026fba1c96636c5d71129392d23a8172365663`, published fork main. The preceding bounded Playwright installation succeeded in [CI #81](https://github.com/Frozen811/codex-lb/actions/runs/37723719827): runner APT configuration, installation (19 seconds), and actual dashboard browser smoke (39 seconds) all passed.

## Cloud failure and root cause

CI #81 completed with **32 successful jobs and three failures**. The primary [integration-core-1](https://github.com/Frozen811/codex-lb/actions/runs/37723719827/job/113137144381) failure was `test_reason_only_incomplete_opens_durable_circuit_before_next_dispatch[/v1/responses]`; the other failures were the integration-core and CI Required aggregates. Separate Windows, release guards, and simplicity passed.

The log recorded two actual incomplete terminals, a durable circuit opening at failure count two, then `retry_circuit_cooldown_continuity_bound` and HTTP 503 at the second request. The reader had already claimed the request's terminal settlement, but its durable circuit write completed before downstream enqueue. The stream's post-submit guard saw an empty queue, no response-created ID/events, and an active cooldown, so it detached the already-owned terminal as if the submitted request were still eventless.

The unmodified real-route file passed **3/3** in isolation. Deterministic scheduling controls then reproduced the actual defect without relying on CI load: block the second terminal after the real durable circuit write, synchronize submit completion and the post-submit cooldown read, then release publication. Before source changes all **three route cases failed with the same HTTP 503**. Two independent unit controls also failed by replacing the owned incomplete with a synthetic failure: one uses an active settlement claim, the other an observed upstream-terminal timestamp after claim completion.

## Repair and invariant coverage

The post-submit refusal now additionally requires that terminal settlement is not `claimed` and no upstream terminal timestamp is present. The pre-submit check and existing verified stale-anchor recovery policy are untouched. No new send, account switch, reservation acquisition, or setting is introduced.

All six real-route cases (ordinary timing and held publication on `/v1/responses`, its trailing-slash equivalent, and `/backend-api/codex/responses`) retain the upstream incomplete, durable failure counts, active cooldown, duplicate receipt replay without dispatch, settled reservations, zero account pressure, and expected request logs. Existing no-terminal unit controls still detach and refuse the request. The two ownership/observation controls separately bind both added predicates.

An additional exploratory assertion that every different input must return 503 was removed: that would change existing verified recovery/admission policy, rather than verify this terminal-publication race. The final regression preserves the original receipt and circuit assertions and the existing no-terminal refusal; it introduces no new admission promise.

## Focused local validation

| Command /scope | Result |
|---|---|
| `uv run pytest -q tests/unit/test_proxy_http_bridge.py -k 'cooldown or terminal_settlement or circuit' --tb=short --show-capture=no` | 84 PASS |
| `uv run pytest -q tests/integration/test_bridge_retry_terminal_contracts.py tests/integration/test_bridge_cleanup_delivery_contracts.py tests/unit/test_http_bridge_eventless_semantics.py tests/unit/test_bridge_cleanup_delivery_contracts.py --tb=short --show-capture=no` | 51 PASS |
| Whole-repo Ruff check /format | PASS, 1483 formatted files |
| Scoped ty on the source and both edited test files | PASS |
| Proxy architecture, cancellation safety, timing seams, settings tiers | PASS; settings 98/98 unchanged |
| Simplicity and whitespace checks | PASS |
| Strict OpenSpec 1.11.0 change and main specs | PASS, 68/68 capabilities |

The scopes above are disjoint: **135 passing cases**, no skips or xfails. Smaller red/green selections overlap and are not added. Existing Starlette/AnyIO deprecation warnings remain.

## Completeness and publication boundary

One normative requirement and three scenarios are synchronized with the main Responses spec and stable context. Source inspection, claim/timestamp controls, real-route durable persistence, and existing negative controls establish correctness and coherence without changing recovery policy. All 338 source registry rows remain byte-identical; original task counts and live-provider/production limits remain intact.

The CI #81 failure remains historical evidence. The user authorized commit/push of the repair to `Frozen811/codex-lb:main` and complete CI monitoring on the exact published SHA. A new successful cloud matrix remains required; local 135 passes and the successful browser job alone are not a full CI success.
