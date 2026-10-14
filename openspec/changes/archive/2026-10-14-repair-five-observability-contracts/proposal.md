## Why

Exactly five unverified registry records are selected: UP-ISSUE-1870, UP-PR-2146, UP-DISC-378, UP-DISC-1894 and UP-DISC-292. Source attribution is displayed but cannot be filtered; the proposed activity heatmap is absent. Tool analysis has no supported offline entry point. Existing rollup reporting and opt-in retention require independent evidence and clear operator documentation.

## What Changes

- Add an observed upstream facet with stable IDs, historical deleted-source labels, exact totals and URL persistence.
- Add an optional browser-local six-month UTC request heatmap, using hourly rollups and the exact bounded raw complement.
- Add a streaming offline archive tool-usage summary with explicit error/unknown coverage, without retaining arguments or results in the output. Quality-of-model judgments are outside automatic measurement.
- Verify existing report rollup/cache and retention behavior; document their operating limits.
- Update exactly the five selected registry rows with local evidence; preserve unrelated dirty work.

## Capabilities

### New Capabilities
- `request-log-upstreams`: observed subscription/model-source filtering.
- `dashboard-request-activity`: optional six-month activity view.
- `tool-usage-analysis`: local archive analysis.

### Modified Capabilities
- `frontend-architecture`: additive dashboard controls.

## Impact

Runtime: app/modules/request_logs/{api,service,schemas,repository,upstreams}.py; app/modules/dashboard/{api,activity}.py. UI: frontend/src/features/dashboard/{api,schemas}.ts, hooks/use-request-logs.ts, components/{dashboard-page,recent-requests-table,request-activity-heatmap}.tsx, components/filters/request-filters.tsx; frontend/src/hooks/use-dashboard-preferences.ts; frontend/src/features/settings/components/appearance-settings.tsx; existing locale JSON files. Tool: scripts/analyze_tool_usage.py. Verification: focused backend/frontend/browser tests, OpenSpec spec/context, docs/usage-reporting.md and issues-check.md. No new database migration, environment field or navigation item.
