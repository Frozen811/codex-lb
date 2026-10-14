## Context

Auth imports already accept opaque access-only credentials and explicit identity. Backend optional token fields return null, but frontend export schemas require strings. Codex-format exports omit identity that opaque tokens cannot reconstruct.

## Goals / Non-Goals

Preserve export/import identity and usable export UI for all supported credential shapes. Verify current Business isolation, idle refresh and API-key source contracts. Live provider session longevity, SMS challenges and encrypted portable bundles are outside this batch.

## Decisions

Add explicit email/plan/workspace/seat fields only to Codex auth output. Keep OpenCode's provider-keyed payload unchanged. Use snake_case fields recognized by AuthFile. Frontend accepts null/missing ID and refresh tokens, retains their null JSON values and offers copy controls only for present credentials. Existing stock-client paths accept additive metadata.

## Risks / Trade-offs

Auth exports contain secrets and remain permission/step-up protected with no-cache headers. Metadata is exported only with those credentials. Browser previews truncate present secrets and do not fabricate optional ones. Model-source API keys are separately billed provider credentials; neither them nor a valid PAT bypass provider security controls.

## Verification

Red/green API round-trips for opaque credentials, sibling workspace imports, nullable export schema/component tests, local synthetic upstream source dispatch, existing Guardian lifecycle suites and viewport/browser export checks.
