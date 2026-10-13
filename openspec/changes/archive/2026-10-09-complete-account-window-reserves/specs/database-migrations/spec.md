## ADDED Requirements

### Requirement: Fork account reserves extend the current migration head
Account reserve policy columns and constraints SHALL be added by one forward migration on the current fork warm-up threshold head. Existing positive scalar caps SHALL retain their admission meaning in the shared reserve policy, and zero scalar caps SHALL remain blocked. Existing credentials, account identity, historical migration files and warm-up settings SHALL remain unchanged. Downgrade SHALL remove only reserve fields and constraints while retaining legacy scalar values.

#### Scenario: Existing capped account
- **WHEN** a database with an existing scalar cap is upgraded
- **THEN** a positive cap SHALL become an enabled shared cap and a zero cap SHALL retain its existing deny behavior.

#### Scenario: Fresh account and downgrade
- **WHEN** an uncapped account is upgraded and the reserve revision is subsequently downgraded
- **THEN** the policy SHALL default off and downgrade SHALL preserve credentials and unrelated settings.
