## MODIFIED Requirements

### Requirement: Child HTTP bridge idle retention follows the child affinity bound

HTTP bridge sessions for requests carrying recognized subagent lineage SHALL retain an idle socket and stream lease for at most the effective child affinity TTL, capped at 300 seconds. A shorter configured retention or affinity TTL MUST remain shorter. Hard turn-state or process affinity MUST NOT bypass this idle cap. The cap MUST apply to both creation and reuse, MUST NOT interrupt an active request, and MUST NOT weaken stored-object account ownership. Requests without recognized child lineage SHALL keep their ordinary retention policy, including Codex lifetime promotion when reusing a turn-state alias.

#### Scenario: Child thread caps long bridge retention
- **WHEN** a child thread would otherwise retain an idle bridge for 1800 seconds
- **THEN** its effective idle retention is at most 300 seconds

#### Scenario: Shorter policy remains shorter
- **WHEN** the configured child affinity or bridge retention is below 300 seconds
- **THEN** the effective bridge idle retention does not exceed the shorter bound

#### Scenario: Reuse adopts the child bound
- **WHEN** a child request reuses a compatible bridge with a longer idle lifetime
- **THEN** the retained bridge idle lifetime is shortened to the child bound

#### Scenario: Parent retention remains ordinary
- **WHEN** a request has no recognized subagent lineage
- **THEN** ordinary Codex and prompt-cache bridge retention remains applicable

#### Scenario: Parent alias reuse retains promoted Codex lifetime
- **WHEN** a parent request reuses a prompt-cache bridge through its turn-state alias
- **AND** the bridge has adopted the configured Codex idle lifetime
- **THEN** reuse does not shorten that lifetime to the original prompt-cache retention
