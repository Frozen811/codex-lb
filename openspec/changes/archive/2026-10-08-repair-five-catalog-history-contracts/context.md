## Scope and sources

Exactly UP-PR-2445, UP-PR-2101, UP-PR-2085, UP-ISSUE-1467 and UP-PR-2543. source-snapshot.json records fresh GitHub descriptions and exact PR heads. Source claims do not establish local correctness.

## Example and decisions

A notes write with {"context":{"session_id":"task-a"},"path":"notes.md"} remains on its notes owner when the process header changes. A quota error is returned on that owner rather than writing another account's notes.

Astra labels such as gpt-6-astra-extra-high-fast are normalized by the existing request-policy path. The captured official upstream catalog is https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/models-manager/models.json.

## Constraints and failure modes

No new setting or data schema. Native object validation does not rewrite body bytes. Ordinary Responses affinity remains soft; native body sessions are hard. Missing body session retains header compatibility and does not authorize cross-account retries.

## Verification boundaries

Local API stubs and isolated databases can establish routing and catalog contracts. Live Codex/provider acceptance, public artifacts, cloud CI and production are independent. No publication is requested.
