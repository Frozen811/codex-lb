## REMOVED Requirements

### Requirement: Abrupt eventless upstream websocket drops remain account-neutral
**Reason**: This obsolete requirement contradicts the later `Abrupt upstream websocket drops remain account-neutral` requirement by requiring post-output drops to penalize accounts.
**Migration**: Use the existing later requirement for all abrupt HTTP bridge drops. Preserve `stream_incomplete`, unsafe replay refusal, eventless-only windowed drain, authored-close/protocol penalties, and bridge-scope circuit accounting.
