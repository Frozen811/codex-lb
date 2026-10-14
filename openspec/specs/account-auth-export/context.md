# account-auth-export context

## Account operator verification on 2026-10-09

Restore applies explicit metadata to the imported destination identity, including null alias and false warm-up enrollment. Workspace metadata is portable. Repeated restore uses the existing account slot when identity matches, and pauses a paused backup entry. A source ID is only reused after matching identity; normal auth-file import retains its duplication policy. Example: a foreign source ID carrying an existing workspace credential updates the local matching account. Import routing policy can still require a paused account.

See [requirements](spec.md). Live providers, server database execution and production remain outside local test evidence.

## Access-only identity portability (2026-10-14)

Codex auth export now carries explicit email, plan_type, workspace_id,
workspace_label and seat_type. Opaque credentials cannot reconstruct these
from a JWT, so metadata must survive download and reimport. For example,
a PAT for a1@example.invalid in workspace A returns to the same local slot;
another member of A or the same email in B retains its own credentials.
OpenCode output remains a provider-keyed OAuth object without this metadata.

Missing ID/refresh tokens are null in backend output. The export dialog accepts
them, exposes only available copy controls and retains nulls in auth.json.
Long identity text wraps; the dialog height is bounded and scrollable so its
Download/Close controls remain reachable on mobile. Auth exports contain
plaintext credentials and still require accounts:export and existing step-up
rules, with no-cache responses and secret-free audit events. Encrypted portable
bundles from UP-PR-1938 remain a separate unverified feature.

See [requirements](spec.md). Verification uses synthetic credentials only.
