## Why

Five open registry records describe missing account inventory controls and API-key model selection. Operators cannot inspect complete plan/status distributions, sort remaining quotas, see imminent reset-credit expiry, compact unused keys, or allow supported image adapter models through the dashboard picker.

## What Changes

- Add accessible plan/status inventory charts based on all loaded accounts (UP-PR-2565).
- Add an optional persisted compact API-key list, sorting, pagination and recorded-usage filtering while retaining the default detail view and permissions (UP-PR-2566).
- Expose supported image adapter models with typed `imageOnly` metadata in the dashboard picker and exclude them from Automations (UP-PR-2576).
- Mark positive reset-credit counts whose nearest expiry is within 72 hours; refresh the warning without refetching and honor existing visibility settings (UP-PR-2577).
- Add status and remaining 5h/weekly/monthly quota sort modes, retaining unknown values last and deterministic ties (UP-PR-2578).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `frontend-architecture`: Account inventory charts, key list controls, expiry warning and account sorting.
- `api-keys`: Supported image models in the dashboard catalog and key allowlists.

## Impact

Accounts/APIs pages, shared donut presentation, API-key usage helpers, dashboard model schemas/endpoint, supported image model constants and Automations model filtering. Focused component/integration tests, synthetic before/after screenshots and local contract checks. No dependency, migration, environment setting, core navigation item or release change. Preserve the 85 existing modified/untracked files captured before work; shared locales, api-keys specs and registry require additive updates.
