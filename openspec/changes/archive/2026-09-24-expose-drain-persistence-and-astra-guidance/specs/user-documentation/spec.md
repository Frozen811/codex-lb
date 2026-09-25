## ADDED Requirements

### Requirement: Client examples recommend current frontier model lineup

Client setup documentation across the quickstart README and the documentation site SHALL recommend `gpt-6-astra` for complex reasoning and coding tasks. Model-specific context-window guides (such as the 872k context-window opt-in) SHALL remain specific to the GPT-5.6 family. Inert client configuration profiles and multi-client configuration examples SHALL demonstrate current frontier defaults without modifying catalog, pricing, or protocol contracts.

#### Scenario: Client setup examples use GPT-6 Astra

- **WHEN** an operator inspects the quickstart client setup section in `README.md`, `README.zh-CN.md`, or `docs/client-setup.md`
- **THEN** the primary model configuration snippet uses `gpt-6-astra` with `model_reasoning_effort = "xhigh"`

#### Scenario: GPT-5.6 context-window opt-in instructions remain family-specific

- **WHEN** an operator reviews large context-window instructions
- **THEN** the 872k context-window opt-in instructions explicitly apply to the `gpt-5.6-*` family
