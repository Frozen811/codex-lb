## Context

See proposal.md. CI selection currently ignores renamed source filenames and trusts PR files pagination without comparing the reported count. Nix source inputs, including the Hatch hook/helpers under scripts/, extend beyond its existing filter. README and community notes claim incompatible verified totals; the linked source inventory contains 120 distinct issues, 128 PRs and 49 discussions. The published fork site still links edits to upstream.

## Goals / Non-Goals

Goals: conservative CI selection, attributed historical evidence, correct fork site identity and isolated publisher authority.

Non-goals: independently resolving all 297 linked records, changing application behavior, enabling upstream publishing in the fork, changing Pages account settings or publishing artifacts.

## Decisions

- Reuse the CI workflow path as the existing all-area fallback; avoid a second filter/output contract. Validate API record count before adding rename aliases; reject malformed/cyclic evidence conservatively.
- Add packaging hooks and real Nix inputs to their existing filters. Select the full suite for workflow or selector changes rather than maintaining fragile per-workflow routing.
- Keep imported issue details and source-author markers as historical claims, with a corrected summary. Do not replace them with newly invented verified counts.
- Resolve Pages base URL through the pinned configure-pages action for main builds, using build-job Pages read permission only. MkDocs uses that output with a fork default for PR/local builds. Owning-spec links and the settings-reference generator target the fork; upstream issue/author references remain upstream. Account-level custom domain/HTTPS redirects remain an external limitation.
- Scope upstream cleanup using the same repository condition as its publisher. Independent fork publication remains separate.

## Risks / Trade-offs

- Conservative filters run more CI for shared inputs; fewer omitted validations justify the added work.
- Docs/site metadata changes affect the next deployed site; a local build is not cloud deployment evidence.
- Original issue bodies include third-party assertions. The global provenance notice and independent registry remain necessary until per-entry verification completes.

## Migration Plan

Apply local changes and focused regressions, strict docs/spec checks, then sync and archive after verification. No release, push or external settings mutation is part of this change. Reverting these source edits is sufficient to roll back.
