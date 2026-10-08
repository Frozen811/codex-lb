# Tool continuity fixture context

The [tool continuity sanitization requirement](spec.md#requirement-responses-fixture-sanitization-preserves-tool-continuity-evidence) keeps regression fixtures capable of exposing history loss. Function and custom calls can carry optional async markers, and client tool-search outputs carry loaded declarations in `tools` rather than an arbitrary output string.

For example, a call with `async: true` and its later typed output retain the same anonymized call ID; an otherwise identical call without that field remains without it. Captured arguments and query text still pass through the existing deterministic redaction rules. Markers on unrelated item types remain outside their allowlists.

This fixture behavior supports protocol testing and does not establish live provider or Codex client support for asynchronous calls. Invalid replay evidence remains subject to the owning [Responses requirements](../responses-api-compat/spec.md). Existing captured-catalog provenance and platform-specific directory persistence checks are independent controls; their inherited failures are recorded separately in batch verification.
