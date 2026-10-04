# Release publishing context

## Repository boundaries

The upstream release-please/beta/artifact workflows are intentionally skipped in this fork; they are not the fork release channel. Their failure cleanup has the same `Soju06/codex-lb` boundary as their publisher. A cancelled upstream job in `Frozen811/codex-lb` cannot draft a fork release. Fork withdrawal remains owned by `docker-publish.yml`, whose exact-source gate and partial-publication limits still apply.

For example, dispatching upstream `release.yml` in the fork does not publish to upstream PyPI and does not invoke upstream cleanup on a fork tag. Local YAML tests verify these conditions; actual cloud runs remain evidence for their specific source SHA, not an inferred consequence of those tests.

Normative contracts: [spec.md](spec.md).

## Independent fork publisher

`Frozen811/codex-lb` uses `.github/workflows/docker-publish.yml` for GitHub wheel/sdist and GHCR linux/amd64 images. The canonical upstream Release/Release Please/beta preparation workflows are scoped to `Soju06/codex-lb`; enabling them indiscriminately in the fork would mix upstream package ownership and fork publishing. This publisher adds source/artifact gates; it does not waive review, version preparation or the existing stable-promotion soak requirements. Release timing is an operator decision after these prerequisites are met.

Use supported tags such as `v1.25.2-beta.1`; the package spelling is `1.25.2b1`, the runtime and OCI version are `1.25.2-beta.1`. Historic `v1.25.0-hardened.N` tags are preserved as history and refused by the new publisher. Repairing managed fields to the existing `1.25.1` project version does not publish `v1.25.1` or prove that its existing public image is current.

The release tag must point to current main. The initial gate checks GitHub's latest main-push runs for CI, Release guards, Simplicity budgets and Windows startup regression at that SHA, plus the CI Required job on the current run attempt. Filtering on successful runs alone would let an older green run hide a newer failure, so the gate loads all outcomes and checks the newest run. Missing data, API errors and bounded-pagination overflow fail closed. A manual Windows run helps diagnose the published baseline but does not replace automatic main-push evidence. See [GitHub workflow runs API](https://docs.github.com/en/rest/actions/workflow-runs) for the source fields and filtering contract.

After isolated package and loaded-image smoke tests, the same gate checks the tag/main/CI again. If main has advanced or a rerun is pending, prepare a new coherent candidate instead of publishing an old release. Registry login and uploads occur after this recheck. The same locally loaded image is tagged and pushed; there is no second build with potentially changed dependencies.

## Package contents and installation checks

Source distributions use Hatch `only-include` to select explicit root-relative build inputs. Ordinary unanchored include patterns can also select identically named files below local agent worktrees; see [Hatch explicit selection](https://hatch.pypa.io/latest/config/build/#explicit-selection). Wheel and sdist validation checks metadata, all application Python files, bundled frontend bytes and sdist managed files. Workspace/environment entries are rejected. Smoke additionally compares installed application hashes to checkout, because a correct archive does not guarantee a correct cached installation.

Package smoke installs wheel and sdist into separate clean environments and launches the installed CLI outside the checkout with a temporary SQLite database, data directory and encryption-key path. It checks distribution/runtime versions, readiness, dashboard HTML and referenced JS/CSS. Docker smoke uses tmpfs, a random loopback port and a temporary container; existing production data and accounts are not used. Windows cleanup terminates the spawned launcher/interpreter tree so inherited log handles cannot leave an orphan server.

These tests establish the packaging/startup path. They do not establish OAuth, real Codex generation, Pause/quota display, production PostgreSQL/MySQL, remote networking, ARM64 or every installation instruction. The installation audit matrix in root issues-check.md tracks those separately.

## Publication and failures

Publication is serialized across tags. Existing release assets or exact image tags block retries; investigate a partial upload rather than silently clobbering it. Packages, SHA256SUMS and source/CI JSON provenance upload first, then exact Docker tags, then stable aliases. Beta publishes only its exact tags and remains a GitHub prerelease. A newer valid stable GitHub release prevents alias regression. Source revision/version labels and provenance identify the candidate; local uncommitted audit images use an explicitly local revision marker.

The publisher requires an existing GitHub release. A manual invocation requires its explicit supported tag and main workflow ref; no branch-only build or implicit `latest` publication is accepted. On failure/cancellation the associated release is made draft. This cleanup applies even when the initial source gate failed. Do not manually dispatch this publisher against an existing successful release: existing assets/tags are refused and failure cleanup will withdraw the associated metadata.

GitHub and GHCR are separate systems: partially uploaded assets, exact tags, or partially advanced aliases can remain after a registry/network failure. Making the release draft is not an atomic rollback. Inspect digests and release assets before recovery, preserve failure evidence and use a new candidate where required. The final source read also cannot lock main against changes immediately afterwards; serialization and rechecking narrow the race but do not make CI immutable.

Example: a public `v1.25.2-beta.1` tag identifies SHA A, but A's CI is failed while SHA B's CI is green. Publication refuses A, performs no new registry push or package upload, and drafts that release. Passing local tests on A is insufficient to bypass this refusal.


## Fork CI repair (2026-10-04)

The required CI contract in [spec.md](spec.md) retains complete integration-core coverage, per-test watchdogs and aggregate gates. The former 20-minute shard budget cancelled a continuously progressing job at roughly 75% on run 37209560169. Its bounded budget is now 40 minutes; no test is removed and a failing/cancelled shard still blocks both aggregates.

The associated repairs align test fixtures with existing product contracts: explicit slash aliases remain capability classified; unsafe-to-migrate authored WebSocket errors retain their status/code/message; direct and routed native Responses bodies are decoded as zstd before semantic assertions. Strict ty includes all tests; concrete table casts, mock typing and positive payload narrowing replace invalid fixture assumptions.

For example, a selected owner's authored usage_limit_reached error remains that same error on the original socket when complete replay cannot be proved. It is not replaced by an admission-stage owner-unavailable envelope. The no-second-account and no-replay assertions remain mandatory.

Historical Windows installed-wheel smoke failed on cleanup of an open log handle at 282ce1470. The same current smoke implementation passed subsequent 8f713d322 and 94c9a8c24 runs; this is historical flake evidence rather than a reason to skip Windows verification. The repair is considered cloud-verified only after all required jobs for its exact published SHA complete successfully. Actual runtime/provider/deployment and unrelated SQLite/native aggregate residuals remain separate.
