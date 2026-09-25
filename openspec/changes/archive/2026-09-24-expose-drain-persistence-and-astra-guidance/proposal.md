# Change: Expose Drain Persistence Ownership and Align Documentation with Astra Guidance

## Why

1. **Expose Request-Persistence Ownership During Drain (#2343)**:
   During reversible process drain, `/internal/drain/status` checks `draining`, `bridge_drain_active`, and `in_flight`. However, when an admitted request completes downstream streaming, `in_flight` is decremented while detached background settlement (such as API-key reservation settlement and terminal logging) is still being processed in `_background_cleanup_tasks` and `_request_log_tasks`. Orchestrators (such as Kubernetes preStop hooks) inspecting `/internal/drain/status` may observe `in_flight=0` and terminate the container before database settlement completes, stranding reserved quota or lost terminal logs. Exposing request-persistence activity directly in `/internal/drain/status` allows orchestrators to wait until all persistence tasks have cleanly completed.

2. **Use GPT-6 Astra in Current Client Examples (#2311)**:
   Current README and client setup examples reference `gpt-5.6-sol` as the recommended default model. OpenAI now recommends `gpt-6-astra` for complex reasoning and coding workflows. Updating default examples across `README.md`, `README.zh-CN.md`, and `docs/client-setup.md` to `gpt-6-astra` aligns user guidance with current best practices while keeping model family limits, pricing, and protocol fixtures intact.

3. **Align Agent Instructions with Astra Prompt Guidance (#2309)**:
   The GPT-6 Astra model benefits from explicit prompting instructions regarding autonomy, task ownership, and verification boundaries. Adding explicit Astra alignment guidance in `AGENTS.md` avoids premature user confirmation loops, over-testing of small changes, and clarifies isolated test database safety.

## What Changes

- **Health Drain API**:
  - In `app/modules/proxy/_service/request_log.py`, add `request_persistence_activity_snapshot_nowait(self)` to `RequestLogMixin` returning `request_persistence_pending`, `request_persistence_active`, `api_key_settlements_pending`, and `persistence_drain_active`.
  - In `app/modules/health/api.py`, call `request_persistence_activity_snapshot_nowait()` in `internal_drain_status` and add its fields to the `checks` payload.
  - In `tests/unit/test_health_probes.py`, add tests verifying that `internal_drain_status` surfaces request persistence activity.
- **Client Documentation**:
  - In `README.md`, `README.zh-CN.md`, and `docs/client-setup.md`, update default client setup examples from `gpt-5.6-sol` to `gpt-6-astra`.
- **Agent Instructions**:
  - In `AGENTS.md`, add explicit Astra prompt alignment guidelines regarding agent autonomy, scope-bounded verification, and test isolation.

## Capabilities

### Modified Capabilities
- `graceful-shutdown`: `/internal/drain/status` MUST expose request persistence and API-key settlement activity alongside `in_flight` and bridge activity.
- `user-documentation`: Client configuration examples MUST recommend `gpt-6-astra` as the default model for complex reasoning and coding workflows.

## Impact
- APIs: `/internal/drain/status` includes `request_persistence_pending`, `request_persistence_active`, `api_key_settlements_pending`, and `persistence_drain_active`.
- Documentation: `README.md`, `README.zh-CN.md`, `docs/client-setup.md`, `AGENTS.md`.
- No database migrations, no settings tier modifications.
