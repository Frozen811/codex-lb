# Tasks: Bridge Anchor Rejection Stream Terminal, Desktop OpenAI Provider, and Telemetry Opt-Out Hardening

## 1. Responses Stream Terminal & Error Mapping (Issue #2493)
- [x] Set `yielded_any = True` when yielding `keepalive_event` in `app/modules/proxy/_service/http_bridge/streaming.py`.
- [x] Add `"bridge_previous_response_not_found"` to `SYNTHETIC_TRANSPORT_FAILURE_CODES` in `app/core/errors.py`.
- [x] Include `"bridge_previous_response_not_found"` in `native_transport_startup_failure` and `_stream_response_error_events` in `app/modules/proxy/api.py`.
- [x] Add `"bridge_previous_response_not_found"` to `_is_previous_response_not_found_public_error` in `app/modules/proxy/api.py`.
- [x] Add regression test coverage in `tests/unit/test_proxy_http_bridge.py`.

## 2. Desktop Built-In Provider Preservation (Issue #2262)
- [x] Document overriding `[model_providers.openai]` in `docs/client-setup.md`.
- [x] Provide sample snippet in `docs/examples/codex/config.toml`.
- [x] Add unit test in `tests/unit/test_codex_upstream_paths.py`.

## 3. Telemetry Opt-Out Hardening & Kill Switch (Issue #1844)
- [x] Update `TelemetryOptOut.occurred_at` type to `datetime | str` in `app/modules/telemetry/schemas.py`.
- [x] Synchronize snapshot transmission and opt-out with `_TRANSMISSION_LOCK` in `app/modules/telemetry/sender.py`.
- [x] Suppress identity creation in `app/modules/telemetry/api.py` when telemetry is disabled via environment variable.
- [x] Add unit test coverage in `tests/unit/test_telemetry_sender.py` and `tests/unit/test_telemetry_api.py`.
