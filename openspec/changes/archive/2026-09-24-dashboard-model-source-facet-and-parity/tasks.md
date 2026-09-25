# Tasks: Dashboard Model Source Visibility, Upstream Transport Parity, Compaction Switchover, and Safe Slimming

## 1. Dashboard Model Source Visibility (Issue #1870)
- [x] 1.1 In `recent-requests-table.tsx`, fallback `accountLabel` to `request.modelSourceId` when `request.accountId` is null.
- [x] 1.2 In `recent-requests-table.tsx`, render `modelSourceId` and `modelSourceKind` in the request details dialog.
- [x] 1.3 Add missing translation strings to `en.json`, `ko.json`, and `zh-CN.json`.
- [x] 1.4 Add unit test in `recent-requests-table.test.tsx` verifying model source display in account cell and request details modal.

## 2. Upstream Transport Parity & Fingerprint Normalization (Issue #1208)
- [x] 2.1 Verify `codex-lb-native-egress` uses `reqwest` with Rustls TLS, custom H2 initial stream/connection window sizes, and max frame sizes matching Codex CLI.
- [x] 2.2 Verify `_normalize_non_native_upstream_fingerprint` in `app/core/clients/proxy.py` strips `x-stainless-*` and `x-openai-client-*` headers and normalizes User-Agent, originator, and version.
- [x] 2.3 Verify test coverage in `tests/unit/test_proxy_upstream_fingerprint.py`.

## 3. Sticky Compaction Switchover (Issue #986)
- [x] 3.1 Verify sticky thread affinity sets `reallocate_sticky=True` during remote compaction in `app/modules/proxy/_service/compact.py`.
- [x] 3.2 Verify normal follow-up requests maintain `reallocate_sticky=False` to preserve prompt cache and prevent mid-thread thrashing.
- [x] 3.3 Verify test coverage in `tests/unit/test_select_with_stickiness.py` and `tests/integration/test_proxy_compact.py`.

## 4. Safe Payload Slimming (Issue #568)
- [x] 4.1 Verify payload slimming restricts mutations to historical tool outputs and images without dropping conversation turns.
- [x] 4.2 Verify prompt cache stability and test coverage in `tests/unit/test_proxy_utils.py`.
