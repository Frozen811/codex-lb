## ADDED Requirements

### Requirement: Astra bootstrap metadata preserves captured native capabilities

Before authoritative model refresh, the system MUST advertise `gpt-6-astra` through OpenAI-compatible and native catalogs with captured OpenAI Codex `rust-v0.153.4` metadata: backend context window 272000, maximum context window 872000, client version 0.153.0, websocket preference enabled, default reasoning low, reasoning levels low/medium/high/xhigh/max/ultra, unified_exec shell, code_mode_only tools, multi-agent v2, Responses Lite enabled and a priority Fast tier. Captured plan availability MUST be preserved. Live account catalogs MUST remain authoritative. Known `gpt-6-*` slugs SHALL use websocket-preferred bootstrap fallback before refresh.

#### Scenario: Native and compatible catalogs expose Astra offline
- **WHEN** either model catalog is read before refresh
- **THEN** Astra is present with its captured context and capability metadata

#### Scenario: Live catalog controls Astra
- **WHEN** an authoritative live account catalog omits Astra
- **THEN** bootstrap Astra does not override that omission
