# Upstream identity in request logs

[Requirements](spec.md). This facet identifies the route family; subscription_pool includes pre-selection failures and does not prove successful account dispatch. Model-source IDs remain stable when names change or configurations are deleted. Current names are only display metadata, never credential or URL data.

Example: /api/request-logs?upstream=subscription_pool&upstream=src_a combines those upstreams with OR, then intersects API-key/model/status/time filters. Options ignore the current upstream selection so another source can be added. Demand rollups lack this dimension; filtered exact counts use raw indexed logs and separate cache entries. Source options disappear when all their logs are soft-deleted or pruned. Native PostgreSQL/MySQL query plans require their own verification.

## SQLite legacy paired facets

The upstream options response also contains the existing model, API-key and status facets. On SQLite without the live-row partial indexes, a missing NULL counterpart can make the visibility-first query choose a broad prefix scan even though the ordinary pair index exists. For example, 20,000 log rows with non-NULL error codes under the error status previously caused 40,000 VM operations just to establish that no NULL option existed.

The pair index first answers raw NULL presence using only equality bounds. A positive result still executes the original live-row visibility check, so a soft-deleted or excluded raw pair does not become an option. This adds a bounded SQLite-only probe and preserves PostgreSQL/MySQL query behavior. The actual HTTP benchmark keeps its existing operation ceiling and reports per-statement work on failure; the PostgreSQL partial-index regression remains scoped to its legacy facets. See [requirements](spec.md).
