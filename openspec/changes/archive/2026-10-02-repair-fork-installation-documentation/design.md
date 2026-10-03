## Context

See proposal.md. The shared checkout contains earlier verified, uncommitted installation batches. Fork Pages is configured locally but its public deployment is not assumed. Release wheel and image identity differ from current source.

## Goals / Non-Goals

Goals: repair actionable reader paths and shell examples, preserve actual upstream attribution, and provide a command/artifact evidence ledger.

Non-goals: publishing releases, changing GitHub metadata, deploying Pages, changing user installations, or rerunning every prior cloud/platform experiment.

## Decisions

- Link README guidance to tracked docs source until public Pages is confirmed; do not replace it with a guessed hosted URL.
- Preserve historical artifact URLs and label their metadata/runtime/source identity. Record immutable/public claims as outstanding rather than silently rewriting history.
- Use quoted revision variables with validation rather than angle-bracket arguments. Separate platform launchers and document substitutions.
- Add focused documentation contract tests plus independent shell/runtime checks in task-specific temporary stores. Keep command evidence in verification/context; no new application settings or runtime features.

## Risks / Trade-offs

- Source links render on GitHub rather than a hosted site until publication; strict MkDocs checks and anchor checks cover the local site.
- Some commands require real accounts/cloud/privileged host changes; inventory them as unexecuted rather than claim parser checks prove them.
- Historical artifact metadata remains inconsistent; retain exact digests and date the evidence.
