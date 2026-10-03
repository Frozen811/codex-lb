# codex-lb (Hardened Community Edition)
*Community fork of [Soju06/codex-lb](https://github.com/Soju06/codex-lb); independent verification is tracked in [issues-check.md](issues-check.md).*

---

## 🌐 English Overview

### Executive Summary

**codex-lb Hardened Community Edition** is the historical name of this fork. The published [v1.25.0-hardened.3](https://github.com/Frozen811/codex-lb/releases/tag/v1.25.0-hardened.3) has package metadata `1.25.1`; its runtime/version drift and later source fixes are recorded in [the independent audit](issues-check.md). This document describes source integration work, not certification of all fixes in that artifact.

While the upstream repository established powerful load-balancing and account-pooling concepts, production environments at scale suffered from critical failure modes:
1. **HTTP/2 Transport Cascades**: A single dropped stream in Native Egress severed the underlying HTTP/2 connection, abruptly terminating all concurrent streams across all accounts.
2. **Stream Cap Freezes**: Streams interrupted before terminal events leaked their concurrency leases, permanently exhausting `account_stream_cap` until restart.
3. **Upstream Contract Breaches**: OpenAI/Codex API breaking changes (such as rejecting `max_output_tokens` with HTTP 400 and rejecting compaction triggers with HTTP 404) broke account health probes and automatic window warmup.
4. **SQLite Concurrency Deadlocks**: Intense multi-stream burst traffic produced unrecoverable database locks ("database is locked" errors).
5. **Session wedging**: Injected anchors rejected by upstream (`previous_response_not_found`) caused client hangs without yielding terminal error events.

The source registry contains 120 unique issue links, 128 PR links and 49 discussion links as counted on 2026-10-02; these are linked records, not verified fixes or current GitHub open counts. See [ISSUES.md](ISSUES.md) for the counting rule and historical source-author claims, and [issues-check.md](issues-check.md) for scoped tests, source SHAs, artifact evidence and remaining work. No aggregate completion or production-readiness claim is made.

---

### Key Architectural Fixes & Enhancements

#### 1. Native Egress, Rust Network Engine & HTTP/2 Multiplexing
- **Stream Cascade Isolation ([#2471](https://github.com/Soju06/codex-lb/issues/2471), [#2470](https://github.com/Soju06/codex-lb/issues/2470))**:
  - Implemented strict per-stream lifecycle boundaries. A network drop on one stream no longer tears down the shared HTTP/2 connection.
  - Added deterministic `finally: await stream.aclose()` blocks in `_stream_response_error_events` and egress adapters, guaranteeing that `account_stream_cap` leases are freed immediately upon disconnection.
  - Settle account leases and circuit states before error-health state writes.
- **Backpressure & Connection Recovery**:
  - Bound Native Egress worker queues to prevent unbounded memory growth during downstream stalls.
  - Idle disconnects on pooled connections no longer mark healthy accounts as unhealthy.

#### 2. HTTP-to-WebSocket Bridge & Replay Relocation
- **Terminal Event Delivery on Injected Anchor Rejection ([#2493](https://github.com/Soju06/codex-lb/issues/2493))**:
  - When upstream returns `previous_response_not_found` on an injected continuation anchor and no fresh replay is available, the bridge now explicitly emits a terminal `response.failed` event with standardized error envelopes, preventing downstream client hangs.
- **Replay Relocation Engine ([PR #2428](https://github.com/Soju06/codex-lb/pull/2428))**:
  - Integrated `app/modules/proxy/replay_relocation.py` (`RelocationInputs`, `RelocationVerdict`, `decide_relocation`).
  - Added pure transcript reconstruction (`project_durable_transcript_for_account_neutral_fresh_replay`), positive item enumeration, and tail overlap resolution in `app/modules/proxy/replay_safety.py`.
- **Session Quarantine & Takeover**:
  - Stale and abandoned bridge sessions are retired gracefully without pinning shutdown or blocking database writers.

#### 3. Upstream Codex / OpenAI Responses Compatibility
- **Force Probe Modernization ([PR #2496](https://github.com/Soju06/codex-lb/pull/2496), [#2410](https://github.com/Soju06/codex-lb/issues/2410))**:
  - Removed unsupported `max_output_tokens` field from Force Probe payloads in `app/modules/accounts/service.py`. The Codex Responses endpoint now rejects this field with HTTP 400; omitting it allows probes to succeed with HTTP 200 and wake rate limiters properly.
- **Transparent Warmup Compaction Fallback ([#1895](https://github.com/Soju06/codex-lb/issues/1895), [#1976](https://github.com/Soju06/codex-lb/issues/1976))**:
  - Added automatic fallback to minimal plain Responses API requests when upstream returns 404 on `compaction_trigger`, allowing `/v1/warmup` to reliably initialize 5-hour quota windows.
  - Corrected rolling quota reset deadline calculations for multi-account pools.

#### 4. Dashboard, Web UI & API Keys
- **Dashboard API Key Usage Reset ([#2492](https://github.com/Soju06/codex-lb/issues/2492))**:
  - Added individual "Reset usage" actions in the API key row menu and bulk reset actions via multi-row selection with "Select all with limits".
- **Authentication & TOTP Stability**:
  - Repaired TOTP dialog submission on macOS Chrome / WebKit browsers and normalized multi-byte unicode input handling.
- **Production Static Assets**:
  - Built fresh Vite bundle directly into `app/static/`, enabling full dashboard functionality zero-config out of the box.

#### 5. Database Reliability & Multi-Replica Operations
- **SQLite Watchdog & Write Timeout Protection**:
  - Guarded single-writer SQLite transactions with timeout monitors, preventing silent deadlocks under high request volume.
  - Implemented clean process lifecycle sentinels and automated WAL checkpoints.
- **Alembic Migration Topology**:
  - Single-head migration graph with strict downgrade/upgrade tests and data backfill hygiene.

#### 6. Security & Audit Hygiene
- **Universal Log Sanitization ([#2028](https://github.com/Soju06/codex-lb/issues/2028), [PR #2490](https://github.com/Soju06/codex-lb/pull/2490))**:
  - Implemented `install_redacting_loop_exception_handler` wrapping asyncio event loop exceptions in `_RedactedRepr`, preventing credential leakage in unhandled task traces.
  - Sanitized Bearer tokens, passwords, API keys, and URL query credentials across all log handlers.

#### 7. Live Deployment Hardening (v1.25.0-hardened.3)
- **OAuth Proxy Route Reauthentication**: Passed `intended_account_id` to route resolution so reauthenticating accounts route via their own assigned proxy binding instead of falling back to default pool or erroring with `default_pool_unconfigured`. Unbound accounts egress direct as intended, avoiding IP split.
- **Continuity Single-Account Owner Pinning ([#2274](https://github.com/Soju06/codex-lb/issues/2274))**: On an owner-lookup miss for `previous_response_id`, single-account pools and scoped keys now unambiguously pin the single candidate rather than failing closed with 502 `previous_response_owner_unavailable`.
- **Image Fan-out (`n > 1`) Settlement & Fault Isolation**: Replaced unprotected `asyncio.gather` with `gather(return_exceptions=True)`. Settles token usage for all successful subcalls on partial failure instead of discarding them, releases on zero success or cancellation, and cleanly surfaces the first error.
- **Bridge Payload Signing via Configured Encryption Key**: Changed `_sign_bridge_payload` to call `get_or_create_key()` which honors `CODEX_LB_ENCRYPTION_KEY` env var across stateless cluster replicas.
- **Reset-Credit Target Account Validation**: Validates `target_chatgpt_account_id` before redeeming reset credits cross-account, preventing sending requests upstream with `account_id=None`.

---

### Verification & Quality Assurance

- Evidence is recorded per source SHA and product path in [issues-check.md](issues-check.md), including failed checks and remaining artifact/platform limits. Historical totals and author-reported test runs do not certify the current tree or release.
- OpenSpec validation uses the CI-pinned CLI; architecture and simplicity limits remain governed by repository checks. Targeted local tests and successful exact-source cloud CI are separate evidence.

---

## 🇷🇺 Русскоязычное описание

### Общий обзор и назначение

**codex-lb Hardened Community Edition** — историческое название форка. Публичный [v1.25.0-hardened.3](https://github.com/Frozen811/codex-lb/releases/tag/v1.25.0-hardened.3) имеет версию пакета `1.25.1`; расхождение runtime и последующие source-исправления описаны в [независимом аудите](issues-check.md). Этот документ описывает интеграции в исходниках, а не подтверждение всех исправлений в опубликованном артефакте.

При эксплуатации оригинального репозитория под реальной нагрузкой возникали критические отказы:
1. **Разрывы HTTP/2 соединений**: Сетевой сбой на одном активном стриме Native Egress приводил к закрытию всего HTTP/2 мультиплексированного соединения и обрыву стримов всех остальных аккаунтов.
2. **Зависание аккаунтов по лимиту стримов**: Исключения до прихода терминального события не вызывали `aclose()` и не освобождали lease стрима, навсегда блокируя аккаунт по `account_stream_cap`.
3. **Несовместимость с изменениями upstream OpenAI/Codex**: Недавние изменения в эндпоинтах Codex привели к тому, что передача поля `max_output_tokens` возвращала HTTP 400, блокируя принудительный опрос здоровья аккаунтов (Force Probe), а отправка `compaction_trigger` возвращала 404 при автопрогреве лимитов (/v1/warmup).
4. **Блокировки базы данных SQLite**: Параллельные потоки вызывали дедлоки («database is locked»).
5. **Подвисание клиентов при реджекте якорей**: При ошибке `previous_response_not_found` на proxy-injected якоре HTTP-мост закрывался без отправки терминального события ошибки.

В исходном реестре на 2026-10-02 найдены ссылки на 120 уникальных Issues, 128 PR и 49 Discussions. Это ссылочные записи, а не количество проверенных исправлений или текущих открытых обращений GitHub. Правило подсчёта и исторические заявления автора находятся в [ISSUES.md](ISSUES.md); доказательства отдельных проверок и открытая очередь — в [issues-check.md](issues-check.md). Общая завершённость и готовность к production не заявляются.

---

### Ключевые исправления по подсистемам

#### 1. Сетевой транспорт Native Egress (Rust / HTTP/2)
- **Изоляция сбоев стримов ([#2471](https://github.com/Soju06/codex-lb/issues/2471), [#2470](https://github.com/Soju06/codex-lb/issues/2470))**:
  - Исключена передача сбоя одного стрима на всё HTTP/2 соединение.
  - Внедрены гарантированные блоки `finally: await stream.aclose()`, освобождающие аренду стрима в любых сценариях обрыва сети.
  - Резервации API-ключей и аренда аккаунтов закрываются строго до фиксации метрик ошибок.

#### 2. HTTP-to-WebSocket мост и модуль Replay Relocation
- **Терминальные события при отклонении якоря ([#2493](https://github.com/Soju06/codex-lb/issues/2493))**:
  - Клиент больше не висит бесконечно при реджекте инжектированного якоря upstream-сервисом: мост генерирует корректное терминальное событие `response.failed`.
- **Интеграция модуля Replay Relocation ([PR #2428](https://github.com/Soju06/codex-lb/pull/2428))**:
  - Реализован алгоритм чистой реконструкции транскрипта беседы (`replay_relocation.py`, `replay_safety.py`), обеспечивающий плавную смену аккаунтов без повреждения контекста диалога.

#### 3. Совместимость с upstream Codex API
- **Обновление Force Probe ([PR #2496](https://github.com/Soju06/codex-lb/pull/2496), [#2410](https://github.com/Soju06/codex-lb/issues/2410))**:
  - Из тела запроса Force Probe удалено поле `max_output_tokens`, на которое текущий API Codex возвращает ошибку 400 `Unsupported parameter: max_output_tokens`. Опрос аккаунтов теперь возвращает HTTP 200 и надежно активирует лимитеры.
- **Прозрачный фоллбэк прогрева лимитов ([#1895](https://github.com/Soju06/codex-lb/issues/1895))**:
  - При возврате HTTP 404 на эндпоинте компактинга система автоматически переключается на минимальный plain Responses API запрос, гарантируя старт 5-часовых окон квоты.

#### 4. Панель управления (Dashboard UI) и API-ключи
- **Сброс счетчиков лимитов API-ключей ([#2492](https://github.com/Soju06/codex-lb/issues/2492))**:
  - В таблицу API-ключей добавлено действие сброса использования («Reset usage») для отдельного ключа и массовый сброс для выбранных ключей без необходимости перевыпуска.
- **Сборка фронтенда**:
  - Свежий бандл скомпилирован в `app/static/`, интерфейс работает из коробки без запуска dev-серверов Node.js/Bun.

#### 5. База данных и многопроцессорность
- **Защита от дедлоков SQLite**:
  - Добавлен сторожевой таймер долгих транзакций записи, устранены условия гонки при конкурентных запросах.
  - Топология миграций Alembic проверена на единый граф без конфликтующих веток.

#### 6. Безопасность и логи
- **Маскирование учетных данных ([#2028](https://github.com/Soju06/codex-lb/issues/2028), [PR #2490](https://github.com/Soju06/codex-lb/pull/2490))**:
  - Устранена утечка Bearer-токенов, API-ключей и паролей в логах исключений Event Loop через специальную обертку `_RedactedRepr`.

#### 7. Дополнительная стабилизация в проде (v1.25.0-hardened.3)
- **Привязка прокси при повторной OAuth-авторизации**: Передача `intended_account_id` в резолвер маршрутов обеспечивает роутинг через назначенный прокси конкретного аккаунта; несвязанные аккаунты идут напрямую без ошибки `default_pool_unconfigured` и без разрыва IP.
- **Определение владельца преемственности для одиночных аккаунтов ([#2274](https://github.com/Soju06/codex-lb/issues/2274))**: При промахе поиска владельца по `previous_response_id` для пулов или ключей с единственным аккаунтом запрос больше не падает с 502 `previous_response_owner_unavailable`, а надёжно привязывается к единственному владельцу.
- **Учёт токенов и устойчивость Image Fan-out (`n > 1`)**: При частичном сбое генерации пачки изображений использованные токены успешных подзапросов корректно фиксируются в лимитах ключа, а при отмене резервация освобождается.
- **Подпись запросов моста настроенным ключом шифрования**: Функция подписи моста использует `get_or_create_key()`, соблюдая общую переменную окружения `CODEX_LB_ENCRYPTION_KEY` для всех реплик.
- **Валидация целевого аккаунта при списании кредитов сброса лимита**: Защита от отправки запроса с `account_id=None` при меж-аккаунтном списании.

---

### Стандарты верификации и простоты

- **OpenSpec SSOT**: Нормативные контракты находятся в `openspec/specs/`; результат валидации привязан к версии CLI и проверяемому source SHA в [независимом аудите](issues-check.md).
- **Simplicity Gates**: Бюджеты определены в `.github/simplicity-budgets.toml`; проверяем их на конкретном дереве исходников.
- **Ограничения по размеру файлов**: Архитектурные лимиты проверяются repository checkers, а не историческим счётчиком в release notes.
- **Тесты**: Целевые локальные тесты, полный cloud CI и проверка опубликованных артефактов учитываются отдельно; результаты и ограничения — в [issues-check.md](issues-check.md).

---

## 🚀 Quick Start / Быстрый запуск

### 1. Локальный запуск через `uv` (Local run)
Source checkout: нужны uv и Bun **1.3.14**. Launcher строит отсутствующие
dashboard assets; один `uv run codex-lb` их не создаёт. Bash:
```bash
git clone https://github.com/Frozen811/codex-lb.git || exit 1
cd codex-lb || exit 1
./run.sh
```
Windows PowerShell и выбор full SHA: [Python guide](docs/deployment/python.md#run-from-a-fork-checkout).
Панель управления и прокси доступны по адресу: **`http://localhost:2455`**.

### 2. Запуск в Docker (Docker run)
Docker Engine / Linux containers, Bash:
```bash
git clone https://github.com/Frozen811/codex-lb.git || exit 1
cd codex-lb || exit 1
docker build -t codex-lb:hardened .
docker volume create codex-lb-data
docker run -d --name codex-lb \
  -p 2455:2455 -p 1455:1455 \
  -v codex-lb-data:/var/lib/codex-lb \
  codex-lb:hardened
```

### 3. Настройка клиента Codex CLI (`~/.codex/config.toml`)
Ниже только provider fragment; полный пример с API-key auth и model:
[Client Setup](docs/client-setup.md#codex-cli-ide-extension).
```toml
model_provider = "codex-lb"

[model_providers.codex-lb]
base_url = "http://127.0.0.1:2455/backend-api/codex"
wire_api = "responses"
```

---

<a id="how-to-update"></a>
## 🔄 How to Update / Инструкция по обновлению

### 1. If using Git clone (Windows / Linux / macOS)
Stop the old process/writers, save a paired DB/key backup, and select a reviewed
fork revision. Remote names are local conventions: `origin` may point at
Soju06 rather than Frozen811. The explicit fetch below does not depend on that
name. Use a clean checkout or a separate checkout for saved local changes.

Source launchers require uv and Bun 1.3.14 for missing dashboard assets; see
the [checkout guide](docs/deployment/python.md#run-from-a-fork-checkout).
After updating frontend sources, rebuild them with the pinned Bun/frozen lock
before restarting, since complete existing assets are reused.

**Windows (PowerShell):**
```powershell
$sourceRevision = "<reviewed-full-sha>"
if (git status --porcelain) { throw "Save local changes or use a separate checkout first." }
git fetch --depth 1 https://github.com/Frozen811/codex-lb.git $sourceRevision
if ($LASTEXITCODE -ne 0) { throw "Fork fetch failed." }
git switch --detach FETCH_HEAD
if ($LASTEXITCODE -ne 0) { throw "Source selection failed." }
git rev-parse HEAD
# Rebuild changed frontend sources with Bun 1.3.14 before normal startup.
.\run.ps1
# or double-click start.bat
```

**Linux / macOS / Server:**
```bash
source_revision="<reviewed-full-sha>"
test -z "$(git status --porcelain)" || { echo "Save local changes or use a separate checkout first."; exit 1; }
git fetch --depth 1 https://github.com/Frozen811/codex-lb.git "$source_revision" && git switch --detach FETCH_HEAD || { echo "Fork source selection failed."; exit 1; }
git rev-parse HEAD
uv sync --frozen
./run.sh
```

The repository does not install a `codex-lb.service` systemd unit. If you
created a service separately, update its selected source/package and restart
the unit you configured. Keep its data directory and encryption key; see the
[Python](docs/deployment/python.md), [Nix](docs/deployment/nix.md) and
[remote access](docs/deployment/remote.md) guides for the applicable launch mode.

Run each step only after the previous one succeeds. A remote SHA does not
include uncommitted local audit fixes. Runtime version alone does not identify
the selected code; compare the source/image identity and verify retained
settings/account access. See [update and rollback checks](docs/deployment/docker.md#update-identity-and-rollback)
and [platform evidence](docs/deployment/python.md#platform-and-topology-evidence).

---

### 2. If using pip or uv pre-built wheel
The URLs below install the historical hardened.3 artifact. Its package version
is 1.25.1 but runtime is 1.25.0-beta.9; it does not include later checkout fixes.
Select a verified newer artifact URL explicitly when available. See the
[Python installation guide](docs/deployment/python.md) for source and package channels.

**pip:**
```bash
pip install --upgrade https://github.com/Frozen811/codex-lb/releases/download/v1.25.0-hardened.3/codex_lb-1.25.1-py3-none-any.whl
codex-lb
```

**uv:**
```bash
uv tool install --reinstall https://github.com/Frozen811/codex-lb/releases/download/v1.25.0-hardened.3/codex_lb-1.25.1-py3-none-any.whl
codex-lb
```

---

### 3. If running via uvx (zero install)
For the historical fork wheel, refresh its cached tool environment explicitly:
```bash
uvx --refresh --from https://github.com/Frozen811/codex-lb/releases/download/v1.25.0-hardened.3/codex_lb-1.25.1-py3-none-any.whl codex-lb
```

Refreshing this URL does not select new source fixes. Git installs require the
selected source SHA and Bun 1.3.14 when dashboard assets need building; see the
Python guide. Keep the data directory/encryption key and back up the database
before switching code or package sources. Do not assume a downgrade can read
an upgraded database schema.

---

### 4. If using Docker / Docker Compose
For a source build, back up the application volume and database, select the
desired fork revision, and rebuild only the application. Server-only Compose:
```bash
# Select the reviewed fork SHA explicitly as above, then:
docker compose -f docker-compose.prod.yml up -d --force-recreate server
```

Root `docker-compose.yml` is development (backend + Vite frontend); use
`docker compose up -d --build --force-recreate server frontend` for that setup.
Keep the same volumes and database URL. A source pull/rebuild does not update
an installation made from a public image. Public `latest`/`1.25.1` still refer
to historical source `f622c563`; choose a tested release digest deliberately.
See the [fork Docker guide](docs/deployment/docker.md) for image provenance,
database profiles, external PostgreSQL and recreation. Restoring older code
may also require restoring the matching database backup.

