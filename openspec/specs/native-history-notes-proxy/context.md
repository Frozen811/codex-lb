# Native History and Notes Proxy Context

## Purpose
Explains native Codex history and notes v2 operations (`/alpha/history/v2` and `/alpha/notes/v2`) and thread affinity preservation.

## Background & Rationale
Experimental Codex context management uses native history and notes operations to store checkpoints, manage private scratchpads across session windows, and retrieve conversation logs.
In previous proxy versions, these paths returned HTTP 405/404, preventing experimental context management tools from working through codex-lb.

## Operations
Supported `history/v2` operations (POST):
- `list_windows`: lists available history windows
- `list_items`: lists conversation items
- `read_item`: reads item payload
- `search_contents`: searches history contents

Supported `notes/v2` operations (GET and POST):
- `list_files_by_prefix`: lists scratchpad files
- `read_file`: reads scratchpad file
- `search_contents`: searches scratchpad files
- `append_to_file`: appends text to a file
- `write_file`: creates or overwrites a file
- `thread_hint`: provides context hints

Unrecognized operation names return HTTP 404 with OpenAI-style error envelope.
Requests route to the thread owner via `thread-id` headers and retain child-thread/subagent placement preferences.

## Transport parity and verification scope

The [opaque transport requirement](spec.md#requirement-native-history-and-notes-preserve-opaque-transport-data)
keeps native payloads and allowed encryption headers unmodified. For example,
`POST /v1/alpha/notes/v2/write_file/?path=a&path=b` forwards the original bytes
and both query values to the selected account's `codex/alpha/notes/v2/write_file`.
The duplicated `/backend-api/codex/v1/` prefix uses the same operation.

Local route coverage exercises every supported operation and slash variant,
unknown operations, scoped API-key admission, repeated thread affinity and
child-thread placement. A loopback HTTP upstream additionally checks raw media
type and gzip decoding. Encryption-header values in these tests are synthetic;
no hosted encryption/decryption or account-pool history recovery is claimed.
Unavailable upstreams return the selected account's control error; native history/notes never retry across accounts.

## Body-session ownership

The [body-session contract](spec.md#requirement-native-body-session-owns-history-and-notes)
uses the native JSON context identity to keep notes and history account-local.
For example, a write with `{"context":{"session_id":"task-a"},"path":"notes.md"}`
retains the same owner when the process header changes. Its first operation can
inherit an eligible existing soft process-session owner for `task-a`; later
inference rotation does not move its notes. Header-only GET/POST compatibility
requests retain their existing affinity and child placement.

Bodies are validated as JSON objects and forwarded as the original bytes.
Encrypted-argument and output-truncation headers remain opaque. Missing,
blank or nonstring session values do not manufacture a body-session owner.
A selected owner's 401, quota error or refresh connection failure cannot send
the operation to another account. Local API regressions use synthetic headers
and isolated SQLite; native decryption and pooled history fan-out are outside
this account-local contract.
