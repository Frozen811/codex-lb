# Why

Standalone Codex web search (`POST /alpha/search`) exhibits two compatibility issues (Issue #2128):
1. `POST /v1/alpha/search` returns HTTP 405 Method Not Allowed because the route is currently only registered under `/backend-api/codex/alpha/search`. Clients targeting the `/v1` prefix fail.
2. In `codex_control_request` (`app/core/clients/proxy.py`), `upstream_headers["Content-Type"] = content_type` blindly sets the capitalized key even when `_build_upstream_headers` already preserved or set a lowercase `content-type` header. This duplicates the header on the wire (`content-type` and `Content-Type`), causing upstream to reject requests with `400 Unsupported content type`.

# What Changes

1. Register `codex_alpha_search` on both `@router.post("/alpha/search")` and `@v1_router.post("/alpha/search")` in `app/modules/proxy/api.py`.
2. In `codex_control_request` (`app/core/clients/proxy.py`), replace `upstream_headers["Content-Type"] = content_type` with `_replace_header_preserving_position(upstream_headers, "content-type", content_type, fallback_name="Content-Type")`. If `payload is None`, strip all case variations of `content-type` from `upstream_headers`.

# Capabilities

## Modified Capabilities

- `responses-api-compat`: Standalone web search is available on both `/backend-api/codex/alpha/search` and `/v1/alpha/search`, and control requests do not duplicate `Content-Type` headers.

# Impact

Clients can perform standalone web search using either `/backend-api/codex/alpha/search` or `/v1/alpha/search` without 405 Method Not Allowed errors, and requests do not fail upstream with 400 Unsupported content type due to duplicate Content-Type headers.
