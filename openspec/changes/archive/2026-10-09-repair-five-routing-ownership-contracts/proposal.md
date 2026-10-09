## Why

The registry has five independently unverified routing tasks: UP-PR-2332, UP-PR-2469, UP-PR-2486, UP-PR-2458, and UP-PR-2001. A pre-visible quota rejection currently creates payload ownership for retained ciphertext and prevents otherwise legal replacement selection; the other four contracts need current product-path verification.

## What Changes

- Prevent a coded pre-visible quota/rate-limit rejection from creating a dispatch owner when retained reasoning or compaction ciphertext is the only account-scoped state; forward that ciphertext unchanged.
- Keep independent owners, resource references, unknown state, ambiguous execution, and visible output fail-closed.
- Prevent routed file finalization from moving accounts after an earlier poll returned, even when a later connection failure is individually pre-dispatch.
- Restore projected retained-reasoning replay for durably proven bypass requests only after owner quota evidence.
- Emit a ciphertext-free diagnostic when the replacement account rejects encrypted reasoning and keep that request-shaped rejection health-neutral.
- Verify existing model-rejection failover, routed file transport provenance and poll ownership, hard-owner backoff admission, and durable-history quota recovery.
- Update exactly the five selected registry records after verification and preserve earlier dirty work.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: Narrow retained-ciphertext quota failover and diagnostics.
- `account-routing`: Encrypted-content rejection health neutrality and hard-owner transient backoff admission.

## Impact

Implementation is scoped to replay safety and streaming retry/health classification. No settings, schema, dependency, release, or dashboard changes. Existing wire payloads and ownership/settlement paths remain authoritative. Verification uses isolated local test databases and controlled upstream adapters.
