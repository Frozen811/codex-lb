## Context

See proposal.md for the exact five-row scope. Native helper events are drained by a single multiplexed reader and a per-socket pump. Blocking that pump on the data consumer would delay send acknowledgements. Direct OAuth calls currently bypass the routed transport error translator. Pro Lite aliases already exist, but weekly-only provider shapes require an independent recovery test.

## Goals / Non-Goals

**Goals:** Preserve transport ownership, FIFO output, safe errors and account status compare-and-set while repairing the selected boundaries.

**Non-Goals:** New configuration, account routing policies, image post-processing, provider changes, schema migration or publication.

## Decisions

- Native messages use the existing generous 4096-event class of bound plus a 32 MiB accumulated payload budget. A single large frame is accepted on an empty queue, retaining existing 64 MiB frame compatibility. UTF-8 and interpreted payload copies count toward accumulation. Overflow aborts the socket without blocking ACK processing; accepted frames remain ordered ahead of the terminal failure. A blocking queue was rejected because ACK and data share the pump.
- OAuth uses one direct-session context manager translating aiohttp client failures and timeouts into a constant transport_error message. Cancellation remains outside that catch. Callback/manual/device APIs retain their existing error/finalization handling.
- Weekly-only recovery follows normalized windows and the existing successful probe plus available-usage contract. Background refresh continues to honor a real persisted 429 cooldown; an operator pause wins compare-and-set.
- Transparent output is a format capability: PNG/WebP pass through unchanged and JPEG fails with param=output_format. No image processing is added.
- CCodex remains an exact allowlist; inference transport selection is unchanged. Raise urllib3's package floor to the already locked patched version.

## Risks / Trade-offs

- Local stubs do not prove live provider alpha output, historical account reset causality or Desktop behavior: preserve these limits in verification.
- A larger message cap increases permitted buffering: byte accounting bounds accumulation and a finite event cap bounds empty-message overhead.
- Callback terminal races must still honor a concurrent success: exercise existing lifecycle suites alongside the new transport tests.
