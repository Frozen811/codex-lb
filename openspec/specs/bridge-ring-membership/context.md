# Bridge replica signing

The [shared-key requirement](spec.md#requirement-bridge-signing-uses-the-configured-shared-encryption-key) makes replica verification follow the same key configuration as credential encryption. An environment key is authoritative even when each pod has a different, missing, or invalid key file. File-only deployments need the same effective file contents across replicas. Different effective keys fail signature verification before upstream dispatch.

For example, replica A and replica B can have separate writable data volumes while sharing `CODEX_LB_ENCRYPTION_KEY`. Their local file paths do not participate in signing. Environment-key signing neither reads nor creates those files. Removing that environment setting changes the effective key to the configured file and therefore needs coordinated operator handling; the audit does not authorize rotating live keys.

Both primary signature versions and the tools-bound signature are verified using independently reloaded sender and receiver settings. These tests prove key resolution and receiver acceptance/refusal; they do not attest a deployed Kubernetes cluster or public image.

## Independent maintenance owners (2026-10-09)

The [maintenance-isolation requirement](spec.md#requirement-optional-maintenance-cannot-block-ring-renewal) keeps ring renewal independent of durable ownership reconciliation, stale-operation cleanup, idle sweeping and cap refresh. Each optional phase has one periodic owner and awaits its current pass before another. Ordinary failures are logged and retried on the next cadence. Proxy service lookup happens per pass, so a lazily initialized service remains supported.

For example, a blocked reconciliation pass stays single-flight while actual SQLite heartbeat writes and the other phase owners continue. Shutdown signals optional work before waiting for responses and stops it before bridge teardown; heartbeat remains available until ring shutdown. Cancellation-deferring phase cleanup is tracked and prevents a CLEAN record.

Default ring operations obtain a fresh background session for each operation; explicit factories remain available for existing callers. This separates request-pool connection admission, while SQLite's single writer lock remains shared. No new setting or DB migration is needed. The fork's existing readiness envelope and empty-ring policy remain; upstream's ancillary readiness-envelope redesign is outside this record's heartbeat-isolation scope.
