# Verification: image and control transport contracts

Date: 2026-10-04 (Europe/Kiev). Base HEAD: `282ce147038ac53b72bca30d69c4ad9a9ac1b7cc`.
Exactly three source rows: UP-PR-2508, UP-PR-2513 and UP-PR-2537.
Local working-tree verification; no commit, push, release, deployment or cloud gate is claimed.

## Findings and corrections

### UP-PR-2513: empty control payload and transport-generated media type

The existing case-insensitive replacement already removes duplicate media-type spellings for nonempty JSON/SDP. A zero-byte payload was treated as a body, so its Content-Type survived. Normalizing it to None fixed the argument-level regression, but real aiohttp POSTs still generated application/octet-stream. The final correction also suppresses the automatic Content-Type field for bodyless requests in both direct and routed transports. Nonempty bytes, query parameters, credentials, native first-header spelling/position and other routing behavior are preserved.

### UP-PR-2537: incompatible Images fallback

The dedicated host resolver preferred Sol correctly, but its fallback list still included Luna, the host whose forced image-generation rejection the source report describes. When Sol/Astra were unavailable or suppressed, a visible Luna won over 5.5. Images now choose Sol, Astra, then 5.5, with the existing Sol default when none is visible. Default account probes retain their Luna-then-5.5 policy. Public gpt-image model names, image-tool configuration, reference-image bytes and public request-log model names remain preserved.

### UP-PR-2508: retained inline-image sessions

Existing bridge behavior is confirmed through real local WebSocket traffic. Text, an admitted valid inline PNG, then text with the image in history share one upstream connection and prompt-cache identity; image bytes remain verbatim. Invalid-image rejection settles usage and allows a later text request on the same account. A silent origin under the two-second request budget receives one dispatch, then terminates and settles. The existing long-budget test permits the initial attempt plus one pre-created retry; it also passes. This batch preserves that bounded retry policy and does not claim a universal prohibition on all pre-created retries.

The older main requirement still stated a blanket bypass for all images. It now includes the already implemented bounded PNG/JPEG exception, local oversize rejection and existing fallback/retry boundaries. The overlapping active upstream change is left untouched.

## Reproduction and runtime evidence

| Command / scope | Result |
|---|---|
| `uv run pytest -q tests/unit/test_host_models.py tests/unit/test_codex_upstream_paths.py -k 'images_exclude_luna or images_skip_suppressed or removes_content_type_when_no_payload' --show-capture=no --tb=short` before fixes | 4 failed, 1 passed, 72 deselected: three Luna selections and one empty-body media type |
| First new integration run after argument-level correction | Four empty-POST cases found automatic application/octet-stream; direct wire assertions drove the additional transport fix |
| Final `uv run pytest -q tests/integration/test_image_control_transport_contracts.py tests/unit/test_host_models.py tests/unit/test_codex_upstream_paths.py --show-capture=no --tb=short` with the native helper environment below | 112 passed, no skips, 42.09s |
| `uv run pytest -q tests/unit/test_images_translation.py tests/unit/test_http_bridge_inline_image_admission.py tests/integration/test_http_bridge_inline_images.py tests/integration/test_proxy_images.py --show-capture=no --tb=short` | 169 passed, no skips, 140.95s |

The final new suite has 35 cases: three bridge route forms, invalid/silent image terminal controls, twelve native/SDK JSON/SDP/empty-body control routes, six Python/native routed HTTP-proxy wire cases, and twelve Images generation/edit/host/alias cases. Canonical Images routes work and their slash variants retain the documented 405 refusal without dispatch. Two early harness assumptions (Images slash acceptance and the JSON edit images shape) were corrected to the existing product contract; they are not product fixes.

The native wire cases use the existing `target/debug/codex-lb-native-egress.exe` via `CODEX_LB_NATIVE_EGRESS_TEST_BINARY`. Its SHA-256 is `BBD2BB52E5FE9989151E245A5CA7E3A280D292C304B2540EC68417973205466D`. Native cases forbid Python fallback and executed successfully; this batch did not rebuild Rust.

Origins and error frames are synthetic local HTTP/WebSocket servers. Routes, account selection, API-key admission, request logs and reservations use the application and isolated SQLite. The compatible-host origin deliberately rejects Luna, modeling the source report; it does not certify current live provider capabilities. Completed requests settle reservations, terminal image requests leave no reserved row, and the imported account remains active.

These two final selections contain 281 distinct passing cases. They are focused subsystem evidence, not full-repository or exact-head cloud CI evidence. Both emitted the existing Starlette BlockingPortal deprecation warning; neither skipped cases.

## Static and specification checks

- Scoped Ruff check and format check: PASS for both app files, both unit files and the new integration suite.
- Scoped `uv run ty check` on the same five files: PASS.
- Proxy architecture, cancellation safety and timing seam scripts: PASS.
- Settings tiers: PASS, 98/98 fields.
- Simplicity budgets: PASS; no configuration, dependency, migration, README or dashboard surface added.
- `npx --yes @fission-ai/openspec@1.11.0 validate --specs --strict --no-interactive`: 68/68 PASS.
- Strict validation of this change: PASS.
- All three delta requirement blocks equal their synchronized main blocks.
- `git diff --check`: PASS.

## Completeness, correctness and coherence

| Dimension | Assessment |
|---|---|
| Completeness | Three selected source rows have current evidence and local closure; six tasks complete |
| Correctness | Both runtime defects reproduced; real-origin tests verify corrected headers/host choices and retained bridge behavior, with separate unit negatives and full focused existing suites |
| Coherence | Existing account ownership, reservation settlement, public model identity and bounded retry policy preserved; normative requirements and explanatory context synchronized |

No unresolved critical finding blocks this local scope. Verification was performed in this task, including a separate final source/spec/baseline review; no independent reviewer agent was used.

## Preservation and residual scope

The initial snapshot contains 84 dirty/untracked files. Outside the four intended overlaps (proxy.py, responses spec/context and issues-check.md), all 80 preexisting dirty paths remain byte-identical. Removing the four added proxy lines reconstructs its exact baseline hash; earlier context remains a byte-preserved prefix. The main spec keeps all unrelated requirements, replacing only the old image-bypass block and appending the control requirement. Initially clean host, unit-test and Images spec/context files have focused changes; the new integration/change artifacts are additive.

Exactly the three selected source rows changed. The latest registry summary records 43 local closures, 6 partial rows and 248 unchecked rows out of 297 source entries. Historical counts and reports remain historical.

Live vendor image validation, #903 traffic/cache percentages, real client/provider acceptance, WSS fingerprint parity, public packages, production, cloud CI and F-045/CI-04 aggregate stability remain outside this local result. No unrelated active OpenSpec change was archived.

## Final source fingerprints

| Path | SHA-256 |
|---|---|
| `app/core/clients/proxy.py` | `d6679d2077ec8f7e44c0c3ce52c1469b5ff71919ed2a4948ae1844f44cff6858` |
| `app/core/openai/host_models.py` | `6371aafe5e2626a0bba9a7ecd5715dbe036155bcd51238c0975ff3671971ed1d` |
| `tests/unit/test_codex_upstream_paths.py` | `d7443f49d2989c5d38c34d48f86ee363e883baf1e40f1bd6280977d625101a05` |
| `tests/unit/test_host_models.py` | `7337fd9bd0e79902f1acea118240b81a2734c0d33b4af1c97944d247417d84e3` |
| `tests/integration/test_image_control_transport_contracts.py` | `fecf0ad6b32a68342e216f8f4f2ac06fd97d31184e983733e9dfb472d168d0ab` |
