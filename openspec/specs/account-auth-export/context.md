# account-auth-export context

## Account operator verification on 2026-10-09

Restore applies explicit metadata to the imported destination identity, including null alias and false warm-up enrollment. Workspace metadata is portable. Repeated restore uses the existing account slot when identity matches, and pauses a paused backup entry. A source ID is only reused after matching identity; normal auth-file import retains its duplication policy. Example: a foreign source ID carrying an existing workspace credential updates the local matching account. Import routing policy can still require a paused account.

See [requirements](spec.md). Live providers, server database execution and production remain outside local test evidence.
