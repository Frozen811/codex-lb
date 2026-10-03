## Verification: repair-setup-upgrade-health-platforms

2026-10-02, base HEAD f52adb7274c96c0702e19aa02eabd4f1c7556231. Local delta, earlier changes preserved.

## Completeness

Five tasks complete. Four added requirement blocks/seven scenarios synchronized exactly into three owning specs. Stable context promoted; operator guides link owning contracts. No new settings, dependencies, migration, version bump or release.

## Correctness mapping

| Requirement/scenario | Evidence |
|---|---|
| Untrusted projected loopback denied | test_internal_drain_provenance.py actual start/stop/status routes, before fix unauthorized200, after403 + unchanged drain state; raw/empty capture unit test |
| Remote/conflicting caller through loopback proxy denied | Same three routes reject remote and conflicting forwarded hints; captured peer/projection alone cannot grant control |
| Direct local lifecycle remains available | Local trust-enabled reversal test, existing unit deadline/cancellation/status tests; actual container ready503/live200/operator stop; seven Linux signal/DB cases |
| Origin points upstream | COMMUNITY_RELEASE explicit URL/SHA and clean-tree/failure guards; actual isolated checkout retains Soju06 origin but fetches/selects Frozen811 full f52 SHA; examples regressions |
| Recreate and paired restore | Public pinned old1.25.0-beta.9 → final local source1.25.1; actual settings/account/cipher/key retention, current recreate, old image + old pair in new restore volume; both schema checks; task mutable tag doesn't change running image |
| Ready backend lacks dashboard/upstream | Final candidate ready200/root503 corrected pinned/frozen/source-or-package hint; selected-venv helperNone + successful synthetic response; upstream stop gives ready200/generation502 upstream_unavailable; invalid env/DB and busy port fail with named stages |
| Declared architectures without execution | Live public index linux/amd64 + unknown/unknown attestation; guide matrix dates/previous snapshots/unexecuted ARM64/macOS/physical/cloud scope, wheel portability vs native dependencies; regression tests |

## Checks and platform accounting

- Windows:321 passed/7 explicit POSIX skips. Linux:17 passed, including all7 skipped cases and10 repeated provenance tests.328 unique cases completed on appropriate platforms;338 passed executions.
- Full Ruff check/format PASS,1430 files; full ty PASS; all five architecture checks PASS; thresholds unchanged.
- Strict MkDocs PASS; OpenSpec1.11.0 strict change/main68 PASS; exact four-block/seven-scenario sync PASS.
- Simplicity README222/225, headings10/10, env54/60, nav5/5, root0/0, settings98/98 unchanged.
- Regression negative evidence: proper provenance cases6 failed/4 passed before fix. Windows POSIX signal fixtures5 failures and shebang-only discovery2 failures were fixture/platform defects, corrected without weakening shutdown/protocol assertions. Linux startup polling corrected to30s monotonic bound; shutdown deadlines unchanged.

## Runtime identities and limitations

Public old amd64 manifest31557c9d04de1fb263b022b0ab1309c4d020675309a69ecac2d19365d35b3087, image21776e26…, OCI revisionf622c563…, metadata1.25.1/runtime1.25.0-beta.9. Final candidatef0901e61dc90376a35b0a79604bc2f25e2791dc36dded11607503e85816c7229 copies current app/config/scripts over dependency image2a359147…, runtime1.25.1. This is not a new public release/full native/frontend rebuild claim.

Linux frozen test runner used initial source snapshot7c485240… and final mounted tests; final asset-hint edit is independently validated in Windows route/final runtime. Lifecycle/provenance module byte hashes match final candidate. Actual idle SIGTERM exits0 in1.528–2.281s with clean shutdown/OOM false; signal fixtures separately preserve POSIX return/deadline/terminal assertions. Native Windows console/physical network/ARM64/macOS and every downgrade pair are unexecuted.

Earlier harness assumptions (reset name/schema, drain envelope detail vs middleware error, system interpreter vs venv, raw-insert cache and same-store port collision) were corrected before PASS and are not application findings. Final probes use real import/product routes, explicit selected interpreter, isolated stores and exact observed errors.

Public OCI description still carries historical100% claims; immutable artifact was not relabelled or republished. No production container/store, user config or remote refs were changed. Source/control and document contract implementation has no critical unresolved issue; ready for archive with these audit limits retained. Local reports: Temp/codex-lifecycle-20261002/report.json, failure-report.json/public-index.json. No commit/push/CI dispatch/publication occurred.
