## Design

The existing MySQL selection mixes whole integration files, selected migration
nodes, a root-level API file and one unit-test node. Preserve those selectors
instead of broadening the suite based on directory names or markers. Group
selectors by source file so schema-reset and module-state assumptions remain
serial within one runner. A data-only manifest is shared by Make and Python.

Three runners each retain their own MySQL 8.4 service and the existing xdist
worker databases. Keep pinned actions, the current dashboard-assets artifact,
test-user grants, dependency caches and non-backend placeholder checks.

The existing MySQL check name remains a strict aggregate, analogous to core.
CI Required depends on both the matrix and aggregate. Actual speed and the
6–7 minute workflow target are measured after publishing; elapsed goals are
performance objectives rather than deterministic contract assertions.

Baseline: main commit 6c08cf8b1d83b4d39bd105980736a1dbb53bd056,
workflow 37528342525, MySQL job 112491283495: 12m 27s; full CI: 13m 21s.

## Local verification

The original Makefile selection and the canonical manifest collect the same
2,405 node IDs. Shards collect 698, 847 and 860 IDs respectively, with no
duplicates or omissions and with all selectors from one file on one runner.
The baseline executed 2,364 tests and skipped 41.

The workflow contracts pass 16 tests and the sharder passes 24 tests. All three
Make targets also execute a representative database test successfully against
MySQL 8.4 with two xdist workers. Invalid shard indexes fail before pytest can
fall back to a broader selection. Lint, formatting, type checks and strict
OpenSpec validation complete the implementation verification. Cloud execution
and actual elapsed measurements follow the main push, with run-specific
evidence saved outside versioned source.
