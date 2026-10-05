Five initially unverified records: UP-PR-2564, UP-ISSUE-2511, UP-PR-2517, UP-PR-2519, UP-ISSUE-2302. Base HEAD f987d08e69978ee6452c4e5997b11e80a81ba5f2; initial dirty files are preserved under a temporary SHA256 manifest. GitHub source bodies and PR heads were read freshly on 2026-10-05.

Example: selecting a.json, b.json, c.json sends a.json first. If b.json is rejected, c.json is untouched and retry sends b.json followed by c.json. The UI exposes the remaining filenames without inspecting or displaying token contents.

The existing Prolite route tests cover aliases and negative identity controls. Telemetry verification adds a persisted-row aggregate. Bridge verification covers LF, CRLF and CR pretty-printed JSON with prompt upstream refusal. Accessibility verification exercises names and keyboard behavior in both forms. Local evidence does not substitute for GitHub CI; publication and its exact-head matrix are recorded separately after local completion.
