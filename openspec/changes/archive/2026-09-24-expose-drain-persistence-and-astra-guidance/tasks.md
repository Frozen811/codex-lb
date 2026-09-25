# Tasks: Expose Drain Persistence Ownership and Align Documentation with Astra Guidance

- [x] 1. Expose Request-Persistence Ownership in Internal Drain Status (#2343)
  - [x] 1.1 Add `request_persistence_activity_snapshot_nowait` to `RequestLogMixin` in `app/modules/proxy/_service/request_log.py`
  - [x] 1.2 Surface `request_persistence_activity_snapshot_nowait` in `/internal/drain/status` in `app/modules/health/api.py`
  - [x] 1.3 Add unit tests in `tests/unit/test_health_probes.py` verifying persistence snapshot reporting
- [x] 2. Update Client Examples to GPT-6 Astra (#2311)
  - [x] 2.1 Update Codex CLI snippet in `README.md` and `README.zh-CN.md` to `gpt-6-astra`
  - [x] 2.2 Update `docs/client-setup.md` frontier introduction and client examples (Codex, OpenCode, OpenClaw, Hermes)
  - [x] 2.3 Update downloadable example profiles `docs/examples/codex/config.toml` and `docs/examples/codex/daybreak-blue.config.toml`
- [x] 3. Align Agent Instructions with Astra Prompt Guidance (#2309)
  - [x] 3.1 Add Astra prompt guidance section in `AGENTS.md` covering agent autonomy, scope-bounded verification, and test isolation
- [x] 4. Verification and OpenSpec Archival
  - [x] 4.1 Run unit tests and linters
  - [x] 4.2 Sync delta specs to main specs and validate OpenSpec
  - [x] 4.3 Archive OpenSpec change, update ISSUES.md and walkthrough.md
