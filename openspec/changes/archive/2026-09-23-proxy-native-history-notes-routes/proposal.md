# Proxy native history and notes v2 routes

## Why

Experimental Codex context management uses native history and notes v2 operations to store checkpoints, manage private scratchpads across session windows, and retrieve conversation logs. In current proxy releases, these endpoints are unhandled, returning HTTP 405/404, which prevents experimental context management clients from operating through codex-lb.

## What Changes

1. **Proxy route handlers**:
   - Register endpoints under `/backend-api/codex/alpha/history/v2/{operation}` (and trailing slash `/`) and `/v1/alpha/history/v2/{operation}`. Supported operations: `list_windows`, `list_items`, `read_item`, `search_contents` (POST).
   - Register endpoints under `/backend-api/codex/alpha/notes/v2/{operation}` (and trailing slash `/`) and `/v1/alpha/notes/v2/{operation}`. Supported operations: `list_files_by_prefix`, `read_file`, `search_contents`, `append_to_file`, `write_file`, `thread_hint` (GET and POST).
   - Forward all valid operations via the existing `_codex_control_proxy` infrastructure to the selected ChatGPT account.
   - Return HTTP 404 for unrecognized operation names.

2. **Session and Thread Affinity**:
   - Update `_sticky_key_for_codex_control_request` to honor `thread-id` headers and child-thread lineage (`x-openai-subagent`, `x-codex-parent-thread-id`), preserving continuity and subagent account steering.

3. **Security & Capabilities**:
   - Register the new routes in `_FAIL_CLOSED_HTTP_ROUTES` so capability-bearing ingress fail closed appropriately when unsupported.

## Capabilities

### New Capabilities
- `native-history-notes-proxy`: Exposes native Codex history/notes v2 operations and maintains thread/session affinity and owner failover semantics.
