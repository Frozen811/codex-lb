## Context

An API-key-restricted request passes a fixed allowed account collection to selection. A legacy hard CODEX_SESSION row can resolve to an owner outside that collection. Selection reports hard-affinity saturation, but the no-wait proof only recognizes explicit exclude_account_ids, so streaming keeps reselecting until the full request budget expires. Both observed failure envelopes are closed failures, but the wait is futile and the scope control's exact error becomes timing-dependent.

## Decisions

Carry the existing account_ids constraint into StickySelectionRequest as an optional frozen allowed set. The existing boolean exclusion proof remains false for non-hard-affinity failures and temporarily unhealthy in-scope owners; it becomes true if the resolved hard owner is either explicitly excluded or outside the supplied allowed set. Keep owner identity out of public error surfaces and do not alter retirement authority or sticky mutation.

The sticky fixture uses a copy of the real Settings model with its existing explicit values and a matching 75-second stream budget. A real-route callback verifies the selector marks the out-of-scope owner excluded before the recovery wait can be taken, retaining dispatch-forbidden and unmodified-owner-row assertions. Selector controls exercise both scoped-out and scoped-in temporarily unavailable owners.

## Risks / Trade-offs

Only the caller-supplied immutable allowed-account constraint is added to the proof; live account health and missing database rows are not treated as a policy exclusion. Existing genuine-owner recovery remains allowed. The fixture gains missing production fields without increasing a deadline or weakening expected errors.
