## Context

See proposal.md. The authorization pattern currently guesses safe commas and permits placeholder-based short circuits. The same helpers serve error fields, exception text and structured JSON fallback strings. Existing TOTP ASCII normalization and allowlisted refresh diagnostics are already present.

## Goals / Non-Goals

Goals: prevent credential tails from reaching operators and independently verify the three registry contracts.
Non-goals: replace general logging, change TOTP normalization or OAuth classification, publish artifacts or touch live accounts.

## Decisions

Apply an authorization-field pass before generic substitutions. A complete single- or double-quoted value can be replaced as one field; otherwise redact to the current line end. Do not infer diagnostic boundaries from commas, ampersands or existing placeholders. Preserve complete quoted-field delimiters and line endings. Existing standalone Basic/Bearer and proxy-header backstops retain their contracts.

Reject grammar-aware authorization parsing: malformed parameters and attacker-selected status/code labels make its boundaries unreliable. Dropping same-line context is acceptable; structured log extras and subsequent lines remain available.

Use only inert synthetic credentials. Check refresh through a local aiohttp OAuth endpoint and the real account manager/repository. Expand setup/verify rejection checks for Persian and superscript digits; confirm replay state and session remain unchanged.

## Risks / Trade-offs

- Lost context after unquoted Authorization: explicit policy documented in the owning spec and focused expectation changes.
- Re-redacting a placeholder: test exact idempotency, complete quoted delimiters and CR/LF preservation.
- Existing source fixes mistaken for new repairs: distinguish verification-only TOTP/refresh work in the registry and evidence.
