# Local verification and first full-CI repair

Date: 2026-10-08, Europe/Kiev. The user explicitly authorized committing **all** local work to fork main and continuing complete CI through success.

## Preserved publication

The initial manifest contains 77 dirty/untracked paths spanning the auth/credit, image/compact/terminal and input/forwarding packages. Their bytes were backed up outside the repository. Every staged blob was checked against `git hash-object --path` before commit. All 77 paths were committed as `71c5332ca24666455aa6836f0bd05f9e8b304cc2`, pushed without force to `Frozen811/codex-lb:main`, and verified by `git ls-remote`. No prior work was discarded.

## CI #86 evidence and repairs

[Full CI #86](https://github.com/Frozen811/codex-lb/actions/runs/37818859876), attempt 1, ran the complete 35-job matrix on that SHA and completed **FAILURE: 25 success /10 failure**, including failed dependent aggregates. Docs, Windows startup, release guards and simplicity completed successfully. The source was genuinely tested across SQLite, PostgreSQL, MySQL, bridge, browser, Rust, Docker, Helm and Nix; this first run is historical and is not represented as green.

The distinct failures were:

- Six `ty` diagnostics: two account fixture reads and one selection result needed explicit non-null assertions. Full `uv run ty check` now passes.
- Edu quota fixture: `credits_has=True` with a zero balance was still expected to activate an exhausted account. The current owning spec requires spendable credits, so the fixture now expects `quota_exceeded`; positive-balance and unlimited-credit controls remain.
- Compact slash fixture: two already implemented aliases were still expected to return 405. Both now assert 200, no redirects, and developer content on the actual upstream wire.
- Trusted-capability inventory: both compact aliases were missing from the explicit fail-closed inventory. Adding them also expands the route denial controls; no gate is bypassed.
- Direct WS retry: four blank async-ID cases actually retried despite being unsafe. The same-owner fresh-resend classifier now requires boolean markers and nonblank async IDs. Bad histories keep `stream_incomplete` on v1 or `previous_response_not_found` on the native endpoint, create no additional connection and send no fresh request. Cross-account portability and same-owner account-bound history remain separate existing policies.

## Windows checks repaired without falsifying evidence

The working catalog had CRLF hash `8127b8c46c8df716980afa7efed6d9ad6ac755ace20fd15d7bf5044df5d5baa2`, while its exact Git blob has the historical provenance hash `de111010ad347d62a87346760fb6746bc1a490483359b8cefd66e57daa0ed576`. Removing only CRLF conversion reproduced the Git blob byte-for-byte. A specific `.gitattributes` rule pins catalog JSON to LF; provenance and catalog content were not rewritten.

Artifact file flushing and atomic replacement remain mandatory. Directory fsync is skipped only where POSIX directory handles are unsupported; forced supported-platform open/sync failures still propagate. POSIX 0600 mode checks remain strict, while Windows checks its writable mode without claiming a POSIX mask.

The repeated-marker Chat test now uses the existing VirtualScheduler. It proves the original 1 ms probe and 50 ms signal discovery behavior, marker consumption, handoff and complete task/timer cleanup. No production timeout or runtime Chat code changed.

## Final local checks

Disjoint acceptance: **579 PASS**, no skips or exclusions:

```text
uv run pytest -q tests/unit/test_codex_body_fixtures.py tests/unit/test_codex_body_sanitizer.py tests/unit/test_traffic_artifacts.py tests/unit/test_responses_streaming_timeout_hardening.py --tb=short --show-capture=no --timeout=45
```

**276 PASS**, including the previously failing catalog and both CLI writes, artifact error controls and timeout hardening.

```text
uv run pytest -q -n 4 --dist worksteal tests/integration/test_accounts_api_extended.py tests/integration/test_five_registry_contracts.py tests/integration/test_daybreak_capability_routes.py tests/integration/test_background_jobs_runtime.py tests/integration/test_load_balancer_multi_replica.py --tb=short --show-capture=no --timeout=45
```

**281 PASS**, including all newly exposed cloud fixture failures and the modified nullable fixtures.

```text
uv run pytest -q -n 4 --dist worksteal tests/integration/test_proxy_websocket_responses.py -k replays_client_full_resend_previous_response_miss --tb=short --show-capture=no --timeout=45
```

**20 PASS**: both actual WS routes, no-call and valid function/custom positive controls, whitespace/null identities, string/numeric/null markers, original envelopes and no additional dispatch.

```text
uv run pytest -q tests/unit/test_proxy_utils.py -k 'chat_startup_probe_consumes or websocket_client_previous_response_full_resend_is_retry_safe or websocket_client_input_is_self_contained' --tb=short --show-capture=no --timeout=45
```

**2 PASS**, including deterministic repeated markers. Earlier four-failure red controls and cloud failures remain historical; reruns are not counted twice.

Whole-repository Ruff, formatting (1498 files) and ty pass. Architecture, cancellation, timing, settings (98/98), migration topology (272 revisions, unchanged single head) and simplicity checks pass. Strict pinned OpenSpec change/main validation passes, **68/68** specs; strict MkDocs passes. Three added requirements across compatibility-tooling and Responses are synchronized with stable context. Whitespace checks pass.

Remaining work in this active change is exact-SHA complete cloud verification and publication evidence. Source queue remains 338 records with 121 local closures, 7 partial and 210 unverified; no additional upstream task was closed by the CI repair. Existing public/provider/production boundaries remain.
