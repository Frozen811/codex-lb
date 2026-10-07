## Context

The current fork already contains the upstream monthly-ingestion, chart and timezone changes. Their presence does not establish correct behavior in this fork. Source metadata is pinned in source-snapshot.json.

## Decisions

Reuse the shared monthly-duration classifier for old primary-slot rows. Only absent or explicit zero-duration secondary windows establish the monthly-only shape. Unknown/positive-duration secondary observations remain independent windows. Preserve primary windows when monthly-only classification is not established.

Team's weekly capacity does not establish a 30-day capacity. Remove the invented monthly default while preserving explicit capacity overrides and percentages. Newer short/weekly evidence supersedes stale monthly observations independently of plan.

Routing and freshness previously inferred monthly support from the capacity default. Keep their existing Free/Team support using a shared predicate independent of the estimate; retain the existing unsupported-history handling for ordinary plans. This preserves Team quota holds and freshness without inventing credits. API-key share calculations still require a numeric capacity and retain their unknown-evidence behavior.

Use isolated SQLite API tests and existing frontend component/browser paths. No live account data or credentials are required. Existing verified behavior will receive an evidence-backed closure rather than redundant replacement code.

## Risks

Operators may see null monthly credit estimates where a fabricated estimate was previously shown. Percentages and reset/window metadata remain available. Historical invalid monthly shapes must remain visible in their original slots. Existing global capacity override behavior is retained.
