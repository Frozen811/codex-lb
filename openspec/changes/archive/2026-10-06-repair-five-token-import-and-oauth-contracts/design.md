## Context

See proposal.md. Existing schemas accept optional credentials, and shared routing gates already exclude revoked access generations while retaining refresh-only warnings. Missing credentials are represented by encrypted empty strings in existing non-null DB columns.

## Goals / Non-Goals

Goals: complete five registry scopes through public APIs and deterministic local checks, with no new runtime configuration. Non-goals: provider/PAT entitlement validation, DB schema changes, publication, or production work.

## Decisions

- Validate in AuthTokens so file parsing and backup restore use the same rule. Normalize only absent optional token text; retain nonblank token bytes exactly. Reject a blank access token instead of creating an unusable account.
- Add PAT entry within the existing import dialog, serializing a File for the existing API. Require email and account ID rather than inventing identity, offer Business/Enterprise plan selection, keep the token masked, clear it after success/dismissal and retain the batch submission guard. No new route or navigation item.
- Non-refreshable preflight checks force and known JWT expiry before its existing return. Use existing permanent error handling; no refresh request and no separate credential-state store. Unknown expiry remains permitted for opaque PATs.
- Keep generation-fenced rejection, settlement, safe neutral retry and hard-owner refusal in their existing layers. Verify both route families rather than changing proven routing policy.
- Put the optional Compose overlay under deploy/docker; merge a loopback-only mapping explicitly, with no environment knob or default port occupation. Manual callback/device login already exists.
- Preserve all prior dirty-file hashes; only issues-check.md is shared and changes are limited to five rows plus the new evidence summary.

## Risks / Trade-offs

- Missing optional credentials remain encrypted empty strings in DB -> no fake usable credentials and no migration; API export uses null for absence.
- Opaque tokens have no locally verifiable expiry -> upstream acceptance remains authoritative and forced repair fails closed.
- Removing default callback publishing changes direct Docker browser login -> document manual callback/device login and an explicit override.
- Controlled upstream adapters do not prove real hosted-provider acceptance -> state this limit in evidence.
