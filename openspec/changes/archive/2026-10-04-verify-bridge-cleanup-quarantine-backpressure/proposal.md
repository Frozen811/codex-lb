## Why

Three unverified registry claims need independent regression evidence: UP-ISSUE-2270 scheduled retry cleanup, UP-ISSUE-2268 quarantine ownership, and UP-ISSUE-2266 paused downstream streams. Existing generation fencing misses same-timestamp failure changes and a cleanup pass can reselect a changed candidate; closed stream queues retain payloads and cancelled putters.

## What Changes

- Fence scheduled purge on the selected failure count as well as timestamp and generation, and visit each key once per pass.
- Verify existing quarantine ownership and settlement fences through real bridge completions and replacement sessions.
- Release detached stream buffers and cancelled waiters, and verify bounded delivery, resumed ordering, stall failure and reservation cleanup.
- Record scoped evidence and update exactly the three selected registry rows.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: complete scheduled purge fencing and detached queue cleanup requirements; verify quarantine lifetime and paused delivery contracts.

## Impact

`app/modules/proxy/durable_bridge_repository.py`, HTTP bridge queue/delivery code, focused tests and the owning OpenSpec spec/context. No schema, dependency or configuration addition. Work remains local; live providers, public artifacts and cloud CI are separate scopes.
