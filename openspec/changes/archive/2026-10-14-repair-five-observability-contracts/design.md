## Decisions

Reuse the indexed request-log source identity. Add upstream conditions at the existing list/filter seam and to the count cache. Demand rollups omit this dimension, so selected upstreams use raw exact counts. Upstream options ignore their own selection while the other facets honor it. Unfiltered source enumeration uses the existing skip-scan implementation plus a NULL presence probe, joining only ID/name/kind metadata.

The activity endpoint uses the shared watermark partition rule. UTC midnight boundaries prevent partial-day historical ambiguity. Warmup is excluded. The frontend requests activity only when the browser-local alternate mode is enabled, preserving the weekly pace default and usage donuts.

The tool analyzer streams explicit JSONL/gzip input files. It deduplicates archived full-resend/terminal copies by session/request and call identity, associates results with their calls, and counts explicit structured failures separately from unknown outcomes. It reports names/counts, never arguments, result text, headers or credentials. It does not infer model mistakes from text. No application database or global archive setting is initialized.

## Verification

Real disposable SQLite API regressions cover source filtering/count/cache/self-facet/deletion and activity rollup-tail boundaries. Existing report/retention suites cover prior behavior. Frontend tests cover URL/filter/mode state; browser screenshots and small/mobile view checks cover UI. Offline subprocess fixtures cover compression, duplicates, partial outputs and privacy. PostgreSQL/MySQL and live/provider/cloud scopes require separate evidence if not run.
