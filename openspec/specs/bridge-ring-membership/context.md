# Bridge replica signing

The [shared-key requirement](spec.md#requirement-bridge-signing-uses-the-configured-shared-encryption-key) makes replica verification follow the same key configuration as credential encryption. An environment key is authoritative even when each pod has a different, missing, or invalid key file. File-only deployments need the same effective file contents across replicas. Different effective keys fail signature verification before upstream dispatch.

For example, replica A and replica B can have separate writable data volumes while sharing `CODEX_LB_ENCRYPTION_KEY`. Their local file paths do not participate in signing. Environment-key signing neither reads nor creates those files. Removing that environment setting changes the effective key to the configured file and therefore needs coordinated operator handling; the audit does not authorize rotating live keys.

Both primary signature versions and the tools-bound signature are verified using independently reloaded sender and receiver settings. These tests prove key resolution and receiver acceptance/refusal; they do not attest a deployed Kubernetes cluster or public image.
