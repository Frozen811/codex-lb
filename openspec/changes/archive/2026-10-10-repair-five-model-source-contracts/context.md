## Scope and rationale

Exactly five selected rows: UP-ISSUE-2318, UP-PR-2324, UP-ISSUE-2290, UP-PR-2305, UP-PR-1905. The compact proposal requests forwarding, whereas responses-api-compat and the verified UP-PR-2451 contract require clean refusal. Verify that implemented contract and explicitly record the proposal mismatch; do not call forwarding implemented.

The CPA pair lacks runtime discovery despite historical helper-only claims. Implement configure-once discovery in the fork without importing upstream migration branches. Provider authentication and translation remain external.

Example: POST /api/model-sources/ with supportsResponses=true and catalogMode=cli_proxy_api. A scheduled tick reads /models?client_version=... with only the source's inference credential. Removing model-a from a valid snapshot retains its row and refuses requests; a 500 or malformed snapshot changes nothing. A returning model restores availability, while an operator pause remains in effect.

The existing 292 dirty files have a hash manifest in the task's temporary snapshot. Preserve unrelated contents; local tests do not establish current cloud CI, release or deployment state.
