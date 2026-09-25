# sticky-session-operations Specification Delta

## ADDED Requirements

### Requirement: Sticky thread switchover deferred to compaction boundaries

To protect prompt-cache locality and prevent unexpected token re-billing during active conversations, sticky thread selection MUST NOT switch the pinned account during standard follow-up turns under routine quota pressure (`reallocate_sticky=False`). Sticky switchover MUST be deferred until explicit compaction boundaries where `reallocate_sticky=True` is enabled.

#### Scenario: Normal follow-up maintains sticky affinity
- **GIVEN** an active conversation thread with a healthy pinned account
- **WHEN** a normal follow-up request is processed
- **THEN** selection retains the pinned account without triggering sticky reallocation

#### Scenario: Compaction boundary enables sticky reallocation
- **GIVEN** a remote compaction request for an active thread
- **WHEN** account selection runs with `reallocate_sticky=True`
- **THEN** sticky reallocation is permitted to switch to a healthier account
