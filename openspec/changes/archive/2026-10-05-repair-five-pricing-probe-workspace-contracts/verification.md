# Verification: five pricing, probe, bridge and workspace contracts

Date: 2026-10-05, Europe/Kiev. Base HEAD: `f987d08e69978ee6452c4e5997b11e80a81ba5f2`.
Selected exactly five previously unverified source rows: **UP-PR-2547,
UP-PR-2553, UP-PR-2555, UP-ISSUE-2560, UP-PR-2573**.
The previous five-item repair package and upstream registry refresh were already
dirty and are preserved. No commit, push, merge, release or deployment was made.

## Source evidence

Fresh GitHub REST reads confirmed all four PRs open and not merged:

| Object | Exact inspected head | Scope |
| --- | --- | --- |
| [PR 2547](https://github.com/Soju06/codex-lb/pull/2547) | `974630bf29358b19c345bf80b347ea7b27f176ad` | Ultrafast pricing and exact monetary settlement |
| [PR 2553](https://github.com/Soju06/codex-lb/pull/2553) | `6387ab54b80b968d0c0834d77a36b51c99beced0` | Helm startup timing |
| [PR 2555](https://github.com/Soju06/codex-lb/pull/2555) | `b4533f4964e4d1282dfb0bc5ca2cae892678b223` | Detach terminal append at the delivery bound |
| [Issue 2560](https://github.com/Soju06/codex-lb/issues/2560) | Issue body read live; OPEN | Shared CCodex native identity classification |
| [PR 2573](https://github.com/Soju06/codex-lb/pull/2573) | `06b86fefef0f3320a32997f13f863fa188796925` | Exact workspace deactivation and safe failover |

Upstream implementation and test patches informed this repair. Pricing and
workspace regression cases were adapted from those public PRs; Helm and SQLite
writer tests retain their upstream structure. Gateway wire tests, expanded
cache-write/overlay/ownership cases and current failover adaptation were added
locally. The upstream dependency/release/contributor changes were outside this
bounded repair package.

[OpenAI pricing](https://developers.openai.com/api/docs/pricing), checked live,
confirms Astra Ultrafast ordinary input/cached read/cache write/output rates of
60/6/75/300 USD per million tokens in short context and 120/12/150/450 in long
context. These rates and provenance were added to the existing bundled snapshot.

## Reproduction and implementation

Before source edits, the focused runtime/API selection reported **58 failed,
31 passed, 355 deselected** in 45.60s. Failures included 18 gateway header cases,
workspace classification/action, six bundled pricing cases, both actual SQLite
writer probes, 16 monetary route cases, workspace failover and refresh. The
separate Helm selection reported **6 failed** in 2.88s.

- **2547:** explicit Ultrafast fields include all four disjoint input/output
  categories and both contexts. Adapters validate complete price groups and
  preserve them through snapshots, compatible refreshes and offline startup.
  Decimal source scaling and final microdollar products prevent integral-boundary
  loss while retaining fractional truncation. Effective response-tier logs and
  settlement agree, including downgrade, context threshold, writes, repeated
  finalization and the next admission being blocked.
- **2553:** default probe timing remains 5/2/1/30/1. Schema rejects null,
  boolean, fractional and invalid-range values. Handler/port remain fixed;
  readiness and liveness are unchanged in all six overlays. External-DB and
  staging test fixtures provide the documented synthetic database Secret source.
- **2555:** timeout and caller cancellation stop waiting without cancelling the
  tracked append. Both rows_v1 and chunks_v2 writers finish after releasing a
  real blocked SQLite statement; a second connection acquires BEGIN IMMEDIATE.
  The real durable coordinator rejects a late append after settlement, with
  `late_results == [False]`, incomplete spool and no replay events. Existing
  attempt cleanup, downstream delivery and shutdown tests pass.
- **2560:** exact originators and slash-delimited gateway User-Agent prefixes
  use the shared classifier. HTTP and both WebSocket builders retain identity
  and version; lookalikes still normalize. Eight actual API-to-loopback upstream
  cases cover both gateway identities, HTTP/WS transport and canonical/backend
  routes with GPT-6.1 Sol. Existing stable-version/offline cache tests pass.
- **2573:** only the exact code becomes `account_unavailable` and permanent
  workspace evidence. Current `failover_outcome` walk endings are retained,
  unavailable owners cannot retry and the account is excluded from selection.
  Keyed status-error health uses existing deferred settlement machinery.
  Twenty-two route cases cover fresh/owned/keyed/unkeyed requests, both compact
  routes, hard file pins, SSE failures before/after visible text, second-request
  selection and unknown/code-less 402 controls. Usage refresh preserves an
  excluded workspace while its same-identity sibling successfully stores usage.

## Current-code checks

Selections below overlap; they are not an aggregate unique-test count.

| Check | Result |
| --- | --- |
| Pricing/catalog/metadata/key service/failover/balancer/fingerprint modules | **810 passed**, 8.39s |
| Ultrafast actual API routes including mixed writes and effective default | **36 passed**, 40.62s |
| Workspace status/SSE/compact/ownership/bare-402 routes | **22 passed**, 26.76s |
| Gateway actual loopback HTTP/WebSocket upstream | **8 passed**, 11.28s |
| Usage updater complete module after sibling-success assertion | **158 passed**, 3.13s |
| Codex version + three terminal batcher/writer/handler modules | **57 passed**, 2.85s |
| New runtime/corrected catalog/both writer-format selection | **94 passed**, 2.55s |
| Helm startup/shutdown/replica/monitoring/external-secret modules | **141 passed**, 67.93s |
| Broader terminal/late-clear/stalled selection | **91 passed**, 9.18s; baseline admission warning below |
| Existing load-balancer refresh module | **94 passed, 3 skipped**, 2.28s; obsolete T21 cases below |
| Helm lint --strict: default and all six overlays | **7/7 PASS** |
| Ruff check and format checks on changed source/tests | **PASS**, 34 checked format paths |
| `uv run ty check app` | **PASS** |
| Proxy architecture, cancellation safety, timing seams, settings tiers | **PASS**; 98/98 settings, no new settings |
| OpenSpec 1.11.0 strict change validation | **PASS** |
| OpenSpec 1.11.0 strict main-spec validation | **68 passed, 0 failed** |
| Exact delta/main requirement comparison | **7 requirements / 15 scenarios**, six matching capabilities |
| `git diff --check` | **PASS** |

Focused commands:

```text
uv run pytest tests/unit/test_pricing.py tests/unit/test_pricing_catalog.py tests/unit/test_metadata_scheduler.py tests/unit/test_api_keys_service.py tests/unit/test_failover_foundation.py tests/unit/test_load_balancer.py tests/unit/test_proxy_upstream_fingerprint.py -q --tb=short
uv run pytest tests/integration/test_api_keys_api.py -k ultrafast_cost_logs -q --tb=short
uv run pytest tests/integration/test_proxy_transient_retry.py -k "deactivated_workspace or bare_402 or keyed_workspace" -q --tb=short --show-capture=no
uv run pytest tests/integration/test_gateway_wire_contracts.py -q --tb=short
uv run pytest tests/unit/test_usage_updater.py -q --tb=short --show-capture=no
uv run pytest tests/unit/test_codex_version.py tests/unit/test_http_bridge_event_batcher.py tests/unit/test_http_bridge_terminal_spool_handler.py tests/unit/test_http_bridge_terminal_append_writer_lock.py -q --tb=short --show-capture=no
uv run pytest tests/unit/test_five_runtime_contracts.py tests/unit/test_pricing_catalog.py tests/unit/test_http_bridge_terminal_append_writer_lock.py -q --tb=short --show-capture=no
uv run pytest tests/unit/test_helm_startup_probe.py tests/unit/test_helm_shutdown_contract.py tests/unit/test_helm_replica_artifacts.py tests/unit/test_helm_monitoring_artifacts.py tests/unit/test_helm_external_secrets.py -q --tb=short
uv run pytest tests/unit/test_http_bridge_event_batcher.py tests/unit/test_http_bridge_terminal_spool_handler.py tests/unit/test_http_bridge_terminal_append_writer_lock.py tests/unit/test_proxy_http_bridge.py -k "terminal or late_clear or stalled" -q --tb=short
uv run pytest tests/unit/test_proxy_load_balancer_refresh.py -q --tb=short --show-capture=no
uv run ty check app
uv run python scripts/check_proxy_architecture.py
uv run python scripts/check_cancellation_safety.py
uv run python scripts/check_proxy_timing_seams.py
uv run python scripts/check_settings_tiers.py
npx --yes @fission-ai/openspec@1.11.0 validate repair-five-pricing-probe-workspace-contracts --strict
npx --yes @fission-ai/openspec@1.11.0 validate --specs --strict
git diff --check
```

Helm 3.19.0 was downloaded to an isolated temporary tool directory from the
official distribution and its SHA256 verified against the official checksum:
`6488630c2e5d5945ed990fa02fd9e99f9c6792cdbcd79eb264b6cfb90179d2d1`.
The tests had that directory prepended to PATH; no Helm skip was used. No
dependency or lockfile changes were needed.

## Review, preservation and boundaries

Current source review verified that the new monetary path retains cached-write
partitioning, all permanent routing evidence is code-specific, walk exclusions
remain explicit, and keyed workspace health follows reservation settlement.
The terminal change preserves existing task tracking, attempt fencing and shutdown
ownership. The complete public compact ownership check uses an actual file pin;
an unpinned opaque item alone does not establish that compact ownership contract.

The three refresh-module skips are existing tests at lines 2122/2192/2264 whose
own reasons say per-account T21 locking eliminates their old version-conflict
scenario. This selection is recorded with its skips and is not aggregate-green.

The broader terminal selection emits an existing AdmissionLease garbage-collection
warning. A temporary diagnostic plugin traced it to
`test_retry_http_bridge_precreated_request_keeps_accepted_replay_on_hard_capable_session_owner[capacity_terminal_pre_staged]`
and request_submit's precreated admission path. The exact test still passes and
emits the same warning with the original HEAD `append_terminal_event` restored
only in the test process (**1 passed**, 0.92s). No source file was restored or
changed for that experiment. This adjacent lifecycle warning remains an open
verification residual; the broader ownership surface is not declared clean.

Full CI, POSIX, hosted-provider model acceptance, Kubernetes runtime/kubeconform,
distributed database contention, published artifacts and production are outside
this local batch. Existing F-045, issue 1981's writer-slot readiness/probe scope,
and shutdown mid-statement cancellation remain outside PR 2555's bounded scope.
CCodex release shipping and optional error-code differentiation are not claimed.

All previous dirty files remain preserved. Unchanged paths were checked against
the initial SHA256 manifest. The intentional shared balancer file reconstructs
the original checksum after removing this batch's three edits. The four shared
spec/context prefixes match their original manifest checksums. Exactly the five
selected source rows are closed locally; the other **333 source rows** remain
byte-identical. Final queue: **338 records, 70 locally closed, 7 partial,
261 unverified**. Registry readback and archive completion are checked before the
final report.
