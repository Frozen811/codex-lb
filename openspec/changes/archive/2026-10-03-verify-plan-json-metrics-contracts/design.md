## Context

See proposal.md for scope. The shared Responses normalizer already preserves JSON mentions as developer input. Chat only defers instruction hoisting for `response_format`, so using `text.format` hoists before the normalizer can inspect input. Business Pro Lite canonicalization and logging-neutral metrics startup are already implemented.

## Goals / Non-Goals

Prove all three items at their product boundaries with isolated databases and loopback servers. Preserve ordinary instruction hoisting, compact/Lite behavior, unknown-plan guards, and the operator's existing logging configuration. No new knobs or migration.

## Decisions

- Determine JSON mode after format mapping using the shared Responses format predicate. Keep a single normalization rule rather than adding a second JSON-mention classifier.
- Exercise Chat routes with recording HTTP upstreams, across streaming modes, equivalent format controls, instruction roles, and content forms; check returned content and wire payload.
- Exercise alias imports and refresh with real repositories, then read from a new session and inspect dashboard output. Include unknown plans and workspace identity mismatch.
- Extend the existing CLI subprocess logging regression to file paths containing spaces, text/JSON formats, and info/debug levels. Check both servers' access records and redaction after metrics startup.
- Decode Uvicorn's actual five-field access argument tuple without mutating the shared record, retaining support for explicitly structured records. JSON formatters must not enrich tracing helper diagnostics by calling those same helpers again; skip enrichment for that logger to break recursion even on unexpected tracing failures.

## Risks / Trade-offs

Loopback/SQLite evidence does not certify hosted providers, deployed replicas, public artifacts, or cloud CI. Record those limits separately. Subprocess tests must close owned processes on failure; database tests use the existing isolated harness.
