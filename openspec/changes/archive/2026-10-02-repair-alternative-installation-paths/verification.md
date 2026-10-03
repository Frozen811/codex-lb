# Verification: repair-alternative-installation-paths

Verified locally on 2026-10-02 against checkout HEAD f52adb72 plus the working
changes. Application container image:
`sha256:2a359147af629b6a3bf1505e352622d000307478975eeb738225be68f53b6d44`.
Detailed baseline failures, tool versions, command shapes and runtime
observations are recorded in issues-check.md section 22.

| Dimension | Result |
|---|---|
| Completeness | 7/7 tasks; 4 added requirements implemented and synced |
| Correctness | Rendered regressions and disposable product-path checks cover the added scenarios |
| Coherence | Existing install modes, schema gates, upgrade ordering and env contracts retained |

## Requirement mapping

1. **Helm external installs progress before readiness waits**:
   `_helpers.tpl` and migration-job.yaml distinguish existing app credentials
   from chart-created credentials. configmap.yaml selects mounted writable
   scratch; the migration key path is explicit. test_helm_external_secrets.py
   covers ordinary install Jobs, existing-secret hooks, upgrades, schema gate
   and writable scratch. Real empty-DB direct/DB-only/app-secret installs,
   two-pod readiness/ring, wrong-password refusal and upgrade DB/key retention
   passed in kind 0.30.0/Kubernetes 1.35.0. No post-install hook can gate these
   fresh external installs. The smoke script adds a separate empty direct-URL
   database; Bash syntax passed, its new cloud execution remains pending.
2. **Fork Helm and Nix guidance identifies source and artifact channels**:
   chart metadata/default images, Makefile/smoke image names, README variants,
   getting-started, Nix/Kubernetes guides and COMMUNITY_RELEASE select or
   describe the fork source channel. Bundled PostgreSQL is pinned to the
   anonymously tested 18.6 image digest. Actual bundled install/upgrade,
   Helm test, PVC-backed PostgreSQL and dashboard assets passed. No published
   fork artifact was asserted current. No systemd unit is implied installed.
3. **Nix frontend installation does not depend on store hardlinks**:
   flake.nix uses isolated/copyfile/frozen install; .gitattributes pins Nix LF.
   Actual Linux baseline EPERM and copied-Windows CRLF failure both passed
   after repair. Nix 2.35.2 build/flake check, nixfmt and editable dev shell
   passed. The installed package passed help/invalid args, four startups
   outside source, readiness/HTML/JS/CSS, env precedence, DB/key retention,
   migration check and bounded SIGTERM shutdown with no surviving listener.
4. **Remote reverse-proxy instructions preserve application transport**:
   deploy/nginx.conf and the remote guide preserve Host/port, upgrade headers,
   client identity, SSE buffering behavior and bounded timeouts. nginx 1.28
   syntax passed. Actual app readiness/assets, same/cross-site Origin and
   authentication refusal passed. Disposable protocol upstream proved SSE
   delivery before a delayed second event and WebSocket 101/echo with the
   original Host. TLS, OAuth and actual Codex generation are separate.

## Checks

- Focused Helm suites: **120 passed**, no skips.
- Full Ruff check/format and ty: **PASS**.
- All five architecture checkers: **PASS**, limits unchanged.
- Helm lint `--strict`: **PASS**; existing external and bundled Helm tests passed.
- Nix package, flake checks and dev shell: **PASS** on x86_64 Linux.
- MkDocs `--strict`: **PASS**.
- Simplicity budgets: **PASS**, unchanged.
- CI-pinned OpenSpec 1.11.0: **68/68 main specs strict PASS**; change and both
  changed main capabilities strict PASS. Old local 1.3.0 errors were verified
  identical to exact-HEAD baseline before selecting the CI-pinned validator.
- `git diff --check` and Bash smoke syntax: **PASS**.

## Assessment

No critical issues or requirement/spec divergence remain in this scoped
change. Requirements and stable operational context are synced. Ready to
archive. Unexecuted ARM64/Darwin, ESO/provider controllers, ingress/Gateway TLS,
OAuth/Codex generation and new cloud CI/publication are explicitly retained as
audit boundaries; they are not inferred from adjacent successes.
