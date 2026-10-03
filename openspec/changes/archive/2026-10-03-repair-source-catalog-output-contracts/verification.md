# Verification: source catalogs, collaboration choices and output budgets

Date: 2026-10-03. Base HEAD: `f52adb7274c96c0702e19aa02eabd4f1c7556231`.
Evidence applies to this dirty working tree and the fingerprints below.
Exactly three audit entries: UP-PR-2525, UP-PR-2526 and UP-PR-2528.

## Results

| Dimension | Result |
|---|---|
| Completeness | All seven tasks completed before archive |
| Correctness | Three requirement blocks mapped to public-route tests below |
| Coherence | Shared compatibility projection and choice predicate; no configuration or migration |
| Critical / warning findings | None remaining within this local scope |

## Reproduction and repairs

New regression selection before production edits:

```text
python -m pytest tests/integration/test_v1_models.py
  tests/integration/test_model_source_collaboration.py
  tests/integration/test_source_catalog_contracts.py -q
  -k 'output_budget_contract or prunes_namespaced_function_choices or persisted_source_instructions'
28 failed, 37 passed, 135 deselected
```

- Sixteen budget failures: raw `true` became 1, `false` became 0, and zero or
  negative integers bypassed the fallback. Failure example: `/v1/models`,
  GPT-6 Astra, raw `true`, observed 1 versus required 128000.
- Twelve choice failures: a recording loopback source received a forced or
  allowed `collaboration.spawn_agent` function choice after its namespace
  definition was removed. Mixed allowed choices also retained that dangling
  entry next to the legitimate bare function.
- All nine persisted-instruction cases passed before the fixes: the existing
  source implementation already handles instruction projection correctly.

The budget projection now admits only positive, non-boolean integers, without
coercion or changes to raw/native metadata. One shared choice predicate removes
namespaced functions when namespace tools were dropped, including entries in
`allowed_tools`; bare functions and remaining choice fields stay intact.

## Requirement and scenario coverage

### UP-PR-2525: Source base instructions are preserved in Codex catalogs

`test_persisted_source_instructions_update_both_catalog_views` creates an actual
source through the dashboard API, reads both native catalogs, replaces the
model metadata through PATCH and reads the persisted metadata back through
the dashboard API. Both catalogs then return the new exact Unicode/CRLF/tab
string without restart. Nine cases cover Unicode/whitespace strings, empty and
whitespace-only strings, null, boolean, integer, float, list and mapping.
Capability declarations remain exact and request overrides/credentials stay
out of catalogs. Existing unit/catalog cases cover absent metadata as well.

### UP-PR-2526: Source-routed Responses tools are capability-filtered

`test_source_responses_preserves_collaboration_tools_and_choices` drives both
public Responses paths and both slash forms through a real local aiohttp
upstream. It asserts complete nested namespace schemas and matching namespace,
function, allowed namespace and allowed namespaced-function choices. Valid
declarations include v1, v2, future whitespace-padded v99 and explicit namespace
opt-in. Unsupported hosted tools and include entries remain pruned.

The new negative-choice regression covers forced namespaced functions, an
allowed choice containing only a namespaced function, and a mixed allowed
choice. Missing/blank/non-string declaration tests remain conservative. All
88 cases in this suite are covered across the main run and the additional
16-case allowed-function selection. The six related API-key route tests also
pass, including replay namespace stripping and existing hosted-tool filters.

### UP-PR-2528: Compatible output budgets use valid upstream counts

`test_model_output_budget_contract_on_public_surfaces` covers three GPT-6 slugs
and an unknown model across eleven raw values (44 cases). Each case reads the
list route, individual retrieval, slash retrieval and native data alias.
All four output fields agree; valid 96000 and 1 remain authoritative; malformed
known values use 128000 and unknown values use null. Native raw field types,
registry metadata, 272000 input budgets and 872000 raw ceilings stay unchanged.
Existing route tests cover a fully missing raw field and GPT-6 fallback parity.

## Final validation

```text
python -m pytest tests/unit/test_model_sources_catalog.py
  tests/integration/test_v1_models.py
  tests/integration/test_model_source_collaboration.py
  tests/integration/test_source_catalog_contracts.py -q --tb=short --show-capture=no
252 passed

python -m pytest tests/integration/test_model_source_collaboration.py -q
  -k 'allowed-function-choice' --tb=short --show-capture=no
16 passed, 72 deselected

python -m pytest tests/integration/test_api_keys_api.py -q
  -k 'source and (tool or search or namespaces)' --tb=short --show-capture=no
6 passed, 100 deselected
```

Distinct covered cases: **274**. The extra 16-case selection was added after
the main run; its cases do not duplicate that run. Existing AnyIO deprecation
warning is unrelated. No test bootstrap credentials are retained here.

- Ruff check and format check: all four modified Python files PASS.
- Targeted ty: all four modified Python files PASS.
- `scripts/check_proxy_architecture.py`: PASS with existing boundaries.
- OpenSpec 1.11.0 strict change validation: PASS.
- Strict main validation: **68 passed, 0 failed**.
- Delta/main requirement blocks: exactly synchronized; no previous scenarios
  were removed from the modified source-tool-filtering requirement.
- Diff and source/contract review performed by the primary agent, without a
  delegated reviewer. Existing unrelated dirty edits remain in place.

## Source fingerprints (SHA-256)

| File | SHA-256 |
|---|---|
| `app/modules/proxy/api.py` | `c945e89f40810fa5969ed84f99d51f11a615c9736f80917fbcc216677872cf0e` |
| `tests/integration/test_v1_models.py` | `0a34782103c8d7b5360636eeb25c7aa1f29c9561fb35656f23ea18cc8215d91c` |
| `tests/integration/test_model_source_collaboration.py` | `1f8384280984ec2b71376fcd173375d5ce8083c733097b8559c03dc7eaa431ff` |
| `tests/integration/test_source_catalog_contracts.py` | `700065727e95205826a62fe173740bb04a96f0e4a0088bb5d1a97691a2a0a5a3` |
| `openspec/specs/model-catalog-compat/spec.md` | `860831fac83dad967451bcba8c3b323783a5672cbd21a8183708dab7b206679a` |
| `openspec/specs/responses-api-compat/spec.md` | `fe0eb52b25dc7a2f095531e31308745b9a340c91beffea7253fbf93b0c371e5e` |

## Scope limits

Local ASGI routes, real isolated SQLite persistence and loopback HTTP upstream
traffic are verified. Hosted providers, real client collaboration sessions,
public packages/images and current-head cloud gates are separate evidence.
No commit, push, merge, release or deployment was performed. This local batch
does not claim that upstream PRs are merged or their public gates are green.
