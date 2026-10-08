## Why

Five unverified registry records cover image bridge admission, source-owned compaction refusal, compact deadlines, and post-terminal health writes. The inline-image length shortcut currently mistakes malformed oversized base64 for a valid oversized image, violating unsupported-shape precedence.

## What Changes

- Preserve unsupported-shape precedence for malformed base64 above the encoded fast-path bound without decoding or copying the full segment.
- Route both explicit compact endpoints with a trailing slash through the same handler as their canonical forms; repair source-compaction refusal documentation.
- Synchronize resolved transport-log labels and the 900-second compact budget with existing verified behavior.
- Independently verify UP-PR-2503, UP-PR-2534, UP-PR-2451, UP-PR-2317, and UP-PR-2319 through focused public-path and transport tests.
- Preserve default bridge image admission, replayed bytes, explicit compact refusal, deadline ownership, settlement, and cancellation contracts.
- Record exact evidence and close only the five selected local registry scopes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: clarify that malformed base64 remains unsupported even above the encoded length shortcut, and verify the existing image/compact/terminal contracts.

## Impact

Implementation scope: `app/modules/proxy/_service/http_bridge/helpers.py` and the two compact route registrations in `app/modules/proxy/api.py`. Regression files: `tests/unit/test_http_bridge_inline_image_admission.py`, `tests/unit/test_compact_deadline_contracts.py`, `tests/unit/test_bridge_transport_labels.py`, `tests/integration/test_http_bridge_inline_images.py`, `tests/integration/test_source_compaction_refusal.py`, `tests/integration/test_proxy_compact.py`, `tests/integration/test_proxy_compact_hop_by_hop.py`, and `tests/integration/test_proxy_responses.py`. Documentation scope: the owning spec/context, change artifacts, and `issues-check.md`. No new settings, schema, dashboard surface, dependency changes, publication, or deployment. Pre-existing dirty work is backed up and must remain intact.
