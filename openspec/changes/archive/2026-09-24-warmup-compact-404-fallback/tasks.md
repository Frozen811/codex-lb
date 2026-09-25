## 1. Implementation

- [x] 1.1 Add plain responses fallback handling for 404 responses in `_submit_warmup_request` (`app/modules/proxy/_service/warmup.py`).
- [x] 1.2 Import `stream_responses` and `ResponsesRequest` and implement the minimal fallback stream request.
- [x] 1.3 Ensure load balancer success and request log metadata are recorded on successful fallback.

## 2. Regression coverage

- [x] 2.1 Add integration test in `tests/integration/test_proxy_warmup.py` verifying that when `core_compact_responses` fails with 404, `/v1/warmup` transparently falls back to plain responses and succeeds.

## 3. Verification

- [x] 3.1 Run `uv run pytest tests/integration/test_proxy_warmup.py`.
- [x] 3.2 Run `uv run ruff check app tests`.
- [x] 3.3 Validate OpenSpec specs: `bunx @fission-ai/openspec@1.11.0 validate --specs`.
