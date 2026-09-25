# Design: Cap SQLite Bulk Usage History Reads

## Context

In high-throughput environments using SQLite, `UsageRepository.bulk_history_since` executes a full table scan over the 7-day lookback floor for every dashboard poll. While PostgreSQL was optimized in PR #1891 with lateral scans (`_bulk_history_since_capped_postgresql`), SQLite remained uncapped.

## Query Design for SQLite

SQLite lacks PostgreSQL's `LATERAL` join. However, because `account_ids` in `bulk_history_since` is bounded (representing active pool accounts, typically 1 to 50 accounts), executing one targeted index seek per account in `sqlite3` via `to_thread.run_sync` provides near-instant response times without lock contention.

### 1. Window Predicates
```python
if window == "primary":
    window_clause = "coalesce(window, 'primary') = 'primary'"
    window_params = []
else:
    window_clause = "window = ?"
    window_params = [window]
```

### 2. Capped Only Query (`uncapped_recent_floor is None`)
```sql
SELECT id, account_id, used_percent, recorded_at, reset_at, window_minutes
FROM usage_history
WHERE account_id = ?
  AND {window_clause}
  AND recorded_at >= ?
ORDER BY recorded_at DESC, id DESC
LIMIT ?
```
Params: `[account_id, *window_params, cutoff_param, per_account_row_cap]`.

### 3. Compound Floor Query (`uncapped_floor > cutoff`)
```sql
SELECT id, account_id, used_percent, recorded_at, reset_at, window_minutes
FROM (
    SELECT id, account_id, used_percent, recorded_at, reset_at, window_minutes
    FROM usage_history
    WHERE account_id = ?
      AND {window_clause}
      AND recorded_at >= ?
      AND recorded_at < ?
    ORDER BY recorded_at DESC, id DESC
    LIMIT ?
)
UNION ALL
SELECT id, account_id, used_percent, recorded_at, reset_at, window_minutes
FROM usage_history
WHERE account_id = ?
  AND {window_clause}
  AND recorded_at >= ?
```
Params: `[account_id, *window_params, cutoff_param, floor_param, per_account_row_cap, account_id, *window_params, floor_param]`.

### 4. All Recent Query (`uncapped_floor <= cutoff`)
```sql
SELECT id, account_id, used_percent, recorded_at, reset_at, window_minutes
FROM usage_history
WHERE account_id = ?
  AND {window_clause}
  AND recorded_at >= ?
ORDER BY recorded_at ASC, id ASC
```
Params: `[account_id, *window_params, cutoff_param]`.

### 5. Sorting Contract
Python sorts each account's hydrated snapshots oldest-first by `(snapshot.recorded_at, snapshot.id)` before returning, matching the exact contract guaranteed by PostgreSQL's `_bulk_history_since_capped_postgresql`.

## In-Memory Session Fallback

When `sqlite_path is None` (e.g. `:memory:` databases), `UsageRepository.bulk_history_since` executes the existing SQLAlchemy query and applies the cutoff and row cap slicing in Python:
- For `uncapped_recent_floor is None`: `snapshots[-per_account_row_cap:]`
- For `uncapped_recent_floor is not None`: `tail[-per_account_row_cap:] + recent` where `recent` are rows `>= eff_floor` and `tail` are rows `< eff_floor`.

## Verification Strategy

1. Integration parity tests:
   - `test_bulk_history_since_per_account_row_cap_keeps_newest_rows`: asserts `[15.0, 16.0, 17.0]` on both PostgreSQL and SQLite.
   - `test_bulk_history_since_row_cap_respects_per_account_cutoffs_postgresql`: dialect skip removed, verified on SQLite.
   - `test_bulk_history_since_row_cap_exempts_uncapped_recent_floor_postgresql`: dialect skip removed, verified on SQLite.
2. Query plan verification:
   - `test_bulk_history_since_capped_query_plan_is_indexed_sqlite`: executes `EXPLAIN QUERY PLAN` on primary and secondary window queries, verifying `USING INDEX` on `idx_usage_window_*` and ensuring no `USE TEMP B-TREE`.
3. Uncapped cache regression:
   - All existing tests for `_bulk_history_since_sqlite` cache keys, digest invalidation, and incremental append detection continue to pass untouched.
