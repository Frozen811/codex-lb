## Context

See proposal.md for the three-item audit scope. `ParsedSseBlock` already carries
the parsed upstream payload through streaming stages. The current timing-only
string scanner disagrees with the structured classifier on JSON whitespace,
escaped property names and nested keys. Integration tests are excluded from
the graph index, so their fixtures and coverage were inspected directly.

## Goals / Non-Goals

Use the existing content classifier for every relay mode and test accounting
from local transport through persistence and public read APIs. No changes to
prices, migrations, API-key ownership, routing, UI controls or configuration.

## Decisions

- Replace the duplicate lexical classifier with `parse_sse_data_json` plus
  `observe_output_timing`. Parsed carriers reuse their payload without another
  JSON decode; untagged strings pay one decode to establish correct evidence.
  A regular expression cannot reliably distinguish nested keys from root content.
- Decoder limits on unrelated metadata in plain-string frames skip optional
  sampling instead of turning an otherwise relayed stream into a failure.
- Keep observation before awaited processing and byte relay unchanged. Use a
  controllable proxy clock for exact timing assertions and real local upstream
  sockets for response parsing; delay settlement after terminal observation.
- Verify cache writes using the existing catalog with known synthetic usage.
  Assert stored reservations, cost components and repeat-finalization counters.
- Verify optional source telemetry separately from native-account timing, since
  upstream metrics remain a labeled legacy estimate rather than local samples.

## Risks / Trade-offs

Untagged synthetic/custom stream producers need a JSON decode for output
sampling. Cached upstream carriers avoid this work; a unit test pins reuse.
Local synthetic upstreams cannot certify hosted user incidents or published
artifacts; the registry preserves those limits.
