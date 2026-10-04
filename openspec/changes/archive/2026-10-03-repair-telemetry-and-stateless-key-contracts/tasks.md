## 1. Telemetry opt-out ordering

- [x] 1.1 Add failing loopback collector/API races at registration, activation, and snapshot; verify pre-fix failures.
- [x] 1.2 Serialize complete snapshot protocol and consent writes; verify completion, failure, cancellation, retry, and subsequent disabled silence.
- [x] 1.3 Validate opt-out timestamps and UTC output; verify malformed refusal and valid string/datetime compatibility.

## 2. Client statistics and shared keys

- [x] 2.1 Verify all Codex client groups through stored request logs and the public preview API; synchronize the mapping contract.
- [x] 2.2 Verify raw environment key account import/decryption, explicit override precedence, default file fallback, invalid settings, and sentinel mismatch using isolated storage.

## 3. Final verification

- [x] 3.1 Run focused subsystem suites, Ruff, scoped typing, and strict OpenSpec validation; record results.
- [x] 3.2 Review implementation against each requirement and scenario, synchronize stable context, update exactly three registry entries, and archive only after verification.
