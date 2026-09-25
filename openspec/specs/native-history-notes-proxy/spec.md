# Native History and Notes Proxy Specification

## Purpose
Expose native Codex history/notes v2 operations and maintain thread/session affinity and owner failover semantics.

## Requirements

### Requirement: Native History and Notes v2 Endpoints
The proxy SHALL expose the following native Codex operations under `/backend-api/codex/alpha/` and `/v1/alpha/`:
- `history/v2/`: `list_windows`, `list_items`, `read_item`, `search_contents` (POST).
- `notes/v2/`: `list_files_by_prefix`, `read_file`, `search_contents`, `append_to_file`, `write_file`, `thread_hint` (GET and POST).

#### Scenario: Known operations forward to upstream
- **WHEN** an authenticated client sends a request to any of the 10 supported operations
- **THEN** the request is forwarded to upstream ChatGPT backend via the selected account
- **AND** response status and payload are preserved.

#### Scenario: Unknown operations return 404
- **WHEN** a client sends a request with an unrecognized operation name under `alpha/history/v2/` or `alpha/notes/v2/`
- **THEN** the proxy returns HTTP 404 `not_found`.

#### Scenario: Trailing slash paths are supported equivalently
- **WHEN** a request arrives at `/backend-api/codex/alpha/.../<operation>/`
- **THEN** it is handled equivalently to `/backend-api/codex/alpha/.../<operation>`.

### Requirement: Thread and Child-Thread Affinity
Codex control requests SHALL evaluate `thread-id` headers for stickiness and preserve child-thread subagent placement preferences.

#### Scenario: Thread identity routes to thread owner
- **WHEN** a control request includes a `thread-id` header
- **THEN** it resolves thread affinity to route to the account associated with that thread.
