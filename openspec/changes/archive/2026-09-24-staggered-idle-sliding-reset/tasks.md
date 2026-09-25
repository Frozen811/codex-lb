## 1. Regression coverage

- [x] 1.1 Add unit tests proving non-zero staggered idle slots fire when `reset_at` slides with `now`.
- [x] 1.2 Prove stable slot staggering across the rolling window and across refresh ticks.

## 2. Implementation

- [x] 2.1 Update `_staggered_idle_due` in `app/modules/limit_warmup/service.py` to detect sliding `reset_at` and evaluate slot offsets against a stable cycle start.
- [x] 2.2 Preserve fixed reset evaluation for accounts with anchored reset deadlines.

## 3. Verification

- [x] 3.1 Run `uv run pytest tests/unit/test_limit_warmup.py`.
- [x] 3.2 Run `uv run ruff check app tests`.
- [x] 3.3 Validate OpenSpec specs: `bunx @fission-ai/openspec@1.11.0 validate --specs`.
