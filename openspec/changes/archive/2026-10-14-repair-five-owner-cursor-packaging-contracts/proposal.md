## Why

Required-owner WebSocket connect failures can be replaced by generated owner-unavailable errors, and cancelled SQLite RETURNING writes can retain a writer lock through traceback-held cursors. Five unverified registry records also need independent evidence for Docker callback isolation, patched urllib3 packaging and native stream documentation.

## What Changes

- Preserve the original connect error for hard response/file/session owners while retaining movable-request failover and cleanup.
- Weakly track SQLite driver cursors and finalize every live cursor before closing the connection on its existing worker thread; install the factory on request and background engines.
- Restore the native stream normalizer's runtime docstring without changing executable stream behavior.
- Independently verify existing loopback-only opt-in Docker callbacks and urllib3 >=2.8.0 lock/package metadata.
- Own exactly UP-PR-2591, UP-PR-2600, UP-PR-2098, UP-PR-2588 and UP-PR-2595; retain unrelated dirty work and all external verification limits.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: required-owner connection failure envelopes remain original.
- `database-backends`: connection teardown finalizes retained SQLite cursors despite cancellation and cleanup errors.

## Impact

Application changes: app/modules/proxy/_service/websocket/mixin.py, app/modules/proxy/api.py, app/db/session.py and new app/db/sqlite_connection.py. Tests: focused owner-connect public/native/bridge regressions, retained-cursor and terminal-batcher SQLite regressions, existing Docker OAuth and stream tests. OpenSpec deltas/canonical context and issues-check.md carry the five-row evidence. No configuration, migration, dependency-version change, publication or deployment.
