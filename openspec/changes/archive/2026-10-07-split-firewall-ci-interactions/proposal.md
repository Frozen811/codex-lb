## Why

Cloud CI at 352e58d9 still exceeded the unchanged 15-second timeout in the
combined Firewall add/remove flow. All other frontend and backend tests passed.
Preloading and paste alone do not provide enough margin on a busy runner.

## What Changes

Keep every interaction and assertion in independent route-level checks:
Advanced expansion, adding an IP, removing an existing IP and legacy routing.
Each starts with fresh MSW storage and
auth state. Add assertions for confirmation, input cleanup and dialog disposal.
Retain the existing lazy route preload, real App, timeout and coverage gates.

## Impact

The existing fast flow requirements remain unchanged; only frontend test
organization and its verification context change.
