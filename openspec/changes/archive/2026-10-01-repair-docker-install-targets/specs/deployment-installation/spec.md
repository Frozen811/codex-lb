## ADDED Requirements

### Requirement: Container build contexts exclude workstation state

The standard, distroless and development frontend builds MUST exclude local environment credential files, dependency directories, databases, version-control metadata and agent worktrees from their Docker build contexts. Required application, frontend, lockfile and native build inputs MUST remain available. All frontend container builds SHALL use the frontend package's pinned Bun version and frozen dependency lock.

#### Scenario: Build from a workstation checkout

- **WHEN** a checkout contains local dependency trees, nested env files or agent worktrees
- **THEN** those files are excluded from each applicable build context
- **AND** the required source and lockfiles remain available to build the image

### Requirement: Local container installs survive recreation

Standard and distroless source-built images MUST start as non-root users with writable named-volume data storage, provide readiness and dashboard assets, and include an executable native egress helper and a usable certificate trust store. Both images MUST define a shell-independent Docker healthcheck against application readiness. Recreating a container with the same data volume MUST preserve its application data and encryption key.

#### Scenario: New local image and empty volume

- **WHEN** an operator builds a supported local image and starts it with an empty named volume
- **THEN** the non-root application reaches readiness and serves dashboard HTML, JavaScript and CSS
- **AND** its persistent data directory is writable

#### Scenario: Container is recreated

- **WHEN** an operator recreates the container while retaining its named volume
- **THEN** startup reaches readiness with the existing application data and encryption key

### Requirement: Development Compose exposes a working frontend proxy

The root development Compose setup MUST start its backend and frontend without requiring a local env file. The frontend MUST run as a non-root user with writable source and dependency-cache paths, resolve its backend through the Compose service network and proxy health/API requests. Source watch MUST avoid copying workstation dependency trees and env credential files into the running frontend. Development documentation MUST distinguish this setup from the production server-only setup.

#### Scenario: Clean checkout without local configuration

- **WHEN** an operator builds and starts the root Compose backend and frontend from a clean checkout
- **THEN** both are reachable at their documented ports
- **AND** frontend health requests reach the ready backend

### Requirement: Docker CI exercises standard and distroless startup

The Docker CI job SHALL build both standard and distroless local images and verify readiness and bundled dashboard assets in isolated temporary containers before passing. Smoke cleanup MUST run on failures as well as successes and MUST NOT operate on production containers or volumes.

#### Scenario: Distroless builds but cannot start

- **WHEN** the distroless image builds successfully but its runtime cannot reach readiness or serve required assets
- **THEN** the Docker CI job fails and removes its temporary smoke containers
