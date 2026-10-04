# Three-item local verification batch

This batch covers only UP-PR-2512, UP-PR-2515, and UP-PR-2529 from issues-check.md, at base HEAD `282ce147038ac53b72bca30d69c4ad9a9ac1b7cc` with an initially clean checkout.

The existing alias mapping is already correct: case/whitespace variants of `self_serve_business_prolite` persist as `prolite`. Actual imports, recorded loopback usage calls, independent database reads, and dashboard capacity summaries prove the behavior without adding an account tier. Unknown-plan and conflicting-workspace usage remains refused.

The Chat mapper recognized JSON mode too early, before equivalent `text.format` controls were considered. Sixteen route cases failed before repair; the existing shared Responses format predicate now determines whether the mapper should defer instruction hoisting. For example, a system instruction `Return JSON only` with `text.format.type=json_object` reaches upstream as a developer input message, not top-level instructions. Non-JSON instructions still merge into instructions, and appended user turns do not alter the earlier prefix.

Metrics already starts with logging-neutral configuration. Broader subprocess checks exposed a JSON access formatter that expected fields Uvicorn only populates on a private text-formatter copy, and recursive enrichment of tracing-helper diagnostic records when the optional tracing package is missing. The JSON formatter now decodes the real argument tuple without changing the shared record; tracing-helper records skip enrichment. Existing trace/span enrichment for ordinary records remains tested.

Evidence is local Windows/Python transport/SQLite. Hosted providers, compiled native helper packaging, installed tracing exporters, deployed replicas, exact-head cloud CI, and public release artifacts remain outside this verification. The optional uvloop-only module is skipped on this environment; Windows subprocess results are not presented as POSIX graceful-shutdown evidence. No new setup, configuration, dependencies, or migration is needed.
