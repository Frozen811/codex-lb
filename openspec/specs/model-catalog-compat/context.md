# Model catalog compatibility context

The requirements are in [spec.md](spec.md).

## Stored source instructions and compatible output budgets

The [source instruction contract](spec.md#requirement-source-base-instructions-are-preserved-in-codex-catalogs)
projects the operator's stored string directly into the typed catalog entry.
For example, `{"base_instructions":"  Keep 日本語 comments.\r\n"}` keeps the
two leading spaces and CRLF on both native catalog views. A missing, null or
object-valued instruction keeps the empty default. Updating metadata replaces
the next catalog response; a pinned client catalog still needs its own refresh.
Server-side request overrides remain private to forwarding.

The [output-budget contract](spec.md#requirement-compatible-output-budgets-use-valid-upstream-counts)
uses a positive non-boolean integer as explicit upstream evidence. For
example, GPT-6 Sol with a raw limit of 96000 exposes 96000 in every compatible
output field; `true`, zero or a negative count instead uses its existing
128000 fallback. An unknown model with malformed metadata keeps null.
This is a compatibility projection, so it neither edits native raw metadata
nor changes the input budget or how many tokens a generation requests.

The audit verifies dashboard persistence/update and local catalog routes,
including individual retrieval and the native data alias. It does not certify
hosted model limits, live client catalog refresh or published artifacts.

## Individual model retrieval

OpenAI-compatible clients such as Visual Studio Copilot can validate a model
with `GET /v1/models/{model_id}` before using it. The [retrieval contract](spec.md#requirement-individual-model-retrieval-matches-the-visible-catalog)
uses the visible list catalog's allowlist and source-assignment policies.
For example, `/v1/models/vendor/model/` retrieves the `vendor/model` entry;
the final slash is a route delimiter and the internal slash stays in the ID.

The direct slash route precedes the greedy ID route to avoid an incorrect 404.
Unknown, allowlist-excluded and unassigned-source models use `model_not_found`,
without exposing hidden metadata. Independent requests can generate different
`created` timestamps; all other fields match the list item. Local HTTP tests
verify these cases and reservation release on catalog failure. Actual Visual
Studio registration and hosted model availability remain external evidence.

## Codex client discovery

The native catalog can advertise a model correctly while a client still uses
its bundled list. This distinction matters when a model becomes available
after the installed client's bundled catalog was built.

In Codex 0.159.0, configuring a provider's `env_key` puts discovery on the
API-key path, including when `requires_openai_auth = true`. That path needs
both the `api_key_model_discovery` feature and support for an API-key catalog.
A custom `base_url` needs an explicit `model_catalog_url` for the latter.

For example, a provider whose base URL is
`http://127.0.0.1:2455/backend-api/codex` uses
`http://127.0.0.1:2455/backend-api/codex/models` as its catalog URL, together
with `api_key_model_discovery = true` in `[features]`. Keep the host and port
aligned when configuring a remote installation. These settings do not replace
the provider's authentication or capability-routing settings.

The [client setup guide](../../../docs/client-setup.md#model-discovery-in-the-codex-app)
and [downloadable example](../../../docs/examples/codex/config.toml) include
both settings. Merge them into existing TOML tables and restart the desktop
app so it loads the updated configuration.

### Evidence and limits

An isolated Codex 0.159.0 app-server probe using the same authentication and
binary produced the following `model/list` results:

| Configuration | Newly advertised model |
| --- | --- |
| Built-in subscription provider | Present, not hidden |
| Custom provider with `env_key`, without discovery settings | Absent |
| Custom provider with the discovery feature only | Absent |
| Custom provider with the feature and explicit catalog URL | Present, not hidden |

This verifies catalog ingestion, not inference entitlement. Setting `model`
by name and populating the model picker are separate concerns. The behavior
is version-specific; this evidence does not promise compatibility with every
Codex release.

Version-pinned Codex sources:
- [API-key discovery gate](https://github.com/openai/codex/blob/687a119f0fcaace47e1f1abcc77cec6c813fd6da/codex-rs/models-manager/src/manager.rs#L485-L495)
- [Custom-provider catalog support](https://github.com/openai/codex/blob/687a119f0fcaace47e1f1abcc77cec6c813fd6da/codex-rs/model-provider/src/models_endpoint.rs#L201-L209)

## Astra bootstrap and retained Spark discovery

The [Astra bootstrap requirement](spec.md#requirement-astra-bootstrap-metadata-preserves-captured-native-capabilities)
uses [OpenAI Codex rust-v0.153.4](https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/models-manager/models.json)
as a captured startup fallback. It retains the 272000 backend input budget,
872000 ceiling, low default reasoning, unified_exec shell and native code-mode
capabilities. Pricing remains owned by the shared pricing snapshot. A live
authoritative catalog can omit Astra; bootstrap must not grant live access.

Spark is a quota-only bootstrap model: omission from a general catalog does
not prove withdrawal of the separate allowance. A controlled Pro catalog
containing only Luna was persisted to isolated SQLite and restored through
the startup reconciliation path; native, compatible and dashboard catalog
APIs retained Spark. This proves catalog visibility, not live inference
entitlement or provider acceptance.

Published and inline API-key discovery fragments are checked after merging
provider-only fragments with the shipped top-level feature settings, as the
guide instructs. The existing installed-client harness requires macOS
sandbox-exec, so Windows validation of TOML does not establish live picker
behavior on a current client.
