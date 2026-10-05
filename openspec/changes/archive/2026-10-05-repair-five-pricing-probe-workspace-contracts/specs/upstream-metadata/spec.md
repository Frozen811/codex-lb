## ADDED Requirements

### Requirement: Validated Ultrafast price groups survive offline startup
The pricing catalog MUST preserve complete Ultrafast input, cached-read, cache-write and output rates for short and long contexts. Long-context groups MUST share the positive base context threshold. Invalid or incomplete groups MUST NOT replace valid pricing. Compatible refreshes and persisted or bundled snapshots MUST retain the rates.

#### Scenario: Offline Astra pricing
- **WHEN** the service starts offline and prices a confirmed Ultrafast Astra response
- **THEN** its applicable bundled Ultrafast rates are used

#### Scenario: Compatible refresh and invalid mode
- **WHEN** a compatible base-only catalog refresh omits Ultrafast rates
- **THEN** the last valid tier rates remain available
- **AND** an incomplete or mismatched context mode does not replace a valid model

