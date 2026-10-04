# Независимая проверка форка codex-lb

Рабочий реестр проверки и исправления результатов работы другого агента в [Frozen811/codex-lb](https://github.com/Frozen811/codex-lb). Охватывает оформление репозитория, документацию, Docker-образы, пакеты, релизы, Actions, код и все заявления об исправлениях из [ISSUES.md](ISSUES.md).

Этот файл фиксирует доказательства, замечания, исправляющие коммиты и повторные проверки. Нормативные контракты остаются в [openspec/specs](openspec/specs), работа по изменению поведения — в [openspec/changes](openspec/changes). Заявления автора, зелёная сборка образа и наличие теста сами по себе не означают, что проблема решена.

**Последнее обновление: 2026-10-04.** Публикация §47 включает **все восемь прежних archived пакетов** и сохраняет результаты §46 (UP-ISSUE-2483 / UP-ISSUE-1901 / UP-ISSUE-2291). Scope: 125 ранее сохранённых файлов, отдельный журнал публикации; fresh checks и ограничения — в [publication evidence](openspec/changes/archive/2026-10-04-verify-sqlite-history-reports-transcript/prior-changes-publication.md). Цель — `Frozen811/codex-lb:main`. Предыдущие partial/public/cloud/production и F-045/CI-04 сохраняют свой статус; commit/push не означают release/deploy или cloud verification.

**Текущий локальный результат — §50:** UP-ISSUE-2169 / UP-ISSUE-2108 / UP-ISSUE-2074 закрыты локально. HTTP phase provenance исправлен (6 red-before); native fallback и post-output neutrality подтверждены. 132-case focused run, final 30 API cases, 18 actual WebSocket cases, 6 native outcomes и static/spec checks PASS; counts перекрываются. [Verification](openspec/changes/archive/2026-10-04-repair-http-phase-and-drop-contracts/verification.md). Новый commit/push и exact-head cloud CI подтверждаются отдельно; прежние внешние/production/platform остатки сохраняются.

**CI repair verified — section 49:** published source `575c18f4e` has 29/29 successful CI jobs and successful Windows/release guards/simplicity checks. [Exact-SHA evidence](openspec/changes/archive/2026-10-04-repair-fork-ci-regressions/verification.md).

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
| ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | Собственный описанный scope задачи завершён по связанным локальным доказательствам; эта отметка не подтверждает новый cloud CI, публикацию или production |
| ИСПРАВЛЕНО В SOURCE | Исправляющий коммит присутствует в ancestry текущего HEAD; результаты относятся к указанному source snapshot, публикация/production подтверждаются отдельно |
| ЧАСТИЧНО ПРОВЕРЕНО | Выполненная часть и её evidence отмечены; перечисленный остаток не закрыт |
| НЕ ПРИМЕНИМО | Есть явное обоснование, почему пункт не относится к форку |

Приоритеты: P1 — падающий продуктовый путь, нарушение владения/расчётов или существенный блокер выпуска; P2 — регрессия, нарушение обязательной проверки, документации или поставки; P3 — оформление и улучшение сопровождаемости. Приоритет очереди не означает, что дефект уже подтверждён.

Отметка `[x]` подтверждает явно описанный scope задачи, не автоматически Git-коммит,
cloud CI, выпуск или production deployment. `[ ]` может содержать выполненную
локальную часть и отдельный открытый остаток. Для нового рабочего дерева
смотрим сводный статус и последнюю карточку evidence; исторические разделы
сохраняют результаты и ограничения своего source snapshot.

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
| F-001 | P1 | ИСПРАВЛЕНО В SOURCE / ПУБЛИКАЦИЯ ОТДЕЛЬНО | Account snapshots клонируются внутри сессии; реальный teardown и HTTP/compact/WebSocket проверены, см. раздел 13; ancestry/пакет — §28.2 |
| F-002 | P2 | ИСПРАВЛЕНО В SOURCE / ПУБЛИКАЦИЯ ОТДЕЛЬНО | Архитектурные границы восстановлены; `load_balancer.py` 3021/3021, checker проходит без изменения лимитов; ancestry/пакет — §28.2 |
| F-003 | P1 | ИСПРАВЛЕНО В SOURCE / ПУБЛИКАЦИЯ ОТДЕЛЬНО | OpenSpec согласован с bounded sole-owner fallback из #2274; неоднозначность, ошибки listing, пустой scope и paused admission покрыты; ancestry/пакет — §28.2 |
| F-004 | P2 | ИСПРАВЛЕНО В SOURCE / ПУБЛИКАЦИЯ ОТДЕЛЬНО | Scoped compact test seam обновлён; реальный scoped API-путь и отсутствие выбора чужого аккаунта проверены; ancestry/пакет — §28.2 |
| F-005 | P2 | ИСПРАВЛЕНО В SOURCE / ПУБЛИКАЦИЯ ОТДЕЛЬНО | Воспроизведён durable-first порядок: helper смешивал общий и локальный deadline; исправлен helper, оба порядка покрыты Responses-тестом; §17; ancestry/пакет — §28.2 |
| F-006 | P1 | ИСПРАВЛЕНО В SOURCE / ПУБЛИКАЦИЯ ОТДЕЛЬНО | Ungated publisher заменён exact-source CI gate с повторной проверкой перед upload/login; live main CI отказ подтверждён. Новый cloud workflow ещё не выполнен, см. раздел 16; ancestry/пакет — §28.2 |
| F-007 | P2 | SOURCE + ЛОКАЛЬНО / ПОЛНЫЙ АУДИТ ОТКРЫТ | Неподтверждённые claims 164/165/100% сняты; источник явно исторический, пересчитаны 120 Issues + 128 PR + 49 Discussions = 297 ссылочных записей, category sums 158/184; это не число проверенных фиксов. Каждое обращение остаётся отдельной проверкой; §23 |
| F-008 | P2 | ИСПРАВЛЕНО В SOURCE / ПУБЛИКАЦИЯ ОТДЕЛЬНО | Старый Windows workflow успешно запущен вручную; новая автоматизация и installed-wheel smoke проверены локально, требуют публикации и main-push run; §17; ancestry/пакет — §28.2 |
| F-009 | P1 | ИСПРАВЛЕНО В SOURCE / ПУБЛИКАЦИЯ ОТДЕЛЬНО | Direct WebSocket обходил unknown-owner refusal при Codex affinity; удалён обход, проверены новый запрос и уже открытый socket; ancestry/пакет — §28.2 |
| F-010 | P1 | ПОДТВЕРЖДЕНО / ОТКРЫТО | Fresh anonymous GHCR check: `latest`/`1.25.1` всё ещё `f622c563`, hardened.3 — `deed76ba`. README теперь раскрывает исторический digest, production Compose локально собирает source; новые публичные исправления не опубликованы; §19 |
| F-011 | P2 | ИСПРАВЛЕНО В SOURCE / ПУБЛИКАЦИЯ ОТДЕЛЬНО | Пути diagnostics приведены к `/`, Windows/POSIX и outside-root identity проверены; architecture tests **16 passed**; §17; ancestry/пакет — §28.2 |
| F-012 | P1 | ИСПРАВЛЕНО В SOURCE / ПУБЛИКАЦИЯ ОТДЕЛЬНО | Обычный turn на открытом direct WebSocket обходил Pause; добавлена проверка routing marker перед send, после admission. Реальный Pause API, anchored/fresh turns, peer snapshot, удаление и сохранение in-flight ответа проверены, см. раздел 14; ancestry/пакет — §28.2 |
| F-013 | P1 | SOURCE + ЛОКАЛЬНО / ARTIFACT SCOPE ОТКРЫТ | Managed версии и публичные пакеты расходились с runtime/Helm: `1.25.1` против `1.25.0-beta.9`; local parity, rebuild и clean install проверены. Исторические artifacts/tag не исправлены, см. раздел 16 |
| F-014 | P2 | ИСПРАВЛЕНО В SOURCE / ПУБЛИКАЦИЯ ОТДЕЛЬНО | Публичный sdist hardened.3 включает 5967 entries под `.kilo/worktrees`; explicit root selection и archive refusal добавлены. Новый локальный sdist не содержит worktree entries; cloud artifact ещё не опубликован; ancestry/пакет — §28.2 |
| F-015 | P1 | ИСПРАВЛЕНО В SOURCE / ПУБЛИКАЦИЯ ОТДЕЛЬНО | Build contexts допускали nested env/credential files и agent worktrees; frontend также допускал host dependencies. Реальный BuildKit export на inert fixtures подтвердил baseline и устранение; §18; ancestry/пакет — §28.2 |
| F-016 | P2 | ИСПРАВЛЕНО В SOURCE / ПУБЛИКАЦИЯ ОТДЕЛЬНО | Bun в distroless/inline Compose расходился с package/workflows: 1.4.2 против 1.3.14; версии согласованы, оба targets собраны и запущены; §18; ancestry/пакет — §28.2 |
| F-017 | P2 | ИСПРАВЛЕНО В SOURCE / ПУБЛИКАЦИЯ ОТДЕЛЬНО | Docker CI собирал только стандартный образ без runtime smoke; добавлены distroless build и readiness/assets/native/CA проверки. Оба образа получили shell-free healthcheck; cloud execution ещё не выполнен; §18; ancestry/пакет — §28.2 |
| F-018 | P2 | ИСПРАВЛЕНО В SOURCE / ПУБЛИКАЦИЯ ОТДЕЛЬНО | Development frontend запускался с UID 0. Inline image переведён на USER bun с правильным ownership; UID 1000, Vite/TSX/proxy/watch/recreate подтверждены повторным прогоном; §18; ancestry/пакет — §28.2 |
| F-019 | P1 | ИСПРАВЛЕНО В SOURCE / ПУБЛИКАЦИЯ ОТДЕЛЬНО | Обычный production Compose up выбирал кешированный старый GHCR image вместо checkout. Введены local image name + pull_policy build; actual up заменил намеренно подложенный historical image актуальным source; §19; ancestry/пакет — §28.2 |
| F-020 | P2 | ИСПРАВЛЕНО В SOURCE / ПУБЛИКАЦИЯ ОТДЕЛЬНО | MySQL ping и PostgreSQL pg_isready сообщали успех при неверном доступе; loopback PostgreSQL дополнительно обходил пароль через trust. Проверки заменены authenticated SQL, PostgreSQL использует HOSTNAME; wrong password/database реально отклоняются; §19; ancestry/пакет — §28.2 |
| F-021 | P2 | SOURCE + ЛОКАЛЬНО / ARTIFACT SCOPE ОТКРЫТ | Основной Docker Quick Start и перевод выбирали upstream, fork latest обещал актуальность, update guide смешивал dev/prod/public. Исправлены выбор source/digest, происхождение образа, DB URLs и команды обновления; §19. Остальные claims F-007 отдельно |
| F-022 | P1 | ИСПРАВЛЕНО В SOURCE / ПУБЛИКАЦИЯ ОТДЕЛЬНО | Чистый Git/source install выпускал wheel без dashboard assets. Custom Hatch hook собирает assets закреплённым Bun/frozen lock либо отказывает с prerequisite guidance; actual clean source wheel/sdist и 11 regressions PASS; §20; ancestry/пакет — §28.2 |
| F-023 | P1 | ИСПРАВЛЕНО В SOURCE / ПУБЛИКАЦИЯ ОТДЕЛЬНО | Explicit-root sdist selector всё ещё допускал worktrees/credentials внутри выбранных frontend/app folders. Inert marker archive probe воспроизвёл 4 leaks; explicit nested exclusions устранили все markers; §20; ancestry/пакет — §28.2 |
| F-024 | P1 | ИСПРАВЛЕНО / WINDOWS CLOUD PASS | Новый build hook требовал Bun при editable uv sync и сломал первый Windows run. Editable-only exemption и CI guard проверены локально и на опубликованном SHA 4dce7220; §20.5 |
| F-025 | P1 | ИСПРАВЛЕНО / SOURCE SMOKE PASS | Checkout launchers не выбирали собственный проект и не готовили dashboard; clean baseline readiness 200, UI 503. Frozen project-bound startup теперь готовит assets; foreign cwd/paths with spaces Windows/Linux PASS; §21 |
| F-026 | P2 | ИСПРАВЛЕНО / SOURCE SMOKE PASS | PowerShell терял CLI exit 2, batch также не сохранял errorlevel, run.sh был 100644. Exit status/args исправлены, Bash 100755; actual PS/pwsh/cmd/Linux failure/signal tests PASS; §21 |
| F-027 | P1 | ИСПРАВЛЕНО / WINDOWS+LINUX PASS | Bun build выбирал host Node 18 через Vite shebang и падал на node:util styleText. Frontend tools теперь --bun runtime, pinned 1.3.14; actual builds PASS; §21 |
| F-028 | P2 | ИСПРАВЛЕНО / PR CI PASS | Affinity/close-1009 fixtures обходили committed account routing notification. Fixtures приведены к реальному import lifecycle, runtime Pause guard не ослаблялся; 11 routes + 25 Pause local PASS и full PR CI; §21 |
| F-029 | P1 | ИСПРАВЛЕНО / NIX CLOUD PASS | Explicit Nix sources не включали объявленный Hatch hook/helper; wheel build падал до assets reuse. Узкие source filters исправлены, actual Nix flake check на f61669d6 PASS; §21; [Nix evidence](openspec/changes/archive/2026-10-01-repair-nix-hook-source-filter/verification.md). |
| F-030 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Helm defaults/OCI instructions выбирали upstream; теперь fork source/chart, явный image выбор, StatefulSet drain и DB/key rollback boundaries; §22 |
| F-031 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Fresh external DB + --wait блокировались schema gate/post-install циклом; DB-only Secret также ссылался на отсутствующий encryption Secret. Regular install Job исправила оба пути; §22 |
| F-032 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Kubernetes без Docker marker выбирал read-only /home/app/.codex-lb для runtime cache. Chart задаёт writable mounted scratch, migrator получает явный key-file; §22 |
| F-033 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Nix frontend падал с EPERM hardlinks на immutable store; CRLF в Windows flake ломал embedded shell. copyfile/frozen install + LF attribute проверены реальной сборкой/startup; upstream Nix commands исправлены; §22 |
| F-034 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | COMMUNITY_RELEASE предполагал неустановленный systemd unit; remote guide не давал executable proxy example. Предположение снято, nginx config и границы documented/verified; §22 |
| F-035 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | CI detector игнорировал rename origin, неполную/malformed API pagination и Nix source/build-helper inputs; conservative full-suite fallback и корректные filters проверены CLI-output regressions; CI-02, §23 |
| F-036 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Fork docs metadata/edit/owning-spec links оставались upstream; upstream release failure cleanup не имел repo guard. Fork metadata + configured Pages base URL и cleanup owner boundary исправлены; REL-03, §23 |
| F-037 | P2 | ПОДТВЕРЖДЕНО / ОТКРЫТО | Redirect chain проверен заново: default HTTPS → 301 http://extr3me.me/codex-lb/ → 200; custom HTTPS отказывается с CERTIFICATE_VERIFY_FAILED / hostname mismatch. Исправление настроек/сертификата и Pages redeploy не выполнено; §28.4 |
| F-038 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Отрицательный CLI/env keep-alive принимался как допустимый; validation lower bound, zero-valid и fresh CLI refusal покрыты. Ранее описано SETUP-02 §24, отдельный F-ID добавлен при сверке §28 |
| F-039 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Dashboard trusted-header sanitizer/resolver доверяли projected request.client вместо captured raw socket peer; valid proxy/remote caller и spoofed loopback покрыты реальными auth routes. Ранее SETUP-06 §25; §28 |
| F-040 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | OAuth callback runner/site оставались после failed/cancelled bind, failure lacked safe diagnostics; cleanup/retry и pending/manual callback routes покрыты. Ранее SETUP-06 §25; §28 |
| F-041 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Internal drain start/stop/status допускали spoofed projected loopback; raw peer + projected loopback + no forwarded hints, denial without state mutation и local reversal покрыты. Ранее SETUP-09 §26; §28 |
| F-042 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Missing-assets response советовал bare bun build; hint теперь pinned/frozen/Bun runtime для source и complete artifact для installed package/image. Route ready200/root503 покрыт; SETUP-09 §26; §28 |
| F-043 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО / TEST SCOPE | Windows discovery fixtures требуют PATHEXT launcher; process signals POSIX-only и реально исполнялись на Linux; startup polling bounded30s без расширения shutdown bounds. Test fixture portability, не новый production transport fix; SETUP-10 §26; §28 |
| F-044 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО / ПОЛНЫЙ EXECUTION ОТКРЫТ | Copy/paste shell mix/redirection placeholders, stale SSO Deployment, unexported env и TOML wire_specification исправлены; 111 blocks parse + scoped runtime tests. DOC-INSTALL-03 §27; §28 |
| F-045 | P2 | ТРЕБУЕТ РАЗБОРА | При общей Windows проверке test_cli_sqlite_restart_and_paired_restore упал на INSERT после server stop с SQLite disk I/O error; отдельный повтор PASS. Причина/стабильность ещё не установлены, product DB corruption не доказана; CI-04/SETUP-03, §28.4 |
| F-046 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | POST standalone search с завершающим `/` возвращал 405 на canonical/v1/doubled-prefix ingress. Hidden slash routes переиспользуют control handler; red-before/green-after и real gzip HTTP upstream проверены; UP-ISSUE-2128, §29. |
| F-047 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | GET single model с завершающим `/` искал ID вместе с delimiter и возвращал 404. Slash route зарегистрирован перед greedy path; nested IDs, list parity, auth/allowlist/source scope и cleanup проверены; UP-ISSUE-2038, §29. |
| F-048 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Response schema планировщика отвергала malformed legacy clock strings (`9:00`, `bad`, empty), GET/partial correction падали с 500. Read schema возвращает исходные строки, strict write schema сохранена; UP-PR-2540, §31. |
| F-049 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | SCIM declared-length precheck вызывала ValueError на >4300 decimal digits и superscript digit; malformed headers читали body. ASCII decimal comparison без int, SCIM400/413 и zero-padding/stream boundaries покрыты; UP-PR-2541, §31. |
| F-050 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | aiohttp ERROR(WebSocketError(1009)) терял код размера в адаптере: bridge возвращал 503/stream_incomplete и запускал replay. Typed exact-code branch сохраняет size evidence до generic recovery; реальные sockets, settlement и same-account reuse проверены; UP-PR-2539, §32. |
| F-051 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Authorization redactor оставлял credential tails после quoted/repeated commas, malformed parameters, status/ampersand и placeholder. **56 failed / 32 passed** до правки; complete-quoted/current-line masking, actual text/JSON log files, exception rendering и CR/LF idempotency PASS. UP-ISSUE-2028, §33. |
| F-052 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Verbatim SSE timing scanner пропускал spaced/escaped JSON keys и принимал nested metadata за output. Real HTTP route записывал first output1000 вместо500 мс. Shared parsed-content classifier, cached carrier reuse, decoder guards, HTTP/WebSocket/DB/logs/reports и 40TPS при total3000/terminal1000 PASS; UP-PR-2444, §34. |
| F-053 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Source tool filter удалял namespace, но оставлял forced/allowed function choice с этим namespace. **12 failed** на реальном loopback upstream до правки; shared choice predicate убирает dangling entries, сохраняет bare functions/mode и разрешённые namespaces. UP-PR-2526, §35. |
| F-054 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Compatible output-budget projection считала bool целым и принимала zero/negative raw limits: GPT-6 fallback мог стать1/0/-1. **16 failed** до правки; positive non-boolean integer precedence, unknown null, list/retrieval/slash/native data aliases и неизменность input/native metadata PASS. UP-PR-2528, §35. |
| F-055 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Метрика accounts_available не передавала committed rejection reason в shared eligibility predicate. **9 failed**: revoked/invalidated/rejected access с future/unknown/unreadable expiry считался доступным при routing block. Reason из existing snapshot, repair/expiry/inventory/failure-recovery/multiprocess PASS; UP-PR-2523, §36. |
| F-056 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Dashboard не показывал Resume для quota_exceeded при поддержке existing reactivate API. **3 frontend failed** до правки; callback-once, busy/read-only, reauth protection, Chromium POST/refreshed actions, реальная DB/CAS/owner и screenshots до/после PASS; UP-PR-2527, §36. |
| F-057 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Chat JSON mode распознавался только по response_format: эквивалентный text.format терял JSON-инструкцию из input. **16 route failed** до правки; shared Responses predicate после format mapping, developer role/order, 96 actual upstream turns и prefix stability PASS; UP-PR-2515, §37. |
| F-058 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | JSON access formatter читал поля, которые Uvicorn создаёт только на private copy текстового formatter: реальные client/request/status были null. Native argument tuple теперь декодируется без мутации LogRecord; оба listeners, text/JSON stream/file parity и 200/503 PASS; UP-PR-2529, §37. |
| F-059 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | JSON debug без optional OpenTelemetry рекурсивно форматировал diagnostic logs failed trace lookup и мешал CLI startup. Диагностика tracing helper пропускает собственное enrichment; оба listeners reachability, no RecursionError/logging errors и ordinary trace/span enrichment PASS; UP-PR-2529, §37. |
| F-060 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Telemetry lock не охватывал register/activate и dashboard commit: 9 red-before real collector/API races. Complete protocol и решения сериализованы; 12 complete/cancel/503/timeout cases, signature/disabled silence PASS. Global collector fence отдельно; UP-ISSUE-1844, §38. |
| F-061 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Opt-out timestamp union оставлял malformed strings и не приводил offset strings к UTC: 4 red-before cases. Typed datetime/ISO parsing, numeric refusal, canonical UTC/Z и actual signing PASS; UP-ISSUE-1844, §38. |
| F-062 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Windows IOCP route loss 1231/1232 игнорировался при ошибочной process-neutral классификации peer reset/timeout 64/121. 8 red-before; typed provenance и real generation/route tests PASS; UP-ISSUE-2456, §39. |
| F-063 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Native transport diagnostics терялись между core synthetic event и request-log writer: 6 actual body failures записывали failure_phase=null. Attempt-owned typed trace теперь сохраняет request/body phase, static exception и observed status без новых SSE fields/replay; UP-ISSUE-2471, §39. |
| F-064 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Direct error-kind frame-less endings штрафовали аккаунт без учёта positive transport evidence: 4 red-before route cases. Typed adapter provenance и specific native ResetWithoutClosingHandshake transport phase; real socket abort Python/native, unproven/protocol/authored-close controls PASS. UP-ISSUE-2081, §40. |
| F-065 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Selected-owner quota error-kind terminal подменялся owner-unavailable и писал health до finalization; file-bound account-switch refusal делал то же. Original sanitized 429/code/type/message/param/reset metadata сохранены, no replay, settlement/log/health ownership у finalizer. UP-ISSUE-2081, §40. |
| F-066 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Native Responses JSON POST не имел request zstd, вопреки broad parity claim. TLS HTTP/2 red-before; scoped opt-in level-3 zstd, exact decompressed JSON, stale encoded headers removal, opaque/multipart/Python fallback boundaries PASS. Полная real-client TLS/header-order parity не доказана; UP-ISSUE-1208, §40. |
| F-067 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО / TEST SCOPE | Unsafe full-resend unit fixture mock-ала только durable lookup и при owner retirement открывала real SQLite без accounts: 6 reproducible failures. Retirement double возвращает false и проверяет expected owner; original refusal assertions сохранены. Same 107-case selection PASS; UP-ISSUE-2465, §41. |
| F-068 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Durable claim release сбрасывал replacement local half-open probe даже после CAS miss/error. 3 red-before; exact local lease остаётся у submission finalizer, durable helper не меняет чужой probe. UP-ISSUE-2271, §44. |
| F-069 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Caller cancellation после DB claim commit теряла receipt до assignment на request. Actual submission + SQLite red-before; bounded scheduler task/deferred cancellation и fenced undispatched cleanup, repeated cancellation PASS. UP-ISSUE-2271, §44. |
| F-070 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Newly inserted claim не имел captured epoch для release; post-commit query мог вернуть successor receipt. Inserted-row red-before, retained inserted epoch и snapshot внутри winning transaction; successor generation fence PASS. UP-ISSUE-2271, §44. |
| F-071 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | Scheduled retry cleanup не сравнивал count и повторно удалял changed candidate после partial batch. 4 red-before; full snapshot fence + keyset cursor, 12 SQLite/PG/MySQL cases PASS. UP-ISSUE-2270, §45. |
| F-072 | P2 | ИСПРАВЛЕНО ЛОКАЛЬНО | Queue close сохранял payloads/cancelled putters; closed None отменял shared reader, stall терял terminal. 3 unit red-before; Queue.shutdown, graceful finish и ordered failure с fixed5s bound PASS. UP-ISSUE-2266, §45. |
| F-073 | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО | ASGI send cancellation не закрывала body iterator; bridge wrapper оставлял nested generator GC и поздний reserved row. Actual v1/slash/backend red-before; explicit nested close, repeated cancellation/writer-error и reservation cleanup PASS. UP-ISSUE-2266, §45. |
| F-074 | P2 | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | 14 producer branches теряли provenance локального отказа и получали transport shaping. Полный audit 27 contexts, native до/после commitment, signed forwarding, no-send и реальный reservation cleanup PASS. UP-ISSUE-2388, §48; [evidence](openspec/changes/archive/2026-10-04-repair-bridge-refusal-transition-terminal/verification.md). |
| F-075 | P1 | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | Unanchored keyed later/raised terminal начинал error-health write при ещё reserved reservation. 2 backend red-before; shared helper ждёт settlement при account_health_error. 18 actual-route cases с DB readback, одним terminal и logged exception PASS. UP-ISSUE-2033, §48; [evidence](openspec/changes/archive/2026-10-04-repair-bridge-refusal-transition-terminal/verification.md). |


### F-001 — ORM-объекты покидают сессию до чтения ID

Текущий итог: исправлено в source `7d151b9e`, ancestry текущего HEAD подтверждена; HTTP/compact/WS evidence §§13/21. Ниже сохранено исходное воспроизведение 2026-09-30; прежнее «SHA нет» относится к тому срезу.

- Исходный коммит: `deed76bab5fafa36051c2cf474a1b29055988aae`; воспроизведено на `7ec39f82`.
- Исходные файлы в срезе 2026-09-30: `load_balancer.py`, `_service/continuity_owner.py`, callers в compact, streaming retry и WebSocket. После локальной правки общий resolver находится в [_service/support.py](app/modules/proxy/_service/support.py), старый модуль удалён.
- `list_continuity_owner_candidates()` возвращает `Account` после выхода из repository context. Чтение `candidates[0].id` вызывает `DetachedInstanceError`; обработчик исключений helper охватывает вызов listing, но не это чтение.
- Локально падают `test_v1_responses_single_account_missing_previous_response_owner_fails_closed_without_dispatch` и `test_v1_responses_compact_single_account_missing_previous_response_owner_fails_closed` из `tests/integration/test_proxy_responses.py`. В CI также падают forwarding-сценарии sticky sessions и OpenAI compatibility.
- Шесть helper-тестов на моках проходят: это не покрывает реальный teardown ORM-сессии.
- Проверка исправления: реальные repository/session boundaries, HTTP stream/non-stream, compact, WebSocket, scoped/unscoped key; ошибки остаются в ожидаемом OpenAI-envelope.
- Исправляющий SHA: **нет**. Локальная правка и повторная проверка выполнены 2026-10-01, см. раздел 13; cloud/release verification остаётся открытой.

### F-002 — архитектурные проверки

Текущий итог: source fix присутствует в HEAD (proxy batch `7d151b9e`); локальные gates и исторические PR checks §§13/21. Нижеследующие нарушения/«SHA нет» описывают исходный срез.

- Коммит: `deed76ba`; проверенный HEAD: `7ec39f82`.
- `load_balancer.py`: 3037 строк при нормативном лимите 3021.
- Compact импортирует `app.modules.proxy._service.continuity_owner`; checker разрешает для compact домен `support`.
- Доказательства: локальный `scripts/check_proxy_architecture.py`, CI lint job, unit `test_repository_proxy_architecture_passes`.
- Контракт: [proxy-architecture/spec.md](openspec/specs/proxy-architecture/spec.md). Восстановить границы/размер, не повышая лимиты ради прохождения.
- Исправляющий SHA: **нет**.

### F-003 / F-004 — continuity contract и scoped compact

Текущий итог: source contract/helper seam и externally failing routes исправлены в proxy batch `7d151b9e`; §§13/21. Ниже — исходная диагностика, а не текущий статус.

- F-003: новый fallback при пропущенном owner lookup использует единственного кандидата. Основной контракт [Hard continuity owner lookup fails closed](openspec/specs/responses-api-compat/spec.md) требует немедленного fail-closed; точную допустимость scoped-key исключения и single-pool сценария необходимо разобрать вместе с историей и тестами.
- В diff `deed76ba` нет обновления OpenSpec, хотя меняются continuity, OAuth и другие продуктовые пути.
- F-004: `tests/unit/test_proxy_utils.py::test_compact_owner_miss_uses_api_key_scope_before_fail_closed` локально и в CI получает `ProxyResponseError(502)` вместо ожидаемого результата.
- Существующий тест подменяет `_load_selection_inputs`, новый helper использует другой listing path. Падение теста подтверждено; отдельный функциональный дефект scoped API-key пока не доказан.
- Не исправлять ситуацию удалением регрессионного теста или ослаблением ownership. Сначала установить требуемый контракт, затем синхронизировать implementation, OpenSpec и тест реального API-пути.
- Исправляющий SHA: **нет**.

### F-005 — quarantine cooldown зависит от условий запуска

Текущий итог: fixture исправлена в source `7d151b9e`; last path commit/ancestry проверены. 69-test evidence §17 и PR integration §21. Новый SQLite flake F-045 является отдельным пунктом.

- Сценарий: `tests/integration/test_http_quarantine_provenance.py::test_completion_separates_local_failure_from_durable_adoption[success-failed-load-retry-weaker]`.
- CI core-1: примерно `1599.989` вместо `700.0`. В отдельном локальном запуске прошёл.
- Разбор 2026-10-01: принудительный durable-first load перед local arm воспроизводит **1599.9605** на Windows. Во время `await` persistence другой reader может принять poison row до локального weaker fence; helper `arm` возвращал общий, уже продлённый deadline вместо срока локального evidence.
- Исправление: helper возвращает собственный `local_poison_until` или `suppressed_weaker_until`; исходные final-deadline/ownership assertions сохранены. Проверяются оба порядка, lookup retry и частичные failures. Production quarantine не менялся. Подробности и **69 passing integration tests** — §17; исправляющего SHA ещё нет, cloud shard после публикации остаётся обязательным.

### F-006 / F-008 — покрытие процесса поставки

Текущий итог: source gate/Windows automation находятся в HEAD (`9c797af3` → release merge `245152d7`); historical Windows/PR verification §§20.5/21. Published artifacts и current dirty/cloud delta отдельно; ниже — исходный publisher snapshot.

- Docker Publish [run 36756416840](https://github.com/Frozen811/codex-lb/actions/runs/36756416840) завершился успешно на `deed76ba`, CI этого SHA завершился с ошибкой.
- [docker-publish.yml](.github/workflows/docker-publish.yml) запускается от опубликованного release или вручную; явного prerequisite на успешный CI в нём нет.
- Проверка тега, digest, содержимого образа, smoke-теста и фактически выдаваемого `latest` ещё не выполнена. Success означает успешную публикацию, а не отсутствие продуктовых регрессий.
- Исходный [windows-startup.yml](.github/workflows/windows-startup.yml) имел только `workflow_dispatch`; API показывал 0 запусков. 2026-10-01 получен успешный manual baseline run; локально добавлены автоматические source events, installed-wheel smoke и обязательный exact-source Windows prerequisite для публикации. Новая версия Actions ещё не опубликована; §17.

## 4. Очередь проверки оформления, поставки и сопровождения

Сводные статусы синхронизированы с журналом §§13–42. «Локально» означает проверенный указанный source/runtime scope; public artifacts, cloud gates и пользовательские инциденты учитываются отдельно. Частичная проверка явно перечисляет остаток. Отсутствие нового коммита не означает отсутствие описания или evidence.

| ID | Приоритет | Область | Что проверяем | Статус | Выполненная часть / остаток |
|---|---|---|---|---|---|
| IMG-01 | P1 | GHCR images | Все опубликованные теги, digest, source SHA, OCI version/revision/source labels; сопоставление release → commit → workflow → image | ЧАСТИЧНО ПРОВЕРЕНО | GHCR aliases/digests/source/OCI и historical release checked §§16/19/26/27; не все tags/workflow linkage сертифицированы, F-010 открыт. |
| IMG-02 | P1 | latest / версии | Куда указывают `latest`, `1.25.1`, hardened-теги и команды README/compose; воспроизводимый pull по digest | ПОДТВЕРЖДЕНО / ОТКРЫТО | Historical latest/1.25.1 источник f622c563 vs newer source; explicit digest documented, новый public image не опубликован; F-010, §§19/26/27. |
| IMG-03 | P1 | Чистый Docker-запуск | Запуск документированной команды без env-файла; dashboard, ready health, API, persistence, корректная остановка | ЛОКАЛЬНО ПРОВЕРЕНО | linux/amd64 public digest и source containers: ready/assets, volume/key recreation, shutdown; §§18/19/26. Real OAuth и другие architectures отдельно. |
| IMG-04 | P1 | Обновление образа | Сохранение БД, WAL, encryption key и конфигурации; миграция существующих данных; проверяемый rollback | ЛОКАЛЬНО ПРОВЕРЕНО | Actual old → candidate → recreate → old paired snapshot restore в isolated volume, DB/key/settings/account retention; §26. Не универсальный downgrade guarantee. |
| IMG-05 | P2 | Архитектуры | Фактический manifest и поддерживаемые CPU/OS; обещания multiarch подтверждены запуском или ограничены документацией | ЧАСТИЧНО ПРОВЕРЕНО | Manifest amd64 vs unknown/unknown attestation confirmed; dated platform matrix, x64 runtime only. Native ARM64/macOS остаются unexecuted; §§26/27. |
| IMG-06 | P2 | Dockerfile / distroless | Python/Rust/helper, frontend assets, Alembic/config/data files, права каталогов, entrypoint, сигналы и shutdown | ЛОКАЛЬНО ПРОВЕРЕНО | Standard/distroless helper/CA/non-root/assets/migrations/health and process checks §§18/26; все platform permutations не заявлены. |
| IMG-07 | P2 | Compose | `docker-compose.yml`/prod, optional `.env.local`, минимальная версия Compose, порты, volumes, healthcheck, restart и источник image | ЛОКАЛЬНО ПРОВЕРЕНО | Dev/prod source Compose, optional env, authenticated DB readiness, volumes/recreation and explicit build; §§18/19/26. New publication отдельно. |
| IMG-08 | P2 | Scan / исключения | Обоснованность `.trivyignore`, срок/объём исключений, связь со сканом; зелёный результат не получен скрытием применимых проблем | НЕ ПРОВЕРЕНО | Applicable CVE scan, exclusion rationale/expiry и отсутствие скрытия findings ещё не доказаны; historical CI scan result не заменяет этот аудит. |
| PKG-01 | P1 | Wheel / sdist | Чистая установка опубликованных артефактов; CLI, dashboard assets, миграции, imports; версия пакета совпадает с заявленной | ЧАСТИЧНО ПРОВЕРЕНО | Public wheel/sdist installed historically §§20/27; wheel fresh Windows/Linux runtime PASS. Public runtime drift/nested sdist worktrees не устранены новым artifact; F-013/014. |
| PKG-02 | P2 | uvx / pip / clone | Все варианты Quick Start реально воспроизводятся; Git-install отличается от PyPI/релизного wheel только документированным образом | ЧАСТИЧНО ПРОВЕРЕНО | Fork URL/channel, pip/uvx/tool and Git source paths checked §§20/21/27; full per-command runtime coverage DOC-INSTALL-03 остаётся открытой. |
| PKG-03 | P2 | Launchers | `run.ps1`, `run.sh`, `start.bat`: cwd с пробелами, fresh checkout, missing runtime, graceful errors, upgrade и отсутствие секретов в выводе | ИСПРАВЛЕНО В SOURCE | 742fc58d: Windows PS5/pwsh/cmd и Linux/WSL cwd/args/failures/start/restart verified §21; native macOS unexecuted. Launcher commit ancestry §28. |
| PKG-04 | P2 | Lockfiles | Python/Bun/Rust версии и lockfiles согласованы; frozen install воспроизводим; helper не собирается неожиданно при простом импорте | ЛОКАЛЬНО ПРОВЕРЕНО | Frozen uv/Bun/Rust source setup and optional native-helper boundary §§18/20/21/22; lockfiles не изменены в dirty batches. Public unlocked historical dependencies отдельно. |
| REL-01 | P1 | Release gates | CI того же SHA до выпуска, обязательные jobs, защита от публикации непроверенной ревизии; связь с F-006 | SOURCE ПРОВЕРЕН / НОВЫЙ ВЫПУСК ОТКРЫТ | 9c797af3/245152d7 exact-source publication guard and tests; historical PR/main gates §21. Dirty batches не имеют exact-head cloud CI или нового релиза. |
| REL-02 | P2 | Версии / release notes | `pyproject.toml`, frontend/package, uv.lock, release tag, wheel, image и docs; объяснение hardened version scheme и реального состава релиза | ЧАСТИЧНО ПРОВЕРЕНО | Local version parity and historical artifact/tag/runtime discrepancy documented F-013 §§16/20/27; public metadata/package replacement ещё нет. |
| REL-03 | P2 | Upstream workflows | Release guards, beta/release-please, metadata и docs jobs работают в контексте форка; intended skips отделены от ошибок | ИСПРАВЛЕНО ЛОКАЛЬНО | Intentional upstream publisher skips, cleanup owner boundary и fork docs ownership verified F-036 §23. Current local changes/cloud deployment/Pages HTTPS separately open. |
| CI-01 | P1 | Current-head checks | Каждый uploaded SHA и attempt: обязательные checks, логи первичных failures, skipped/cancelled jobs, итоговый CI Required | VERIFIED / CLOSED FOR SOURCE 575c18f4e | Section 49: CI run 37224667796 attempt 1, published main SHA 575c18f4e55ab1138086523cc81edf00c03bfb4b; 29/29 CI jobs success, all core shards and both aggregates success, Windows/release guards/simplicity success. [Evidence](openspec/changes/archive/2026-10-04-repair-fork-ci-regressions/verification.md). |
| CI-02 | P2 | Changes detection | Python/frontend/Rust/migrations/packaging changes включают нужные jobs; изменение workflows не создаёт ложный green | ИСПРАВЛЕНО ЛОКАЛЬНО | Rename/count-complete pagination, full-suite fallback и Nix inputs tested F-035 §23; fresh detector tests §28. New cloud run отдельно. |
| CI-03 | P2 | DB matrix | SQLite/PostgreSQL/MySQL/MariaDB: реальное покрытие, migration head/topology, upgrade/downgrade/backfill/drift; aliases типов не скрывают несовместимость | ЧАСТИЧНО ПРОВЕРЕНО | SQLite/PostgreSQL/MySQL isolated migrations/drift/backup/runtime §§19/24/26; полный MariaDB/каждой migration downgrade/backfill audit не выполнен. |
| CI-04 | P2 | Flakes / isolation | Quarantine, session lifecycle, background loops, cache/durable state, xdist/shards; повторное прохождение после объяснения причины | ЧАСТИЧНО ПРОВЕРЕНО / F-045 ОТКРЫТ | Quarantine helper/source regressions F-005 §§17/21; lifecycle checks §§25/26. New Windows SQLite aggregate fail / isolated PASS §28; причина и стабильность не закрыты.; §39: native terminal probes group timeout / fresh-process PASS, session-lifecycle причина не изолирована. |
| CI-05 | P2 | Windows | Получить CI/локальные доказательства supported Windows startup и transport, включая F-008 | ЧАСТИЧНО ПРОВЕРЕНО | Published Windows source run 4dce7220 PASS §20.5; PS/cmd source startup §21, recent auth/helper/package Windows checks §§25–28. Dirty delta cloud coverage отдельно. |
| CI-06 | P2 | Browser / UI | До/после screenshots, viewport, browser smoke и реальные user flows; мок-тесты не заменяют запуск dashboard | ЧАСТИЧНО ПРОВЕРЕНО | Real dashboard HTML/assets and scoped bootstrap/auth/import/runtime flows §§18–27; полный browser/viewport/screenshots flow audit не выполнен. |
| DOC-01 | P2 | README | Название/назначение форка, поддерживаемые платформы, Quick Start, ссылки, badges, версии, ограничения; проверить README.md и README.zh-CN.md | ИСПРАВЛЕНО ЛОКАЛЬНО | Fork README/Chinese links, historical source/artifact distinction, shell/channel guidance and budget checked §§23/27. Published hosted guides ещё stale. |
| DOC-02 | P2 | Заявления о качестве | Сравнение с upstream, «production/hardened», «100%», счётчики исправлений и OpenSpec: каждому утверждению соответствуют SHA и доказательства | ЛОКАЛЬНО ИСПРАВЛЕНО / ПОЛНЫЙ АУДИТ ОТКРЫТ | Source-author claims vs independent evidence, 297 unique linked records corrected F-007 §23; public 100%/production claims and per-entry source audit remain open §§27/28. |
| DOC-03 | P2 | Документация | mkdocs/navigation, client setup, settings, deploy/update guides; рабочие ссылки на owning OpenSpec и отсутствие противоречащих инструкций | ИСПРАВЛЕНО ЛОКАЛЬНО / PUBLIC ОТКРЫТ | MkDocs/nav/spec backlinks/generated reference and client/config/deploy guides §§22–27; 75 links/24 anchors and strict renders PASS. Published Pages F-037 отдельно. |
| DOC-04 | P2 | Конфигурация | `.env.example`, precedence code < env < dashboard, tiers, encryption key, proxy routing; только существующие поля и проверенные примеры | ЛОКАЛЬНО ПРОВЕРЕНО | Env discovery/precedence, .env.example zero-config, dashboard persistence, key/endpoint semantics §§24–26; static export fixes §27. No new settings. |
| DOC-05 | P2 | Обновление пользователей | COMMUNITY_RELEASE.md, FIXES-NOT-IN-v1.25.1.md, release assets и инструкции: что входит в каждый tag, совместимость и rollback | ЧАСТИЧНО ПРОВЕРЕНО | Explicit fork/source/digest update, historical wheel boundary и paired rollback §§26/27; original FIXES-NOT artifact claims/public release notes целиком не закрыты. |
| DOC-06 | P3 | Оформление GitHub | About/description, homepage, topics, package/release descriptions, default branch, badges, docs URL; правки GitHub — отдельное действие | ПОДТВЕРЖДЕНО / ОТКРЫТО | About/homepage/release/OCI descriptions unsupported/stale, Pages redirect+cert mismatch F-037; §§27/28. Public changes не выполнялись. |
| DOC-07 | P3 | Авторство / лицензии | LICENSE, attribution, contributors, credits за перенесённые PR; различие собственной правки и интеграции community work | НЕ ПРОВЕРЕНО | Полный LICENSE/attribution/community integration audit не завершён. Сохранение существующих contributors markers/links не доказывает все credits. |
| GOV-01 | P2 | OpenSpec | Behaviour-changing commits имеют change artifacts, нормативные specs и контекст; strict validation, verification перед archive | ЧАСТИЧНО ПРОВЕРЕНО | Шесть dirty OpenSpec batches, 40/40 tasks, verification/spec sync и strict68 PASS §§22–28. Все historical/upstream commits на spec coverage не проаудированы. Дополнение §42: сверены 29 independent archive reports, 201/201 checked tasks; missing completion marks и ссылки исправлены. |
| GOV-02 | P2 | Simplicity | README/env/nav/root budgets, конфигурационные tiers, архитектурные ratchets; необходимые исключения оформлены по правилам репозитория | ЛОКАЛЬНО ПРОВЕРЕНО | Simplicity/tiers/architecture checks записаны для scoped batches §§22–27; fresh budgets §28. Ratchets не ослаблены; полный review новых внешних PR не заявлен. |
| GOV-03 | P2 | Git tracking | Разделение origin/fork, base SHA, upstream integrations/cherry-picks; 19 коммитов апстрима проверены на patch-equivalence, а не только на SHA | ЧАСТИЧНО ПРОВЕРЕНО | Source fixing commit ancestry подтверждена; explicit fork fetch при upstream origin Windows/Bash §§26–28. Все 19 upstream integrations на patch-equivalence не проверены. |
| GOV-04 | P2 | PR readiness | Точные issue references, current-head CodeRabbit threads, check rollup, merge state, screenshots; отсутствие PR не означает выполненный review | ИСТОРИЧЕСКИ ПРОВЕРЕНО / НОВЫЙ DELTA ОТКРЫТ | Четыре PR source-head CI/review/merge gates записаны §21; dirty batches без нового PR/CodeRabbit/current-head cloud evidence. Старый review не перенесён автоматически. |
| GOV-05 | P2 | Реестр исходных claims | Сверить 108/110/164, категории, merged/superseded/discussions, дубли и «0 задач»; считать independently verified отдельно | ЧАСТИЧНО ПРОВЕРЕНО | Source count/type claims corrected F-007 §23; связанные проверенные/partial исходные карточки уточнены §28. Полный semantic per-entry audit остаётся открыт. |
| GOV-06 | P2 | Этот новый root-файл | `issues-check.md` зарегистрирован локально в `[root_files].allowed` 2026-10-01; checker проходит на текущем HEAD, будущий tracked root tree проверяется после коммита | ЛОКАЛЬНО ПРОВЕРЕНО | issues-check.md root allowlist tracked; current check root0/0 §28. Новых root files/исключений не добавлялось. |

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

Очередь ниже сформирована из локального `ISSUES.md` на исходном HEAD. На первом срезе все строки имели **НЕ ПРОВЕРЕНО**; актуальные результаты находятся в столбце **Наша проверка**. Связанные issue/PR отмечаются отдельно после сопоставления их собственного scope с доказательствами; зелёная подсистема не закрывает автоматически всё обращение. Найденные выше регрессии пока записаны как F-карточки; связывать их с конкретным upstream issue следует после установления связи.

В заголовках исходного файла найдено **155 отдельных карточек**. Дополнительно найдено **142 уникальных ссылки** на issues, PR и discussions, не являющиеся URL этих карточек: итого **297 уникальных ссылок**. Это число ссылок для проверки объёма, не число уникальных багов и не подтверждение исходного счётчика «164». Вспомогательные ссылки могут оказаться контекстом, дублем сценария или неподходящей задачей; это фиксируется явно.

Для строки с результатом создаём карточку по шаблону раздела 7 и указываем её ID в последнем столбце. Тип источника обязателен: issue и PR с одинаковым номером нельзя смешивать; номера относятся к `Soju06/codex-lb`.

<!-- source-queue:start -->

### Исходный раздел 1: Native Egress, Rust-движок и сетевой транспорт

| ID / источник | Заявленная тема | Исходный статус | Наша проверка | Карточка / исправляющий SHA |
|---|---|---|---|---|
| [UP-ISSUE-2471](https://github.com/Soju06/codex-lb/issues/2471) | bug(proxy): with upstream_stream_transport=http the native egress multiplexes every account's streams onto ONE shared HTTP/2 connection — one transport fa… | РЕШЕНО | ИСПРАВЛЕНО ЛОКАЛЬНО / ЧАСТИЧНО ПРОВЕРЕНО | F-063, §39: реальный TLS HTTP/2 helper подтверждает account isolation/reuse; shared-pool control воспроизводит collateral failure. Native request/body phase, static exception и observed status теперь доходят до БД; 6 red-before body cases. Ambiguous pre-head POST не replay. Raw error-chain/cf-ray и per-request WSS preference остаются открыты. [Evidence](openspec/changes/archive/2026-10-03-repair-native-transport-recovery/verification.md). |
| [UP-ISSUE-2470](https://github.com/Soju06/codex-lb/issues/2470) | bug(proxy): direct-HTTP stream that dies with "Native upstream transport ended before a terminal event" never releases its account stream lease → per-acco… | РЕШЕНО | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §39: existing nested cleanup подтверждён actual helper + v1/backend/native Codex routes, stream/non-stream, EOF/body/head failures. 18 сценариев × 3 POST: caps=1, pressure=0, reservation settled/released и helper state empty после каждого запроса; третий успешен без restart. Public/cloud/production отдельно. [Evidence](openspec/changes/archive/2026-10-03-repair-native-transport-recovery/verification.md). |
| [UP-ISSUE-2456](https://github.com/Soju06/codex-lb/issues/2456) | bug(proxy): Windows transport errors bypass shared-client recovery | РЕШЕНО | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | F-062, §39: fresh upstream scope — route loss 1231/1232, исторический excerpt 64/121 устарел. 8 red-before cases; typed route classification, real shared generation retirement/CAS ownership, active lease retention, connector-only retry и health neutrality PASS. Reset/timeout сохраняют ordinary endpoint handling. Physical route loss/public/cloud отдельно. [Evidence](openspec/changes/archive/2026-10-03-repair-native-transport-recovery/verification.md). |
| [UP-ISSUE-2425](https://github.com/Soju06/codex-lb/issues/2425) | bug: input_image requests still fail ~35% during overload on beta.8 — the HTTP bridge bypass, not the upstream transport, is the cause (follow-up to #2363… | РЕШЕНО | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §40: existing bounded inline PNG/JPEG admission подтверждена 69 tests; v1/backend text-image-text reuse, output-free overload recovery, exact image bytes, budgets, unsupported-shape/rollback and cancellation. Hosted overload percentages/public artifacts отдельно. [Evidence](openspec/changes/archive/2026-10-03-verify-image-websocket-transport-contracts/verification.md). |
| [UP-ISSUE-2081](https://github.com/Soju06/codex-lb/issues/2081) | bug: direct websocket terminal failures lose transport and owner evidence | РЕШЕНО | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | F-064/F-065, §40: 20 terminal route controls +4 selected-owner quota cases, 10 adapter provenance cases, real Python/native socket abort; original sanitized terminal/metadata, no unsafe replay, one finalization/health. File-bound refusal и existing settlement/cancellation checks PASS. Public/deployed traffic отдельно. [Evidence](openspec/changes/archive/2026-10-03-verify-image-websocket-transport-contracts/verification.md). |
| [UP-ISSUE-1208](https://github.com/Soju06/codex-lb/issues/1208) | feat: Improve upstream transport parity and eliminate the easily identifiable codex-lb fingerprint | РЕШЕНО | ИСПРАВЛЕНО ЛОКАЛЬНО / ЧАСТИЧНО ПРОВЕРЕНО | F-066, §40: actual TLS HTTP/2 origin подтверждает zstd request bodies, deterministic exact decoded JSON, lowercase H2 headers, native identity and absent implicit negotiation/request-ID, 2 MiB/5 MiB windows. Native compact/routed, raw-body/multipart/Python fallback controls PASS. Claims полного header-order/TLS fingerprint исправлены; live Codex CLI comparison, hosted acceptance и public packages остаются открыты. [Evidence](openspec/changes/archive/2026-10-03-verify-image-websocket-transport-contracts/verification.md). |

### Исходный раздел 2: HTTP/WebSocket Bridge, стриминг, ретраи и сессии

| ID / источник | Заявленная тема | Исходный статус | Наша проверка | Карточка / исправляющий SHA |
|---|---|---|---|---|
| [UP-ISSUE-2493](https://github.com/Soju06/codex-lb/issues/2493) | bug: Beta.9 HTTP bridge can close native stream without terminal event after proxy-injected anchor rejection | РЕШЕНО | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §41: existing runtime fix подтверждён actual WebSocket + native backend/slash routes: local precommit 502, post-created/keepalive ровно один masked SSE terminal, upstream code в БД, finalized/released reservations и pressure=0. Definitive denied-anchor retirement подтверждена existing route. Исходное универсальное обещание rate_limit_exceeded исправлено. [Evidence](openspec/changes/archive/2026-10-04-repair-bridge-terminal-lineage-failover/verification.md). |
| [UP-ISSUE-2465](https://github.com/Soju06/codex-lb/issues/2465) | bug: beta.9 sticky bridge lineages wedge permanently; image+tools path sends invalid parallel_tool_calls | РЕШЕНО | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | F-067, §41: два bounded silent logical turns, затем retry последнего полного body без poisoned anchor; actual HTTP Lite image+tools, serial calls/all_turns/header и payload preservation PASS. Partial unit mock retirement исправлен: 6 red-before, same 107-case selection green. Delta/account-owned/ambiguous-journal fences сохранены. [Evidence](openspec/changes/archive/2026-10-04-repair-bridge-terminal-lineage-failover/verification.md). |
| [UP-ISSUE-2455](https://github.com/Soju06/codex-lb/issues/2455) | bug(proxy): bridge payload bypass blocks verified quota failover | РЕШЕНО | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §41: actual HTTP owner429→alternate success с API-key-scoped durable proof, exact full body и удалённой stale affinity; другой ключ, wrong prefix, missing output, explicit anchor, owned item и owner mismatch не получают grant. Canonical/slash, reservations и pressure=0 PASS; file/lookup/forwarded guards проверены related suites/source. [Evidence](openspec/changes/archive/2026-10-04-repair-bridge-terminal-lineage-failover/verification.md). |
| [UP-ISSUE-2447](https://github.com/Soju06/codex-lb/issues/2447) | SQLite database is locked during login/OAuth under concurrent streaming load | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2409](https://github.com/Soju06/codex-lb/issues/2409) | bug(proxy): intermittent cache misses on Astra/SOL with the same Pro account across HTTP and WebSocket (195k–777k input) | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2389](https://github.com/Soju06/codex-lb/issues/2389) | bug(http-bridge): a model-transition fork rescues one turn, then re-derives the same owner conflict | РЕШЕНО | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §48: existing fix подтверждён real balancer conflict + durable coordinator/SQLite, child owner и turn N+1 с reasoning history на трёх routes; нет повторного fork/connection. Protected aliases/rollback/cancellation сохранены. Live providers/clients и distributed/platform scope отдельно. [Evidence](openspec/changes/archive/2026-10-04-repair-bridge-refusal-transition-terminal/verification.md). |
| [UP-ISSUE-2388](https://github.com/Soju06/codex-lb/issues/2388) | bug(proxy): other HTTP-bridge local refusals still reach native Codex clients as an empty 200 | РЕШЕНО | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | F-074, §48: per-site audit 27 contexts; 14 pre-dispatch branches marked, mixed/post-send producers retained. Canonical/slash/native, committed terminal+DONE и signed forwarding PASS; no new upstream frame, reservation/lease cleanup. Literal empty-body symptom не воспроизведён для каждого current producer; исправлена подтверждённая transport misclassification. [Evidence](openspec/changes/archive/2026-10-04-repair-bridge-refusal-transition-terminal/verification.md). |
| [UP-ISSUE-2273](https://github.com/Soju06/codex-lb/issues/2273) | bug: incomplete responses can bypass bridge retry limits | РЕШЕНО | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §44: existing reason-only accounting подтверждён actual HTTP/WebSocket v1/slash/backend и real SQLite; 24 raw/interpreted precedence/exclusion cases. Distinct attempts дают counts 1→2/cooldown, stored terminal не создаёт send/strike; authored terminal сохранён на исходной отправке. Proof-gated replay остаётся предусмотренным исключением. [Evidence](openspec/changes/archive/2026-10-04-verify-bridge-retry-claim-lifecycle/verification.md). |
| [UP-ISSUE-2272](https://github.com/Soju06/codex-lb/issues/2272) | bug: bridge retries can stay blocked after cooldown ends | РЕШЕНО | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §44: real durable missing/zero/negative/elapsed cooldown допускает повторный admission; настоящая local expiry выдаёт один probe, повторные loads сохраняют его lease. Existing ownership/cleanup/settlement regression PASS. Отдельная crash/abandonment policy не сертифицирована. [Evidence](openspec/changes/archive/2026-10-04-verify-bridge-retry-claim-lifecycle/verification.md). |
| [UP-ISSUE-2271](https://github.com/Soju06/codex-lb/issues/2271) | bug: retry claims can stay locked after their owner exits | РЕШЕНО | ИСПРАВЛЕНО ЛОКАЛЬНО / ЧАСТИЧНО ПРОВЕРЕНО | F-068/069/070, §44: cancellation after commit, inserted-row epoch, post-commit receipt replacement и unfenced local probe clearing исправлены; real submission/SQLite, repeated cancellation и successor CAS PASS. Открыты process crash/reclamation, uncertain internal timeout, generation rollback ABA, ordinary-success/newer-claim settlement policy и PostgreSQL/MySQL/migration runtime. Полного закрытия нет. [Evidence](openspec/changes/archive/2026-10-04-verify-bridge-retry-claim-lifecycle/verification.md). |
| [UP-ISSUE-2270](https://github.com/Soju06/codex-lb/issues/2270) | bug: retry cleanup can delete state changed by a newer request | РЕШЕНО | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | F-071, §45: 4 scheduled red-before cases; selected count/timestamp/generation fence и keyset cursor не удаляют изменённую строку повторным выбором. 12 cases на SQLite/PostgreSQL16/MySQL8.4, batches1/128; continuity/tombstone/age controls PASS. [Evidence](openspec/changes/archive/2026-10-04-verify-bridge-cleanup-quarantine-backpressure/verification.md). |
| [UP-ISSUE-2268](https://github.com/Soju06/codex-lb/issues/2268) | bug: old bridge requests can clear a newer session's quarantine | РЕШЕНО | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §45: existing ownership/failure-cutoff подтверждены 9 actual completion cases: initial strike during settlement, replacement и pruned/recreated key. Старое completion не снимает новый fence; related quarantine controls PASS. Existing overflow policy не переработана. [Evidence](openspec/changes/archive/2026-10-04-verify-bridge-cleanup-quarantine-backpressure/verification.md). |
| [UP-ISSUE-2266](https://github.com/Soju06/codex-lb/issues/2266) | bug: paused streams can keep growing worker memory | РЕШЕНО | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | F-072/F-073, §45: cancelled waiter/retained buffer/sentinel cancellation и nested iterator/reservation lifetime исправлены. Fixed5s stall cap, ordered resume или one failure; actual ASGI pause/stall/cancel/writer-error canonical/slash/backend, zero bytes/pressure, settled reservations и active account PASS. Per-stream scope; global RSS/native/spool отдельно. [Evidence](openspec/changes/archive/2026-10-04-verify-bridge-cleanup-quarantine-backpressure/verification.md). |
| [UP-ISSUE-2169](https://github.com/Soju06/codex-lb/issues/2169) | test: make native SSE fallback refusal fixture portable on macOS | РЕШЕНО | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §50: existing closed-port fix подтверждён source lifetime и fresh native helper: четыре SSE и два compact outcomes PASS, no replay/selected-owner/cleanup, без skips или расширения deadlines. Windows/source closure; native macOS execution отдельно. [Evidence](openspec/changes/archive/2026-10-04-repair-http-phase-and-drop-contracts/verification.md). |
| [UP-ISSUE-2108](https://github.com/Soju06/codex-lb/issues/2108) | bug: HTTP Responses logs omit observed upstream phase timings | РЕШЕНО | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | §50: 6 red-before actual API/DB cases; keepalive/local failure больше не создают upstream phases. 30 final API/DB/optional-Prometheus cases, queue500/event250/created500/TTFT1000, zero/null/normalized local ID и actual wire PASS. Старые minute-long stalls отдельно. [Evidence](openspec/changes/archive/2026-10-04-repair-http-phase-and-drop-contracts/verification.md). |
| [UP-ISSUE-2090](https://github.com/Soju06/codex-lb/issues/2090) | fix(proxy): reconcile reservations after late HTTP-bridge anchor injection | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2074](https://github.com/Soju06/codex-lb/issues/2074) | bug: post-output frame-less bridge drops still penalize account health | РЕШЕНО | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §50: existing production fix подтверждён 18 real WebSocket/HTTP cases: после text/buffered reasoning one stream_incomplete, no replay/health/eventless signal. Authored1011/binary penalty сохранён. Противоречащий старый normative пункт удалён; live provider/production отдельно. [Evidence](openspec/changes/archive/2026-10-04-repair-http-phase-and-drop-contracts/verification.md). |
| [UP-ISSUE-2033](https://github.com/Soju06/codex-lb/issues/2033) | proxy: a failing post-terminal health write emits a second terminal stream frame | РЕШЕНО | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | F-075, §48: existing single-terminal containment подтверждён, выявленный health-before-committed-settlement исправлен. 18 route cases: first/later/raised, anchored/unanchored keys, real reservation readback, one original terminal и one logged exception; disconnect/cancellation controls PASS. Public/cloud/production отдельно. [Evidence](openspec/changes/archive/2026-10-04-repair-bridge-refusal-transition-terminal/verification.md). |
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
| [UP-ISSUE-2356](https://github.com/Soju06/codex-lb/issues/2356) | bug(proxy): experimental context management returns 405 for native notes v2 calls | РЕШЕНО | ЛОКАЛЬНО ПРОВЕРЕНО / ЗАКРЫТО | §29: 96 known +18 unknown operation/alias/slash variants, bytes/query/encryption-header preservation, auth/account scope, child placement/fallback and unavailable upstream. Existing implementation подтверждена; hosted encryption/history recovery и public artifacts отдельно. [Evidence](openspec/changes/archive/2026-10-02-repair-native-client-compatibility/verification.md). |
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
| [UP-ISSUE-2426](https://github.com/Soju06/codex-lb/issues/2426) | bug(metrics): populate account counts and expose availability for alerting | РЕШЕНО | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §42: producer/inventory/availability проверены independent §36: real DB/ASGI exposition, zeroes/status/repair/expiry/delete/failure recovery и multiprocess livemax; optional metrics dependency была установлена, final exporter tests не skipped. F-055 исправлен; [evidence](openspec/changes/archive/2026-10-03-verify-account-pool-probe-recovery/verification.md). Production alert deployment отдельно. |
| [UP-ISSUE-2420](https://github.com/Soju06/codex-lb/issues/2420) | bug(accounts): Hard-coded Pro and Pro Lite credit capacities disagree with observed quota consumption, distorting pooled credit reporting | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2413](https://github.com/Soju06/codex-lb/issues/2413) | feat: Luna Reserve (gpt-reserve) fallback when chat quota is exhausted | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2327](https://github.com/Soju06/codex-lb/issues/2327) | fix(accounts): recover stale holds after verified matching operator probes | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2288](https://github.com/Soju06/codex-lb/issues/2288) | feat: pool reset credits across accounts in Codex Desktop | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2285](https://github.com/Soju06/codex-lb/issues/2285) | feat: show pooled quota in Codex Desktop while staying signed in | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2274](https://github.com/Soju06/codex-lb/issues/2274) | bug: continuations can be routed to the wrong account | РЕШЕНО | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §42: явное закрытие ранее проверенного bounded sole-owner/scope и HTTP/compact/WS continuation scope; F-001/003/004/009, §§13/14/21. Source 7d151b9e → f847fc57 присутствует в ancestry текущего HEAD. Historical quota incident/public artifact отдельно. [Evidence](openspec/changes/archive/2026-10-01-repair-continuity-owner-snapshots/verification.md). |
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
| [UP-ISSUE-2483](https://github.com/Soju06/codex-lb/issues/2483) | perf(usage): high memory usage and query latency in bulk history reads on SQLite | РЕШЕНО | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | §46: 4 red-before malformed-cap cases; fail-fast validation до dialect dispatch. 100 000 rows → 1 280 snapshots, cutoffs/floor/ties/zero и dashboard parity PASS; capped read не использует uncapped cache. PostgreSQL/production RSS отдельно. [Evidence](openspec/changes/archive/2026-10-04-verify-sqlite-history-reports-transcript/verification.md). |
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
| [UP-ISSUE-2128](https://github.com/Soju06/codex-lb/issues/2128) | bug(proxy): standalone web search fails on v1 and duplicates native Content-Type | РЕШЕНО | ИСПРАВЛЕНО ЛОКАЛЬНО / ЗАКРЫТО | F-046, §29: slash 405 reproduced/fixed на трёх ingress; auth/scope, raw bytes/repeated query, real gzip JSON upstream, JSON/SDP Content-Type casing и bodyless removal PASS. Live hosted search и новый public helper/image не сертифицированы. [Evidence](openspec/changes/archive/2026-10-02-repair-native-client-compatibility/verification.md). |
| [UP-ISSUE-1467](https://github.com/Soju06/codex-lb/issues/1467) | bug: gpt-5.3-codex-spark works on Pro but is missing from /v1/models | РЕШЕНО | НЕ ПРОВЕРЕНО | — |

### Исходный раздел 7: Безопасность, шифрование, логирование и телеметрия

| ID / источник | Заявленная тема | Исходный статус | Наша проверка | Карточка / исправляющий SHA |
|---|---|---|---|---|
| [UP-ISSUE-2028](https://github.com/Soju06/codex-lb/issues/2028) | fix(logging): shared log-redaction patterns leave credential tails for auth-param lists, quoted keys, and whitespace-separated tokens | РЕШЕНО | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | F-051, §33: original probes и дополнительные malformed/status/ampersand/placeholder cases; error fields, text/JSON messages/exceptions, actual log files, quoted context и CR/LF idempotency PASS. Unquoted Authorization теперь маскируется до конца строки; public/cloud отдельно. [Evidence](openspec/changes/archive/2026-10-03-repair-auth-log-audit-contracts/verification.md). |
| [UP-ISSUE-1844](https://github.com/Soju06/codex-lb/issues/1844) | Telemetry opt-out: close the consent/send race and follow-up hardening | РЕШЕНО | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | F-060/F-061, §38: 9 red-before гонок и 4 timestamp cases; full protocol + dashboard commit lock, 12 actual collector races с complete/cancel/503/timeout, Ed25519 и disabled silence PASS. Global cross-process fence/collector authority и deferred observability остаются открыты. [Evidence](openspec/changes/archive/2026-10-03-repair-telemetry-and-stateless-key-contracts/verification.md). |
| [UP-ISSUE-1843](https://github.com/Soju06/codex-lb/issues/1843) | bug: telemetry client type is wrong | РЕШЕНО | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §38: existing mapping подтверждён через 11 stored-group preview cases и 24 actual Responses/Chat stream/non-stream routes, loopback upstream, new-session log readback и canonical shares. SSOT дополняет CLI/Desktop aliases; private/missing groups → other. Real client applications/public/cloud отдельно. [Evidence](openspec/changes/archive/2026-10-03-repair-telemetry-and-stateless-key-contracts/verification.md). |
| [UP-ISSUE-1572](https://github.com/Soju06/codex-lb/issues/1572) | feat: support CODEX_LB_ENCRYPTION_KEY for stateless replicas | РЕШЕНО | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | §38: env-key encryption уже работает; topology/key-selection SSOT и mismatch remediation исправлены. Actual import/DB/decryption, explicit precedence/blank fallback, inaccessible default file, same/different sentinel и два fresh processes PASS; key material не раскрывается. Deployed PostgreSQL topology/public/cloud отдельно. [Evidence](openspec/changes/archive/2026-10-03-repair-telemetry-and-stateless-key-contracts/verification.md). |

### Исходный раздел 8: Dashboard, UI и Prometheus метрики

| ID / источник | Заявленная тема | Исходный статус | Наша проверка | Карточка / исправляющий SHA |
|---|---|---|---|---|
| [UP-ISSUE-2492](https://github.com/Soju06/codex-lb/issues/2492) | feat: Reset API key limit usage from dashboard without regenerating keys | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2443](https://github.com/Soju06/codex-lb/issues/2443) | bug(metrics): dashboard/report TPS uses post-settlement latency and reasoning-inclusive TTFT | РЕШЕНО | ЧАСТИЧНО ПРОВЕРЕНО | §42: API/DB/daily-report часть уже проверена §34: reasoning125, first output500, terminal1000, total3000 мс; qualified 40TPS и sample/median/filter/virtual-time regressions. [Evidence](openspec/changes/archive/2026-10-03-repair-usage-and-generation-evidence/verification.md). Полный recent-requests dashboard UI / very-short-window / queue-consumer scenario аудит этого issue отдельно не записан; полностью не закрыт. |
| [UP-ISSUE-2418](https://github.com/Soju06/codex-lb/issues/2418) | bug(frontend): Apple Passwords TOTP autofill does not populate Chrome verification dialog | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2309](https://github.com/Soju06/codex-lb/issues/2309) | docs: align agent instructions with Astra prompt guidance | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2262](https://github.com/Soju06/codex-lb/issues/2262) | feat(proxy): preserve built-in OpenAI provider when routing ChatGPT-authenticated Codex Desktop through codex-lb | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2038](https://github.com/Soju06/codex-lb/issues/2038) | Visual Studio Copilot requires GET /v1/models/{model_id} | РЕШЕНО | ИСПРАВЛЕНО ЛОКАЛЬНО / ЗАКРЫТО | F-047, §29: visible/nested model slash 404 reproduced/fixed; list parity, unknown/hidden models, independent allowlist/source scope, auth и reservation release PASS. Actual Visual Studio UI registration и public packages остаются внешним scope. [Evidence](openspec/changes/archive/2026-10-02-repair-native-client-compatibility/verification.md). |
| [UP-ISSUE-1901](https://github.com/Soju06/codex-lb/issues/1901) | bug(reports): /api/reports takes ~120 s for a 7-day window (~543k rows) while equivalent raw SQL finishes in ~2.5 s | РЕШЕНО | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §46: existing rollup/cache/runtime проверен actual /api/reports на 543 000 SQLite rows; raw/folded totals и exact daily medians равны. 21.416 с raw / 7.811 с folded / 0.015 с cache. Неподтверждённое millis promise исправлено; ARM/production benchmark отдельно. [Evidence](openspec/changes/archive/2026-10-04-verify-sqlite-history-reports-transcript/verification.md). |

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
| [UP-ISSUE-2410](https://github.com/Soju06/codex-lb/issues/2410) | bug: Force Probe sends unsupported payload fields and can fail to settle successful probes | РЕШЕНО | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §42: existing probe payload/ORM snapshot contract проверен §36: accounts_service_probe/load_balancer suites и real dashboard API + rollback/closed repositories, accepted/rejected/network/partial-row и health/lease controls. Recorded 719-case scope, не повторный новый прогон. [Evidence](openspec/changes/archive/2026-10-03-verify-account-pool-probe-recovery/verification.md). Реальный vendor probe отдельно. |
| [UP-ISSUE-2314](https://github.com/Soju06/codex-lb/issues/2314) | ci: reconcile issue and PR status-label ownership and lifecycle | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2311](https://github.com/Soju06/codex-lb/issues/2311) | docs: use GPT-6 Astra in current client examples | РЕШЕНО | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2291](https://github.com/Soju06/codex-lb/issues/2291) | bug: queued transcript batches wait between flushes | РЕШЕНО | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §46: existing loop подтверждён 320-event ten-write burst, bounded fair passes и false/exception isolation без intervening waits. Real SQLite rows_v1/chunks_v2 сохраняют 320 events + один terminal; stale-owner epoch отклонён. Live production speedup отдельно. [Evidence](openspec/changes/archive/2026-10-04-verify-sqlite-history-reports-transcript/verification.md). |
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
| [UP-PR-2502](https://github.com/Soju06/codex-lb/pull/2502) | MySQL / MariaDB support | RESOLVED / MERGED IN FORK | ЧАСТИЧНО ПРОВЕРЕНО | MySQL runtime install/migrations/read-write/paired restore проверены §§19/24; полная MariaDB/всех module contracts проверка не выполнена. |
| [UP-PR-2503](https://github.com/Soju06/codex-lb/pull/2503) | fix(http-bridge): keep replayed history images on the bridge | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2504](https://github.com/Soju06/codex-lb/pull/2504) | fix(usage): account for cache-write tokens | RESOLVED / MERGED IN FORK | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §34: 24 actual local HTTP/WebSocket native-protocol cases, missing/negative/mixed/excess writes, disjoint costs, raw DB counts, finalized reservations, repeat CAS, API cost components и next-request429; migration/backfill и 6 background checks PASS. Existing source implementation подтверждена; packaged Rust helper/public/cloud отдельно. [Evidence](openspec/changes/archive/2026-10-03-repair-usage-and-generation-evidence/verification.md). |
| [UP-ISSUE-2505](https://github.com/Soju06/codex-lb/issues/2505) | bug: shutdown cancels schedulers and the leader-lease keeper mid-DB-work (SQLite pool CancelledError, unreleased lease, unclean run-state) | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2506](https://github.com/Soju06/codex-lb/pull/2506) | fix(shutdown): let DB-owning background tasks finish before cancelling them | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2507](https://github.com/Soju06/codex-lb/pull/2507) | feat(cli): add --log-level and --log-file; stop the metrics server resetting logging | RESOLVED / MERGED IN FORK | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §42: ранее CLI flags/launcher log paths проверены §§17/21; оставшийся metrics logging scope закрыт §37: test_cli.py и structured/OTel suites, четыре real CLI processes text/JSON × info/debug, primary+metrics, spaced file path и stream/file access parity. [Evidence](openspec/changes/archive/2026-10-03-verify-plan-json-metrics-contracts/verification.md). Установленные tracing exporters/POSIX/public артефакты отдельно. |
| [UP-PR-2508](https://github.com/Soju06/codex-lb/pull/2508) | fix(proxy): reuse bridge sessions for inline images | RESOLVED / MERGED IN FORK | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §43: existing bounded-image reuse подтверждён real local WebSocket: text/image/history на одном socket и prompt-cache identity, verbatim PNG, invalid-image recovery и settled reservations; existing long-budget precreated retry policy сохранена. Main blanket-bypass wording синхронизирована. [Evidence](openspec/changes/archive/2026-10-04-repair-image-control-transport-contracts/verification.md). Live vendor/cache/public/cloud отдельно. |
| [UP-PR-2509](https://github.com/Soju06/codex-lb/pull/2509) | chore(deps): bump the frontend-minor-patch group across 1 directory with 16 updates | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2510](https://github.com/Soju06/codex-lb/pull/2510) | chore(deps): bump the python-minor-patch group across 1 directory with 11 updates | MERGED/CLOSED | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2511](https://github.com/Soju06/codex-lb/issues/2511) | bug(accounts): self_serve_business_prolite usage plan is rejected as unknown | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2512](https://github.com/Soju06/codex-lb/pull/2512) | fix(accounts): normalize business prolite plan alias | RESOLVED / MERGED IN FORK | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §37: three import variants и five real HTTP refresh cases; new-session DB/dashboard readback, canonical prolite/default capacity/Pro-equivalent eligibility, unchanged identity/credentials, unknown-plan/workspace refusal PASS. Existing fix подтверждён; hosted plans/public/cloud отдельно. [Evidence](openspec/changes/archive/2026-10-03-verify-plan-json-metrics-contracts/verification.md). |
| [UP-PR-2513](https://github.com/Soju06/codex-lb/pull/2513) | fix(proxy): send a single Content-Type on codex control requests | MERGED/CLOSED | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | §43: empty-byte body сохранял Content-Type; после normalization aiohttp всё ещё генерировал octet-stream. Empty→None + skip_auto_headers исправлены direct/routed; real native/SDK JSON/SDP/empty routes и Python/native HTTP-proxy wire PASS, first spelling/position и query/body сохранены. [Evidence](openspec/changes/archive/2026-10-04-repair-image-control-transport-contracts/verification.md). Public/cloud отдельно. |
| [UP-ISSUE-2514](https://github.com/Soju06/codex-lb/issues/2514) | feat(accounts): redeem all eligible reset credits in one action | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2515](https://github.com/Soju06/codex-lb/pull/2515) | fix(chat): keep the JSON instruction in input for json_object requests | RESOLVED / MERGED IN FORK | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | §37, F-057: 16 red-before text.format cases исправлены shared mode detection после format mapping; 48 route variants × two turns = 96 actual HTTP upstream bodies, roles/content/order/hoisting и prefix stability PASS. Main spec исправляет unsupported system role; slash redirects проверены с follow_redirects. Hosted provider/public/cloud отдельно. [Evidence](openspec/changes/archive/2026-10-03-verify-plan-json-metrics-contracts/verification.md). |
| [UP-PR-2516](https://github.com/Soju06/codex-lb/pull/2516) | docs: declare native web search support in Codex examples | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2517](https://github.com/Soju06/codex-lb/pull/2517) | fix(telemetry): map codex_cli_rs user agent to codex-cli family | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2518](https://github.com/Soju06/codex-lb/pull/2518) | test(db): cover the SCIM/overflow merge revision's single-head convergence | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2519](https://github.com/Soju06/codex-lb/pull/2519) | fix(http-bridge): parse multi-line upstream websocket frames | RESOLVED / SUPERSEDED BY #2530 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2520](https://github.com/Soju06/codex-lb/pull/2520) | refactor(proxy): extract streaming response entrypoint | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2521](https://github.com/Soju06/codex-lb/pull/2521) | fix(model-sources): validate optional usage and preserve streamed telemetry | RESOLVED / MERGED IN FORK | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §34: 20 new local-upstream route cases for Chat/Responses, stream/non-stream, missing/bool/int32 reasoning, invalid cached counts, timing-sum overflow и multiline CRLF/UTF-8 fragments. Real DB/log API, exact13-token settlement и invalid total502/released/zero counters PASS; full source parser suite PASS. Hosted/public/cloud отдельно. [Evidence](openspec/changes/archive/2026-10-03-repair-usage-and-generation-evidence/verification.md). |
| [UP-PR-2522](https://github.com/Soju06/codex-lb/pull/2522) | perf(db): request_logs facet indexes and loose-scan probes (stacked on #2502) | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2523](https://github.com/Soju06/codex-lb/pull/2523) | fix(metrics): publish fresh account pool gauges on scrape | RESOLVED / MERGED IN FORK | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | §36, F-055: 9 red-before reason/expiry cases исправлены передачей committed rejection reason в shared predicate. Fresh inventory, repair, expiry/deletion, 503→fresh recovery, overlapping reads, optional dependency и multiprocess PASS. Public/cloud отдельно. [Evidence](openspec/changes/archive/2026-10-03-verify-account-pool-probe-recovery/verification.md). |
| [UP-PR-2524](https://github.com/Soju06/codex-lb/pull/2524) | fix(accounts): snapshot force probe state before session cleanup | RESOLVED / MERGED IN FORK | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §36: existing snapshot fix подтверждён через real dashboard route/rollback/close, missing/partial/monthly rows, newer-failure/lease guards и rejected probes. 3 new weekly-primary/elapsed-window cases восстанавливают healthy без изменения history/thresholds. Public/cloud отдельно. [Evidence](openspec/changes/archive/2026-10-03-verify-account-pool-probe-recovery/verification.md). |
| [UP-PR-2525](https://github.com/Soju06/codex-lb/pull/2525) | fix(model-sources): preserve source base instructions in catalogs | RESOLVED / MERGED IN FORK | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §35: existing projection подтверждена через dashboard create/PATCH, actual stored metadata readback и оба Codex catalogs; 9 Unicode/CRLF/whitespace/default cases, latest update/capability preservation/no credentials or overrides PASS. Normative SSOT синхронизирован; hosted/client/public/cloud отдельно. [Evidence](openspec/changes/archive/2026-10-03-repair-source-catalog-output-contracts/verification.md). |
| [UP-PR-2526](https://github.com/Soju06/codex-lb/pull/2526) | fix(model-sources): preserve declared collaboration namespaces | RESOLVED / MERGED IN FORK | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | §35, F-053: 12 red-before dangling namespaced function choices исправлены; 88 recording HTTP cases для обеих Responses routes/slash, v1/v2/future/explicit opt-ins, nested schemas, forced/allowed choices и hosted include pruning PASS. Main contract/context синхронизирован; real provider/client/public/cloud отдельно. [Evidence](openspec/changes/archive/2026-10-03-repair-source-catalog-output-contracts/verification.md). |
| [UP-PR-2527](https://github.com/Soju06/codex-lb/pull/2527) | fix(routing): recover weekly-only Pro reserve accounts | MERGED/CLOSED | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | §36, F-056: 14 real Responses route cases подтверждают post-block weekly-primary recovery, debounce/freshness/exhaustion/rate-limit guards и unchanged owner/storage. Quota Resume восстановлен после 3 red frontend cases; real reactivate CAS и Chromium single POST/refreshed actions PASS, screenshots до/после. Public/cloud отдельно. [Evidence](openspec/changes/archive/2026-10-03-verify-account-pool-probe-recovery/verification.md). |
| [UP-PR-2528](https://github.com/Soju06/codex-lb/pull/2528) | fix(proxy): advertise GPT-6 max output tokens | RESOLVED / MERGED IN FORK | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | §35, F-054: 16 red-before malformed precedence cases исправлены; 44 new cases на трёх GPT-6 slugs/unknown и четырёх public surfaces. Valid upstream counts win, invalid known→128000/unknown→null; metadata/capability/aliases согласованы, input/native raw fields unchanged. Main SSOT синхронизирован; hosted limits/public/cloud отдельно. [Evidence](openspec/changes/archive/2026-10-03-repair-source-catalog-output-contracts/verification.md). |
| [UP-PR-2529](https://github.com/Soju06/codex-lb/pull/2529) | fix(metrics): stop the metrics server from reconfiguring process logging | RESOLVED / MERGED IN FORK | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | §37, F-058/F-059: existing neutral Config подтверждён; real JSON null fields и debug recursion исправлены. Four CLI subprocesses text/JSON × info/debug, both listeners, log path with spaces, stream/file parity, userinfo redaction и numeric 200/503 PASS. Optional uvloop/POSIX shutdown, deployed exporters/public/cloud отдельно. [Evidence](openspec/changes/archive/2026-10-03-verify-plan-json-metrics-contracts/verification.md). |
| [UP-PR-2530](https://github.com/Soju06/codex-lb/pull/2530) | fix(http-bridge): parse multiline websocket JSON messages | RESOLVED / MERGED IN FORK | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | Existing source fix подтверждён: compact/pretty/CRLF errors, native parity, message/tool output items, реальные WebSocket bytes и next-turn recovery. §32, [evidence](openspec/changes/archive/2026-10-02-repair-bridge-json-lite-close-contracts/verification.md); public/cloud отдельно. |
| [UP-PR-2531](https://github.com/Soju06/codex-lb/pull/2531) | fix(proxy): normalize parallel_tool_calls for Responses-Lite upstream | RESOLVED / MERGED IN FORK | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | Existing finalizer подтверждён: omitted/null/true/false, Lite/non-Lite bridge routes, actual direct HTTP и GET426→POST fallback, input/cache/reasoning и untrusted marker controls. §32, [evidence](openspec/changes/archive/2026-10-02-repair-bridge-json-lite-close-contracts/verification.md); public/cloud отдельно. |
| [UP-PR-2532](https://github.com/Soju06/codex-lb/pull/2532) | chore(docker): bump rust from 1.96.0-slim-bookworm to 1.98.1-slim-bookworm | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2533](https://github.com/Soju06/codex-lb/pull/2533) | chore(deps): bump the python-minor-patch group across 1 directory with 17 updates | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2534](https://github.com/Soju06/codex-lb/pull/2534) | feat(proxy): admit bounded inline images on the HTTP responses bridge | RESOLVED / MERGED IN FORK | НЕ ПРОВЕРЕНО | — |
| [UP-ISSUE-2535](https://github.com/Soju06/codex-lb/issues/2535) | feat: show pooled quota in Codex /status by serving and forwarding /backend-api calls | MERGED/CLOSED | ЧАСТИЧНО ПРОВЕРЕНО | API/passthrough/usage suites и actual Codex CLI 0.159.3 с synthetic upstream; §§14/25. Real Desktop /status/live quota incident не закрыт. |
| [UP-PR-2536](https://github.com/Soju06/codex-lb/pull/2536) | feat(proxy): show pooled quota in Codex /status by serving and forwarding /backend-api calls | RESOLVED / MERGED IN FORK | ЧАСТИЧНО ПРОВЕРЕНО | API/passthrough/usage suites и actual Codex CLI 0.159.3 с synthetic upstream; §§14/25. Real Desktop /status/live quota incident не закрыт. |
| [UP-PR-2537](https://github.com/Soju06/codex-lb/pull/2537) | fix(images): route image requests through compatible host | RESOLVED / MERGED IN FORK | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | §43: fallback всё ещё выбирал incompatible Luna перед 5.5. Images candidates теперь Sol/Astra/5.5; probes unchanged, unavailable/suppressed controls и 12 real HTTP generation/edit/alias cases PASS. Public tool/log model, reference bytes и slash405 contract сохранены. [Evidence](openspec/changes/archive/2026-10-04-repair-image-control-transport-contracts/verification.md). Live provider/public/cloud отдельно. |
| [UP-ISSUE-2538](https://github.com/Soju06/codex-lb/issues/2538) | bug(http-bridge): upstream error responses silently swallowed as timeouts - pretty JSON parsing + Responses-Lite parallel_tool_calls | РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §42: обе части issue уже подтверждены §§32/41: full pretty/CRLF WebSocket JSON не теряет terminal error, final Responses-Lite payload использует serial tool calls. Native/slash/error recovery и real HTTP image/tools controls PASS в записанных suites. [JSON/Lite evidence](openspec/changes/archive/2026-10-02-repair-bridge-json-lite-close-contracts/verification.md), [route evidence](openspec/changes/archive/2026-10-04-repair-bridge-terminal-lineage-failover/verification.md). Live Factory/provider/public scope отдельно. |
| [UP-PR-2539](https://github.com/Soju06/codex-lb/pull/2539) | fix(proxy): treat websocket close 1009 as terminal payload_too_large | РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | F-050: typed aiohttp size error сохраняет1009; HTTP/WS до/после output, реальный oversize socket, no replay/health/exclusion, reservation cleanup и same-account recovery. §32, [evidence](openspec/changes/archive/2026-10-02-repair-bridge-json-lite-close-contracts/verification.md); public/cloud отдельно. |
| [UP-PR-2540](https://github.com/Soju06/codex-lb/pull/2540) | fix(quota): reject invalid planner clock times | РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | Strict clock writes/atomic refusal подтверждены; F-048 legacy response/correction исправлена. §31, [evidence](openspec/changes/archive/2026-10-02-verify-planner-scim-cache-admission/verification.md); public/cloud отдельно. |
| [UP-PR-2541](https://github.com/Soju06/codex-lb/pull/2541) | fix(scim): enforce body limits while reading the stream | РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | POST/PUT/PATCH actual stream boundaries/no mutation подтверждены; F-049 declared-length crash исправлен. §31, [evidence](openspec/changes/archive/2026-10-02-verify-planner-scim-cache-admission/verification.md); external IdP/cloud отдельно. |
| [UP-PR-2542](https://github.com/Soju06/codex-lb/pull/2542) | test(shutdown): override the current account import permission | РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §42, TEST SCOPE: permission-override/lifespan regression относится к test_otel.py; полная module suite входила в independent 146-pass logging/OTel selection §37 после исправлений, не в source-author 49-pass claim. [Evidence](openspec/changes/archive/2026-10-03-verify-plan-json-metrics-contracts/verification.md). Новый cloud run не заявлен. |
| [UP-PR-2543](https://github.com/Soju06/codex-lb/pull/2543) | docs(codex): enable API-key model discovery in setup examples | РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2544](https://github.com/Soju06/codex-lb/pull/2544) | chore(metadata): refresh model pricing and Codex version | РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2545](https://github.com/Soju06/codex-lb/pull/2545) | fix(cache): retain failed immediate invalidations | РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | Existing pending retention подтверждена через Pause API, locked/driver/cancelled write, actual retry/DB/peer routing cache, commit ambiguity/namespace isolation. §31, [evidence](openspec/changes/archive/2026-10-02-verify-planner-scim-cache-admission/verification.md); deployed replicas/cloud отдельно. |

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
| [UP-PR-2490](https://github.com/Soju06/codex-lb/pull/2490) | PR #2490: fix(auth): add secret-safe refresh failure diagnostics | Раздел 12, L1347 | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §33: existing source fix независимо проверен real local OAuth HTTP401/400/429/503, actual repository, private/ordinary callers в обоих порядках, one exchange/one safe diagnostic, unknown code→other, no credentials/body/identity leakage, status/credential persistence. Existing unit coverage подтверждает transport и local pre-exchange failures; public/cloud отдельно. [Evidence](openspec/changes/archive/2026-10-03-repair-auth-log-audit-contracts/verification.md). |
| [UP-PR-2489](https://github.com/Soju06/codex-lb/pull/2489) | PR #2489: fix(accounts): preserve quota chart samples and account display state | Раздел 12, L1348 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2488](https://github.com/Soju06/codex-lb/pull/2488) | PR #2488: fix(proxy): handle CRLF and malformed UTF-8 in owner forwarding | Раздел 12, L1349 | НЕ ПРОВЕРЕНО | — |
| [UP-PR-2487](https://github.com/Soju06/codex-lb/pull/2487) | PR #2487: fix(auth): reject non-ASCII TOTP digits safely | Раздел 12, L1350 | ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО | §33: existing ASCII normalization independently verified; fullwidth/Arabic-Indic/Persian/superscript/mixed digits дают HTTP400 invalid_totp_code на setup+verify без enrollment/replay/session mutation; formatted ASCII code затем принимается, replay/window tests PASS. Public/cloud отдельно. [Evidence](openspec/changes/archive/2026-10-03-repair-auth-log-audit-contracts/verification.md). |
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
| [UP-PR-2444](https://github.com/Soju06/codex-lb/pull/2444) | PR #2444: fix(metrics): separate observed generation timing from request latency | Раздел 12, L1369 | ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО | F-052, §34: unit red-before и real HTTP first-output1000→500 reproduced/fixed; parsed content controls spaced/escaped/nested keys без byte rewrite. Both upstream transports сохраняют TTFT125/first output500/two chunks/terminal1000/total3000; log API и qualified daily median40TPS PASS; migration/sample/cohort tests PASS. Public/cloud отдельно. [Evidence](openspec/changes/archive/2026-10-03-repair-usage-and-generation-evidence/verification.md). |
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
| [1f62b4f7](https://github.com/Frozen811/codex-lb/commit/1f62b4f7a902da0b60fa57d32c98d02459eb70e9) | feat(upstream): resolve and integrate upstream issues and PRs #2538-#2545 | ЧАСТИЧНО ПРОВЕРЕНО | §42: current source scope #2538, PR #2539/#2540/#2541/#2542/#2545 локально закрыт с evidence §§31/32/37/41. PR #2543/#2544 ещё не проверены независимо; полное содержимое исторического commit/current-head cloud gate не объявлены verified. |
| [e354c7d3](https://github.com/Frozen811/codex-lb/commit/e354c7d380e865d835e59289f7181044be4f9a77) | docs: add comprehensive update guide for fork users and refresh release links | НЕ ПРОВЕРЕНО | — |
| [eaf9c16d](https://github.com/Frozen811/codex-lb/commit/eaf9c16dbd0e2fd0259a2702124d1b39148d0a01) | fix(db): handle sqlite integer and biginteger reflection equivalence in schema drift check | НЕ ПРОВЕРЕНО | — |
| [c7ca9558](https://github.com/Frozen811/codex-lb/commit/c7ca9558578b1c31bc3fa6bb08de65dba799f824) | feat(proxy): show pooled quota and forward codex chatgpt-backend calls (#2535, #2536) | ЧАСТИЧНО ПРОВЕРЕНО | Backend API/auth/usage suites и actual Codex CLI synthetic product path §§14/25; real Desktop /status и исторический quota incident открыты. |
| [cf820e0f](https://github.com/Frozen811/codex-lb/commit/cf820e0f20d6c90a510364ae684231a99c80ac4d) | docs: document v1.25.0-hardened.2 release and pooled quota setup | НЕ ПРОВЕРЕНО | — |
| [deed76ba](https://github.com/Frozen811/codex-lb/commit/deed76bab5fafa36051c2cf474a1b29055988aae) | fix: live deployment hardening fixes (oauth proxy reauth, continuity owner, image fanout, bridge key, reset credit) | ЧАСТИЧНО ПРОВЕРЕНО / ИСПРАВЛЕНЫ БЛОКЕРЫ | Continuity/source/packaging blockers исправлены последующими commits; §§13–21. INC-04/05/06 локально закрыты с additional fan-out repair, §30; OAuth binding и public/deployed bundle остаются открыты. |
| [7ec39f82](https://github.com/Frozen811/codex-lb/commit/7ec39f82709ee1ca4c00489a8d5fc301d49320ed) | fix(compose): make .env.local optional in docker compose files | ПРОВЕРЕНО ЛОКАЛЬНО — OPTIONAL ENV | Missing .env.local path проверен real dev/prod Compose §§18/19; другие ancestor defects и новые public artifacts учитываются отдельно. |

## 9. Журнал обновления реестра

- 2026-10-02: выполнена registry reconciliation (§28): все136 dirty/untracked paths связаны с шестью archived batches; 34 delivery/governance статуса синхронизированы, source ancestry подтверждена, добавлены F-038–F-045 и scoped cross-references. Исторические snapshots не выданы за current cloud/public verification.
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
| INC-03-OWNER | P1 | ИСПРАВЛЕНО В SOURCE | Sole owner рассматривается по полному разрешённому scope; ошибки listing и неоднозначность сохраняют отказ, владелец проходит normal admission | F-001/F-003/F-004/F-009; source 7d151b9e/f847fc57 присутствует в HEAD; локальные/PR результаты §§13/21, artifact evidence отдельно |
| INC-04-FANOUT | P1 | ИСПРАВЛЕНО ЛОКАЛЬНО / ЗАКРЫТО | Дополнительно исправлены потеря completed usage при cancellation, log failure перед settlement и raw exception response. Generations/edits: partial/all failure, repeated cancellation в cleanup/handoff/release, cached tokens и real quota; 20 route cases. | §30; [evidence](openspec/changes/archive/2026-10-02-repair-fanout-signing-reset-credit/verification.md). Public/deployed artifact отдельно. |
| INC-05-SIGNING | P1 | ЛОКАЛЬНО ПРОВЕРЕНО / ЗАКРЫТО | Existing configured-key fix подтверждён 10 signed sender/receiver cases: env/file precedence, distinct/missing/invalid files, file-only, mismatch и обе primary signature версии. Env mode не создаёт/меняет key files. | §30; [evidence](openspec/changes/archive/2026-10-02-repair-fanout-signing-reset-credit/verification.md). Live replicas/public image отдельно. |
| INC-06-RESET | P2 | ЛОКАЛЬНО ПРОВЕРЕНО / ЗАКРЫТО | Existing missing-target refusal подтверждён 36 authenticated alias/slash/explicit-default-auto/NULL-empty cases: 401 OpenAI envelope, no consume/refresh/snapshot mutation. Valid target использует свой token/ID/redeem ID. На этих consume routes нет API-key token reservation. | §30; [evidence](openspec/changes/archive/2026-10-02-repair-fanout-signing-reset-credit/verification.md). Real redemption/public artifact отдельно. |
| INC-07-PATCH | P1 | ИСПРАВЛЕНО В SOURCE | Patch применён к рабочему дереву и дополнен: typed scope, архитектурные границы, OpenSpec, реальные session/API/WS регрессии и отказ вместо affinity bypass | Коммит автора patch не импортирован; наше исправление 7d151b9e/f847fc57 присутствует в HEAD; §§13/21/28, author patch commit не импортирован |
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
| INSTALL-06 | Wheel из GitHub Release через pip | Правильная ссылка и версия форка; чистая venv на поддерживаемых ОС; зависимости, console scripts, frontend/config/migrations; импорт и старт вне checkout; сеть и подключение Codex | PUBLIC ПРОВЕРЕН Windows/Python 3.13 (§20) и Linux/WSL Python 3.13 (§27): actual pip + uv pip, CLI/migrations/readiness/assets вне checkout, root code соответствует tag после newline normalization; historical runtime drift раскрыт. Real OAuth/Codex/native macOS отдельно; Linux wheel дополнительно проверен §27; §§20/27 |
| INSTALL-07 | Sdist / source archive из Release | Метаданные, состав без чужих worktrees и credentials, сборка wheel из sdist, установка вне checkout, dashboard/config/migrations; скачивание и инструкции | PUBLIC ПРОВЕРЕН: clean rebuild/install/startup, но 5967 nested worktree entries и runtime drift остаются в старом asset. Исправленный local sdist также исключает nested markers, содержит build hooks/assets и перестраивается без Bun; F-014/023, §20 |
| INSTALL-08 | `uv` / `uvx` / установка из индекса | Каждая заявленная команда и канал: действительно ли устанавливает форк, а не upstream `codex-lb`; version pinning, runtime deps, config/data directory и дальнейшие обновления | ПРОВЕРЕНО Windows + Linux/WSL (§27): isolated uvx/uv tool public wheel, source replacement сохраняет data/key; corrected published Git SHA install PASS. Editable-only uv sync exemption проверен после cloud failure; §20 |
| INSTALL-09 | Запуск из Git checkout | clone URL/ref форка, `uv sync --frozen`, frontend и Rust prerequisites, подготовка assets, CLI/start команды; чистое окружение без существующей `.venv` и кешей разработчика | WINDOWS/LINUX SOURCE ПРОВЕРЕНО: fresh no-venv/assets copies + actual anonymous Git clone b5aa440b, frozen setup, frontend/readiness/assets/data recreate; optional Windows native build/discovery/handshake PASS; F-025/027, §21 |
| INSTALL-10 | Windows скрипты / Desktop + WSL | `run.ps1`, `start.bat` и остальные найденные entrypoints; пути с пробелами, PowerShell/cmd синтаксис, prerequisites, Docker Desktop/WSL границы, firewall и startup failures | WINDOWS SOURCE ПРОВЕРЕНО: PS5/pwsh/cmd foreign cwd/path spaces, help, missing uv/wrong Bun, real startup/assets, preserved exit 1/2, data/key reuse; WSL Linux tested separately, no system firewall changes; §21 |
| INSTALL-11 | Linux/macOS скрипты | `run.sh` и документированные команды; shell/permissions, Python/native helper архитектура, env/config paths, background/foreground/restart и корректный выход | LINUX/WSL ПРОВЕРЕНО: executable Bash, clean setup, cwd/args/spaces, readiness/assets, repeat data/key, SIGTERM forwarding/app shutdown/no listener, exit 143. Native macOS не исполнялся и остаётся отдельной границей; §21 |
| INSTALL-12 | Helm / Kubernetes | Fork chart/package/image repository и version; values, secrets, PVC/DB, migrations, probes, service/ingress/OAuth/TLS/WS; clean install, upgrade, rollback; одиночный и документированный multi-replica режим | ЛОКАЛЬНО ПРОВЕРЕНО kind/Kubernetes 1.35 amd64: bundled PG 18.6/PVC, direct URL/generated key, DB-only Secret, existing app Secret, two-pod ring, upgrade/key/DB retention, dashboard и fail-closed bad password. ESO/Ingress/Gateway/TLS/OAuth/real Codex остаются отдельно; F-030/031/032, §22 |
| INSTALL-13 | Nix / flake | Все опубликованные `nix run`/build команды, fork URL/ref, locked inputs, Python/native/frontend contents, runtime/data paths; доступность реального Nix стенда | ЛОКАЛЬНО ПРОВЕРЕНО x86_64 Linux/Nix 2.35.2: package + flake check + editable dev shell; readiness/HTML/JS/CSS вне checkout, env precedence, migration check, DB/key restart, SIGTERM cleanup. EPERM linking и CRLF исправлены; Darwin/ARM64/real Codex отдельно; F-033, §22 |
| INSTALL-14 | Прочие найденные способы | System service, reverse proxy, удалённый сервер, установщик или сторонняя инструкция — отдельная карточка на каждый реально обещанный путь | ИНВЕНТАРИЗАЦИЯ ЗАВЕРШЕНА для README/COMMUNITY_RELEASE/docs/deploy: собственного systemd unit/remote installer нет, restart assumption снят. Shipped nginx example проверен: actual app/assets/Origin/auth + synthetic SSE/WS 101/Host. Caddy/Traefik/Apache/TLS/provider integration не исполнялись; F-034, §22 |
| INSTALL-15 | Distroless и все дополнительные Docker targets | `Dockerfile.distroless`, inline Dockerfile frontend в `docker-compose.yml`, CI build/smoke targets и все найденные overrides; отдельно entrypoint/native helper/CA certificates/non-root/healthcheck, диагностика без shell и реальные платформы | ЛОКАЛЬНО ПРОВЕРЕНО найденных app/frontend targets на linux/amd64; distroless UID 65532, CA/native/healthcheck/recreate, CI delta валиден. Новый cloud CI/CVE scan/ARM64 остаются открыты; §18 |

Docker-инвентарь включает также образы зависимостей в Compose/Helm/CI: PostgreSQL, MySQL и остальные реально используемые сервисы; их версии, readiness, сети, volumes, credentials и совместимость проверяются в контексте каждого соответствующего способа установки. Developer/CI image не считать готовым образом для обычного пользователя. На текущем checkout `docker-compose.yml` содержит development frontend/backend; отдельный `docker-compose.dev.yml` не найден — не придумывать такой файл в инструкции.

### 15.2. Общая матрица конфигурации, сети и клиентского пути

- [ ] **SETUP-01:** повторить точные команды каждого варианта на чистом стенде; записать prerequisites и время до первого рабочего dashboard. Убрать необходимость угадывать URL, путь, имя volume или команду запуска.
- [x] **SETUP-02:** проверить источники и precedence конфигурации: env-файлы и `CODEX_LB_ENV_FILE`, рабочий каталог, CLI/env, defaults и настройки панели; допустимые и ошибочные значения, сообщения об отсутствующем обязательном параметре. Проверить применимость `.env.example` к каждому режиму. **ИСПРАВЛЕНО ЛОКАЛЬНО**, §24.1: discovery/precedence, CLI negative keep-alive regression, dashboard persistence и mode-specific guidance; нового SHA/CI нет.
- [x] **SETUP-03:** проверить data directory, SQLite/PostgreSQL/MySQL в заявленных вариантах, migrations, encryption key, ownership/permissions и сохранение accounts/settings после recreate/update. Backup/restore и rollback проверять на отдельной тестовой БД, не на пользовательском store. **ИСПРАВЛЕНО ЛОКАЛЬНО**, §24.2: isolated paired restore всех трёх backends, schema checks, key/permissions failures. Older-binary downgrade, реальные upstream accounts и новые публичные артефакты не сертифицированы. Дополнение §28: aggregate Windows test failure / isolated retry PASS отслеживается отдельно F-045; стабильность не объявлена доказанной.
- [ ] **SETUP-04:** проверить host/container/client endpoints; loopback и `0.0.0.0`, порты **2455/1455**, port collision, DNS и доступ к upstream; Docker bridge, `host.docker.internal`, WSL/Windows и LAN/remote сценарии. Не рекомендовать контейнерный `localhost` для внешней DB/сервиса без проверки адресации. **ИСПРАВЛЕНО ЛОКАЛЬНО / ЧАСТИЧНО ПРОВЕРЕНО**, §24.3: Windows + Docker Desktop matrix PASS; WSL/физический LAN/Linux host-network runtime evidence остаётся открытым.
- [x] **SETUP-05:** проверить HTTP/SSE/WebSocket через прямой доступ и документированный reverse proxy; TLS certificates/trust, proxy env, timeouts/idle disconnect/reconnect, firewall и failure diagnostics. Для сетевой ошибки записывать точный этап, HTTP envelope/код и безопасный фрагмент логов. **ИСПРАВЛЕНО ЛОКАЛЬНО**, §25.1: direct/stock nginx HTTP/TLS actual routes, certificate trust, SSE/WS/reconnect и scoped env/timeout tests; external forward-proxy/VPN/provider combinations не сертифицированы.
- [ ] **SETUP-06:** проверить локальную и удалённую dashboard authentication, bootstrap/password/API keys, OAuth callback/port и импорт аккаунта. Подтвердить, что инструкция работает без публикации токенов и без отключения обязательной защиты. **ИСПРАВЛЕНО ЛОКАЛЬНО / ЧАСТИЧНО ПРОВЕРЕНО**, §25.2: auth provenance defect, callback bind/cancel cleanup, protected bootstrap/import, synthetic manual exchange PASS. Реальный OpenAI login остаётся открытым.
- [x] **SETUP-07:** подключить поддерживаемый Codex по docs/client-setup.md: effective provider/config, generation и usage endpoints, URL suffix, required auth, HTTP/WS compatibility. На тестовом стенде подтвердить запрос через форк, выбор аккаунта, quota windows и Pause; версия клиента обязательна в evidence. **ИСПРАВЛЕНО ЛОКАЛЬНО**, §25.3: actual Codex CLI **0.159.3**, isolated configuration, HTTP + client WS, account identity, key/pool quota и Pause; upstream synthetic, real entitlement/Desktop sync не объявлены доказанными.
- [x] **SETUP-08:** выполнить документированные update/restart/recreate, сохранить данные и проверить версию после обновления; отдельно rollback с ограничениями совместимости БД. Проверить cached `latest`, pinned tags/digests и отсутствие скачивания upstream вместо форка. **ИСПРАВЛЕНО ЛОКАЛЬНО**, §26.1: explicit fork fetch с upstream origin, actual public pinned old → local source candidate, preserved settings/account/key, recreation и paired old-image restore; general downgrade/public publication не заявлены.
- [x] **SETUP-09:** доказать работу readiness/healthcheck и graceful shutdown; проверить неправильный env, недоступную DB, отсутствие assets/native helper, занятый порт и недоступный upstream. Инструкция должна дать проверяемую диагностику и путь восстановления. **ИСПРАВЛЕНО ЛОКАЛЬНО**, §26.2: forwarded-loopback control defect, actionable asset hint, actual failure matrix/healthcheck/SIGTERM и Linux process/DB tests; Windows console termination отдельно.
- [x] **SETUP-10:** разделить реально проверенные OS/architectures/topologies и непроверенные обещания. `unknown/unknown` attestation не считать ARM64 поддержкой; отсутствие стенда указывать явно. **ИСПРАВЛЕНО ЛОКАЛЬНО**, §26.3: dated guide matrix, live amd64/attestation descriptors, POSIX test scope + executed Linux coverage, Windows helper discovery fixtures; ARM64/native macOS/physical-network certification не подменена x64 evidence.

### 15.3. Проверка описания и простоты установки

- [ ] **DOC-INSTALL-01:** сверить GitHub About, README/переводы, COMMUNITY_RELEASE, release assets/notes, GHCR description, docs navigation и deployment примеры с одним актуальным описанием форка и owning OpenSpec capabilities. **ИСПРАВЛЕНО ЛОКАЛЬНО / PUBLIC ОТКРЫТ**, §§27/28: source navigation и описания сверены; live About/release/OCI и stale Pages требуют public correction.
- [x] **DOC-INSTALL-02:** для всех ссылок/команд проверить owner/repository/version/channel; выявить `uvx codex-lb`, Nix/Helm/image или release URL, которые ведут на upstream. Не заменять ссылку на форк, пока соответствующий fork artifact не существует и не проверен. **ПРОВЕРЕНО ЛОКАЛЬНО**, §§27/28: owner/channel inventory, verified fork wheel/sdist digests, actual historical runtime Windows/Linux. Доступность всех issue/vendor URLs и current-source publication не объявлены подтверждёнными.
- [ ] **DOC-INSTALL-03:** проверить каждую команду copy/paste в её заявленной оболочке; Windows/PowerShell переносы и quoting, Bash quoting, абсолютные/относительные пути и config examples; зафиксировать успешный результат, а не только синтаксическую валидность. **ИСПРАВЛЕНО ЛОКАЛЬНО / EXECUTION ЧАСТИЧНО**, §§27/28: 111 parser checks плюс Windows/Linux pip product/tool/Git; полное инфраструктурное/privileged command execution открыто.
- [ ] **DOC-INSTALL-04:** выбрать основной короткий способ установки после проверки; рядом указать требования, открытие панели, добавление аккаунта, подключение Codex и обновление. Остальные варианты должны иметь понятное назначение и проверенную инструкцию. **ЧАСТИЧНО**, §§22/27/28: explicit channels/prerequisites/readiness/client/update pointers есть; единый короткий primary path после current-artifact certification ещё не выбран.
- [ ] **DOC-INSTALL-05:** исправить неподтверждённые обещания «всё исправлено», «100%», «поддерживается» и «проще», сопоставив их с evidence и ограничениями; F-007 остаётся открытым до проверки исходного реестра. **ЧАСТИЧНО ИСПРАВЛЕНО**, §§23/27/28: local aggregate claims сняты; публичные описания и per-entry semantic audit остаются открыты.
- [x] **DOC-INSTALL-06:** изменения поведения установки сначала оформить в OpenSpec; пользовательские страницы docs/ связать с owning capability, пояснения — в context. Новые README feature sections и ручные правки CHANGELOG не добавлять. **ПРОВЕРЕНО ЛОКАЛЬНО**, §§22–28: шесть OpenSpec batches, 40 completed tasks, requirement/scenario ownership, context/docs backlinks, strict main68 PASS; README feature sections/CHANGELOG не расширялись. Это не public deployment gate.

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

## 21. Main integration и INSTALL-09 / INSTALL-10 / INSTALL-11 — 2026-10-01

### 21.1. Предыдущие исправления перенесены в main

Пользователь поручил перенос после обсуждения main/PR gates. Действующий GitHub аккаунт — owner Frozen811. Использованы четыре тематических PR, merge с сохранением commit ancestry, без force-push. Перед каждым merge проверены exact-head check-runs, успешный CI Required, REST mergeable_state=clean, отсутствие CHANGES_REQUESTED и unresolved non-outdated review threads через GitHub GraphQL; review pagination завершена, findings не пропускались.

| PR | Проверенный source SHA | Merge SHA в main |
|---|---|---|
| [#2 proxy](https://github.com/Frozen811/codex-lb/pull/2) | `feadca30900411efaa2523351315218d5d721c5f` | `f847fc5718f3971ad7bb4c99137b23c007ebc634` |
| [#3 release gates](https://github.com/Frozen811/codex-lb/pull/3) | `72487a38c4daaed70f5633bff76a03829c61da0d` | `245152d7931244f37044713ec0f630cecc42051f` |
| [#4 Docker](https://github.com/Frozen811/codex-lb/pull/4) | `904efd6653a08cd14cc4a6b75547a0690828822e` | `bff1bd56a915cede3c366c124f8d4f11c5cd7e19` |
| [#5 Python](https://github.com/Frozen811/codex-lb/pull/5) | `f61669d62acfe69a15e982d3afadf8a28c1b8b14` | **`8a2b706e4d5ec86f71ec84bd704be8cfde98b7d8`** |

Full CI обнаружил проблемы, не покрытые прежними targeted tests: affinity fixtures raw-inserted accounts после startup snapshot без import availability callback; close-1009 test мокал connected account без committed row. Исправлены только fixtures после реального commit, не Pause/runtime routing guard. Local **11** affinity/close route tests и **25** Pause cases прошли. Дополнительно Nix source filter не включал новый Hatch hook; добавлены только два declared helper files для package/editable variants. Actual [Nix job](https://github.com/Frozen811/codex-lb/actions/runs/36917479916/job/110555586516) на f61669d6 — success.

PR2 final run [36916078511](https://github.com/Frozen811/codex-lb/actions/runs/36916078511), attempt 2 — **success**. В attempt 1 shard2 закончил **1085 passed / 327 skipped**, но job помечен cancelled и aggregate отказал; это не assertion regression. Повторены только failed/cancelled jobs, gate не ослаблен. PR3/4/5 CI Required также success на указанных heads. Новые main-push runs после merge — отдельная evidence chain; не выдавать PR success за уже прошедший final-main CI. Release/tag/GHCR/PyPI publication не выполнялась.

### 21.2. Реальные source-launcher дефекты и исправления

- **F-025:** scripts использовали caller cwd и `uv run codex-lb`, поэтому editable install не готовил ignored dashboard. Isolated Windows cold-source baseline имел `/health/ready` 200, `/` **503**. Added shared `scripts/source_startup.py`: missing assets через pinned helper, затем app.cli в том же interpreter. Helpers honor frozen uv.lock and own checkout; help не требует frontend prerequisites. Внешний cwd не используется для выбора чужого проекта/config.
- **F-026:** Windows PowerShell native CLI error возвращал launcher exit **0**. PS5/pwsh теперь сохраняют $LASTEXITCODE, batch делегирует через quoted own path/system PowerShell и сохраняет errorlevel; interactive pause только без аргументов. Bash shipped mode был **100644**, стал **100755**, script anchors dirname и execs uv.
- **F-027:** реальный Linux source build выбрал Node **18.19.1** через Vite shebang и упал на absent `node:util.styleText`. `build_dashboard.py` теперь использует `bun --bun run build`; это confirmed runtime selection fix, не версия зависимости. Windows/Linux isolated Bun **1.3.14** archives сверены с official SHASUMS256.

### 21.3. Доказательства INSTALL-09/10/11

Windows audit root: `C:\Users\ext\AppData\Local\Temp\codex-lb-install-batch7-20261001\`; fresh source snapshots не содержали .venv/static/node_modules/env. Logs/result scripts retained. Ubuntu 24.04 WSL final source audit: `/home/ext/.cache/codex-lb-launcher-audits/batch7-v22xztgg/`; uv **0.11.16**, isolated Python/cache/data and Bun **1.3.14**, host Node **18.19.1**.

| Продуктовый путь | Итог |
|---|---|
| Cold Windows PowerShell 5 source | **PASS** frontend install/build, readiness/HTML/JS/CSS from foreign cwd, checkout path with spaces |
| Windows pwsh repeat | **PASS** same data/key after restart |
| cmd/start.bat | **PASS** real startup, quoted checkout path/foreign cwd, preserved CLI exit 2 |
| Windows log argument containing spaces | **PASS** actual CLI created the supplied log path; fresh rebuild with forced Bun runtime passed |
| Missing uv | **PASS refusal**, PS and batch exit 1 with actionable diagnostic |
| Wrong Bun 1.4.2 | **PASS refusal**, no dashboard-less server started |
| Help without pinned Bun | **PASS**, CLI options available, no frontend output created |
| Invalid CLI arguments | **PASS**, PS5/pwsh/cmd/Linux returned CLI exit 2 |
| Windows retained state | **PASS**, synthetic dashboard setting false and encryption-key hash survived PS/pwsh/batch restarts |
| Linux executable source run | **PASS**, direct run.sh from foreign cwd/path spaces, cold source build, readiness/HTML/JS/CSS and log-path args |
| Linux repeat/state | **PASS**, setting/key retained on second start |
| Linux foreground SIGTERM | **PASS**, uv forwarded termination; application shutdown completed, listener removed, supervisor returned expected signal exit **143** |
| Optional Windows Rust/native helper | **PASS**, pinned Rust **1.96.0**, own CARGO_HOME/TARGET_DIR build --release --locked; native --help, PATH discovery, protocol handshake and child cleanup |

Windows server tests use only owned process-tree cleanup; graceful Windows console Ctrl+C/close GUI semantics не заявлены выполненными. No real account/OAuth/Codex traffic, native macOS execution, LAN firewall changes или production data. Native transport handshake — не реальный upstream request. WSL tools/data отдельны от Windows, общая SQLite между двумя instances не использовалась.

Intermediate harness failures recorded: baseline incorrectly expected dashboard 404, observed 503; initial cmd nested quote form was wrong, actual cmd call form passed; Python 3.14 module-style help differs from Python 3.13 prog name, assertion now checks product description/options; initial Linux SIGTERM assertion expected zero although uv legitimately returned 143 with complete shutdown; first Linux build failed on old Node and caused the actual --bun fix. None counted as green before correction. Automatic cleanup review rejected removing the disposable static directory without stated reason; no retry deletion, final Windows build used another fresh copy.

### 21.4. Проверки, документация и следующий PR

**35 focused unit cases PASS**, включая 7 new source-startup tests; full Ruff check/format, ty, architecture и strict OpenSpec **68 main specs PASS**. README **222/225**, headings **10/10**, budgets unchanged. PS/pwsh/Bash/cmd source commands, prerequisite pins, explicit frontend rebuild after update, optional Rust PATH setup и WSL/native OS boundaries отражены в owning Python guide/context; CHANGELOG не редактировался.

OpenSpec: [repair-checkout-launchers](openspec/changes/archive/2026-10-01-repair-checkout-launchers/), verified and archived. Ветка **fix/checkout-launchers** опубликована и открыта как [PR #6](https://github.com/Frozen811/codex-lb/pull/6) в main; fixing commit `742fc58d`, main integration commit `7bc6c8f1`, Nix verification archive `b5aa440b`.

Actual anonymous `git clone --branch fix/checkout-launchers` с пустым developer credential helper получил exact source **`b5aa440bccbd4ed9ed5f1e8c86f8aa973a3de579`**. Clone path содержит пробелы, .venv/static absent before launch. PowerShell из foreign cwd с isolated data/cache и pinned Bun выполнил cold build; readiness/HTML/JS/CSS passed. Это независимая проверка опубликованного checkout, не только local source snapshot. Последующий report commit не меняет launcher behavior.

Final main-push [CI 36923500040](https://github.com/Frozen811/codex-lb/actions/runs/36923500040) на **`8a2b706e4d5ec86f71ec84bd704be8cfde98b7d8`** и новый PR6 CI ещё выполнялись при записи отчёта; completed jobs нового PR без failure. Successful preceding PR gates не выдаются за terminal main-push conclusion. No release/tag/image publication. Historical packages/images F-010 не обновлены; release timing остаётся gated по exact-source main CI и artifact verification.

## 22. INSTALL-12/13/14 — Helm, Nix и остальные способы — 2026-10-02

### 22.1. Исходный срез и границы

Baseline checkout: `f52adb72` (`fix/checkout-launchers`), перед работой clean. Изменения этой тройки остаются **в рабочем дереве**: fixing commit, новый current-head CI и release/image publication отсутствуют. CHANGELOG не редактировался. Реестр сохраняет отдельные проверки реального client/OAuth и других платформ; локальный результат не выдаётся за public artifact verification.

Инструменты: Windows host + Docker Desktop Linux engine, Helm **3.19.0**, kind **0.30.0**, Kubernetes node **1.35.0**, Nix **2.35.2** (контейнер `nixos/nix@sha256:7a007c766426c1877758ddc5cb87a965ac131fc78c582ce0083d922d51ae945c`), nginx **1.28-alpine** (`sha256:a8b39bd9cf0f83869a2162827a0caf6137ddf759d50a171451b335cecc87d236`). Synthetic DB/credentials, отдельный kubeconfig/context и контейнеры; пользовательский `codex-lb-server-1` и его volumes не менялись.

Actual source app build: `codex-lb-install-20261002:local`, image ID **`sha256:2a359147af629b6a3bf1505e352622d000307478975eeb738225be68f53b6d44`**. Runtime app соответствует baseline application source; изменены chart/flake/docs, не app API/schema. No GHCR upload.

### 22.2. Helm: воспроизведение, исправление и реальные installs

**F-030:** `docs/deployment/kubernetes.md`, chart README/metadata/default image и local smoke tags выбирали upstream. Defaults теперь `frozen811/codex-lb`; инструкции используют source chart + явно построенный image. Public fork aliases раскрыты как historical. Upgrade drain исправлен с несуществующего Deployment на `statefulset/codex-lb-workload`, с ожиданием удаления старых pods. DB/key backups, PVC/Secret retention, ограничения rollback и отдельный OAuth callback описаны.

**F-031 baseline 1:** fresh external PostgreSQL URL + chart-managed app Secret + `helm install --wait --timeout 50s` → **exit 1/context deadline exceeded**, pod `Init:0/1`, migration Job отсутствует. Helm waits for Ready до post-install hook: schema gate ожидает миграцию, которая не запускается.

**F-031 baseline 2:** existing DB-only Secret + generated app key + `--timeout 35s` → **exit 1/failed pre-install**. Kubernetes event: `secret "key-baseline-codex-lb" not found` при mounting encryption-key. DB Secret не доказывал доступность app Secret.

Теперь generated/materialized app credentials используют обычную install Job. `auth.existingSecret` сохраняет pre-install/pre-upgrade hook; остальные upgrades — pre-upgrade. Bundled mode сохраняет startup migration, install Job отсутствует. Schema gate external mode не отключался. CI smoke теперь создаёт **отдельную пустую БД** для direct URL/generated Secret и проверяет две replicas; wrapper прошёл Bash syntax check, новый cloud run не выполнялся.

| Проверка реального Kubernetes пути | Результат |
|---|---|
| Direct URL, empty external DB, generated app Secret, --wait | PASS: migration Job Complete, 2 Ready pods |
| Existing DB-only Secret, empty DB, generated key | PASS: Job Complete, Ready app |
| Existing app Secret с DB URL/key, empty DB | PASS: pre-install migration + 2 Ready pods |
| Two-replica `/health/ready` | PASS: ring_size=2, is_member=true |
| External install upgrade / pod replacement | PASS: key SHA-256 тот же, synthetic row `kept-through-upgrade` сохранена |
| Wrong DB password | EXPECTED FAIL: Helm timeout, migration Error, app Init:0/1; трафик не admitted |
| Bundled Bitnami PG 18.6/PVC + source app | PASS: PG/app Ready, upgrade и Helm test Passed |
| Actual dashboard HTML и referenced assets | PASS: external/bundled, 17 nonempty JS/CSS assets |
| Helm test external release / lint --strict | PASS |

Bundled chart **18.6.7** был locked, но его DB image использовал mutable `latest`. Реальная anonymous загрузка и `postgres --version` подтвердили **18.6**. Image теперь pinned **`sha256:c7f76dc578e0a4bb7f49dadeb7a625239349b1e22b420fa9e4500c69c7d13f8f`**, actual pinned upgrade PASS. Это PostgreSQL artifact, не fork application publication.

**F-032:** приложение становилось Ready, но version metadata cache выдавал `OSError: Read-only file system: /home/app/.codex-lb`. В Kubernetes Docker marker не гарантирован. ConfigMap теперь задаёт `/tmp/codex-lb` на writable emptyDir; migration Job получает `CODEX_LB_ENCRYPTION_KEY_FILE=/var/lib/codex-lb/encryption.key`. После upgrade actual write/settings checks PASS, read-only error отсутствует. Scratch archives/cache ephemeral; DB/key durable, отдельный archive PVC документирован через существующие extras.

Не исполнялись: ESO/SecretStore provider, Ingress/Gateway controllers, real TLS/certificates, OAuth/Codex account traffic, реальные managed Kubernetes clouds и ARM64. Rendered tests проверили ExternalSecrets и routing/monitoring/shutdown artifacts; они не заменяют live provider check.

### 22.3. Nix: чистый package и запуск вне checkout

Archive baseline source не содержит developer venv/assets. Первая actual Nix build воспроизвела **EPERM** на 747 dependency links: build user пытался hardlink root-owned immutable store files. `bunInstallFlags` теперь **isolated + copyfile + frozen-lockfile**. После копирования Windows working flake следующая сборка воспроизвела embedded-shell **$'\r': command not found**; `.gitattributes` задаёт `*.nix text eol=lf`. Actual LF/copyfile build PASS, formatter PASS, flake check PASS. Package store output: `/nix/store/qsn8g7www8w4915rhk7rm69n6fdyy5cb-codex-lb-1.25.1` (до cosmetic nixfmt; same package behavior).

| Проверка Nix installed runtime | Результат |
|---|---|
| Package build + flake check x86_64-linux | PASS |
| `nix develop` editable import | PASS: import указывает на `/work/source/app/__init__.py` |
| CLI help / invalid argument | PASS: exit 0 / exit 2 |
| Четыре normal starts вне checkout | PASS: readiness, HTML, referenced JS/CSS |
| `.env` затем `.env.local` | PASS: SQLite создаётся в directory из .env.local |
| Explicit CODEX_LB_ENV_FILE / process env override | PASS: separate selected stores |
| Restart DB/key retention + migration check | PASS: same key hash, DB preserved, check exit 0 |
| SIGTERM cleanup | PASS: Application shutdown complete, bounded exit, listener отсутствует; captured signal exit -15 |

README/translation/getting-started выбирают `nix run .` из fork checkout. Новый owning guide объясняет full-SHA remote fork URL, lock/input toolchain, storage, env precedence, update/DB rollback и optional native-helper boundary. Bare upstream URL больше не является fork installation command.

Aarch64 Linux/Darwin не исполнялись. Flake объявляет их, но local verification относится к x86_64 Linux. Реальный native-egress/Codex/OAuth не доказан readiness тестом. Nix package/development source filter из F-029 сохранён.

### 22.4. INSTALL-14: инвентарь и nginx

README/переводы, COMMUNITY_RELEASE, docs/, deployment files просмотрены на дополнительные installers/services. Собственный `codex-lb.service` и one-command remote installer не обнаружены. COMMUNITY_RELEASE больше не обещает `systemctl restart codex-lb` после install без unit; independently managed supervisor описан отдельно. Traffic-parity user timer относится к developer canary, не к app installation.

Shipped `deploy/nginx.conf` подключается в http context, слушает 8080 → loopback 2455, сохраняет Host/port, overwrites client forwarding headers, HTTP/1.1 Upgrade, SSE buffering off, read/send timeout 3600. Same-host trust CIDR и container namespace/service-name различия отражены в remote guide. TLS/OAuth callback не подменяются открытием dashboard.

- Actual app behind unchanged nginx file: `/health/ready`, dashboard HTML и все assets **200 PASS**.
- Dashboard password setup с matching Origin → ожидаемый **401 invalid_bootstrap_token**; cross-site Origin → **403 cross_site_request_rejected**. Host/port preserved, remote bootstrap не обойдён.
- Actual unauthenticated app WebSocket → expected **401** authentication refusal.
- Separate disposable aiohttp protocol backend: first SSE event received до delayed second event, **PASS**; WebSocket **101/echo**, Host с nonstandard port preserved, **PASS**.
- nginx config syntax **PASS**. Caddy/Traefik/Apache/provider auth/real TLS не исполнялись; их упоминания не являются certification.

### 22.5. Проверки и оформление

**120 focused unit tests PASS** (реальный Helm доступен, skips нет), full Ruff check/format и ty PASS. Все 5 architecture checkers PASS, thresholds не менялись. MkDocs **strict build PASS**. Simplicity: README **222/225**, headings **10/10**, env **47/60**, core nav **5/5**, root entries **0/0** — budgets unchanged.

OpenSpec validator совпадает с pinned CI tool **1.11.0**: **68 main specs strict PASS**, change и оба modified capabilities strict PASS. Первоначальный локальный вызов старого CLI 1.3.0 дал 18 failed capabilities / 71 errors; isolated exact-HEAD comparison подтвердил тот же baseline error set без новых ошибок. Это несовместимость старого validator, не основание менять 18 unrelated specs. После выбора CI-pinned version все проверки прошли.

Intermediate test harness assumptions исправлены до PASS: bundled resources нельзя выбирать только по kind (первым был PostgreSQL StatefulSet), external-secrets fixture требует external-mode overlay, Windows docs reads используют explicit UTF-8, Nix SIGTERM legitimately preserves -15, actual WebSocket auth refusal — 401. Первый bundled wait 50s был слишком коротким для cold pull/migrations; фактический Ready/upgrade/Helm test проверены затем с 120s window.

OpenSpec: [repair-alternative-installation-paths](openspec/changes/archive/2026-10-02-repair-alternative-installation-paths/), verified and archived; requirements/context synced to main; verification report содержит mapping каждого требования на tests/runtime evidence. Работа локальная; текущая публикация этой тройки и новые cloud checks отсутствуют.

## 23. F-007 / CI-02 / REL-03 — claims, CI selection и fork workflows — 2026-10-02

После INSTALL-01…15 взяты три открытых пункта следующего audit блока. Базовый checkout HEAD **`f52adb7274c96c0702e19aa02eabd4f1c7556231`**, исправления — локальный незакоммиченный delta поверх существующих INSTALL-12/13/14 правок. Ранее выполненные изменения сохранены; нового source SHA/cloud CI/release/deployment этой тройки нет.

### 23.1. F-007: арифметика и границы evidence

README обещал **165/165 Resolved** и **164/100%**, ISSUES summary смешивал **108/110/164/0 задач**, COMMUNITY_RELEASE — **156 Issues/101 PR/132 проблем** и полный green без привязки к SHA. Независимый recount всех `https://github.com/Soju06/codex-lb/{issues,pull,discussions}/N` в ISSUES.md, с dedup по паре `(тип URL, номер)`, дал **120 Issues + 128 PR + 49 Discussions = 297 ссылочных записей**. Ссылки внутри описаний входят в inventory; это не число текущих открытых Issues или уникальных задач. Historical category sums — **158 «Всего» / 184 «Решено»**, включая Discussions; некоторые category rows «решено» больше «всего».

README badges/banner, перевод и community overview/quality sections больше не заявляют общую завершённость или production certification. Historical release name/tag retained, package metadata и subsequent source/artifact distinction explicit. ISSUES summary содержит правило/count/date и attribution: все исходные resolved markers и тестовые заявления исторические до отдельной карточки evidence. Body/source links сохранены. F-007 исправлен в части неверного представления результата; **полный независимый проход 297 records не выполнен и не объявлен закрытым**.

### 23.2. CI-02 / F-035: выбор реальных checks

Подтверждено CLI-output regressions: перенос `app/example.py → docs/example.py` выдавал backend=false; частичный или malformed API список мог считаться полным; Nix filter пропускал изменения app/config/frontend sources, README/LICENSE и `scripts/hatch_build.py` / `scripts/build_dashboard.py`. Hatch helpers уже запускали backend/Docker — дефект их пропуска относился к **Nix**, а не к отсутствующему root hook.

Detector теперь проверяет count уникальных текущих filenames против event changed_files, добавляет previous_filename отдельно для filters, распознаёт повторные/malformed entries, incomplete pagination, cycles/API limit. При неизвестном count, API error, неполном evidence или изменении workflows/selector/shared API helper/line-ending policy выбирается full suite через existing CI workflow sentinel. Nix filter включает потребляемые package sources. Обычный docs-only PR остаётся selective; пустой complete list корректен. Публичный CLI contract сохраняет те же семь outputs.

GitHub API ограничен [3000 файлами](https://docs.github.com/en/rest/pulls/pulls#list-pull-requests-files); превышение ceiling не трактуется как complete evidence. Tests покрывают также outage на второй странице после успешной docs-only первой страницы. Production API/session/routing не менялись.

### 23.3. REL-03 / F-036: fork docs и upstream authority

Live read-only GitHub evidence подтвердило workflow-based Pages и опубликованный HTML с upstream edit links. MkDocs repository/edit links теперь Frozen811; owning OpenSpec tree/blob links в docs и settings-reference generator также fork. Main docs build получает base_url от pinned `actions/configure-pages` с **pages:read**, enablement=false; PR/local builds используют fork default. Deployment permission scope/main-only condition сохранены.

Actual strict rendered builds с default `https://frozen811.github.io/codex-lb/` и isolated `https://docs.example.test/custom/codex-lb/` прошли; canonical URL, fork edit link и owning-spec link проверены в generated HTML. Отдельная disposable page с missing internal link дала ожидаемый **strict exit 1**. Settings reference соответствует regenerated output.

Upstream Release Please/beta/metadata/artifact guards на `Soju06/codex-lb` — intended skips. Upstream failure-withdrawal job теперь тоже repo-scoped: cancellation в fork не даёт upstream cleanup authority редактировать fork release. Independent fork publisher/exact-source gates не ослаблены; existing regressions passed. Нового cloud run этих YAML не выполнялось.

**F-037 остаётся отдельно:** Pages API сейчас сообщает `http://extr3me.me/codex-lb/`, cname отсутствует, https_enforced=false; default fork Pages URL реально redirects на HTTP endpoint. Direct HTTPS fetch custom host завершился URLError, точная transport cause не установлена. Изменение metadata исправляет следующий rendered build, но не означает cloud deployment или исправление account-level HTTPS/redirect settings. Эти настройки не менялись.

### 23.4. Проверки и завершение

- До implementation новые regressions дали **33 failed / 15 passed**, воспроизведя defects. Финально пять focused files — detector/GitHub API, fork automation scope, required CI contexts, fork release publication, generated settings reference — **143 passed**, один existing Starlette/AnyIO deprecation warning.
- Modified Python Ruff check/format **PASS**; actual MkDocs strict default/custom renders **PASS**, broken-link negative probe **PASS**.
- Simplicity unchanged: README **222/225**, headings **10/10**, env **47/60**, core nav **5/5**, root **0/0**.
- OpenSpec change strict validation CI-pinned **1.11.0 PASS**; requirements/context synced, verified change archived, **68 main specs strict PASS**, `git diff --check` **PASS**. Все 7 tasks завершены.

OpenSpec: [repair-audit-and-ci-evidence](openspec/changes/archive/2026-10-02-repair-audit-and-ci-evidence/), полный requirement/scenario mapping — verification.md. Commit, push, merge, tag/release, workflow dispatch, registry publication, Pages settings mutation и production deployment не выполнялись. Следующий открытый блок: SETUP-02/03/04 (configuration/data/network matrix) и semantic per-entry audit; public-artifact/new-cloud/Pages HTTPS limitations сохраняются.

## 24. SETUP-02 / SETUP-03 / SETUP-04 — configuration, paired restore и endpoints — 2026-10-02

Базовый HEAD **`f52adb7274c96c0702e19aa02eabd4f1c7556231`**. Новый локальный delta поверх сохранённых INSTALL-12/13/14 и F-007/CI-02/REL-03 правок; нового commit/cloud CI/release нет. Проверка использовала временные stores и синтетический paused account, без production DB, реальных upstream credentials или изменения существующего `codex-lb-server-1`.

### 24.1. SETUP-02: источники конфигурации и ошибочные значения

Подтверждено: configuration guide ошибочно обещал `.env.local` «next to the process». Python discovery привязан к module root, explicit `CODEX_LB_ENV_FILE` выбирает ordered list с `os.pathsep`; относительные пути разрешаются из cwd. Default < earlier env file < later env file < process env; non-NULL dashboard override остаётся выше env для dashboard-owned settings. Listener CLI/env — отдельный путь, unprefixed HOST/PORT в application dotenv не задают listener defaults.

CLI принимал отрицательный keep-alive из флага и env: новые regressions до правки **2 failed / 1 passed**. Теперь negative value завершается до создания store/server с named diagnostic, zero valid. Existing integer/port/TLS tests сохранены. Env-file tests проверяют порядок файлов, process override, relative paths, ignored unknown names/missing files и bool_parsing diagnostic. Native source launch default/env paths и dashboard override проверены actual CLI/HTTP.

Docs и `.env.example` объясняют Python, standalone Docker, Compose, Nix и Helm ingestion, platform separators, reload boundary, optional SQLite defaults и shared DB/key prerequisites. Nix/Helm behavior опирается также на prior isolated runtime evidence §22, а не на обещание нового запуска этих installers. Fork links corrected. Новых setting fields/env options нет.

### 24.2. SETUP-03: реальные DB/key snapshots и restore

Подтверждено: database guide и Docker storage paragraph представляли копию data directory как достаточную backup-инструкцию без оговорки для external SQL. Теперь руководство различает consistent SQLite backup API, SQL logical dump, независимые key/archive/spool paths, writable ownership и restore старого executable с его paired snapshot. Binary/Helm rollback не обещает schema downgrade.

| Проверка | SQLite (Windows CLI) | PostgreSQL `postgres:18-alpine` | MySQL `mysql:8.4` |
|---|---|---|---|
| Fresh startup/migrations/readiness | PASS | PASS | PASS |
| Persisted dashboard override + paused account after restart/recreate | PASS | PASS | PASS |
| Snapshot/dump restore into isolated store | backup API → empty directory PASS | custom pg_dump → createdb/pg_restore PASS | mysqldump → empty DB/mysql import PASS |
| Matching-key decrypt of synthetic access/refresh credentials | PASS | PASS | PASS |
| Dashboard wins over changed env; clearing returns to env | PASS | PASS | PASS |
| `codex-lb-db check` | migration_policy=ok, schema_drift=none | same, original + restored | same, original + restored |

Source-mounted `/app/app` used current local code; dependency runtime image **`sha256:2a359147af629b6a3bf1505e352622d000307478975eeb738225be68f53b6d44`** is an environment dependency, not newly certified public source artifact. DBs/volumes/networks were separately named and removed after rehearsal. Stock user **UID 1000**, generated key **0600**, identical key across recreate PASS. Unwritable storage refused startup. Replacing the restored SQLite key with another valid Fernet key refused startup with fingerprint mismatch. Docker SIGTERM completed graceful shutdown; Windows test termination is crash-style and is not claimed as graceful SIGTERM evidence.

The exact Python backup snippet extracted from docs was executed: committed WAL row retained, standalone journal_mode=DELETE snapshot, existing destination refused **PASS**. SQLite restore regression additionally verifies account inventory/settings through the actual HTTP endpoints. The test's same-interpreter post-crash reader produced disk I/O errors while a fresh reader reported integrity=ok and retained rows; final rehearsal separates snapshot writer and restored-store reader into fresh processes. This is not recorded as a proven application corruption defect. Snapshot handles close explicitly before starting the restored application.

Older-binary schema downgrade, DB-major upgrades, ARM64/Darwin ownership, archive content recovery with active user data and actual upstream account use are not inferred from this synthetic restore. No migration files or backend code changed.

### 24.3. SETUP-04: address spaces, callback and failure stages

Remote guide now separates bind host from client URL, container loopback from sibling/host DB, published host ports, Docker Desktop host endpoint, Linux host-gateway prerequisites and WSL addressing modes. It identifies HTTP **2455** and fixed temporary OAuth callback **1455** separately. Publishing a callback port does not start a listener; TLS/OAuth/client authentication remain separate setup paths.

Actual Docker Desktop checks against current source runtime:

- User-defined bridge + loopback-published random host port: readiness/dashboard HTML **PASS**; container-local `127.0.0.1:2455` **PASS**.
- `host.docker.internal` → disposable host HTTP listener bound to all IPv4 interfaces **PASS**. Sibling `postgres:5432` / `mysql:3306` authenticated DB paths were exercised in §24.2.
- Callback 1455 before account login correctly has no listener **PASS**; real OAuth bind/tunnel/login belongs to SETUP-06 and was not performed.
- Outbound `chatgpt.com` DNS **PASS**; reserved `.invalid` hostname fails with `gaierror` before TCP; `https://auth.openai.com` returns **HTTP 403** after transport, not OAuth success.
- Busy Docker-published host port refused; second native CLI on the existing container HTTP port refused with address-in-use **PASS**. CLI collision test uses a separate temporary store to isolate listener failure from shared-store/ring lifecycle.

**SETUP-04 checkbox remains open** for WSL mode transitions, physical LAN/remote clients, native Linux host-network/gateway execution and actual Wi-Fi/VPN DNS switching. The available Windows/Docker Desktop matrix and documentation fixes are complete; none of those other platform paths is labelled certified. SETUP-05/06/07 are the next independent transport/auth/Codex tasks.

### 24.4. Проверки и OpenSpec

**204 focused tests PASS**: CLI/env-file/home-dir **55**; settings/tier/seeding/connect-address/Docker-networking/settings API **146**; fresh CLI persistence/restore/negative-timeout process tests **3**. One existing Starlette/AnyIO deprecation warning. Full Ruff check/format **PASS** (1424 files), full ty **PASS**, all five architecture checkers **PASS**, thresholds unchanged. MkDocs strict rendered build **PASS**.

Simplicity: README **222/225**, headings **10/10**, env example **54/60**, core nav **5/5**, root entries **0/0**, Settings fields **98/98**. Added explanatory template comments fit the existing budget; no budget/config expansion.

OpenSpec: [repair-setup-configuration-data-network](openspec/changes/archive/2026-10-02-repair-setup-configuration-data-network/). Four added requirements / six scenarios synced to deployment-installation and deployment-networking; stable rationale in owning context.md files; verification.md maps every scenario to its tests/runtime/docs. CI-pinned OpenSpec **1.11.0 strict change validation PASS**, **68 main specs strict PASS**. Archive follows verified task completion. Commit, push, merge, publication, workflow dispatch and production deployment were not performed.

## 25. SETUP-05 / SETUP-06 / SETUP-07 — transport, auth и actual Codex client — 2026-10-02

Base HEAD **`f52adb7274c96c0702e19aa02eabd4f1c7556231`**. Изменения локальные поверх предыдущих сохранённых batches; нового SHA/cloud CI/release нет. Тестовые stores, credentials и upstream изолированы. Существующий `codex-lb-server-1` не менялся; rehearsal containers/volumes удалены.

### 25.1. SETUP-05: authenticated transport и TLS

Source-mounted `/app/app` использует текущий код; dependency image `sha256:2a359147af629b6a3bf1505e352622d000307478975eeb738225be68f53b6d44`, nginx `1.28-alpine`. Это не новый public image. Shipped `deploy/nginx.conf` не менялся: TLS adaptation сохраняет directives и добавляет listener/certificate/key. Self-signed test certificate с IP SAN используется как explicit trusted CA; verification не отключалась.

| Product path | Direct HTTP | nginx HTTP | nginx TLS |
|---|---|---|---|
| Actual authenticated generation requests | PASS | PASS | PASS |
| SSE first event before delayed completion | PASS, 0.125s | PASS, 0.101s | PASS, 0.063s |
| Actual proxy WS event completion | PASS | PASS | PASS |
| Close + fresh WS reconnect | PASS | PASS | PASS |

Times — локальное последнее наблюдение, не performance guarantee. Responses проходят через реальный proxy и синтетический upstream; это больше, чем echo transport, но не OpenAI generation. TLS: trusted matching certificate **PASS**, default trust refuses untrusted fixture CA **PASS**. На Windows fixture `localhost`/IPv6 path давал около 10s задержки TLS или handshake timeout при IPv4-only publication; IP SAN + явно проверенный `127.0.0.1` устранили этот неоднозначный маршрут без увеличения application timeout budgets.

Remote guide объясняет разные projection/application trust settings, Host/scheme, certificate verification, nginx 32 MiB body cap, idle timeout scopes и отличие synthetic WS probe от product request. Existing outgoing proxy-env tests выявили Windows fixture bug: `setenv(lowercase)` затем `delenv(UPPERCASE)` удалял то же значение. В четырёх tests порядок исправлен; assertions/production proxy resolution не менялись. Broader client/HTTP/WS suite сначала **4 failed / 174 passed**, затем **178 passed**. Physical firewall/VPN, real authenticated outbound forward proxy, live TLS-provider setups и все реальные idle/replay combinations не сертифицированы.

### 25.2. SETUP-06: два подтверждённых auth/lifecycle defects

**Trusted-header:** sanitizer и resolver доверяли `request.client` после proxy projection. Trusted socket `127.0.0.1` с forwarded user `203.0.113.42` ошибочно возвращал **401**; untrusted socket с projected loopback получал **200** при широкой projection allowlist. Неперехваченный raw peer тоже мог выдавать principal. Новые regressions до исправления **3 failed / 1 passed**. Оба consumers теперь используют existing `raw_socket_peer_host`; missing capture fails closed. После исправления valid route/session **200**, spoof/duplicate **401 proxy_auth_required**, audit mutation сохраняет asserted actor и projected client IP **PASS**. Forwarded caller IP не заменяет socket proxy authority.

**OAuth callback:** failed/cancelled startup оставлял initialized AppRunner, а swallowed bind OSError не имел полезной диагностики. Новые bind/cancel/warning regressions до исправления **3 failed**. Listener очищает собственные ресурсы до propagation; bind warning содержит host/port/exception type, без callback query/state/code/verifier. Occupied real TCP port → pending browser flow → actual manual-callback route с явно synthetic token exchange → stored account success **PASS**. Cancellation cleanup и повторный bind того же server object **PASS**. Existing expiry/race/replay/log-privacy suite сохранена.

Actual TLS-proxy runtime: setup без bootstrap token → **401 invalid_bootstrap_token**; правильный fixture token/password → **200** + session; foreign Origin mutation → **403 cross_site_request_rejected**; API key создаётся через authenticated dashboard; keyless generation → **401**; synthetic auth file import → **200**. Инструкции не обещают locality по одному localhost URL и объясняют manual callback/device alternatives. Реальные user tokens/passwords не использовались.

**SETUP-06 остаётся открытым для реального OpenAI login/entitlement.** Synthetic exchange, callback listener и импорт не подменяют эту проверку. Доступные local/remote-auth code paths исправлены и проверены; credentials у пользователя не запрашивались.

### 25.3. SETUP-07: реальный клиент и observable routing

Installed **`codex-cli 0.159.3`**, Windows x64; isolated `CODEX_HOME`, ephemeral credentials, strict config, readonly sandbox, no tools, plugins off. `auth.json` не создавался и пользовательская конфигурация не редактировалась. Actual executable получил **SETUP_OK** из реального codex-lb с fixture upstream.

- `env_key` + `requires_openai_auth=false` → HTTP completion **PASS**. С `true` completion также **PASS**. Это version-specific observation: [официальная auth documentation](https://learn.chatgpt.com/docs/auth#alternative-model-providers) сейчас говорит, что true игнорирует env_key. Guide сохраняет distinction, explicit false CLI path и отдельные Desktop/Daybreak eligibility contracts.
- WS-declared provider → **1 actual client WebSocket connection** в server logs, **2 upstream WS response requests**, completion **PASS**. HTTP path проверен отдельно; supports_websockets не объявлен гарантией для всех будущих клиентов.
- Fixture generation ledger: **14 requests**, все с выбранным **`cgpt-setup`** и Authorization; includes transport checks, CLI turns и explicit probe. Request content/credential values не публикуются.
- Actual account probe обновил stored upstream windows: **primary 10%, secondary 20%**. Matching ChatGPT identity `/backend-api/wham/usage` вернула эти pooled windows **PASS**.
- API-key caller `/api/codex/usage` вернул настроенные **credit** windows **18000 / 604800 seconds**. До добавления credit limits rate_limit был null — корректный иной contract, а не pool percent. Docs уточняют identity-dependent output и не обещают конверсию token-count limits в credit windows.
- Pause выбранного account перед новым запросом → **503** с no-account refusal, fixture generation count не увеличился **PASS**. Это не claim о мгновенной отмене уже начатых responses или причине исторического INC-08.

Guide conflict marker removed. Downloadable TOML usage base исправлен с root на **`/backend-api`**; generation/catalog suffixes согласованы. Удалена гарантия seamless cloud conversation sync от одного provider-key override. Все guide TOML blocks parse; marker/suffix regressions **PASS**. Real model entitlement, OpenAI subscription accounting, Desktop/cloud sync и сторонние клиенты не доказаны этим CLI fixture.

### 25.4. Проверки, OpenSpec и очередь

**324 unique focused tests PASS**: auth/OAuth/projection/lifecycle **122**; trusted identity/raw firewall/bootstrap **24**; backend passthrough/Codex payload/outbound WS/HTTP/API auth/client examples **178**. Updated audit-actor и occupied-port manual recovery assertions дополнительно прошли в своих focused files; это не добавлено к unique count. Existing Starlette/AnyIO deprecation warning.

Full Ruff check/format **PASS** (1427 files), full ty **PASS**, пять architecture checkers **PASS**. MkDocs strict rendered build **PASS**. Simplicity неизменна: README222/225, headings10/10, env54/60, core nav5/5, root0/0, Settings98/98. Новых env/settings/dependencies/migrations нет.

OpenSpec: [repair-setup-transport-auth-client](openspec/changes/archive/2026-10-02-repair-setup-transport-auth-client/), four requirement blocks / eight scenarios synced to admin-auth, oauth-callback-privacy, deployment-networking и user-documentation; verification.md содержит mapping. CI-pinned **1.11.0 strict change/main specs PASS** (68 capabilities); verified change archived. Runtime ledger: local Temp/codex-transport-20261002/report.json; fixture scripts/logs — disposable local evidence, не release artifacts.

Следующая самостоятельная тройка: **SETUP-08/09/10**. Остатки SETUP-04/06, public-artifact/cloud evidence, Pages HTTPS и semantic per-entry audit остаются открытыми. Commit, push, merge, production deployment, workflow dispatch и публикация не выполнялись.

## 26. SETUP-08 / SETUP-09 / SETUP-10 — update, lifecycle и platform evidence — 2026-10-02

Base HEAD **`f52adb7274c96c0702e19aa02eabd4f1c7556231`**, новый локальный delta поверх сохранённых предыдущих batches. Shared checkout не переключался; `codex-lb-server-1` не перезапускался. Production stores/credentials не использовались; все runtime rehearsal containers/volumes удалены.

### 26.1. SETUP-08: правильный source, cached tag и paired rollback

Подтверждено: COMMUNITY_RELEASE update examples использовали `git pull origin main`, хотя `origin` в этом checkout — **Soju06**, а `fork` — **Frozen811**. Теперь guide явно выбирает fork URL/full reviewed SHA, проверяет clean tree и ошибки fetch/switch, напоминает про остановку writers, paired backup и rebuild changed frontend. В отдельном пустом checkout с upstream origin реально выполнены explicit Frozen811 fetch и detached selection **f52adb72…**; origin остался upstream. Это проверка команды, не применение удалённого SHA к shared dirty checkout.

Живой read-only registry check: `latest` index **`sha256:ad9aa84b12bce9f6afc63adb3aa86e73f6aafca1814e6f20b486b00f21c60447`**, amd64 runtime manifest **`sha256:31557c9d04de1fb263b022b0ab1309c4d020675309a69ecac2d19365d35b3087`**. Runtime manifest отдельно pulled по immutable digest, без retargeting user aliases.

| Объект | Наблюдение |
|---|---|
| Public pinned runtime image ID | `sha256:21776e26b83f738e13afa29a134175cd8a0edd7a7c9a46f02bcf523e47aeab97` |
| Public OCI labels | source Frozen811, revision `f622c5632013d24ce9236d176113087b387c7990`, version **1.25.1** |
| Actual old runtime | **1.25.0-beta.9**, Docker HEALTHCHECK отсутствует |
| Existing local cached aliases before pull | `bf95e76a…`, RepoDigests empty, different image ID; local tag/version alone is not registry provenance |
| Final current-source overlay | `sha256:f0901e61dc90376a35b0a79604bc2f25e2791dc36dded11607503e85816c7229`, runtime **1.25.1** |

Candidate копирует текущие app/config/scripts поверх dependency image **`2a359147…`**; это ограниченный local source-overlay rehearsal, не новая full-build/public release certification. Версия не bump-илась для теста. OCI public description всё ещё содержит historical «100% verified» claim — неизменяемый старый artifact не исправлен редактированием текущих docs; public-artifact claim gate остаётся открытым.

Runtime sequence: old pinned image → synthetic paused account + stored setting → clean stop → pre-upgrade DB/key snapshot → candidate migration/startup → current recreate → old image с matching snapshot в **отдельном пустом restore volume**. Во всех применимых стадиях settings/account inventory, decrypt synthetic access/refresh и identical key **PASS**. Candidate и old restored `codex-lb-db check`: **migration_policy=ok / schema_drift=none**. Старый image не открывал migrated original store; downgrade newer schema не объявлен безопасным.

Mutable-tag probe менял только task-specific tag: пока old container работал, tag уже указывал на candidate, но container `.Image` и runtime остались old; recreate выбрал candidate **PASS**. Docker/Python guides разделяют local image IDs, registry index/manifest digests, runtime/package/source identity. Kubernetes «rollback supported» blanket promise заменён migration-specific description плюс paired restore boundary.

### 26.2. SETUP-09: protected lifecycle control и failure matrix

**Подтверждённый drain-control defect:** start/stop/status доверяли projected `request.client`. Remote raw socket с X-Forwarded-For loopback и loopback proxy с conflicting remote hints получали **200**. Proper regressions до правки **6 failed / 4 passed**; initial harness missing reset/schema были исправлены отдельно и не засчитаны как product evidence. Теперь три routes требуют captured raw loopback, projected loopback и отсутствие nonempty forwarded identity hints. Missing capture также **403**. Reused existing predicate exported из request_locality; source resolution behavior не переписывался. Direct local preStop с global trust enabled, reversal, monotonic deadline/cancellation и unchanged state после denial **PASS**.

**Missing-assets hint:** runtime советовал bare `bun run build`, несмотря на ранее подтверждённый host Node/shebang дефект. Теперь 503 guidance разделяет source checkout (pinned Bun/frozen install/`bun --bun run build`) и reinstall/rebuild complete installed artifact. Readiness contract не расширялся assets/upstream checks.

| Стенд / этап | Actual результат |
|---|---|
| Candidate Docker health command | Docker state **healthy**, independently observed |
| Headerless direct-local drain | Ready **503** `error.type=service_unavailable`, message **Server is draining**; live **200**; stop reversible |
| Missing dashboard assets | Ready **200**, root **503** с corrected source/package hint |
| Invalid leader_election_enabled | Nonzero startup **exit1**, named validation diagnostic |
| Unavailable PostgreSQL at startup | Nonzero **exit1**, migration/connect **OperationalError**, no ready listener |
| Missing native helper on selected venv PATH | Discovery **None**, readiness **200**, actual synthetic generation completed via Python transport |
| Upstream fixture stopped after successful generation | Ready **200**, generation **502**, OpenAI envelope code **upstream_unavailable**, connect failure stage |
| Busy HTTP port, separate collision store | CLI **exit3**, **address already in use** |

Последний failure test deliberately killed только собственный synthetic upstream в контейнере. Другой python/system interpreter или raw account insert после cached startup не использованы как окончательные product probes: final helper/fallback использует selected venv и real import route. Busy-port fixture использует separate store, чтобы не спутать SQLite lifetime lock с bind failure.

Actual idle process SIGTERM на old/candidate/recreate/restore/no-assets/no-helper: **1.528–2.281s**, exit **0**, OOM false, application shutdown complete, no pool closing/reset errors. Это наблюдение данного контейнерного runtime, не универсальный supervisor exit code. Existing Linux tests отдельно доказали terminal-before-close/late admission, stuck turn bounds, cleanup cancellation/SIGINT, preStop deadline и DB-work completion/lease cleanup.

### 26.3. SETUP-10: платформы, attestations и реальные signal tests

Owning Python guide содержит dated matrix: Windows x64/Python3.13, Linux/amd64 Docker, prior Ubuntu24.04 WSL source b5aa440b, prior kind1.35 amd64/2-pod и Nix x86_64; native macOS/ARM64, WSL networking/physical LAN, cloud/ESO/Ingress/Gateway остаются unexecuted scope. Предыдущие green results не перенесены на новые платформы.

Live OCI index содержит только **linux/amd64 runtime** и **unknown/unknown attestation-manifest**; это не ARM64. `py3-none-any` packaging и flake aarch64 targets не названы runtime certification.

Пять process-signal tests прежде падали на Windows: SIGTERM termination не вызывал POSIX drain, SIGINT send_signal unsupported. Теперь они помечены POSIX-only, как два existing DB-shutdown tests. **Все семь исполнены на Linux**, не закрыты skip-ами. Cold Linux fixture imports также не укладывались в прежние 100×20ms polling; bounded monotonic **30s startup window** исправляет fixture startup, shutdown assertions/deadlines не расширены. Native discovery fixtures раньше создавали shebang-only name, не discoverable через Windows PATHEXT: corrected `.cmd` launcher сохраняет реальные discovery/protocol/close assertions; оба affected tests PASS, production helper discovery не менялась.

### 26.4. Проверки и OpenSpec

Windows focused suite: **321 passed / 7 POSIX skipped**. Linux runner с frozen dev dependencies: **17 passed**, включая эти 7 signal/DB cases и 10 repeated provenance cases. Итого **328 unique cases получили PASS хотя бы на соответствующей платформе**, 338 passed executions; Windows skips не считаются подтверждением POSIX. Existing Starlette/AnyIO deprecation warning.

Linux test runner `1b110984…` создан поверх initial source overlay `7c485240…`; final candidate `f0901e61…` дополнительно содержит новый asset error hint. Lifecycle/provenance modules health API/request_locality/server/shutdown byte hashes между runner и final candidate **совпали**; final hint отдельно прошёл Windows route test и actual final runtime probe. Dependencies взяты через `uv sync --frozen --dev --no-install-project`; ни lockfile, ни runtime dependency list не менялись.

Full Ruff/format **PASS** (1430 files), full ty **PASS**, пять architecture checks **PASS**, MkDocs strict rendered build **PASS**. Simplicity unchanged: README222/225, headings10/10, env54/60, core nav5/5, root0/0, Settings98/98. OpenSpec CI-pinned **1.11.0 strict change/main PASS**, 68 capabilities; four added requirements/seven scenarios synchronized exactly.

OpenSpec: [repair-setup-upgrade-health-platforms](openspec/changes/archive/2026-10-02-repair-setup-upgrade-health-platforms/), verified tasks/context/report archived. Reproducible regression files retained; transient runtime/manifest ledger — local Temp/codex-lifecycle-20261002/report.json, failure-report.json и public-index.json. No commit/push/merge, workflow dispatch, release/public-image mutation или production deployment.

Следующая независимая тройка: **DOC-INSTALL-01/02/03**. SETUP-04/06 physical-network/live-login evidence, public metadata/artifacts/new CI, Pages HTTPS и полный semantic registry audit остаются отдельными открытыми пунктами.

## 27. DOC-INSTALL-01 / DOC-INSTALL-02 / DOC-INSTALL-03 — fork docs, channels и shell commands — 2026-10-02

Base HEAD **`f52adb7274c96c0702e19aa02eabd4f1c7556231`**, local delta поверх сохранённых previous batches. Checkout не переключался; public metadata/artifacts не изменялись; user stores/accounts и production runtime не использовались.

### 27.1. DOC-INSTALL-01: локальные entry points и публичное расхождение

README/Chinese operational links вели на upstream docs, а English comparison содержал устаревший абсолютный **67/67**. Теперь guides указывают на tracked fork docs; comparison назван historical source claims с per-entry audit. About comments дают neutral fork description; docs home явно идентифицирует Frozen811. Upstream overview/issue/PR/contributor attribution сохранён. COMMUNITY quickstart больше не обещает assets от bare `uv run codex-lb`; использует launcher с uv/Bun1.3.14 prerequisites. TOML ошибочный `wire_specification` заменён на canonical `wire_api`, fragment связан с full client guide.

Live read-only evidence: GitHub About всё ещё говорит **production-ready / 100% verified / all156**, homepage ведёт на old v1.25.0. Latest hardened.3 release note утверждает production-ready/thoroughly verified. OCI config description повторяет 100% claim. Эти public resources локальными правками не исправлены; **DOC-INSTALL-01 остаётся открыт в public scope**.

Pages GET с default HTTPS URL дал root/getting-started/Python/Docker **200** после автоматического redirect; §28 уточнил, что конечный ресурс использует **HTTP**, а custom HTTPS отклоняется по certificate hostname mismatch. Repo/edit links ведут в Soju06, Python содержит old `<source-sha>`, Nix **404**. Initial PowerShell Invoke-WebRequest внутренне ошибся; это не было засчитано как отсутствие сайта. Python fetch сохранил HTML и выявил stale publication; получение HTML не доказывает HTTPS до конечного сайта. Новая local MkDocs build fork ownership корректна, но новая Pages deployment не выполнена.

### 27.2. DOC-INSTALL-02: URL/channel inventory и реальные packages

Inventory: **271 unique related URLs** в entry points/docs/chart; includes issues/specs/vendor references, это не 271 независимо fetched endpoint. Fork operational links направлены к tracked guides, Kubernetes chart и settings backlinks исправлены на fork. Bare `pip install codex-lb` / `uvx codex-lb` остаются explanatory upstream warnings; runnable host recommendation выбирает explicit fork package/source. Nix checkout/explicit Frozen811 SHA и tracked Helm chart не подменены придуманным release URL.

Latest release **v1.25.0-hardened.3**, опубликован 2026-09-30. Оба actual assets скачаны заново, sizes/digests совпали с GitHub API:

| Artifact | Actual bytes | SHA-256 |
| --- | ---: | --- |
| wheel | 3400777 | `4af955c73887193d9592d0baf8e638bdec80051f6df5bad8e78e663abd9ad0bf` |
| sdist | 40575939 | `24c965ff57aecead9e15b3a24159857b0c53c9307d7966bc8b4aae87cd3ce744` |

GHCR public `latest` index **`ad9aa84b…`**, amd64 runtime manifest **`31557c9d…`**, OCI revision **f622c563…**, label1.25.1; unknown/unknown is attestation. Registry/config прочитаны без запуска Docker или публикации. PyPI metadata наблюдалась как upstream codex-lb1.24.0; bare name не представлен fork package.

Historical wheel реально установлен по exact fork URL через pip в isolated Python3.13 venvs на **Windows x64** и **Ubuntu24.04 WSL x86_64**. Foreign cwd и пути с пробелами; по **два старта** каждого: readiness200, dashboard200, **17 referenced assets200/nonempty**, key hash сохранён после restart, `codex-lb-db check` **migration_policy=ok / schema_drift=none**. Actual runtime **1.25.0-beta.9**, distribution metadata **1.25.1**. Fixture environments созданы через uv venv --seed; separate `python -m venv` line не заявлена исполненной verbatim. Sdist в этом batch проверен bytes/digest, его install evidence остаётся historical§20.

`uvx --from <wheel URL> … --help` и isolated `uv tool install`/installed help **PASS на обеих OS**; tools затем uninstalled из task-specific directories. Это source/package selection + help, а product runtime проверен отдельными pip starts выше. Ни real OAuth/generation, ни current source fixes этому artifact не приписаны. **DOC-INSTALL-02 локальная ownership/channel проверка завершена**; release certification/new CI не выполнены.

### 27.3. DOC-INSTALL-03: подтверждённые shell failures и execution boundaries

Исправлено: Bash block с Windows launcher; unquoted `<source-sha>` в VCS/Git snippets; Helm placeholders `<namespace>`, `<release>`, `<fullname>`, `<your values…>`; SSO `<username>/<provider-id>` и stale `deploy/codex-lb` вместо installed StatefulSet/container; traffic-sanitization path placeholders; unexported Bash firewall/telemetry assignments. Windows update label теперь PowerShell, не Command Prompt. Docker получил отдельный PowerShell example с continuation rules. Source SHA validation и checkout failure guards предотвращают продолжение неверного выбора.

Command inventory включает **111 shell fences** (103 Bash +8 PowerShell), в том числе nested list blocks, пропущенные initial extractor. Все **bash -n / PowerShell AST parse PASS**. Parsing не выдан за successful install. **24 focused tests PASS**, в том числе ownership, named-shell separation, canonical TOML, redirection placeholders, current Helm workload kind и child environment export. Proper fenced-block test обнаружил дополнительный nested SSO placeholder, исправленный перед final PASS.

PowerShell и Bash source-selection portions из COMMUNITY_RELEASE реально fetched explicit fork full SHA и detached **f52adb72…** в отдельных temporary Git stores с пробелами, при `origin=Soju06`; origin остался upstream. Launcher/frontend часть этих blocks не запускалась. Начальный Windows runtime harness некорректно остановил wrapper; process-tree cleanup/retry завершили fixture. Initial Linux inline-argument quoting упал до uv; saved script успешно исполнил tool checks. Эти harness failures не объявлены product regressions или PASS.

Docker daemon в этом turn недоступен. Docker/Compose/Helm/Nix/nginx/cloud/supervisor/privileged recovery, Bun user installers, real clients/login и macOS/ARM64 commands заново не выполнялись. Previous runtime evidence§18–26 сохраняет собственные snapshots; новым examples не присвоен новый infrastructure PASS. **DOC-INSTALL-03 остаётся открыт для полного per-command runtime coverage**. Stable [command inventory](openspec/changes/archive/2026-10-02-repair-fork-installation-documentation/command-inventory.md) фиксирует каждый block/hash и S/G/P/H evidence category.

### 27.4. Валидация и итог

**24 focused tests PASS**; targeted Ruff check/format и ty **PASS**; strict MkDocs **PASS**; **75 entry-point fork guide links /24 rendered anchors PASS**. Simplicity **README218/225, headings10/10, env54/60, nav5/5, root0/0**. No new env/settings/dependency/migration/UI surface. Existing AnyIO/Starlette deprecation warning.

OpenSpec [repair-fork-installation-documentation](openspec/changes/archive/2026-10-02-repair-fork-installation-documentation/): user-documentation, **2 added requirements /1 modified**, preserving existing README scenarios and adding stale-site fallback. Requirements/context synchronized; CI-pinned1.11.0 strict change/main validation completed before verified local archive. Detailed [verification](openspec/changes/archive/2026-10-02-repair-fork-installation-documentation/verification.md) identifies public and execution residuals. Disposable scripts/reports: local Temp/codex-doc-install-20261002; fixture runtime stores/tools removed. No commit/push/merge/dispatch/release/deployment.

Next independent trio: **DOC-INSTALL-04/05/06**. DOC-INSTALL-01 public metadata/Pages correction, DOC-INSTALL-03 complete infrastructure command execution, SETUP-04/06 physical-network/live-login and full semantic registry audit remain explicitly open.

## 28. Сверка всех выполненных исправлений и dirty checkout — 2026-10-02

### 28.1. Что означало «есть незакоммиченные исправления»

Это Git state, а не отсутствие учёта. До этой сверки **шесть** local batches уже
описаны в §§22–27 и archived OpenSpec; **40/40** их implementation/verification
пунктов отмечены `[x]`. Свежий `git status --porcelain -uall` на HEAD
**`f52adb7274c96c0702e19aa02eabd4f1c7556231`** содержит **136 файлов**:
**75 modified tracked +61 untracked**, включая48 files внутри шести архивов.
Untracked OpenSpec/test/config file может иметь полное evidence, но ещё не
входить в Git-коммит. Ни один из136 paths не оставлен без mapping ниже.

Реальный пробел был в summary: §4 всё ещё объявлял большинство областей
«НЕ ПРОВЕРЕНО», source-integrated fixes были названы только local, а новые
SETUP defects имели описание в журнале, но не отдельный F-ID. Теперь:

- Все **34** delivery/governance rows имеют отдельный актуальный статус,
  completed scope и остаток; исходные критерии проверки сохранены.
- Source fixes отделены от uncommitted delta; partial/public/cloud status
  не скрыт. F-038–F-044 — **новые номера уже описанных исправлений**, не
  семь новых code changes в этом turn.
- DOC-INSTALL-06 локально отмечен `[x]` по уже имеющемуся OpenSpec evidence;
  DOC-INSTALL-01/03/04/05 сохраняют явный открытый остаток.
- Related original cards UP-ISSUE-2274, UP-ISSUE-2535, UP-PR-2536/2502/2507
  обновлены только в independent-evidence колонке, с bounded/partial scope;
  исходные author claims не переписаны. Остальные imported claims не закрыты
  на основании adjacent installation tests.
- INC-03-OWNER/INC-07-PATCH получили fixing source SHAs; INC-01/08/10,
  весь five-fix bundle и неподтверждённые авторские broad commits остаются
  отдельно. Commit queue c7ca9558/deed76ba/7ec39f82 уточнена по выполненной части.

### 28.2. Исправления, которые уже находятся в Git history

Live local `git merge-base --is-ancestor <sha> HEAD` подтвердил ancestry всех
ниже перечисленных fixing/integration commits. Это локальная проверка Git
history; GitHub refs и старые CI checks заново не опрашивались. Исторические
exact-source PR/cloud результаты остаются в §§20.5/21 и не становятся cloud
проверкой current dirty tree.

| Source commit / merge | Выполненная часть | Evidence |
| --- | --- | --- |
| 165240e3 | Style-only alignment, AST unchanged | §20.4 |
| 7d151b9e → f847fc57 | Continuity snapshots/scope/WS Pause, quarantine fixture, proxy boundaries | F-001–005/009/012; §§13/14/17/20/21; last quarantine path commit также7d151b9e |
| 9c797af3 → 245152d7 | Exact-source release gate, managed parity/Windows automation | F-006/008/013; §§16/17/20/21; current Helm parity имеет дополнительный dirty delta §22 |
| 5b72137f → bff1bd56 | Docker contexts/targets/dev/prod source/DB probes | F-015–020; §§18/19/20/21 |
| 43959260 /4dce7220 → 8a2b706e | Source dashboard build hook, nested sdist exclusions/editable exception | F-014/022/023/024; §§20/21 |
| 742fc58d | Checkout launchers/cwd/exit/assets | F-025/026; §21 |
| 17d13a48 /f61669d6 | Declared Nix build helpers and pinned Bun runtime | F-027/029; §21 |

F-028 fixture integration также находится в этой ancestry (a5b4e403/feadca30
вошли в verified proxy source/merge chain); historical route/PR evidence §21.
Новые commits/push/merge/release этой сверкой не выполнялись.

### 28.3. Шесть незакоммиченных batches уже имеют описание и проверки

| Раздел | OpenSpec archive | Tasks | Локально завершено | Открытая граница |
| --- | --- | ---: | --- | --- |
| §22 | repair-alternative-installation-paths | 7/7 | INSTALL-12/13/14, F-030–034; Helm/Nix/nginx | ARM64/Darwin/ESO/Ingress/Gateway/live OAuth/new cloud |
| §23 | repair-audit-and-ci-evidence | 7/7 | F-007/035/036, CI-02, REL-03; count/CI/owner gates | Full semantic claims audit/public metadata/Pages F-037 |
| §24 | repair-setup-configuration-data-network | 7/7 | SETUP-02/03/local04, F-038; env/process/paired data | Physical network/older binaries; current SQLite flake F-045 |
| §25 | repair-setup-transport-auth-client | 6/6 | SETUP-05/local06/07, F-039/040; proxy/auth/callback/client | Real OpenAI login/entitlement/Desktop/physical network |
| §26 | repair-setup-upgrade-health-platforms | 5/5 | SETUP-08/09/10, F-041/042/043; rollback/control/platform | New public artifact/full-build/all platforms/new cloud |
| §27 | repair-fork-installation-documentation | 8/8 | DOC-INSTALL-02, local01/03, F-044; links/shell/package proof | Public metadata/Pages and full per-command execution |

All six verification reports inspected; required files present. Their delta
specs retain **24 requirement names /52 scenario names** in current main specs.
Those counts include repeated capabilities/modified requirements across batches;
they are not24 newly introduced global capabilities. Current strict validation
covers68 capabilities. Archive task completion does not close the last column.

### 28.4. Свежая проверка этого working tree и обнаруженные остатки

17 relevant test files covering actual modified CLI/env/CI/auth/OAuth/drain/
helper/docs/process paths: **321 passed /95 skipped /1 failed** on Windows.
Все95 skips — Helm rendering tests (helm отсутствует на PATH), не runtime PASS.
Ещё четыре modified proxy-env fixture cases: **4 passed /59 deselected**.
Недопущенные/невыбранные случаи не выданы за новое verification evidence.

Failure **F-045**: `test_cli_sqlite_restart_and_paired_restore` упал на
synthetic account INSERT после остановки first CLI process с SQLite
**disk I/O error**. Отдельный повтор exact test дал **1 passed**, без правки
кода. Это inconsistent result; причина/order/Windows filesystem/process
interaction ещё не установлены. Aggregate run не назван green, failure не
скрыт пересчётом successful executions. Отдельный process test PASS сохраняет
isolated evidence, но стабильность/full-suite coverage остаётся открытой CI-04.
User DB/store не использовались, production corruption не доказана.

F-037 уточнён собственным redirect-disabled read-only HTTPS probe:
`https://frozen811.github.io/codex-lb/` → **301**
`http://extr3me.me/codex-lb/` → **200**. Direct
`https://extr3me.me/codex-lb/` → **CERTIFICATE_VERIFY_FAILED, hostname mismatch**.
Поэтому §27 observation HTML200 не считается end-to-end HTTPS success.
Это fresh diagnosis, не изменение account settings/certificate/publication.

Strict MkDocs build **PASS**; OpenSpec1.11.0 **68 main specs PASS**.
Simplicity **README218/225, headings10/10, env54/60, nav5/5, root0/0 PASS**.
Registry checks: **136 paths mapped,135 other files unchanged,45 unique F-IDs,
34 correctly structured queue rows,0 missing local link targets**. Все original
criteria сохранены; F-028 a5b4e403/feadca30 ancestry также подтверждена. Historical
Helm120/Linux signal17/Nix/Docker runtime records сохранены как scoped dated
results; в этом turn инфраструктурные стенды не перезапускались, source tree
не менялся ради проверки и real credentials не читались.

### 28.5. Полное соответствие dirty/untracked paths

Snapshot перед reconciliation:75 MOD +61 NEW =136. Для каждого пути указан
пакет, ID или описание правки и существующий evidence раздел. Mapping основан
на actual diff и verified reports, не на одном совпадении имени файла. Прямые
code deltas в app состоят из семи файлов; infrastructure/docs/spec/test
изменения соответствуют тем же шести batches. Полные byte hashes snapshot и
machine-readable mapping сохранены task-locally в
Temp/codex-registry-reconciliation-20261002/before.json и file-map.json.

| Path | Git | Пакет / раздел | Что учтено |
| --- | --- | --- | --- |
| `.env.example` | MOD | §24 | SETUP-02: mode/precedence guidance |
| `.gitattributes` | MOD | §22/23 | F-033: Nix LF; CI-02 detection input |
| `.github/scripts/detect_changed_areas.py` | MOD | §23 | F-035/CI-02: complete change evidence |
| `.github/workflows/docs.yml` | MOD | §23 | F-036/REL-03: Pages metadata and fork owner |
| `.github/workflows/release.yml` | MOD | §23 | F-036/REL-03: upstream cleanup guard |
| `COMMUNITY_RELEASE.md` | MOD | §22/23/26/27 | Fork channels/claims/source update/shell examples |
| `ISSUES.md` | MOD | §23 | F-007: historical source claims and count semantics |
| `Makefile` | MOD | §22 | F-030: explicit fork smoke image |
| `README.md` | MOD | §22/23/27 | Fork install provenance, claims and source guide links |
| `README.zh-CN.md` | MOD | §22/23/27 | Translated entry-point ownership/shell guidance |
| `app/cli.py` | MOD | §24 | F-038: nonnegative keep-alive validation |
| `app/core/auth/dashboard_mode.py` | MOD | §25 | F-039: raw socket proxy authority |
| `app/core/middleware/dashboard_auth_proxy.py` | MOD | §25 | F-039: header sanitizer socket authority |
| `app/core/request_locality.py` | MOD | §26 | F-041: reuse exported forwarded-hint predicate |
| `app/main.py` | MOD | §26 | F-042: missing-assets recovery hint |
| `app/modules/health/api.py` | MOD | §26 | F-041: protected drain start/stop/status |
| `app/modules/oauth/service.py` | MOD | §25 | F-040: callback setup cleanup and safe warning |
| `deploy/helm/codex-lb/Chart.yaml` | MOD | §22 | F-030/031/032: fork chart values/metadata/job/secret/cache config |
| `deploy/helm/codex-lb/README.md` | MOD | §22/26/27 | F-030/031/032; migration/rollback and shell placeholders |
| `deploy/helm/codex-lb/templates/_helpers.tpl` | MOD | §22 | F-030/031/032: fork chart values/metadata/job/secret/cache config |
| `deploy/helm/codex-lb/templates/configmap.yaml` | MOD | §22 | F-030/031/032: fork chart values/metadata/job/secret/cache config |
| `deploy/helm/codex-lb/templates/hooks/migration-job.yaml` | MOD | §22 | F-030/031/032: fork chart values/metadata/job/secret/cache config |
| `deploy/helm/codex-lb/values.yaml` | MOD | §22 | F-030/031/032: fork chart values/metadata/job/secret/cache config |
| `docs/api-keys.md` | MOD | §23 | F-036/DOC-03: fork owning-spec backlinks |
| `docs/authentication.md` | MOD | §23/25 | Fork backlink and trusted-header auth provenance |
| `docs/client-setup.md` | MOD | §23/25/27 | Fork backlink, API-key/client endpoint/config examples |
| `docs/configuration.md` | MOD | §23/24 | Fork backlink, mode-specific env discovery/precedence |
| `docs/conversations.md` | MOD | §23 | F-036/DOC-03: fork owning-spec backlinks |
| `docs/database.md` | MOD | §23/24 | Fork backlink, paired backup/restore boundaries |
| `docs/deployment/docker.md` | MOD | §22/23/24/26/27 | Install channel, storage, update identity/rollback, PowerShell |
| `docs/deployment/kubernetes.md` | MOD | §22/23/26/27 | Migration/install/rollback/source links and Bash prerequisite |
| `docs/deployment/python.md` | MOD | §22/26/27 | Source/package/platform/update channels and named shells |
| `docs/deployment/remote.md` | MOD | §22/24/25/27 | Endpoint/proxy/TLS/trust/export guidance |
| `docs/examples/codex/config.toml` | MOD | §25 | SETUP-07: usage/catalog/provider URL contract |
| `docs/getting-started.md` | MOD | §22/25/27 | Source channels, callback/auth setup and shell guidance |
| `docs/index.md` | MOD | §23/27 | Fork ownership/spec backlinks/English docs identity |
| `docs/live-voice.md` | MOD | §23 | F-036/DOC-03: fork owning-spec backlinks |
| `docs/metrics.md` | MOD | §23 | F-036/DOC-03: fork owning-spec backlinks |
| `docs/reference/settings.md` | MOD | §23 | F-036/DOC-03: fork owning-spec backlinks |
| `docs/routing.md` | MOD | §23 | F-036/DOC-03: fork owning-spec backlinks |
| `docs/rust-architecture.md` | MOD | §23 | F-036/DOC-03: fork owning-spec backlinks |
| `docs/sso.md` | MOD | §23/27 | Fork backlink; F-044 current Helm workload and safe placeholders |
| `docs/telemetry.md` | MOD | §23/27 | Fork backlink; F-044 Bash export |
| `docs/traffic-parity.md` | MOD | §23/27 | Fork backlinks and quoted capture paths/placeholders |
| `docs/troubleshooting.md` | MOD | §23/24/25/26 | Fork backlink; distinct startup/product/auth failure stages |
| `docs/usage-reporting.md` | MOD | §23 | F-036/DOC-03: fork owning-spec backlinks |
| `flake.nix` | MOD | §22 | F-030/033: fork metadata, copyfile immutable-store install |
| `issues-check.md` | MOD | §22–28 | Registry evidence/status/coverage reconciliation |
| `mkdocs.yml` | MOD | §22/23 | Nix navigation and fork site/edit metadata |
| `openspec/specs/admin-auth/context.md` | MOD | §25 | F-039/SETUP-06 raw peer identity contract/context |
| `openspec/specs/admin-auth/spec.md` | MOD | §25 | F-039/SETUP-06 raw peer identity contract/context |
| `openspec/specs/deployment-installation/context.md` | MOD | §22/24/26 | Install ordering, env/data/rollback/platform requirements/context |
| `openspec/specs/deployment-installation/spec.md` | MOD | §22/24/26 | Install ordering, env/data/rollback/platform requirements/context |
| `openspec/specs/deployment-networking/context.md` | MOD | §22/24/25 | Proxy transport/endpoint/trust/TLS requirements/context |
| `openspec/specs/deployment-networking/spec.md` | MOD | §22/24/25 | Proxy transport/endpoint/trust/TLS requirements/context |
| `openspec/specs/github-automation/context.md` | MOD | §23 | F-035/CI-02 complete-change selection requirements/context |
| `openspec/specs/github-automation/spec.md` | MOD | §23 | F-035/CI-02 complete-change selection requirements/context |
| `openspec/specs/graceful-shutdown/spec.md` | MOD | §26 | F-041/SETUP-09 direct-local drain requirements/context |
| `openspec/specs/oauth-callback-privacy/spec.md` | MOD | §25 | F-040 bind/cancel/privacy requirements/context |
| `openspec/specs/release-management/context.md` | MOD | §23 | F-036 upstream cleanup scope requirements/context |
| `openspec/specs/release-management/spec.md` | MOD | §23 | F-036 upstream cleanup scope requirements/context |
| `openspec/specs/user-documentation/context.md` | MOD | §23/25/26/27 | Ownership/claims/client/platform/shell contracts/context |
| `openspec/specs/user-documentation/spec.md` | MOD | §23/25/26/27 | Ownership/claims/client/platform/shell contracts/context |
| `scripts/generate_settings_reference.py` | MOD | §23 | F-036: preserve generated fork spec links |
| `scripts/helm-kind-smoke.sh` | MOD | §22 | F-030/031: fork image and fresh external DB install case |
| `tests/integration/test_graceful_websocket_process_shutdown.py` | MOD | §26 | F-043: POSIX signal scope and bounded startup readiness |
| `tests/integration/test_oauth_flow.py` | MOD | §25 | F-040: occupied callback/pending/manual recovery route |
| `tests/unit/test_cli.py` | MOD | §24 | F-038: negative/zero CLI/env keep-alive cases |
| `tests/unit/test_github_ci_scripts.py` | MOD | §23 | F-035: detector CLI output regressions |
| `tests/unit/test_health_probes.py` | MOD | §26 | F-041: captured local/internal control units |
| `tests/unit/test_helm_external_secrets.py` | MOD | §22 | F-031/032: empty DB install modes/secret/scratch rendering |
| `tests/unit/test_helm_replica_artifacts.py` | MOD | §22 | F-030: consistent fork smoke image and replica artifacts |
| `tests/unit/test_native_egress.py` | MOD | §26 | F-043: Windows discoverable helper fixtures |
| `tests/unit/test_proxy_websocket_client.py` | MOD | §25 | Windows env case aliases fixture order; 4 fresh cases PASS |
| `tests/unit/test_settings_env_files.py` | MOD | §24 | SETUP-02: env discovery/relative/ordered process precedence |
| `deploy/nginx.conf` | NEW | §22/25 | F-034/SETUP-05: shipped proxy transport config |
| `docs/deployment/nix.md` | NEW | §22/26/27 | Fork flake/runtime/platform/update/Bash guide |
| `openspec/changes/archive/2026-10-02-repair-alternative-installation-paths/.openspec.yaml` | NEW | §22 | INSTALL-12/13/14; F-030–034; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-alternative-installation-paths/context.md` | NEW | §22 | INSTALL-12/13/14; F-030–034; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-alternative-installation-paths/design.md` | NEW | §22 | INSTALL-12/13/14; F-030–034; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-alternative-installation-paths/proposal.md` | NEW | §22 | INSTALL-12/13/14; F-030–034; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-alternative-installation-paths/specs/deployment-installation/spec.md` | NEW | §22 | INSTALL-12/13/14; F-030–034; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-alternative-installation-paths/specs/deployment-networking/spec.md` | NEW | §22 | INSTALL-12/13/14; F-030–034; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-alternative-installation-paths/tasks.md` | NEW | §22 | INSTALL-12/13/14; F-030–034; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-alternative-installation-paths/verification.md` | NEW | §22 | INSTALL-12/13/14; F-030–034; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-audit-and-ci-evidence/.openspec.yaml` | NEW | §23 | F-007/035/036; CI-02/REL-03; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-audit-and-ci-evidence/design.md` | NEW | §23 | F-007/035/036; CI-02/REL-03; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-audit-and-ci-evidence/proposal.md` | NEW | §23 | F-007/035/036; CI-02/REL-03; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-audit-and-ci-evidence/specs/github-automation/spec.md` | NEW | §23 | F-007/035/036; CI-02/REL-03; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-audit-and-ci-evidence/specs/release-management/spec.md` | NEW | §23 | F-007/035/036; CI-02/REL-03; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-audit-and-ci-evidence/specs/user-documentation/spec.md` | NEW | §23 | F-007/035/036; CI-02/REL-03; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-audit-and-ci-evidence/tasks.md` | NEW | §23 | F-007/035/036; CI-02/REL-03; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-audit-and-ci-evidence/verification.md` | NEW | §23 | F-007/035/036; CI-02/REL-03; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-fork-installation-documentation/.openspec.yaml` | NEW | §27 | DOC-INSTALL-01/02/03; F-044; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-fork-installation-documentation/command-inventory.md` | NEW | §27 | DOC-INSTALL-01/02/03; F-044; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-fork-installation-documentation/context.md` | NEW | §27 | DOC-INSTALL-01/02/03; F-044; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-fork-installation-documentation/design.md` | NEW | §27 | DOC-INSTALL-01/02/03; F-044; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-fork-installation-documentation/proposal.md` | NEW | §27 | DOC-INSTALL-01/02/03; F-044; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-fork-installation-documentation/specs/user-documentation/spec.md` | NEW | §27 | DOC-INSTALL-01/02/03; F-044; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-fork-installation-documentation/tasks.md` | NEW | §27 | DOC-INSTALL-01/02/03; F-044; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-fork-installation-documentation/verification.md` | NEW | §27 | DOC-INSTALL-01/02/03; F-044; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-configuration-data-network/.openspec.yaml` | NEW | §24 | SETUP-02/03/04; F-038; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-configuration-data-network/design.md` | NEW | §24 | SETUP-02/03/04; F-038; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-configuration-data-network/proposal.md` | NEW | §24 | SETUP-02/03/04; F-038; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-configuration-data-network/specs/deployment-installation/spec.md` | NEW | §24 | SETUP-02/03/04; F-038; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-configuration-data-network/specs/deployment-networking/spec.md` | NEW | §24 | SETUP-02/03/04; F-038; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-configuration-data-network/tasks.md` | NEW | §24 | SETUP-02/03/04; F-038; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-configuration-data-network/verification.md` | NEW | §24 | SETUP-02/03/04; F-038; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-transport-auth-client/.openspec.yaml` | NEW | §25 | SETUP-05/06/07; F-039/040; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-transport-auth-client/design.md` | NEW | §25 | SETUP-05/06/07; F-039/040; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-transport-auth-client/proposal.md` | NEW | §25 | SETUP-05/06/07; F-039/040; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-transport-auth-client/specs/admin-auth/spec.md` | NEW | §25 | SETUP-05/06/07; F-039/040; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-transport-auth-client/specs/deployment-networking/spec.md` | NEW | §25 | SETUP-05/06/07; F-039/040; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-transport-auth-client/specs/oauth-callback-privacy/spec.md` | NEW | §25 | SETUP-05/06/07; F-039/040; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-transport-auth-client/specs/user-documentation/spec.md` | NEW | §25 | SETUP-05/06/07; F-039/040; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-transport-auth-client/tasks.md` | NEW | §25 | SETUP-05/06/07; F-039/040; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-transport-auth-client/verification.md` | NEW | §25 | SETUP-05/06/07; F-039/040; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-upgrade-health-platforms/.openspec.yaml` | NEW | §26 | SETUP-08/09/10; F-041/042/043; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-upgrade-health-platforms/design.md` | NEW | §26 | SETUP-08/09/10; F-041/042/043; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-upgrade-health-platforms/proposal.md` | NEW | §26 | SETUP-08/09/10; F-041/042/043; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-upgrade-health-platforms/specs/deployment-installation/spec.md` | NEW | §26 | SETUP-08/09/10; F-041/042/043; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-upgrade-health-platforms/specs/graceful-shutdown/spec.md` | NEW | §26 | SETUP-08/09/10; F-041/042/043; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-upgrade-health-platforms/specs/user-documentation/spec.md` | NEW | §26 | SETUP-08/09/10; F-041/042/043; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-upgrade-health-platforms/tasks.md` | NEW | §26 | SETUP-08/09/10; F-041/042/043; archived plan/spec/verification artifact |
| `openspec/changes/archive/2026-10-02-repair-setup-upgrade-health-platforms/verification.md` | NEW | §26 | SETUP-08/09/10; F-041/042/043; archived plan/spec/verification artifact |
| `openspec/specs/graceful-shutdown/context.md` | NEW | §26 | F-041/SETUP-09 direct-local drain requirements/context |
| `openspec/specs/oauth-callback-privacy/context.md` | NEW | §25 | F-040 bind/cancel/privacy requirements/context |
| `tests/integration/test_internal_drain_provenance.py` | NEW | §26 | F-041: raw-peer/hint control routes and unchanged denial state |
| `tests/integration/test_setup_auth_paths.py` | NEW | §25 | F-039: actual trusted-header routes and audit actor |
| `tests/integration/test_setup_health_messages.py` | NEW | §26 | F-042: ready200/root503 actionable hint |
| `tests/integration/test_setup_process.py` | NEW | §24/28 | SETUP-02/03 process/pair tests; F-045 aggregate fail isolated PASS |
| `tests/unit/test_client_setup_examples.py` | NEW | §25 | SETUP-07: TOML/suffix/conflict-marker regression |
| `tests/unit/test_fork_automation_scope.py` | NEW | §23 | F-036: fork docs/release owner guards |
| `tests/unit/test_installation_documentation.py` | NEW | §27 | F-044: operational links/named shells/TOML/placeholders/exports |
| `tests/unit/test_oauth_callback_startup.py` | NEW | §25 | F-040: failed/cancelled callback startup cleanup |
| `tests/unit/test_setup_update_guidance.py` | NEW | §26 | SETUP-08/10: explicit fork update/rollback/platform matrix |

### 28.6. Итог и последующие задачи

Все существующие local/source исправления имеют отметку и ссылку на evidence;
неописанных dirty/untracked paths: **0/136**. Только `issues-check.md` изменён
этой reconciliation; hashes остальных135 файлов проверены неизменными. Новых
source/OpenSpec code changes, commit/push/publication/deployment не выполнялось.
Это обновление учёта существующих batches, не новый implementation batch.

Открытые задачи сохраняются: F-010/013/014 public artifacts, F-007 full semantic
claims audit, F-037 public Pages/TLS, F-045 Windows test stability, SETUP-01
all-command clean-stand execution, SETUP-04 physical network, SETUP-06 live login,
DOC-INSTALL-01/03/04/05 residuals, IMG-08 scan/exclusions, DOC-07 full credits,
current-delta cloud/PR gates и original unverified source claims/incidents.
Прежняя рекомендация брать DOC-INSTALL-04/05/06 теперь историческая:
06 уже локально выполнен. Следующую тройку нужно выбирать из фактически
незавершённых IDs, учитывая отмеченные local результаты и открытые остатки.

## 29. UP-ISSUE-2356 / UP-ISSUE-2128 / UP-ISSUE-2038 — native client compatibility — 2026-10-02

Взяты ровно три ранее независимо непроверенных пункта. Base HEAD:
`f52adb7274c96c0702e19aa02eabd4f1c7556231`; изменения локальные поверх существующего
dirty checkout. Исправляющего SHA, commit/push/publication этого пакета нет.

### 29.1. History/notes v2 — UP-ISSUE-2356

Существующие маршруты подтверждены для всех 10 POST operations и всех 6 GET
notes operations: три ingress prefixes × обе slash-формы = **96 variants**.
Дополнительно **18 unknown-operation variants** возвращают 404 `not_found`.
Проверены точные POST body bytes, повторяющиеся query values и allowed synthetic
encryption headers, API-key admission/account scope, existing thread affinity,
unavailable upstream и шесть child placement/fallback cases. При preference
`always` новый child выбирает другой доступный account; при единственном
account допускается parent; повтор child сохраняет собственную affinity.
Новый runtime defect этому пункту не приписан; закрыт local route/transport
evidence gap. Hosted encryption/decryption и cross-account history recovery
не объявлены доказанными.

### 29.2. Standalone search — UP-ISSUE-2128 / F-046

`POST .../alpha/search/` на canonical, `/v1` и doubled-prefix paths попадал
в catch-all и возвращал **405**. Добавлены две hidden slash registrations на
существующий handler. Все три alias/slash пары проходят actual account selection;
body bytes/repeated query и JSON ответ сохраняются. Existing case-insensitive
Content-Type replacement подтверждена для JSON/SDP и трёх spelling variants;
bodyless removal также проходит. Media-type runtime заново не переписывался.

### 29.3. Individual models — UP-ISSUE-2038 / F-047

`GET /v1/models/gpt-5.2/` и `GET /v1/models/vendor/model/` возвращали **404**,
хотя модели были видимы в list catalog. Slash route теперь зарегистрирован
перед greedy ID route: delimiter убран маршрутизацией, internal slash сохранён.
Проверены catalog field parity кроме independently generated `created`,
unknown/hidden `model_not_found`, auth, independent allowlist/source scopes,
оба вместе и reservation cleanup после catalog failure. Visual Studio UI
registration не выполнялась.

### 29.4. Проверки и закрытие

До runtime fix десять regressions дали **5 failed / 5 passed**: три search405
и два model404. Финальные непересекающиеся наборы: **229 integration passed**,
**15 search/control transport passed**, **16 docs checks passed** — всего
**260 passed**. Baseline/retry runs не прибавлены повторно.

Шесть tests используют настоящий loopback HTTP upstream с gzip response:
public route → account selection → real Python control client → response
adapter. Nonempty JSON декодируется, exact bytes/query и single Content-Type
сохранены, Content-Encoding/Set-Cookie не просачиваются в downstream.

Ruff check/format, proxy architecture, simplicity budgets, strict MkDocs,
OpenSpec1.11.0 strict change и **68/68 main specs** — PASS. Второй review проход
сверил route order, list visibility и каждое normative обещание с tests;
opaque body guarantee уточнена до POST, GET не синтезирует body. Отдельного
reviewer agent не использовали. Три requirement blocks синхронизированы точно.

Каждая из трёх исходных registry rows и сводные F-046/F-047 обновлены.
Пакет [repair-native-client-compatibility](openspec/changes/archive/2026-10-02-repair-native-client-compatibility/)
проверен; [verification evidence](openspec/changes/archive/2026-10-02-repair-native-client-compatibility/verification.md).
Public release/image/helper parity, hosted traffic и cloud/current-delta gates
сохраняют отдельный открытый scope. Остальные registry tasks этим пакетом
не закрывались.

## 30. INC-04-FANOUT / INC-05-SIGNING / INC-06-RESET — 2026-10-02

Пакет содержит ровно три исходные задачи из §10.2. Предыдущие dirty изменения сохранены; исходные helper-only проверки дополнены внешними HTTP routes, реальными API-key reservations/DB quota и signed sender/receiver settings.

### 30.1. Fan-out: red-before и исправление

Новые generations/edits tests до правки дали **6 failed, 6 passed**: cancellation после успешного subcall освобождала reservation и теряла расход; failure model-log rewrite срывал settlement; unexpected exception выдавался клиенту текстом. Теперь все children принадлежат service scheduler, cancellation cancels/drains pending children, completed image-tool usage передаётся единственному settlement owner до log rewriting, raw exception скрывается. Повторная отмена в child cleanup, settlement handoff и release не прерывает обязательную очистку. **20 route cases** проверяют один settlement/release, finalized/released DB rows, actual quota и cached input tokens.

### 30.2. Подпись и reset-credit

Подпись уже использовала configured key; **10 cases** на production header builder/parser подтвердили env precedence, разные/отсутствующие/invalid files без file mutation, shared file-only key, mismatch refusal и обе primary signature версии. Sender/receiver используют независимо перезагруженные settings.

Missing-target reset refusal также присутствовал. **36 authenticated HTTP cases** охватывают canonical `/api/codex`, backend WHAM/Codex, slash/no slash, explicit/default/auto и NULL/empty target ID: 401 `invalid_api_key`/`authentication_error`, no upstream consume, post-redemption refresh или snapshot mutation. Valid cross-account consume отдельно проверяет distinct target token, ChatGPT account ID, original redeem ID и refresh обоих аккаунтов. Token reservation на этих ChatGPT consume routes отсутствует; settlement означает сохранение credit snapshot при refusal.

### 30.3. Проверки и статус

Общий targeted прогон: **241 passed**; последующие усиленные cached-token assertions: **20 passed**, distinct target token: **1 passed**. Ruff check/format, targeted ty, proxy architecture, cancellation safety, timing seams и strict OpenSpec change — PASS. После archive проверено точное соответствие трёх normative blocks и strict main specs: **68 passed, 0 failed**. Совместимость сверена с каждым delta scenario; контракт не ослаблялся под mocks. Единственное pytest warning — existing Starlette deprecation.

Три задачи в собственных registry rows отмечены локально закрытыми, сводная строка five-fix commit согласована. Capability specs/context синхронизированы; verified change [repair-fanout-signing-reset-credit](openspec/changes/archive/2026-10-02-repair-fanout-signing-reset-credit/) и [verification](openspec/changes/archive/2026-10-02-repair-fanout-signing-reset-credit/verification.md).

Public packages/images, deployed multi-replica infrastructure, cloud CI, real upstream image generation/redemption сохраняют отдельный непроверенный scope. INC-02-OAUTH и исторические routing/quota incidents этим пакетом не закрыты. Коммит, push, release и deployment не выполнялись.

## 31. UP-PR-2540 / UP-PR-2541 / UP-PR-2545 — clock, SCIM, cache admission — 2026-10-02

Взяты ровно три независимо непроверенные registry rows. Base HEAD:
`f52adb7274c96c0702e19aa02eabd4f1c7556231`; предыдущий dirty checkout сохранён.
Результат: две дополнительные runtime-регрессии исправлены, существующий cache
fix подтверждён внешним operator path; все три задачи локально закрыты.

### 31.1. Clock times — UP-PR-2540 / F-048

Strict invalid-write rejection уже работал. Однако read response schema
отвергала исторические `9:00`, `bad`, пустую строку и trailing newline: GET
settings возвращал 500, оператор не мог исправлять поля по одному. Read schema
теперь возвращает исходные строки; request pattern не ослаблен. Пять legacy
variants проверены через GET settings/forecast, omitted/null updates, start-only
и end-only correction и настоящие persisted values. Невалидные новые значения
в обоих полях возвращают 422 без сохранения companion setting.

### 31.2. SCIM — UP-PR-2541 / F-049

Actual streamed 64 KiB bound существовал. Declared-length precheck использовала
`isdigit()` + `int()` и падала на длинных decimal headers и Latin-1 superscript
digit; malformed lengths читали body. ASCII decimal syntax и сравнение
zero-stripped строк устраняют crash без произвольного integer parsing.
SCIM400/413 проверены без body receive и DB writes. POST/PUT/PATCH × absent/false
length прерывают stream на первом crossing chunk, не читают tail и сохраняют
existing resource. Валидный fragmented body ровно64KiB проходит все три метода
как с обычной длиной, так и с5000 leading zeroes.

### 31.3. Cache — UP-PR-2545

Новый production defect не найден. Через настоящий Pause API воспроизведены
locked write, driver failure и cancellation после committed status change.
Local routing блокируется сразу, namespace остаётся pending, реальный retry
пишет version, отдельный DB-backed peer cache обновляется и stale ACTIVE bridge
snapshot больше не используется. Existing cancellation/backoff, interrupted
commit, in-flight marker и namespace isolation tests также прошли.
Source-process loss остаётся границей in-memory queue/TTL backstop.

### 31.4. Проверки и закрытие

Red-before новые planner/SCIM cases: **13 failed / 4 passed**; green-after
selected scope: **26 passed**. Финальная scoped suite: **225 passed, 1 skipped**
(existing Windows `tzset` limitation), одно existing Starlette warning. Эти
прогоны не складывались в общий счётчик. Ruff check/format, targeted ty,
architecture/cancellation/timing/simplicity checks, strict change и **68/68
main specs** — PASS. Второй source/scenario review выполнен без отдельного
reviewer agent; все восемь delta scenarios сопоставлены с tests.

Три исходные registry rows обновлены вместе со сводными F-048/F-049.
Verified change [verify-planner-scim-cache-admission](openspec/changes/archive/2026-10-02-verify-planner-scim-cache-admission/),
[verification evidence](openspec/changes/archive/2026-10-02-verify-planner-scim-cache-admission/verification.md).
Specs/context синхронизированы. Cloud/current-delta CI, public artifacts,
deployed replicas, live IdP и MySQL/PostgreSQL runtime отдельно не проверялись.
Другие tasks не закрывались; commit/push/release/deployment не выполнялись.

## 32. UP-PR-2530 / UP-PR-2531 / UP-PR-2539 — JSON, Lite и size errors — 2026-10-02

Пакет содержит ровно три исходные registry задачи. База:
`f52adb7274c96c0702e19aa02eabd4f1c7556231`; предыдущие незакоммиченные
изменения сохранены. Для UP-PR-2530/2531 production fixes уже присутствовали;
расширена независимая проверка, новый дефект там не заявляется.

### 32.1. UP-PR-2530 — полные WebSocket JSON документы

Compact/pretty/CRLF ошибки, metadata-first и interpreted native payload проходят
реальные HTTP routes без misleading timeout/replay. Lifecycle и output_item.done
для message/function_call сохраняют Unicode, escaped newline и весь terminal
output. Подтверждено, что output_item.done заново сериализуется после возможного
duplicate-tool rewrite; отдельная production правка этой ветки не требовалась.
Реальный локальный aiohttp WebSocket проверяет LF/CRLF на байтовом пути.

### 32.2. UP-PR-2531 — финальный Lite payload

Три bridge ingress × Lite/non-Lite × omitted/null/true/false; проверены outgoing
parallel_tool_calls, input/cache identity, reasoning и marker. Дополнительно
реальный HTTP сервер принимает direct POST либо GET426→POST fallback: все16
сочетаний подтверждают parallel_tool_calls=false и trusted Lite header.
Non-Lite сохраняет свой transport serialization; untrusted client header/marker
не создаёт Lite trust. Existing source finalizer исправен.

### 32.3. UP-PR-2539 / F-050 — потерянный aiohttp код1009

aiohttp ERROR(WebSocketError(1009)) терял close_code в адаптере. До правки
регрессии дали **7 failed / 9 passed**: до response.created происходил replay
и приходил503, после output — stream_incomplete вместо ошибки размера.
Пять production строк сохраняют exact typed size evidence до generic network
recovery. Тот же выбор после исправления: **16 passed**.

Actual socket reader limit1024 и upstream message4096 воспроизводят настоящий
aiohttp size error; следующий небольшой запрос работает на том же аккаунте.
HTTP/WS before/after output, единственный terminal error, no health/exclusion,
reservation release и свободный response-create gate проверены. Other-code
controls1002/1006/1011 и ordinary disconnect health behavior сохранены.

### 32.4. Верификация и закрытие

Финальная объединённая focused suite: **207 passed**, одно existing
Starlette/AnyIO deprecation warning. Промежуточные прогоны не суммируются.
Ruff check/format, targeted ty, architecture/cancellation/timing/simplicity
checks, strict change validation и **68/68 main specs** — PASS.
Повторный source/scenario review выполнен без отдельного reviewer agent;
все девять delta scenarios сопоставлены с тестами. Specs/context синхронизированы.

Три собственные registry строки обновлены на «закрыто локально» вместе с
F-050 и сводным диапазоном журнала. Verified change:
[repair-bridge-json-lite-close-contracts](openspec/changes/archive/2026-10-02-repair-bridge-json-lite-close-contracts/),
[verification evidence](openspec/changes/archive/2026-10-02-repair-bridge-json-lite-close-contracts/verification.md).
Public artifacts, cloud CI, deployed replicas и реальный OpenAI/Codex traffic
этими проверками не подтверждены. Commit/push/release/deployment не выполнялись.

## 33. UP-ISSUE-2028 / UP-PR-2487 / UP-PR-2490 — authorization logs, TOTP и refresh diagnostics — 2026-10-03

Ровно три исходные registry задачи; база
`f52adb7274c96c0702e19aa02eabd4f1c7556231`, прежние dirty batches сохранены.
Для TOTP и refresh diagnostics production fixes уже находились в source;
новый production defect подтверждён только для логирования, F-051.

### 33.1. UP-ISSUE-2028 / F-051 — credential tails

Original issue probes и дополнительные status/ampersand/placeholder cases дали
**56 failed / 32 passed** до правки. Authorization field теперь маскируется
до generic token substitutions: complete quoted field сохраняет delimiters,
остальное маскируется до текущего line end. Unquoted same-line status/code
после поля больше не гарантируются; structured extras и следующие строки
сохраняются. Старые separator expectations обновлены вместе с контрактом.

Новый logging suite: **94 passed**. Проверены error fields, text/JSON messages
и rendered exceptions, actual log-file writes, quoted context, LF/CRLF/CR,
idempotency и no sentinel leakage. Existing Basic/Bearer/structured logging
behavior продолжает проходить свою suite.

### 33.2. UP-PR-2487 — TOTP HTTP path

Fullwidth, Arabic-Indic, Persian, superscript и mixed digits проверены на
setup-confirm и verify routes. HTTP400 invalid_totp_code не меняет enrollment,
replay step или session cookie. Следующий formatted ASCII code принимается
и продвигает counter. Existing window/replay coverage также проходит.
Новая production правка нормализатора не требовалась.

### 33.3. UP-PR-2490 — real local OAuth failures

Локальный aiohttp сервер реально принимает OAuth refresh form; реальные
AuthManager/AccountsRepository используют owned DB session. Десять сочетаний
HTTP401 revoked/invalidated, HTTP400 expired, HTTP503 hostile code и HTTP429
без code проверены при двух порядках private/ordinary callers. Один exchange,
одно safe warning, SHA-256 account reference, safe code/other и classification
flags, no identity/credential/provider body/exception leakage — PASS.
Permanent failures сохраняют REAUTH_REQUIRED, transient — ACTIVE; credential
ciphertexts не меняются. Existing unit tests подтверждают transport и local
pre-exchange failures/claim release. Новая production правка не требовалась.

### 33.4. Проверки и закрытие

Финальная focused suite: **279 passed**, одно existing Starlette/AnyIO warning.
Отдельный metrics logging test с frozen optional dependency: **1 passed**;
промежуточные прогоны не суммируются. Ruff check/format, targeted ty,
architecture/cancellation/timing/settings/simplicity и strict change validation
— PASS; **68/68 main specs** valid. uvloop-only suite на Windows не выполнена.

Повторный review current source/scenarios выполнен без отдельного агента.
Specs/context синхронизированы; troubleshooting объясняет потерю same-line
context после unquoted Authorization. Stale graph после reindex не использован
как финальное evidence; финальная сверка опирается на файлы и runtime tests.

Три собственные registry строки закрыты локально; F-051 и верхний summary
обновлены. Verified change:
[repair-auth-log-audit-contracts](openspec/changes/archive/2026-10-03-repair-auth-log-audit-contracts/),
[verification](openspec/changes/archive/2026-10-03-repair-auth-log-audit-contracts/verification.md).
Public/cloud/deployed/real upstream scope остаётся отдельно.
Commit/push/release/deployment не выполнялись.

## 34. UP-PR-2504 / UP-PR-2521 / UP-PR-2444 — usage, source telemetry и generation samples — 2026-10-03

Проверены и закрыты локально ровно три registry items. База рабочего дерева:
`f52adb7274c96c0702e19aa02eabd4f1c7556231`, поверх ранее существовавших изменений.
Сравнение с pre-edit snapshot подтвердило сохранность **108 unrelated tracked
diff blocks**. Нового исправляющего SHA нет.

### 34.1. UP-PR-2504 — существующий cache-write учёт подтверждён

24 новых сценария выполняют реальный локальный HTTP/WebSocket native-protocol
upstream через `POST /v1/responses`, Python transport и изолированную SQLite.
100000 input, 20000 cached reads, 24 output и missing/negative/50000/excessive
200000 write counts дают independently calculated total0.8212/0.8212/0.9462/1.0212
USD. Проверены raw nullable write counts, disjoint normalization, finalized
reservations, повторная CAS finalization без двойной оплаты, read API cost
components и следующая blocked429 request без второго upstream dispatch.
Existing100000-write example1.25USD, migration/history/missing-cost repair
проходят; ещё 6 tests проверяют automation/limit/planner warm-up и probe.

### 34.2. UP-PR-2521 — optional telemetry подтверждена через продуктовые пути

20 новых проверок local upstream → Chat/Responses API → DB → request-log API.
Stream/non-stream сохраняют output и usage; missing/bool/int32-overflow reasoning
остаётся unknown, invalid cached count не даёт discount, overflowing timing sum
игнорируется. Multiline CRLF и UTF-8 fragments сохраняют metadata; Chat raw bytes
идентичны, Responses сохраняет контракт своего public envelope. Valid limited
key settles13 tokens; invalid non-stream totals дают502/usage_unavailable,
released reservation и unchanged zero counters. Source speed остаётся
legacy_estimate либо missing_usage, без invented subscription samples.

### 34.3. UP-PR-2444 / F-052 — подтверждённый дефект output sampling исправлен

Две spaced/escaped unit regressions упали до правки. Actual local HTTP route
записал first output1000 вместо500ms: lexical verbatim scanner искал точное
`"delta":`, а nested keys могли создать/скрыть sample. Новый observer использует
shared parsed-content classifier и существующий cached SSE carrier; byte relay
сохранён. Plain-string decoder-limit failures не прерывают optional sampling.
Все spacing/escaping/nested-key cases и no-second-decode test PASS.

Actual HTTP и WebSocket upstreams подтверждают TTFT125, first non-reasoning
output500, two output chunks, terminal1000 и total3000ms после2s cleanup.
Для24 output/4 reasoning DB, request-log API и qualified daily reports дают
40TPS и tpsSampleCount1. Timing migration и median/filter/sample tests PASS.

### 34.4. Проверки и закрытие

Основная focused suite — **460 passed**; отдельные background tests — **6 passed**.
После decoder guards финальный rerun modified subsystem — **74 passed**; reruns
не суммируются, distinct coverage468 cases. Ruff check/format, targeted ty,
proxy architecture/cancellation/timing seam checks и strict change validation
PASS; **68/68 main specs** strict valid. Main/delta requirement blocks совпадают.
Сценарии и итоговый diff повторно проверены без отдельного агента.

Собственные строки трёх UP-PR обновлены, F-052 и summary синхронизированы.
Verified OpenSpec:
[repair-usage-and-generation-evidence](openspec/changes/archive/2026-10-03-repair-usage-and-generation-evidence/),
[verification и source fingerprints](openspec/changes/archive/2026-10-03-repair-usage-and-generation-evidence/verification.md).
Hosted incidents, packaged Rust helper, PostgreSQL runtime, public artifacts и
current-head cloud gates этим локальным evidence не закрываются.
Commit/push/release/deployment не выполнялись.

## 35. UP-PR-2525 / UP-PR-2526 / UP-PR-2528 — source instructions, collaboration и output budgets — 2026-10-03

Ровно три строки §6 закрыты в локальном scope. Base HEAD
`f52adb7274c96c0702e19aa02eabd4f1c7556231`; evidence относится к dirty source
snapshot с SHA-256 fingerprints в verification, а не к новому коммиту.
Предыдущие изменения сохранены. Исторический статус автора из ISSUES.md не
принимается за доказательство upstream merge или текущих cloud gates.

### 35.1. UP-PR-2525 — существующая source instruction projection подтверждена

Dashboard API create/PATCH → isolated SQLite → stored metadata readback → оба
Codex catalog views возвращают исходные и обновлённые строки с Unicode,
CRLF/tabs и whitespace. Девять новых cases проходят и до правок: string,
empty/whitespace-only, null/bool/int/float/list/mapping. Existing tests также
подтверждают missing default. Capabilities сохранены, credentials и request
overrides отсутствуют в catalog. Добавлен отсутствовавший normative main
requirement и stable context; generation instructions автоматически не меняются.

### 35.2. UP-PR-2526 / F-053 — dangling namespaced function choices исправлены

Новая независимая выборка дала **12 failed**: source уже удалял неподдерживаемый
namespace, но forced/allowed function choice продолжал ссылаться на него.
Shared choice predicate учитывает оставшийся namespace для functions; при
pruning сохраняет bare functions и mode, пустой allowed choice удаляет.

Все **88 recording loopback HTTP cases** покрыты: оба Responses paths и slash
forms, v1/v2/nonblank future version и explicit namespace opt-in, invalid
declarations, полные nested schemas, forced namespace/function и оба allowed
shapes. Unsupported hosted tools и includes pruned; разрешённые namespaced
function choices сохранены. Шесть связанных API-key route tests PASS.
Implemented version opt-in и новые pruning semantics синхронизированы в SSOT.

### 35.3. UP-PR-2528 / F-054 — output-budget precedence исправлена

Новая выборка дала **16 failed**: raw true превращался в1, false/zero в0,
negative count обходил GPT-6 fallback. Shared compatible projection принимает
только positive non-boolean integers, без coercion и изменения native metadata.

**44 новых cases** покрывают три GPT-6 slugs + unknown model, 11 raw values и
list/retrieval/slash/native data alias (176 reads). Valid96000/1 сохраняют
precedence; malformed known limit→128000, unknown→null. Все четыре output
fields согласованы; input272000, raw ceiling872000, native field values/types и
registry snapshot остаются прежними. Полностью missing field покрыт прежними
route tests. Новый normative requirement/context синхронизирован.

### 35.4. Проверки и закрытие

Основной прогон — **252 passed**. Добавленные затем allowed-function-choice
cases — **16 passed**, без дублирования основного прогона; related API-key
selection — **6 passed**. Итого **274 различных cases**. Ruff check/format и
targeted ty всех четырёх Python files, proxy architecture и diff check PASS.
Change strict valid; **68/68 main specs** strict valid; main/delta blocks
согласованы. Итоговый source/contract review проведён основным агентом без
делегированного reviewer.

Собственные строки UP-PR-2525/2526/2528, F-053/F-054 и summary обновлены.
Verified OpenSpec:
[repair-source-catalog-output-contracts](openspec/changes/archive/2026-10-03-repair-source-catalog-output-contracts/),
[verification и fingerprints](openspec/changes/archive/2026-10-03-repair-source-catalog-output-contracts/verification.md).
Hosted model sources, actual client collaboration sessions, public artifacts и
current-head cloud gates остаются отдельным scope. Commit/push/release/deploy
не выполнялись.

## 36. Три задачи: метрики пула, Force Probe и weekly-only reserve (2026-10-03)

Локально закрыты ровно **UP-PR-2523 / UP-PR-2524 / UP-PR-2527** на base HEAD
`f52adb72` с сохранением предыдущих dirty changes. Findings F-055/F-056,
собственные карточки и summary обновлены. Проверка выполнена основным агентом
независимо от исходных claims; делегированный reviewer не использовался.

### 36.1. UP-PR-2523 / F-055 — доступность учитывает access rejection

**9 failed** на real database + ASGI metrics exposition: три established
blocking reasons × future/unknown/unreadable expiry давали availability1 при
routing block. Причина не передавалась в существующий shared predicate.
Теперь reason берётся из уже загруженного snapshot; status inventory сохраняется,
repair до refresh-only warning возвращает availability1 на следующем scrape.
Quiet expiry/deletion, zeroes, failure503→fresh recovery, overlapping refresh,
optional-dependency и multiprocess cases PASS. Prometheus extra установлен
из frozen lock; итоговые exporter tests исполнены, без skip.

### 36.2. UP-PR-2524 — snapshot settlement подтверждён

Existing clone-before-teardown fix проверен через dashboard route и реальные
rollback/close repositories: missing/partial/monthly rows, zero primary capacity,
newer failure vs lease-only activity, rejected/network-failed probes PASS.
Три новых сценария weekly-primary87% и expired primary/secondary доводят
accepted probes до healthy без изменения сохранённых rows или thresholds.

### 36.3. UP-PR-2527 / F-056 — weekly recovery и quota Resume

14 real Responses cases на canonical/v1 routes подтверждают fresh post-block
weekly-primary recovery, cleared expired local hold, account ownership и storage.
Missing/pre-block/same-second/exhausted/debounce evidence не восстанавливает
аккаунт; independent rate-limit сохраняет persisted deadline/local cooldown.
Exhaustion возвращает HTTP429 usage_limit_reached. Synthetic5h rows не создаются.

В dashboard отсутствовал Resume для quota_exceeded при существующем backend
reactivation. **3 frontend cases failed** до изменения canResume. Callback-once,
busy/read-only и reauth protections теперь PASS; real API/CAS снимает persisted
quota markers, не меняя owner. Chromium проверяет real Accounts rendering,
single existing POST и active actions после refresh. Screenshots
[до](openspec/changes/archive/2026-10-03-verify-account-pool-probe-recovery/screenshots/quota-resume-before.png)/
[после](openspec/changes/archive/2026-10-03-verify-account-pool-probe-recovery/screenshots/quota-resume-after.png)
проверены визуально; browser API fixtures и real backend tests явно разделены.

### 36.4. Проверки и остаток

Основной прогон **716 Python passed**, затем **3 distinct API cases passed**:
итого **719 Python**. Frontend **24 passed**, Chromium **1 passed** —
**744 distinct cases**. Последний прогон изменённых integration files:
**69 passed**; повторы не добавлены к счётчику. Ruff check/format, targeted ty,
TypeScript, ESLint, proxy architecture/cancellation/timing/settings/simplicity,
scoped diff check PASS; change strict valid, **68/68 main specs strict valid**.

Verified OpenSpec:
[verify-account-pool-probe-recovery](openspec/changes/archive/2026-10-03-verify-account-pool-probe-recovery/),
[verification](openspec/changes/archive/2026-10-03-verify-account-pool-probe-recovery/verification.md).
Hosted accounts/инциденты, production replicas, public artifacts/Pages и
current-head cloud CI/CodeRabbit/release остаются открытым отдельным scope.
Commit/push/PR/release/deploy не выполнялись.

## 37. UP-PR-2512 / UP-PR-2515 / UP-PR-2529 — plan alias, JSON input и shared logging (2026-10-03)

Закрыты локально ровно три выбранные строки на base HEAD
`282ce147038ac53b72bca30d69c4ad9a9ac1b7cc`; исходный checkout был чистым.
Публичный upstream status не изменялся.

### 37.1. UP-PR-2512 — Business Pro Lite подтверждён

Existing source fix корректно canonicalizes `self_serve_business_prolite` в `prolite`.
Three import variants (alias, whitespace/uppercase, canonical) проходят dashboard
import API и readback отдельной DB session. Five actual loopback HTTP refresh cases
подтверждают accepted paid transition, unknown-plan refusal и unconditional conflicting
workspace refusal. Fresh-session metadata/usage, default `1125/37800` credits,
Pro-equivalent eligibility, сохранение account identity/workspace/encrypted credentials
и `/api/usage/summary` подтверждены. Новый account tier или production alias logic
не добавлялись.

### 37.2. UP-PR-2515 / F-057 — equivalent JSON controls исправлены

**16 failed / 40 passed до правки** в новой integration suite: только `text.format`
терял JSON instruction из input; object/string `response_format` уже работали.
JSON mode теперь определяется shared Responses predicate после format mapping.
**48 route variants × two turns = 96 actual HTTP upstream requests** покрывают
system/developer, string/content parts, mixed-case JSON mention, Unicode/CRLF,
stream/non-stream и canonical/trailing slash requests. Slash requests используют
существующий redirect с `follow_redirects=True`; redirect-free aliases не заявляются.
Developer role, original content/order, unrelated instruction hoisting и unchanged
prefix после дополнительного user turn подтверждены. Main spec больше не обещает
unsupported original system role. Focused mapping/cache/Responses/Chat suites PASS.

### 37.3. UP-PR-2529 / F-058 / F-059 — JSON observability исправлена

Metrics listener уже не применяет global logging config/level. Expanded subprocess
matrix выявила два смежных дефекта existing formatters: **info/JSON** записывал
null client/request/status; **debug/JSON** без optional OpenTelemetry рекурсивно
форматировал failed trace lookup diagnostics и не запускал reachable listener.
JSON access formatter декодирует actual Uvicorn tuple без мутации LogRecord;
диагностика tracing helper пропускает собственное enrichment.

После исправления **four real CLI subprocesses PASS**: text/JSON × info/debug,
primary `/health` и standalone `/metrics`, log path with spaces, URL userinfo
redaction и identical access records в stream/file. Numeric 200/503, repeat rendering
без LogRecord mutation и ordinary trace/span enrichment проверены отдельно.
Established INFO/WARNING keyed-secret policy не менялась.

### 37.4. Проверки и границы

**779 различных целевых Python тестов PASS**: Chat/format/cache/new product suite
376, plan/usage/metrics/CLI 253, structured logging/OTel 146, CLI subprocesses 4.
Один optional uvloop module пропущен; повторные проверки не прибавлены к итогу.
Ruff check/format, scoped `ty check`, strict change validation и **68/68 main specs**
PASS. Final implementation отдельно сверена с requirements/scenarios и regression
evidence; критичных незакрытых расхождений не найдено.

OpenSpec:
[verify-plan-json-metrics-contracts](openspec/changes/archive/2026-10-03-verify-plan-json-metrics-contracts/),
[verification](openspec/changes/archive/2026-10-03-verify-plan-json-metrics-contracts/verification.md).
Собственные registry rows, F-057/F-058/F-059 и summary синхронизированы.
Hosted plans/provider/Codex UI, native-helper artifacts, PostgreSQL replicas,
installed tracing exporters, POSIX signal shutdown, public packages/images и
exact-head cloud CI остаются отдельным непроверенным scope.
Commit/push/PR/release/deploy не выполнялись.

## 38. Telemetry ordering, client families и stateless encryption — три задачи

Дата: **2026-10-03, Europe/Kiev**. Source HEAD `282ce147038ac53b72bca30d69c4ad9a9ac1b7cc`; этот пакет остаётся uncommitted. Ровно три исходные registry rows: **UP-ISSUE-1844 / UP-ISSUE-1843 / UP-ISSUE-1572**. Прежние dirty изменения сохранены.

### 38.1. UP-ISSUE-1844 — F-060 / F-061 исправлены в локальном scope

Исходная blocking-socket matrix воспроизвела **9 failing dashboard-disable races** на register/activate/snapshot. Sender lock охватывал только final snapshot POST; activation мог пройти после opt-out, а dashboard сохранял disabled во время отправки. Теперь fresh consent/identity check, register, activate и final POST сериализованы с dashboard decision commit и opt-out scheduling. **12 actual loopback collector/API races PASS**: три фазы × completion/cancel/HTTP503/timeout. Подписи Ed25519 проверены receiver; после opt-out новые disabled sends молчат. Отменённые задачи awaited, сетевой total timeout сохранён.

Четыре failing timestamp cases показали acceptance malformed strings и сохранение offset без UTC canonicalization. Field теперь typed datetime с ISO parsing; malformed/numeric refusal, naive/offset inputs и UTC `Z` сериализация подтверждены. Preview env suppression и persisted-over-env precedence сохранились в focused suites. Глобальный fence между процессами требует collector-side authority; deferred lifecycle diagnostics и hosted collector не закрыты.

### 38.2. UP-ISSUE-1843 — existing fix независимо подтверждён

**11 stored-group cases** и **24 actual Responses/Chat routes** покрывают CLI/Desktop aliases, private/missing groups, stream/non-stream, real local HTTP upstream и new-session DB log readback. Canonical shares и `clients_other_ratio` корректны, private UA strings не появляются в preview. Main spec раньше не перечислял работающие `codex`/`codex-cli` и Desktop aliases; allowlist синхронизирован. Новая production mapping не понадобилась.

### 38.3. UP-ISSUE-1572 — existing key behavior подтверждён, operator contract исправлен

Dashboard account import при valid env key и deliberately unusable default key path сохраняет decryptable ciphertext; fresh settings/encryptors и два отдельных Python процесса читают общий ciphertext без key-файла. Explicit bytes/file/env precedence, blank-file fallback, invalid settings, same/different fingerprints и unchanged sentinel проверены. Topology/spec/context теперь разрешают existing `CODEX_LB_ENCRYPTION_KEY`; mismatch diagnostic указывает env и file remediation, не раскрывая ключи. Реальный PostgreSQL replica deployment отдельно.

### 38.4. Verification и ограничения

**184 различных целевых Python теста PASS**: combined telemetry/client/key/migration/settings matrix182 и два focused fingerprint-lock tests. Final diagnostic integration rerun PASS и не прибавлен к числу. Ruff check/format, scoped `ty`, cancellation safety, strict change validation и **68/68 main specs strict PASS**. Verification сопоставлена с каждой requirement/scenario; применимый локальный scope закрыт, внешние ограничения сохранены.

OpenSpec: [repair-telemetry-and-stateless-key-contracts](openspec/changes/archive/2026-10-03-repair-telemetry-and-stateless-key-contracts/), [verification](openspec/changes/archive/2026-10-03-repair-telemetry-and-stateless-key-contracts/verification.md).

Cloud CI, public packages/images, deployed PostgreSQL replicas, real client/account traffic, collector authority/retention и глобальная межпроцессная гонка не сертифицированы. Commit/push/PR/release/deploy не выполнялись. Задачи1843/1572 уже содержали working code, поэтому их закрытие опирается на новую проверку и исправление неполного контракта, а не на исходный claim РЕШЕНО.

## 39. UP-ISSUE-2471 / UP-ISSUE-2470 / UP-ISSUE-2456 — native transport и Windows route parity

Пакет содержит ровно три строки исходного реестра. Base SHA `282ce147038ac53b72bca30d69c4ad9a9ac1b7cc`; изменения локальные, без fixing commit, push, релиза или production. OpenSpec: [repair-native-transport-recovery](openspec/changes/archive/2026-10-03-repair-native-transport-recovery/verification.md).

### 39.1. UP-ISSUE-2456 / F-062 — исторический excerpt не отражал актуальную постановку

Свежий upstream report уточняет Windows IOCP route loss **1231/1232**; reset/timeout **64/121** остаются endpoint-attributed. Форк классифицировал именно 64/121 как process-wide и пропускал 1231/1232 с errno EINVAL. **8 red-before failures**: два route-number unit cases, два endpoint refusal cases и четыре product routes.

Классификатор исправлен; сообщение с номером ошибки не создаёт provenance. Шесть новых HTTP route cases используют реальные shared ClientSession generations: typed connector retry остаётся на том же аккаунте, ambiguous error не replay; новая generation обслуживает следующие вызовы, старый активный lease удерживает retired session до release. Для route loss account health и pressure не меняются; 64/121 не вращают общий клиент и сохраняют обычный external upstream_unavailable path. Строка **ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО**; physical adapter loss и public/cloud отдельно.

### 39.2. UP-ISSUE-2471 / F-063 — HTTP/2 isolation подтверждена, потеря diagnostics исправлена

Source-built helper + временный CA + actual TLS HTTP/2 origin наблюдают physical connections. Аккаунт A переиспользует своё соединение для трёх запросов, B использует другое; abort A не мешает B завершиться. Shared-pool control, убирающий IPC pool key, воспроизводит collateral failure обоих аккаунтов.

Второй дефект подтверждён через БД: **6 actual body-failure variants** сохраняли failure_phase=null. Attempt-owned typed trace теперь передаёт request/body_read phase, native_transport_error, static NativeEgressTransportError и observed HTTP status в request_logs. Для body failure сохраняется 200, для pre-head failure статус не выдумывается. Client SSE не получает новых diagnostic fields; ambiguous POST не повторяется. Более сильная cancellation/terminal classification имеет приоритет.

Строка **ИСПРАВЛЕНО ЛОКАЛЬНО / ЧАСТИЧНО ПРОВЕРЕНО**. Raw error-chain/cf-ray и per-request WSS preference из более широкого upstream report остаются открыты; macOS offload не сертифицирован.

### 39.3. UP-ISSUE-2470 — existing cleanup подтверждён на product path

**18 сценариев × 3 actual POST = 54 upstream exchanges**: v1/backend/native Codex headers, stream/non-stream, EOF/body/pre-head failure. При caps=1 после каждого запроса реальное account pressure равно нулю, reservation released/finalized, persistence drained, helper stream state empty. Два отказа не мешают третьему успешному запросу без restart. Backend stream=false получает свой JSON upstream contract; canonical non-stream собирает SSE. Строка **ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО**; необнаруженный дефект не заменяли лишним рефакторингом.

### 39.4. Итоговые проверки и остаток

- **595 Python passed**, 12 terminal-probe cases исключены только из этого процесса и каждый затем прошёл в fresh process с timeout20: **12 × 1 passed**. Дополнительный focused proxy-utils selector: **17 passed**. Итого **624 разных Python cases PASS** на финальном source, включая **26 новых product cases**; skips не выдавались за native evidence.
- Полный совместный прогон не сертифицирован: unconstrained run завис, bounded rerun завершился timeout30 на существующем native terminal probe; grouped isolated selector также завис на routed case. Fresh-process cases PASS. Причина group/session-lifecycle нестабильности не изолирована; **CI-04 остаётся открыт**.
- `cargo test --locked -p codex-lb-egress -p codex-lb-egress-worker`: **25 PASS**. Helper SHA-256: `019142892DE956AA904BDA69759B84CAB283912A9BE8919C3C9AA03815E48B81`.
- Ruff check/format, proxy architecture, simplicity budgets, strict change validation и **68/68 main specs** PASS. Все четыре changed requirement blocks сверены с main SSOT.
- **19 pre-existing modified files**, кроме обновляемого registry, сохранены byte-identical. Graph refresh не увидел новый trace symbol; его data flow проверен по текущему source и actual routes.
- Старый complete active change `recover-windows-transport-failures` содержит superseded 64/121 delta; его нельзя механически архивировать поверх исправленного main spec. Исторические artifacts не переписывались.
- Public artifacts/cloud gates/реальные provider/client приложения/production остаются отдельным scope; no commit/push/release/deploy.

## 40. UP-ISSUE-2425 / UP-ISSUE-2081 / UP-ISSUE-1208 — images и terminal transport evidence

Дата: **2026-10-03, Europe/Kiev**. Ровно три исходные registry rows. Base SHA `282ce147038ac53b72bca30d69c4ad9a9ac1b7cc`; текущий пакет локальный, uncommitted. [OpenSpec/evidence](openspec/changes/archive/2026-10-03-verify-image-websocket-transport-contracts/verification.md).

### 40.1. UP-ISSUE-2425 — existing bounded admission подтверждена

**69 image tests PASS**. Дополнительно проверены backend route, text-image-text retained connection и output-free `server_is_overloaded` recovery. Inline PNG/JPEG bytes сохраняются; successful follow-up использует retained bridge, raw path запрещён guard. Per-image/frame caps, unsupported images, explicit rollback и cancellation сохранились. Blanket bypass уже ограничен existing admission, нового production routing patch не требовалось. Upstream report остаётся открытым; fleet failure percentages не объявлялись воспроизведёнными.

### 40.2. UP-ISSUE-2081 — F-064 / F-065 исправлены

**4 red-before route failures** доказали ошибочную health penalty для positively ended error-kind sockets. Typed `transport_ended` идёт из direct/routed/native adapters. Real source-built native socket abort дополнительно воспроизвёл потерю provenance из-за Rust `ResetWithoutClosingHandshake`; только этот typed protocol variant переклассифицирован в transport. Другие protocol failures не нейтрализованы.

Отдельный selected-owner error-kind quota terminal сохранял `upstream_unavailable` вместо исходного 429 `usage_limit_reached`; existing response.failed test не покрывал эту ветку. Refusal ветки теперь прекращают replay и передают authentic sanitized event обычному finalizer без раннего health write. **24 direct route cases**, adapter controls и owner/file-bound helper regressions PASS; параметры/reset metadata сохраняются, connect/send не повторяются, log и health ровно один раз. Pre-dispatch owner failures отдельно сохраняют старый contract.

### 40.3. UP-ISSUE-1208 — F-066 исправлен, parity ограничена доказательствами

Actual TLS HTTP/2 probe до правки не имел `content-encoding`; source native requests теперь получают scoped opt-in zstd level3 для prepared Responses/compact JSON POSTs. Raw relay остаётся exact bytes; multipart и Python fallback не получают zstd. Stale Content-Encoding/Content-Length заменяются только для opt-in body. H2 origin видит matching encoded length, deterministic repeated body, exact decoded JSON, lowercase H2 headers, selected account/native identity и fixed windows. Нормативное обещание «prevent fingerprint divergence» и source claim полного header order исправлены на измеримые гарантии. Real Codex ClientHello/header-order comparison и hosted acceptance не выполнены; строка остаётся частично проверенной.

### 40.4. Verification и остаток

- **797 разных Python cases PASS**: 274 unit adapter/native/Codex/fingerprint/cancellation; 69 image; 24 direct terminal routes; 69 proxy-utils selected tests; 349 native wire/HTTP cases; 12 native terminal cases каждый в fresh process. Повторные selectors не суммировались. Это разделённые процессы, не aggregate-green claim.
- **25 Rust tests PASS**; helper SHA-256 `BBD2BB52E5FE9989151E245A5CA7E3A280D292C304B2540EC68417973205466D`.
- Ruff check/format, scoped `ty`, architecture, cancellation/timing seams, simplicity budgets, strict change и **68/68 main specs PASS**. Verification сопоставлена с каждой requirement/scenario; OpenSpec синхронизирован и архивирован.
- 12 ранее нестабильных grouped terminal cases прошли на финальном helper в отдельных процессах. CI-04 не закрыт, cause/stability aggregate не заявлены.
- Три собственные registry rows, F-064/F-065/F-066, summary и claims в ISSUES.md синхронизированы. 66 unique F rows и repository-relative links проверены. Из 57 baseline dirty/untracked paths восемь относятся к этому пакету; остальные **49 byte-identical**. Fast graph refresh всё ещё не видит renamed test; текущий source и runtime tests служат evidence.
- Live provider/client traffic, TLS fingerprint equivalence, public artifacts/cloud gates и production остаются отдельным scope. Commit/push/release/deploy не выполнялись.

## 41. UP-ISSUE-2493 / UP-ISSUE-2465 / UP-ISSUE-2455 — bridge continuation contracts

Дата: **2026-10-04, Europe/Kiev**. Ровно три исходные source-queue rows. Base SHA `282ce147038ac53b72bca30d69c4ad9a9ac1b7cc`; пакет локальный, без fixing commit, push, публикации или production. [OpenSpec/verification](openspec/changes/archive/2026-10-04-repair-bridge-terminal-lineage-failover/verification.md).

### 41.1. UP-ISSUE-2493 — существующая terminal delivery подтверждена

Actual local WebSocket origin сначала завершает turn, затем отказывает proxy-injected anchor. Native backend canonical/slash routes проверены до commitment и после response.created/response.in_progress keepalives. Local fence до commitment возвращает structured 502 stream_incomplete; после commitment клиент получает ровно один response.failed, без unexpected EOF/private marker/raw anchor. Upstream previous_response_not_found остаётся в request log. API-key reservations finalized/released, pending/queued requests пусты, account pressure=0. Снятие conclusively denied anchor отдельно подтверждено existing HTTP route regression. Исходное описание ISSUES.md обещало иной общий rate_limit_exceeded/retry-delay outcome; приведено к фактическим проверенным веткам.

### 41.2. UP-ISSUE-2465 / F-067 — lineage, Lite и unit-fixture boundary

Два последовательных distinct logical turns получают bounded eventless failures от real local WebSocket; retry последнего portable full body после poison boundary завершается на fresh lineage без старого previous_response_id. Полный body сохранён. Delta-only, account-owned и ambiguous operation-journal ограничения остаются: одна лишь тишина не разрешает дублировать активную recovery claim.

Actual local HTTP origin для image+function tool + Responses-Lite получает parallel_tool_calls=false при true/false/null/omitted ingress, reasoning.context=all_turns, неизменные image/tool payloads и derived Lite header. V1/backend paths, existing multiline/Lite/non-Lite и bounded-image contracts дополняют друг друга.

Расширенная unit selection воспроизвела **6 failed / 101 passed**: unsafe full-resend fixture подменяла lookup, но оставляла real retire_continuity_owner_if_unavailable, который открывал SQLite без таблицы accounts. Изолированный повтор дал те же **6 failed / 4 passed**. Fixture теперь возвращает false на retirement boundary и проверяет expected_account_id=acc-owner; refusal assertions не изменены. Повтор той же selection: **107 passed**. Runtime-code для этой тройки не менялся.

### 41.3. UP-ISSUE-2455 — existing quota failover подтверждён реальным HTTP

API-key-scoped durable alias/count/fingerprint seeded в actual SQLite. Payload budget принудительно мал только в тесте. Full resend получает actual HTTP429 usage_limit_reached на A и response.completed на B; stale turn-state header отсутствует у обоих upstream attempts, полный input сохранён. Canonical и slash routes дают одинаковый результат.

Wrong API-key scope, prefix mismatch, отсутствующий previous output, explicit anchor, account-owned item и conflicting proof/owner не получают account-neutral quota failover. Reservations settled/released, pressure обоих accounts=0. Existing seven-case regression добавляет file owner и failed optional lookup; raw owner conflict и forwarded/replay controls сохранены. Protected guard отказа не заменяет проверку конкретной live-инсталляции.

### 41.4. Проверки и закрытие

- New real-origin/DB suite: **27 passed**.
- Focused bridge unit selection после F-067: **107 passed**.
- Existing denied-anchor/stale-owner/quarantine route selection: **28 passed**.
- Full Lite/multiline/eventless/cancel-drain suites + denied-anchor retirement route: **98 passed**.
- Existing bypass proof + raw owner-conflict selection: **8 passed**.
- Ruff check/format, targeted ty, architecture, cancellation, timing, settings tiers, simplicity budgets и strict OpenSpec: PASS; **68/68** main specs.

Counts относятся к отдельным focused commands, не к full-repository/CI aggregate; точные команды и source fingerprints находятся в verification. Все три собственные registry rows и summary согласованы; unit defect F-067 закрыт в TEST SCOPE. Из первоначальных 76 dirty/untracked files вне заявленных metadata/spec правок ничего не изменено. Fixing SHA, public release, cloud checks, real Factory/Codex/macOS provider traffic и production не заявлены. F-045/CI-04 и внешние residuals других пакетов остаются открытыми.

## 42. Сверка всех отметок завершения — 2026-10-04

Это сверка реестра с существующими доказательствами, а не новый runtime/CI прогон. Latest repair batch остаётся §41. Код, тесты, specs и archived artifacts этим этапом не изменены; меняется только issues-check.md.

### 42.1. Последняя тройка была отмечена

UP-ISSUE-2493 / UP-ISSUE-2465 / UP-ISSUE-2455 уже имели **ПРОВЕРЕНО / ЗАКРЫТО ЛОКАЛЬНО** в собственных строках §6, ссылки на verification и согласованные §§41/summary до этой сверки. Во всех 13 тройках §§29–41 primary rows также существовали: **37 локальных закрытий и 2 явно partial задачи**. UP-ISSUE-2471 сохраняет diagnostics/WSS residual; UP-ISSUE-1208 — real-client fingerprint/header-order residual. Эти две строки не закрыты полностью.

### 42.2. Исправлены старые связанные записи

| Запись | Что было | Теперь / доказательство |
|---|---|---|
| UP-ISSUE-2274 | Локально проверено, без явного закрытия и прямой verification link | Явно закрыто локально; bounded owner/scope и HTTP/compact/WS, §§13/14/21; [owner evidence](openspec/changes/archive/2026-10-01-repair-continuity-owner-snapshots/verification.md) |
| UP-ISSUE-2538 | НЕ ПРОВЕРЕНО при завершённых обеих частях JSON/Lite | Закрыто локально по §§32/41; [JSON/Lite](openspec/changes/archive/2026-10-02-repair-bridge-json-lite-close-contracts/verification.md), [real origins](openspec/changes/archive/2026-10-04-repair-bridge-terminal-lineage-failover/verification.md) |
| UP-PR-2542 | НЕ ПРОВЕРЕНО при пройденном test_otel.py | Закрыто локально в TEST SCOPE; independent logging/OTel module selection §37, [evidence](openspec/changes/archive/2026-10-03-verify-plan-json-metrics-contracts/verification.md) |
| UP-PR-2507 | Partial, metrics logging ещё отдельно | Закрыто локально: earlier CLI scope + four real primary/metrics CLI processes и file/stream checks §37; [evidence](openspec/changes/archive/2026-10-03-verify-plan-json-metrics-contracts/verification.md) |
| UP-ISSUE-2426 | НЕ ПРОВЕРЕНО при проверенных pool exporters | Закрыто локально: DB/ASGI status/availability и multiprocess scope §36; [evidence](openspec/changes/archive/2026-10-03-verify-account-pool-probe-recovery/verification.md) |
| UP-ISSUE-2410 | НЕ ПРОВЕРЕНО при проверенных Force Probe paths | Закрыто локально: payload/snapshot, real API/repository and negative controls §36; [evidence](openspec/changes/archive/2026-10-03-verify-account-pool-probe-recovery/verification.md) |
| UP-ISSUE-2443 | НЕ ПРОВЕРЕНО при проверенной API/report части | **ЧАСТИЧНО ПРОВЕРЕНО** по §34; dashboard UI/short-window/consumer-delay scope полностью не подтверждён. [Evidence](openspec/changes/archive/2026-10-03-repair-usage-and-generation-evidence/verification.md) |
| Commit 1f62b4f7 | В ПРОВЕРКЕ, только просмотр scope | Частично проверен: шесть из восьми named source entries имеют локальное закрытие; PR2543/2544 и full commit/cloud audit открыты |
| F-029 | Был выполнен Nix source/cloud scope, report не имел прямой ссылки в реестре | Добавлена [историческая verification link](openspec/changes/archive/2026-10-01-repair-nix-hook-source-filter/verification.md); новые platform/runtime claims не добавлены |

### 42.3. Полнота учёта и границы

| Группа | Проверено записей | Результат сверки |
|---|---:|---|
| F-находки §3 | 67 | Все IDs F-001…F-067 присутствуют по одному, статусы есть; 60 имеют scoped source/local fixes, 4 partial, F-010/F-037/F-045 открыты |
| Поставка/сопровождение §4 | 34 | У всех есть статус и выполненная часть/остаток; GOV-01 обновлён до current archive coverage |
| Source queue §6 | 297 | 40 явно закрыты локально, 6 partial, 251 ещё НЕ ПРОВЕРЕНО; это не 297 закрытых обращений |
| Commit queue §8 | 49 | Group scope не подменён source-task closure: 45 ещё НЕ ПРОВЕРЕНО, 3 partial и 1 scoped optional-env closure |
| Incidents §10.2 | 10 | 5 scoped source/local результатов; INC-01/02-OAUTH/08-PAUSE/09-DOC/10-QUOTA-DISPLAY остаются открыты |
| Install variants §15.1 | 15 | Все имеют own status/evidence или явно описанный остаток |
| SETUP/DOC-INSTALL §15.2–15.3 | 16 | 9 отмечены [x], 7 [ ] сохраняют явный незавершённый scope; partial work не превращена в полное закрытие |

Сверены все **29 независимых архивных reports за 2026-10-01…04** и их **201/201 completed tasks**; unchecked tasks в них нет. Каждый report теперь имеет ссылку/идентификацию из реестра. Два active upstream verification reports (narrow-input-image-upstream-transport-pin и retain-immediate-invalidation-bumps) не используются для автоматического закрытия новых claims: cache issue уже имеет independent §31, image contracts — independent §§40/41. Их active/archive lifecycle этим этапом не менялся.

После нормализации Markdown angle brackets **missing local links = 0**: проверены repository evidence и исторические attachment paths. Исторические sections/даты/tests counts сохранены; новая дата сверки не делает старые тесты свежими. Source queue type/IDs и внешние ссылки не удалены. Снимок всех 84 исходных dirty/untracked files подтвердил, что вне issues-check.md содержимое не менялось. Git diff whitespace check PASS.

Отдельно не закрыты public artifacts/metadata/Pages, real login/client/provider/platform scopes, exact-head cloud CI и aggregate stability F-045/CI-04. Отметка автора в ISSUES.md или наличие checked OpenSpec tasks сами по себе не превращают НЕ ПРОВЕРЕНО в resolved. Новые commit/push/release/deploy не выполнялись.

## 43. UP-PR-2508 / UP-PR-2513 / UP-PR-2537 — image reuse, control media types и Images hosts

Пакет обработал ровно три ранее НЕ ПРОВЕРЕНО source rows. HEAD остаётся `282ce147038ac53b72bca30d69c4ad9a9ac1b7cc`; результат локальный, без commit/push/release/deploy. Полный [verification report](openspec/changes/archive/2026-10-04-repair-image-control-transport-contracts/verification.md) содержит red-before, команды, границы и fingerprints.

### 43.1. UP-PR-2508 — существующая session reuse подтверждена

Три route формы через actual local WebSocket подтверждают text → PNG → text с image history на одной upstream connection, verbatim bytes и prompt-cache identity. Invalid-image terminal и silent origin оставляют reservations settled и account active; следующий text request работает. Short-budget wire case отправляет image один раз. Полная existing suite также подтверждает допустимые initial + one precreated retry при длинном бюджете; политика не менялась. Старое blanket-bypass требование в main spec теперь включает уже реализованное bounded-inline исключение. Строка закрыта локально; реальные vendor captures/cache hit rates и исторический #903 не сертифицированы.

### 43.2. UP-PR-2513 — два слоя empty-body media type исправлены

Пустые bytes сохраняли Content-Type; after normalization real aiohttp POST автоматически добавлял application/octet-stream. Empty payload нормализован в None, automatic Content-Type подавлен на direct/routed путях. Nonempty JSON/SDP, duplicate case spellings, first native header position, unchanged body/query и real Python/native HTTP-proxy requests проходят. Строка исправлена и закрыта локально.

### 43.3. UP-PR-2537 — incompatible Images fallback исправлен

Dedicated resolver уже выбирал Sol первым, но fallback всё ещё допускал Luna перед 5.5. Три red unit cases воспроизвели этот выбор; Images теперь используют Sol/Astra/5.5 с прежним Sol default. Account probes сохраняют Luna/5.5. Двенадцать real HTTP generation/edit/alias cases подтверждают public image tool/log model, reference-image bytes и native JSON/multipart input. Images trailing-slash refusal остаётся 405. Строка исправлена и закрыта локально; synthetic refusal origin не является доказательством текущих live provider capabilities.

### 43.4. Проверки, сохранность и текущий итог

| Проверка | Результат |
|---|---|
| New contract suite + host/control unit suites | 112 passed, без skips; native helper executed с запретом Python fallback |
| Existing image translation/admission/bridge/Images suites | 169 passed, без skips |
| Scoped Ruff/check-format и ty | PASS |
| Proxy architecture, cancellation, timing, settings tiers, simplicity budgets | PASS |
| Strict OpenSpec main/change, delta/main equality и git whitespace check | 68/68 main specs PASS, change valid, blocks equal, diff clean |

Текущая source queue содержит **43 локальных закрытия, 6 partial и 248 НЕ ПРОВЕРЕНО из 297**; исторические числа §42 сохранены как срез. Из 84 исходных dirty/untracked paths вне четырёх intended overlaps все 80 byte-identical. Предыдущие изменения proxy.py восстанавливаются точно после удаления четырёх добавленных строк; прежний context сохранён как prefix. Из existing source rows изменены только выбранные три. OpenSpec change синхронизирован, проверен и архивирован. Live provider/client, public artifacts, production, cloud gates и F-045/CI-04 остаются отдельными scope.


## 44. UP-ISSUE-2273 / UP-ISSUE-2272 / UP-ISSUE-2271 — retry accounting, cooldown и claim lifecycle

Дата: **2026-10-04, Europe/Kiev**. Ровно три исходные source-queue rows; base SHA `282ce147038ac53b72bca30d69c4ad9a9ac1b7cc`. [OpenSpec/verification](openspec/changes/archive/2026-10-04-verify-bridge-retry-claim-lifecycle/verification.md). Изменения локальные, без fixing commit, push, релиза или deployment.

### 44.1. UP-ISSUE-2273 — existing accounting подтверждён

Actual loopback WebSocket + HTTP v1/slash/backend routes дают durable counts 1→2 и cooldown для двух разных incomplete sends; authored reason-only terminal сохранён на исходной отправке. Stored-operation повтор не отправляет frame и не добавляет strike. 24 raw/interpreted cases покрывают explicit error precedence, missing/unknown reason, soft affinity, prewarm, skip-log, observed output, safe replay, disarmed attempt и deferred reasoning. Third proof-gated full resend может оставаться допустимым по existing policy; blanket prohibition не заявлена. Native stored-operation replay сохраняет отдельный existing downstream lifecycle, универсальная terminal delivery для него этим пакетом не сертифицирована. **Строка закрыта локально по accounting scope**.

### 44.2. UP-ISSUE-2272 — existing cooldown contract подтверждён

Real SQLite missing/zero/negative/elapsed deadline не создаёт phantom probe и допускает три повторных admission. Наблюдавшийся local cooldown при настоящей expiry допускает ровно один local half-open probe; repeated same-episode loads сохраняют его lease. Existing ownership/cleanup, ambiguous-send и settlement controls PASS. **Строка закрыта локально по описанному admission scope**; новую crash-expiry policy не утверждаем.

### 44.3. UP-ISSUE-2271 / F-068 / F-069 / F-070 — исправлены cancellation и receipt ownership

3 red-before release cases снимали новый local probe независимо от результата durable CAS. Direct await claim терял committed receipt при caller cancellation; отсутствующая prior row не давала release epoch даже после deferral. Scheduler-owned bounded acquisition сохраняет result до cancellation propagation, request получает exact receipt/inserted epoch, undispatched finalizer выполняет fenced release с cancellation deferral. Repository получает receipt внутри winning transaction, поэтому post-commit successor не подменяет returned generation. Repeated cancellation при release, existing/missing row, successor CAS и local key-lock timeout PASS; attempted/ambiguous send остаётся защищён.

**Строка частично исправлена, полного закрытия нет**. Process death/reclamation, uncertain internal timeout, generation rollback ABA, ordinary-success/newer-claim settlement policy и supported PostgreSQL/MySQL/migration runtime остаются открытыми. Remote Retry-After bound сам по себе не доказывает reclaimability.

### 44.4. Проверки и сохранность

- Финальные новые tests: **43 passed** (40 unit + 3 actual route cases), no skip/failure.
- Coordinator + новые tests: **111 passed**; existing targeted retry/ownership regressions: **71 passed**. Counts overlapping, не full-repository aggregate. Exact commands и final-source ordering — в verification.
- Scoped Ruff check/format, ty, architecture, cancellation, timing, settings tiers, simplicity budgets: PASS. Strict OpenSpec 1.11.0 change/main: **68/68 specs PASS**; delta/main equality проверена.
- Из 97 исходных dirty/untracked paths только issues-check.md и owning responses spec/context являются intended overlaps; остальные **94 byte-identical**. Original spec/context сохранены как byte prefixes. Ровно три existing source rows получили statuses/evidence. [Fingerprints](openspec/changes/archive/2026-10-04-verify-bridge-retry-claim-lifecycle/fingerprints.md).

Текущая source queue: **45 local closures, 7 partial, 245 НЕ ПРОВЕРЕНО из 297**. Исторические sections/counts сохранены; no new cloud/provider/artifact/production claims.


## 45. UP-ISSUE-2270 / UP-ISSUE-2268 / UP-ISSUE-2266 — cleanup fencing и paused delivery

Дата: **2026-10-04, Europe/Kiev**. Ровно три source rows, исходно НЕ ПРОВЕРЕНО; base SHA `282ce147038ac53b72bca30d69c4ad9a9ac1b7cc`. [Verification](openspec/changes/archive/2026-10-04-verify-bridge-cleanup-quarantine-backpressure/verification.md) содержит команды, red-before, mapping и границы. Результат локальный, без commit/push/release/deploy.

### 45.1. Scheduled cleanup — исправлено

4 initial scheduled failures подтвердили отсутствие count fence и повторный выбор изменённой строки после успешного удаления соседней. Timestamp/generation/count сравниваются с captured candidate, composite keyset проходит каждый ключ один раз. Batches1/128 покрывают same-timestamp strike, claim и epoch change, mixed и zero-delete batch; unchanged stale row удаляется. **12 cases PASS на каждом из SQLite, PostgreSQL16 и MySQL8.4** через настоящий leader cleanup method и SQL. Interleaving вставлен перед DELETE на cleanup connection, это не независимые writer processes. Existing age/continuity/tombstone controls сохранены. UP-ISSUE-2270 закрыт локально; F-071 исправлен.

### 45.2. Quarantine lifetime — existing fix проверен

**9 actual HTTP/WebSocket completions** на v1/slash/backend сохраняют initial failure во время settlement, quarantine replacement session и pruned/recreated entry. Global monotonic numbering, owner и early local cutoff уже корректны; дополнительная runtime правка quarantine не требовалась. Existing recovery/poison/local-strike controls PASS. UP-ISSUE-2268 закрыт локально по stale-clear ownership scope. Existing overflow tradeoff остаётся прежним: active poison может превышать nominal cap, weaker entries evictable; новая unconditional bound policy не утверждается.

### 45.3. Paused delivery — исправлены buffer и iterator ownership

3 unit red-before показали cancelled putter leak, отсутствие terminal после stall и CancelledError на closed sentinel. Actual ASGI send cancellation на трёх routes оставляла buffered bytes; после outer close canonical/slash ещё оставляли reserved rows до позднего GC, что устранило explicit nested bridge close. Queue.shutdown освобождает detached payloads и будит producers; producer cancellation продолжает распространяться. Resumed consumer получает ordered output или одну downstream failure после accepted prefix. None завершает очередь без ожидания slot и без подмены принятого success. Fixed5s delivery maximum ограничивается также idle/deadline и не сокращает model idle gap при свободной очереди.

Actual pause/resume, stall, cancellation и writer-error cases дают queued_bytes=0, pressure=0, reservations released/finalized и account active. Repeated cancellation ждёт generator cleanup перед propagation. UP-ISSUE-2266 закрыт локально в per-stream HTTP bridge scope; F-072/F-073 исправлены. Existing lone oversized event exception, process-wide RSS, aggregate replay spool и native-helper buffers отдельно.

### 45.4. Проверки и учёт

- Final new/existing queue+delivery selection: **82 passed**, no skips/failures (39 new cases).
- Existing quarantine/cleanup/detach/terminal selection: **91 passed**, 2538 deselected; команды scoped, не full-repository aggregate.
- PostgreSQL16 и MySQL8.4: **12 passed** на каждом; первоначальный connection-refused setup после выхода disposable containers не учитывается как зелёный прогон. После restart/readiness final tests PASS; test containers удалены.
- Scoped Ruff/check-format и ty, architecture/cancellation/timing/settings/simplicity gates PASS. Strict OpenSpec change и **68/68** main specs PASS; normative blocks синхронизированы, context содержит ограничения/examples; verification и tasks завершены перед archive.
- Из **110** исходных dirty/untracked paths только repository, issues-check.md и owning spec/context являются intended overlaps; остальные **106 byte-identical**. Prior receipt fix сохранён, exploratory detach/API edits удалены; original context — byte prefix. [Fingerprints](openspec/changes/archive/2026-10-04-verify-bridge-cleanup-quarantine-backpressure/fingerprints.md).

Current source queue: **48 local closures, 7 partial, 242 НЕ ПРОВЕРЕНО из 297**. Исторические counts/sections сохранены; изменены ровно три existing source rows. Live providers/clients, public artifacts, production, exact-head cloud CI/review и F-045/CI-04 не закрываются этим пакетом.


## 46. UP-ISSUE-2483 / UP-ISSUE-1901 / UP-ISSUE-2291 — SQLite history, reports и transcript backlog

Дата: **2026-10-04, Europe/Kiev**. Ровно три исходно unchecked source rows; base `282ce147038ac53b72bca30d69c4ad9a9ac1b7cc`. [Verification](openspec/changes/archive/2026-10-04-verify-sqlite-history-reports-transcript/verification.md) содержит red-before, команды, mapping и ограничения.

- **2483 — исправлено и закрыто локально.** Negative LIMIT делал SQLite read неограниченным; bool/string принимались, float давал database error. Все четыре malformed caps теперь отклоняются до backend selection. 100 000 history rows дают 1 280 snapshots на 20 accounts; primary/secondary, tighter cutoffs, timestamp/ID ties, zero cap и recent-floor exemptions проверены. Реальный dashboard capped/uncapped parity PASS.
- **1901 — existing fix проверен и закрыт локально.** Actual public reports route на 543 000 valid speed samples: raw 21.416 с, folded 7.811 с, cache 0.015 с. Summary/daily/filter outputs и medians совпадают. Исходное millis promise исправлено: exact short-window medians продолжают читать retained raw evidence. ARM/live production timing отдельно.
- **2291 — existing fix проверен и закрыт локально.** Ten bounded writes для 320-event burst, fair opportunities competing operations, refusal/exception isolation и один initial wait. Real SQLite rows_v1/chunks_v2 сохраняют ordered 320 events + один completed terminal; stale owner epoch не пишет. Shutdown/overflow/terminal regressions PASS.

Новые cases: **29 PASS** (27 combined + 2 real persistence). Focused new/existing selection: **39 PASS**; existing batcher/report/rollup selection: **43 PASS**. Counts overlapping, не full-repository aggregate. Ruff/format, scoped types, architecture/cancellation/timing/settings/simplicity и strict OpenSpec подтверждаются verification. Ровно три source rows получили explicit closure; related source rows не закрываются автоматически. Предыдущие dirty изменения не входят в коммит этого пакета. Public/cloud/provider/production/platform limitations сохранены.

Финальная проверка дерева публикации (HEAD + только этот пакет): **81 passed**, no skips/failures, 108.22 с. Повторные dense report timings: **21.372 с raw / 7.855 с folded / 0.013 с cached**. Code/test bytes соответствуют проверенному дереву. OpenSpec archived после проверки и sync.


## 47. Публикация всех оставшихся прошлых изменений — 2026-10-04

Прямой запрос пользователя: «закомить прошлые изменения тоже». Parent `8f713d322e7d61102092cc379506d38429b9fc58`; fork main проверен перед действием. Все **125** remaining paths совпадают с прежним preservation manifest. Публикуются восемь пакетов §§37–41/43–45 вместе с их существующими статусами и evidence; уже опубликованные результаты §46 сохраняются.

[Точная свежая проверка и список пакетов](openspec/changes/archive/2026-10-04-verify-sqlite-history-reports-transcript/prior-changes-publication.md). Scoped Ruff/format (46 Python files), ty (21 app files), architecture/cancellation/timing/settings/topology/simplicity, strict OpenSpec 68/68 и Rust 25 tests PASS. Fresh Python: **554 distinct targeted tests PASS** (294 unit + 141 integration A + 119 integration B), no skips/failures. Native wire probes выполнены с freshly built helper; exact commands/timings/hash — в publication evidence. Новых runtime правок при публикации нет.

UP-ISSUE-2471 / 1208 / 2271 остаются частичными, F-045/CI-04 и существующая native aggregate instability не объявляются закрытыми. Исторические counts и записи «commit/push не выполнялись» описывают свои прежние локальные этапы. Этот этап добавляет commit/push в fork main, без release/deploy/cloud claims.

## 48. UP-ISSUE-2389 / UP-ISSUE-2388 / UP-ISSUE-2033 — continuity, local refusals и terminal settlement

Дата: **2026-10-04, Europe/Kiev**. Base `94c9a8c24cc0dfdd4c5bce00aa1c46e6bc9d9b6d`, исходное дерево чистое. Ровно три source rows, исходно НЕ ПРОВЕРЕНО. [Verification](openspec/changes/archive/2026-10-04-repair-bridge-refusal-transition-terminal/verification.md), [per-site audit](openspec/changes/archive/2026-10-04-repair-bridge-refusal-transition-terminal/refusal-audit.md), [baseline control](openspec/changes/archive/2026-10-04-repair-bridge-refusal-transition-terminal/baseline.md).

- **2389 — existing fix проверен, закрыто локально.** Реальный sticky owner conflict в LoadBalancer и durable coordinator создаёт child на другом разрешённом аккаунте. Сохранённый turn-state на следующем ходе с reasoning history разрешается в тот же child; повторный fork/connect отсутствует. Три ingress variants; protected aliases, rollback, cancellation и second-conflict guards сохранены.
- **2388 — исправлено, закрыто локально.** 14 доказуемых pre-dispatch branches получают local provenance; 27 candidate contexts разобраны отдельно. 40 submission/startup cases, 16 compatibility/metadata cases, 6 durable claim/renew failures и 5 marker controls. Native до/после commitment и signed internal forwarding доставляют статус/код либо один terminal+DONE. Continuation не получает raw-HTTP replay permission; actual loopback send count, SQLite reservations и cleanup проверены. Исторический literal empty-body symptom не заявлен как воспроизведённый для каждого текущего producer.
- **2033 — exception containment подтверждён, settlement ordering исправлен, закрыто локально.** Unanchored keyed health write мог стартовать до commit settlement. Shared helper теперь ждёт settlement при pending error-health. 18 route cases читают actual terminal reservation state до injected health failure; клиент получает один исходный terminal, failure логируется один раз. Existing disconnect/cancellation controls PASS.

Final new selection: **88 passed**, no skips/failures, 125.81 с. Existing targeted selections: **36 passed** и **25 passed**, no skips/failures; это не полная suite. Baseline runtime negative control: **24 failed, 6 passed**; все шесть code files затем восстановлены byte-identical. Scoped Ruff/format, ty, architecture/cancellation/timing/settings/simplicity PASS. Strict change validation и **68/68** main specs PASS. Три normative blocks и stable context синхронизированы; [fingerprints](openspec/changes/archive/2026-10-04-repair-bridge-refusal-transition-terminal/fingerprints.md) фиксируют проверенные runtime/test bytes.

Current source queue: **54 local closures, 7 partial, 236 НЕ ПРОВЕРЕНО из 297**. Из existing source rows изменены только выбранные три; related PR rows не закрываются автоматически. OpenSpec change проверен и архивирован. Live clients/providers, PostgreSQL/MySQL runtime, distributed races, cloud gates, public artifacts и production остаются внешними scope. F-045/CI-04 и прежние partial statuses сохранены. На этапе реализации commit/push/release/deploy не выполнялись. Последующий прямой запрос пользователя разрешает локальный коммит этой тройки в `main`; push/release/deploy не запрошены.


## 49. Repair failed fork CI runs — 2026-10-04

User request: inspect the screenshot commits, fix failures, create a new commit and observe fully successful CI. Base e03f212a1; published fork main 94c9a8c24. Historical exact-SHA runs and primary jobs are recorded in [verification](openspec/changes/archive/2026-10-04-repair-fork-ci-regressions/verification.md).

Reproduced five route/WebSocket regression failures, 75 complete ty diagnostics and native zstd-as-JSON parsing. Repairs preserve explicit capability policy, authored terminal metadata and no-replay/ownership assertions. Core shard timeout increases from 20 to 40 minutes; full partition, per-test watchdogs and mandatory aggregates remain intact. Windows historical WinError32 cleanup failed after readiness/assets passed; two newer runs succeeded with the same launcher, so current cloud smoke remains required.

Local verification: 13, 98, 237 and 364 targeted cases PASS; full ty and Ruff/format, static architecture/cancellation/timing/settings/topology/simplicity checks and strict OpenSpec 68/68 PASS. Native wire selection uses the real freshly built helper and has no skips. These local results do not close cloud CI-01 yet.

CI-01: VERIFIED / CLOSED for published source 575c18f4e55ab1138086523cc81edf00c03bfb4b. CI run 37224667796 attempt 1 completed successfully with all 29 jobs, all core shards and CI Required. Windows, release guards and simplicity budgets for the same SHA also passed. Source queue and prior task statuses remain unchanged; F-045/CI-04 and other external residuals are not closed by assumption. A documentation-only follow-up records this evidence and archives the verified change; its final main-push checks are observed separately before reporting completion.

## 50. HTTP phase provenance, native fallback и post-output health

Ровно три выбранных пункта: UP-ISSUE-2169, UP-ISSUE-2108, UP-ISSUE-2074. Исходный clean local/fork main SHA — `1edc716c5366d49ce95df00c57025871d237377c`. HTTP consumer теперь исключает keepalive/comment и локальные SSE события из upstream фаз, сохраняя реальный upstream error с local response ID и наблюдённый zero. Сохранены lazy/verbatim forwarding, existing metrics labels и post-admission anchor.

Native SSE/compact existing refusal fixture подтверждён real helper (6/6), post-output bridge semantics — real WebSocket/HTTP (18/18) с health/no-replay/eventless controls. Старое противоречащее eventless-only нормативное требование удалено. Основной focused run 132 PASS; final provenance/optional-metrics selection 30 PASS; unit selector 38 PASS. Эти counts частично перекрываются. Полные команды, red-before и limitations — в [verification](openspec/changes/archive/2026-10-04-repair-http-phase-and-drop-contracts/verification.md).

Каждая из трёх собственных строк обновлена и reread. OpenSpec/code/context согласованы, strict main validation 68/68 PASS. Это локальные закрытия; новый SHA не объявлен cloud-green до полного exact-head GitHub CI. Native macOS, hosted-provider/production, F-045/CI-04 и release artifacts сохраняют свой отдельный scope.
