# Verification: DOC-INSTALL-01/02/03

Date: 2026-10-02. Base HEAD: `f52adb7274c96c0702e19aa02eabd4f1c7556231`; this batch is an uncommitted delta over preserved prior batches. No publication, production restart or user account login was performed.

## Completeness, correctness and coherence

Three requirements (two added, one modified), covering fork source/channel links, named-shell examples and README fallback when public Pages is stale. The existing README scenarios are retained, with one new fallback scenario. Local implementation is verified; external publication and full environment-specific command execution are residual registry work.

| Scenario | Evidence |
| --- | --- |
| Fork installation links | Both README operational links select tracked fork guides; 75 local guide links and 24 anchors checked against rendered HTML; 24 focused tests pass |
| Public description differs | Live About/API, release note and OCI config contain unsupported readiness/verification claims; recorded below and left unresolved |
| Select source in named shell | PowerShell and Bash source-selection portions of COMMUNITY_RELEASE executed against temporary Git stores with spaces; upstream origin unchanged, exact selected fork HEAD obtained |
| Windows launcher example | README mixed Bash/PowerShell block removed; Python guide has separate examples, revision validation and failed-checkout guard; tests and 8 PowerShell parser checks pass |
| Published fork site stale | Direct HTTPS observes 200 for root/getting-started/Python/Docker but upstream repo/edit links and stale Python placeholder; Nix returns 404; README uses tracked source |

No critical local implementation gaps. Design followed: no guessed fork artifact, no upstream attribution rewrite, no application code/configuration/dependency change. Public metadata/site and unexecuted deployment commands are warnings, not locally closed claims.

## Public source/channel inventory

- About still says production-ready / 100% verified / 156 tracked issues and its homepage points to `/releases/tag/v1.25.0`. Proposed replacement description is the neutral English About comment in README; public metadata was not edited.
- Latest release remains `v1.25.0-hardened.3`, published 2026-09-30. Its release body still calls it production-ready/thoroughly verified. Downloaded both assets again and checked API digest against actual bytes:
  - wheel: 3,400,777 bytes, SHA-256 `4af955c73887193d9592d0baf8e638bdec80051f6df5bad8e78e663abd9ad0bf`;
  - sdist: 40,575,939 bytes, SHA-256 `24c965ff57aecead9e15b3a24159857b0c53c9307d7966bc8b4aae87cd3ce744`.
- GHCR `latest` index remains `sha256:ad9aa84b12bce9f6afc63adb3aa86e73f6aafca1814e6f20b486b00f21c60447`; amd64 runtime manifest `sha256:31557c9d04de1fb263b022b0ab1309c4d020675309a69ecac2d19365d35b3087`. Config labels identify source Frozen811, revision `f622c5632013d24ce9236d176113087b387c7990`, version 1.25.1 and the same unsupported 100% description. The second unknown/unknown entry is an attestation.
- PyPI `codex-lb` remains an upstream channel (observed metadata version 1.24.0); bare pip/uvx names were retained only as explanatory warnings, not silently redirected to invented fork packages.
- Nix selects the fork checkout or explicit `github:Frozen811/codex-lb/FULL_COMMIT_SHA`; Helm selects the tracked fork chart. Chart configuration backlink corrected to fork docs. Upstream issue/PR/contributor links and explicitly named upstream documentation overview remain attributed to their owners.
- The URL inventory contains 271 unique related URLs across entry points/docs/chart, including references to issues/specs/tool vendors. This is a local ownership inventory, not a claim that every external reference was fetched or every endpoint passed.

## Executed commands and product checks

- Windows x64 and Ubuntu 24.04 WSL x86_64, selected Python 3.13: isolated venvs outside the repo, paths containing spaces, actual `python -m pip install <historical wheel URL>` followed by installed console-script help/startup. Harness created environments with `uv venv --seed`; it did not claim to execute the separate `python -m venv` line verbatim.
- On each OS: two starts with the same separate data store; readiness 200, root HTML 200, **17 referenced asset URLs** all 200/nonempty. Key SHA-256 unchanged across restart. After stopping the process, installed `codex-lb-db check` gives `migration_policy=ok / schema_drift=none`.
- Both runtimes report `1.25.0-beta.9`, distribution metadata `1.25.1`, module path inside the isolated environment. This rechecks the public wheel; it does not certify later source fixes or real OAuth/upstream routing.
- `uvx --python 3.13 --from <wheel URL> codex-lb --help` and `uv tool install --python 3.13 <wheel URL>` plus installed help completed on both OSes. UV_TOOL_DIR/BIN_DIR were task-specific; persistent fixture tools uninstalled afterwards. Help is package/source-selection evidence, not an additional product startup check.
- COMMUNITY_RELEASE PowerShell/Bash fetch/switch portions selected exact `f52adb7274c96c0702e19aa02eabd4f1c7556231` even with `origin=https://github.com/Soju06/codex-lb.git`; origin was unchanged. Clone/launcher/frontend-build portions were not part of those source-selection probes.
- Docker daemon is unavailable in this turn; no Docker/Helm/Nix/supervisor operations were rerun. Prior runtime records in issues-check §§18–26 remain dated evidence for their exact snapshots, not fresh execution of new examples. Bun user installers, real-account/client login, privileged recovery, cloud/ESO/Ingress/Gateway and native macOS/ARM64 remain unexecuted.
- Initial Windows harness stopped only the console-script wrapper, causing temporary-file cleanup failure; retry owned the fixture process tree and completed both runs/cleanup. The failed harness attempt is not product evidence. Initial WSL inline argument quoting failed before tool execution; a saved script then completed the actual tool checks.

## Static and documentation checks

- 24 focused tests: installation documentation, update guidance, client examples and fork automation scope; PASS. Existing Starlette/AnyIO deprecation warning.
- Ruff check/format and ty on the new test file: PASS.
- MkDocs strict build: PASS; entry-point link/anchor check: 75/24 PASS.
- All **111 shell blocks** inventoried, including two indented list fences missed by the initial extractor: 103 Bash `bash -n` and 8 PowerShell AST parser checks PASS. Parsing alone does not close runtime execution coverage.
- Simplicity: README 218/225, headings 10/10, env 54/60, nav 5/5, tracked root exceptions 0/0; PASS. No new setting/dependency/migration/UI feature.
- OpenSpec 1.11.0 strict change and main-spec validation, followed by verified archive; outcomes recorded in issues-check §27.

Reproduction helpers and full raw command bodies are task-local under `%TEMP%/codex-doc-install-20261002/` (inventory.py, verify_runtime.py, verify_git_windows.py, verify_git_linux.py, verify-tools.sh, bash_parse.py, verify_links.py plus JSON reports). Artifact/public metadata observations contain no credentials. Runtime stores and installed fixture tools were removed; uv download caches are ordinary local caches. The stable per-block inventory in command-inventory.md records shell, content fingerprint and evidence category without making those disposable paths a release artifact.
