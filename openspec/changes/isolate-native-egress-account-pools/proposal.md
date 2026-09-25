# Proposal: Isolate Native Egress Account Connection Pools

## Why

When `upstream_stream_transport=http` is enabled, the native egress helper (`codex-lb-native-egress`) pools and reuses `reqwest::Client` instances solely by proxy URL, connect timeout, and response decoding settings. The pool key lacks account/connection-group isolation.

Consequently, all accounts sending requests to the same upstream host (e.g. `chatgpt.com`) share a single `reqwest::Client` instance and its underlying HTTP/2 connection pool. Under HTTP/2, all streams to the same host are multiplexed over a single TCP/TLS connection. If this connection drops (e.g. due to OS-level TCP segmentation offload bugs or transient network resets), **all in-flight streams across all accounts fail simultaneously** with an unretried, untyped drop (Issue #2471).

## What Changes

1. **Protocol Extension (`codex-lb-protocol`):**
   - Add optional `pool_key: Option<String>` to `NativeRequest` (`serde(default, skip_serializing_if = "Option::is_none")`).
2. **Rust Helper Client Isolation (`codex-lb-egress`):**
   - Include `pool_key: Option<String>` in `ClientKey`.
   - Ensure separate `reqwest::Client` connection pools are instantiated for distinct `pool_key` values (e.g. per-account), preventing cross-account connection sharing and blast radius.
3. **Python Native Egress Client (`app/core/clients/native_egress.py`):**
   - Add `pool_key: str | None = None` to `NativeEgressRequest` and propagate it through the JSON IPC command.
4. **Proxy Egress Call Site (`app/core/clients/proxy.py`):**
   - Supply `pool_key=account_id` when invoking `active_native_egress_client.request()` for streaming/non-streaming direct HTTP requests.

## Capabilities

### Modified Capabilities
- `outbound-http-clients`: Packaged native egress isolates HTTP/2 connection pools by account `pool_key`, ensuring transport failures on one account do not affect concurrent streams of other accounts.

## Impact
- `crates/codex-lb-protocol/src/lib.rs`
- `crates/codex-lb-egress/src/http.rs`
- `app/core/clients/native_egress.py`
- `app/core/clients/proxy.py`
- `tests/unit/test_native_egress.py`
- Fixes #2471.
