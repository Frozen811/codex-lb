# Tasks: isolate-native-egress-account-pools

- [x] 1. Protocol and Rust Helper Pool Isolation
  - [x] 1.1 Add `pool_key: Option<String>` to `NativeRequest` in `crates/codex-lb-protocol/src/lib.rs`.
  - [x] 1.2 Include `pool_key: Option<String>` in `ClientKey` and `execute_request` in `crates/codex-lb-egress/src/http.rs`.
- [x] 2. Python Client and Proxy Integration
  - [x] 2.1 Add `pool_key: str | None = None` to `NativeEgressRequest` and request JSON serialization in `app/core/clients/native_egress.py`.
  - [x] 2.2 In `app/core/clients/proxy.py`, pass `pool_key=account_id` when invoking `active_native_egress_client.request()`.
- [x] 3. Tests & Verification
  - [x] 3.1 Unit tests in `tests/unit/test_native_egress.py` verifying `pool_key` serialization and protocol compatibility.
  - [x] 3.2 Verify `cargo check` / `cargo test` if cargo is available, or verify Python side with pytest.
  - [x] 3.3 Verify `ruff check` and migration topology.

