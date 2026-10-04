# Publication of previously verified local changes

Date: 2026-10-04, Europe/Kiev. Parent commit: `8f713d322e7d61102092cc379506d38429b9fc58`. User explicitly requested committing the previously preserved changes too. Target: Frozen811/codex-lb main.

## Scope and existing verification

The 125 remaining modified/untracked paths exactly match the previous preservation manifest. Before publication formatting, the 119 non-overlapping original files were byte-identical to their captured versions; one archived delta has now had a trailing empty line removed for git diff --check; the six document overlaps retain both the prior packages and the published three-item batch. All eight prior archived changes have complete task lists and verification evidence. Existing partial and external scopes remain partial/open.

| Prior archive | Verification |
|---|---|
| 2026-10-03-repair-native-transport-recovery | [evidence](../2026-10-03-repair-native-transport-recovery/verification.md) |
| 2026-10-03-repair-telemetry-and-stateless-key-contracts | [evidence](../2026-10-03-repair-telemetry-and-stateless-key-contracts/verification.md) |
| 2026-10-03-verify-image-websocket-transport-contracts | [evidence](../2026-10-03-verify-image-websocket-transport-contracts/verification.md) |
| 2026-10-03-verify-plan-json-metrics-contracts | [evidence](../2026-10-03-verify-plan-json-metrics-contracts/verification.md) |
| 2026-10-04-repair-bridge-terminal-lineage-failover | [evidence](../2026-10-04-repair-bridge-terminal-lineage-failover/verification.md) |
| 2026-10-04-repair-image-control-transport-contracts | [evidence](../2026-10-04-repair-image-control-transport-contracts/verification.md) |
| 2026-10-04-verify-bridge-cleanup-quarantine-backpressure | [evidence](../2026-10-04-verify-bridge-cleanup-quarantine-backpressure/verification.md) |
| 2026-10-04-verify-bridge-retry-claim-lifecycle | [evidence](../2026-10-04-verify-bridge-retry-claim-lifecycle/verification.md) |

## Fresh publication checks

- Scoped Ruff check/format: all 46 pending Python files pass; scoped ty: all 21 pending app files pass.
- Proxy architecture, cancellation safety, timing seams, settings tiers 98/98, migration topology (271 revisions, one head) and simplicity budgets pass.
- Strict OpenSpec 1.11.0 main validation: 68/68 pass. Every registry OpenSpec link resolves; eight archives have no unchecked implementation tasks.
- `cargo fmt --all -- --check`, `cargo test --locked -p codex-lb-egress -p codex-lb-egress-worker`: 25 Rust tests pass. `cargo build --locked -p codex-lb-egress-worker` succeeds.
- Fresh targeted Python unit selection: 294 passed, no skips/failures, 15.24 s.
- Integration selection A: 141 passed, no skips/failures, 104.85 s (cleanup/delivery, retry terminals, telemetry/key, plan/JSON and real socket abort).
- Integration selection B: 119 passed, no skips/failures, 147.20 s (native transport, image/control routes, selected-owner terminal evidence, bridge continuations and real primary/metrics CLI logs).
- Total fresh Python coverage: 554 distinct cases across disjoint unit/integration file selections. This is targeted coverage, not the full repository or the previously unstable native terminal aggregate.
- Native wire probes ran with the freshly source-built helper selected by CODEX_LB_NATIVE_EGRESS_TEST_BINARY; SHA256 `bbd2bb52e5fe9989151e245a5ca7e3a280d292c304b2540ec68417973205466d`. No native test skips.
- Staged whitespace check initially found one new blank line at the end of the archived outbound-http-clients delta; only that empty line was trimmed. No runtime or normative text changed.

Unit command:

```text
uv run --frozen pytest -q --timeout=30 --tb=short tests/unit/test_bridge_cleanup_delivery_contracts.py tests/unit/test_bridge_retry_claim_lifecycle.py tests/unit/test_websocket_terminal_provenance.py tests/unit/test_http_bridge_event_queue.py tests/unit/test_network_recovery.py tests/unit/test_structured_logging.py tests/unit/test_host_models.py tests/unit/test_codex_upstream_paths.py tests/unit/test_telemetry_sender.py
```

## Boundaries

Publication does not certify cloud CI, CodeRabbit, production, public packages/images, hosted provider/client behavior or platform parity. The earlier grouped native terminal cleanup instability remains explicit in its original verification; this commit does not claim a whole-repository or full native aggregate pass. UP-ISSUE-2471, UP-ISSUE-1208 and UP-ISSUE-2271 remain partial. F-045/CI-04 remain open. Historical test counts are not re-counted as fresh execution. No additional code changes are introduced for publication.


Integration commands (CODEX_LB_NATIVE_EGRESS_TEST_BINARY points to target/debug/codex-lb-native-egress.exe):

```text
uv run --frozen pytest -q --timeout=30 --tb=short tests/integration/test_bridge_cleanup_delivery_contracts.py tests/integration/test_bridge_retry_terminal_contracts.py tests/integration/test_telemetry_key_contracts.py tests/integration/test_plan_json_contracts.py tests/integration/test_websocket_terminal_wire.py
141 passed
uv run --frozen pytest -q --timeout=30 --tb=short tests/integration/test_native_transport_contracts.py tests/integration/test_image_control_transport_contracts.py tests/integration/test_direct_websocket_terminal_evidence.py tests/integration/test_bridge_continuation_contracts.py tests/integration/test_metrics_server_logging.py
119 passed
```

Fresh commands emit only the existing Starlette/AnyIO deprecation warning. Previous verification files remain historical evidence, including their explicit partial scopes and aggregate limitations.
