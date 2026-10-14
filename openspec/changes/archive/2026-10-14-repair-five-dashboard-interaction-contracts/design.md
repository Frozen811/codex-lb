## Context

See proposal.md for the five registry rows. The frontend already implements OTP
autocomplete, bounded account lists, Compact sorting, remembered consent dismissal
and persisted session TTLs. Keep those implementations and verify their boundaries.

## Goals / Non-Goals

Make failed saves visible, name fullscreen actions correctly and explain remote
session limits. Do not alter authentication locality, cookie expiry policy,
telemetry defaults, request payloads or unrelated dirty files.

## Decisions

- Reuse the existing alert/error utility for consent mutation failures, leaving
  both actions available for retry. A failed save must not dismiss the dialog.
- Use the existing localized enter/exit fullscreen labels for accessible names.
- Add localized explanatory session copy. A browser cannot reliably infer the
  socket peer or trusted forwarding policy, so do not guess an effective TTL.
- Test responsive containment using browser geometry and synthetic accounts;
  DOM class assertions alone cannot establish that an overflow bug is absent.

## Risks / Trade-offs

- Apple Passwords and browser cookie caps are external behavior: Chromium input
  event coverage cannot prove the macOS extension interaction or indefinite login.
- Large configured TTLs still follow the existing locality guard. Explain this
  explicitly instead of weakening the guard to satisfy an old discussion.

## Migration Plan

No migration or new configuration. Revert the small frontend/spec changes to roll
back. Production activation is outside this local task.
