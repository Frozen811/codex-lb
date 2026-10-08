## Context

See proposal.md for the five-record scope. The bridge classifier uses a length shortcut before strict decoding. Unsupported inputs must win over a valid oversized sibling. The existing ordinary decoder and 5 MB/64 MiB budgets remain authoritative.

## Goals / Non-Goals

Preserve shape precedence at the length shortcut with bounded-memory validation. Verify the existing refusal/deadline/terminal behavior at public routes. Do not add source compaction forwarding or change retry authority. Build the current Windows native helper and verify its large-message IPC locally; live providers and production remain separate.

## Decisions

Validate oversized base64 syntax using a compiled character-class expression against the original URL with a start position, then check quartet length and padding. This avoids copying or decoding the multi-megabyte segment while rejecting whitespace, non-ASCII, URL-safe characters and malformed padding. Derive decoded size from quartet count minus padding. Ordinary bounded segments retain the existing strict decoder.

Use the existing fake upstream adapters with real ASGI routes and isolated SQLite for acceptance. Exercise both Responses route families, nested tool results, legal oversized controls and settlement recovery. Compact refusal tests must guard selection, admission, reservation and dispatch. Verify native/socket plumbing with focused Python and Rust tests plus actual large-message IPC against the freshly built Windows helper.

Register hidden trailing-slash aliases for both compact handlers. A broader dynamic route currently matches those paths with a disallowed method before slash redirection can help. Explicit aliases preserve the same dependencies, validation, ownership and accounting while keeping canonical OpenAPI paths unchanged. Synchronize the stale disabled-source exception: terminal Codex compaction is refused, while file-pinned subscription routing remains unchanged.

## Risks / Trade-offs

- Syntax checking adds one linear scan to oversized image rejection. Ingress is already bounded; no payload-sized copy or decoded allocation is added.
- PR 2503's historical current-turn bypass is superseded by default-on bounded admission from 2534; tests follow the current owning spec, including explicit rollback.
- Existing explicit model-source compact refusal is retained. The separate forwarding proposal UP-PR-2324 is not selected.
- Pre-existing dirty files overlap test suites and registry; compare backups before completion and never overwrite their changes.
