# Tasks for Strict Model Routing and Access Token Account Support

## Tasks
- [x] 1. Support access-token-only credential imports in `app/core/auth/__init__.py` and `app/modules/accounts/schemas.py` <!-- id: task-access-token-schemas -->
- [x] 2. Update claims extraction to support JWT access-token fallback and explicit auth metadata <!-- id: task-claims-extraction -->
- [x] 3. Support non-refreshable accounts in `app/modules/accounts/auth_manager.py`, `service.py`, and `mappers.py` <!-- id: task-non-refreshable-handling -->
- [x] 4. Implement strict model-to-account routing in `app/modules/proxy/model_account_routing.py` and `app/modules/proxy/service.py` <!-- id: task-strict-model-routing -->
- [x] 5. Add unit and integration tests for access-token imports, non-refreshable accounts, and model routing <!-- id: task-tests -->
- [x] 6. Sync delta specs to main specs and validate OpenSpec <!-- id: task-openspec-sync -->
