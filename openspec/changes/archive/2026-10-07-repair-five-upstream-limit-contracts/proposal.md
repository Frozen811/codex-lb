## Why

Five unverified registry records cover the same failure pipeline: usage-limit classification, account exclusion, pool termination, client reset metadata, and retry-health reset metadata. Existing code needs independent product-path verification; malformed reset values can interrupt terminal rendering, and the usage-limit spec still promises unsafe reclassification of request errors.

## What Changes

- Preserve finite upstream reset metadata while ignoring malformed values at error parsing and terminal rendering boundaries.
- Align usage-limit requirements with the existing protection against request content echoed in `invalid_request_error` messages.
- Verify exactly UP-PR-2449, UP-PR-2439, UP-PR-2440, UP-PR-2403, and UP-PR-2391, including terminal frames, keyed settlement, pool bounds, and original quota terminals after failed replay.
- Record focused evidence and close only these five registry rows before the authorized local commit on `main`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: finite reset metadata and safe code-less usage-limit classification across error delivery forms.

## Impact

Source changes: `app/core/errors.py` and `app/core/openai/models.py`. Existing parser fallback in `app/modules/proxy/helpers.py` uses the same typed model and needs no separate change. Added tests: `tests/unit/test_openai_errors.py`, `tests/integration/test_proxy_transient_retry.py`, and `tests/integration/test_http_responses_bridge.py`. Existing focused suites cover classification, pool bounds, HTTP bridge replay, and keyed health settlement. Documentation changes: the Responses capability spec/context, this change's artifacts, and `issues-check.md`. No new settings, migrations, dependencies, release, or deployment.
