## MODIFIED Requirements

### Requirement: SCIM body admission stops at the route limit

SCIM resource writes MUST enforce their 64 KiB body limit while consuming
the request stream. An oversized request MUST stop receiving at the first
chunk that exceeds that limit and MUST return the SCIM 413 envelope without
writing an account. Buffered body bytes MUST NOT exceed the route limit.
The existing declared-length precheck MUST remain in effect. A valid body
split across chunks, including a body exactly at the limit, MUST remain valid.
At the SCIM route, a supplied Content-Length MUST contain only ASCII decimal
digits; malformed values MUST return SCIM 400 without reading the body.
Decimal lengths exceeding the route limit MUST return SCIM 413 before body
consumption even when their digit count exceeds the runtime integer parser's
limit. Leading zeroes MUST NOT change the declared length's meaning.

#### Scenario: Stream exceeds the limit without a declared length

- **GIVEN** a SCIM body arrives in several chunks without Content-Length
- **WHEN** received bytes first exceed 64 KiB
- **THEN** the API returns SCIM 413 without reading subsequent chunks
- **AND** it writes no account

#### Scenario: Valid resource arrives in fragments

- **WHEN** a valid resource arrives in several chunks totaling at most 64 KiB
- **THEN** the API parses the complete resource normally

#### Scenario: Oversized or malformed declared length is refused safely

- **WHEN** a resource write reaches the SCIM route with an oversized ASCII decimal length or a nondecimal declared length
- **THEN** the route returns SCIM 413 or SCIM 400 respectively without consuming the body or changing users
- **AND** oversized decimal values remain refused even beyond the runtime integer conversion limit

#### Scenario: Understated length cannot bypass the stream budget

- **WHEN** POST, PUT, or PATCH supplies a small Content-Length but streams more than 64 KiB
- **THEN** SCIM returns 413 at the first crossing chunk without consuming the tail
- **AND** the existing user's active state and profile remain unchanged and no new user is written

#### Scenario: Leading zeroes preserve an admissible declared length

- **WHEN** a valid fragmented SCIM body supplies its correct length with leading zeroes
- **THEN** the resource write succeeds even if the header contains more digits than the integer parser accepts
