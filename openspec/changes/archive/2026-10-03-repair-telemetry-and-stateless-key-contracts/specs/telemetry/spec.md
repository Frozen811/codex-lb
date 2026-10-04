## MODIFIED Requirements

### Requirement: Client family allowlist mapping

Telemetry client statistics MUST report only canonical client-family identifiers produced by the documented mapping table, MUST map any unmatched user-agent group to `other`, and MUST NOT transmit raw user-agent group values.

The canonical mapping table (raw `useragent_group` → family):

| Raw group(s) | Family |
| --- | --- |
| `codex_exec`, `codex-tui`, `codex_cli_rs`, `codex`, `codex-cli` | `codex-cli` |
| `Codex Desktop`, `codex desktop`, `codex_chatgpt_desktop`, `codex_atlas` | `codex-desktop` |
| `codex_vscode` | `codex-vscode` |
| `AsyncOpenAI` | `openai-sdk-python` |
| `OpenAI` | `openai-sdk-js` |
| `ai`, `ai-sdk` | `vercel-ai-sdk` |
| `opencode` | `opencode` |
| `Mozilla` | `browser` |
| `curl`, `undici`, `node`, `Python-urllib`, `python-requests`, `aiohttp` | `script` |
| anything else | `other` |

The payload MUST include `clients_other_ratio` so mapping coverage decay is observable
without ever transmitting the unmatched raw values.

#### Scenario: Private tool names never leave the instance

- **WHEN** request logs contain a user-agent group not present in the mapping table
- **THEN** its traffic is attributed to `other` and the raw group string is absent from the
  payload

#### Scenario: Codex CLI variants collapse to one family

- **WHEN** traffic exists from `codex_exec`, `codex-tui`, and `codex_cli_rs` (the interactive
  Codex CLI's native user-agent fingerprint)
- **THEN** the payload reports a single `codex-cli` family combining all three

#### Scenario: Codex client aliases preserve their family

- **WHEN** stored request logs contain any documented CLI or Desktop group
- **THEN** the settings preview attributes all matching traffic to its canonical family
- **AND** unknown and missing groups contribute only to `other`

### Requirement: Telemetry transmission and opt-out synchronization

Within one application process, telemetry snapshots, dashboard consent decisions, and opt-out notifications MUST be serialized across the complete registration, activation, and final POST sequence. Snapshot transmission MUST re-check active consent and identity before any protocol request under that serialization. Once a dashboard disable commits, no later snapshot registration, activation, or POST from that process MUST be sent until consent becomes active again. Cancellation or transmission failure MUST release serialization ownership. Opt-out timestamps MUST accept valid ISO-8601 datetime strings or datetime objects, reject malformed timestamps, and serialize in UTC with a `Z` suffix; naive datetime inputs MUST be interpreted as UTC. Requesting a preview while environment fallback disables undecided telemetry MUST NOT create or persist an identity.

#### Scenario: Disabled queued snapshot sends no protocol requests

- **GIVEN** a snapshot waits while dashboard disable commits
- **WHEN** the snapshot gets transmission ownership
- **THEN** it observes inactive consent and sends no registration, activation, or snapshot

#### Scenario: Snapshot transmission aborts when opt-out occurs concurrently

- **GIVEN** a pending telemetry snapshot transmission
- **WHEN** an opt-out event is dispatched concurrently
- **THEN** consent re-check under the transmission lock observes that telemetry is disabled
- **AND** the snapshot POST is aborted

#### Scenario: Dashboard disable waits for an in-flight snapshot

- **GIVEN** a snapshot protocol request is in flight in the process
- **WHEN** the dashboard disables telemetry
- **THEN** the snapshot finishes or is cancelled before the disable commits
- **AND** the final opt-out follows the snapshot protocol without later stale activation

#### Scenario: Cancellation releases transmission ownership

- **WHEN** an in-flight snapshot is cancelled or fails
- **THEN** a dashboard decision and its opt-out can still complete

#### Scenario: Opt-out timestamps are validated and canonical

- **WHEN** an opt-out is built with an ISO-8601 datetime string or datetime input
- **THEN** its timestamp serializes as the equivalent UTC datetime ending in `Z`
- **AND** malformed timestamp strings are rejected before signing

#### Scenario: Telemetry preview under env kill switch does not write identity

- **GIVEN** undecided telemetry is disabled via `CODEX_LB_TELEMETRY_ENABLED=false`
- **WHEN** the dashboard requests status or preview
- **THEN** no instance identity is generated or saved
