# Local verification: telemetry and stateless key contracts

Date: 2026-10-03 (Europe/Kiev). Source HEAD: `282ce147038ac53b72bca30d69c4ad9a9ac1b7cc`; fixes are uncommitted working-tree changes. Existing sender/client/crypto source came from `cf0455a17ceb253b9657f50d66aa790c87aae102`. Pre-existing unrelated edits were preserved.

Exactly three registry entries: [UP-ISSUE-1844](https://github.com/Soju06/codex-lb/issues/1844), [UP-ISSUE-1843](https://github.com/Soju06/codex-lb/issues/1843), [UP-ISSUE-1572](https://github.com/Soju06/codex-lb/issues/1572). The upstream issue bodies were read; their original resolved claims are not treated as evidence for this checkout.

## Completeness and correctness

| Contract | Product evidence | Result |
| --- | --- | --- |
| Full local snapshot/decision/opt-out ordering | Actual aiohttp loopback collector plus real settings API and SQLite consent; gates at register/activate/snapshot, each with completion, cancellation, HTTP 503, and timeout | 12 races pass; final opt-out last, subsequent disabled sends silent, committed consent inactive |
| Fresh consent/identity before any protocol write | Existing sender unit refusal cases strengthened from register/activate to zero protocol requests | Inactive, replaced identity, and failed consent reads produce no network requests |
| Timestamp validation and canonical UTC | Invalid string/numeric input, valid offset string, naive and offset datetime; real opt-out receiver checks Z suffix | Malformed input rejected; valid input normalized without wire-field changes |
| Outbound signing | Loopback receiver verifies Ed25519 signatures for activation, snapshot, and opt-out using the registered public key | All signatures verified |
| Client-family allowlist | 11 persisted groups through real preview; 24 real Responses/Chat HTTP route variants across streaming/non-streaming and six user agents, actual loopback upstream and new-session log readback | CLI/Desktop groups aggregate correctly; private/missing groups become other; raw private names absent from preview |
| Stateless encryption key | Dashboard account import, persisted encrypted access/refresh tokens, fresh encryptors/settings, deliberately unusable default key-file path | Shared key decrypts credentials; no key file touched |
| Key selection and fingerprint | Explicit bytes/file/env precedence, blank fallback, invalid settings, independent sentinel sessions, different valid key and ciphertext rejection | Same selection for crypto/fingerprint; mismatch preserves original sentinel and does not expose either key |
| Cross-process key compatibility | Separate fresh Python writer and reader processes with synthetic env key and inaccessible default key file | Ciphertext readable across processes; no key file needed |
| Startup diagnostic | Real mismatch exception checked after final wording fix; existing transient-lock and exhausted-budget tests | Environment and file remediation supported; retry/refusal behavior preserved |

The initial 29-case regression run reported 15 failures and 14 passes. Thirteen failures were product regressions: nine dashboard-disable races and four timestamp validation/offset cases. Two failures were harness assumptions: a substring privacy assertion incorrectly matched `codex` in the application name, and the app lifespan had already stamped a different test key before the env override. The assertions now check private names and use a separate isolated sentinel database without deleting the application sentinel. Later boundary cases expand the product suite to 59 tests.

## Validation

One combined focused run passed **182 tests**:

```powershell
uv run --frozen pytest tests/integration/test_telemetry_key_contracts.py tests/unit/test_telemetry_sender.py tests/unit/test_telemetry_api.py tests/unit/test_telemetry_consent.py tests/unit/test_telemetry_snapshot.py tests/unit/test_crypto.py tests/unit/test_telemetry_migration.py tests/unit/test_settings_multi_replica.py tests/unit/test_settings_tiers.py -q --tb=short --show-capture=no
```

Two additional focused startup fingerprint lock tests passed, giving **184 distinct tests**. The final diagnostic wording was followed by a passing rerun of the account/key/mismatch integration test; that rerun is not added to the count. No full-repository test run is claimed.

- Ruff check and format: all changed application/test files pass (11 files formatted correctly).
- `uv run --frozen ty check app/modules/telemetry app/core/config/key_fingerprint.py`: pass.
- `uv run --frozen python scripts/check_cancellation_safety.py`: pass.
- `bunx @fission-ai/openspec@1.11.0 validate repair-telemetry-and-stateless-key-contracts --strict`: pass.
- `bunx @fission-ai/openspec@1.11.0 validate --specs --strict`: **68/68 pass** after synchronization and final diagnostic contract update.
- Diff whitespace check: pass. Existing Starlette BlockingPortal deprecation warning remains; no test skip or failure.

## Coherence review

Implementation was reviewed against every modified/added requirement and scenario. The API and sender share one process lock, consent is freshly read before protocol writes, complete send retries remain bounded by the existing timeout, and cancellation unwinds ownership. API background work receives an immutable identity, never the request AsyncSession. Timestamp validation precedes signing. Key selection and client mapping remain their existing shared implementations; only the misleading key diagnostic and their incomplete specification change. No dependency, schema, configuration surface, dashboard pixels, or simplicity-budget growth. No critical unresolved discrepancy in the local contract.

## Residual scope

The lock guarantees ordering within one process. It cannot recall an already transmitted snapshot or fence another replica's in-flight request. Collector authority/generation protocol, collector retention, identifier-bearing lifecycle observability deferred by the original issue, deployed PostgreSQL replicas, real client applications/accounts, cloud CI, public artifacts, and production deployment remain unverified. These three rows close only their documented local scope. No commit, push, PR, release, collector change, or deployment was performed.
