# Proxy Runtime Observability Context

## Purpose and Scope

This capability defines what operators should be able to see in the live server console while debugging proxy traffic.

See `openspec/specs/proxy-runtime-observability/spec.md` for normative requirements.

## Authorization field redaction

Unquoted authorization values are masked through the current line end. Commas,
ampersands, malformed parameters and names like `status` cannot identify a safe
diagnostic boundary; a previous `[REDACTED]` marker also does not prove that a
following credential tail is safe. Complete quoted values retain their quotes
and adjacent fields. Subsequent lines and structured log extras remain useful
for diagnostics. This policy applies to explicit Authorization fields at WARNING
or higher and to error-log fields; existing lower-level redaction boundaries stay
unchanged.

For example, `authorization=Digest username="a,b", response="QA_SENTINEL", status=failed`
renders as `authorization=[REDACTED]`. Put `status=failed` in a structured extra
or on the next line to retain it. Generic Basic/Bearer tokens outside an explicit
authorization field keep their existing separator behavior.

The independent UP-ISSUE-2028 audit found partial masking in the earlier source;
text/JSON formatting, exception rendering, actual log-file writes, quoted fields
and CR/LF idempotency now have regression coverage.

## Decisions

- **Timestamps are always on:** timestamped console logs are a baseline operator need, not a debug-only feature.
- **Request tracing is opt-in:** outbound request summary and payload tracing remain configurable because payload logs can be noisy or sensitive. Since issue #1340 phase 1 the switch is the single `CODEX_LB_TRACE` comma-separated channel list (`shape`, `shape_raw_cache_key`, `payload`, `service_tier`, `upstream_summary`, `upstream_payload`); empty default = all off. It is an incident-debugging knob for interactive use only.
- **Error logs must be correlated:** request id, endpoint, status, code, and message are the minimum useful fields for debugging 4xx/5xx failures.
- **Prewarm observability is outcome-only:** the Codex HTTP-bridge prewarm canary experiment finished, so its bucket/cohort dimensions were retired (issue #1340 phase 4). The `codex_lb_http_bridge_prewarm_total` counter is labelled by `outcome` only, request logs record `prewarm_status` / `prewarm_latency_ms` (statuses: `not_applicable`, `skipped`, `success`, `timeout`, `error` — `canary_miss` no longer occurs). The legacy `prewarm_canary_bucket` / `prewarm_eligible_reason` request-log columns stayed declared but unwritten through v1.22–v1.24; `retire-prewarm-canary-column-mappings` removed them from the ORM model and allow-listed the retained physical columns in the schema-drift gate, because a previous-release replica still maps them and renders explicit NULLs in its INSERTs while the migration Job runs ahead of the workload roll. The Alembic drop revision ships the release after (see the next-release queue in `openspec/specs/deployment-installation/context.md`).
- **TTFT datasource selection stays in Grafana:** the Helm chart packages the
  TTFT dashboard but does not provision a PostgreSQL datasource or its
  credentials. The visible, single-select `DS_SQL` variable keeps
  installation-specific datasource UIDs out of chart values while routing all
  four SQL panels through one explicit selection.

## Operational Notes

- Use request ids to correlate inbound proxy logs, outbound upstream traces, and client-visible failures.
- Prefer summary tracing in normal debugging sessions; enable payload tracing only when the exact normalized outbound request matters.
- For direct compact `5xx` failures, look for `proxy_compact_failure` alongside `upstream_request_complete`; together they show the compact failure phase, failure detail, exception type, retry metadata, and affinity source.
- After the Grafana sidecar imports the TTFT dashboard, select the ordinary
  PostgreSQL datasource that points to the codex-lb database from the visible
  **PostgreSQL** dropdown. A datasource registered only as a frontend runtime
  plugin is not listed by Grafana's datasource variable.
- Timeout invariant violation logs describe startup `Settings` and imported
  constant validation only. They intentionally avoid request-scoped overrides,
  runtime-derived effective timeout values, payloads, API keys, access tokens,
  raw affinity keys, account emails, and other high-cardinality identifiers.

## Affinity decisions in request logs

Issue #2349 adds three nullable columns to existing request logs: `sticky_key_source`, `sticky_kind`, and `sticky_key_hash`. They work without trace settings. Callers with `conversations:read` permission can also read them as `stickyKeySource`, `stickyKind`, and `stickyKeyHash` in `GET /api/request-logs`. Responses without that permission hide all three fields through the existing sensitive-metadata gate.

The hash is the first 16 lowercase hexadecimal characters of SHA-256 over the resolved selection key encoded as UTF-8. For example, a resolved key of `abc` records `ba7816bf8f01cfea`. Session selection keys can differ from raw session headers, so hashing the header separately does not reproduce that value. The metadata never stores raw keys or prompts, even when raw-key tracing is enabled. A hash supports equality grouping, but it is not protection against guessing low-entropy keys. Existing request-log retention applies.

Direct streaming rows retain their existing attempt granularity. Compact records its final operation, while native WebSocket and HTTP bridge rows describe the settled or failed request state. A row covering several sends records its final policy, not an intermediate decision history. Existing recovery can clear a key; that produces a null hash while retaining the original source classification. Metadata alone does not explain hard-owner precedence, rerouting, or account-health decisions.

Rows before affinity resolution, historical rows, auxiliary control/file/transcription/realtime/warmup rows, and external-model-source rows can have all three fields null. This means observation was unavailable. An explicit no-affinity observation uses source `none`; its kind and hash are null. No historical decision is reconstructed.

For a bounded administrator query:

```sql
SELECT sticky_key_source, sticky_kind, sticky_key_hash, COUNT(*) AS rows
FROM request_logs
WHERE requested_at >= CURRENT_TIMESTAMP - INTERVAL '1 day'
GROUP BY sticky_key_source, sticky_kind, sticky_key_hash;
```

## Authentication migration convergence

The affinity history converges with dashboard roles, users, the final compatibility-credential projection and audit actor columns through a no-op merge. Published revisions remain unchanged. Databases already on the authentication branch retain their current credentials and session generations; the earlier credential projection is not replayed on merge-only reupgrade. Databases on the older affinity history run the existing authentication backfills once. Ledgerless schema bootstrap retains those migrations' existing legacy-credential projection behavior.

The subsequent invite migration converges through a second no-op join. Pending, consumed and revoked invite rows retain their hashes, expiry/consumption/revocation times, creator snapshots and flags. The older affinity history creates an empty invite table through the unchanged upstream migration.

## Output sampling across JSON serialization

Timing observation uses the same decoded content fields as structured streaming,
including the verbatim relay path. Upstream SSE carriers retain their parsed
payload, so reading it for output sampling does not require a second decode.
Plain string producers need a parse; a lexical substring check cannot distinguish
a root `delta` from nested metadata or recognize JSON-escaped property names.
The observation changes no relayed bytes or routing/settlement decisions.

For example, reasoning observed at 125 ms, first text at 500 ms, second text at
750 ms and completion at 1,000 ms produce TTFT 125 ms and two output chunks.
With 24 output tokens including four reasoning tokens, qualified TPS is
`(24 - 4) / ((1000 - 500) / 1000) = 40`. Two seconds of cleanup after terminal
receipt can make total latency 3,000 ms without changing that estimate.
`"delta" : "hello"` and `"\u0064elta":"hello"` describe the same content;
`"metadata":{"delta":"hello"},"delta":""` contains no output sample.

## Optional model-source telemetry

Source metadata is ancillary to the forwarded response. Preserve reported reasoning
usage, but leave missing reasoning unknown; reject boolean counts and values beyond
PostgreSQL's signed 32-bit request-log storage range. Validate timing operands and
their sum before rounding. For example, two individually finite 1e308 timings are
not usable measurements and cannot interrupt an otherwise valid response.

The usage parser incrementally decodes UTF-8 and waits for complete SSE events,
including multi-line data and CRLF split across network chunks. Forwarding still
yields original upstream bytes. Source routing, metric qualification and report
cohorts are unchanged. See the optional-source-metrics requirement in spec.md.

## Account pool metrics

The pool metrics describe the shared account inventory, not process-local activity. Summing worker snapshots multiplies the inventory; taking a maximum prevents a newer deletion or pause from lowering the observed count. Prometheus `livemostrecent` selects the latest live-worker observation and removes the automatic PID label.

The existing routing cache is seeded at startup and refreshed on account-routing invalidations. Those events alone cannot reflect a token crossing its expiry time while the pool is idle. The metrics ASGI application therefore awaits the same refresh before exposition. It performs one account projection query per scrape, never probes upstream, and fails the scrape if the refresh fails. Operators can use Prometheus `up` alongside availability rather than interpreting stale values as fresh.

The routing cache continues to load its existing complete status map. Metrics omit rows pending deletion, matching the account repository's operator-facing inventory. Only reauthentication-required tokens need decryption for the expiry predicate. Active tokens are counted even when their JWT expiry is past because ordinary routing can refresh them; unknown expiry on a reauthentication-required account remains eligible under the existing predicate.

For example, two active accounts and one reauthentication-required account with a refresh-only warning and future token expiry produce `accounts_available = 3`. If all three are occupied by streams, the metric remains 3. When the reauthentication token expires, the next scrape reports 2 without changing the status inventory.

The availability projection also carries the committed credential rejection reason into the same shared eligibility predicate used by routing. A revoked or invalidated access credential remains unavailable even if its JWT expires tomorrow or cannot be parsed. Its `reauth_required` inventory count remains visible. A refresh-only warning with usable access credentials remains eligible; after credential repair clears the blocking reason, the next scrape reflects recovery. This does not add request-specific quota, cooldown, or concurrency filters or another database query.
