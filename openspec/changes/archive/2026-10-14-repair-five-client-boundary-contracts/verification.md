# Five client boundary contracts - local verification, 2026-10-14

Initial HEAD: `cfc939cc69e6534996365a348b74eaf414283f34`, branch `main`. The initial working tree contained 26 dirty/untracked files from previous work. This batch owns exactly five initially unverified rows: UP-PR-2589, UP-PR-2593, UP-ISSUE-2594, UP-ISSUE-2601 and UP-ISSUE-2602. No commit, push, PR, merge, release or deployment was performed.

## Completeness, correctness and coherence

| Dimension | Result |
|---|---|
| Completeness | Eight implementation/verification/closure tasks complete; five source rows updated and reread. |
| Correctness | Six delta requirements mapped to application code and public/adapter regressions; canonical specs synchronized. |
| Coherence | Existing session leases, exact native identity allowlist, image tool translation and account recovery compare-and-set retained. No new operator setting or migration. |

| Row | Result and evidence |
|---|---|
| UP-PR-2589 | Existing exact CCodex allowlist independently verified: 12 real HTTP route cases (canonical/slash, public/Codex), six native WS route cases, known identities and negative lookalikes. Existing builder matrix tests cover originator-only, UA-only and combined signals. HTTP transport policy remains honored. Fixed missing urllib3 package floor to >=2.8.0; lock version unchanged and built wheel METADATA rejects 2.7.0. |
| UP-PR-2593 | Removed GPT Image 2's blanket transparent-background rejection; shared format guard refuses transparent JPEG before dispatch with param=output_format. Twelve model/format unit cases plus 48 route cases cover PNG/WebP/JPEG, generation/edit, JSON/SSE, public/native and unchanged slash refusals. Tool settings and exact returned bytes retained; streaming edits keep image_edit event names. |
| UP-ISSUE-2594 | Reproduced QueueFull and lost output at 65 frames. Message queue now has a 4096-event cap and 32 MiB accumulated payload budget, charging UTF-8, binary and interpreted payload copies/metadata. Bursts of 65/256 text, binary and interpreted frames preserve FIFO and send ACK progress. Byte/count overflow preserves accepted frames, fails actual pending sends, aborts and finalizes once. Cancellation, reader failure, large-frame compatibility and byte reclamation covered alongside existing helper/chunking/close tests. |
| UP-ISSUE-2601 | New direct-session error boundary translates aiohttp client errors/payload errors and timeouts into sanitized transport_error. Browser callback uses real local TCP HTTP and durable SQLite status; manual callback and device-start API paths return their existing safe envelopes/results. Constant public message and exception-type-only warning exclude private URL/code/verifier text. Cancellation propagates and session lease cleanup runs. Existing callback race/replay/device lifecycle tests passed. |
| UP-ISSUE-2602 | Current production code required no additional change: five independent real account API/SQLite cases establish weekly-only primary=604800 seconds with secondary=0/no reset, canonical prolite alias, early reset and normal rollover recovery, failed/exhausted holds and concurrent operator pause. Successful recovery subsequently serves gpt-6-astra through the real public Responses route with the recovered account. Existing usage updater suite preserves ordinary real-429 cooldown and CAS guards. |

## Final test evidence

**662 distinct PASS, 0 skips, 0 xfails.** Final selections use disjoint test files:

1. `uv run pytest -q tests/unit/test_native_websocket_buffering.py tests/unit/test_native_egress.py tests/unit/test_native_egress_websocket_chunking.py tests/unit/test_oauth_transport_errors.py tests/unit/test_oauth_client.py tests/unit/test_oauth_route.py tests/unit/test_images_schemas.py tests/unit/test_images_translation.py tests/unit/test_proxy_upstream_fingerprint.py tests/unit/test_five_runtime_contracts.py tests/unit/test_usage_updater.py --tb=short --maxfail=3`: **487 passed** in 14.19s.
2. `uv run pytest -q tests/integration/test_proxy_images.py tests/integration/test_client_boundary_contracts.py --tb=short --maxfail=3`: **139 passed** in 159.92s.
3. `uv run pytest -q tests/integration/test_oauth_flow.py --tb=short --maxfail=2 -k 'callback or device or network or transport'`: **36 passed**, 27 deselected, in 18.28s.

Each final run reports the existing Starlette BlockingPortal deprecation. Intermediate harness failures were corrected: native edit uses JSON rather than multipart, Images trailing-slash aliases intentionally return 405, edit streaming emits image_edit.completed, and model eligibility is proven by public inference rather than a nonexistent registry.get API. These are not counted as product defects or final passes. Test storage uses the existing disposable tests/runtime.py setup; no application/production database was used.

## Static, package and specification checks

- Repository-wide Ruff check passed; Ruff format check passed on **1557 files**. Scoped ty passed on all three changed application files.
- Proxy architecture, cancellation safety, timing seams, settings tiers, migration topology and static migration-duration guards passed unchanged. Topology remains 275 revisions with the existing 20261010_000000_add_source_catalog_discovery head; runtime migration duration was not measured.
- Simplicity budgets passed: README 218/225 lines, headings 10/10, env 54/60, nav 5/5 and tracked root extras 0/0.
- `uv lock --check --offline` passed. `uv build --wheel --offline --out-dir C:/Users/ext/.codex/visualizations/2026/10/14/01a138a4-6571-7a31-8c62-a9cb0d22d563/client-boundary-wheel` produced codex_lb-1.25.1-py3-none-any.whl. Its Requires-Dist metadata contains urllib3>=2.8.0 and the specifier rejects 2.7.0, accepts 2.8.0. This is a local build, not a published package.
- Strict change validation passed; canonical strict validation passed **68/68**. Two Images requirements were modified, four requirements added to three other capabilities, and all four context docs synchronized. Documentation sync preserves original prefixes outside the two modified Images requirement blocks and original context prefixes.
- Full application/test/spec diff reviewed; whitespace check passed. The saved closure audit proves **25/25 unrelated initial dirty/untracked files unchanged** and **354/354 other source rows byte-identical**. Queue: 359 records, 203 local closures, eight partial, two not applicable, 146 unverified. Exact closure hashes and selected saved-row readback are in closure.json.

## Practical limits

Local Windows/Python, disposable SQLite, a real local callback TCP listener and fake upstream transports establish these contracts. The PNG fixture is a valid one-pixel transparent RGBA image; WebP output is a synthetic byte fixture, proving byte preservation rather than provider alpha correctness. The native budget is accumulated payload bytes, not total process RSS; a lone large frame and fragment reassembly retain the existing helper frame limit. Pro Lite recovery uses successful HTTP probe status plus fresh available usage; the historical reporter's lost account row and actual provider terminal are not attested. Live CCodex/Desktop/provider/native helper deployment, PostgreSQL/MySQL execution, distributed races, hosted current-head CI, public artifacts and production remain separate. Other registry residuals and partials remain unchanged.
