# Operator Pause and quota observations

The user clarified on 2026-10-01 that the local client appeared to exhaust quota while the panel still showed approximately 11%; client version and precise Pause timing are uncertain. This observation does not establish new post-Pause dispatch or compare the same account/window/sample time. The direct WebSocket bypass is investigated independently.

Example: first response completes on A, the dashboard Pause API commits, and a second fresh or anchored response.create arrives on the same socket. That frame must be refused using the visible routing marker. An earlier in-progress response remains owned by A and may finish; Pause does not promise instantaneous cancellation or an upstream quota freeze.

Routing diagnostics must distinguish pooled quota from the caller's own quota, 5h versus weekly windows, stale dashboard evidence and direct client traffic. No cause for INC-01/INC-08 is asserted without client/server request correlation.
