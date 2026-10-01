## ADDED Requirements

### Requirement: Server-only Compose installs the selected source

The server-only Compose setup MUST build the selected checkout by default under a local image name, even when an older application image is cached. It MUST NOT tag a source build as a published registry release. Without a database override it SHALL use persistent SQLite; an explicit external PostgreSQL URL SHALL select that backend. Documented PostgreSQL certificate-verification configuration MUST apply to migrations and runtime SQL. Invalid credentials, an unresolved database hostname, a mismatched TLS hostname or an untrusted certificate MUST NOT yield successful application readiness.

#### Scenario: Historical public image is cached

- **WHEN** an operator runs the documented server-only Compose startup from a checkout
- **THEN** Compose builds and runs that checkout rather than the cached historical release
- **AND** the resulting image uses a local name

#### Scenario: External PostgreSQL is configured

- **WHEN** the server-only application receives a reachable valid PostgreSQL URL
- **THEN** migrations and application settings use that database
- **AND** recreation retains the database state and encryption key

#### Scenario: Verified TLS database installation

- **WHEN** an operator configures PostgreSQL with certificate and hostname verification and a mounted trusted CA
- **THEN** migrations and runtime SQL connect over verified TLS
- **AND** an untrusted certificate or mismatched hostname prevents readiness

### Requirement: Database profiles require explicit backend selection

Development database profiles SHALL start optional PostgreSQL or MySQL services without implicitly changing the application backend. Installation documentation MUST provide explicit application URL selection using service DNS for containers and loopback for host clients, startup readiness ordering, and application recreation after configuration changes. Database service healthchecks MUST execute authenticated SQL against the configured database as the application user and MUST fail when credentials or the database are invalid.

#### Scenario: A database profile is enabled without a URL

- **WHEN** an operator starts an optional database profile without setting the application database URL
- **THEN** the application continues to use its default SQLite backend
- **AND** the documentation explains how to select the profile database explicitly

#### Scenario: Server accepts connections but rejects the user

- **WHEN** the database is reachable but the configured application credentials or database are invalid
- **THEN** its health probe fails

### Requirement: Fork Docker instructions identify the selected artifact

Fork Docker instructions MUST select a fork artifact or fork checkout explicitly, distinguish historical public images from newer source fixes, and provide an immutable digest for historical image reproduction. Runtime and distribution versions, source revision and supported runtime platforms MUST be recorded independently when auditing public images. An installation smoke MUST NOT be treated as proof that routing fixes or a new release were published.

#### Scenario: Public alias predates source fixes

- **WHEN** the public alias resolves to a revision older than audited checkout fixes
- **THEN** fork installation instructions disclose that boundary and provide the source-build path
- **AND** they do not promise the newer fixes in the historical image
