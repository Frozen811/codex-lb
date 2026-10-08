## MODIFIED Requirements

### Requirement: Proactive active account credential refresh

Codex-LB SHALL periodically refresh account credentials in the background when an account's last refresh is strictly older than twelve hours, independently of ordinary request-time freshness. Accounts with status `active` or `paused` SHALL be eligible for proactive credential refresh; accounts with status `reauth_required` or `deactivated` SHALL NOT be selected. Proactive credential refresh MUST NOT change a paused account's routing eligibility: a paused account remains excluded from request routing regardless of refresh outcome, except that a permanent refresh failure transitions the account to its documented permanent-failure status the same way it does for active accounts. The proactive refresh scheduler SHALL be enabled by default with zero required configuration. Whether a refresh pass runs SHALL be decided by the dashboard setting `auth_guardian_enabled` (a nullable `dashboard_settings` column; NULL inherits the deprecated `CODEX_LB_AUTH_GUARDIAN_ENABLED` environment variable, then the default `true`), exposed with provenance on `GET`/`PUT /api/settings`. The scheduler loop SHALL always start; each refresh pass SHALL read the effective value from the dashboard-settings snapshot at the start of the pass and SHALL skip the pass while it is `false`, so a change made in the dashboard applies on the next pass on every replica without a restart. The multi-replica leader guard remains a precondition for any refresh work.

#### Scenario: Idle active account becomes stale

- **GIVEN** an account has status `active`
- **AND** its `last_refresh` is older than twelve hours
- **WHEN** Auth Guardian runs on the elected leader
- **THEN** Codex-LB force-refreshes that account without requiring request traffic to select it first

#### Scenario: Idle paused account keeps its refresh token alive

- **GIVEN** an account has status `paused`
- **AND** its `last_refresh` is older than twelve hours
- **WHEN** Auth Guardian runs on the elected leader
- **THEN** Codex-LB force-refreshes that account's credentials
- **AND** the account's status remains `paused`
- **AND** the account remains excluded from request routing

#### Scenario: Known-bad credentials are not refreshed

- **GIVEN** an account has status `reauth_required` or `deactivated`
- **AND** its `last_refresh` is older than twelve hours
- **WHEN** Auth Guardian selects refresh candidates
- **THEN** the account is not selected

#### Scenario: Guardian runs on a default install

- **GIVEN** a single-replica deployment with no `CODEX_LB_AUTH_GUARDIAN_*` configuration and no dashboard value for `auth_guardian_enabled`
- **WHEN** the Auth Guardian scheduler is built
- **THEN** the scheduler is enabled and its passes run

#### Scenario: Dashboard pause applies on the next pass without a restart

- **GIVEN** the scheduler was started with `auth_guardian_enabled` effectively `true`
- **WHEN** an operator sets `auth_guardian_enabled` to `false` in the dashboard
- **THEN** the next refresh pass skips without refreshing any account
- **AND** when the operator sets it back to `true` (or clears it so the inherited `true` applies) the pass after that refreshes stale accounts again
- **AND** no replica was restarted

#### Scenario: Environment alias applies only while the dashboard value is unset

- **GIVEN** `CODEX_LB_AUTH_GUARDIAN_ENABLED=false` and no dashboard value
- **WHEN** an operator sets `auth_guardian_enabled` to `true` in the dashboard
- **THEN** refresh passes run and `provenance.auth_guardian_enabled.source` is `dashboard`
- **AND** clearing the dashboard value returns to the environment value (`source` `env`)

#### Scenario: Guardian rechecks idle age independently of request freshness

- **WHEN** an active or paused account is thirteen hours old while request-time freshness is eight days
- **THEN** the guardian force-refreshes it
- **AND** a row refreshed by a peer to exactly twelve hours old or newer is skipped at the persisted-row recheck

### Requirement: Credit-backed secondary quota remains usable

When account status is derived from persisted usage snapshots, an exhausted secondary-window usage percentage MUST NOT by itself mark an account `quota_exceeded` if the governing usage snapshot reports usable credit-backed capacity. Usable credit-backed capacity is present when `credits_unlimited` is true or `credits_balance` is positive; `credits_has` alone MUST NOT establish spendable capacity.

This credit-aware interpretation MUST be shared by proxy account selection and account/dashboard summary status mapping so an account selected as usable by the proxy is not simultaneously displayed as `quota_exceeded` in the operator summary. Primary-window exhaustion with an available or credit-covered secondary window MUST still produce `rate_limited`; both exhausted windows without spendable credits MUST produce `quota_exceeded` with the secondary reset, and paused or deactivated accounts MUST NOT be reactivated solely because a usage snapshot reports usable credits.

#### Scenario: Secondary quota exhausted with credits remains active

- **GIVEN** an account is persisted as `quota_exceeded`
- **AND** its governing secondary-window usage reports `used_percent >= 100`
- **AND** the same usage snapshot reports usable credit-backed capacity
- **WHEN** proxy selection or account-summary mapping derives the effective status
- **THEN** the effective status is `active`

