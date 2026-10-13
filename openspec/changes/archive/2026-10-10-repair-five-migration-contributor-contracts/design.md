## Context

See proposal.md. The existing topology guard already allows only the exact released September collision after convergence. The duration checker is stdlib-only; SQLAlchemy/Alembic and PostgreSQL drivers are already dependencies. Runtime revision progress reports private per-revision elapsed times. Scripts and integration tests are excluded from the code graph, so their relationships require direct inspection.

## Goals / Non-Goals

Measure actual migrations on a synthetic database and reject over-budget revisions. Preserve released revision identities and all previous work. Background migration phases, production measurements, publishing, deployment, application database deletion and changes to upstream GitHub state are outside this batch.

## Decisions

Use a separately created random test database on the supplied PostgreSQL server; never clear an operator-supplied database. Populate realistic nullable user-agent distributions and timestamps using database-side generation. Derive the baseline head from a supplied Git ref, then upgrade through the current graph while collecting existing per-revision execution records. Apply a statement timeout as well as the measured elapsed budget. Persist JSON and a Markdown job summary even when a revision fails. SQLite supports small local harness tests and is explicitly identified as such.

The static check targets executable SQL strings, ignores prose/comments, recognizes case/qualified identifiers, and accepts explicit bounded primary-key predicates instead of the presence of an unrelated LIMIT word. It does not claim to parse arbitrary dynamic SQL or prove scan performance; the actual benchmark provides the complementary gate.

Keep the September merge; independently exercise both released parents and both-parent ledgers. The alternative PR's restamping would invalidate released identities and is unnecessary to achieve its desired single-head outcome.

Contributor instructions cite focused authoritative guidance while preserving repository conventions, OpenSpec and merge rules. Test storage is established before application imports; regression coverage follows affected HTTP/WebSocket/bridge boundaries. No blanket delegation requirement is introduced.

## Risks / Trade-offs

- Synthetic timings depend on hardware and row distributions: report backend, fixture rows, baseline and measured revision data; never label them production timings.
- Static SQL analysis is intentionally bounded: supported forms receive regression tests; dynamic operations remain subject to runtime measurement.
- A failed migration can leave a disposable database: cleanup runs after connections close, with unique names and no application database reuse.
- Hosted execution is unavailable until authorized publication; local verification and checked-in workflow are distinct evidence.
