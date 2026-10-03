## MODIFIED Requirements

### Requirement: Source-routed Responses tools are capability-filtered

When forwarding a Responses request to an OpenAI-compatible source, the proxy MUST forward `function` tools unchanged and MUST drop non-`function` tools the
source model has not declared support for. A source model declares support in
its `raw_metadata_json`: `"supports_search_tool": true` keeps web-search tools
(`web_search`, including the `web_search_preview` alias), a nonblank string
`"multi_agent_version"` keeps `namespace` tools, and
`"experimental_supported_tools"` MAY list additional supported tool types.
The version declaration MUST accept future nonblank strings and MUST NOT opt
in for missing, blank or non-string values. Declared namespace definitions,
including nested function schemas, MUST be forwarded unchanged.
When only some tools are dropped, a `tool_choice` that references a dropped
tool MUST be removed so the forwarded payload never names a tool that is not
present. Bare `function`-typed choices MUST be preserved; a function choice
with a namespace MUST be removed when namespace tools were dropped. The same
rule MUST prune entries inside `allowed_tools`, preserving the remaining
choice fields and removing `tool_choice` if no entries remain. When all tools
are dropped, `tools`, `tool_choice`, and `parallel_tool_calls` MUST be removed
together. Whenever a hosted tool is dropped, `include` entries specific to
that tool type (for example `web_search_call.*` for `web_search`,
`file_search_call.*` for `file_search`, `code_interpreter_call.*` for
`code_interpreter`, and `computer_call_output.*` for computer-use tools) MUST
be pruned from the forwarded payload; non-tool-specific entries (for example
`reasoning.encrypted_content`) MUST be kept, and the `include` field MUST be
removed entirely when pruning empties it. This filtering MUST apply on every
source-routed Responses surface (`/backend-api/codex/responses` and
`/v1/responses`), including their trailing-slash forms.

#### Scenario: Codex-only tools are dropped for a plain source model

- **GIVEN** a Responses-capable source model with no tool capability opt-ins
- **WHEN** a Responses request with a `function` tool, a `namespace` tool, and a `web_search` tool is forwarded to it
- **THEN** the forwarded payload contains only the `function` tool

#### Scenario: Search-capable source models keep web-search tools

- **GIVEN** a source model whose `raw_metadata_json` sets `"supports_search_tool": true`
- **WHEN** a Responses request with a `function` tool and a `web_search` tool is forwarded to it
- **THEN** the forwarded payload contains both tools
- **AND** a `tool_choice` of `{"type": "web_search"}` is preserved

#### Scenario: tool_choice referencing a dropped tool is removed

- **GIVEN** a source model with no tool capability opt-ins
- **WHEN** a Responses request with a `function` tool, a `web_search` tool, and `tool_choice` `{"type": "web_search"}` is forwarded to it
- **THEN** the forwarded payload contains only the `function` tool
- **AND** the forwarded payload contains no `tool_choice` key

#### Scenario: include entries of a dropped tool are pruned

- **GIVEN** a source model with no tool capability opt-ins
- **WHEN** a Responses request with a `function` tool, a `web_search` tool, and `include` `["web_search_call.action.sources", "reasoning.encrypted_content"]` is forwarded to it
- **THEN** the forwarded payload contains only the `function` tool
- **AND** the forwarded payload's `include` contains only `"reasoning.encrypted_content"`

#### Scenario: Dropping every tool removes the tool-only fields

- **GIVEN** a source model with no tool capability opt-ins
- **WHEN** a Responses request whose tools are all unsupported is forwarded to it
- **THEN** the forwarded payload contains no `tools`, `tool_choice`, or `parallel_tool_calls` keys

#### Scenario: Future collaboration versions preserve complete namespaces

- **WHEN** a source declares a nonblank collaboration version and receives a namespace with nested function schemas and a matching forced or allowed choice
- **THEN** the upstream receives that namespace and matching choice unchanged
- **AND** unsupported hosted tools and their include entries remain pruned

#### Scenario: Missing namespace capability removes namespaced function choices

- **WHEN** a source without namespace support receives a namespaced function choice or an allowed choice mixing namespaced and bare functions
- **THEN** dropped namespace functions are absent from the forwarded choice
- **AND** bare function choices and unrelated allowed-choice fields remain intact

#### Scenario: Explicit namespace opt-in works without a version declaration

- **WHEN** a source explicitly lists `namespace` in `experimental_supported_tools` without a valid collaboration version
- **THEN** complete namespace tools and matching choices are preserved
