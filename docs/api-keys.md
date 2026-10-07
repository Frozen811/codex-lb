# API Key Authentication

API key auth is **disabled by default**. In that mode, only local requests to the protected proxy routes can
proceed without a key; non-local requests are rejected until proxy authentication is configured. Enable it in
**Settings → API Key Auth** on the dashboard when clients connect remotely or through Docker, VM, or container
networking that appears non-local to the service.

When enabled, clients must pass a valid API key as a Bearer token:

```
Authorization: Bearer sk-clb-...
```

## Protected routes

The protected proxy routes covered by this setting are:

- `/v1/*` (except `/v1/usage`, which always requires a valid key)
- `/backend-api/codex/*`
- `/backend-api/transcribe`

## Creating keys

Dashboard → API Keys → Create. The full key is shown **only once** at creation. Keys support optional expiration, model restrictions, and rate limits (tokens / cost per day / week / month).

Keys can also be scoped to specific accounts, so a key draws quota only from the accounts assigned to it:

![API keys with assigned accounts](screenshots/apis-assigned-accounts.jpg)

## Inspecting keys and choosing image models

The **APIs** page starts in Detail view. Switch to **List view** for a compact, sortable inventory; the view choice is remembered in your browser. Search, status and usage filters work together. **Key not used** means no recorded last use and no positive request, token or cost usage. Missing usage remains unknown. Open a list row to inspect its details; read-only access does not expose management actions.

The allowed-model picker includes all supported Images adapter identifiers, including `gpt-image-2` and its supported variants. Select an image identifier when creating or editing a key to restrict its image requests. These entries are marked as image-only and do not appear in Automations or get added to the public Responses model catalog.

*Specs: [frontend-architecture](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/frontend-architecture), [api-keys](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/api-keys)*

The **Observation window** selector applies 7, 30, 60, or 90 days to the selected key's usage totals and trend. The overview and inventory continue to show their labeled lifetime figures. Available history depends on retention; a longer window does not restore deleted logs.

In **Settings → API keys**, **Reset usage** clears a key's configured limit counters without changing its credential or deleting request history. For a bulk reset, failed keys remain selected and their names and errors are shown so you can retry them.

**Credits (display only)** defines a Codex usage-display override. Traffic does not consume this counter and reaching its maximum does not block requests. Use token or cost limits for enforced budgets, or the estimated usage-share policy below for a percentage of the subscription pool.

## Estimated usage-share limits

An API key can optionally cap its estimated share of its subscription-account pool. A 20% cap gives it an estimated budget equal to 20% of the normalized long-window capacity of its assigned accounts, or of the eligible global pool when the key is unscoped. The cap can be combined with fixed token and dollar limits.

For each account, Codex-LB attributes the account's used long-window credits in proportion to the key's tracked demand from the current quota-window start through that usage sample's recording time. Later requests wait for a later upstream sample instead of inheriting earlier pool usage. Unkeyed generation and internal warm-up remain unattributed pool demand. Model-source, file, metadata, control, thread-goal, and realtime traffic is excluded from attribution and is never denied by this policy. A key with no tracked generation demand therefore has zero estimated usage even when other keys have heavily used the pool. Quota resets, plan changes, and pool membership changes automatically resize the estimate.

The estimate is deliberately approximate and slightly delayed. OpenAI does not report exact subscription-quota cost per request, request logs settle after work completes, and direct account usage outside Codex-LB cannot be attributed. Missing or stale upstream evidence fails open rather than falsely blocking the key. The request path requests at most one immediate coalesced account refresh; the normal staggered scheduler covers the rest of the pool without a refresh burst. A failure to schedule that best-effort wake-up is logged and does not reject the request. Local pre-dispatch refusals are account-neutral and therefore do not feed their own future estimate. Concurrent requests can briefly overshoot the cap.

## Reasoning effort policies

A key can either enforce one reasoning effort or allow a selected non-empty set of client-requested efforts.
Leave the allowed-efforts selection empty to keep the existing unrestricted behavior. A request that explicitly
sets an effort outside its key's allowlist receives a `403 reasoning_effort_not_allowed` response. Requests that
omit a reasoning effort continue to use the model or upstream default.

The policy evaluates the effort selected by the client, including supported model aliases such as `-xhigh`.
Each configured effort is distinct: allowing `high` does not allow `xhigh`, and allowing `max` does not allow
`ultra`. The proxy still rewrites an allowed `ultra` request to the upstream wire value `max`.

![API key reasoning-effort policy](screenshots/apis-reasoning-efforts.jpg)

For wiring keys into each client, see [Client Setup](client-setup.md).

---

*Spec: [api-keys](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/api-keys)*