#### Scenario: Exhausted primary window keeps rate-limit precedence

- **GIVEN** an account has usable credit-backed capacity in its usage snapshot
- **AND** its primary-window usage reports `used_percent >= 100`
- **WHEN** proxy selection or account-summary mapping derives the effective status
- **THEN** the effective status is `rate_limited`

#### Scenario: Operator-disabled states are preserved

- **GIVEN** an account is `paused` or `deactivated`
- **AND** its usage snapshot reports usable credit-backed capacity
- **WHEN** proxy selection or account-summary mapping derives the effective status
- **THEN** the account remains `paused` or `deactivated`

#### Scenario: Credit flag without spendable balance

- **WHEN** the secondary window is exhausted and credits_has is true with a missing, zero or negative balance and no unlimited credits
- **THEN** selection and the operator summary retain quota_exceeded
- **AND** if both windows are exhausted the secondary reset remains authoritative

### Requirement: Credit-backed usage remains selectable after quota windows fill

When deriving effective account status from upstream usage samples, the system MUST treat the latest credit metadata as an override for secondary quota-derived blocking state. If the latest usage sample with credit metadata reports `credits_unlimited = true` or `credits_balance > 0`, then secondary quota windows at `100%` MUST NOT by themselves make the account `quota_exceeded`. Primary-window exhaustion MUST keep `rate_limited` precedence when the secondary window is available or covered by spendable credits. Both exhausted windows without spendable credits MUST remain `quota_exceeded`. A bare `credits_has = true` flag MUST NOT grant the override.

This override MUST NOT reactivate accounts that are explicitly `paused` or
`deactivated`. When multiple usage samples carry credit metadata, the newest
sample by `recorded_at` MUST be used.

#### Scenario: Credit-backed weekly account remains selectable

- **GIVEN** an account is otherwise routable
- **AND** its weekly usage window reports `used_percent = 100`
- **AND** its primary usage window is below `100`
- **AND** the newest usage sample with credit metadata reports a positive credit balance
- **WHEN** the load balancer derives account state
- **THEN** the derived status remains `active`
- **AND** the account remains eligible for selection

#### Scenario: Credit-backed account remains rate-limited when primary window is exhausted

- **GIVEN** an account is otherwise routable
- **AND** its primary usage window reports `used_percent = 100`
- **AND** the newest usage sample with credit metadata reports a positive credit balance
- **WHEN** the load balancer derives account state
- **THEN** the derived status is `rate_limited`
- **AND** the reset guard points at the primary reset time

#### Scenario: Newer zero-credit sample removes the override

- **GIVEN** an older usage sample reports available credits
- **AND** a newer usage sample reports no credits and zero credit balance
- **WHEN** quota status is derived from usage
- **THEN** the newer zero-credit sample is authoritative
- **AND** a full quota window can still derive `rate_limited` or `quota_exceeded`

#### Scenario: Paused account is not reactivated by credits

- **GIVEN** an account is paused
- **AND** its newest usage sample reports available credits
- **WHEN** quota status is derived from usage
- **THEN** the account remains paused

### Requirement: Preflight refresh credential failure retains unexpired access tokens

When an ordinary active-account preflight receives a permanent refresh-credential-only failure (`refresh_token_invalidated`, `refresh_token_expired`, `refresh_token_reused`, `invalid_refresh_token` or `invalid_grant`), the system MUST re-read the latest account row. Recovery MUST require a row without a deletion marker, status `reauth_required`, the matching canonical refresh warning and a known access-token expiration strictly in the future. The request SHALL continue with that stored token only while these conditions hold, without clearing the warning or changing credentials or refresh timestamps. Forced callers sharing the exchange MUST still fail. Actual access rejection, account/session invalidation, transient failures, expired or unknown access tokens and operator-disabled states MUST NOT qualify for this fallback.

#### Scenario: Unexpired access token is retained after preflight refresh revocation
- **GIVEN** an active account with an unexpired access token whose `last_refresh` warrants preflight refresh
- **WHEN** preflight refresh receives `refresh_token_invalidated` from upstream
- **THEN** the account is marked `reauth_required` in the database
- **AND** `ensure_fresh` does not raise `RefreshError`
- **AND** the unexpired access token is returned and dispatched upstream

#### Scenario: Operator deletion wins over preflight recovery

- **WHEN** ordinary preflight receives a permanent refresh-only failure but the fresh account row has been marked for deletion
- **THEN** the request MUST fail without dispatching the retained access token
- **AND** the deletion marker, credentials and refresh warning MUST remain unchanged

#### Scenario: Forced caller and ordinary caller share refresh failure

- **WHEN** ordinary and forced callers share one failed refresh exchange in either arrival order
- **THEN** only the ordinary active caller with an eligible persisted row retains its access token
- **AND** the forced caller receives the refresh failure

#### Scenario: Session invalidation does not qualify as refresh-only failure

- **WHEN** preflight fails because the account session or access credentials have been invalidated
- **THEN** the request fails even if the stored access-token expiry is in the future
