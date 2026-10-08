# Tool continuity fixture context

The [tool continuity sanitization requirement](spec.md#requirement-responses-fixture-sanitization-preserves-tool-continuity-evidence) keeps regression fixtures capable of exposing history loss. Function and custom calls can carry optional async markers, and client tool-search outputs carry loaded declarations in `tools` rather than an arbitrary output string.

For example, a call with `async: true` and its later typed output retain the same anonymized call ID; an otherwise identical call without that field remains without it. Captured arguments and query text still pass through the existing deterministic redaction rules. Markers on unrelated item types remain outside their allowlists.

This fixture behavior supports protocol testing and does not establish live provider or Codex client support for asynchronous calls. Invalid replay evidence remains subject to the owning [Responses requirements](../responses-api-compat/spec.md). Existing captured-catalog provenance and platform-specific directory persistence checks are independent controls; their inherited failures are recorded separately in batch verification.

## Reference bytes and artifact persistence

Reference capture catalogs retain LF in Git checkouts so Windows CRLF conversion cannot invalidate their recorded SHA256. The original catalog/provenance bytes remain the authority; replacing their digest with a host-transformed digest would erase reproducibility evidence.

Artifact writers flush and fsync the file before atomic replacement. POSIX directory handles are then synced and real open/sync errors propagate. Windows has no supported POSIX directory handle, so that extra step is omitted; this does not claim POSIX directory durability or permission masks there. For example, a sanitizer output on Windows still uses file flushing and atomic replacement, while the same write on Linux must surface a directory EIO.
