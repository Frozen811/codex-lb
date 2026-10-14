## Context

The first response.completed owns the image result and tool usage. Existing collector branches already protect it against trailing error and response.failed, but not response.incomplete. The duplicate Internal host selection requirement contradicts the tested image-compatible Sol/Astra/5.5 order.

## Goals / Non-Goals

Complete exactly the selected five local source scopes. Preserve unrelated dirty work and existing public response/error shapes. Do not claim live-provider, Desktop, hosted CI, public artifact or production verification.

## Decisions

- Once an Images completion is captured, drain subsequent SSE events without reinterpreting them. Before completion, incomplete/failed/error keep their existing refusal behavior.
- Keep one canonical host-selection requirement and remove the obsolete duplicate.
- Test real application ingress and disposable SQLite with synthetic upstream transport; include edit/generation aliases, public model policy and reservation settlement. Inspect task and stream ownership on errors and cancellation.
- Verify screenshot history slimming through supported HTTP/native WebSocket paths, preserving the current turn, IDs and original caller payload. Do not broaden the omission policy.
- Verify the extracted stream entrypoint retains lazy retry ownership, filtering and forwarded options; verify authentic terminal errors and cleanup budgets using existing focused lifecycle suites.

## Risks / Trade-offs

Draining remains necessary for persistence cleanup. A terminal event before completion still rejects the result. Synthetic provider tests cannot establish production failure rates or vendor acceptance.
