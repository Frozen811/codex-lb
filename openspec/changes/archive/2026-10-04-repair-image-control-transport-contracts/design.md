## Context

See proposal.md. The checked runtime already reuses bridge sessions for bounded inline images and replaces control media types case-insensitively. Two boundary cases remain: empty bytes are still treated as a body, and the Images fallback list retains Luna despite the source report identifying that host as incompatible.

## Goals / Non-Goals

Prove transport behavior through real local origins and isolated database settlement. Keep existing account ownership, ambiguous-dispatch guards, public image model identities, probe defaults and all unrelated dirty work. Live provider capability certification, public artifacts and production changes are outside this local repair.

## Decisions

- Normalize an empty control payload to `None` before building headers and transport arguments. Merely deleting the media type while sending `b""` lets a transport regenerate a media type.
- Remove Luna only from Images candidates, retaining Sol, Astra and 5.5 order plus the existing Sol default when no candidate is visible. Do not introduce a capability toggle or runtime host retry; catalog visibility is not account entitlement.
- Modify the older blanket image-bypass requirement to incorporate the already implemented PNG/JPEG admission exception. Keep oversize rejection and ambiguous-create replay guards explicit; do not archive or alter unrelated active changes.
- Exercise canonical/alias routes and slash forms, retained socket reuse, invalid-image recovery, silent-image dispatch bounds, JSON/SDP headers and Images host/public-model translation. Preserve the existing initial-plus-one pre-created retry policy under a long request budget; the short-budget local-wire case terminates after one dispatch. Use separate unit negatives and complete focused existing suites for verification.

## Risks / Trade-offs

Synthetic origins prove payloads, headers, routing and settlement, but not live provider acceptance or actual vendor image decoding. Existing image size limits and account restrictions remain in force. Excluding Luna changes Images fallback selection; account probes continue selecting it under their existing policy.
