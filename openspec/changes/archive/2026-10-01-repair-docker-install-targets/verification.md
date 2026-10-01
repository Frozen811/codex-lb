# Verification: repair-docker-install-targets

## Completeness

10/10 local implementation/evidence tasks complete for INSTALL-02/04/15. Four deployment-installation requirements and context are synchronized. No public release or cloud execution is claimed.

## Correctness

- Real BuildKit COPY/local export reproduced forbidden inert markers in baseline contexts: root 7 and frontend 5. Fixed policies retained zero forbidden markers and all required sample source/lock inputs (8 root, 4 frontend). No real secrets used.
- Standard and distroless builds passed for linux/amd64. Each image started twice with its own named volume, served readiness/HTML/JS/CSS, ran as non-root (1000/65532), had 150 trusted CAs and an executable native helper. Both Docker healthchecks became healthy. Persisted dashboard setting and encryption-key hash survived recreate. Every graceful stop exited zero without OOM.
- Clean source snapshots omitted env, workstation dependencies and user data. Development backend/frontend builds, Vite HTML/transformed TSX, backend/proxy readiness, watch sync and exclusion of env/dependencies, backend restart and force-recreate passed. The final full repeat also proved non-root frontend UID 1000 and permission compatibility.
- 20 focused unit tests passed for Docker networking, PostgreSQL/MySQL Compose contracts and launcher contracts. These do not claim live database installs.
- actionlint 1.7.12 passed on CI; smoke shell syntax passed with LF bytes. Architecture, simplicity and diff whitespace checks passed. Strict delta and 68 main specs passed.
- Own audit containers, volumes, network and Compose watch process trees were removed; final label/name/process queries were empty. Build images and inert audit snapshots/logs remain for repeatability.

## Coherence

No version bump, new operator setting or schema migration. Existing standard-image Trivy gates retained; the Docker job gains distroless build and isolated readiness/assets/native/CA smoke. Frontend pinning matches packageManager; root/frontend ignores and watch policy are consistent. Rendered Docker docs link to the fork capability and explain source-built images, dev/server-only modes, volume ownership, update limits and shell-free diagnostics. README/CHANGELOG unchanged.

## Limitations

Docker Desktop Linux engine 29.8.1/Compose 5.5.1 on Windows, Linux/amd64 only. ARM64, Windows container images, real upstream account traffic, OAuth, public GHCR/package artifacts, production external DB and network switching are separate audit items. Complete current CVE scanning of both local images was not run; installation smoke is not a security certification. New CI source is unpublished and cloud execution pending.

Initial audit-helper failures are documented: random-port rebinding around asynchronous watch restart, transient Docker exec while stopped, and an orphan Windows watch child when only its launcher was terminated. The corrected stand observes a new StartedAt, retries transient exec/re-resolves the port and terminates its owned process tree; full final runs pass. These failures do not establish application defects.

Evidence scripts/fixtures/build/watch logs: C:\Users\ext\AppData\Local\Temp\codex-lb-install-batch4-20261001. Main source remains 7ec39f82709ee1ca4c00489a8d5fc301d49320ed; actual newest main-push CI 36761400788 remains failed. No source push, release, registry publication or deployment. No local completeness/correctness/coherence blockers remain.
