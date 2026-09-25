# Change: Transparent Warmup Fallback on Compact 404

## Why
Issue #1895 identified that `POST /v1/warmup` submits upstream pings using compaction (`core_compact_responses()`), which appends `{"type": "compaction_trigger"}` to the request body. On certain Codex upstream endpoints or models that do not support compaction triggers, upstream returns HTTP 404 "Not Found", causing all accounts in the pool to fail warmup with `upstream_error / "Not Found"`.
While PR #1963 fixed the probe half of #1895 (`PROBE_MAX_OUTPUT_TOKENS = 16`), the warmup path still permanently fails when upstream 404s the compaction trigger. Transparently falling back to a minimal plain Responses API request allows `/v1/warmup` to complete successfully, waking the rate limiter and auto-starting quota windows without operator intervention.

## What Changes
1. In `app/modules/proxy/_service/warmup.py`, catch `ProxyResponseError` with `status_code == 404` (or `upstream_status_code == 404`) during `_submit_warmup_request`.
2. When caught, fall back to sending a minimal streaming Responses API request (`stream_responses`) with `max_output_tokens=16`, `stream=True`, `store=False`.
3. If the fallback request succeeds, mark the account successful in the load balancer and record the request log accordingly.
4. Add integration tests proving transparent fallback to plain responses when compact returns 404.

## Capabilities

### Modified Capabilities
- `proxy-warmup`: Add requirement and scenario for transparent fallback to minimal plain Responses API requests when upstream returns 404 to compaction pings.

## Impact
- `app/modules/proxy/_service/warmup.py`
- `tests/integration/test_proxy_warmup.py`
- No database migrations, no settings changes, no breaking API changes.
