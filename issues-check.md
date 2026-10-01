# Независимая проверка форка codex-lb

Рабочий реестр проверки и исправления результатов работы другого агента в [Frozen811/codex-lb](https://github.com/Frozen811/codex-lb). Охватывает оформление репозитория, документацию, Docker-образы, пакеты, релизы, Actions, код и все заявления об исправлениях из [ISSUES.md](ISSUES.md).

Этот файл фиксирует доказательства, замечания, исправляющие коммиты и повторные проверки. Нормативные контракты остаются в [openspec/specs](openspec/specs), работа по изменению поведения — в [openspec/changes](openspec/changes). Заявления автора, зелёная сборка образа и наличие теста сами по себе не означают, что проблема решена.

**Последнее обновление: 2026-10-01.** Предыдущие локальные исправления и новый пакет INSTALL-06/07/08 закоммичены и отправлены в `fix/python-install-audit`; текущие результаты — §20. Stable main и публичные release artifacts не обновлялись. Реестр полного аудита установки — §15; прежние утверждения о неопубликованных правках ниже сохранены как история соответствующих прогонов.

## 1. Правила ведения

- У каждой проверки есть стабильный ID, конкретный SHA, статус и доказательства. При новом HEAD прежний результат остаётся историческим; затронутый участок проверяется повторно.
- Для исправления фиксируем исходный сценарий, ожидаемое и фактическое поведение, причину, изменённые файлы, OpenSpec, исправляющий SHA и результат повторной проверки.
- Закрываем пункт только после независимой проверки применимого продуктового пути: API, WebSocket, CLI, UI, миграция, установка или запуск опубликованного артефакта.
- Различаем тесты на моках, тесты с реальной БД, проверку внешнего маршрута, CI и проверку опубликованного образа. Указываем, что именно проверено и что осталось.
- Статус CI берём с GitHub для точного SHA и конкретного attempt. `skipped`, `cancelled` и успешный Docker Publish не заменяют прохождение обязательных checks.
- Групповой коммит проверяем по каждой заявленной задаче. Если исправление нескольких обращений одно и то же, связываем строки с одной карточкой доказательств, сохраняя все исходные ссылки.
- Не переносим автоматически отметки «РЕШЕНО», «MERGED» или «100%» из исходного реестра. Закрытый апстримный PR тоже нуждается в проверке его наличия и поведения в форке.
- Изменения поведения ведём по правилам [AGENTS.md](AGENTS.md), [CONTRIBUTING.md](.github/CONTRIBUTING.md) и [PRINCIPLES.md](PRINCIPLES.md). Архитектурные ограничения не ослабляем ради зелёного CI.
- Не записываем токены, пароли, содержимое приватных запросов и пользовательские данные. Используем обезличенные воспроизведения.
- Создание этого реестра не выполняет исправления, публикацию, push, merge, перезапуск сервиса или переписку с другим агентом. Такие действия выполняются в рамках последующих поручений пользователя.

### Статусы

| Статус | Значение |
|---|---|
| НЕ ПРОВЕРЕНО | Доказательств независимой проверки ещё нет |
| В ПРОВЕРКЕ | Исследуем код, артефакт или воспроизводим сценарий |
| ПОДТВЕРЖДЕНО | Дефект или нарушение подтверждено указанными доказательствами |
| ТРЕБУЕТ РАЗБОРА | Есть расхождение или риск, но причина либо применимость ещё не установлена |
| ИСПРАВЛЕНО, ЖДЁТ ПРОВЕРКИ | Есть исправляющий SHA; закрывать пока нельзя |
| ИСПРАВЛЕНО ЛОКАЛЬНО | Правка в рабочем дереве прошла указанные локальные проверки; исправляющего SHA, нового CI и релизного evidence ещё нет |
| ПРОВЕРЕНО | Объём проверки завершён; указаны SHA, доказательства и ограничения |
| НЕ ПРИМЕНИМО | Есть явное обоснование, почему пункт не относится к форку |

Приоритеты: P1 — падающий продуктовый путь, нарушение владения/расчётов или существенный блокер выпуска; P2 — регрессия, нарушение обязательной проверки, документации или поставки; P3 — оформление и улучшение сопровождаемости. Приоритет очереди не означает, что дефект уже подтверждён.

## 2. Исходный срез аудита

Срез за 2026-09-30, выполненный в этом чате до создания реестра. Это исходная точка, а не обещание актуальности после новых коммитов.

| Объект | Зафиксированное состояние |
|---|---|
| Форк | `Frozen811/codex-lb`, родитель `Soju06/codex-lb` |
| HEAD локально и на GitHub | `7ec39f82709ee1ca4c00489a8d5fc301d49320ed` |
| Рабочее дерево до создания файла | Чистое |
| Remotes | `origin` — апстрим; `fork` — репозиторий пользователя; локальная `main` отслеживает `origin/main` |
| Расхождение с апстримом | 49 коммитов форка, 19 апстримных; общая база `09a140fa9979a908e60acc97232367e0a08ef32c` |
| Апстримная main при сравнении | `f8ffbac2099a113fba54dfd8d77774f5bca80ffa` |
| Последний проверенный CI | [run 36761400788](https://github.com/Frozen811/codex-lb/actions/runs/36761400788), `failure`, HEAD `7ec39f82` |
| Предыдущий проверенный CI | [run 36756336188](https://github.com/Frozen811/codex-lb/actions/runs/36756336188), `failure`, HEAD `deed76ba` |
| Последний проверенный релиз | [v1.25.0-hardened.3](https://github.com/Frozen811/codex-lb/releases/tag/v1.25.0-hardened.3), опубликован 2026-09-30; Docker Publish выполнен на `deed76ba` |
| Артефакты релиза | `codex_lb-1.25.1-py3-none-any.whl`, `codex_lb-1.25.1.tar.gz`; содержимое и установка не проверены |
| OpenSpec | 68 основных capability-папок, 105 активных change-папок; наличие папки не означает завершение |
| Windows Actions | `windows-startup.yml` запускается вручную; на момент проверки запусков нет |
| Открытые PR форка | На момент проверки отсутствуют; состояния review threads и merge gates конкретного PR не оценивались |
| Исходный реестр | `ISSUES.md`: 390065 байт, 3712 строк; заявлено 164 решённых Issues/PRs и 0 оставшихся задач |

### Результаты уже выполненной проверки

- `python -m ruff check app tests`: успешно.
- `python scripts/check_proxy_architecture.py`: две ошибки, см. F-002.
- Целевой pytest: `tests/unit/test_continuity_owner.py`, scoped compact-тест и два API-теста owner lookup miss — **6 passed, 3 failed**.
- Второй целевой pytest: `test_images_fanout.py`, `test_oauth_route.py`, `test_reset_credits_redeem.py`, `test_http_bridge_forwarding.py` и один quarantine-сценарий — **94 passed**.
- Полная локальная suite, локальные PostgreSQL/MySQL, запуск контейнеров и установка релизных пакетов не выполнялись.

### Подтверждённое состояние Actions на исходном HEAD

| Проверка | Результат / доказательство |
|---|---|
| Lint (ruff) | Failure на architecture-check; [job 110044676627](https://github.com/Frozen811/codex-lb/actions/runs/36761400788/job/110044676627) |
| Unit | 2 failed, 12104 passed, 8 skipped, 1 xfailed; [job 110044676646](https://github.com/Frozen811/codex-lb/actions/runs/36761400788/job/110044676646) |
| Integration-core-1 | 1 failed, 1129 passed, 42 skipped; [job 110044676866](https://github.com/Frozen811/codex-lb/actions/runs/36761400788/job/110044676866) |
| Integration-core-2 | 3 failed, 1086 passed, 327 skipped; [job 110044676869](https://github.com/Frozen811/codex-lb/actions/runs/36761400788/job/110044676869) |
| Integration-core-3 | 2 failed, 1244 passed, 37 skipped; [job 110044676715](https://github.com/Frozen811/codex-lb/actions/runs/36761400788/job/110044676715) |
| MySQL | Failure с `DetachedInstanceError` на нескольких Responses/compact-сценариях; [job 110044677015](https://github.com/Frozen811/codex-lb/actions/runs/36761400788/job/110044677015) |
| Integration-core aggregate / CI Required | Failure; следствие упавших обязательных jobs, не отдельный первичный дефект |
| Остальные jobs в этом CI | Success: frontend lint/types/tests/build, browser smoke, Rust, PostgreSQL, bridge, e2e, миграции SQLite/PostgreSQL/MySQL, Docker build, package, OpenSpec, contributors, Nix, Helm |

## 3. Находки независимого аудита

| ID | Приоритет | Статус | Проблема / следующий шаг |
|---|---|---|---|
| F-001 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Account snapshots клонируются внутри сессии; реальный teardown и HTTP/compact/WebSocket проверены, см. раздел 13 |
| F-002 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Архитектурные границы восстановлены; `load_balancer.py` 3021/3021, checker проходит без изменения лимитов |
| F-003 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | OpenSpec согласован с bounded sole-owner fallback из #2274; неоднозначность, ошибки listing, пустой scope и paused admission покрыты |
| F-004 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Scoped compact test seam обновлён; реальный scoped API-путь и отсутствие выбора чужого аккаунта проверены |
| F-005 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Воспроизведён durable-first порядок: helper смешивал общий и локальный deadline; исправлен helper, оба порядка покрыты Responses-тестом; §17 |
| F-006 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Ungated publisher заменён exact-source CI gate с повторной проверкой перед upload/login; live main CI отказ подтверждён. Новый cloud workflow ещё не выполнен, см. раздел 16 |
| F-007 | P2 | ТРЕБУЕТ РАЗБОРА | Заявление «164 исправления / 100%» не подтверждено независимым проходом; проверить арифметику, объём и доказательства |
| F-008 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО / CLOUD ЧАСТИЧНО | Старый Windows workflow успешно запущен вручную; новая автоматизация и installed-wheel smoke проверены локально, требуют публикации и main-push run; §17 |
| F-009 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Direct WebSocket обходил unknown-owner refusal при Codex affinity; удалён обход, проверены новый запрос и уже открытый socket |
| F-010 | P1 | ПОДТВЕРЖДЕНО / ОТКРЫТО | Fresh anonymous GHCR check: `latest`/`1.25.1` всё ещё `f622c563`, hardened.3 — `deed76ba`. README теперь раскрывает исторический digest, production Compose локально собирает source; новые публичные исправления не опубликованы; §19 |
| F-011 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Пути diagnostics приведены к `/`, Windows/POSIX и outside-root identity проверены; architecture tests **16 passed**; §17 |
| F-012 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Обычный turn на открытом direct WebSocket обходил Pause; добавлена проверка routing marker перед send, после admission. Реальный Pause API, anchored/fresh turns, peer snapshot, удаление и сохранение in-flight ответа проверены, см. раздел 14 |
| F-013 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Managed версии и публичные пакеты расходились с runtime/Helm: `1.25.1` против `1.25.0-beta.9`; local parity, rebuild и clean install проверены. Исторические artifacts/tag не исправлены, см. раздел 16 |
| F-014 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Публичный sdist hardened.3 включает 5967 entries под `.kilo/worktrees`; explicit root selection и archive refusal добавлены. Новый локальный sdist не содержит worktree entries; cloud artifact ещё не опубликован |
| F-015 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Build contexts допускали nested env/credential files и agent worktrees; frontend также допускал host dependencies. Реальный BuildKit export на inert fixtures подтвердил baseline и устранение; §18 |
| F-016 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Bun в distroless/inline Compose расходился с package/workflows: 1.4.2 против 1.3.14; версии согласованы, оба targets собраны и запущены; §18 |
| F-017 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Docker CI собирал только стандартный образ без runtime smoke; добавлены distroless build и readiness/assets/native/CA проверки. Оба образа получили shell-free healthcheck; cloud execution ещё не выполнен; §18 |
| F-018 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Development frontend запускался с UID 0. Inline image переведён на USER bun с правильным ownership; UID 1000, Vite/TSX/proxy/watch/recreate подтверждены повторным прогоном; §18 |
| F-019 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Обычный production Compose up выбирал кешированный старый GHCR image вместо checkout. Введены local image name + pull_policy build; actual up заменил намеренно подложенный historical image актуальным source; §19 |
| F-020 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | MySQL ping и PostgreSQL pg_isready сообщали успех при неверном доступе; loopback PostgreSQL дополнительно обходил пароль через trust. Проверки заменены authenticated SQL, PostgreSQL использует HOSTNAME; wrong password/database реально отклоняются; §19 |
| F-021 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Основной Docker Quick Start и перевод выбирали upstream, fork latest обещал актуальность, update guide смешивал dev/prod/public. Исправлены выбор source/digest, происхождение образа, DB URLs и команды обновления; §19. Остальные claims F-007 отдельно |
| F-022 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Чистый Git/source install выпускал wheel без dashboard assets. Custom Hatch hook собирает assets закреплённым Bun/frozen lock либо отказывает с prerequisite guidance; actual clean source wheel/sdist и 11 regressions PASS; §20 |
| F-023 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Explicit-root sdist selector всё ещё допускал worktrees/credentials внутри выбранных frontend/app folders. Inert marker archive probe воспроизвёл 4 leaks; explicit nested exclusions устранили все markers; §20 |
| F-024 | P1 | ИСПРАВЛЕНО / WINDOWS CLOUD PASS | Новый build hook требовал Bun при editable uv sync и сломал первый Windows run. Editable-only exemption и CI guard проверены локально и на опубликованном SHA 4dce7220; §20.5 |

### F-001 — ORM-объекты покидают сессию до чтения ID

- Исходный коммит: `deed76bab5fafa36051c2cf474a1b29055988aae`; воспроизведено на `7ec39f82`.
- Исходные файлы в срезе 2026-09-30: `load_balancer.py`, `_service/continuity_owner.py`, callers в compact, streaming retry и WebSocket. После локальной правки общий resolver находится в [_service/support.py](app/modules/proxy/_service/support.py), старый модуль удалён.
- `list_continuity_owner_candidates()` возвращает `Account` после выхода из repository context. Чтение `candidates[0].id` вызывает `DetachedInstanceError`; обработчик исключений helper охватывает вызов listing, но не это чтение.
- Локально падают `test_v1_responses_single_account_missing_previous_response_owner_fails_closed_without_dispatch` и `test_v1_responses_compact_single_account_missing_previous_response_owner_fails_closed` из `tests/integration/test_proxy_responses.py`. В CI также падают forwarding-сценарии sticky sessions и OpenAI compatibility.
- Шесть helper-тестов на моках проходят: это не покрывает реальный teardown ORM-сессии.
- Проверка исправления: реальные repository/session boundaries, HTTP stream/non-stream, compact, WebSocket, scoped/unscoped key; ошибки остаются в ожидаемом OpenAI-envelope.
- Исправляющий SHA: **нет**. Локальная правка и повторная проверка выполнены 2026-10-01, см. раздел 13; cloud/release verification остаётся открытой.

### F-002 — архитектурные проверки

- Коммит: `deed76ba`; проверенный HEAD: `7ec39f82`.
- `load_balancer.py`: 3037 строк при нормативном лимите 3021.
- Compact импортирует `app.modules.proxy._service.continuity_owner`; checker разрешает для compact домен `support`.
- Доказательства: локальный `scripts/check_proxy_architecture.py`, CI lint job, unit `test_repository_proxy_architecture_passes`.
- Контракт: [proxy-architecture/spec.md](openspec/specs/proxy-architecture/spec.md). Восстановить границы/размер, не повышая лимиты ради прохождения.
- Исправляющий SHA: **нет**.

### F-003 / F-004 — continuity contract и scoped compact

- F-003: новый fallback при пропущенном owner lookup использует единственного кандидата. Основной контракт [Hard continuity owner lookup fails closed](openspec/specs/responses-api-compat/spec.md) требует немедленного fail-closed; точную допустимость scoped-key исключения и single-pool сценария необходимо разобрать вместе с историей и тестами.
- В diff `deed76ba` нет обновления OpenSpec, хотя меняются continuity, OAuth и другие продуктовые пути.
- F-004: `tests/unit/test_proxy_utils.py::test_compact_owner_miss_uses_api_key_scope_before_fail_closed` локально и в CI получает `ProxyResponseError(502)` вместо ожидаемого результата.
- Существующий тест подменяет `_load_selection_inputs`, новый helper использует другой listing path. Падение теста подтверждено; отдельный функциональный дефект scoped API-key пока не доказан.
- Не исправлять ситуацию удалением регрессионного теста или ослаблением ownership. Сначала установить требуемый контракт, затем синхронизировать implementation, OpenSpec и тест реального API-пути.
- Исправляющий SHA: **нет**.

### F-005 — quarantine cooldown зависит от условий запуска

- Сценарий: `tests/integration/test_http_quarantine_provenance.py::test_completion_separates_local_failure_from_durable_adoption[success-failed-load-retry-weaker]`.
- CI core-1: примерно `1599.989` вместо `700.0`. В отдельном локальном запуске прошёл.
- Разбор 2026-10-01: принудительный durable-first load перед local arm воспроизводит **1599.9605** на Windows. Во время `await` persistence другой reader может принять poison row до локального weaker fence; helper `arm` возвращал общий, уже продлённый deadline вместо срока локального evidence.
- Исправление: helper возвращает собственный `local_poison_until` или `suppressed_weaker_until`; исходные final-deadline/ownership assertions сохранены. Проверяются оба порядка, lookup retry и частичные failures. Production quarantine не менялся. Подробности и **69 passing integration tests** — §17; исправляющего SHA ещё нет, cloud shard после публикации остаётся обязательным.

### F-006 / F-008 — покрытие процесса поставки

- Docker Publish [run 36756416840](https://github.com/Frozen811/codex-lb/actions/runs/36756416840) завершился успешно на `deed76ba`, CI этого SHA завершился с ошибкой.
- [docker-publish.yml](.github/workflows/docker-publish.yml) запускается от опубликованного release или вручную; явного prerequisite на успешный CI в нём нет.
- Проверка тега, digest, содержимого образа, smoke-теста и фактически выдаваемого `latest` ещё не выполнена. Success означает успешную публикацию, а не отсутствие продуктовых регрессий.
- Исходный [windows-startup.yml](.github/workflows/windows-startup.yml) имел только `workflow_dispatch`; API показывал 0 запусков. 2026-10-01 получен успешный manual baseline run; локально добавлены автоматические source events, installed-wheel smoke и обязательный exact-source Windows prerequisite для публикации. Новая версия Actions ещё не опубликована; §17.

## 4. Очередь проверки оформления, поставки и сопровождения

Все пункты ниже — **НЕ ПРОВЕРЕНО**, если отдельная карточка находки не устанавливает более точный статус. Это перечень проверок, а не утверждение о наличии дефектов.

| ID | Приоритет | Область | Что проверяем и чем закрываем |
|---|---|---|---|
| IMG-01 | P1 | GHCR images | Все опубликованные теги, digest, source SHA, OCI version/revision/source labels; сопоставление release → commit → workflow → image |
| IMG-02 | P1 | latest / версии | Куда указывают `latest`, `1.25.1`, hardened-теги и команды README/compose; воспроизводимый pull по digest |
| IMG-03 | P1 | Чистый Docker-запуск | Запуск документированной команды без env-файла; dashboard, ready health, API, persistence, корректная остановка |
| IMG-04 | P1 | Обновление образа | Сохранение БД, WAL, encryption key и конфигурации; миграция существующих данных; проверяемый rollback |
| IMG-05 | P2 | Архитектуры | Фактический manifest и поддерживаемые CPU/OS; обещания multiarch подтверждены запуском или ограничены документацией |
| IMG-06 | P2 | Dockerfile / distroless | Python/Rust/helper, frontend assets, Alembic/config/data files, права каталогов, entrypoint, сигналы и shutdown |
| IMG-07 | P2 | Compose | `docker-compose.yml`/prod, optional `.env.local`, минимальная версия Compose, порты, volumes, healthcheck, restart и источник image |
| IMG-08 | P2 | Scan / исключения | Обоснованность `.trivyignore`, срок/объём исключений, связь со сканом; зелёный результат не получен скрытием применимых проблем |
| PKG-01 | P1 | Wheel / sdist | Чистая установка опубликованных артефактов; CLI, dashboard assets, миграции, imports; версия пакета совпадает с заявленной |
| PKG-02 | P2 | uvx / pip / clone | Все варианты Quick Start реально воспроизводятся; Git-install отличается от PyPI/релизного wheel только документированным образом |
| PKG-03 | P2 | Launchers | `run.ps1`, `run.sh`, `start.bat`: cwd с пробелами, fresh checkout, missing runtime, graceful errors, upgrade и отсутствие секретов в выводе |
| PKG-04 | P2 | Lockfiles | Python/Bun/Rust версии и lockfiles согласованы; frozen install воспроизводим; helper не собирается неожиданно при простом импорте |
| REL-01 | P1 | Release gates | CI того же SHA до выпуска, обязательные jobs, защита от публикации непроверенной ревизии; связь с F-006 |
| REL-02 | P2 | Версии / release notes | `pyproject.toml`, frontend/package, uv.lock, release tag, wheel, image и docs; объяснение hardened version scheme и реального состава релиза |
| REL-03 | P2 | Upstream workflows | Release guards, beta/release-please, metadata и docs jobs работают в контексте форка; intended skips отделены от ошибок |
| CI-01 | P1 | Current-head checks | Каждый uploaded SHA и attempt: обязательные checks, логи первичных failures, skipped/cancelled jobs, итоговый CI Required |
| CI-02 | P2 | Changes detection | Python/frontend/Rust/migrations/packaging changes включают нужные jobs; изменение workflows не создаёт ложный green |
| CI-03 | P2 | DB matrix | SQLite/PostgreSQL/MySQL/MariaDB: реальное покрытие, migration head/topology, upgrade/downgrade/backfill/drift; aliases типов не скрывают несовместимость |
| CI-04 | P2 | Flakes / isolation | Quarantine, session lifecycle, background loops, cache/durable state, xdist/shards; повторное прохождение после объяснения причины |
| CI-05 | P2 | Windows | Получить CI/локальные доказательства supported Windows startup и transport, включая F-008 |
| CI-06 | P2 | Browser / UI | До/после screenshots, viewport, browser smoke и реальные user flows; мок-тесты не заменяют запуск dashboard |
| DOC-01 | P2 | README | Название/назначение форка, поддерживаемые платформы, Quick Start, ссылки, badges, версии, ограничения; проверить README.md и README.zh-CN.md |
| DOC-02 | P2 | Заявления о качестве | Сравнение с upstream, «production/hardened», «100%», счётчики исправлений и OpenSpec: каждому утверждению соответствуют SHA и доказательства |
| DOC-03 | P2 | Документация | mkdocs/navigation, client setup, settings, deploy/update guides; рабочие ссылки на owning OpenSpec и отсутствие противоречащих инструкций |
| DOC-04 | P2 | Конфигурация | `.env.example`, precedence code < env < dashboard, tiers, encryption key, proxy routing; только существующие поля и проверенные примеры |
| DOC-05 | P2 | Обновление пользователей | COMMUNITY_RELEASE.md, FIXES-NOT-IN-v1.25.1.md, release assets и инструкции: что входит в каждый tag, совместимость и rollback |
| DOC-06 | P3 | Оформление GitHub | About/description, homepage, topics, package/release descriptions, default branch, badges, docs URL; правки GitHub — отдельное действие |
| DOC-07 | P3 | Авторство / лицензии | LICENSE, attribution, contributors, credits за перенесённые PR; различие собственной правки и интеграции community work |
| GOV-01 | P2 | OpenSpec | Behaviour-changing commits имеют change artifacts, нормативные specs и контекст; strict validation, verification перед archive |
| GOV-02 | P2 | Simplicity | README/env/nav/root budgets, конфигурационные tiers, архитектурные ratchets; необходимые исключения оформлены по правилам репозитория |
| GOV-03 | P2 | Git tracking | Разделение origin/fork, base SHA, upstream integrations/cherry-picks; 19 коммитов апстрима проверены на patch-equivalence, а не только на SHA |
| GOV-04 | P2 | PR readiness | Точные issue references, current-head CodeRabbit threads, check rollup, merge state, screenshots; отсутствие PR не означает выполненный review |
| GOV-05 | P2 | Реестр исходных claims | Сверить 108/110/164, категории, merged/superseded/discussions, дубли и «0 задач»; считать independently verified отдельно |
| GOV-06 | P2 | Этот новый root-файл | `issues-check.md` зарегистрирован локально в `[root_files].allowed` 2026-10-01; checker проходит на текущем HEAD, будущий tracked root tree проверяется после коммита |

## 5. Порядок работы с коммитами и исправлениями

1. Зафиксировать новый HEAD форка, исходную базу, dirty state и диапазон diff. Не путать чужие незакоммиченные изменения с проверяемым SHA.
2. Сначала проверить поставку: source SHA образов/пакетов, версии, Quick Start, update/rollback и правдивость описаний.
3. Разобрать обязательные CI failures: F-001/F-002, scoped compact, quarantine и MySQL. Исправление проверять и на исходном failing path, и на соседних transport paths.
4. Проверять исправления из исходного реестра по одной concern-группе: native egress → bridge/retries → continuity/compact → accounts/quota/OAuth → DB → compatibility → auth/logging → UI/metrics → features.
5. Для каждой интеграции community PR сопоставить исходный patch, фактический diff форка, adaptation, зависимости, tests и OpenSpec. Не делать вывод о переносе по одному commit title.
6. После исправляющего коммита повторить целевые тесты и получить current-head GitHub evidence. Широкий прогон нужен при широкой правке или признаках взаимодействия; маленькая правка не требует слепого запуска всей suite.
7. Перед выпуском проверить именно собранный артефакт и обновление существующей установки. Результат source tests не переносить автоматически на другой tag/digest.

### Инварианты при проверке кода

- Владелец файлов, `previous_response_id`, turn-state и API-key scope соблюдается при selection, retry, replay, compaction и forwarding.
- Reservations, usage settlement, account leases и terminal events завершаются ровно один раз; partial failure и disconnect не оставляют ресурсы или неоплаченный успешный fan-out.
- `AsyncSession` не разделяется между конкурентными задачами; данные не читаются из expired/detached объектов; spawned tasks отменяются/дожидаются на всех exit paths.
- Retry/timeout/capacity loops ограничены, excluded accounts действительно исключены; клиентский idle/disconnect не портит здоровье исправного аккаунта.
- Реальные публичные пути, aliases/trailing slash, error envelopes, schemas и config semantics совпадают с контрактом.
- Миграции сохраняют исторические строки и single-head lineage; docs не обещают behaviour, отсутствующее в runtime.

## 6. Очередь всех обращений из ISSUES.md

Очередь ниже сформирована из локального `ISSUES.md` на исходном HEAD. Все строки начинаются с **НЕ ПРОВЕРЕНО**: текущие зелёные тесты отдельных подсистем не закрывают автоматически все связанные issues. Найденные выше регрессии пока записаны как F-карточки; связывать их с конкретным upstream issue следует после установления связи.

В заголовках исходного файла найдено **155 отдельных карточек**. Дополнительно найдено **142 уникальных ссылки** на issues, PR и discussions, не являющиеся URL этих карточек: итого **297 уникальных ссылок**. Это число ссылок для проверки объёма, не число уникальных багов и не подтверждение исходного счётчика «164». Вспомогательные ссылки могут оказаться контекстом, дублем сценария или неподходящей задачей; это фиксируется явно.

Для строки с результатом создаём карточку по шаблону раздела 7 и указываем её ID в последнем столбце. Тип источника обязателен: issue и PR с одинаковым номером нельзя смешивать; номера относятся к `Soju06/codex-lb`.

<!-- source-queue:start -->

### Исходный раздел 1: Native Egress, Rust-движок и сетевой транспорт

| ID / источник | Заявленная тема | Исходный статус | Наша проверка | Карточка / исправляющий SHA |
|---|---|---|---|---|
| [UP-ISSUE-2471](https://github.com/Soju06/codex-lb/issues/2471) | bug(proxy): with upstream_stream_transport=http the native egress multiplexes every account's streams onto ONE shared HTTP/2 connection — one transport fa… | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2470](https://github.com/Soju06/codex-lb/issues/2470) | bug(proxy): direct-HTTP stream that dies with "Native upstream transport ended before a terminal event" never releases its account stream lease → per-acco… | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2456](https://github.com/Soju06/codex-lb/issues/2456) | bug(proxy): Windows transport errors bypass shared-client recovery | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2425](https://github.com/Soju06/codex-lb/issues/2425) | bug: input_image requests still fail ~35% during overload on beta.8 — the HTTP bridge bypass, not the upstream transport, is the cause (follow-up to #2363… | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2081](https://github.com/Soju06/codex-lb/issues/2081) | bug: direct websocket terminal failures lose transport and owner evidence | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1208](https://github.com/Soju06/codex-lb/issues/1208) | feat: Improve upstream transport parity and eliminate the easily identifiable codex-lb fingerprint | РЕШЕНО | НЕ ПРОВЕРЕНО | — |

### Исходный раздел 2: HTTP/WebSocket Bridge, стриминг, ретраи и сессии

| ID / источник | Заявленная тема | Исходный статус | Наша проверка | Карточка / исправляющий SHA |
|---|---|---|---|---|
| [UP-ISSUE-2493](https://github.com/Soju06/codex-lb/issues/2493) | bug: Beta.9 HTTP bridge can close native stream without terminal event after proxy-injected anchor rejection | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2465](https://github.com/Soju06/codex-lb/issues/2465) | bug: beta.9 sticky bridge lineages wedge permanently; image+tools path sends invalid parallel_tool_calls | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2455](https://github.com/Soju06/codex-lb/issues/2455) | bug(proxy): bridge payload bypass blocks verified quota failover | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2447](https://github.com/Soju06/codex-lb/issues/2447) | SQLite database is locked during login/OAuth under concurrent streaming load | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2409](https://github.com/Soju06/codex-lb/issues/2409) | bug(proxy): intermittent cache misses on Astra/SOL with the same Pro account across HTTP and WebSocket (195k–777k input) | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2389](https://github.com/Soju06/codex-lb/issues/2389) | bug(http-bridge): a model-transition fork rescues one turn, then re-derives the same owner conflict | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2388](https://github.com/Soju06/codex-lb/issues/2388) | bug(proxy): other HTTP-bridge local refusals still reach native Codex clients as an empty 200 | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2273](https://github.com/Soju06/codex-lb/issues/2273) | bug: incomplete responses can bypass bridge retry limits | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2272](https://github.com/Soju06/codex-lb/issues/2272) | bug: bridge retries can stay blocked after cooldown ends | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2271](https://github.com/Soju06/codex-lb/issues/2271) | bug: retry claims can stay locked after their owner exits | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2270](https://github.com/Soju06/codex-lb/issues/2270) | bug: retry cleanup can delete state changed by a newer request | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2268](https://github.com/Soju06/codex-lb/issues/2268) | bug: old bridge requests can clear a newer session's quarantine | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2266](https://github.com/Soju06/codex-lb/issues/2266) | bug: paused streams can keep growing worker memory | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2169](https://github.com/Soju06/codex-lb/issues/2169) | test: make native SSE fallback refusal fixture portable on macOS | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2108](https://github.com/Soju06/codex-lb/issues/2108) | bug: HTTP Responses logs omit observed upstream phase timings | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2090](https://github.com/Soju06/codex-lb/issues/2090) | fix(proxy): reconcile reservations after late HTTP-bridge anchor injection | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2074](https://github.com/Soju06/codex-lb/issues/2074) | bug: post-output frame-less bridge drops still penalize account health | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2033](https://github.com/Soju06/codex-lb/issues/2033) | proxy: a failing post-terminal health write emits a second terminal stream frame | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1935](https://github.com/Soju06/codex-lb/issues/1935) | feat: retry upstream model-capacity responses for Codex goals | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1898](https://github.com/Soju06/codex-lb/issues/1898) | fix(proxy): persist complete HTTP bridge replay transcripts | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1870](https://github.com/Soju06/codex-lb/issues/1870) | feat: add an upstream facet to dashboard request logs | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1799](https://github.com/Soju06/codex-lb/issues/1799) | bug: HTTP responses session bridge returns 503: "preserving an incompatible admission handoff" | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1758](https://github.com/Soju06/codex-lb/issues/1758) | http-bridge: evicting an inflight waiter does not cancel its creator, so multiple creators race one session key | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1711](https://github.com/Soju06/codex-lb/issues/1711) | WebSocket mid-turn interruptions regressed sharply in 1.23.0-beta.x vs 1.22.0 (new "scope cleanup exceeded its remaining drain budget" warning) | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1304](https://github.com/Soju06/codex-lb/issues/1304) | WebSocket clean-close handoff can consume a queued turn | РЕШЕНО | НЕ ПРОВЕРЕНО | — |

### Исходный раздел 3: Responses API, Context Compaction, якоря и `previous_response_id`

| ID / источник | Заявленная тема | Исходный статус | Наша проверка | Карточка / исправляющий SHA |
|---|---|---|---|---|
| [UP-ISSUE-2356](https://github.com/Soju06/codex-lb/issues/2356) | bug(proxy): experimental context management returns 405 for native notes v2 calls | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2318](https://github.com/Soju06/codex-lb/issues/2318) | feat(proxy): forward explicit compact requests to Responses model sources | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2269](https://github.com/Soju06/codex-lb/issues/2269) | bug: forwarded continuations can lose required conversation history | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1950](https://github.com/Soju06/codex-lb/issues/1950) | bug(compact): hosted computer screenshots can still hard-fail compaction and wedge image-heavy threads | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1942](https://github.com/Soju06/codex-lb/issues/1942) | bug: Regression: /v1/responses becomes unusable after upgrading from 1.22.0 to 1.24.0 (PR #1943) | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1921](https://github.com/Soju06/codex-lb/issues/1921) | bug: existing Codex threads repeatedly fail with invalid previous_response_id | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1895](https://github.com/Soju06/codex-lb/issues/1895) | bug(warmup): /v1/warmup fails with 404 (compact payload) and account probe fails with 400 (max_output_tokens=1) — windows cannot be auto-started | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-986](https://github.com/Soju06/codex-lb/issues/986) | feat: optional sticky account switchover only after compaction boundary | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-568](https://github.com/Soju06/codex-lb/issues/568) | follow-up: side effects of response.create history slimming (#560) | РЕШЕНО | НЕ ПРОВЕРЕНО | — |

### Исходный раздел 4: Управление аккаунтами, OAuth, квоты, лимиты и Warmup

| ID / источник | Заявленная тема | Исходный статус | Наша проверка | Карточка / исправляющий SHA |
|---|---|---|---|---|
| [UP-ISSUE-2442](https://github.com/Soju06/codex-lb/issues/2442) | bug(proxy): early token_expired reauth account poisons fresh Codex HTTP routing | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2426](https://github.com/Soju06/codex-lb/issues/2426) | bug(metrics): populate account counts and expose availability for alerting | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2420](https://github.com/Soju06/codex-lb/issues/2420) | bug(accounts): Hard-coded Pro and Pro Lite credit capacities disagree with observed quota consumption, distorting pooled credit reporting | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2413](https://github.com/Soju06/codex-lb/issues/2413) | feat: Luna Reserve (gpt-reserve) fallback when chat quota is exhausted | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2327](https://github.com/Soju06/codex-lb/issues/2327) | fix(accounts): recover stale holds after verified matching operator probes | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2288](https://github.com/Soju06/codex-lb/issues/2288) | feat: pool reset credits across accounts in Codex Desktop | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2285](https://github.com/Soju06/codex-lb/issues/2285) | feat: show pooled quota in Codex Desktop while staying signed in | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2274](https://github.com/Soju06/codex-lb/issues/2274) | bug: continuations can be routed to the wrong account | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2076](https://github.com/Soju06/codex-lb/issues/2076) | bug: default Docker port 1455 mapping can intercept Codex Desktop OAuth callbacks | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2064](https://github.com/Soju06/codex-lb/issues/2064) | bug(proxy): revoked access tokens repeatedly re-enter reauth routing | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1976](https://github.com/Soju06/codex-lb/issues/1976) | bug(warmup): staggered idle slots can be unreachable for sliding reset_at | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1946](https://github.com/Soju06/codex-lb/issues/1946) | UI account section bug | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1918](https://github.com/Soju06/codex-lb/issues/1918) | bug: codex-lb incorrectly calculates usage for edu accounts | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1793](https://github.com/Soju06/codex-lb/issues/1793) | feat: weekly limits estimation in $ | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1708](https://github.com/Soju06/codex-lb/issues/1708) | ux/docs: make routing, sticky affinity, quota thresholds, warm-up, and account eligibility understandable in the dashboard | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1632](https://github.com/Soju06/codex-lb/issues/1632) | feat: support model sources via model_catalog_json for ChatGPT OAuth users | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1576](https://github.com/Soju06/codex-lb/issues/1576) | feat: add strict model-to-ChatGPT OAuth account routing | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1415](https://github.com/Soju06/codex-lb/issues/1415) | perf(balancer): optimize low-TTFT routing for large account pools under bursts | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1413](https://github.com/Soju06/codex-lb/issues/1413) | feat(accounts): support explicit access-token-only credential imports | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1367](https://github.com/Soju06/codex-lb/issues/1367) | bug(accounts): Team 30d quota is displayed as 5h | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1340](https://github.com/Soju06/codex-lb/issues/1340) | Simplicity backlog: settings-surface reduction (164 → ~110 fields) & deferred follow-ups | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1130](https://github.com/Soju06/codex-lb/issues/1130) | feat: support for (personal) access token accounts (for business/enterprise) | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-850](https://github.com/Soju06/codex-lb/issues/850) | (Feature) Full Account Backup & Restore | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-631](https://github.com/Soju06/codex-lb/issues/631) | Account limit restriction | РЕШЕНО | НЕ ПРОВЕРЕНО | — |

### Исходный раздел 5: База данных (SQLite / PostgreSQL), локи и производительность

| ID / источник | Заявленная тема | Исходный статус | Наша проверка | Карточка / исправляющий SHA |
|---|---|---|---|---|
| [UP-ISSUE-2483](https://github.com/Soju06/codex-lb/issues/2483) | perf(usage): high memory usage and query latency in bulk history reads on SQLite | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2474](https://github.com/Soju06/codex-lb/issues/2474) | Migration graph forks into two heads on main (MultipleHeads): 20260914_000000 collision (#2431 vs #2422) | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2292](https://github.com/Soju06/codex-lb/issues/2292) | feat(db): gate PostgreSQL-only support on a verified SQLite migration path | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2034](https://github.com/Soju06/codex-lb/issues/2034) | bug: single-loop SQLite deployment turns Codex Desktop HTTP fallback into a 20 s first token (5 s over ws) plus ~2 s fixed overhead per turn | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1981](https://github.com/Soju06/codex-lb/issues/1981) | bug: wedged-teardown interrupt fails with "Cannot operate on a closed database", then the process holds the SQLite write lock permanently (55 min of datab… | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1949](https://github.com/Soju06/codex-lb/issues/1949) | bug: encryption-key fingerprint stamp flakes CI on SQLite lock contention | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1682](https://github.com/Soju06/codex-lb/issues/1682) | bug: leader lease loss on single-instance SQLite causes a self-sustaining 17-minute `database is locked` stall that blocks leader re-election | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1471](https://github.com/Soju06/codex-lb/issues/1471) | ci(db): gate long-running migrations with a production-scale duration check | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1470](https://github.com/Soju06/codex-lb/issues/1470) | feat(db): make data-backfill migrations non-blocking, resumable, and observable | РЕШЕНО | НЕ ПРОВЕРЕНО | — |

### Исходный раздел 6: Совместимость с клиентами, роутинг моделей и порты

| ID / источник | Заявленная тема | Исходный статус | Наша проверка | Карточка / исправляющий SHA |
|---|---|---|---|---|
| [UP-ISSUE-2302](https://github.com/Soju06/codex-lb/issues/2302) | fix(a11y): name model-source capability checkboxes | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2290](https://github.com/Soju06/codex-lb/issues/2290) | feat(model-sources): discover CLIProxyAPI catalogs and retain unavailable ownership | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2128](https://github.com/Soju06/codex-lb/issues/2128) | bug(proxy): standalone web search fails on v1 and duplicates native Content-Type | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1467](https://github.com/Soju06/codex-lb/issues/1467) | bug: gpt-5.3-codex-spark works on Pro but is missing from /v1/models | РЕШЕНО | НЕ ПРОВЕРЕНО | — |

### Исходный раздел 7: Безопасность, шифрование, логирование и телеметрия

| ID / источник | Заявленная тема | Исходный статус | Наша проверка | Карточка / исправляющий SHA |
|---|---|---|---|---|
| [UP-ISSUE-2028](https://github.com/Soju06/codex-lb/issues/2028) | fix(logging): shared log-redaction patterns leave credential tails for auth-param lists, quoted keys, and whitespace-separated tokens | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1844](https://github.com/Soju06/codex-lb/issues/1844) | Telemetry opt-out: close the consent/send race and follow-up hardening | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1843](https://github.com/Soju06/codex-lb/issues/1843) | bug: telemetry client type is wrong | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1572](https://github.com/Soju06/codex-lb/issues/1572) | feat: support CODEX_LB_ENCRYPTION_KEY for stateless replicas | РЕШЕНО | НЕ ПРОВЕРЕНО | — |

### Исходный раздел 8: Dashboard, UI и Prometheus метрики

| ID / источник | Заявленная тема | Исходный статус | Наша проверка | Карточка / исправляющий SHA |
|---|---|---|---|---|
| [UP-ISSUE-2492](https://github.com/Soju06/codex-lb/issues/2492) | feat: Reset API key limit usage from dashboard without regenerating keys | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2443](https://github.com/Soju06/codex-lb/issues/2443) | bug(metrics): dashboard/report TPS uses post-settlement latency and reasoning-inclusive TTFT | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2418](https://github.com/Soju06/codex-lb/issues/2418) | bug(frontend): Apple Passwords TOTP autofill does not populate Chrome verification dialog | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2309](https://github.com/Soju06/codex-lb/issues/2309) | docs: align agent instructions with Astra prompt guidance | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2262](https://github.com/Soju06/codex-lb/issues/2262) | feat(proxy): preserve built-in OpenAI provider when routing ChatGPT-authenticated Codex Desktop through codex-lb | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2038](https://github.com/Soju06/codex-lb/issues/2038) | Visual Studio Copilot requires GET /v1/models/{model_id} | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1901](https://github.com/Soju06/codex-lb/issues/1901) | bug(reports): /api/reports takes ~120 s for a 7-day window (~543k rows) while equivalent raw SQL finishes in ~2.5 s | РЕШЕНО | НЕ ПРОВЕРЕНО | — |

### Исходный раздел 9: Предложения пользователей и фичи (Feature Requests / RFC)

| ID / источник | Заявленная тема | Исходный статус | Наша проверка | Карточка / исправляющий SHA |
|---|---|---|---|---|
| [UP-ISSUE-2343](https://github.com/Soju06/codex-lb/issues/2343) | feat(health): expose request-persistence ownership during drain | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2304](https://github.com/Soju06/codex-lb/issues/2304) | feat(images): support GPT Image 2.5 Flare and Sunburst in the Images API | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1979](https://github.com/Soju06/codex-lb/issues/1979) | feat(automations): add an opt-in verified weekly-window prestart preset | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1959](https://github.com/Soju06/codex-lb/issues/1959) | feat: Would you be interested in an optional auto re-login feature? | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1636](https://github.com/Soju06/codex-lb/issues/1636) | Add safe targeted Codex session metadata repair | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1595](https://github.com/Soju06/codex-lb/issues/1595) | feat: try fuzzing for testing | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1307](https://github.com/Soju06/codex-lb/issues/1307) | feat: subagent prompt-cache affinity TTL | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1080](https://github.com/Soju06/codex-lb/issues/1080) | feat: add configurable longer observation windows for API key usage | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-956](https://github.com/Soju06/codex-lb/issues/956) | feat: pace-aware throttling to land exactly on reset boundaries | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-620](https://github.com/Soju06/codex-lb/issues/620) | Complete deferred Images API fan-out and observability tasks | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-578](https://github.com/Soju06/codex-lb/issues/578) | (design) Reconsider budget-safe routing gate vs health-tier overlap and per-window thresholds | РЕШЕНО | НЕ ПРОВЕРЕНО | — |

### Исходный раздел 10: Прочие ошибки и регрессии

| ID / источник | Заявленная тема | Исходный статус | Наша проверка | Карточка / исправляющий SHA |
|---|---|---|---|---|
| [UP-ISSUE-2410](https://github.com/Soju06/codex-lb/issues/2410) | bug: Force Probe sends unsupported payload fields and can fail to settle successful probes | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2314](https://github.com/Soju06/codex-lb/issues/2314) | ci: reconcile issue and PR status-label ownership and lifecycle | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2311](https://github.com/Soju06/codex-lb/issues/2311) | docs: use GPT-6 Astra in current client examples | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2291](https://github.com/Soju06/codex-lb/issues/2291) | bug: queued transcript batches wait between flushes | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2029](https://github.com/Soju06/codex-lb/issues/2029) | bug: historical minute-long Codex LB stalls and event-loop starvation remain unresolved | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1924](https://github.com/Soju06/codex-lb/issues/1924) | bug(proxy): inline-image 429 can prevent prompt-cache failover | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1707](https://github.com/Soju06/codex-lb/issues/1707) | bug: existing Codex thread can remain unusable on dead hard-affinity owner while fresh/side chat works | РЕШЕНО | НЕ ПРОВЕРЕНО | — |

### Исходный раздел 14: Новые проблемы, баги, предложения и Pull Requests из оригинального репозитория (Upstream #2497–#2537)

| ID / источник | Заявленная тема | Исходный статус | Наша проверка | Карточка / исправляющий SHA |
|---|---|---|---|---|
| [UP-PR-2497](https://github.com/Soju06/codex-lb/pull/2497) | feat(accounts): show reset credits for paused accounts | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2498](https://github.com/Soju06/codex-lb/issues/2498) | docs: add `supports_standalone_web_search` to the Codex provider example | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2499](https://github.com/Soju06/codex-lb/issues/2499) | bug(model-sources): multi-agent capability does not preserve client collaboration tools | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2500](https://github.com/Soju06/codex-lb/issues/2500) | bug: #1968 shield-loop livelock still ships in latest stable 1.24.0; please cut a stable patch with #1969 | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2501](https://github.com/Soju06/codex-lb/issues/2501) | bug: native HTTP upstream regressed in 1.25.0-beta.7 with native upstream request failures | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2502](https://github.com/Soju06/codex-lb/pull/2502) | MySQL / MariaDB support | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2503](https://github.com/Soju06/codex-lb/pull/2503) | fix(http-bridge): keep replayed history images on the bridge | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2504](https://github.com/Soju06/codex-lb/pull/2504) | fix(usage): account for cache-write tokens | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2505](https://github.com/Soju06/codex-lb/issues/2505) | bug: shutdown cancels schedulers and the leader-lease keeper mid-DB-work (SQLite pool CancelledError, unreleased lease, unclean run-state) | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2506](https://github.com/Soju06/codex-lb/pull/2506) | fix(shutdown): let DB-owning background tasks finish before cancelling them | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2507](https://github.com/Soju06/codex-lb/pull/2507) | feat(cli): add --log-level and --log-file; stop the metrics server resetting logging | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2508](https://github.com/Soju06/codex-lb/pull/2508) | fix(proxy): reuse bridge sessions for inline images | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2509](https://github.com/Soju06/codex-lb/pull/2509) | chore(deps): bump the frontend-minor-patch group across 1 directory with 16 updates | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2510](https://github.com/Soju06/codex-lb/pull/2510) | chore(deps): bump the python-minor-patch group across 1 directory with 11 updates | MERGED/CLOSED | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2511](https://github.com/Soju06/codex-lb/issues/2511) | bug(accounts): self_serve_business_prolite usage plan is rejected as unknown | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2512](https://github.com/Soju06/codex-lb/pull/2512) | fix(accounts): normalize business prolite plan alias | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2513](https://github.com/Soju06/codex-lb/pull/2513) | fix(proxy): send a single Content-Type on codex control requests | MERGED/CLOSED | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2514](https://github.com/Soju06/codex-lb/issues/2514) | feat(accounts): redeem all eligible reset credits in one action | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2515](https://github.com/Soju06/codex-lb/pull/2515) | fix(chat): keep the JSON instruction in input for json_object requests | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2516](https://github.com/Soju06/codex-lb/pull/2516) | docs: declare native web search support in Codex examples | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2517](https://github.com/Soju06/codex-lb/pull/2517) | fix(telemetry): map codex_cli_rs user agent to codex-cli family | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2518](https://github.com/Soju06/codex-lb/pull/2518) | test(db): cover the SCIM/overflow merge revision's single-head convergence | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2519](https://github.com/Soju06/codex-lb/pull/2519) | fix(http-bridge): parse multi-line upstream websocket frames | RESOLVED / SUPERSEDED BY #2530 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2520](https://github.com/Soju06/codex-lb/pull/2520) | refactor(proxy): extract streaming response entrypoint | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2521](https://github.com/Soju06/codex-lb/pull/2521) | fix(model-sources): validate optional usage and preserve streamed telemetry | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2522](https://github.com/Soju06/codex-lb/pull/2522) | perf(db): request_logs facet indexes and loose-scan probes (stacked on #2502) | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2523](https://github.com/Soju06/codex-lb/pull/2523) | fix(metrics): publish fresh account pool gauges on scrape | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2524](https://github.com/Soju06/codex-lb/pull/2524) | fix(accounts): snapshot force probe state before session cleanup | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2525](https://github.com/Soju06/codex-lb/pull/2525) | fix(model-sources): preserve source base instructions in catalogs | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2526](https://github.com/Soju06/codex-lb/pull/2526) | fix(model-sources): preserve declared collaboration namespaces | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2527](https://github.com/Soju06/codex-lb/pull/2527) | fix(routing): recover weekly-only Pro reserve accounts | MERGED/CLOSED | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2528](https://github.com/Soju06/codex-lb/pull/2528) | fix(proxy): advertise GPT-6 max output tokens | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2529](https://github.com/Soju06/codex-lb/pull/2529) | fix(metrics): stop the metrics server from reconfiguring process logging | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2530](https://github.com/Soju06/codex-lb/pull/2530) | fix(http-bridge): parse multiline websocket JSON messages | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2531](https://github.com/Soju06/codex-lb/pull/2531) | fix(proxy): normalize parallel_tool_calls for Responses-Lite upstream | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2532](https://github.com/Soju06/codex-lb/pull/2532) | chore(docker): bump rust from 1.96.0-slim-bookworm to 1.98.1-slim-bookworm | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2533](https://github.com/Soju06/codex-lb/pull/2533) | chore(deps): bump the python-minor-patch group across 1 directory with 17 updates | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2534](https://github.com/Soju06/codex-lb/pull/2534) | feat(proxy): admit bounded inline images on the HTTP responses bridge | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2535](https://github.com/Soju06/codex-lb/issues/2535) | feat: show pooled quota in Codex /status by serving and forwarding /backend-api calls | MERGED/CLOSED | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2536](https://github.com/Soju06/codex-lb/pull/2536) | feat(proxy): show pooled quota in Codex /status by serving and forwarding /backend-api calls | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2537](https://github.com/Soju06/codex-lb/pull/2537) | fix(images): route image requests through compatible host | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2538](https://github.com/Soju06/codex-lb/issues/2538) | bug(http-bridge): upstream error responses silently swallowed as timeouts - pretty JSON parsing + Responses-Lite parallel_tool_calls | РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2539](https://github.com/Soju06/codex-lb/pull/2539) | fix(proxy): treat websocket close 1009 as terminal payload_too_large | РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2540](https://github.com/Soju06/codex-lb/pull/2540) | fix(quota): reject invalid planner clock times | РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2541](https://github.com/Soju06/codex-lb/pull/2541) | fix(scim): enforce body limits while reading the stream | РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2542](https://github.com/Soju06/codex-lb/pull/2542) | test(shutdown): override the current account import permission | РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2543](https://github.com/Soju06/codex-lb/pull/2543) | docs(codex): enable API-key model discovery in setup examples | РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2544](https://github.com/Soju06/codex-lb/pull/2544) | chore(metadata): refresh model pricing and Codex version | РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2545](https://github.com/Soju06/codex-lb/pull/2545) | fix(cache): retain failed immediate invalidations | РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ | НЕ ПРОВЕРЕНО | — |

### Связанные issues: дополнительные ссылки (5)

| ID / источник | Тема или роль ссылки | Место в ISSUES.md | Наша проверка | Карточка / исправляющий SHA |
|---|---|---|---|---|
| [UP-ISSUE-2068](https://github.com/Soju06/codex-lb/issues/2068) | #2068 / PR #2398: bug(proxy): quota failover stalls unanchored full-resend threads | Раздел 3, L418 | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1975](https://github.com/Soju06/codex-lb/issues/1975) | #1975 / PR #2326: bug(warmup): live usage ingestion can consume reset evidence without invoking limit warm-up | Раздел 4, L606 | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1132](https://github.com/Soju06/codex-lb/issues/1132) | Связанная ссылка; установить роль и связь с исправлением | Раздел 4, L622 | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-1919](https://github.com/Soju06/codex-lb/issues/1919) | #1919 / PR #2429: bug: Need to reauthenticate accounts with Advanced Account Security every single day | Раздел 4, L624 | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-446](https://github.com/Soju06/codex-lb/issues/446) | Связанная ссылка; установить роль и связь с исправлением | Раздел 9, L1114 | НЕ ПРОВЕРЕНО | — |

### Связанные Pull Requests: дополнительные ссылки (88)

| ID / источник | Тема или роль ссылки | Место в ISSUES.md | Наша проверка | Карточка / исправляющий SHA |
|---|---|---|---|---|
| [UP-PR-2449](https://github.com/Soju06/codex-lb/pull/2449) | PR #2449: fix(proxy): read the usage-limit rejection off the frame upstream actually sends | Раздел 2, L145 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2430](https://github.com/Soju06/codex-lb/pull/2430) | PR #2430: feat(proxy): add transcript core storage | Раздел 2, L151 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2391](https://github.com/Soju06/codex-lb/pull/2391) | PR #2391: feat(proxy): shape the failover decision around the pool and render its terminal | Раздел 2, L157 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2403](https://github.com/Soju06/codex-lb/pull/2403) | PR #2403: feat(proxy): classify usage-limit rejections and answer pool-walk exclusion | Раздел 2, L163 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2440](https://github.com/Soju06/codex-lb/pull/2440) | PR #2440: fix(proxy): preserve upstream reset metadata in retry health | Раздел 2, L169 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2439](https://github.com/Soju06/codex-lb/pull/2439) | PR #2439: fix(proxy): preserve upstream quota reset metadata on terminal errors | Раздел 2, L175 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2423](https://github.com/Soju06/codex-lb/pull/2423) | PR #2423 / #1921: fix(proxy): reject a dead client anchor instead of asking for a retry | Раздел 2, L181 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2332](https://github.com/Soju06/codex-lb/pull/2332) | PR #2332: fix(proxy): fail over account-local model rejection | Раздел 3, L427 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2469](https://github.com/Soju06/codex-lb/pull/2469) | PR #2469: fix(proxy): preserve routed file failover provenance | Раздел 3, L451 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2451](https://github.com/Soju06/codex-lb/pull/2451) | PR #2451: fix(proxy): refuse remote compaction for model-source models before account selection | Раздел 3, L457 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2468](https://github.com/Soju06/codex-lb/pull/2468) | PR #2468: fix(quota): validate planner timezones and tolerate legacy malformed keys | Раздел 4, L514 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2117](https://github.com/Soju06/codex-lb/pull/2117) | PR #2117: fix(proxy): retire revoked routing within budget | Раздел 4, L736 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2484](https://github.com/Soju06/codex-lb/pull/2484) | PR #2484: perf(usage): cap SQLite bulk usage history reads per account | Раздел 5, L754 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2460](https://github.com/Soju06/codex-lb/pull/2460) | PR #2460: fix(dashboard-users): take the owner row before the owned-key cascade reads it | Раздел 5, L773 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-421](https://github.com/Soju06/codex-lb/pull/421) | Связанная ссылка; установить роль и связь с исправлением | Раздел 9, L1114 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-561](https://github.com/Soju06/codex-lb/pull/561) | Связанная ссылка; установить роль и связь с исправлением | Раздел 9, L1114 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2490](https://github.com/Soju06/codex-lb/pull/2490) | PR #2490: fix(auth): add secret-safe refresh failure diagnostics | Раздел 12, L1347 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2489](https://github.com/Soju06/codex-lb/pull/2489) | PR #2489: fix(accounts): preserve quota chart samples and account display state | Раздел 12, L1348 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2488](https://github.com/Soju06/codex-lb/pull/2488) | PR #2488: fix(proxy): handle CRLF and malformed UTF-8 in owner forwarding | Раздел 12, L1349 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2487](https://github.com/Soju06/codex-lb/pull/2487) | PR #2487: fix(auth): reject non-ASCII TOTP digits safely | Раздел 12, L1350 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2486](https://github.com/Soju06/codex-lb/pull/2486) | PR #2486: fix(balancer): admit a hard continuity owner serving its own transient backoff | Раздел 12, L1351 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2473](https://github.com/Soju06/codex-lb/pull/2473) | PR #2473: feat(proxy): add gpt-reserve as an operator-enabled Luna Reserve model | Раздел 12, L1353 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2472](https://github.com/Soju06/codex-lb/pull/2472) | PR #2472: fix(proxy): surface native transport give-up terminals | Раздел 12, L1354 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2467](https://github.com/Soju06/codex-lb/pull/2467) | PR #2467: fix(proxy-responses): retire tombstoned injected anchors | Раздел 12, L1357 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2464](https://github.com/Soju06/codex-lb/pull/2464) | PR #2464: feat(ui): add compact and fullscreen dashboard account views | Раздел 12, L1358 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2463](https://github.com/Soju06/codex-lb/pull/2463) | PR #2463: feat(api-keys): add estimated usage-share limits | Раздел 12, L1359 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2462](https://github.com/Soju06/codex-lb/pull/2462) | PR #2462: fix(db): repair September migration lineage | Раздел 12, L1360 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2461](https://github.com/Soju06/codex-lb/pull/2461) | PR #2461: fix(db): converge the SCIM token and subscription-overflow heads | Раздел 12, L1361 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2458](https://github.com/Soju06/codex-lb/pull/2458) | PR #2458: fix(proxy): recover bridge-bypassed quota failover | Раздел 12, L1363 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2457](https://github.com/Soju06/codex-lb/pull/2457) | PR #2457: fix(proxy): recover Windows transport failures | Раздел 12, L1364 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2448](https://github.com/Soju06/codex-lb/pull/2448) | PR #2448: feat(proxy): diversify subagents from parent accounts | Раздел 12, L1366 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2446](https://github.com/Soju06/codex-lb/pull/2446) | PR #2446: fix(rust): upgrade rustls past RUSTSEC-2026-0285 | Раздел 12, L1367 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2445](https://github.com/Soju06/codex-lb/pull/2445) | PR #2445: feat(proxy): forward the Codex plugin catalog upstream so chatgpt_base_url can point at codex-lb | Раздел 12, L1368 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2444](https://github.com/Soju06/codex-lb/pull/2444) | PR #2444: fix(metrics): separate observed generation timing from request latency | Раздел 12, L1369 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2429](https://github.com/Soju06/codex-lb/pull/2429) | PR #2429: fix(auth): reuse shared refresh policy in guardian | Раздел 12, L1373 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2428](https://github.com/Soju06/codex-lb/pull/2428) | PR #2428: feat(proxy): decide relocation once, and rebuild a conversation from the durable spool | Раздел 12, L1374 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2398](https://github.com/Soju06/codex-lb/pull/2398) | PR #2398: fix(proxy): prepare portable WebSocket full resends for quota replay | Раздел 12, L1377 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2377](https://github.com/Soju06/codex-lb/pull/2377) | PR #2377: fix(dashboard): calm the telemetry consent dialog | Раздел 12, L1379 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2345](https://github.com/Soju06/codex-lb/pull/2345) | PR #2345: fix(proxy): preserve local quarantine evidence during completion | Раздел 12, L1380 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2344](https://github.com/Soju06/codex-lb/pull/2344) | PR #2344: feat(health): expose request-persistence ownership during drain | Раздел 12, L1381 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2326](https://github.com/Soju06/codex-lb/pull/2326) | PR #2326: fix(warmup): preserve live reset evidence across skipped polls | Раздел 12, L1383 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2325](https://github.com/Soju06/codex-lb/pull/2325) | PR #2325: feat(cli): bound whole-home retag planning and report progress | Раздел 12, L1384 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2324](https://github.com/Soju06/codex-lb/pull/2324) | PR #2324: feat(proxy): forward explicit compact requests to model sources | Раздел 12, L1385 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2323](https://github.com/Soju06/codex-lb/pull/2323) | PR #2323: feat(cli): add targeted session metadata preview and repair | Раздел 12, L1386 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2322](https://github.com/Soju06/codex-lb/pull/2322) | PR #2322: feat(db): explain guarded migration recovery stamping | Раздел 12, L1387 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2321](https://github.com/Soju06/codex-lb/pull/2321) | PR #2321: fix(accounts): preserve observed monthly quota across plans | Раздел 12, L1388 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2319](https://github.com/Soju06/codex-lb/pull/2319) | PR #2319: fix(proxy): contain post-terminal health write failures | Раздел 12, L1389 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2317](https://github.com/Soju06/codex-lb/pull/2317) | PR #2317: fix(proxy): align compact budget with responses stream | Раздел 12, L1390 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2308](https://github.com/Soju06/codex-lb/pull/2308) | PR #2308: fix(proxy): project pooled quotas into Codex rate-limit events | Раздел 12, L1391 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2307](https://github.com/Soju06/codex-lb/pull/2307) | PR #2307: feat(db): log per-revision migration progress | Раздел 12, L1392 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2305](https://github.com/Soju06/codex-lb/pull/2305) | PR #2305: feat(model-sources): discover CPA catalogs and retain unavailable ownership | Раздел 12, L1393 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2303](https://github.com/Soju06/codex-lb/pull/2303) | PR #2303: perf(http-bridge): drain queued transcript batches without interval waits | Раздел 12, L1394 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2294](https://github.com/Soju06/codex-lb/pull/2294) | PR #2294: feat(telemetry): expand anonymous telemetry to schema v2 with summable day aggregates and histograms | Раздел 12, L1395 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2280](https://github.com/Soju06/codex-lb/pull/2280) | PR #2280: fix(proxy): preserve newer retry state during scheduled cleanup | Раздел 12, L1396 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2278](https://github.com/Soju06/codex-lb/pull/2278) | PR #2278: fix(proxy): count incomplete responses toward bridge retries | Раздел 12, L1397 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2277](https://github.com/Soju06/codex-lb/pull/2277) | PR #2277: fix(proxy): preserve continuation anchors during input normalization | Раздел 12, L1398 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2276](https://github.com/Soju06/codex-lb/pull/2276) | PR #2276: fix(proxy): preserve newer quarantine during response cleanup | Раздел 12, L1399 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2255](https://github.com/Soju06/codex-lb/pull/2255) | PR #2255: fix(shutdown): deny WebSocket upgrades during drain with 503 instead of a pre-handshake close | Раздел 12, L1401 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2146](https://github.com/Soju06/codex-lb/pull/2146) | PR #2146: feat(dashboard): add request heatmap on dashboard | Раздел 12, L1402 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2133](https://github.com/Soju06/codex-lb/pull/2133) | PR #2133: fix(proxy): isolate bridge heartbeat from maintenance | Раздел 12, L1403 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2132](https://github.com/Soju06/codex-lb/pull/2132) | PR #2132: fix(auth): retain access rejection through late health updates | Раздел 12, L1404 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2122](https://github.com/Soju06/codex-lb/pull/2122) | PR #2122: fix(warmup): restore reset usage threshold | Раздел 12, L1405 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2121](https://github.com/Soju06/codex-lb/pull/2121) | PR #2121: fix(proxy): recover tool-complete goal followups from unavailable owners | Раздел 12, L1406 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2120](https://github.com/Soju06/codex-lb/pull/2120) | PR #2120: fix(auth): retain unexpired access on refresh preflight failure | Раздел 12, L1407 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2119](https://github.com/Soju06/codex-lb/pull/2119) | PR #2119: fix(accounts): require spendable credits for quota override | Раздел 12, L1408 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2118](https://github.com/Soju06/codex-lb/pull/2118) | PR #2118: feat(ui): add Japanese dashboard localization | Раздел 12, L1409 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2115](https://github.com/Soju06/codex-lb/pull/2115) | PR #2115: feat(proxy): support Astra steering with transport-owned dispatch | Раздел 12, L1411 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2112](https://github.com/Soju06/codex-lb/pull/2112) | PR #2112: fix(observability): record HTTP upstream phase timings | Раздел 12, L1412 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2102](https://github.com/Soju06/codex-lb/pull/2102) | PR #2102: feat(proxy): support Codex history and notes across account pools | Раздел 12, L1413 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2101](https://github.com/Soju06/codex-lb/pull/2101) | PR #2101: fix(proxy): add native history and notes routes with account-local ownership | Раздел 12, L1414 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2099](https://github.com/Soju06/codex-lb/pull/2099) | PR #2099: feat(proxy): preserve async tool results across continuations | Раздел 12, L1415 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2098](https://github.com/Soju06/codex-lb/pull/2098) | PR #2098: fix(docker): isolate host OAuth callback port by default | Раздел 12, L1416 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2097](https://github.com/Soju06/codex-lb/pull/2097) | PR #2097: feat(proxy): enforce Astra configuration-update policy | Раздел 12, L1417 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2088](https://github.com/Soju06/codex-lb/pull/2088) | PR #2088: fix(http-bridge): retain draining owners through safe recovery | Раздел 12, L1418 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2085](https://github.com/Soju06/codex-lb/pull/2085) | PR #2085: feat(models): add gpt-6 astra catalog support | Раздел 12, L1419 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2075](https://github.com/Soju06/codex-lb/pull/2075) | PR #2075: fix(proxy): keep frameless bridge drops account neutral | Раздел 12, L1420 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2069](https://github.com/Soju06/codex-lb/pull/2069) | PR #2069: fix(proxy): recover unanchored quota replay | Раздел 12, L1421 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2065](https://github.com/Soju06/codex-lb/pull/2065) | PR #2065: Feature/multi file account import | Раздел 12, L1422 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2048](https://github.com/Soju06/codex-lb/pull/2048) | PR #2048: fix(proxy): preserve exhausted sticky failover | Раздел 12, L1423 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2001](https://github.com/Soju06/codex-lb/pull/2001) | PR #2001: fix(proxy): release payload owner after pre-visible quota rejection | Раздел 12, L1424 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-1962](https://github.com/Soju06/codex-lb/pull/1962) | PR #1962: fix(proxy): preserve half-open probe ownership during cleanup | Раздел 12, L1425 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-1952](https://github.com/Soju06/codex-lb/pull/1952) | PR #1952: fix(proxy): preserve tool search pairs through replay | Раздел 12, L1426 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-1938](https://github.com/Soju06/codex-lb/pull/1938) | PR #1938: feat(accounts): add encrypted portable account bundles | Раздел 12, L1427 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-1932](https://github.com/Soju06/codex-lb/pull/1932) | PR #1932: feat(db): add safe SQLite compaction | Раздел 12, L1428 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-1905](https://github.com/Soju06/codex-lb/pull/1905) | PR #1905: fix(proxy): preserve continuation ownership across source routing | Раздел 12, L1429 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-1903](https://github.com/Soju06/codex-lb/pull/1903) | PR #1903: fix(proxy): bound memory used by paused bridge streams | Раздел 12, L1430 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-1528](https://github.com/Soju06/codex-lb/pull/1528) | PR #1528: feat(accounts): add per-account usage limits | Раздел 12, L1431 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-1084](https://github.com/Soju06/codex-lb/pull/1084) | PR #1084: fix(proxy): fail fast on locally-generated retry hint in capacity-wait loop | Раздел 12, L1432 | НЕ ПРОВЕРЕНО | — |

### Обсуждения и предложения: дополнительные ссылки (49)

| ID / источник | Тема или роль ссылки | Место в ISSUES.md | Наша проверка | Карточка / исправляющий SHA |
|---|---|---|---|---|
| [UP-DISC-1920](https://github.com/Soju06/codex-lb/discussions/1920) | #1920: ARCHIVE THE REPO!. this project is dogshit i disabled it all and stopped using it way better other options all ai slop code | Раздел 11, L1192 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-1104](https://github.com/Soju06/codex-lb/discussions/1104) | #1104: Caching | Раздел 11, L1195 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-1894](https://github.com/Soju06/codex-lb/discussions/1894) | #1894: Why is the reporting so SLOW? | Раздел 11, L1198 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-1551](https://github.com/Soju06/codex-lb/discussions/1551) | #1551: Price estimate bug? | Раздел 11, L1201 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-1320](https://github.com/Soju06/codex-lb/discussions/1320) | #1320: Reset Limits | Раздел 11, L1204 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-1136](https://github.com/Soju06/codex-lb/discussions/1136) | #1136: Configure openai_base_url for Remote Codex CLI Sessions | Раздел 11, L1207 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-1134](https://github.com/Soju06/codex-lb/discussions/1134) | #1134: The Codex App does not automatically clean up the context. | Раздел 11, L1210 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-790](https://github.com/Soju06/codex-lb/discussions/790) | #790: all account deactivated all the sudden | Раздел 11, L1213 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-1012](https://github.com/Soju06/codex-lb/discussions/1012) | #1012: 2FA Autofill | Раздел 11, L1216 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-959](https://github.com/Soju06/codex-lb/discussions/959) | #959: Business workspace with shared budget | Раздел 11, L1219 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-791](https://github.com/Soju06/codex-lb/discussions/791) | #791: PI harness | Раздел 11, L1222 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-536](https://github.com/Soju06/codex-lb/discussions/536) | #536: Figma connection lost when using Codex LB | Раздел 11, L1225 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-352](https://github.com/Soju06/codex-lb/discussions/352) | #352: Where is everyone getting accounts from now? | Раздел 11, L1228 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-1944](https://github.com/Soju06/codex-lb/discussions/1944) | #1944: For now, you can try the enhanced version | Раздел 11, L1232 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-994](https://github.com/Soju06/codex-lb/discussions/994) | #994: codex-reset: a tiny Linux/CLI redeem tool building on your wham research | Раздел 11, L1235 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-500](https://github.com/Soju06/codex-lb/discussions/500) | #500: Just created an Opencode plugin for simplified setup on codex-lb | Раздел 11, L1238 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-2232](https://github.com/Soju06/codex-lb/discussions/2232) | #2232: **Title: Does load balancing across multiple Plus accounts still make sense?** | Раздел 11, L1242 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-1998](https://github.com/Soju06/codex-lb/discussions/1998) | #1998: Question: Is there an official migration path from SQLite to PostgreSQL in codex-lb? | Раздел 11, L1245 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-1864](https://github.com/Soju06/codex-lb/discussions/1864) | #1864: Frequent Invalid previous_response_id errors when using Codex with codex-lb | Раздел 11, L1248 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-1575](https://github.com/Soju06/codex-lb/discussions/1575) | #1575: How can I display the rate option in the codex app? | Раздел 11, L1251 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-1820](https://github.com/Soju06/codex-lb/discussions/1820) | #1820: Is "Dashboard session lifetime" working? | Раздел 11, L1254 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-1593](https://github.com/Soju06/codex-lb/discussions/1593) | #1593: Reauthentication when switching Business accounts: same workspace vs different workspace | Раздел 11, L1257 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-1501](https://github.com/Soju06/codex-lb/discussions/1501) | #1501: This project can't work now? | Раздел 11, L1260 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-1406](https://github.com/Soju06/codex-lb/discussions/1406) | #1406: Codex Lag and localhost:2455 delay | Раздел 11, L1263 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-1192](https://github.com/Soju06/codex-lb/discussions/1192) | #1192: The latest model is not found: Sol/Terra/Luna | Раздел 11, L1266 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-1227](https://github.com/Soju06/codex-lb/discussions/1227) | #1227: Problem with 5.6 Sol | Раздел 11, L1269 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-1055](https://github.com/Soju06/codex-lb/discussions/1055) | #1055: Plan mode in codex-cli with codex-lb? | Раздел 11, L1272 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-1037](https://github.com/Soju06/codex-lb/discussions/1037) | #1037: How to enable fast mode on version 1.20.0 | Раздел 11, L1275 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-803](https://github.com/Soju06/codex-lb/discussions/803) | #803: Codex Desktop history disappears when switching model_provider to codex-lb | Раздел 11, L1278 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-978](https://github.com/Soju06/codex-lb/discussions/978) | #978: The 'gpt-5.5-codex' model is not supported when using Codex with a ChatGPT account. | Раздел 11, L1281 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-864](https://github.com/Soju06/codex-lb/discussions/864) | #864: 7 free accounts > 1 plus — intentional? | Раздел 11, L1284 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-848](https://github.com/Soju06/codex-lb/discussions/848) | Связанная ссылка; установить роль и связь с исправлением | Раздел 11, L1287 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-573](https://github.com/Soju06/codex-lb/discussions/573) | #573: Context limits | Раздел 11, L1290 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-728](https://github.com/Soju06/codex-lb/discussions/728) | #728: i recieve this message by lb : unexpected status 401 Unauthorized: | Раздел 11, L1293 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-704](https://github.com/Soju06/codex-lb/discussions/704) | #704: Where do my HTTP limits go? | Раздел 11, L1296 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-661](https://github.com/Soju06/codex-lb/discussions/661) | #661: Does Codex LB work with the Codex Mobile feature? | Раздел 11, L1299 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-636](https://github.com/Soju06/codex-lb/discussions/636) | #636: Import&#124;Export Accaunts | Раздел 11, L1302 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-406](https://github.com/Soju06/codex-lb/discussions/406) | #406: Codex-Lb does not Works Over VPS? | Раздел 11, L1305 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-292](https://github.com/Soju06/codex-lb/discussions/292) | #292: Request log retention: auto-clearing and configuration options | Раздел 11, L1308 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-212](https://github.com/Soju06/codex-lb/discussions/212) | #212: OpenFang | Раздел 11, L1311 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-1306](https://github.com/Soju06/codex-lb/discussions/1306) | Связанная ссылка; установить роль и связь с исправлением | Раздел 11, L1315 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-884](https://github.com/Soju06/codex-lb/discussions/884) | #884: Idea: API-based authorization flow for accounts when SMS verification is unavailable | Раздел 11, L1318 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-980](https://github.com/Soju06/codex-lb/discussions/980) | #980: Error on compaction | Раздел 11, L1321 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-852](https://github.com/Soju06/codex-lb/discussions/852) | #852: RFC: OIDC federation — keyless CI auth for codex-lb | Раздел 11, L1324 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-709](https://github.com/Soju06/codex-lb/discussions/709) | #709: Feature Request: Optional “Reset My Limits” / Limit Warm-Up Trigger | Раздел 11, L1327 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-663](https://github.com/Soju06/codex-lb/discussions/663) | #663: Feature Request: Support for ENABLE_FORWARD_USER_INFO_HEADERS | Раздел 11, L1330 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-420](https://github.com/Soju06/codex-lb/discussions/420) | #420: Paused -> stealth mode on.... | Раздел 11, L1333 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-342](https://github.com/Soju06/codex-lb/discussions/342) | #342: ChatGPT Business Account | Раздел 11, L1336 | НЕ ПРОВЕРЕНО | — |
| [UP-DISC-378](https://github.com/Soju06/codex-lb/discussions/378) | #378: Deeper usage analysis | Раздел 11, L1339 | НЕ ПРОВЕРЕНО | — |

<!-- source-queue:end -->

## 7. Карточка проверки или исправления

```markdown
### CHECK-<ID> — <краткое описание>

- Источник: <upstream URL / F-ID / IMG-ID / DOC-ID / commit>.
- Заявление другого агента: <что объявлено исправленным>.
- Приоритет / статус: <P1–P3> / <статус>.
- Проверяемый SHA / base: <полные SHA>.
- Образ или пакет, если применимо: <tag + digest / asset + hash>.
- Затронутые файлы и продуктовые пути: <конкретно>.
- OpenSpec: <основная capability + change / обоснование неприменимости>.
- Воспроизведение: <вход, условия, команда; без секретов>.
- Ожидаемое поведение: <по контракту>.
- Фактическое поведение и причина: <подтверждённое; гипотезы отдельно>.
- Доказательства: <tests/results, GitHub run/job/attempt, sanitized logs>.
- Исправление: <суть, файлы, исправляющий SHA; либо ещё нет>.
- Повторная независимая проверка: <SHA, команды, результат, CI, artifact>.
- Непроверенные условия / ограничения: <что осталось>.
- Связанные строки и находки: <IDs>.
- Дата последнего обновления: <YYYY-MM-DD, Europe/Kiev>.
```

## 8. Журнал новых коммитов

| Дата | SHA / диапазон | Заявленная задача | Затронутые проверки | Независимый результат | Исправляющий SHA / следующий шаг |
|---|---|---|---|---|---|
| 2026-09-30 | `deed76ba` → `7ec39f82` | Live hardening; optional env-file в Compose | F-001–F-006; IMG-07; GOV-01 | Подтверждены ORM-регрессия, architecture violations, failing scoped unit; Compose runtime ещё не проверен | Исправления не внесены |
| 2026-09-30 | `c7ca9558` | Pooled quota / Codex backend passthrough (#2535, #2536) | Исходные карточки #2535/#2536; DOC-03; GOV-01 | Просмотрен scope коммита; полноценная независимая проверка passthrough ещё не завершена | Выполнить проверку API/auth/routing/stream teardown |
| 2026-09-30 | `1f62b4f7` | Интеграция #2538–#2545 | Соответствующие строки очереди; CI-03; GOV-01 | Просмотрен scope коммита; исходные claims ещё не закрыты независимыми доказательствами | Проверить каждую интеграцию отдельно |

### Очередь коммитов форка относительно исходной базы

В исходном диапазоне `origin/main..HEAD` — 49 коммитов. Наличие строки не означает, что коммит полностью проверен. Этот диапазон не включает весь исторический код общей базы; он дополняет проверку обращений из исходного реестра. После новых push добавляем новые строки, сохраняя прежние SHA.

| SHA / GitHub diff | Заявление в commit title | Статус проверки | Связанные карточки |
|---|---|---|---|
| [cf0455a1](https://github.com/Frozen811/codex-lb/commit/cf0455a17ceb253b9657f50d66aa790c87aae102) | feat: production stability hardening, 132 issues resolved, and OpenSpec alignment | НЕ ПРОВЕРЕНО | — |
| [55c0f7c0](https://github.com/Frozen811/codex-lb/commit/55c0f7c025fbda1b4d8d34157a79c62c337d1543) | docs: add Quick Clone & Run instructions for Frozen811/codex-lb fork | НЕ ПРОВЕРЕНО | — |
| [9f02c8f9](https://github.com/Frozen811/codex-lb/commit/9f02c8f93132e8d013f867df5e7a14e974c313a6) | chore(release): bump version to 1.25.0, add prod docker compose, workflows, and badges | НЕ ПРОВЕРЕНО | — |
| [67cc3fae](https://github.com/Frozen811/codex-lb/commit/67cc3fae6a0a2372083c747fb0bbb7ec3f943086) | fix(ci): guard upstream release workflows and make README release badge static | НЕ ПРОВЕРЕНО | — |
| [8f2d5117](https://github.com/Frozen811/codex-lb/commit/8f2d5117e80c1d57fda88de00296580abe91da21) | docs: add side-by-side comparison table, 1-click launchers, and instant docker run | НЕ ПРОВЕРЕНО | — |
| [2cee5a80](https://github.com/Frozen811/codex-lb/commit/2cee5a80ae5fbf89c8f304bcae2866fa920a316c) | fix(db): align migration lineage with upstream converge merge revision | НЕ ПРОВЕРЕНО | — |
| [f222787f](https://github.com/Frozen811/codex-lb/commit/f222787fe1e07d34fe93ec55d6af5adb67b6c133) | feat(proxy): admit bounded inline images on the HTTP responses bridge | НЕ ПРОВЕРЕНО | — |
| [76d32e33](https://github.com/Frozen811/codex-lb/commit/76d32e33244f6671bf2538235e698910223eed74) | docs(issues): synchronize all 41 upstream issues and PRs (#2497-#2537) with screenshots and analysis | НЕ ПРОВЕРЕНО | — |
| [b7733623](https://github.com/Frozen811/codex-lb/commit/b77336237918967574eec8aea47da8fc4200414a) | fix(batch-1): normalize business prolite (#2511/#2512), single Content-Type (#2513), multiline ws JSON (#2519/#2530) | НЕ ПРОВЕРЕНО | — |
| [d3590d34](https://github.com/Frozen811/codex-lb/commit/d3590d34678914f158e26fefd0f2ba0f9ad9c59d) | fix(batch-2): normalize lite parallel_tool_calls (#2531), keep JSON instruction in input (#2515), advertise GPT-6 max output (#2528) | НЕ ПРОВЕРЕНО | — |
| [de86a109](https://github.com/Frozen811/codex-lb/commit/de86a10939547739c15125e14c011cd9582a11ae) | fix(batch-3): telemetry codex_cli_rs (#2517), preserve model source base instructions (#2525) and collaboration namespaces (#2526) | НЕ ПРОВЕРЕНО | — |
| [00226ed1](https://github.com/Frozen811/codex-lb/commit/00226ed1f16e8091a4acb603f5a92c0421885688) | fix(batch-4): metrics server logging config (#2529), snapshot force probe state (#2524), drain db background tasks on shutdown (#2506, #2505) | НЕ ПРОВЕРЕНО | — |
| [995689e1](https://github.com/Frozen811/codex-lb/commit/995689e137ab0e4c6716906d73349c2f97538bd0) | fix(batch-5): declare web search support in codex examples (#2516, #2498), cover scim/overflow merge convergence (#2518), harden model source usage and telemetry (#2521) | НЕ ПРОВЕРЕНО | — |
| [3ad72489](https://github.com/Frozen811/codex-lb/commit/3ad724892136aea3347dbd96c8abc142d9f58003) | fix(batch-6): fresh account pool gauges on scrape (#2523, #2426), stream responses helper extraction (#2520), compatible image generation host model (#2537) | НЕ ПРОВЕРЕНО | — |
| [2a6300a9](https://github.com/Frozen811/codex-lb/commit/2a6300a947d8309905e34aa536e280f9d92ecb7f) | fix(batch-7): cli log level and file (#2507), close livelock (#2500), account for cache-write tokens (#2504) | НЕ ПРОВЕРЕНО | — |
| [f2e14c34](https://github.com/Frozen811/codex-lb/commit/f2e14c34f394f4eef0931e7876a9946612a8e183) | feat(batch-8): show paused reset credits (#2497), resolve native http egress regressions (#2501), bulk redeem reset credits (#2514) | НЕ ПРОВЕРЕНО | — |
| [66873657](https://github.com/Frozen811/codex-lb/commit/66873657622fd88362cf5c5267c7c5fa53475117) | feat(batch-9): admit bounded inline images on http bridge (#2508, #2534), keep replayed images and record resolved upstream transport (#2503) | НЕ ПРОВЕРЕНО | — |
| [36e6d78f](https://github.com/Frozen811/codex-lb/commit/36e6d78f94bcfcd137fa3c90dbf194abc5200ded) | docs: mark Batch 9 issues (#2503, #2508, #2534) resolved in ISSUES.md | НЕ ПРОВЕРЕНО | — |
| [4f04cb75](https://github.com/Frozen811/codex-lb/commit/4f04cb75779d4623f1dcb823f1ffb4ec0e93477f) | chore(docker): bump rust | НЕ ПРОВЕРЕНО | — |
| [13d23e4c](https://github.com/Frozen811/codex-lb/commit/13d23e4c534d3f5af2103953062df016ce357e34) | feat(db): MySQL/MariaDB backend and request_logs facet indexes (#2502, #2522, #2532) | НЕ ПРОВЕРЕНО | — |
| [ac9c0a29](https://github.com/Frozen811/codex-lb/commit/ac9c0a29290072d57773a3141392e6b18625839d) | docs: mark Batch 10 issues (#2502, #2522, #2532) resolved in ISSUES.md | НЕ ПРОВЕРЕНО | — |
| [b814afd0](https://github.com/Frozen811/codex-lb/commit/b814afd0603f4e23bc27d636aa141345228a50b4) | chore(deps): bump the frontend-minor-patch group | НЕ ПРОВЕРЕНО | — |
| [c4d75805](https://github.com/Frozen811/codex-lb/commit/c4d75805e59d756e120b2ca081592fc4bf50fae8) | chore(deps): bump frontend and python dependencies and resolve test regressions (PR #2509, PR #2533) | НЕ ПРОВЕРЕНО | — |
| [88c9cd6b](https://github.com/Frozen811/codex-lb/commit/88c9cd6b635ae3acf4b51c825869af6980ec3cae) | feat(batch-11): bump frontend and python dependencies and resolve test regressions (PR #2509, PR #2533) | НЕ ПРОВЕРЕНО | — |
| [947dd2af](https://github.com/Frozen811/codex-lb/commit/947dd2af70a8db2873d750fa250c9c9575953390) | docs: mark Batch 11 issues (#2509, #2533) resolved in ISSUES.md (100% complete) | НЕ ПРОВЕРЕНО | — |
| [f622c563](https://github.com/Frozen811/codex-lb/commit/f622c5632013d24ce9236d176113087b387c7990) | chore(release): bump version to 1.25.1 with 156 issues resolved | НЕ ПРОВЕРЕНО | — |
| [e80159a0](https://github.com/Frozen811/codex-lb/commit/e80159a09a3c6f6ac1fa536bfc9daa5cd6a1b10d) | chore: align codex-lb version in uv.lock to 1.25.1 | НЕ ПРОВЕРЕНО | — |
| [b98811f5](https://github.com/Frozen811/codex-lb/commit/b98811f54ea896607e041a1a35d92cfa345fc372) | fix(ci): resolve all typecheck, budget, and contributor gates for fork v1.25.1 | НЕ ПРОВЕРЕНО | — |
| [1f5f8821](https://github.com/Frozen811/codex-lb/commit/1f5f8821cfe009cd33d08b53a53fe4c5fb7d79b6) | fix(ci): fix contributors attribution, typecheck winerror on linux, browser smoke collapsible, and proxy bridge session routing | НЕ ПРОВЕРЕНО | — |
| [e0a2a854](https://github.com/Frozen811/codex-lb/commit/e0a2a854f96d315adae937fd7c48bb12dd7e9eaf) | fix(ci): fix live reset warmup, streaming inline images, settings reference, and proxy routing | НЕ ПРОВЕРЕНО | — |
| [f5893d9e](https://github.com/Frozen811/codex-lb/commit/f5893d9e80a70b2ebe357ef6ef4097da9fa00c1a) | fix(ci): fix bridge fast-path framing, soft sticky failover, model eligibility, and websocket terminal classification | НЕ ПРОВЕРЕНО | — |
| [eed1d42c](https://github.com/Frozen811/codex-lb/commit/eed1d42ca4e010be0363bfca567547b56babfed2) | fix(ci): resolve mysql values syntax, ddl compiler defaults, usage share denial, and responses routing | НЕ ПРОВЕРЕНО | — |
| [28a11740](https://github.com/Frozen811/codex-lb/commit/28a11740813575f11766e891a60e0a6407d9c54c) | fix(ci): align websocket continuation error handling, restore 404 bridge rejection, and pass all ci test gates | НЕ ПРОВЕРЕНО | — |
| [9a8d5332](https://github.com/Frozen811/codex-lb/commit/9a8d53321fc8d3eefc9e7c248618910072acb601) | fix(proxy): harmonize websocket continuity owner fail-closed with model source guard | НЕ ПРОВЕРЕНО | — |
| [07af8e7f](https://github.com/Frozen811/codex-lb/commit/07af8e7fe17dba6efca3e20ca06fe7cf2290e394) | style(proxy): format websocket mixin with ruff | НЕ ПРОВЕРЕНО | — |
| [fda00cf8](https://github.com/Frozen811/codex-lb/commit/fda00cf805664dad2cfb1ec4b7ac6a0f2980eca2) | fix(proxy): restore parallel_tool_calls upstream stripping, single-account continuity bypass, and websocket error propagation | НЕ ПРОВЕРЕНО | — |
| [30840ccd](https://github.com/Frozen811/codex-lb/commit/30840ccd114c4b48e962fce20bb9b7d7f156a6f8) | fix(proxy): enforce api key scope for compact continuity bypass and handle websocket continuity errors | НЕ ПРОВЕРЕНО | — |
| [dfd20f7a](https://github.com/Frozen811/codex-lb/commit/dfd20f7a8ed95c519b7a44229caef5d12aedc9c4) | fix(ci): resolve websocket continuity routing, viewport width containment, and trivy base-image scan | НЕ ПРОВЕРЕНО | — |
| [e8e1a623](https://github.com/Frozen811/codex-lb/commit/e8e1a623f6c235e80d61a5de8d1cc75586cd67d5) | chore(ci): allow .trivyignore in simplicity budgets root files | НЕ ПРОВЕРЕНО | — |
| [0e6d8f07](https://github.com/Frozen811/codex-lb/commit/0e6d8f07f9457d4abeb448e4109ed191c9bc647e) | test(quarantine): isolate session id per parameterized test and clean up durable state in provenance tests | НЕ ПРОВЕРЕНО | — |
| [ab1d18b5](https://github.com/Frozen811/codex-lb/commit/ab1d18b5d440cb74bf5e6ba4e4327d4b844e43b4) | fix(db): map mysql type sizing into dialect variants to avoid sqlite collation pollution | НЕ ПРОВЕРЕНО | — |
| [66412181](https://github.com/Frozen811/codex-lb/commit/66412181118ebad708023380afb0cae4e92724f0) | test(quarantine): add unique uuid to test session ids to guarantee cross-test isolation | НЕ ПРОВЕРЕНО | — |
| [1f62b4f7](https://github.com/Frozen811/codex-lb/commit/1f62b4f7a902da0b60fa57d32c98d02459eb70e9) | feat(upstream): resolve and integrate upstream issues and PRs #2538-#2545 | В ПРОВЕРКЕ | Просмотрен scope; продуктовая проверка не завершена |
| [e354c7d3](https://github.com/Frozen811/codex-lb/commit/e354c7d380e865d835e59289f7181044be4f9a77) | docs: add comprehensive update guide for fork users and refresh release links | НЕ ПРОВЕРЕНО | — |
| [eaf9c16d](https://github.com/Frozen811/codex-lb/commit/eaf9c16dbd0e2fd0259a2702124d1b39148d0a01) | fix(db): handle sqlite integer and biginteger reflection equivalence in schema drift check | НЕ ПРОВЕРЕНО | — |
| [c7ca9558](https://github.com/Frozen811/codex-lb/commit/c7ca9558578b1c31bc3fa6bb08de65dba799f824) | feat(proxy): show pooled quota and forward codex chatgpt-backend calls (#2535, #2536) | В ПРОВЕРКЕ | Просмотрен scope; продуктовая проверка не завершена |
| [cf820e0f](https://github.com/Frozen811/codex-lb/commit/cf820e0f20d6c90a510364ae684231a99c80ac4d) | docs: document v1.25.0-hardened.2 release and pooled quota setup | НЕ ПРОВЕРЕНО | — |
| [deed76ba](https://github.com/Frozen811/codex-lb/commit/deed76bab5fafa36051c2cf474a1b29055988aae) | fix: live deployment hardening fixes (oauth proxy reauth, continuity owner, image fanout, bridge key, reset credit) | В ПРОВЕРКЕ | F-001–F-004, F-006; подтверждены отдельные блокеры |
| [7ec39f82](https://github.com/Frozen811/codex-lb/commit/7ec39f82709ee1ca4c00489a8d5fc301d49320ed) | fix(compose): make .env.local optional in docker compose files | В ПРОВЕРКЕ | IMG-07; HEAD содержит F-001–F-005, не все введены этим коммитом |

## 9. Журнал обновления реестра

- 2026-09-30: добавлены пользовательская история маршрутизации после обновлений Codex, исходные пять исправлений, дополнительный неприменённый owner-miss patch и отдельная жалоба о quota после Pause; карточки INC-01–INC-09, hashes и текстовые приложения. Исправление отложено по прямому указанию пользователя.
- 2026-09-30: создан по прямому поручению пользователя. Внесён исходный срез аудита, 8 находок, очередь поставки/документации/CI/оформления и полный индекс уникальных ссылок из `ISSUES.md`; добавлена очередь 49 коммитов форка. Исправления проекта не выполнялись; исходный `ISSUES.md`, workflows, root allowlist и опубликованные артефакты не изменялись.

## 10. История инцидента: аккаунт логина, дополнительный patch и расход после Pause

Добавлено 2026-09-30 по сообщению пользователя. **Исправлять позже**: в этом обновлении только фиксируем историю, исходные материалы и будущие проверки. Патч не применён, тесты патча не запускались, приложение и опубликованные образы не менялись.

### 10.1. Последовательность событий и происхождение сведений

1. **Исходная жалоба пользователя:** после последних обновлений Codex перестал ожидаемо маршрутизировать запросы по пулу; по наблюдению пользователя, расходуется только аккаунт, под которым выполнен логин. Точная версия клиента, режим авторизации, конфигурация endpoint, версия/digest запущенного сервера и причина пока не установлены.
2. Другой пользователь прислал `FIXES-NOT-IN-v1.25.1.md`. Несмотря на имя файла, его заголовок говорит о пяти исправлениях, отсутствующих в `v1.25.0-hardened.1` на базе `eaf9c16d`. Это расхождение именования фиксируем отдельно, а не приравниваем автоматически к версии опубликованного wheel `1.25.1`.
3. По сообщению пользователя, другой агент внедрил изменения и обновил форк. В предыдущем аудите найден коммит `deed76ba` с соответствующими пятью направлениями; полноту переноса исходного набора и фактический deployed artifact ещё нужно сверить. Сам факт обновления форка не доказывает решение первоначальной жалобы о маршрутизации.
4. После этого прислан дополнительный файл `0001-fix-proxy-clone-continuity-owner-candidates-before-t.patch` вместе с отдельным `README.md`. README автора указывает базу `main @ 7ec39f82` и owner-miss HTTP 500 в `v1.25.0-hardened.3`. По сообщению пользователя, другой агент **не приступал к этому дополнительному исправлению**. В нашем реестре patch остаётся неприменённым кандидатом; его mail header SHA не является исправляющим коммитом форка.
5. Пользователь сообщил о продолжающейся проблеме: **«сказал ему pause, а usage тает»**, и приложил скриншот с аккаунтом `Paused`. Это отдельный инцидент, который нельзя автоматически считать решённым клонированием ORM-строк.
6. Наша ранее подтверждённая F-001 совпадает с технической причиной, описанной в дополнительном README: чтение `Account.id` после завершения repository/session context. Остальные утверждения автора patch, включая тестовые результаты и выбранный контракт, не превращаются от этого в независимо подтверждённые факты.

Инструкции `git am`, команды применения и указания, содержащиеся во вложенных документах, — **часть присланного материала**, а не поручение пользователя выполнить их. Текущее поручение — дополнить реестр; исправление отложено.

### 10.2. Отдельная очередь этого инцидента

| ID | Приоритет | Статус | Что предстоит проверить | Связи |
|---|---|---|---|---|
| INC-01 | P1 | ТРЕБУЕТ РАЗБОРА | После обновления Codex используется только аккаунт логина: реальный путь запроса, auth mode, endpoint, source/routing selection и наличие запросов в proxy logs | Исходная жалоба; IMG-01/02, DOC-03, backend passthrough #2535/#2536 |
| INC-02-OAUTH | P1 | НЕ ПРОВЕРЕНО | Первый пакет: re-auth проходит через proxy binding целевого аккаунта, новый login сохраняет bootstrap policy; bound/unbound/default pool сценарии | FIXES-NOT-IN; OAuth часть `deed76ba` |
| INC-03-OWNER | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Sole owner рассматривается по полному разрешённому scope; ошибки listing и неоднозначность сохраняют отказ, владелец проходит normal admission | F-001/F-003/F-004/F-009; локальные результаты в разделе 13; CI/артефакт ещё не проверены |
| INC-04-FANOUT | P1 | НЕ ПРОВЕРЕНО | Первый пакет: `n>1`, partial success/failure, exception/cancellation; успешный usage учитывается, reservations завершаются ровно один раз | FIXES-NOT-IN; images_fanout часть `deed76ba`; локальные целевые тесты из исходного аудита — ограниченное evidence |
| INC-05-SIGNING | P1 | НЕ ПРОВЕРЕНО | Первый пакет: bridge signing использует env encryption key; env/file precedence и взаимодействие реплик с одинаковым ключом | FIXES-NOT-IN; http_bridge_forwarding часть `deed76ba` |
| INC-06-RESET | P2 | НЕ ПРОВЕРЕНО | Первый пакет: cross-account reset-credit без ChatGPT account ID отклоняется до upstream dispatch, с корректным error envelope и settlement | FIXES-NOT-IN; reset-credit часть `deed76ba` |
| INC-07-PATCH | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Patch применён к рабочему дереву и дополнен: typed scope, архитектурные границы, OpenSpec, реальные session/API/WS регрессии и отказ вместо affinity bypass | Коммит автора patch не импортирован; нашего исправляющего SHA пока нет; раздел 13 |
| INC-08-PAUSE | P1 | ТРЕБУЕТ РАЗБОРА | На Paused аккаунте продолжает уменьшаться quota: установить реальный расход после pause, его источник и требуемые pause semantics для нового/уже начатого запроса | Скриншоты пользователя; accounts/leases/bridge/background jobs |
| INC-10-QUOTA-DISPLAY | P1 | ТРЕБУЕТ РАЗБОРА | Уточнение 2026-10-01: локальный Codex сообщил об исчерпании quota, а панель ещё показывала примерно 11%; клиентская версия, аккаунт/окно и момент Pause неизвестны | Проверить источник client usage, выбор владельца, timestamps и фактический запущенный артефакт; F-012 не доказывает причину этого случая |
| INC-09-DOC | P2 | ТРЕБУЕТ РАЗБОРА | Согласовать версии: имя FIXES-NOT-IN-v1.25.1, базовый hardened.1, обновление hardened.3, package 1.25.1, SHA/digest deployed сервиса; проверить заявления о 2053/2138 тестах | DOC-02/05, REL-02, F-006/F-007 |

### 10.3. Что говорит дополнительный patch и что ещё не доказано

- Mail header: `9b2491dfc5d10d7162717436350c2b6a1646e7c1`, дата автора `2026-09-30 22:15:20 +03:00`; это идентификатор источника patch, не применённый SHA текущего форка.
- Diff затрагивает `app/modules/proxy/load_balancer.py`, `tests/integration/test_proxy_responses.py`, `tests/unit/test_continuity_owner.py`, `tests/unit/test_proxy_utils.py`: **174 insertions, 21 deletions** по заголовку patch.
- Runtime-изменение: `accounts = [clone_row(account) for account in await repos.accounts.list_accounts()]` внутри repository context.
- Два integration-теста меняют ожидаемое поведение single-account owner miss с отказа 502 на dispatch к единственному возможному владельцу; scoped unit-тест меняет mock seam с `_load_selection_inputs` на `list_continuity_owner_candidates(api_key=...)`.
- Добавлены сценарии: active + paused account остаются двумя возможными владельцами; scoped key ограничивает множество кандидатов; результат listing содержит другой объект, чем исходная строка.
- Новый helper regression-тест использует mock repository и проверяет clone identity; сам по себе он не воспроизводит настоящий SQLAlchemy teardown/expiry. Для закрытия F-001 нужны также тесты реальных session boundaries и продуктовых маршрутов.
- README автора заявляет **2138 passed**, ранее на этом наборе было три failures; первый документ заявляет **2053 passed, 15 новых тестов**, сборку image и миграции fresh/live-copy. Эти числа и окружения **заявлены автором и нами не перепроверены**.
- Дополнительный patch не обновляет OpenSpec и не решает автоматически F-002, quarantine F-005 или жалобу INC-08. Применимость контрактных изменений проверяем отдельно; нельзя просто объявить старые tests неправильными по описанию автора.
- Первый документ также перечисляет две **не перенесённые** разницы: native stream без terminal event и forwarding `parallel_tool_calls` для non-Lite. Их нужно оценить отдельно по клиентскому поведению и спецификации, не считать частью пяти внедрённых фиксов.

### 10.4. Проверка жалобы о маршрутизации и расходе после Pause

План будущего воспроизведения, а не уже установленная причина:

1. Зафиксировать Codex version/channel, режим авторизации, endpoint/config без секретов, запущенный server SHA/image digest и фактический pool/account state. Сопоставить старую и новую версии клиента при одинаковом сервере.
2. Для нового запроса найти корреляцию client request → proxy request log → выбранный аккаунт → upstream dispatch/settlement. Различить вызовы Responses, compact и `/backend-api` passthrough; проверить, попадают ли запросы вообще в codex-lb.
3. Отделить корректную affinity/continuity привязку от ошибки выбора: пул не обязан менять аккаунт на каждом запросе. Проверить свежую сессию, уже закреплённую сессию, scoped key, модели и несколько eligible accounts.
4. Зафиксировать время подтверждённого Pause и account state в БД, затем отдельно проверить новый запрос, следующий anchored turn, уже открытый WebSocket/bridge и уже выполняющийся stream. Не предполагать заранее, что Pause обязан мгновенно отменять ранее запущенную работу; установить контракт.
5. Сопоставить новые dispatch после Pause с уже начатой генерацией, retry/replay, subagent/fan-out, background warmup/probe/reset и возможной прямой клиентской сессией вне прокси. Это альтернативные направления проверки, а не выводы о причине.
6. Снять несколько последовательных measurements одного и того же аккаунта/окна quota с timestamps. Различить upstream quota remaining, dashboard snapshot, pooled quota, key usage и задержку обновления. Один скриншот не показывает скорость расхода и причинность.
7. Проверить, что Paused account остаётся возможным историческим owner для анализа continuity, но его наличие в списке owner candidates само по себе не даёт разрешение запускать новый запрос на нём. Отдельно покрыть known owner paused, owner miss active+paused, sole paused owner и смену состояния между selection и dispatch.
8. Закрыть INC-01/INC-08 только после независимого воспроизведения и повторной проверки исправления на реальном клиентском пути, с доказательствами выбора аккаунта, pause boundary и расхода.

**Наблюдение по скриншоту:** у выделенного аккаунта виден статус `Paused` и weekly remaining **11%**; рядом Codex показывает **9% usage remaining**. У другого активного аккаунта — weekly **57%**, 5h **94%**. Сопоставимость аккаунтов, окон и времени обновления двух интерфейсов пока не установлена; причинное утверждение о расходе после Pause основано на сообщении пользователя и нуждается в measurements/logs. Повторные clipboard-вложения показывают тот же кадр, а не серию последовательных измерений.

### 10.5. Исходные файлы и идентификация

Документы ниже сохранены также текстом в приложениях к этому реестру, чтобы очередь не зависела только от Downloads. Изображения не копировались в репозиторий: сохранены описание наблюдения, пути и SHA-256. Локальные ссылки на изображения могут не работать в другом checkout или после удаления из Temp; для переносимого evidence позже потребуется сохранить оригиналы в согласованном месте. Внешние файлы не изменялись.

| Материал | Локальный источник | SHA-256 исходного файла |
|---|---|---|
| FIXES-NOT-IN-v1.25.1.md | [FIXES-NOT-IN-v1.25.1.md](<C:/Users/ext/Downloads/FIXES-NOT-IN-v1.25.1.md>) | `f4690ddefe744ffd5aaaf4362fe57086756cf4c0efc98d406e6d37da832493b8` |
| README.md | [README.md](<C:/Users/ext/Downloads/AyuGram Desktop/README.md>) | `2041572a61c39dd21c590472508c2af622f18d90baae32e8587fd34e451cda66` |
| 0001-fix-proxy-clone-continuity-owner-candidates-before-t.patch | [0001-fix-proxy-clone-continuity-owner-candidates-before-t.patch](<C:/Users/ext/Downloads/AyuGram Desktop/0001-fix-proxy-clone-continuity-owner-candidates-before-t.patch>) | `d425b57d26c3ba7e53950b231b9837df94f32386f98d26d07440d1f2d7c70e11` |
| image_2026-09-30_20-17-27.png | [image_2026-09-30_20-17-27.png](<C:/Users/ext/Downloads/image_2026-09-30_20-17-27.png>) | `564f13b201b05607e7d6cc514aa76b71398ba3aa10d06fe2c856c18285b4efd9` |
| photo_2026-09-30_23-23-26.jpg | [photo_2026-09-30_23-23-26.jpg](<C:/Users/ext/Downloads/AyuGram Desktop/photo_2026-09-30_23-23-26.jpg>) | `fe7b896f0229cbc862405d8922733464f21e050b0bbba0e8c68f673691a60e83` |
| codex-clipboard-eb2ca51b-089c-4bdf-80d1-8323de056cb9.png | [codex-clipboard-eb2ca51b-089c-4bdf-80d1-8323de056cb9.png](<C:/Users/ext/AppData/Local/Temp/codex-clipboard-eb2ca51b-089c-4bdf-80d1-8323de056cb9.png>) | `e7a12fac934d66ab926dc895b16f17aa661fae02b8593eb6418c8344f1af5822` |
| codex-clipboard-2f7d1db1-8281-412f-8d8b-88a294078246.png | [codex-clipboard-2f7d1db1-8281-412f-8d8b-88a294078246.png](<C:/Users/ext/AppData/Local/Temp/codex-clipboard-2f7d1db1-8281-412f-8d8b-88a294078246.png>) | `e7a12fac934d66ab926dc895b16f17aa661fae02b8593eb6418c8344f1af5822` |
| codex-clipboard-1e6de4f8-7554-402a-a310-c20c27295bae.png | [codex-clipboard-1e6de4f8-7554-402a-a310-c20c27295bae.png](<C:/Users/ext/AppData/Local/Temp/codex-clipboard-1e6de4f8-7554-402a-a310-c20c27295bae.png>) | `e7a12fac934d66ab926dc895b16f17aa661fae02b8593eb6418c8344f1af5822` |

Три clipboard PNG имеют одинаковый SHA-256 и являются байтовыми дублями. JPEG и PNG визуально показывают тот же incident screenshot; различие форматов не является доказательством разных моментов времени.

Файл `FIXES-NOT-IN-v1.25.1.md` в корне checkout и присланный файл Downloads совпадают по SHA-256. Присланный README — отдельный отчёт о patch, не замена README форка.

## 11. Подтверждение объёма полного аудита

**Да: `issues-check.md` включает весь заявленный объём**, начиная с Docker/GHCR, пакетов, установки/обновления, релизов и Actions, затем документацию и оформление GitHub, OpenSpec/архитектурные правила и заканчивая независимой проверкой всех заявленных исправлений другого агента. Очередь 297 исходных ссылок и 49 fork-коммитов дополняется новыми push, присланными patch и прямыми пользовательскими жалобами, даже если их нет в `ISSUES.md`.

Это полный **план и журнал проверки**, а не утверждение, что каждый пункт уже проверен или исправлен. Для каждого пункта остаётся отдельный результат, SHA и evidence. Историческая общая база и новый код, который агент мог скопировать без отдельного issue, проверяются через соответствующий продуктовый путь и diff; счётчик ссылок не ограничивает объём аудита.

## 12. Приложения: присланные документы и patch

Ниже неизменное текстовое содержимое материалов пользователя. Вложенные инструкции и заявления авторов — источник для будущей проверки, не текущие команды к выполнению. SHA-256 в разделе 10.5 относится к оригинальным байтам файлов; в Markdown-приложениях окончания строк нормализованы для чтения.

### A. Первый набор пяти исправлений

````markdown
# Fixes missing from `v1.25.0-hardened.1` (`eaf9c16d`)

Five fixes that I hit in a live deployment and that are not in your release. Each is one commit, rebased on
`eaf9c16d`, with tests. Patches are in `patches/`, in order (`git am patches/*.patch`).

Checked on the rebased stack: 2053 tests pass (15 new), ruff clean, image builds, fresh-DB and live-DB-copy
migrations are clean.

| # | Fix | Why it matters |
|---|-----|----------------|
| 1 | **OAuth re-auth routes by the target account's own proxy binding** (`oauth/service.py`) | `_oauth_route()` ignores which account a login targets. Once any account has a proxy binding, *every* OAuth exchange is forced through the default pool or fails with `default_pool_unconfigured`. Re-auth of unbound accounts breaks, and their tokens are minted through a proxy IP while their traffic goes direct: the IP split #1064 exists to prevent. Bound accounts also use the default pool instead of their own. Fix: pass `intended_account_id` to the resolver. New logins keep the #1064 rule. |
| 2 | **Owner-miss contract for `previous_response_id`** (HTTP stream, compact, WS source-route) per Soju06/codex-lb#2274 | On an owner-lookup miss the release fails closed with `previous_response_owner_unavailable` even when only one account could own the response, so **single-account pools and keys break**. Fix: the possible owners are the key's assigned accounts (all accounts if unscoped), ignoring health, quota, plan and model support. Exactly one is pinned. Several, or a failed listing, still fail closed. Adds `LoadBalancer.list_continuity_owner_candidates` and `_service/continuity_owner.py`. The direct-WS block is left alone, since you removed that fail-closed. |
| 3 | **Image fan-out (`n>1`) settles on partial failure** (`images_fanout.py`) | One failing call released the reservation and returned the error, so tokens from the calls that *did* succeed were never settled. The key's usage limits were under-counted. An exception from any call escaped `gather` without releasing the reservation, which leaked it. Fix: `gather(return_exceptions=True)`. The reservation is settled with the successful calls' usage, released only if none succeeded, and released on cancellation. The first error is still surfaced. |
| 4 | **Bridge requests are signed with the configured encryption key** (`http_bridge_forwarding.py`) | `get_or_create_key(settings.encryption_key_file)` skips `CODEX_LB_ENCRYPTION_KEY` and uses or creates a file key. Deployments configured by env key sign with a different key than the one configured, and replicas sharing the env key cannot agree on signatures. Fix: `get_or_create_key()`, which honors the env key first. |
| 5 | **Reset-credit redeem rejects a target with no ChatGPT account ID** (`api.py`) | For a cross-account target the request went upstream with `account_id=None`. Now it fails fast with a clear `ProxyAuthError`. |

## Differences I did *not* port (your call)

- **Native stream with no terminal event.** The release aborts the body with 502 `stream_incomplete`. I had switched to
  emitting a retryable `response.failed` event so a native client can't read HTTP 200 + EOF as a completed response.
  `test_native_codex_stream_preserves_missing_terminal_without_synthesis` asserts your behavior, so I left it.
- **`parallel_tool_calls`.** Your #2531 forces `false` for Responses-Lite, which fixes the Desktop rejection. For non-Lite
  requests the field is still dropped, so a client's explicit value is lost. Forwarding it would reopen your #2465
  workaround, so I left it.
````

### B. README дополнительного owner-miss patch

````markdown
# Owner-miss fallback returns HTTP 500 in `v1.25.0-hardened.3`

**Patch:** `0001-fix-proxy-clone-continuity-owner-candidates-before-t.patch`, made against `main` @ `7ec39f82`.
Apply it with `git am`.

## Bug

`LoadBalancer.list_continuity_owner_candidates` returns the ORM `Account` rows *after* the
`async with self._repo_factory()` block has closed their session. `resolve_continuity_owner_candidate` then reads
`candidates[0].id` from a detached row:

```
sqlalchemy.orm.exc.DetachedInstanceError: Instance <Account ...> is not bound to a Session
  continuity_owner.py:32  return candidates[0].id
```

So every `previous_response_id` owner miss on the HTTP stream, `/v1/responses/compact` and WebSocket
source-route paths ends in **HTTP 500 `server_error`**. It should forward to the sole possible owner (#2274).
Single-account pools, the case the fallback exists for, are the ones that hit it.

## Fix (1 line)

Clone the rows inside the session with `clone_row`, as the other `LoadBalancer` snapshot helpers already do:

```python
async with self._repo_factory() as repos:
    accounts = [clone_row(account) for account in await repos.accounts.list_accounts()]
```

## Tests

- **Regression test:** `test_list_continuity_owner_candidates_returns_detached_safe_clones` fails on `7ec39f82` and passes with the fix.
- **Stale tests on `main`:** 3 tests were already failing there. Two still expected "single account fails closed", which contradicts the #2274 contract. The third stubbed the old `account_ids=` signature. The patch updates them to the new contract.
- **Results:** 2138 tests pass across the owner-miss, OAuth, fan-out, bridge, reset-credit and requests suites. `main` had 3 failures on the same set. `ruff check` and `ruff format` are clean.
````

### C. Дополнительный patch, не применён

````diff
From 9b2491dfc5d10d7162717436350c2b6a1646e7c1 Mon Sep 17 00:00:00 2001
From: Anonymous <anonymous@users.noreply.github.com>
Date: Wed, 30 Sep 2026 22:15:20 +0300
Subject: [PATCH] fix(proxy): clone continuity owner candidates before the repo
 session closes

list_continuity_owner_candidates returned the ORM rows of a repo session that
had already closed. resolve_continuity_owner_candidate then read candidates[0].id
on a detached instance, so every previous_response_id owner miss on the HTTP
stream, compact and WebSocket source-route paths ended in DetachedInstanceError
and an HTTP 500 instead of forwarding to the sole possible owner (#2274).

Clone the rows inside the session, as the other LoadBalancer snapshot helpers do.

Also align the tests with the #2274 contract v1.25.0-hardened.3 introduced:
a single-account pool forwards on an owner miss instead of failing closed, and
scoped keys are listed through the api_key argument.
---
 app/modules/proxy/load_balancer.py        |   4 +-
 tests/integration/test_proxy_responses.py | 145 ++++++++++++++++++++--
 tests/unit/test_continuity_owner.py       |  24 ++++
 tests/unit/test_proxy_utils.py            |  22 ++--
 4 files changed, 174 insertions(+), 21 deletions(-)

diff --git a/app/modules/proxy/load_balancer.py b/app/modules/proxy/load_balancer.py
index 8c167d97..a30a8d4b 100644
--- a/app/modules/proxy/load_balancer.py
+++ b/app/modules/proxy/load_balancer.py
@@ -339,7 +339,9 @@ class LoadBalancer:
         ignoring health, quota, plan and model support.
         """
         async with self._repo_factory() as repos:
-            accounts = await repos.accounts.list_accounts()
+            # Clone inside the session: the rows outlive it, and a detached ORM
+            # instance raises DetachedInstanceError on the first attribute read.
+            accounts = [clone_row(account) for account in await repos.accounts.list_accounts()]
         if api_key is not None and getattr(api_key, "account_assignment_scope_enabled", False):
             assigned = set(getattr(api_key, "assigned_account_ids", []) or [])
             return [account for account in accounts if account.id in assigned]
diff --git a/tests/integration/test_proxy_responses.py b/tests/integration/test_proxy_responses.py
index f65b64c2..93f145da 100644
--- a/tests/integration/test_proxy_responses.py
+++ b/tests/integration/test_proxy_responses.py
@@ -1905,17 +1905,25 @@ async def test_v1_responses_missing_previous_response_owner_fails_closed_before_


 @pytest.mark.asyncio
-async def test_v1_responses_single_account_missing_previous_response_owner_fails_closed_without_dispatch(
+async def test_v1_responses_single_account_missing_previous_response_owner_forwards(
     async_client,
     monkeypatch,
 ):
+    # Soju06/codex-lb#2274: exactly one possible owner may proceed.
     auth_json = _make_auth_json("acc_prev_single_cand", "prev-single-cand@example.com")
     files = {"auth_json": ("auth.json", json.dumps(auth_json), "application/json")}
     response = await async_client.post("/api/accounts/import", files=files)
     assert response.status_code == 200

-    async def fake_stream(*args, **kwargs):
-        raise AssertionError("missing previous_response_id owner must fail closed even with 1 account")
+    dispatched: list[tuple[str | None, str | None]] = []
+
+    async def fake_stream(payload, headers, access_token, account_id, **kwargs):
+        del headers, access_token, kwargs
+        dispatched.append((account_id, payload.previous_response_id))
+        yield (
+            'data: {"type":"response.completed","response":{"id":"resp_prev_single_followup",'
+            '"object":"response","status":"completed","output":[]}}\n\n'
+        )

     async def fake_resolve_owner(self, *, previous_response_id, api_key, session_id, surface):
         del self, previous_response_id, api_key, session_id, surface
@@ -1934,16 +1942,17 @@ async def test_v1_responses_single_account_missing_previous_response_owner_fails
         headers={"session_id": "sid_prev_single_missing_owner"},
     )

-    assert response.status_code == 502
-    assert response.json()["error"]["code"] == "previous_response_owner_unavailable"
-    assert response.json()["error"]["message"] == "Previous response owner account is unavailable; retry later."
+    assert response.status_code == 200
+    assert response.json()["id"] == "resp_prev_single_followup"
+    assert dispatched == [("acc_prev_single_cand", "resp_prev_single_missing_owner")]


 @pytest.mark.asyncio
-async def test_v1_responses_compact_single_account_missing_previous_response_owner_fails_closed(
+async def test_v1_responses_compact_single_account_missing_previous_response_owner_forwards(
     async_client,
     monkeypatch,
 ):
+    # Soju06/codex-lb#2274: exactly one possible owner may proceed.
     auth_json = _make_auth_json("acc_prev_compact_single", "prev-compact-single@example.com")
     files = {"auth_json": ("auth.json", json.dumps(auth_json), "application/json")}
     response = await async_client.post("/api/accounts/import", files=files)
@@ -1953,7 +1962,21 @@ async def test_v1_responses_compact_single_account_missing_previous_response_own
         del self, previous_response_id, api_key, session_id, surface
         return None

+    dispatched: list[tuple[str | None, str | None]] = []
+
+    async def fake_compact(payload, headers, access_token, account_id, **kwargs):
+        del headers, access_token, kwargs
+        dispatched.append((account_id, payload.previous_response_id))
+        return CompactResponsePayload.model_validate(
+            {
+                "object": "response.compaction",
+                "compaction_summary": {"id": "cmp_prev_single_followup", "encrypted_content": "summary"},
+                "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
+            }
+        )
+
     monkeypatch.setattr(proxy_module.ProxyService, "_resolve_websocket_previous_response_owner", fake_resolve_owner)
+    monkeypatch.setattr(proxy_module, "core_compact_responses", fake_compact)

     response = await async_client.post(
         "/v1/responses/compact",
@@ -1965,9 +1988,115 @@ async def test_v1_responses_compact_single_account_missing_previous_response_own
         headers={"session_id": "sid_prev_compact_missing_owner"},
     )

+    assert response.status_code == 200
+    assert response.json()["compaction_summary"]["id"] == "cmp_prev_single_followup"
+    assert dispatched == [("acc_prev_compact_single", "resp_prev_compact_missing_owner")]
+
+
+@pytest.mark.asyncio
+async def test_v1_responses_owner_miss_counts_unroutable_accounts_as_possible_owners(
+    async_client,
+    monkeypatch,
+):
+    # Soju06/codex-lb#2274: routing eligibility may reject a known owner but
+    # must not choose one. A paused account can still own the response, so a
+    # pool with one routable and one paused account has two possible owners.
+    account_ids: list[str] = []
+    for raw_account_id, email in (
+        ("acc_prev_unroutable_active", "prev-unroutable-active@example.com"),
+        ("acc_prev_unroutable_paused", "prev-unroutable-paused@example.com"),
+    ):
+        auth_json = _make_auth_json(raw_account_id, email)
+        files = {"auth_json": ("auth.json", json.dumps(auth_json), "application/json")}
+        response = await async_client.post("/api/accounts/import", files=files)
+        assert response.status_code == 200
+        account_ids.append(generate_unique_account_id(raw_account_id, email))
+    paused = await async_client.post(f"/api/accounts/{account_ids[1]}/pause")
+    assert paused.status_code == 200
+
+    async def fake_stream(*args, **kwargs):
+        raise AssertionError("an owner miss with two possible owners must not dispatch to the routable one")
+        if False:
+            yield ""
+
+    async def fake_resolve_owner(self, *, previous_response_id, api_key, session_id, surface):
+        del self, previous_response_id, api_key, session_id, surface
+        return None
+
+    monkeypatch.setattr(proxy_module, "core_stream_responses", fake_stream)
+    monkeypatch.setattr(proxy_module.ProxyService, "_resolve_websocket_previous_response_owner", fake_resolve_owner)
+
+    response = await async_client.post(
+        "/v1/responses",
+        json={
+            "model": "gpt-5.1",
+            "input": "continue",
+            "previous_response_id": "resp_prev_unroutable_missing_owner",
+        },
+        headers={"session_id": "sid_prev_unroutable_missing_owner"},
+    )
+
     assert response.status_code == 502
     assert response.json()["error"]["code"] == "previous_response_owner_unavailable"
-    assert response.json()["error"]["message"] == "Previous response owner account is unavailable; retry later."
+
+
+@pytest.mark.asyncio
+async def test_v1_responses_owner_miss_forwards_to_sole_assigned_account(
+    async_client,
+    monkeypatch,
+):
+    # Soju06/codex-lb#2274: fallback considers only the API key's assigned
+    # accounts, so accounts outside its scope do not make the owner ambiguous.
+    account_ids: list[str] = []
+    for raw_account_id, email in (
+        ("acc_prev_scoped_other", "prev-scoped-other@example.com"),
+        ("acc_prev_scoped_assigned", "prev-scoped-assigned@example.com"),
+    ):
+        auth_json = _make_auth_json(raw_account_id, email)
+        files = {"auth_json": ("auth.json", json.dumps(auth_json), "application/json")}
+        response = await async_client.post("/api/accounts/import", files=files)
+        assert response.status_code == 200
+        account_ids.append(generate_unique_account_id(raw_account_id, email))
+
+    response = await async_client.put("/api/settings", json={"apiKeyAuthEnabled": True})
+    assert response.status_code == 200
+    response = await async_client.post(
+        "/api/api-keys/",
+        json={"name": "prev-scoped-key", "assignedAccountIds": [account_ids[1]]},
+    )
+    assert response.status_code == 200
+    api_key = response.json()["key"]
+
+    dispatched: list[tuple[str | None, str | None]] = []
+
+    async def fake_stream(payload, headers, access_token, account_id, **kwargs):
+        del headers, access_token, kwargs
+        dispatched.append((account_id, payload.previous_response_id))
+        yield (
+            'data: {"type":"response.completed","response":{"id":"resp_prev_scoped_followup",'
+            '"object":"response","status":"completed","output":[]}}\n\n'
+        )
+
+    async def fake_resolve_owner(self, *, previous_response_id, api_key, session_id, surface):
+        del self, previous_response_id, api_key, session_id, surface
+        return None
+
+    monkeypatch.setattr(proxy_module, "core_stream_responses", fake_stream)
+    monkeypatch.setattr(proxy_module.ProxyService, "_resolve_websocket_previous_response_owner", fake_resolve_owner)
+
+    response = await async_client.post(
+        "/v1/responses",
+        json={
+            "model": "gpt-5.1",
+            "input": "continue",
+            "previous_response_id": "resp_prev_scoped_missing_owner",
+        },
+        headers={"session_id": "sid_prev_scoped_missing_owner", "Authorization": f"Bearer {api_key}"},
+    )
+
+    assert response.status_code == 200
+    assert response.json()["id"] == "resp_prev_scoped_followup"
+    assert dispatched == [("acc_prev_scoped_assigned", "resp_prev_scoped_missing_owner")]


 @pytest.mark.asyncio
diff --git a/tests/unit/test_continuity_owner.py b/tests/unit/test_continuity_owner.py
index af58a9fc..5c488121 100644
--- a/tests/unit/test_continuity_owner.py
+++ b/tests/unit/test_continuity_owner.py
@@ -97,3 +97,27 @@ async def test_resolve_continuity_owner_candidate_exception_fails_closed():

     result = await resolve_continuity_owner_candidate(lb)
     assert result is None
+
+
+@pytest.mark.asyncio
+async def test_list_continuity_owner_candidates_returns_detached_safe_clones():
+    """The rows outlive the repo session, so they must be clones: reading an
+    attribute of a detached ORM row raised DetachedInstanceError (owner-miss 500)."""
+    mock_repo = MagicMock()
+    acc1 = Account(id="acc-1", email="acc1@example.com")
+    mock_repo.accounts.list_accounts = AsyncMock(return_value=[acc1])
+
+    class MockRepoFactory:
+        def __call__(self):
+            return self
+
+        async def __aenter__(self):
+            return mock_repo
+
+        async def __aexit__(self, *args):
+            return None
+
+    candidates = await LoadBalancer(MockRepoFactory()).list_continuity_owner_candidates()
+
+    assert [candidate.id for candidate in candidates] == ["acc-1"]
+    assert candidates[0] is not acc1
diff --git a/tests/unit/test_proxy_utils.py b/tests/unit/test_proxy_utils.py
index 6df73d39..db350221 100644
--- a/tests/unit/test_proxy_utils.py
+++ b/tests/unit/test_proxy_utils.py
@@ -16093,7 +16093,6 @@ async def test_compact_owner_miss_uses_api_key_scope_before_fail_closed(monkeypa
     request_logs = _RequestLogsRecorder()
     service = proxy_service.ProxyService(_repo_factory(request_logs))
     account = _make_account("acc_compact_scoped_owner_miss")
-    seen_account_ids: list[list[str] | None] = []

     api_key = ApiKeyData(
         id="key_compact_scope",
@@ -16115,16 +16114,12 @@ async def test_compact_owner_miss_uses_api_key_scope_before_fail_closed(monkeypa
     monkeypatch.setattr(proxy_service, "get_settings", lambda: settings)
     monkeypatch.setattr(service, "_resolve_websocket_previous_response_owner", AsyncMock(return_value=None))

-    async def fake_load_selection_inputs(**kwargs):
-        seen_account_ids.append(kwargs.get("account_ids"))
-        return SimpleNamespace(accounts=[account])
-
-    monkeypatch.setattr(service._load_balancer, "_load_selection_inputs", fake_load_selection_inputs)
-    monkeypatch.setattr(
-        service._load_balancer,
-        "select_account",
-        AsyncMock(return_value=AccountSelection(account=account, error_message=None)),
-    )
+    # Soju06/codex-lb#2274 (as in upstream PR #1905): possible owners come from
+    # the key's assignment scope, not from routing-eligible selection inputs.
+    list_continuity_owner_candidates = AsyncMock(return_value=(account,))
+    monkeypatch.setattr(service._load_balancer, "list_continuity_owner_candidates", list_continuity_owner_candidates)
+    select_account = AsyncMock(return_value=AccountSelection(account=account, error_message=None))
+    monkeypatch.setattr(service._load_balancer, "select_account", select_account)
     monkeypatch.setattr(service, "_ensure_fresh", AsyncMock(return_value=account))
     monkeypatch.setattr(service, "_settle_compact_api_key_usage", AsyncMock())

@@ -16147,7 +16142,10 @@ async def test_compact_owner_miss_uses_api_key_scope_before_fail_closed(monkeypa

     assert result.object == "response.compaction"
     assert result.model_extra == {"output": []}
-    assert seen_account_ids == [[account.id]]
+    list_continuity_owner_candidates.assert_awaited_once()
+    assert list_continuity_owner_candidates.await_args is not None
+    assert list_continuity_owner_candidates.await_args.kwargs["api_key"] is api_key
+    select_account.assert_awaited_once()


 @pytest.mark.asyncio
--
2.54.0.windows.1
````

## 13. Первый блок исправлений — 2026-10-01

### 13.1. Рабочая ревизия и границы результата

- Локальный HEAD и `Frozen811/codex-lb/main`: `7ec39f82709ee1ca4c00489a8d5fc301d49320ed`. GitHub проверен заново 2026-10-01; [CI run 36761400788](https://github.com/Frozen811/codex-lb/actions/runs/36761400788) остаётся `failure` на этом SHA.
- Пользователь разрешил начать предложенный порядок проверки/исправления. До работы единственной незакоммиченной правкой был этот untracked реестр.
- Исправления находятся только в рабочем дереве. Ветка, коммит, push, release, workflow dispatch и deployment не выполнялись. Нового исправляющего SHA нет.
- OpenSpec change: `repair-continuity-owner-snapshots`; итоговые artifacts — [archive/2026-10-01-repair-continuity-owner-snapshots](openspec/changes/archive/2026-10-01-repair-continuity-owner-snapshots). Нормативный контракт: [responses-api-compat/spec.md](openspec/specs/responses-api-compat/spec.md), rationale — [context.md](openspec/specs/responses-api-compat/context.md).

### 13.2. Что исправлено локально

1. **F-001:** присланный patch применён через `git apply`, без импорта коммита автора. `Account` клонируется внутри открытой repository session. Scope читается из типизированного `ApiKeyData`; явно пустой scope не превращается во весь пул. Настоящий teardown теперь оставляет читаемые transient snapshots; тест отдельно подтверждает, что исходная ORM-строка действительно истекла и чтение её ID вызывает `DetachedInstanceError`.
2. **F-002:** общий resolver перенесён в разрешённый `_service/support.py`; старый `_service/continuity_owner.py` удалён. Required-owner policy validation перенесён в существующий `_load_balancer/sticky_selection.py` с `SelectionInputsProtocol`, коды ошибок сохранены. `load_balancer.py`: **3021/3021**, checker проходит; thresholds и checker не ослаблены.
3. **F-003/F-004:** после чтения [upstream #2274](https://github.com/Soju06/codex-lb/issues/2274) OpenSpec согласован с bounded fallback: успешный lookup miss + ровно один возможный subscription owner в разрешённом scope → pin + обычная admission. Routing eligibility не доказывает ownership. Два прежних integration ожидания и scoped compact test seam обновлены; реальный scoped API-путь проверен.
4. **F-009:** новые API-тесты обнаружили отдельный affinity bypass: direct WebSocket с несколькими возможными владельцами или listing error отправлял запрос при Codex affinity. Удалено условие, позволявшее обход. Проверены отказ на новом socket и отказ неоднозначного follow-up на уже открытом socket, без повторного upstream dispatch.
5. Старые transport-only тесты, использовавшие mocked connection и неизвестный anchor без определённого пула, получили **явный одноаккаунтный candidate fixture**. Их исходные проверки marker/replay/error sanitization сохранены; неоднозначный реальный пул проверяется отдельными отрицательными регрессиями. Автоматические timeout/прерванные прогоны не считаются успешной проверкой.

### 13.3. Независимая локальная проверка

Проверка на Windows, Python из существующей `.venv`, SQLite в изолированных временных test DB. Настоящие upstream вызовы заменены существующими тестовыми transport seams; production DB и аккаунты не использованы.

| Набор / команда | Результат |
|---|---|
| Исходный focused owner-miss набор до правок | **6 passed / 3 failed**; реальный ORM teardown reproduces F-001, scoped unit reproduces F-004 |
| `tests/unit/test_continuity_owner.py` | **11 passed**; реальные unscoped/scoped/empty snapshots, paused candidate, listing/attribute failure |
| `test_proxy_utils.py` + `test_load_balancer.py`, `-k 'previous_response or continuity or owner or paused'` | **233 passed**, 1532 deselected |
| `test_proxy_responses.py` + `test_proxy_websocket_responses.py`, тот же `-k` | **76 passed**, 234 deselected; HTTP stream/non-stream, compact, direct WS, known owners, pin/conflict, replay/sanitization и новые отрицательные сценарии |
| `test_proxy_sticky_sessions.py` + `test_openai_compat_features.py`, тот же `-k` | **13 passed**: 12 вместе + отдельный scope-restart сценарий; последний штатно использует 75-секундный request budget и прошёл за 76.19 s |
| `python -m ruff check app tests` | **PASS** |
| Ruff format check изменённых Python-файлов | **PASS** |
| `python scripts/check_proxy_architecture.py` | **PASS** |
| `python .github/scripts/check_simplicity_budgets.py` | **PASS** на текущем tracked HEAD; root allowlist дополнен для будущего коммита реестра |
| OpenSpec strict validation | **PASS**: change проверен строго, нормативный блок синхронизирован и change архивирован; итоговая post-sync проверка — **68 passed / 0 failed**, все 10 tasks завершены |
| `test_check_proxy_architecture.py` | **4 passed / 10 failed**; отдельный F-011, Windows path rendering. Checker и этот test file побайтно сопоставлены с HEAD после нормализации line endings — они не менялись |

Итого **333 успешных целевых runtime-теста** в четырёх непересекающихся наборах. Это не полная suite и не утверждение о зелёном CI. MySQL/PostgreSQL transport regression после этой правки и проверка собранного образа остаются открытыми. Ранее зарегистрированный quarantine F-005 не закрыт.

### 13.4. Обнаруженное несоответствие Docker-тегов — F-010

Получены manifests и OCI labels через `docker buildx imagetools inspect`; образы не запускались и registry не изменялся.

| Тег | OCI revision | Index digest |
|---|---|---|
| `ghcr.io/frozen811/codex-lb:latest` | `f622c5632013d24ce9236d176113087b387c7990` | `sha256:ad9aa84b12bce9f6afc63adb3aa86e73f6aafca1814e6f20b486b00f21c60447` |
| `ghcr.io/frozen811/codex-lb:1.25.1` | OCI labels совпадают с `latest`; digest этого alias отдельно не снимался | Не проверен отдельно |
| `ghcr.io/frozen811/codex-lb:v1.25.0-hardened.3` | `deed76bab5fafa36051c2cf474a1b29055988aae` | `sha256:523445b9dda838f4ab00d920be913b0bc81f6510033cac7a2a3b04605d0311f6` |
| `ghcr.io/frozen811/codex-lb:1.25.0-hardened.3` | Alias подтверждён тем же index digest | `sha256:523445b9dda838f4ab00d920be913b0bc81f6510033cac7a2a3b04605d0311f6` |

- Во всех просмотренных manifests runtime platform — `linux/amd64`; второй `unknown/unknown` — attestation, а не вторая CPU-архитектура.
- README рекламирует hardened.3, но команда форка на строке 50 использует `latest`; production compose на строке 18 закрепляет `1.25.1`. OCI labels этих двух вариантов указывают на более старый `f622c563`, без live-hardening commit `deed76ba`.
- Причина в текущем publish workflow подлежит исправлению отдельно: raw `latest` включается только для default-branch context, выпуск запускается от release; наличие опубликованного hardened-тега не обновляет эти aliases автоматически.
- F-010/IMG-01/IMG-02/REL-01/DOC-01 не закрыты. Нужны согласованная схема версии/aliases, release gates на проверенный SHA, проверка реального артефакта и только затем отдельно разрешённая публикация.

### 13.5. Следующие проверки

1. После отдельно запрошенного коммита/push — Actions точного исправляющего SHA; до этого локальные результаты не заменяют cloud gates.
2. **INC-01/INC-08:** фактический путь Codex → proxy → account и расход после Pause. Новые refusal-тесты подтверждают узкую admission-инварианту; они не доказывают причину пользовательского наблюдения, отсутствие фонового/прямого трафика или мгновенную отмену уже начатой генерации.
3. **F-010/F-006:** версия, Docker aliases и gate публикации; full artifact smoke/update/rollback остаётся впереди.
4. **F-011:** переносимое форматирование архитектурной диагностики на Windows. **F-005:** quarantine/order dependence. Остальные OAuth/fan-out/signing/reset и полный исходный реестр остаются в очереди.

## 14. Маршрутизация, Pause и расхождение квот — 2026-10-01

### 14.1. Уточнение пользовательского случая

Пользователь уточнил: codex-lb был запущен локально; точная версия Codex неизвестна; по его пониманию квота закончилась, а панель ещё показывала около 11%. Поэтому исходный INC-08 не переопределяется как доказанный post-Pause расход. Для расхождения источников/окон/времени измерения добавлен **INC-10-QUOTA-DISPLAY**. INC-01, INC-08 и INC-10 остаются открытыми.

Проверено только чтением, без изменения клиентской конфигурации или запуска сервера:

- Текущий пользовательский `C:/Users/ext/.codex/config.toml`: `model_provider = "codex-lb"`, endpoint провайдера `http://127.0.0.1:2455/backend-api/codex`, `wire_api = "responses"`, `requires_openai_auth = true`; top-level `chatgpt_base_url` отсутствует. Это состояние файла сейчас, а не доказательство effective config исторического клиента или его профиля.
- Сейчас порт **2455 не слушается**. Установленный Windows package OpenAI.Codex — **26.928.3736.0**; это не устанавливает версию клиента в момент жалобы.
- Найденный default store `C:/Users/ext/.codex-lb/store.db` прочитан через SQLite `mode=ro` и `PRAGMA query_only=ON`. В нём **нет аккаунтов и request logs**, Pause events отсутствуют; настройки — `capacity_weighted`, sticky включён, single-account не задан. Этот store нельзя сопоставить со скриншотом и считать БД того инцидента.
- Токены, содержимое auth-файлов и encryption key не читались. Процессы и аккаунты не запускались и не менялись.

### 14.2. Подтверждённый независимый дефект — F-012

**Воспроизведение до правки:** публичный `/v1/responses` WebSocket завершил первый turn; `POST /api/accounts/{id}/pause` вернул 200; второй turn на том же socket получил `response.created` вместо отказа. Аккаунт был выбран реальным load balancer из test DB; подменены только token refresh и upstream transport. Это доказывает bypass для нового dispatch, но не причину пользовательского расхождения квот.

Исправление в [_service/websocket/mixin.py](app/modules/proxy/_service/websocket/mixin.py): перед binding/send каждого нового `response.create` проверяется существующий routing availability marker, **после** асинхронного ожидания admission. Устаревший ACTIVE snapshot открытого socket не даёт права отправить новый запрос после видимого Pause.

- Anchored turn получает `previous_response_owner_unavailable`, fresh turn — `upstream_unavailable`; используются существующие terminal error/cleanup paths.
- Освобождаются reservation и create lease только отказанного unsent turn. Новый health penalty и перенос account-owned payload на другой аккаунт не добавлены.
- Shared socket остаётся открыт: ранее отправленный ответ может закончиться. Немедленная отмена генерации или замораживание upstream quota не обещаются.
- Pure in-memory lookup использует существующий local overlay и peer snapshot; дополнительных DB reads, settings, migrations или изменений cache-invalidation bound нет.

OpenSpec: [2026-10-01-guard-paused-websocket-dispatch](openspec/changes/archive/2026-10-01-guard-paused-websocket-dispatch), [verification.md](openspec/changes/archive/2026-10-01-guard-paused-websocket-dispatch/verification.md). Итоговый нормативный контракт и context синхронизированы с [account-routing](openspec/specs/account-routing/); change архивирован после локальной проверки, все 6 tasks завершены.

### 14.3. Проверки второго блока

| Проверка | Итог |
|---|---|
| Новая regression matrix | **24 passed**: 2 ingress routes × fresh/anchored × 6 состояний: Pause между turns, после connect, во время create admission, при in-flight ответе, peer-only paused snapshot, удалённый account в snapshot |
| Весь `tests/integration/test_proxy_websocket_responses.py` | **212 passed** за 184.53 s; включает новые 24 regression cases, ownership, replay, terminal/settlement, admission и transport behavior |
| `test_codex_backend_passthrough.py` + `test_codex_usage_api.py` + `test_cache_invalidation_bus.py` | **111 passed** за 70.32 s; реальные loopback upstream stubs, HTTP passthrough, pooled usage, cached binding refusal и межрепличная инвалидация |
| `test_proxy_utils.py -k 'revalidate_open_websocket or reused_direct_websocket or (websocket and (reservation or sequential or owner_switch))'` | **8 passed**, 1452 deselected |
| Ruff `check app tests`, format изменённых Python-файлов | **PASS** |
| Architecture и simplicity checkers | **PASS**; thresholds/allowlists архитектуры не ослаблены |
| OpenSpec | Strict delta **PASS**; после sync/archive — **68 main specs passed / 0 failed** |

Итого **331 passed** в трёх непересекающихся наборах этого блока. Число 24 входит в 212; оно не добавляется повторно. Наборы частично пересекаются с ранее зарегистрированными 333 тестами первого блока, поэтому общий уникальный итог не суммируется.

Промежуточные ошибки проверки сохранены как ошибки, а не засчитаны зелёными:

- Начальный тестовый Pause с loopback peer и Host `testserver` получил 401: locality действительно требует подходящий Host. Стенд использует Host `localhost`, не отключает dashboard auth.
- Новый guard выявил несовместимость transport-only fixtures с initial пустым snapshot: выдуманные mock account IDs не находятся в test DB. File-scoped fixture оставляет **только первый пустой startup snapshot** unseeded; дальнейшие native refreshes и missing-account refusal не подменяются. Реальные regression cases явно seed/refresh snapshot; peer/deletion cases доказывают отказ без local mark.
- Промежуточный WebSocket прогон: **203 passed / 1 failed**. Sequential stub заранее отдавал первый ответ, а на first send — уже второй. Стенд теперь отдаёт каждый response batch после соответствующего send и seed-ит routing account; исходные dispatch-owner и payload assertions сохранены. Финальный полный файл: **212 passed**.
- Промежуточный neighboring прогон: **101 passed / 10 failed** только на log assertions — параметр запуска `log_level=ERROR` отфильтровал нужные INFO/DEBUG записи. Повтор без override: **111 passed**; файлы passthrough/usage/bus не менялись.

### 14.4. Что установлено о quota display и что ещё требуется

[client-setup.md](docs/client-setup.md) и [codex-backend-passthrough context](openspec/specs/codex-backend-passthrough/context.md) различают endpoint генерации провайдера и `<chatgpt_base_url>/wham/usage`; описанное клиентское наблюдение в context снято на **Codex 0.157.0**. Поэтому расход через пул и счётчик аккаунта логина могут показывать разные значения. Отсутствие top-level `chatgpt_base_url` в текущем файле — направление проверки, а не установленная причина исторического сообщения.

[Официальный configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) подтверждает отдельные provider/backend keys и необходимость пользовательского уровня для этих параметров. Эта страница сама по себе не доказывает quota-display behavior конкретной установленной desktop версии. Проверки форка подтверждают его ответы и отказ после Pause; клиентский UI в реальном проблемном запуске ещё не проверен.

Для закрытия INC-01/INC-08/INC-10 нужны effective client config/version, SHA/digest реально работающего сервера и корреляция generation/usage запросов со временем Pause и одинаковым quota window. Текущий пустой default store для этого не подходит. Нельзя исправлять процент в UI предположением или объявлять весь routing сломанным по счётчику одного аккаунта.

Следующий доступный локально блок: **F-006/F-010 — release gates, версии Docker aliases и фактические артефакты**. Cloud CI по новым правкам ещё отсутствует: коммит, push, публикация и deployment не выполнялись.

## 15. Полная проверка установки и Docker форка

Дополнение пользователя от **2026-10-01**: проверить весь Docker, используемый форком, всё описание проекта и каждый заявленный способ установки, чтобы пользователь и владелец форка могли установить и запустить его по понятным, рабочим инструкциям. Этот блок входит в общий аудит наряду с проверкой исправлений другого агента. Исправление workflow публикации само по себе не закрывает установку, сеть, конфигурацию или документацию.

### 15.1. Инвентаризация всех вариантов

Перед проверкой собрать команды и ссылки из README (включая переводы), COMMUNITY_RELEASE.md, GitHub About/Topics/Homepage, опубликованного сайта, Release notes, пакета GHCR, docs/, скриптов запуска и deployment-файлов. Каждый найденный дополнительный вариант добавить отдельной строкой; отсутствие инструкции отмечать как пробел. Команда должна устанавливать именно **Frozen811/codex-lb** с известной версией/SHA/digest.

| ID | Вариант | Что проверить | Статус |
|---|---|---|---|
| INSTALL-01 | Готовый GHCR image через `docker run` | Полный copy/paste путь от чистой машины; public pull без developer PAT; правильные fork/tag/digest; dashboard и OAuth ports; постоянный volume; restart/healthcheck; версия и владельцы файлов | PUBLIC DIGEST ПРОВЕРЕН linux/amd64: anonymous pull, named bridge, ports, readiness/assets, non-root, data/key recreate; runtime/OCI drift и отсутствие HEALTHCHECK раскрыты. Новые aliases/fixes F-010 не опубликованы, реальный OAuth не проверен; §19 |
| INSTALL-02 | Локальный `docker build` | Dockerfile, `.dockerignore`, все стадии и base images; Bun/Python/Rust/uv версии; locked dependencies; frontend/native helper; build context без локальных credentials/worktrees; non-root runtime; реальные заявленные CPU/OS платформы | ЛОКАЛЬНО ПРОВЕРЕНО linux/amd64: context/build/runtime/volume recreation/healthcheck; F-015/017, §18. ARM64/public artifacts/real Codex не проверены |
| INSTALL-03 | Обычный Compose | Каждый основной Compose-файл, image/build/pull semantics, command/entrypoint, env-file пути, volume names и permissions; запуск из чистого клона; готовность сервиса и повторный старт | ЛОКАЛЬНО ПРОВЕРЕНО: root dev §18 + PostgreSQL/MySQL profile SQL/migrations/recreate, explicit URL, invalid access/DNS refusal; isolated PG16→18 helper rehearsal сохранил synthetic row; F-020/021, §19 |
| INSTALL-04 | Development Compose | Frontend/backend proxy и адреса, hot reload, native helper, frontend assets, dev volumes и порты; инструкция должна ясно объяснять назначение режима | ЛОКАЛЬНО ПРОВЕРЕНО: clean source без env/deps, оба builds, TSX/Vite, proxy, watch/restart/recreate и cleanup; F-015/016, §18. DB profiles остаются INSTALL-03/05 |
| INSTALL-05 | Production Compose / PostgreSQL | Реальный запуск по опубликованной инструкции; доступ к внешней DB из контейнера, TLS/DNS, migrations/readiness, secrets/env, backup/restart; image против local build; single-replica ограничения | ЛОКАЛЬНО ПРОВЕРЕНО: normal up builds source, default SQLite, external PG без TLS и verify-full TLS, migrations/check/readiness/recreate, invalid password/DNS/certificate refusal. SQL restore + matching key и DB reconnect — §19; настоящий remote production endpoint отдельно |
| INSTALL-06 | Wheel из GitHub Release через pip | Правильная ссылка и версия форка; чистая venv на поддерживаемых ОС; зависимости, console scripts, frontend/config/migrations; импорт и старт вне checkout; сеть и подключение Codex | PUBLIC ПРОВЕРЕН Windows/Python 3.13: actual pip + uv pip, CLI/migrations/readiness/assets вне checkout, root code соответствует tag после newline normalization; historical runtime drift раскрыт. Real OAuth/Codex/native Linux/macOS отдельно; §20 |
| INSTALL-07 | Sdist / source archive из Release | Метаданные, состав без чужих worktrees и credentials, сборка wheel из sdist, установка вне checkout, dashboard/config/migrations; скачивание и инструкции | PUBLIC ПРОВЕРЕН: clean rebuild/install/startup, но 5967 nested worktree entries и runtime drift остаются в старом asset. Исправленный local sdist также исключает nested markers, содержит build hooks/assets и перестраивается без Bun; F-014/023, §20 |
| INSTALL-08 | `uv` / `uvx` / установка из индекса | Каждая заявленная команда и канал: действительно ли устанавливает форк, а не upstream `codex-lb`; version pinning, runtime deps, config/data directory и дальнейшие обновления | ПРОВЕРЕНО Windows: isolated uvx/uv tool public wheel, source replacement сохраняет data/key; corrected published Git SHA install PASS. Editable-only uv sync exemption проверен после cloud failure; §20 |
| INSTALL-09 | Запуск из Git checkout | clone URL/ref форка, `uv sync --frozen`, frontend и Rust prerequisites, подготовка assets, CLI/start команды; чистое окружение без существующей `.venv` и кешей разработчика | НЕ ПРОВЕРЕНО |
| INSTALL-10 | Windows скрипты / Desktop + WSL | `run.ps1`, `start.bat` и остальные найденные entrypoints; пути с пробелами, PowerShell/cmd синтаксис, prerequisites, Docker Desktop/WSL границы, firewall и startup failures | НЕ ПРОВЕРЕНО |
| INSTALL-11 | Linux/macOS скрипты | `run.sh` и документированные команды; shell/permissions, Python/native helper архитектура, env/config paths, background/foreground/restart и корректный выход | НЕ ПРОВЕРЕНО |
| INSTALL-12 | Helm / Kubernetes | Fork chart/package/image repository и version; values, secrets, PVC/DB, migrations, probes, service/ingress/OAuth/TLS/WS; clean install, upgrade, rollback; одиночный и документированный multi-replica режим | НЕ ПРОВЕРЕНО |
| INSTALL-13 | Nix / flake | Все опубликованные `nix run`/build команды, fork URL/ref, locked inputs, Python/native/frontend contents, runtime/data paths; доступность реального Nix стенда | НЕ ПРОВЕРЕНО |
| INSTALL-14 | Прочие найденные способы | System service, reverse proxy, удалённый сервер, установщик или сторонняя инструкция — отдельная карточка на каждый реально обещанный путь | НЕ ПРОВЕРЕНО: требуется завершить инвентаризацию |
| INSTALL-15 | Distroless и все дополнительные Docker targets | `Dockerfile.distroless`, inline Dockerfile frontend в `docker-compose.yml`, CI build/smoke targets и все найденные overrides; отдельно entrypoint/native helper/CA certificates/non-root/healthcheck, диагностика без shell и реальные платформы | ЛОКАЛЬНО ПРОВЕРЕНО найденных app/frontend targets на linux/amd64; distroless UID 65532, CA/native/healthcheck/recreate, CI delta валиден. Новый cloud CI/CVE scan/ARM64 остаются открыты; §18 |

Docker-инвентарь включает также образы зависимостей в Compose/Helm/CI: PostgreSQL, MySQL и остальные реально используемые сервисы; их версии, readiness, сети, volumes, credentials и совместимость проверяются в контексте каждого соответствующего способа установки. Developer/CI image не считать готовым образом для обычного пользователя. На текущем checkout `docker-compose.yml` содержит development frontend/backend; отдельный `docker-compose.dev.yml` не найден — не придумывать такой файл в инструкции.

### 15.2. Общая матрица конфигурации, сети и клиентского пути

- [ ] **SETUP-01:** повторить точные команды каждого варианта на чистом стенде; записать prerequisites и время до первого рабочего dashboard. Убрать необходимость угадывать URL, путь, имя volume или команду запуска.
- [ ] **SETUP-02:** проверить источники и precedence конфигурации: env-файлы и `CODEX_LB_ENV_FILE`, рабочий каталог, CLI/env, defaults и настройки панели; допустимые и ошибочные значения, сообщения об отсутствующем обязательном параметре. Проверить применимость `.env.example` к каждому режиму.
- [ ] **SETUP-03:** проверить data directory, SQLite/PostgreSQL/MySQL в заявленных вариантах, migrations, encryption key, ownership/permissions и сохранение accounts/settings после recreate/update. Backup/restore и rollback проверять на отдельной тестовой БД, не на пользовательском store.
- [ ] **SETUP-04:** проверить host/container/client endpoints; loopback и `0.0.0.0`, порты **2455/1455**, port collision, DNS и доступ к upstream; Docker bridge, `host.docker.internal`, WSL/Windows и LAN/remote сценарии. Не рекомендовать контейнерный `localhost` для внешней DB/сервиса без проверки адресации.
- [ ] **SETUP-05:** проверить HTTP/SSE/WebSocket через прямой доступ и документированный reverse proxy; TLS certificates/trust, proxy env, timeouts/idle disconnect/reconnect, firewall и failure diagnostics. Для сетевой ошибки записывать точный этап, HTTP envelope/код и безопасный фрагмент логов.
- [ ] **SETUP-06:** проверить локальную и удалённую dashboard authentication, bootstrap/password/API keys, OAuth callback/port и импорт аккаунта. Подтвердить, что инструкция работает без публикации токенов и без отключения обязательной защиты.
- [ ] **SETUP-07:** подключить поддерживаемый Codex по docs/client-setup.md: effective provider/config, generation и usage endpoints, URL suffix, required auth, HTTP/WS compatibility. На тестовом стенде подтвердить запрос через форк, выбор аккаунта, quota windows и Pause; версия клиента обязательна в evidence.
- [ ] **SETUP-08:** выполнить документированные update/restart/recreate, сохранить данные и проверить версию после обновления; отдельно rollback с ограничениями совместимости БД. Проверить cached `latest`, pinned tags/digests и отсутствие скачивания upstream вместо форка.
- [ ] **SETUP-09:** доказать работу readiness/healthcheck и graceful shutdown; проверить неправильный env, недоступную DB, отсутствие assets/native helper, занятый порт и недоступный upstream. Инструкция должна дать проверяемую диагностику и путь восстановления.
- [ ] **SETUP-10:** разделить реально проверенные OS/architectures/topologies и непроверенные обещания. `unknown/unknown` attestation не считать ARM64 поддержкой; отсутствие стенда указывать явно.

### 15.3. Проверка описания и простоты установки

- [ ] **DOC-INSTALL-01:** сверить GitHub About, README/переводы, COMMUNITY_RELEASE, release assets/notes, GHCR description, docs navigation и deployment примеры с одним актуальным описанием форка и owning OpenSpec capabilities.
- [ ] **DOC-INSTALL-02:** для всех ссылок/команд проверить owner/repository/version/channel; выявить `uvx codex-lb`, Nix/Helm/image или release URL, которые ведут на upstream. Не заменять ссылку на форк, пока соответствующий fork artifact не существует и не проверен.
- [ ] **DOC-INSTALL-03:** проверить каждую команду copy/paste в её заявленной оболочке; Windows/PowerShell переносы и quoting, Bash quoting, абсолютные/относительные пути и config examples; зафиксировать успешный результат, а не только синтаксическую валидность.
- [ ] **DOC-INSTALL-04:** выбрать основной короткий способ установки после проверки; рядом указать требования, открытие панели, добавление аккаунта, подключение Codex и обновление. Остальные варианты должны иметь понятное назначение и проверенную инструкцию.
- [ ] **DOC-INSTALL-05:** исправить неподтверждённые обещания «всё исправлено», «100%», «поддерживается» и «проще», сопоставив их с evidence и ограничениями; F-007 остаётся открытым до проверки исходного реестра.
- [ ] **DOC-INSTALL-06:** изменения поведения установки сначала оформить в OpenSpec; пользовательские страницы docs/ связать с owning capability, пояснения — в context. Новые README feature sections и ручные правки CHANGELOG не добавлять.

### 15.4. Условия завершения и порядок

Сначала закрыть источник/CI/версию публикации, затем **готовый GHCR image → основной Compose → GitHub wheel/sdist → запуск из исходников и Windows → остальные заявленные варианты**. Параллельно исправлять подтверждённые неправильные команды и ссылки, не рекламируя ещё не опубликованный артефакт.

Для каждой строки сохранять: точную инструкцию/источник, commit SHA и artifact digest/version, OS/CPU/shell и версии инструментов, обезличенную конфигурацию и сетевую топологию, команды и exit codes, наблюдаемый readiness/dashboard/client результат, найденный дефект/F-ID, правку и повторную проверку, оставшиеся ограничения. Проверка сборки не заменяет установку; открытие панели не доказывает генерацию и routing; локальная проверка не заменяет текущий Actions run.

Весь блок считается проверенным только когда каждый заявленный способ воспроизведён на подходящем стенде либо снят с обещаний документации с обоснованием. Непроверенную платформу, публичный artifact, реальный Codex или внешнюю DB не закрывать по аналогии с соседним вариантом.

## 16. Docker-теги, версии артефактов и CI gate — 2026-10-01

### 16.1. Повторный публичный срез

GitHub main остаётся `7ec39f82709ee1ca4c00489a8d5fc301d49320ed`. Его [CI run 36761400788](https://github.com/Frozen811/codex-lb/actions/runs/36761400788) — `completed/failure`; Release guards и Simplicity budgets зелёные, но это не заменяет CI. Read-only вызов **того же** `verify_source_checks()` нового gate против живого API отказал: `source workflow is not successful: ci.yml (completed/failure)`. Тег для этой проверки не создавался: это проверка реального source-CI, не end-to-end запуск новой публикации.

| Public artifact | Повторно проверенный результат |
|---|---|
| GHCR `latest`, `1.25.1` | OCI revision `f622c5632013d24ce9236d176113087b387c7990`, version `1.25.1`; latest index digest `sha256:ad9aa84b12bce9f6afc63adb3aa86e73f6aafca1814e6f20b486b00f21c60447` |
| GHCR `v1.25.0-hardened.3` | OCI revision `deed76bab5fafa36051c2cf474a1b29055988aae`, version `1.25.0-hardened.3`; index digest `sha256:523445b9dda838f4ab00d920be913b0bc81f6510033cac7a2a3b04605d0311f6` |
| Image platforms | `linux/amd64` плюс `unknown/unknown` attestation; последнее не подтверждает ARM64 |
| [hardened.3 release](https://github.com/Frozen811/codex-lb/releases/tag/v1.25.0-hardened.3) | Public, `prerelease=false`; wheel и sdist называются `1.25.1` |
| Published wheel | Metadata `codex-lb==1.25.1`, `app/__init__.py` **1.25.0-beta.9**; HTML/JS/CSS присутствуют; SHA256 `4af955c73887193d9592d0baf8e638bdec80051f6df5bad8e78e663abd9ad0bf` |
| Published sdist | PKG-INFO `1.25.1`, runtime **1.25.0-beta.9**; **5967 entries** под `.kilo/worktrees`; SHA256 `24c965ff57aecead9e15b3a24159857b0c53c9307d7966bc8b4aae87cd3ce744` |

Исторические архивы скачаны в отдельный temporary audit directory и проверены через zip/tar metadata без запуска их кода. Их полная корреляция с tagged source и установка остаются задачами INSTALL-06/07. Текущие публичные aliases/releases не изменялись; **F-010 остаётся открытым**.

### 16.2. Локальные исправления

- `.github/workflows/docker-publish.yml`: вместо branch/default checkout и ungated push — fork-only source gate, обязательный dispatch `tag`, checkout immutable SHA, managed-version validation, сборка и smoke wheel/sdist/локального image, повторный gate, затем login/upload/push. Весь workflow сериализован между разными тегами, actions закреплены SHA.
- `scripts/guard_fork_release.py`: supported tag parsing, annotated/lightweight tags, привязка tag к текущей main и event/initial SHA, newest exact-source **main push** для CI/release guards/simplicity, успешный `CI Required` текущего attempt; missing/pending/failure/cancelled/skipped/stale/PR-only/API error/incomplete pagination → отказ. Не фильтрует только successful runs. Отклоняет несовпадающий prerelease flag, существующие assets и более старый stable при наличии более нового valid stable release.
- Docker публикует два exact tags (`vX.Y.Z…`, `X.Y.Z…`) из **того же загруженного и проверенного образа**; beta/alpha/rc не двигают stable aliases. Stable `latest`, `X`, `X.Y` двигаются после upload packages и exact-image pushes. Существующие exact tags не перезаписываются; нераспознанная ошибка registry lookup тоже блокирует публикацию.
- `scripts/verify_release_artifacts.py`: archive filenames/metadata, Python source и frontend bytes против checkout, sdist managed files, отказ на duplicate/unsafe/worktree/env entries; SHA256SUMS для wheel/sdist и JSON source/CI provenance. Не запускает извлечённые архивные скрипты.
- `scripts/smoke_release.py`: версии distribution/runtime и installed source hashes, CLI вне checkout, temporary SQLite/data/key, readiness/dashboard/JS/CSS; startup reset допускает retry, умерший процесс вызывает быстрый отказ, spawned process tree убирается на Windows.
- `app/__init__.py` и оба Helm fields согласованы с существующей project/frontend/uv версией **1.25.1**. Это исправление drift, не bump нового релиза. Bun в основном Dockerfile согласован с workflow/package manager **1.3.14**; inline Compose и distroless ещё входят в INSTALL-15.
- `pyproject.toml`: sdist `only-include` выбирает explicit root inputs; новый archive не обходится через nested agent checkout. Source archive умеет собрать wheel с frontend assets.
- Failure/cancellation cleanup делает связанный GitHub release draft, включая отказ source gate. Upload без `--clobber`; upstream PyPI/Helm publication не включена. Исторические неправильные теги новый publisher намеренно не принимает.

### 16.3. Проверки и ограничения

| Проверка | Итог |
|---|---|
| Новый release regression file + release_versions/stable guard/beta guard/CI workflow required checks | **115 passed**, из них **54** новых cases; 1 существующий Starlette deprecation warning |
| Ruff check/format и scoped `ty` новых Python файлов | **PASS**; после уточнения типов fixture повторно **54 passed** в новом файле, это не дополнительный уникальный набор поверх 115 |
| actionlint **1.7.12**, official Windows asset с проверенным checksum | **PASS** для fork workflow; optional shellcheck/pyflakes отключены, Python отдельно проверен Ruff |
| `scripts.verify_release_version --tag v1.25.1` | **PASS**, все 6 managed fields согласованы |
| Bun frontend build; `uv build`; archive parity | **PASS**; final local wheel 3,400,427 bytes, sdist 4,430,777 bytes, nested worktree entries **0** |
| Clean installed wheel | **PASS** distribution/runtime/source parity, readiness, HTML/JS/CSS, isolated DB и cleanup |
| Clean installed sdist, отдельная fresh venv и `--no-cache --link-mode copy` | **PASS** rebuild/install, parity, readiness, HTML/JS/CSS и cleanup |
| Основной Dockerfile local build `linux/amd64` | **PASS**, image `codex-lb-release-audit:20261001`, ID `sha256:95f4eb8ff34bfb2aadef80bec672d172dda1f94ee4349532496e99937740cae4`; version `1.25.1`, revision marker `local-uncommitted` |
| Изолированный container smoke | **PASS**: tmpfs, random loopback port, version, readiness, dashboard HTML/JS/CSS; container удалён, production volumes не использовались |
| Architecture / simplicity budgets | **PASS**, лимиты не ослаблены |
| OpenSpec | Strict delta **PASS**; после sync/archive — **68 main specs passed / 0 failed**, см. verification.md |

Среда локальной package проверки: Windows, CPython **3.13.12**, uv **0.12.17**. Docker runtime Python — 3.14 base; запуск прошёл отдельным container smoke. Это не проверки всех OS/архитектур или production DB.

Автоматическая проверка заблокировала удаление двух temporary directories предыдущих smoke failures (`blocked by policy`, без подробной причины). Они оставлены; активные серверы/container этих прогонов не сохранены. Это ограничение housekeeping, не успешный cleanup тех двух промежуточных запусков.

Промежуточные неуспехи не считать зелёными: первый startup reset; inherited log-handle cleanup на Windows; первоначальный `include` selector также выбирал одноимённые файлы внутри worktree (заменён `only-include`); cached sdist install содержал `app/main.py` целиком из NUL bytes. Hash checkout/wheel/sdist одинаковый, исходный `main.py` без NUL; повреждён был installed file. Fresh no-cache install прошёл, источник повреждения кеша **не установлен**. Дополнительная post-install hash проверка подтверждённо отвергает такое окружение до запуска сервера. Это не объявляется дефектом содержимого исходного sdist или уже доказанным багом uv.

OpenSpec change: [guard-fork-release-publication](openspec/changes/archive/2026-10-01-guard-fork-release-publication/), нормативный контракт/context: [release-management](openspec/specs/release-management/).

### 16.4. Решение о выпуске и следующий этап

Пользователь прямо делегировал выбор времени выпуска; разрешение сохранено для этого форка. **Сейчас релиз не выпускается**: cloud main CI красный, локальные правки не имеют опубликованного SHA и новая цепочка Actions ещё не запускалась. При готовности кандидат должен иметь согласованный новый supported tag, green exact-source CI и применимые review/soak prerequisites; исторический `1.25.1` image не перезаписывать свежими неподписанными догадками.

Коммиты/push/merge, workflow dispatch, новые tags/releases, публикация GHCR/PyPI и deployment здесь не выполнялись. Локально исправленный F-006 не означает уже действующий запрет на GitHub. Cleanup после частичного release upload не является атомарным rollback GHCR; aliases могут обновиться частично при сетевом отказе. Final gate не блокирует будущий rerun/main change после API read. Эти ограничения отражены в owning context.

Далее: проверка оставшихся red-CI причин и cloud execution на исправляющем SHA; полный install audit раздела 15 с приоритетом готового Docker/Compose и всех fork/upstream ссылок. Реальный пользовательский quota/routing incident, весь ISSUES.md и F-007 ещё не закрыты.

## 17. Пакет из трёх задач: F-005, F-011, F-008 — 2026-10-01

Исходный и повторно проверенный опубликованный main: `7ec39f82709ee1ca4c00489a8d5fc301d49320ed`. Правки этого пакета локальные, без исправляющего commit SHA. Предыдущие незакоммиченные правки сохранены.

### 17.1. F-005 — источник нестабильного quarantine assertion

Получен исходный лог [integration-core-1](https://github.com/Frozen811/codex-lb/actions/runs/36761400788/job/110044676866): падает **`local_deadline == 700.0`**, значение `1599.9891250133514`. Это assertion тестового helper до проверки итогового срока карантина.

Принудительное принятие durable poison row между persistence и local arm воспроизвело **1599.960518360138** на Windows. `arm` возвращал aggregate `quarantined_until`, включающий durable cooldown и half-open lease. Локальный weaker fence при этом имеет собственный срок 700. Ошибочный вывод о локальном cooldown зависел от порядка reader tasks во время persistence await.

Исправлен только shared test helper: poison возвращает `local_poison_until`, weaker при сохранённой poison classification — `suppressed_weaker_until`. Runtime карантина, cooldown и cleanup не менялись. Responses route test дополнен `local-first`/`durable-first`: **48 комбинаций** evidence × load/retry × completion outcomes × order вместо 24. Итоговые assertions не ослаблены: после успешного settlement+registration локальный запрет остаётся ровно до 700, а принятая durable составляющая снимается; failed settlement/alias registration сохраняют poison. Проверены first-strike и replacement-owner cases.

### 17.2. F-011 — portable architecture diagnostics

`scripts/check_proxy_architecture.py` формирует diagnostic paths через `.as_posix()`, сохраняя repository-relative и outside-root absolute identity. Нормативные thresholds, AST checks и порядок сообщений не менялись.

Baseline **10 failed / 4 passed**, после исправления и двух Windows/POSIX regression cases — **16 passed**. Invalid source/spec cases по-прежнему проваливают checker, независимые проверки продолжаются. Сам checker на текущем dirty tree также прошёл.

### 17.3. F-008 — Windows Actions и startup proof

- Ручной запуск опубликованного старого workflow: [run 36874316285](https://github.com/Frozen811/codex-lb/actions/runs/36874316285), **success**, `workflow_dispatch`, SHA `7ec39f82709ee1ca4c00489a8d5fc301d49320ed`. Он проверил старые memory tests и `create_app` import; это baseline, не execution новой цепочки.
- Локальный `windows-startup.yml`: автоматические `push main`, PR source updates, `merge_group`, manual dispatch; read-only permissions, pinned actions, concurrency. Windows tests включают memory monitor, architecture diagnostics и launcher contract.
- Новый smoke строит dashboard через Bun **1.3.14**, собирает wheel, ставит в отдельный venv через `--no-cache --link-mode copy` и запускает shared smoke вне checkout. Каждый промежуточный native-command failure останавливает PowerShell step.
- Проверено реально на локальном Windows: новый wheel **1.25.1**, Python **3.13.12**, uv **0.12.17**, установленный source hash/runtime/distribution version совпадают, readiness и HTML/JS/CSS доступны, process-tree cleanup завершён. Artifact/venv оставлены в temporary audit folder `codex-lb-windows-batch3-5a9ac81722104a59a86e07e10dfdff1a`.
- Fork publication gate теперь требует **четыре** успешных newest exact-source main-push workflows: CI, release guards, simplicity и Windows startup. Missing/pending/failed/cancelled/skipped/stale/PR-only/manual-only Windows evidence блокирует публикацию. Regression coverage проверяет каждый workflow, включая отсутствие и подмену source/event/path.

Cloud execution **нового** Windows workflow и новых quarantine tests ещё предстоит после публикации исходников. Windows upstream transport, реальные аккаунты/Codex, OAuth, installation/network matrix §15 и quota incident этим пакетом не закрываются. Manual baseline success не удовлетворяет main-push prerequisite нового release gate.

### 17.4. Проверки и итог

| Проверка | Результат |
|---|---|
| Quarantine provenance/races/recovery-origin, Responses route | **69 passed**, включая принудительный прежде падавший durable-first порядок |
| Architecture unit diagnostics | **16 passed** |
| Fork publication, memory monitor, launcher unit tests | **93 passed** |
| Итого focused Python tests этого пакета | **178 passed**, без запуска полной suite |
| Ruff check + format check на шести изменённых Python files | **PASS** |
| Scoped ty для checker/release gate | **PASS** |
| Actionlint 1.7.12 для Windows и Docker publication workflows | **PASS** |
| Frontend build и свежий installed-wheel Windows readiness/assets smoke | **PASS** |
| Architecture / simplicity | **PASS**, thresholds/budgets не ослаблены этим пакетом |
| OpenSpec strict change + main specs | **PASS**, **68 main specs / 0 failed** |

OpenSpec: [repair-windows-and-quarantine-regressions](openspec/changes/archive/2026-10-01-repair-windows-and-quarantine-regressions/), owning requirements/context синхронизированы в `proxy-architecture`, `github-automation`, `release-management`. Quarantine контракт не менялся: исправлена ошибка измерения в regression helper.

**Решение:** F-005/F-011 исправлены локально; F-008 автоматизирован и проверен локально, плюс получен успешный published-baseline run. Не объявлять новое source CI зелёным до реального выполнения на опубликованном исправляющем SHA. В этом пакете был только диагностический workflow dispatch; commit/push/merge, release/tag, GHCR/PyPI publication и deployment не выполнялись. Полный Docker/install audit остаётся в §15; следующий пакет выбирать из открытых пунктов, включая F-007 и Docker/Compose installation paths.

## 18. Пакет INSTALL-02 / INSTALL-04 / INSTALL-15 — 2026-10-01

Проверены **локальная стандартная Docker-сборка**, **development Compose** и **distroless/inline frontend targets**. Правки остаются локальными, поверх прежних batches; новая публикация/исправляющий SHA отсутствуют. Среда: Windows + Docker Desktop Linux engine **29.8.1**, Compose **5.5.1**, runtime **linux/amd64**, Python в образах **3.14**, Bun **1.3.14**, uv builder **0.12.13**, Rust builder **1.96.0**. Не переносить результат на ARM64, Windows containers, production DB или публичный GHCR tag.

### 18.1. Найдено и исправлено

- **F-015:** root `.dockerignore` не исключал вложенные env/credential files и agent worktrees; у frontend context отдельного ignore-файла не было. Синтетический BuildKit `FROM scratch; COPY . /context` + local export подтвердил попадание `.kilo/worktrees`, `.codex/auth.json`, nested `.env.local`, `store.db-wal`, `.git/config`, `.npmrc`, encryption key; frontend допускал host node_modules и env. Использовались только inert markers, реальная утечка пользовательских credentials не утверждается. Добавлены root nested exclusions и `frontend/.dockerignore`; frontend watch исключает env/git/dependencies.
- **F-016:** distroless и inline Compose использовали Bun **1.4.2**, основной Dockerfile/package/workflows — **1.3.14**. Старый `1.4.2-alpine` реально существует, baseline extra-target builds проходят: это toolchain drift, не доказанная ошибка pull/build. Все frontend targets теперь согласованы с package manager и frozen lock.
- **F-017:** существующий CI Docker job строил только стандартный image и сканировал его, без readiness/assets smoke. Добавлены distroless build и isolated startup smoke обоих images: non-root ownership, tmpfs, random loopback port, readiness, HTML/JS/CSS, CA и native helper, trap cleanup. Existing standard-image Trivy gates сохранены. Новый job локально валиден, но не исполнялся в GitHub. В оба Dockerfiles добавлен shell-independent readiness healthcheck; distroless не требует shell.
- **F-018:** отдельная identity-проверка inline frontend показала **UID 0**. Добавлены `USER bun`, writable WORKDIR и `COPY --chown=bun:bun`; повторный полный Compose build/start/proxy/watch/recreate прошёл с **UID 1000**. Это изменение прав только development frontend; backend/distroless уже были non-root.

### 18.2. Доказательства установки и runtime

| Объект | Результат |
|---|---|
| Standard image | `codex-lb-install-audit-standard:20261001`, ID `sha256:7eb246b1597c2fd2952c10beeecb27da5dd5fed612cce1d9e009294c41475d1f`, linux/amd64 |
| Distroless image | `codex-lb-install-audit-distroless:20261001`, ID `sha256:15a8c3dc865c29c4b2dad74461274e8ae3a506916d52da15409fb18b575bbf86`, linux/amd64 |
| Inline development frontend | `codex-lb-install-audit-frontend:20261001`, ID `sha256:b9d9c92f8d1c1d201c96d687d03e0c13d68efaa911bdd737384d210087a5bbf0`, linux/amd64, USER **bun**, UID **1000** |
| Build contexts, baseline → fixed | Root: **7** forbidden markers присутствовали → **0**, **8** required source/lock inputs сохранены. Frontend: **5** присутствовали → **0**, **4** required inputs сохранены |
| Standard install/recreate | **PASS** twice: UID/GID **1000**, version **1.25.1**, 150 trusted CAs, native helper `--help` exit 0, writable named-volume data, readiness/HTML/JS/CSS, Docker health **healthy** |
| Distroless install/recreate | **PASS** twice: UID/GID **65532**, version **1.25.1**, 150 trusted CAs, native helper exit 0, shell отсутствует, writable named volume, readiness/assets и Docker health **healthy** |
| Persistent application data | Для обоих образов изменение `dashboard_settings.sticky_threads_enabled=0` в своей тестовой SQLite БД и hash encryption key сохранились после удаления/recreate контейнера. Ключ/credentials не выводились |
| Graceful stop | Все четыре standalone container stops дали exit **0**, OOMKilled **false** |
| Clean development source | Snapshot текущих tracked source edits + нужных новых build files, без `.env.local`, `.venv`, frontend/node_modules и пользовательского store. Оба Compose builds прошли |
| Development frontend/backend | **PASS**: Vite HTML, transformed `/src/main.tsx`, backend bundled assets, health через frontend → service DNS `server:2455` |
| Compose watch | **PASS**: frontend source sync, env/dependency markers не скопированы; backend source sync+restart наблюдался через новый StartedAt, readiness восстановлен |
| Development recreate | **PASS**: force-recreate server/frontend с тем же isolated volume, backend readiness и assets |
| Cleanup | Own standalone containers/volumes, test Compose project/network/volume и watch process trees убраны; итоговые выборки этих labels/names/PIDs пусты. Пользовательские контейнеры/volumes не использовались |

Аудитные скрипты, context exports, clean snapshots и build/watch logs сохранены в `C:\Users\ext\AppData\Local\Temp\codex-lb-install-batch4-20261001\`. Образы оставлены для повторной проверки. Это локальные Docker image IDs, не опубликованные registry digests и не source SHA.

Не скрывать промежуточные failures: первый smoke после watch смотрел на старый случайный host-порт; последующий probe захватил port до завершения async restart; `docker exec` мог попасть в момент остановки. Финальный стенд ждёт новый StartedAt, переносит exec через transient restart и заново разрешает ephemeral port до readiness. Windows termination только docker launcher оставлял watch child с project lock; проверенный owned PID/process tree остановлен, helper cleanup исправлен. Эти сбои audit helper не объявляются runtime дефектами codex-lb. Финальный полный Compose прогон завершился exit 0.

### 18.3. Документация и проверки

`docs/deployment/docker.md` теперь содержит fork source-build path, default local-image Basic run, назначение development Compose, optional env/minimum Compose, dashboard/backend/OAuth ports, proxy readiness, watch, named-volume/recreate и distroless Python diagnostics. Compose/OpenSpec links указывают на форк; убрано ошибочное утверждение о required `.env.local` и обещание watchtower-friendly immutable tags. Явно указано, что bare `uvx codex-lb` выбирает upstream PyPI, а локальная сборка не означает существования public distroless tag. Нормативные requirements/context синхронизированы в deployment-installation; README/CHANGELOG не расширялись.

Минимум optional `env_file.required=false` подтверждён [официальной документацией Compose](https://docs.docker.com/reference/compose-file/services/#required): **2.24.0**. Реальный прогон выполнен на 5.5.1; минимальная версия отдельно не запускалась.

- **20 focused unit tests PASS**: Docker networking, Postgres/MySQL Compose contracts и launcher contracts. Это не реальные PostgreSQL/MySQL installs.
- **Actionlint 1.7.12 PASS** для ci.yml; shell syntax smoke step проверен с Unix line endings. Существующие contexts и основной CI aggregate не переименованы.
- **Architecture / simplicity / git diff --check PASS**, thresholds/budgets не ослаблены.
- **Strict OpenSpec change PASS**, после sync **68 main specs PASS / 0 failed**.
- OpenSpec change: [repair-docker-install-targets](openspec/changes/archive/2026-10-01-repair-docker-install-targets/), см. verification.md.

### 18.4. Границы закрытия и дальше

Эти три installation paths **проверены и исправлены локально на linux/amd64**. Новый cloud Docker CI, ARM64, полный актуальный CVE scan обоих images, real account/OAuth/Codex traffic и network-switch сценарий этим пакетом не закрыты. Public aliases F-010, production PostgreSQL/MySQL/upgrade profiles, release wheel/sdist/uv/Nix/Helm и полный реестр claims F-007 остаются открытыми.

Коммит/push, новый workflow dispatch, release/tag, GHCR/PyPI publication и deployment не выполнялись. Source публикация и release/image публикация остаются разными действиями; локальная зелёная установка не разрешает выпуск без exact-source CI. Следующая тройка по приоритету: **INSTALL-01 public GHCR**, **INSTALL-03 ordinary Compose/profile configuration**, **INSTALL-05 production Compose/external PostgreSQL**, либо F-007 если выбран блок описания/claims.

Повторный live API check: public main всё ещё `7ec39f82709ee1ca4c00489a8d5fc301d49320ed`, newest exact-source main-push [CI 36761400788](https://github.com/Frozen811/codex-lb/actions/runs/36761400788) — **completed/failure**. Новый source ещё не публиковался; решение о релизе не меняется.

## 19. Пакет INSTALL-01 / INSTALL-03 / INSTALL-05 — 2026-10-01

Проверены публичный fork Docker digest, database profiles и server-only Compose. Исходный/public main остаётся `7ec39f82709ee1ca4c00489a8d5fc301d49320ed`; исправления локальные, поверх сохранённых предыдущих batches. Docker Desktop Linux engine **29.8.1**, Compose **5.5.1**, Linux/amd64. Аудитные скрипты, registry metadata, Compose fixtures и build/startup/schema/cleanup logs: `C:\Users\ext\AppData\Local\Temp\codex-lb-install-batch5-20261001\`.

### 19.1. INSTALL-01 — публичный образ и инструкции

Fresh anonymous GHCR token/manifest lookup и pull через пустой Docker config (без login/developer PAT) подтвердили:

| Public reference | Index digest | OCI source revision |
|---|---|---|
| `latest`, `1.25.1` | `sha256:ad9aa84b12bce9f6afc63adb3aa86e73f6aafca1814e6f20b486b00f21c60447` | `f622c5632013d24ce9236d176113087b387c7990` |
| `v1.25.0-hardened.3` | `sha256:523445b9dda838f4ab00d920be913b0bc81f6510033cac7a2a3b04605d0311f6` | `deed76bab5fafa36051c2cf474a1b29055988aae` |

У обоих indexes только **linux/amd64** runtime + `unknown/unknown` attestation. Latest/1.25.1 OCI version **1.25.1**, фактический runtime **1.25.0-beta.9**. В образе source-copy install: metadata установленной distribution `codex-lb` отсутствует, её версию не следует выдумывать из OCI label. Встроенного Docker HEALTHCHECK нет. Эти исторические artifacts не менялись — **F-010 остаётся открытым**.

Digest latest/1.25.1 запущен дважды на своей named bridge с isolated named volume и случайными loopback host-портами для 2455/1455. **PASS:** non-root UID 1000, writable data, migrations/startup, readiness, dashboard HTML/JS/CSS; synthetic dashboard setting и encryption-key hash сохранились после удаления/recreate контейнера, stop exit 0 и OOMKilled false. Это port publication, не реальный OAuth callback/login или Codex account traffic.

**F-021 исправлен локально:** README historical public command закреплён digest и раскрывает старый source; основной Quick Start и китайский перевод строят форк из checkout вместо upstream image. Existing comparison row больше не обещает актуальность fork latest. Docker guide даёт anonymous historical pull/source-build и ограничения версии/health/platform; COMMUNITY_RELEASE update guide различает source build, dev frontend, server-only Compose и public-image updates. README остался **221/225 lines, 10/10 headings**. Общие claims «100%» и остальная документация остаются F-007/DOC-INSTALL, а не считаются проверенными этим пакетом.

### 19.2. INSTALL-03 — PostgreSQL/MySQL и upgrade profile

Root development frontend/build/watch уже проверены в §18. Теперь реальные `postgres:18-alpine` (**18.6**, index `sha256:77f585114c32fbca283dc835b0596f4e52b51b4c6662d7810b2f4084f60a1873`) и `mysql:8.4` (**8.4.11**, index `sha256:6ea90827b1100f8f2ae306a539f86d2c264a26ed435a2a9f75551dd5c3aeb242`) проверены с source-built backend §18. Runtime fixture сохранил stock command, service network, DB profile/env/storage/health semantics; backend build заменён ранее проверенным локальным образом, frontend исключён из DB-only прогона. В production-проверке ниже backend действительно собирается через Compose.

- **PASS:** включение каждого DB profile без application URL оставляет backend на SQLite. Docs теперь прямо требуют `CODEX_LB_DATABASE_URL` в `.env.local`: service DNS `postgres:5432`/`mysql:3306` внутри Docker, loopback адрес для host clients. Profiles не переносят старые SQLite данные и не выбирают backend автоматически. После env edits требуется recreate; добавлены `up --wait` и предупреждение о development credentials.
- **F-020 воспроизведён:** MySQL `mysqladmin ping` вернул exit 0 при неверном пароле; PostgreSQL `pg_isready` — exit 0 при nonexistent user/database. Первая попытка SQL-пробы PostgreSQL на 127.0.0.1 также приняла неверный пароль: фактический `pg_hba.conf` использует loopback trust, а network connections — scram-sha-256.
- **Исправление:** обе health-пробы выполняют authenticated `SELECT 1` с runtime DB user/password/database. PostgreSQL использует container `$HOSTNAME`, избегая default loopback trust. **PASS:** корректный доступ, отказ при неверном пароле и nonexistent database. Явно выбранный оператором trust policy существующего volume probe не превращает в password policy.
- **PASS:** каждый selected SQL backend прошёл migrations до `20260928_020000_add_request_logs_facet_indexes`, readiness/HTML/JS/CSS и `python -m app.db.migrate check`. Application engine действительно сообщает PostgreSQL/MySQL и `codex_lb`; отдельный SQL client внутри DB подтвердил сохранённую synthetic setting, fresh app volume не создал SQLite store.
- **PASS:** для каждой DB два поколения app container сохраняют remote setting и encryption-key hash. Неверный application password и `.invalid` DB DNS вызывают nonzero startup exit до readiness, а не fallback к SQLite.

Отдельно проверен **postgres-upgrade** с pinned helper digest `48b44882565694a297c62b07e8384b89c0e4264b169b67a655569974752327d0`: PostgreSQL **16** synthetic root-layout volume, остановка writer, offline tar backup, отказ обычного 18 service через legacy PG_VERSION guard, actual one-shot upgrade, затем здоровый PostgreSQL **18.6** с неизменной synthetic row. Образ PG16 index: `sha256:721873c34ceb9f8d8fc265984940dc982404c105f19ad51be9fdc5970a6080ea`. Tar содержимое проверено, restore этого tar не выполнялся; production-size/custom extensions/nested alternative layouts отдельно. Этот тест не трогал реальную БД пользователя.

### 19.3. INSTALL-05 — source selection, external PostgreSQL, TLS и restore

**F-019 воспроизведён:** исходный production Compose с `build` + `image: ghcr.io/frozen811/codex-lb:1.25.1` на обычном `up -d` запустил кешированный historical image, а не checkout. Source fixes могли не попадать в установленное приложение. `docker-compose.prod.yml` теперь использует **`image: codex-lb:local` + `pull_policy: build`**; local build не обозначается published release. Header/docs согласованы: SQLite по умолчанию, внешний PostgreSQL опционально.

Проверен actual Compose build/up с isolated local image name/ports/volumes: перед стартом local tag намеренно указывал на historical image; после normal up container bytes `websocket/mixin.py` совпали с текущим checkout, historical image заменён source build. Образ финального TLS стенда: `codex-lb-batch5-prod-tls:local`, ID `sha256:6ca024ccd009d443bb87c15130fc6d641470797ae47af27687bab3a976700969` (локальный image ID, не published SHA).

| Проверка | Результат |
|---|---|
| No-env server-only startup | **PASS**, persistent SQLite и readiness/assets |
| Отдельный external PostgreSQL через service DNS | **PASS** без TLS: migrations/check, runtime SQL, remote data/key после двух app generations |
| External PostgreSQL с TLS | **PASS**: `PGSSLMODE=verify-full`, read-only CA, migrations + asyncpg runtime SQL, `pg_stat_ssl.ssl=true`, readiness/assets и schema check |
| TLS app recreation | **PASS**: remote setting, schema revision и encryption-key hash сохранены |
| SQL backup/restore | **PASS**: actual `pg_dump -Fc` → `pg_restore --exit-on-error` в отдельную DB `codex_lb_restored`; приложение с прежним data/key volume стартовало, setting/revision/key совпали, schema check/readiness/assets прошли |
| External DB recreation | **PASS**: отдельный PostgreSQL container force-recreate с прежним volume, приложение восстановило доступ; restored SQL state и key сохранились |
| Invalid access/DNS | **PASS**: неверный пароль и unresolved DB hostname не дают readiness; startup exit nonzero |
| Invalid TLS certificate | **PASS**: hostname `wrong-db` при certificate `external-postgres` отклонён; чужой CA также отклонён с certificate verify failed |

TLS проверен на управляемом disposable PostgreSQL с собственной тестовой цепочкой доверия. Настоящий remote endpoint/пользовательский firewall/провайдерский CA, TLS MySQL/MariaDB, real account decrypt/OAuth/Codex traffic здесь не проверялись. Совпадение synthetic key/data — доказательство сохранности установки, не реальная account authentication.

Docker guide содержит минимальный external URL, значение localhost внутри контейнера, Desktop host address, mounted CA override и standard driver env вместо новых CODEX_LB настроек. Key volume требуется также при external DB; для восстановления нужны SQL backup и соответствующий app data/key. `compose pull` не обновляет source-build install; update/recreate должен сохранять выбранный DB URL, volume и TLS override.

### 19.4. Проверки, cleanup и состояние публикации

- **22 focused Python tests PASS:** PostgreSQL/MySQL Compose, Docker networking/source selection, launcher contracts; существующий Starlette deprecation warning. Ruff check/format на трёх test files **PASS**.
- Architecture checker, simplicity budgets, `git diff --check` **PASS**. Лимиты не ослаблялись этим пакетом, CHANGELOG не редактировался.
- Strict change validation **PASS**, main **68 specs PASS / 0 failed**. Requirements/context синхронизированы в deployment-installation; archive: [repair-compose-install-contracts](openspec/changes/archive/2026-10-01-repair-compose-install-contracts/), verification.md содержит mapping требований.
- Финальные выборки `codex-lb-batch5-*` containers, volumes и networks пусты; одноразовые certificate generators использовали `--rm`. Audit images и обезличенные logs оставлены. Fixed production volumes не использовались: каждый стенд заранее проверял отсутствие своих имён и задавал isolated names.
- Промежуточные audit failures не скрыты: harness сначала предположил installed project metadata, затем `/app/pyproject.toml` в source-copy public image; оба отсутствуют, runtime smoke сам по себе прошёл, reporter исправлен. Первоначальный cleanup без активного postgres profile оставил собственный DB container; он убран targeted profile cleanup, helper теперь включает профиль. Неверный пароль через PostgreSQL loopback — причина изменения health probe, не замаскированный PASS.

Fresh GitHub API: main `7ec39f82709ee1ca4c00489a8d5fc301d49320ed`, exact-source main-push [CI 36761400788](https://github.com/Frozen811/codex-lb/actions/runs/36761400788) **completed/failure**. Новые локальные workflows/source не выполнялись в cloud. Commit/push/PR/merge, tags/releases, публикация образов и пользовательский deployment не выполнялись. Release остаётся отложенным до exact-source green CI и проверки артефактов; исправление инструкций не исправляет historical aliases F-010.

Следующая тройка: **INSTALL-06 wheel**, **INSTALL-07 sdist**, **INSTALL-08 uv/uvx/pip** — проверить именно публичные fork artifacts/source selectors и команды, отличая их от уже прошедших локальных rebuilt packages. Остальные установки, claims F-007 и полный ISSUES.md остаются в реестре.

## 20. Пакет INSTALL-06 / INSTALL-07 / INSTALL-08 и source push — 2026-10-01

Пользователь прямо поручил исправить три задачи, сделать коммит и отправить в форк. Создана ветка **`fix/python-install-audit`** от `7ec39f82709ee1ca4c00489a8d5fc301d49320ed`; прежние незакоммиченные batches сохранены и включены отдельными тематическими коммитами. Stable main не переписывался, merge/PR/release/tag/image publication не выполнялись. Новая установка из удалённого Git проверена на source commit **`4395926017cc688fe8c3cc48a308d667941bd17d`**; окончательный tracker/archive commit идёт после него и не меняет app/build behavior.

### 20.1. INSTALL-06/07 — именно публичные wheel/sdist

Оба hardened.3 assets заново скачаны без developer PAT, а не заменены локальными сборками:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `codex_lb-1.25.1-py3-none-any.whl` | 3,400,777 | `4af955c73887193d9592d0baf8e638bdec80051f6df5bad8e78e663abd9ad0bf` |
| `codex_lb-1.25.1.tar.gz` | 40,575,939 | `24c965ff57aecead9e15b3a24159857b0c53c9307d7966bc8b4aae87cd3ce744` |

- Metadata **1.25.1**, runtime **1.25.0-beta.9**, по 90 dashboard asset entries и config package. **762** root Python files wheel и sdist совпадают побайтово между собой и совпадают с tag **`deed76bab5fafa36051c2cf474a1b29055988aae`** после CRLF/LF normalization. Raw 731 mismatches объясняются окончаниями строк; normalized code mismatches **0**.
- Public sdist содержит **5967** `.kilo/worktrees` entries, total **12580** archive entries. Это исторический packaging дефект, не устранённый в существующем release asset. Вложенные scripts не запускались; для build/install использовался root project с проверенным pyproject/Hatch backend.
- **PASS Windows/Python 3.13.12:** fresh venv public wheel через uv pip и отдельно **настоящий pip** с прямым release URL, public sdist через PEP 517 rebuild/install. Все imports/startup выполнялись вне checkout, в своих data/key/SQLite directories.
- **PASS:** runtime/distribution identity, `codex-lb` startup, migration console `codex-lb-db --help`, upgrade/schema check, readiness, dashboard HTML/JS/CSS и создание application store/key. Это реальный installation smoke, а не только archive metadata inspection.
- Исторические assets **не заменены**. Их successful startup не означает наличия continuity/Pause и остальных новых fixes. F-010/F-013/F-014 public-artifact boundaries остаются открытыми до нового gated release.

### 20.2. INSTALL-08 — uv/uvx/pip и clean source

**F-022 воспроизведён:** clean source snapshot без `app/static`, `.venv`, frontend/node_modules и workstation env создал wheel без dashboard; build завершался успешно. Bare README/translation/getting-started uvx selectors также выбирали upstream вместо форка.

**Исправление:** `scripts/hatch_build.py` — custom Hatch hook; `scripts/build_dashboard.py` проверяет index + referenced non-empty JS/CSS и использует packageManager **Bun 1.3.14** с frozen lock при отсутствии assets. Неверный/отсутствующий Bun, frontend install/build failure или incomplete output блокируют package creation с понятным prerequisite message. Complete prebuilt wheel/sdist не требует Bun. Новых runtime settings/dependencies нет.

**F-023 воспроизведён дополнительно:** внутри explicit sdist roots всё ещё попадали synthetic `frontend/.kilo/worktrees/old/leak.py`, `.codex/auth.json`, `store.db-wal`, `encryption.key`; nested `.env.local` уже исключался gitignore. В pyproject добавлены explicit nested exclusions, actual archive probe подтвердил отсутствие всех пяти inert markers после исправления. Реальные credentials в эти fixtures не копировались.

| Проверка | Результат |
|---|---|
| Wrong host Bun 1.4.2 | **PASS refusal:** package build требует 1.3.14, wheel не создаётся |
| Clean source frontend build | **PASS:** isolated Windows Bun 1.3.14 из official release, ZIP checksum проверен против official SHASUMS256; clean frontend install/build, assets packaged |
| Corrected wheel/sdist | **PASS:** установка, migration/schema check, readiness/assets вне checkout; installed hashes всех app Python files совпали с текущим checkout |
| Sdist rebuild without pinned Bun | **PASS:** host Bun остаётся 1.4.2, но complete sdist assets позволяют rebuild без frontend toolchain |
| `uv tool install` public URL | **PASS:** isolated tool/bin/cache, реальный console launcher |
| `uv tool install --reinstall` source replacement | **PASS:** historical public wheel → local corrected wheel при одинаковой metadata 1.25.1; runtime стал 1.25.1, synthetic setting и encryption-key hash сохранились |
| `uvx --from <fork-wheel-URL>` | **PASS:** isolated cached tool, identity и real CLI readiness/assets; upstream selector не используется |
| Actual pip release-URL install | **PASS:** отдельная seeded venv, imports/migrations/readiness/assets |
| Published Git immutable SHA | **PASS:** `uvx --from git+https://github.com/Frozen811/codex-lb.git@4395926017cc688fe8c3cc48a308d667941bd17d`; pinned Bun, Git build hook, runtime/metadata 1.25.1, dashboard present, migrations/check/readiness/assets вне repo |

Документация: новый owning-spec-linked `docs/deployment/python.md` и nav; существующие README/перевод/getting-started/update selectors исправлены. Исторический wheel помечен историческим, Git SHA/Bun prerequisite и bare upstream channel разделены. Есть Windows PowerShell и Linux/macOS pip paths, data-dir/key/update guidance. Linux/macOS native команды документированы, но не заявлены реально выполненными в этом Windows прогоне. Nix selectors отдельно остаются INSTALL-13; их upstream принадлежность раскрыта.

### 20.3. Проверки и границы

- **1628 focused unit tests PASS** на затронутых proxy/architecture/release/Docker/packaging/launcher файлах, включая **11** новых package-hook cases. После финального sdist filter изменения эти 11 повторно прошли; это не ещё 11 уникальных поверх 1628.
- **388 HTTP/WebSocket/quarantine route tests PASS**, включая ранее исправленные ownership/Pause/quarantine paths; один существующий Starlette deprecation warning. Всего **2016** уникальных Python tests этого прогона.
- Full-repo Ruff check + format и `ty check` **PASS**. Исходно format check нашёл четыре ранее существовавших layout/blank-line нарушения; отдельный style commit исправил их. AST этих четырёх файлов до/после одинаковый.
- Architecture, simplicity **221/225 README lines, 10/10 headings**, actionlint для трёх изменённых workflows, lock check и git diff check **PASS**. Full `make ci` не исполнялся: локальный Windows make отсутствует; cloud CI не заменяется этим набором.
- Strict OpenSpec delta и **68 main specs PASS**, SSOT/context синхронизированы. После verification change архивируется в `2026-10-01-repair-python-package-installs`.
- Temporary audit root: `C:\Users\ext\AppData\Local\Temp\codex-lb-install-batch6-20261001\` — downloads, source snapshots, hashes/correlation, build/install/server/check logs. Isolated persistent uv tool удалён; temporary venv/cache/download directories оставлены. Каждый smoke завершал своё process tree; реальный account/data/config не использовался.
- Intermediate harness failure: `uvx python -c` запускался из checkout и импортировал его app, ложно показывая новый runtime для historical install. Исправлено через outside cwd + `python -I`; module path и version проверены в isolated cached environment. Это не runtime-дефект uvx или wheel.

Real OAuth/Codex/account decrypt, другие native OS, enterprise proxy/TLS и downgrade compatibility остаются отдельными проверками. Public package runtime drift/sdist worktrees требуют нового release, а не переписывания исторических assets.

### 20.4. Коммиты и fork

1. `165240e3` — style-only Ruff alignment, AST unchanged.
2. `7d151b9e` — continuity/account ownership, paused WebSocket dispatch и route regressions.
3. `9c797af3` — source/CI/artifact release gate, versions, Windows startup regression.
4. `5b72137f` — Docker contexts/targets/probes, database profiles и source Compose.
5. `43959260` — Python source frontend build, nested sdist exclusions и fork package docs.

Source push в [fork branch](https://github.com/Frozen811/codex-lb/tree/fix/python-install-audit) выполнен, `git ls-remote` подтвердил exact SHA. Main-push CI не запускается на этой ветке: основные workflows настроены на main/PR/merge_group. Available Windows workflow допускает diagnostic dispatch, его результат проверяется отдельно после финального report commit. Это не release gate и не утверждение о green exact-source main CI. Исправления не self-merged в main; релиз/теги/GHCR/PyPI не выпускались.

### 20.5. Cloud verification выявила editable regression

Первый реальный Windows run [36904727598](https://github.com/Frozen811/codex-lb/actions/runs/36904727598), SHA `b89bd0a1bdd8737eb814cd98e380b645cac5c1a8`, завершился **failure** на `uv sync --dev --frozen`. Новый dashboard hook ошибочно применялся также к Hatch `build_editable`, до установки Bun; остальные шаги были skipped. Это дефект добавленного hook, а не окружения GitHub.

Исправление **`4dce7220eed12da1b3b1890af48c09d66eb07ee6`** опубликовано: только editable wheel dependency setup пропускает frontend compilation. Standard wheel/sdist по-прежнему требуют assets либо pinned Bun. Реальный clean no-asset `uv sync` с host Bun 1.4.2 теперь проходит, а стандартная сборка на том же стенде отказывается; 11 package regressions, Ruff/ty и actionlint снова прошли. В Windows workflow добавлена проверка отсутствия неожиданно собранного dashboard после dependency setup.

Повторный exact-source Windows run [36905440811](https://github.com/Frozen811/codex-lb/actions/runs/36905440811), SHA **`4dce7220eed12da1b3b1890af48c09d66eb07ee6`**: terminal API result **completed/success**. Dependency setup, editable guard, portability tests, Bun/frontend build и installed-wheel readiness/assets smoke прошли. Этот manual Windows run не заменяет полный main-push CI/review gates и не разрешает выпуск релиза сам по себе. Следующий commit лишь архивирует verification/report; cloud result относится именно к указанному source SHA.

Follow-up OpenSpec: [repair-editable-package-setup](openspec/changes/archive/2026-10-01-repair-editable-package-setup/), owning spec/context/docs синхронизированы. Source остаётся в отдельной fork branch; F-010 и исторические package/image artifacts не обновлялись.
