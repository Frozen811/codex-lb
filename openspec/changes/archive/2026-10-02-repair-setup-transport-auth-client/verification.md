## Verification: repair-setup-transport-auth-client

2026-10-02; base HEAD f52adb7274c96c0702e19aa02eabd4f1c7556231. Local uncommitted change over preserved earlier batches.

## Completeness

Six implementation/verification tasks complete. Four requirement blocks (one modified, three added), eight scenarios synchronized exactly with four main capabilities. User-facing guides link the owning specs. No new configuration field, dependency, migration or budget increase.

## Correctness

| Requirement/scenario | Observable evidence |
|---|---|
| Duplicate identity denied | Existing test_trusted_header_identity.py + new projected remote duplicate case; protected route 401 proxy_auth_required |
| Single valid identity authenticates | test_setup_auth_paths.py settings/session, actual mutation/audit actor + projected client IP; existing auth suite |
| Remote projected user differs from proxy | Trusted socket loopback outside-user-CIDR route now 200; before fix 401 |
| Untrusted/uncaptured socket cannot acquire authority | Spoofed projected loopback now 401; before fix 200; missing captured peer returns no principal |
| Occupied callback port | Real occupied socket, listener cleanup and pending start/status route, manual callback with synthetic exchange succeeds and persists account; safe warning, no state/code in captured logs |
| Cancelled listener startup | test_oauth_callback_startup.py cancellation after initialization propagates and clears runner/site; retry after failed bind works |
| TLS proxy and trust layers | Concrete remote guide TLS/certificate/projection/application allowlists; actual source runtime behind shipped nginx + TLS adaptation: matching trusted CA readiness, untrusted CA refused, bootstrap/auth/CSRF, unbuffered SSE and WS completion/reconnect |
| Key-authenticated Codex configuration/endpoints | Guide and shipped TOML parse/marker/suffix regressions; actual Codex0.159.3 strict config under isolated home/ephemeral auth; HTTP and actual client WS complete, selected upstream account confirmed, credit vs pooled quota confirmed, Pause refuses new dispatch |

Actual Codex with a WS-declared provider produced one downstream client WS connection and two upstream WS response requests; generation stream responded SETUP_OK. The fixture ledger's 14 generation/probe requests all used cgpt-setup. Stored usage probe returned primary10/secondary20; key credit windows18000/604800s and matching ChatGPT pooled windows were independently asserted. Pause returned503 and generated no new fixture dispatch.

## Coherence/checks

- 324 unique focused tests passed: 122 auth/OAuth/projection/lifecycle, 24 identity/firewall/bootstrap, 178 client/HTTP/WS/backend passthrough/examples. Updated actor/manual recovery assertions passed separately without inflating the unique count.
- Negative evidence: provenance regressions3 failed/1 passed; callback cleanup/warning3 failed before fixes. Four proxy-env tests originally failed due to Windows fixture deleting lowercase settings with uppercase aliases; order fixed, assertions unchanged, final178 passed.
- Full Ruff/format: PASS,1427 files; full ty PASS; five architecture checks PASS, no threshold changes.
- Strict rendered MkDocs PASS. Simplicity budgets unchanged: README222/225, headings10/10, env54/60, nav5/5, root0/0, settings98/98.
- OpenSpec1.11.0 strict change and 68 main capabilities PASS; exact four-block/eight-scenario sync verified.
- Graph guided exact identity/callback consumers; some dynamic aiohttp/framework edges are not reliable in the index and were verified in current source and runtime. Related request-locality/firewall/projection/client egress implementation inspected, retained unchanged.

## Limits/disposition

No unresolved implementation requirement or critical verification issue remains for this local change; ready to archive. The audit keeps SETUP-06 real OpenAI login/entitlement open, and SETUP-04 physical network/platform probes open. Synthetic upstream/token exchange is explicitly labelled; actual installed client/runtime/routing is separately proven. Voluntary WS reconnect does not certify all real idle/network-switching cases or external forward proxies.

Official auth docs currently say requires_openai_auth=true ignores env_key; isolated Codex0.159.3 completed using the provider key under both values. The guide records the version discrepancy and recommends the explicit provider-key CLI mode, preserving advanced Desktop eligibility examples. Source: https://learn.chatgpt.com/docs/auth#alternative-model-providers and https://learn.chatgpt.com/docs/config-file/config-reference.

Local runtime report: C:/Users/ext/AppData/Local/Temp/codex-transport-20261002/report.json. No user auth.json or configuration was edited; no production store was used. All rehearsal containers/volumes were removed and the original server remained running. No commit/push/release/CI dispatch or deployment occurred.
