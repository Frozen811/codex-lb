## Context

All 77 prior local paths are committed and pushed as 71c5332ca. CI #86 confirms the six typing diagnostics. The catalog's Git blob already matches capture provenance; only Windows CRLF conversion changes the working-tree digest. Existing atomic writers fsync the file and replace the destination before trying a POSIX directory handle.

## Goals / Non-Goals

Keep every capture hash and production deadline intact, make local Windows checks meaningful, and prove full exact-SHA fork CI. Do not alter capture provenance to match transformed bytes, increase production timeouts, suppress genuine POSIX I/O failures or add settings/migrations.

## Decisions

- Pin LF specifically for committed reference catalog JSON in .gitattributes and restore the existing working copy to its exact Git bytes. This preserves the historical digest rather than rewriting it.
- Treat directory fsync as a platform capability, using the same explicit Windows boundary already applied in SQLite maintenance. File fsync/atomic replace remain mandatory. POSIX open/sync errors still propagate.
- Use VirtualScheduler in the repeated-marker regression. Windows coarse event-loop ticks make its 100 ms wall clock assumption invalid; virtual timing verifies the unchanged 1 ms probe and 50 ms discovery budget and task cleanup.
- Narrow nullable test records with assertions that also improve fixture failure diagnostics. No application typing workaround is needed.
- Current full CI found stale expectations outside the earlier focused selections: a bare credit flag was still expected to activate exhausted Edu accounts, compact slash aliases were still expected to return 405, and the trusted-capability route inventory omitted those aliases. Align these fixtures with the already owning specs and expand the inventory's fail-closed route controls; no production contract is changed.
- The direct WS same-owner full-resend predicate was intentionally weaker than account-neutral relocation but omitted the new async identity guard. Validate marker type and nonblank async IDs there while retaining account-bound same-owner behavior. Refused retries keep the original endpoint-specific anchor error and do not reconnect; owner-unavailable relabeling would misstate a still-available account.

## Risks / Trade-offs

- Windows cannot claim POSIX directory or permission semantics: preserve file flushing and replacement; test POSIX mode enforcement on POSIX and Windows writable state separately.
- Virtual tests can leave pending tasks: consume the handed-off next item and assert task/timer quiescence.
- New publications cancel in-flight predecessor runs: retain their historical outcomes and verify all applicable workflows on the final head.
