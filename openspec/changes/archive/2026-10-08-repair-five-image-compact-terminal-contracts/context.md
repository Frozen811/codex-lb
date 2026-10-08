# Context

Date: 2026-10-08, Europe/Kiev. Base main: `8369ec720c5ac935f7a64fe3f30aa1cbc323f5e5`. The initial checkout contains the completed auth/credit package documented in registry section 69. Its 19 files are backed up outside the repository with SHA-256 evidence.

Exactly five selected rows were initially НЕ ПРОВЕРЕНО: UP-PR-2503, UP-PR-2534, UP-PR-2451, UP-PR-2317, UP-PR-2319. Live GitHub bodies/heads were read before implementation. Stable behavior is governed by `openspec/specs/responses-api-compat/spec.md`, not unmerged upstream proposals.

Example: a legal oversized PNG base64 sibling plus an oversized JPEG URL containing `!` must follow the unsupported-shape raw path. It must not return a misleading local `payload_too_large` from the bridge. Legal oversized images alone still fail locally before any send.

Publication, hosted CI, real providers, production and unrelated registry rows remain outside this request.

Follow-up verification built the current Rust helper locally on Windows with Cargo 1.96.0 and the locked dependency graph. Native recompilation and local Python/helper IPC acceptance are verified; other platforms and production are separate. The final implementation scope also includes hidden compact aliases in `app/modules/proxy/api.py`. Native crate sources and the dependency lockfile were not modified.
