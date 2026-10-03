# Context: user-documentation

## Fork identity and scoped evidence

The fork site's repository/edit links and owning-spec links target `Frozen811/codex-lb`. Main builds obtain the configured base URL from `actions/configure-pages` with read-only Pages access and enablement disabled; PR/local builds default to `https://frozen811.github.io/codex-lb/`. This avoids hardcoding an unverified custom domain in source. Account-level redirects and HTTPS settings remain external deployment state; rendering the site does not repair or certify those settings.

The historical `ISSUES.md` contains imported source-author claims. Its snapshot count uses distinct `(URL type, number)` pairs, including links in descriptions: 120 issues, 128 PRs and 49 discussions on 2026-10-02. These counts do not measure current GitHub state or verified fixes. Category counters and resolved markers remain attributed historical data; independent verification lives in `issues-check.md` and records source SHA, product-path evidence and limits.

For example, a later passing checkout smoke does not prove that the historical hardened.3 wheel/image contains the same fixes. Entry-point and community summaries point readers to scoped evidence rather than presenting such a source check as aggregate release certification.

Normative requirements live in [`spec.md`](./spec.md). This document carries the
rationale and operational notes for the docs site and entry-point documents.

## Purpose

Restore the founding "1-click setup" promise of the entry-point documents. The
README had grown to 653 lines and `.env.example` to 115 lines / ~45 active
values; both buried the quickstart. Detailed material now has a real home (the
mkdocs-material site with the fork's configured Pages base URL) so the
README and sample env stay slim without losing content.

## Decisions

- **mkdocs-material, docs at `docs/` root.** `docs_dir: docs` means the
  existing `docs/screenshots/` images ship into the site unchanged and README
  image paths keep working on GitHub. Pages live directly under `docs/` (not
  `docs/content/`) so the site homepage is
  configured Pages base URL itself (the local default is `https://frozen811.github.io/codex-lb/`).
- **Strict build as the docs gate.** The `validation:` block in `mkdocs.yml`
  plus `--strict` turns broken internal links, missing anchors, and
  nav-orphaned pages into CI failures. Corollary: any stray `.md` dropped into
  `docs/` breaks the build — keep scratch notes out.
- **`--only-group docs`** keeps the docs build from installing the app
  dependency tree; `uv run --no-sync` stops the run step from re-syncing to the
  dev defaults. The `docs` group is not in uv default-groups, so `make test`
  and friends do not pull mkdocs.
- **Deploy only from main, never cancel in-flight.** PR runs stop after the
  strict build; push runs upload the Pages artifact and deploy via
  `actions/deploy-pages` (`build_type=workflow`).
- **README keeps exactly one client path inline** (Codex CLI `config.toml`) —
  the most common client — with a table linking the rest. No badges; a single
  prominent documentation link line instead (locked decision).
- **all-contributors block stays in README.md** between its markers; the
  generated table is bot-managed and is not hand-written complexity.
- **`.env.example` drift values were deleted, not corrected.** The sample is
  all-commented so it can never drift into behavior changes again. The
  commented `# CODEX_LB_LEADER_ELECTION_ENABLED=false` escape hatch is pinned
  by `tests/unit/test_helm_replica_artifacts.py`.
- **OpenSpec stays normative.** Docs pages carry footer links to their
  governing capability; they render behavior, they do not define it.
- **Community companions stay separate.** Small operator tools that consume an
  existing API can be maintained in independent repositories and linked from
  the docs once they are public and tested. A listing keeps the tool
  discoverable without adding its runtime, CI, release process, or support
  surface to codex-lb. The first listings cover the independently published
  [Codex LB Status Bar](https://github.com/sm1ee/codex-lb-statusbar) and the
  read-only
  [codex-lb SwiftBar](https://github.com/joschi655/codex-lb-swiftbar),
  following the maintainer direction in
  [PR #1233](https://github.com/Soju06/codex-lb/pull/1233#issuecomment-4988227303).
  Listings also carry least-privilege guidance: guest access for monitoring
  where the companion supports it, and admin access only for control features;
  each companion remains responsible for documenting its current auth modes.
  [Codex LB for Omarchy](https://github.com/janaki-sasidhar/omarchy-codex-lb) extends this pattern to Linux with a native Omarchy Quattro plugin using the same dashboard API. Its monitoring-only scope includes guest access, account quota and usage summaries, reset timing, and optional desktop notifications.
  [Codex-LB Rates](https://github.com/uniskela/codex-lb-rates) extends this pattern to Home Assistant with pool and per-account remaining-% sensors via the same dashboard API, supporting guest and admin login for monitoring.
  Placement: the listing renders as an appendix-level section at the end of
  `docs/index.md` (below core usage and screenshots) and is kept
  self-contained so it can move to a dedicated page once the list grows; a
  short mirror lives in the README under the Documentation section (a
  sub-heading, not a new top-level README section, per the simplicity
  budgets).
- **zh-CN README gets a canonical-English banner** rather than a parallel diet;
  full i18n (mkdocs-static-i18n) is a deferred follow-up.

## Constraints / failure modes

- GitHub Pages must be enabled out-of-band by an admin
  (`gh api -X POST repos/Soju06/codex-lb/pages -f build_type=workflow`) before
  the first `main` deploy; until then the deploy job fails while the build
  check still protects PRs.
- `uv.lock` must be regenerated whenever the `docs` group changes — CI and the
  Makefile use `--frozen` unconditionally.
- The README is the PyPI long description (`pyproject.toml`
  `readme = "README.md"`); relative screenshot paths already did not render on
  PyPI, so the diet does not regress it.

## Example

A user asks "how do I upgrade the compose Postgres volume?" — the README
Configuration section links the docs Database page;
The fork site's `database/` page carries the verbatim 16→18
runbook and links the `database-backends` / `database-migrations` specs for the
normative behavior.

## Codex setup authentication and evidence (SETUP-07, 2026-10-02)

Purpose: distinguish dashboard bootstrap/password, Codex LB API keys and upstream
ChatGPT credentials. CLI API-key examples explicitly select env_key with
requires_openai_auth=false; ChatGPT/Desktop and advanced restricted-provider
examples retain their separate eligibility contract. Official auth guidance
currently says OpenAI-auth mode ignores env_key, but actual isolated Codex
0.159.3 completed generation under both flag values using the provider key. This
observed version behavior is recorded rather than generalized to future clients.

Generation base /backend-api/codex, catalog /backend-api/codex/models and usage
backend base /backend-api must move together. The downloadable TOML's missing
usage suffix and guide conflict marker were corrected. For example, an API-key
caller of /api/codex/usage gets its unfiltered credit-limit windows; a matching
ChatGPT identity gets eligible pooled quota. A null API-key rate_limit without
credit limits is not evidence of missing pool accounts. Token-count limits are
not converted into Codex credit windows.

Actual Codex 0.159.3 ran with isolated CODEX_HOME and ephemeral credential storage,
strict config, tool-free synthetic responses, and no user auth.json. Server and
fixture records confirmed client HTTP/WS, selected account, quota windows and
new-request Pause refusal. Already-dispatched work may finish; neither Pause nor
changing the provider key certifies cloud conversation synchronization. Real
OpenAI login/entitlement/accounting and Desktop sync remain outside the rehearsal.
Official sources: https://learn.chatgpt.com/docs/auth#alternative-model-providers
and https://learn.chatgpt.com/docs/config-file/config-reference. Detailed evidence
is in issues-check.md §25 and repair-setup-transport-auth-client/verification.md.

## Health and platform evidence (SETUP-09/10, 2026-10-02)

Purpose: prevent infrastructure signals and build declarations from becoming
product/platform certification. Startup/live/ready, dashboard assets, helper
discovery and authenticated upstream requests prove different contracts.
For example, missing assets produced ready200/dashboard503, and killing only
the synthetic upstream produced ready200/generation502 upstream_unavailable.
Python transport completed a synthetic request with helper discoveryNone.

The troubleshooting guide names error stages and safe recovery without dropping
auth/certificate checks. A direct-local drain returned the actual middleware
503 service_unavailable envelope while live stayed200. Occupied HTTP port
refused with nonzero exit, invalid env named its field, and an unavailable DB
failed migration/startup. A supervisor kill is not evidence of graceful drain.

The Python installation guide consolidates dated Windows x64, Linux/amd64
Docker, Ubuntu WSL, local kind and Nix x86_64 evidence, with earlier snapshots
clearly distinguished from current runs. ARM64/native macOS/physical network
and provider paths remain unexecuted. The public OCI index's unknown/unknown
descriptor is explicitly an attestation; declared Nix systems and py3-none-any
metadata are not runtime support proof.

Native-helper discovery test fixtures now use a PATHEXT launcher on Windows;
shebang-only discovery fixtures had failed there while direct protocol tests
passed. POSIX process tests declare their scope and also executed on Linux;
their Windows skips are not counted as completed signal tests. No production
platform setting, migration or dependency surface was added. Detailed source,
artifact/runtime identities, failure outcomes and verification are in
issues-check§26 and repair-setup-upgrade-health-platforms/verification.md.

## Fork installation entry points (DOC-INSTALL-01/02/03, 2026-10-02)

Purpose: help readers choose fork source and historical artifacts without
borrowing current-source verification for a public release. README, Chinese
README, COMMUNITY_RELEASE and docs home use the fork's tracked English guides.
Upstream issues, contributors and the explicitly named upstream overview retain
their attribution. Each behavior page still links its owning OpenSpec capability.

Decision: prefer tracked source links while published Pages is stale. Direct
HTTPS found the fork Pages site reachable but with upstream edit/repository
links, an old source-sha placeholder and no Nix page. About, release notes and
OCI descriptions still contain unsupported readiness/verification claims;
their public correction remains separate work. Parser failures in PowerShell's
web client were not treated as proof that the site was down.

Constraints: Bash and PowerShell use separate launch examples; placeholders
must be substituted without becoming redirections. Quoted revision variables
validate a full SHA before source selection. Helm/SSO examples use rendered
StatefulSet names, not the removed Deployment. Standalone Bash configuration
examples export values to child processes. Bun installers and privileged
host/cluster recovery were not run against the user's environment.

Example: a historical fork wheel installed through pip on Windows and Linux
reports metadata 1.25.1 but runtime 1.25.0-beta.9. Both isolated stores served
readiness/dashboard/assets and survived restart with the same key; this says
nothing about later uncommitted source fixes. Explicit fork fetch in both
shells selected the reviewed SHA even with an upstream origin.

Failure modes include mixed-shell launchers, angle-bracket arguments, an
unexported environment assignment, stale hosted docs and cached historical
packages. The command ledger accounts for 111 shell blocks (103 Bash, 8
PowerShell); parsing is labeled separately from pip product runs, tool help,
Git selection and earlier dated infrastructure evidence. Full per-command
execution and public metadata/site publication remain open in issues-check§27.
The contract is in [spec.md](spec.md); the bounded local implementation and
evidence are archived as repair-fork-installation-documentation.
