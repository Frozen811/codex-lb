# Account import context

## Purpose and boundaries

[spec.md](spec.md) owns authorization, bounded multipart parsing and credential
lifecycle requirements. Import is an operator-authorized transfer of credentials;
local acceptance does not establish hosted-provider entitlement or token validity.
Accounts require the existing dashboard write permission.

## Access-only credentials and PAT entry

The existing account import dialog offers **Auth files** for sequential auth.json
batches and **Access token** for Business/Enterprise PAT entry. Token entry requires
email and the upstream account ID supplied by the operator; workspace ID is
optional. It uses the existing multipart API rather than a second credential
endpoint. The password input masks the token; pending submission blocks mode
changes/dismissal, failure retains input for retry, and success/dismissal clears it.
No browser storage contains the token.

Example auth-file shape (all values are synthetic):

```json
{
  "tokens": {"accessToken": "synthetic-opaque-pat"},
  "email": "operator@example.invalid",
  "accountId": "upstream-account-id",
  "planType": "enterprise",
  "workspaceId": "workspace-id"
}
```

Snake-case aliases remain supported. Nonblank credential text is retained exactly;
empty optional ID/refresh fields mean absence, including whitespace-only exports.
Existing non-null encrypted DB columns represent missing optional tokens as an
encrypted empty string; exports report missing tokens as null. No usable placeholder
credential is generated and no schema migration is needed.

## Failure and repair

Opaque access tokens may have no locally known expiry. Normal requests and usage
probes can use them, but a forced refresh cannot exchange a missing refresh token.
Known-expired access-only preflight fails before upstream I/O. Responses error
handling marks the credential for reauthentication and preserves existing
[generation-fenced rejection and hard ownership](../account-routing/spec.md).
An upstream rejection remains authoritative even when JWT expiry is in the future.
Refresh-only warning accounts retain their still-usable access tokens.

Re-import a repaired token with the same identity and **Import without overwrite**
disabled to repair its existing slot. When that setting is enabled, importing the
same identity can intentionally create a separate credential slot instead.

## Headless API authorization and subscription credentials (2026-10-14)

A provider API key uses the existing Model Sources flow rather than a ChatGPT
subscription account. Add an OpenAI-compatible source with its base URL, API
key and supported models, then use a codex-lb relay key to request that source's
model. The source key is encrypted at rest, omitted from list responses and
sent as the upstream Bearer credential. A disposable source-server test proves
Responses dispatch without any subscription account. See
[model-source-routing](../model-source-routing/spec.md) for the owning contract.

An access-only Business/Enterprise credential instead uses the Auth import
dialog's Access token mode with explicit email and upstream identity. Its
export/import now preserves metadata and absent refresh/ID tokens. API-key
authorization does not transfer subscription quota, and neither flow bypasses
upstream SMS challenges, security enrollment or entitlement requirements.
Live upstream validity is confirmed by the actual authorized request, not
inferred from local import acceptance. Example inputs in this context are
synthetic. See [import requirements](spec.md).
