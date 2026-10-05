# Context: frontend-architecture

Normative requirements live in [`spec.md`](./spec.md). This document currently
covers the progressive-disclosure navigation and settings model.

## Progressive disclosure (nav + settings)

### Purpose

Part of the simplicity effort (PRINCIPLES.md P3, progressive disclosure): keep
the first-run dashboard surface small — import accounts, hand out an API key,
point a client at the proxy — while every power feature stays one explicit
interaction away.

### Decisions

- **Core vs Advanced split.** Nav: Dashboard, Reports, Accounts, APIs,
  Settings are core; Automations (scheduled warm-up jobs) is the only advanced
  destination today. Settings: Appearance, Import, Guest Access, Password,
  Session, TOTP, and API Keys stay flat; Routing tuning, Upstream Proxy pools,
  Model Sources, Firewall, Quota Planner, and Sticky Sessions collapse into
  the Advanced group.
- **One-item Advanced menu is intentional, not over-engineering.** The menu is
  the mandated landing zone for future power features per PRINCIPLES.md P3: a
  new page-level destination defaults to the Advanced menu unless a spec
  explicitly designates it core.
- **Advanced sections fetch on expand, not on page load — intentional.** The
  Advanced settings group unmounts its children while collapsed (Radix
  Collapsible default, no `forceMount`). Sections that issue queries on mount
  (firewall entries, quota planner, sticky sessions, model sources) therefore
  do not fire network requests when an operator merely opens `/settings`; the
  requests fire on the first expand. This trims first-paint work for the
  common path and must not be flagged as a data-loading regression.
- **Arrays stay in `app-header.tsx`.** `CORE_NAV_ITEMS` and
  `ADVANCED_NAV_ITEMS` are flat `as const` arrays in the header component (no
  separate nav-items module); the CI simplicity budget manifest
  (`.github/simplicity-budgets.toml`, `[core_nav]`) points at this file.
- **No new routes.** `/automations` deep links stay as-is. The legacy
  `/firewall` compatibility route redirects to `/settings?advanced=1#firewall`
  so Advanced expands and the firewall section is in view; plain `/settings`
  stays collapsed by default. Regression tests cover both.

### Example

A read-only guest opens `/settings`: they see Appearance, Import, and API Keys
cards plus a collapsed "Advanced settings" row. No firewall/quota/sticky-session
requests have been issued. One click on the row mounts all six advanced
sections with their controls disabled by the existing `canWrite` gating.

### Testing notes

- Tests that asserted advanced sections on load (settings-page unit test,
  firewall integration flow, header Automations link) expand/open first —
  asserting through the same one-interaction path an operator uses.
- The accounts reset-credits badge stays on the core Accounts item in both
  desktop and mobile navs.

## Dashboard partial-failure isolation

### Purpose and scope

The dashboard overview and request-log listing are independent operator surfaces. A request-log storage or listing outage should not remove healthy fleet quota and account controls. Normative behavior lives in [`spec.md`](./spec.md); while the change is active, its added requirement lives in [`../../changes/preserve-dashboard-overview-on-log-failure/specs/frontend-architecture/spec.md`](../../changes/preserve-dashboard-overview-on-log-failure/specs/frontend-architecture/spec.md).

### Decision rationale

The page composes overview-backed view data as soon as overview data exists and treats request logs as a section-local state machine: initial loading, terminal error announced through a local alert semantic, or ready. Recovery calls the existing request-log query's local refetch operation. A broader dashboard invalidation was rejected because it would refetch healthy data and could make usable incident context disappear.

### Constraints and non-goals

This boundary does not change API shapes, query keys, retry policy, polling, or backend reliability. It does not preserve stale rows after later refetch failures, introduce route splitting or global state, or define global live-region behavior. The header refresh action intentionally keeps its existing broad refresh semantics; only the Request Logs Retry action is local.

### Failure mode and example

If overview, projections, and request-log options return successfully while the initial listing reaches terminal HTTP 500, operators continue to see statistics, quota charts, and account controls. The Request Logs heading remains visible with a locally announced endpoint error and native Retry control. After the endpoint recovers, keyboard-activating Retry replaces that error with the returned rows without issuing another overview request.

### Testing notes

The product-boundary regression renders the real `/dashboard` App route with the production query retry policy and MSW handlers. It counts each request family, seeds unique values for a statistic, quota surface, projection metric, and account control, focuses and keyboard-activates native Retry, holds the recovered listing response pending long enough to assert all healthy surfaces remain mounted, and then verifies the recovered row.

## Estimated pool-allocation control

The API-key create/edit dialogs present `Estimated pool allocation (%)` as a standalone optional policy above fixed usage rules. It is not rendered as a counter rule because it has no local current value or reset clock. Table and detail summaries describe only the configured cap and keep the approximation explicit.

## Manual recovery for quota-exceeded accounts

The [quota Resume requirement](spec.md#requirement-quota-exceeded-accounts-expose-manual-resume) exposes the existing reactivation API for an operator inspecting a quota hold. Reusing Resume keeps one recovery action and one backend compare-and-set transition; no new endpoint, setting, or navigation item is needed.

For example, an operator selecting a weekly-only Pro account marked `quota_exceeded` can choose Resume. The existing mutation sends `POST /api/accounts/{id}/reactivate`, refreshes account data, and the detail returns to its active-account actions. Read-only and busy states retain the existing disabled control. This action does not replace credentials, so `reauth_required` still requires reauthentication. Automatic quota recovery continues to require its existing freshness and debounce evidence, and request-specific routing constraints remain in force.

## Inventory charts, sorting and expiring credits

See [inventory distributions](spec.md#requirement-accounts-inventory-distributions), [compact API-key inventory](spec.md#requirement-optional-compact-api-key-inventory), [expiry warnings](spec.md#requirement-reset-credit-expiry-warning) and [account sorting](spec.md#requirement-status-and-remaining-quota-account-sorting). Plan/status charts count the complete loaded inventory before filters. The existing donut gains a distribution presentation; capacity charts retain their existing behavior. Blank plans and unrecognized statuses remain visible as unknown categories.

The Accounts default remains Most reset credits. Quota sorts treat zero as known and keep missing values last; reset, label and ID ties preserve deterministic order. For example, descending monthly remaining quota orders 80%, 0%, then unknown, and changing the sort preserves an explicitly selected account.

A single list-local clock subscription polls once a minute while both credit badge settings are visible. It refreshes its snapshot when visibility returns and releases its timer when hidden or unmounted. This avoids stale warning state without reading an impure clock during React render or refetching account data. The nearest valid expiry within 72 hours marks positive cached credit counts; paused-account snapshots and redemption policy are unchanged.

APIs retain the Detail view as default. A local browser preference enables a compact paginated list with the same filters and permission controls. Recorded last use, requests, tokens, cached tokens or cost count as usage evidence even if other metadata is absent. For example, a key with one recorded token and no request count does not appear under Key not used. Missing evidence is not proof that the key was never used. Storage denial leaves switching usable; read-only principals can open details without management actions.

## Ordered auth-file imports and capability control labels

The import dialog sends a selected list through the existing single-file mutation, with one request active at a time. If a.json succeeds and b.json fails, the remaining queue is b.json followed by c.json; successful imports remain available and are not repeated on retry. File objects remain in component memory and only filenames are displayed. The batch owns its busy state across per-file mutation transitions and rejects dismissal or duplicate submission until it settles. Model Source controls use translated accessible names and per-form IDs so label clicks address the correct checkbox. See the owning requirements in [spec.md](spec.md) and the five-record verification artifact.
