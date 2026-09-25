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
