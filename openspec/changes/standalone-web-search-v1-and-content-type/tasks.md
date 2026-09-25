## 1. Implementation

- [x] 1.1 In `app/modules/proxy/api.py`, register `codex_alpha_search` with `@v1_router.post("/alpha/search")`.
- [x] 1.2 In `app/core/clients/proxy.py`, update `codex_control_request` to use `_replace_header_preserving_position` for `Content-Type` and avoid duplicate headers.

## 2. Regression Coverage

- [x] 2.1 Add test in `tests/integration/test_proxy_control_requests.py` verifying `POST /v1/alpha/search` forwards to upstream correctly.
- [x] 2.2 Add unit test verifying `codex_control_request` does not duplicate `Content-Type` when inbound headers contain lowercase `content-type`.

## 3. Validation

- [x] 3.1 Run unit and integration tests for web search and control requests.
- [x] 3.2 Run migration topology checks.
