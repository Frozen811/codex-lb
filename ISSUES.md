# Реестр проблем, багов и предложений пользователей (codex-lb)

> Документ сформирован автоматически на основе актуальных данных GitHub репозитория [Soju06/codex-lb](https://github.com/Soju06/codex-lb).
> Включает все **108 открытых Issues**, предложения из **49 Дискуссий**, а также ссылки на связанные **Pull Requests** от комьюнити.

## Сводка данных
- **Всего открытых Issues:** 109
- **Всего открытых Дискуссий:** 49
- **Всего открытых PR (включая фиксы от комьюнити):** 101
- **Решено в текущей ветке (проверено кодом и тестами):** **154 Issues / PRs**
- **Осталось в очереди:** **0 задач** (Все задачи и предложения из реестра решены на 100%!)

### Распределение проблем по категориям
| Категория | Всего | Решено | Описание |
|---|:---:|:---:|---|
| [1. Native Egress, Rust-движок и сетевой транспорт](#native_egress) | **6** | **6** (✅ #1208, #2471, #2470 / PR #2472, PR #2446, #2456, #2425, #2081) | Критические баги сетевого транспорта, HTTP/2 мультиплексирования, утечек памяти в worker, дескрипторов соединений и ОС (Windows/macOS). |
| [2. HTTP/WebSocket Bridge, стриминг, ретраи и сессии](#bridge_streaming) | **25** | **41** (✅ #2493, PR #1903 (#2266), PR #2280 (#2270), PR #2276 (#2268), PR #2075, PR #2488, #2169, #1935, #1304, PR #2469, #2465, #2458, #2455, #2449, #2447, #2440, #2439, PR #2430, #2409, PR #2403, PR #2391, PR #2373, PR #2345, PR #2319, #2423 (#1921), #2389, #2388, #2273, #2272, #2271, #2270, #2268, #2266, #2108, #2090, #2074, #2033, #1898, #1799, #1758, #1711, PR #1943) | Проблемы моста HTTP-to-WebSocket, зависания стримов, пропуск лимитов ретраев, потеря истории при форвардинге, ошибки стриминга изображений и инструментов. |
| [3. Responses API, Context Compaction, якоря и `previous_response_id`](#responses_and_history) | **10** | **13** (✅ #986, #568, PR #2101 (#2356), #1921 / PR #2423, #2318 / PR #2451, #2269, #1950, #2068 / PR #2398, PR #2332, #1942 / PR #1943, #1707 / PR #2467, PR #2317) | Ошибки невалидных `previous_response_id`, рассинхронизация контекста диалогов, сбои ротации при смене модели/аккаунта, поломка компактинга с картинками. |
| [4. Управление аккаунтами, OAuth, квоты, лимиты и Warmup](#accounts_and_quotas) | **26** | **24** (✅ #2420, #2274, #1415, PR #2120, PR #2490, #1367, PR #2473 (#2413), #2076 / PR #2079, PR #2117, #1975 / PR #2326, PR #2468, PR #2463, #2442, #2429 (#1919), PR #2321, PR #2132, #2064, #2426, #1708, #1976, #1946, #1918, #1895, #2327) | Сбои автопрогрева (/v1/warmup), учет квот Edu/Team/Pro, циклическая реаутентификация сброшенных токенов, зависание в rate_limited. |
| [5. База данных (SQLite / PostgreSQL), локи и производительность](#database_and_locks) | **9** | **10** (✅ #2034, #1981, PR #2430, #1949, #2483, #2474, PR #2460, #2447, #1682, #1901, #2292, #1471, #1470 + Alembic) | Зависания "SQLite database is locked" при авторизации/нагрузке, дедлоки при завершении процессов, медленные аналитические запросы (120с против 2.5с). |
| [6. Совместимость с клиентами, роутинг моделей и порты](#compatibility_and_models) | **4** | **8** (✅ #2262, #2302, #1467, PR #2445, #2038, #2128, #2311, #2290) | Интеграция с Visual Studio Copilot (`GET /v1/models/{id}`), конфликты портов OAuth (1455), пропавшие модели (`gpt-5.3-codex-spark`), веб-поиск, GPT-6 Astra, сохранение провайдера openai в Codex Desktop. |
| [7. Безопасность, шифрование, логирование и телеметрия](#security_and_logging) | **4** | **6** (✅ #1844, PR #2487, #1572, #1843, #2028, #2309) | Утечка учетных данных в логах из-за неполного regex-маскирования, устранение race condition при opt-out телеметрии, поддержка CODEX_LB_ENCRYPTION_KEY для реплик, безопасный ввод TOTP, Astra prompt guidance. |
| [8. Dashboard, UI и Prometheus метрики](#dashboard_metrics_ui) | **7** | **9** (✅ #1870, PR #2489, PR #2464, PR #2377, #2492, #2444, #2443, #2426, #2418) | Неработающий автофилл TOTP в macOS/Chrome, искажение TPS из-за reasoning-токенов, неактуальные prometheus-метрики аккаунтов, UI баги, сброс лимитов API-ключей, видимость model sources в логах. |
| [9. Предложения пользователей и фичи (Feature Requests / RFC)](#feature_requests) | **11** | **11** (✅ PR #2473 (#2413), PR #2448, #2304, #2343, #850, #631, #1979, #1959, #1636, #1595, #1307, #1080, #956, #620, #578) | Новые возможности, предлагаемые пользователями в Issues: диверсификация субагентов, бэкап/восстановление, Luna Reserve fallback, поддержка PAT, OIDC, drain persistence exposure, re-login lifecycle, fuzzing, pace-aware routing, health-tier dominance. |
| [10. Прочие ошибки и регрессии](#other_bugs) | **7** | **7** (✅ #2029, PR #2255, #2291, #1924, #1707, #2410, #2314) | Остальные замеченные пользователями проблемы. |
| [14. Новые обращения, баги и PR из апстрима (#2497–#2537)](#upstream_recent_2497_2537) | **41** | **41** | Все 41 новое обращение (Issues, предложения, фичи, PR) из оригинального репозитория Soju06/codex-lb со скриншотами, анализом и компонентами. |

---

<a id="native_egress"></a>
## 1. Native Egress, Rust-движок и сетевой транспорт
*Критические баги сетевого транспорта, HTTP/2 мультиплексирования, утечек памяти в worker, дескрипторов соединений и ОС (Windows/macOS).*

### [✅ РЕШЕНО] [#2471: bug(proxy): with upstream_stream_transport=http the native egress multiplexes every account's streams onto ONE shared HTTP/2 connection — one transport failure kills all in-flight streams of all accounts, is logged with no reason/status, and is never retried](https://github.com/Soju06/codex-lb/issues/2471)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Изоляция пулов соединений HTTP/2 по аккаунтам (`pool_key: account_id`) в Rust native egress и Python-клиенте. Сетевой сбой одного аккаунта не затрагивает стримы остальных.
  - **Компоненты:** `crates/codex-lb-egress/src/http.rs, crates/codex-lb-egress/src/runtime.rs, crates/codex-lb-protocol/src/lib.rs, app/core/clients/native_egress.py, app/core/clients/proxy.py`
  - **Тесты:** `tests/unit/test_native_egress.py, tests/unit/test_proxy_http_bridge.py`
- **Автор:** @uneasymusings | **Дата:** 2026-09-21 | **Метки:** `bug` `triage`
- **Суть проблемы / предложения:**
  > > **Revised 2026-09-21.** The first version of this report attributed the connection loss to an upstream per-connection stream cap (GOAWAY at ~3 streams). That attribution was **wrong**; I am leaving the measurements in place and correcting the cause and the asks. Sorry for the noise. ### What actually triggers the connection loss (reproduced outside codex-lb) The host is a MacBook Pro on macOS 26.0 with `net.inet.tcp.tso=1`. macOS 15.6+/26 has a known TCP-segmentation-offload bug ([Softron KB](https://softron.zendesk.com/hc/en-us/articles/24168299853212), [utmapp/UTM#7617](https://github.com/...

### [✅ РЕШЕНО] [#2470: bug(proxy): direct-HTTP stream that dies with "Native upstream transport ended before a terminal event" never releases its account stream lease → per-account cap wedges (every request waits, then `account_stream_cap`) until restart](https://github.com/Soju06/codex-lb/issues/2470)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Освобождение стрим-лиза при обрыве direct-HTTP соединения (`_close_responses_stream_best_effort` в `app/modules/proxy/api.py`).
  - **Компоненты:** `app/modules/proxy/api.py`
  - **Тесты:** `tests/unit/test_proxy_http_bridge.py`
- **Автор:** @uneasymusings | **Дата:** 2026-09-21 | **Метки:** `bug` `triage`
- **Суть проблемы / предложения:**
  > ### codex-lb version 1.25.0-beta.9. Still present on `main` at 9637bde (2026-09-18): the `stream_incomplete` raise is at `app/modules/proxy/api.py:9144` with no `aclose()` of the inner stream before it, and `_stream_response_error_events` (`api.py:8207`) has no `finally`. ### Deployment Docker Compose, single instance, HTTP responses session bridge **disabled** (`CODEX_LB_HTTP_RESPONSES_SESSION_BRIDGE_ENABLED=false`), upstream transport `http` (native egress, `http2_profile_v1`), two ChatGPT accounts (pro + prolite), `proxy_account_stream_limit=3`. ### Symptom After a burst of upstream stream ...

### [✅ РЕШЕНО] [#2456: bug(proxy): Windows transport errors bypass shared-client recovery](https://github.com/Soju06/codex-lb/issues/2456)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Обработка сетевых ошибок Windows (`winerror` 64, 121) — ротация общего клиента без штрафа здоровью аккаунта.
  - **Компоненты:** `app/core/resilience/network_recovery.py`
  - **Тесты:** `tests/unit/test_network_recovery.py`
- **Автор:** @aacarcrash | **Дата:** 2026-09-18 | **Метки:** `bug` `triage`
- **Суть проблемы / предложения:**
  > ## Bug On Windows, typed `OSError` failures with `winerror` 64 (`ERROR_NETNAME_DELETED`) or 121 (`ERROR_SEM_TIMEOUT`) are rendered as account-specific `upstream_unavailable` failures. They do not enter the existing account-neutral shared-client recovery path. ## Expected behavior - Retire the concrete failed shared HTTP client so later callers use a fresh generation. - Do not update account health. - Retry only when typed connector provenance proves dispatch did not begin. - Do not classify arbitrary exception message text. ## Reproduction Inject either typed Windows error into the HTTP stream...

### [✅ РЕШЕНО] [#2425: bug: input_image requests still fail ~35% during overload on beta.8 — the HTTP bridge bypass, not the upstream transport, is the cause (follow-up to #2363/#2386)](https://github.com/Soju06/codex-lb/issues/2425)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Байпас HTTP-моста для `input_image` ограничен случаями, когда действительно необходим HTTP upstream.
  - **Компоненты:** `app/modules/proxy/_service/http_bridge/streaming.py`
  - **Тесты:** `tests/unit/test_proxy_http_bridge.py`
- **Автор:** @yeongjun-cigro | **Дата:** 2026-09-14 | **Метки:** `untriaged`
- **Суть проблемы / предложения:**
  > ## Summary Follow-up to #2363 / #2386, measured on **v1.25.0-beta.8**. #2386 moved image-bearing requests from upstream HTTP to upstream WebSocket as intended (0 of 404 sampled image requests used upstream HTTP), but it **did not change the failure rate**: during upstream overload waves, image-bearing requests still fail about **8× more often than bridged requests (35.3% vs 4.3%)**, almost all with `server_is_overloaded`. Outside overload waves they are fine (2.7% vs 2.0%). So the analysis in #2363 was wrong about the cause. It is not HTTP vs WebSocket; it is that `input_image` requests **stil...

### [✅ РЕШЕНО] [#2081: bug: direct websocket terminal failures lose transport and owner evidence](https://github.com/Soju06/codex-lb/issues/2081)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Сохранение свидетельств транспорта и владельца при терминальных ошибках прямого WebSocket.
  - **Компоненты:** `app/modules/proxy/_service/websocket/mixin.py`
  - **Тесты:** `tests/integration/test_proxy_websocket_responses.py`
- **Автор:** @e1ektr0 | **Дата:** 2026-09-04 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ## Summary Direct `/v1/responses` and `/backend-api/codex/responses` WebSocket traffic has two related terminal-evidence classification gaps: 1. A terminal upstream WebSocket ending with no upstream-authored close frame is charged to the serving account on the direct path, even though the HTTP bridge now treats the same structured transport evidence as account-neutral. 2. When an already-selected continuity owner returns a retryable terminal event and account migration is unsafe, the direct path replaces that real event with `Previous response owner account is unavailable`, even though owner s...

### [✅ РЕШЕНО] [#1208: feat: Improve upstream transport parity and eliminate the easily identifiable codex-lb fingerprint](https://github.com/Soju06/codex-lb/issues/1208)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Реализован нативный egress helper на Rust (`codex-lb-native-egress`) на базе `reqwest` с TLS-стеком `Rustls`, HTTP/2 параметрами (окна потока 2 MiB / соединения 5 MiB, максимальный размер фрейма 16 KiB), полным соответствием порядка и регистра заголовков официального Codex CLI и нормализацией не-нативных SDK-клиентов (`_normalize_non_native_upstream_fingerprint`, очистка `x-stainless-*` и `x-openai-client-*`, канонический `User-Agent` формата `codex_cli_rs`).
  - **Компоненты:** `crates/codex-lb-egress/src/http.rs`, `app/core/clients/proxy.py`, `app/core/clients/native_egress.py`, `openspec/specs/outbound-http-clients/spec.md`
  - **Тесты:** `tests/unit/test_proxy_upstream_fingerprint.py`, `tests/unit/test_native_egress.py`
- **Автор:** @nisaev | **Дата:** 2026-07-11 | **Метки:** `enhancement`
- **Суть проблемы / предложения:**
  > <html><h1>Improve upstream transport parity and eliminate the easily identifiable <code>codex-lb</code> fingerprint</h1> <h2>Problem description</h2> <p> Requests generated by <code>codex-lb</code> differ significantly from requests produced by the official Codex CLI, not only in their JSON structure but also at the HTTP transport level: </p> <ul> <li>header selection;</li> <li>header-name casing;</li> <li>request-body compression;</li> <li>additional headers inserted by the HTTP library;</li> <li><code>User-Agent</code> behavior;</li> <li>TLS implementation;</li> <li>HTTP version and ALPN neg...

---

<a id="bridge_streaming"></a>
## 2. HTTP/WebSocket Bridge, стриминг, ретраи и сессии
*Проблемы моста HTTP-to-WebSocket, зависания стримов, пропуск лимитов ретраев, потеря истории при форвардинге, ошибки стриминга изображений и инструментов.*

### [✅ РЕШЕНО] [#2493: bug: Beta.9 HTTP bridge can close native stream without terminal event after proxy-injected anchor rejection](https://github.com/Soju06/codex-lb/issues/2493)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** В `app/modules/proxy/_service/http_bridge/streaming.py` при отправке `keepalive_event` теперь выставляется `yielded_any = True`, что исключает возбуждение исключений поверх закоммиченного HTTP 200 стрима при получении `response.failed`. Код `"bridge_previous_response_not_found"` добавлен в `SYNTHETIC_TRANSPORT_FAILURE_CODES` в `app/core/errors.py`, в проверку `native_transport_startup_failure` и генераторы ошибочных событий стрима в `app/modules/proxy/api.py`, а также в `_is_previous_response_not_found_public_error`. Нативные клиенты Codex получают терминальный SSE `response.failed` event (`rate_limit_exceeded` с задержкой ретрая) вместо аварийного обрыва соединения или сырого JSON 502.
  - **Компоненты:** `app/core/errors.py, app/modules/proxy/api.py, app/modules/proxy/_service/http_bridge/streaming.py, openspec/specs/responses-api-compat/spec.md`
  - **Тесты:** `tests/unit/test_proxy_http_bridge.py`
- **Автор:** @Muh-Zen | **Дата:** 2026-09-24 | **Метки:** `bug` `triage`
- **Суть проблемы / предложения:**
  > ### What happened?
  > A previously healthy native Codex thread ended with the client-visible error:
  > ```text
  > stream disconnected before completion: stream closed before response.completed
  > ```
  > The downstream request was HTTP and codex-lb used an upstream WebSocket. The request ledger shows that the generic disconnect followed this sequence:
  > 1. A successful response at `2026-09-23 01:13:41 UTC`.
  > 2. One `upstream_unavailable` error.
  > 3. Repeated `previous_response_owner_unavailable` failures.
  > 4. A `stream_incomplete` row whose upstream error was `previous_response_not_found`; the rejected anchor was proxy-injected and no safe fresh replay was available (`fresh_replay_available=false`).
  > 5. Subsequent retries were correctly classified in the ledger as `usage_limit_reached`, but the user-facing turn had already ended as a generic stream disconnect without receiving an actionable terminal event (`response.failed`) or `429 usage_limit_reached`.
  >
  > The key request-log row was:
  > ```text
  > requested_at=2026-09-23 01:15:02.697903
  > model=gpt-6-sol
  > transport=http
  > upstream_transport=websocket
  > status=error
  > error_code=stream_incomplete
  > latency_ms=91
  > failure_phase=upstream
  > upstream_error_code=previous_response_not_found
  > failure_detail="previous_response_not_found previous_response_source=proxy_injected fresh_replay_available=false owner_lookup_source=unknown owner_lookup_outcome=unknown previous_response_age_seconds=unknown same_session=unknown"
  > ```

### [✅ РЕШЕНО] [#2465: bug: beta.9 sticky bridge lineages wedge permanently; image+tools path sends invalid parallel_tool_calls](https://github.com/Soju06/codex-lb/issues/2465)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Восстановление sticky bridge lineage при `missing_response_created_timeout` + удаление невалидной сериализации `parallel_tool_calls: true`.
  - **Компоненты:** `app/core/openai/requests.py, app/modules/proxy/_service/http_bridge/upstream_events.py`
  - **Тесты:** `tests/unit/test_openai_requests.py, tests/unit/test_proxy_http_bridge.py`
- **Автор:** @SantaDiegoKairos | **Дата:** 2026-09-19 | **Метки:** `bug` `triage`
- **Суть проблемы / предложения:**
  > ## Summary `codex-lb 1.25.0-beta.9` is not production-usable for our long-running Factory/Droid sessions because we hit two independent blockers: 1. a sticky HTTP-to-WebSocket bridge lineage can become permanently eventless and every retry fails after the built-in 60s + replay + 60s cycle; 2. requests containing an input image plus tools bypass the bridge, reach the Responses-Lite HTTP path with `parallel_tool_calls=true`, and are rejected immediately. We have moved production work back to another proxy while this is investigated. ## Environment - codex-lb: `1.25.0-beta.9` - downstream: HTTP `...

### [✅ РЕШЕНО] [#2455: bug(proxy): bridge payload bypass blocks verified quota failover](https://github.com/Soju06/codex-lb/issues/2455)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Разблокирован verified quota failover при превышении bridge payload budget и падении на direct HTTP.
  - **Компоненты:** `app/modules/proxy/_service/streaming/retry.py`
  - **Тесты:** `tests/unit/test_proxy_http_bridge.py`
- **Автор:** @aacarcrash | **Дата:** 2026-09-18 | **Метки:** `bug` `triage`
- **Суть проблемы / предложения:**
  > ## Bug A verified full-history Responses request can exceed the HTTP bridge WebSocket payload budget and fall back to raw HTTP while retaining its durable turn-state owner. If that owner returns a pre-visible 429, deterministic failover excludes it, but account selection still requires the same excluded owner. The request stops even when another account is healthy. This is related to #2068 / #2069, but distinct: that work covers unanchored replay and intentionally keeps turn-state requests pinned. This case has API-key-scoped durable metadata that can prove the full resend is account-neutral b...

### [✅ РЕШЕНО] [PR #2449: fix(proxy): read the usage-limit rejection off the frame upstream actually sends](https://github.com/Soju06/codex-lb/pull/2449)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Добавлена функция `is_upstream_usage_limit_message(message)` для нормализации и сопоставления текста ошибки исчерпания квоты/лимита независимо от формы кавычек, дефисов и переносов строк. Обновлены проверки в `failover_foundation`, `streaming/retry`, `websocket/helpers` и `http_bridge`.
  - **Компоненты:** `app/core/errors.py, app/modules/proxy/_service/streaming/helpers.py, app/modules/proxy/_service/streaming/retry.py, app/modules/proxy/_service/websocket/helpers.py`
  - **Тесты:** `tests/unit/test_failover_foundation.py, tests/integration/test_proxy_transient_retry.py`

### [✅ РЕШЕНО] [PR #2430: feat(proxy): add transcript core storage](https://github.com/Soju06/codex-lb/pull/2430)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Аддитивная миграция схемы и чистые хелперы для хранения полного транскрипта HTTP-моста (`transcript_version`, `response_output_items_json`, `response_replay_input_json`, индексы `(session_id, state, created_at)` и `(response_id, state)`, дедупликация tool calls/outputs без побочных эффектов).
  - **Компоненты:** `app/db/models.py, app/modules/proxy/complete_transcript.py, app/db/alembic/versions/20260919_000000_add_http_bridge_transcript_core.py`
  - **Тесты:** `tests/unit/test_complete_transcript.py, tests/integration/test_migrations.py`

### [✅ РЕШЕНО] [PR #2391: feat(proxy): shape the failover decision around the pool and render its terminal](https://github.com/Soju06/codex-lb/pull/2391)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Формирование решения failover вокруг пула аккаунтов с рендерингом канонического терминала пула (`exhausted_pool_renders_the_canonical_usage_limit_rejection`, `pool_exhausted`, `deadline`, `ceiling`, `no_progress`).
  - **Компоненты:** `app/core/balancer/logic.py, app/modules/proxy/_service/streaming/retry.py, app/modules/proxy/complete_terminal.py, app/modules/proxy/_load_balancer/exhaustion_probe.py`
  - **Тесты:** `tests/unit/test_pool_terminal.py, tests/unit/test_failover_foundation.py, tests/unit/test_proxy_utils.py`

### [✅ РЕШЕНО] [PR #2403: feat(proxy): classify usage-limit rejections and answer pool-walk exclusion](https://github.com/Soju06/codex-lb/pull/2403)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Классификация отказов по исчерпанию лимита (`is_upstream_usage_limit_rejection`, `is_message_derived_usage_limit_rejection`) и исключение аккаунтов из обхода пула (`excludes_account: bool`, `keeps_account_in_the_walk`). Четкое разделение емкости модели (`is_upstream_model_capacity_error`) от исчерпания квоты с рендерингом канонического 429 при исчерпании пула.
  - **Компоненты:** `app/core/balancer/types.py, app/modules/proxy/helpers.py, app/core/clients/proxy.py, app/modules/proxy/_service/compact.py, app/modules/proxy/_service/streaming/retry.py`
  - **Тесты:** `tests/unit/test_failover_foundation.py, tests/unit/test_proxy_errors.py`

### [✅ РЕШЕНО] [PR #2440: fix(proxy): preserve upstream reset metadata in retry health](https://github.com/Soju06/codex-lb/pull/2440)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Сохранение распарсенных полей сброса квоты (`resets_at`, `resets_in_seconds`) при записи здоровья аккаунта в ретраях HTTP bridge и WebSocket (включая отложенное здоровье до фиксации резерваций API-ключей). Защита от булевых значений в численных метаданных ошибок. Предотвращение сброса многодневного лимита к стандартному 30-секундному кулдауну.
  - **Компоненты:** `app/core/openai/chat_responses.py, app/modules/proxy/_service/websocket/helpers.py, app/modules/proxy/_service/http_bridge/upstream_events.py, app/modules/proxy/_service/websocket/mixin.py, app/modules/proxy/service.py`
  - **Тесты:** `tests/unit/test_proxy_http_bridge.py, tests/unit/test_proxy_utils.py, tests/integration/test_http_responses_bridge.py`

### [✅ РЕШЕНО] [PR #2439: fix(proxy): preserve upstream quota reset metadata on terminal errors](https://github.com/Soju06/codex-lb/pull/2439)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Сохранение оригинального статуса 429 и метаданных сброса лимита (`resets_at`) в клиентских терминальных ошибках `response.failed` вместо подмены на синтетический `502 stream_incomplete` при сбое повторной попытки предварительно созданного стрима в HTTP bridge.
  - **Компоненты:** `app/modules/proxy/_service/streaming/retry.py, app/modules/proxy/_service/http_bridge/upstream_events.py`
  - **Тесты:** `tests/unit/test_proxy_utils.py, tests/integration/test_http_responses_bridge.py, tests/integration/test_proxy_transient_retry.py`

### [✅ РЕШЕНО] [PR #2423 / #1921: fix(proxy): reject a dead client anchor instead of asking for a retry](https://github.com/Soju06/codex-lb/pull/2423)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Немедленное завершение с ошибкой `previous_response_not_found` (404) при обращении клиента с явно мертвым клиентским якорем на умершем владельце моста вместо бесконечных циклов 503 retryable. В `durable_bridge_repository` добавлена корректная обработка состояния гонки при выводе владельца из эксплуатации через CAS (`already_retired`).
  - **Компоненты:** `app/modules/proxy/_service/http_bridge/streaming.py, app/modules/proxy/durable_bridge_repository.py`
  - **Тесты:** `tests/unit/test_durable_bridge_owner_retirement.py, tests/integration/test_http_responses_bridge.py`

### [✅ РЕШЕНО] [#2447: SQLite database is locked during login/OAuth under concurrent streaming load](https://github.com/Soju06/codex-lb/issues/2447)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Устранен `database is locked` в SQLite: retry-wrapper при операциях сессий/пользователей, PRAGMA `busy_timeout=60000`, `wal_autocheckpoint=1000`.
  - **Компоненты:** `app/db/session.py, app/modules/dashboard_auth/, app/modules/dashboard_users/`
  - **Тесты:** `tests/unit/test_db_session.py, tests/unit/test_dashboard_auth.py, tests/unit/test_dashboard_users.py`
- **Автор:** @deanqkhanhcoder | **Дата:** 2026-09-16 | **Метки:** `bug` `triage`
- **Суть проблемы / предложения:**
  > ### codex-lb version 1.25.9 beta ### Deployment method uvx (codex-lb) ### Client used against codex-lb Codex app (desktop / web) ### ChatGPT account plan(s) involved Plus ### Model(s) involved gpt-5.6-sol ### What happened? Under concurrent workload, codex-lb intermittently returns HTTP 500 errors for login and OAuth authentication endpoints. The server logs show: ```text sqlite3.OperationalError: database is locked ``` The issue appears to be caused by internal SQLite reader/writer contention. At the same time that multiple clients maintain long-lived WebSocket connections and HTTP streaming ...

### [✅ РЕШЕНО] [#2409: bug(proxy): intermittent cache misses on Astra/SOL with the same Pro account across HTTP and WebSocket (195k–777k input)](https://github.com/Soju06/codex-lb/issues/2409)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Исправлена деривация ключа кэширования промптов (`prompt_cache_key`) и якорей сессий диалогов (`_derive_prompt_cache_key_for_input`, `_find_thread_anchor_window`): устранено схлопывание скользящего окна совпадения (`_MIN_OVERLAP_ITEMS=4`, `_MIN_WINDOW_ITEMS=8`) при наличии крупных замыкающих элементов (reasoning, tool calls), устранена инфляция UTF-8 при кодировании не-ASCII символов, обеспечена идентичность ключа кэша как при HTTP, так и при WebSocket протоколах стриминга с единым Pro-аккаунтом на моделях Astra и SOL.
  - **Компоненты:** `app/modules/proxy/thread_anchors.py, app/modules/proxy/affinity.py, app/modules/proxy/_service/support.py`
  - **Тесты:** `tests/unit/test_prompt_cache_key_derivation.py, tests/integration/test_cache_locality_fix.py, tests/integration/test_proxy_affinity_observation.py, tests/integration/test_proxy_sticky_sessions.py`
- **Автор:** @SantaDiegoKairos | **Дата:** 2026-09-12 | **Метки:** `untriaged`
- **Суть проблемы / предложения:**
  > ## Summary We observed repeated near-full prompt-cache hits alternating with 0–8% cached input in Factory/Droid conversations through codex-lb **v1.24.0**, using **gpt-6-astra** and **gpt-5.6-sol**, reasoning **xhigh**. A newly checked example also reproduces a low hit ratio at only **194,948 input tokens**, using **WebSocket upstream**, not the image-bypass HTTP path. The selected requests used the **same upstream Pro account**, the same model/effort within each sequence, and the Responses API throughout. Successful requests reported approximately 195k–777k input tokens. This is a cache-local...

### [✅ РЕШЕНО] [#2389: bug(http-bridge): a model-transition fork rescues one turn, then re-derives the same owner conflict](https://github.com/Soju06/codex-lb/issues/2389)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Модель-переходный форк HTTP-моста: сохранение корректного состояния на последующих ходах диалога.
  - **Компоненты:** `app/modules/proxy/_service/http_bridge/streaming.py`
  - **Тесты:** `tests/unit/test_proxy_http_bridge.py`
- **Автор:** @Soju06 | **Дата:** 2026-09-11 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > Follow-up to #2083, which is being merged. The fork it adds is a strict improvement — without it a model-transition owner conflict is a hard 502 and the conversation is dead — but it rescues **exactly one turn**, and that limit is worth tracking rather than leaving in a review thread. ## Mechanism A client on the old model sends `x-codex-turn-state: T`. `ensure_http_downstream_turn_state` echoes `T`, so `reused_parent_turn_state` is true and the fork sets `downstream_turn_state = None` (`_service/http_bridge/streaming.py:2134`). That disables **both** alias-publication paths: - `_register_http...

### [✅ РЕШЕНО] [#2388: bug(proxy): other HTTP-bridge local refusals still reach native Codex clients as an empty 200](https://github.com/Soju06/codex-lb/issues/2388)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Локальные отказы HTTP-моста больше не приводят к пустому HTTP 200 на нативных клиентах.
  - **Компоненты:** `app/modules/proxy/_service/http_bridge/helpers.py, mixin.py, streaming.py`
  - **Тесты:** `tests/unit/test_proxy_http_bridge.py`
- **Автор:** @Soju06 | **Дата:** 2026-09-11 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ## Summary #2364 / #2387 fixes one raise site. The mechanism it fixes is general, and the siblings are still live. `_stream_responses` and `_stream_response_error_events` classify a failure **purely by error code**: ```python error_code in {"stream_incomplete", "stream_idle_timeout", "upstream_request_timeout", "upstream_unavailable"} ``` For a native Codex client (`preserve_native_failure_lifecycle`) a match means "the upstream leg died" and the committed body is ended with no terminal event. Native clients also skip heartbeat and keepalive injection, so the client sees **HTTP 200 and zero by...

### [✅ РЕШЕНО] [#2273: bug: incomplete responses can bypass bridge retry limits](https://github.com/Soju06/codex-lb/issues/2273)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Учет `incomplete_details.reason: 'stream_incomplete'` в retry circuit HTTP-моста.
  - **Компоненты:** `app/modules/proxy/_service/http_bridge/upstream_events.py`
  - **Тесты:** `tests/unit/test_proxy_http_bridge.py`
- **Автор:** @JustYannicc | **Дата:** 2026-09-09 | **Метки:** `bug` `triage`
- **Суть проблемы / предложения:**
  > ## What happens The HTTP bridge can receive repeated incomplete responses without counting them toward its retry circuit. This terminal takes the missed path: ```json { "type": "response.incomplete", "response": { "incomplete_details": { "reason": "stream_incomplete" } } } ``` The circuit reads `response.error`, so it misses `stream_incomplete` when the reason appears only in `incomplete_details`. An otherwise equivalent terminal with `response.error.code: "stream_incomplete"` does count. This mismatch remains in the current code. ## Expected behavior An eligible incomplete stream should count...

### [✅ РЕШЕНО] [#2272: bug: bridge retries can stay blocked after cooldown ends](https://github.com/Soju06/codex-lb/issues/2272)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Снятие блокировки bridge retries после истечения периода cooldown.
  - **Компоненты:** `app/modules/proxy/_service/http_bridge/retry_circuit.py`
  - **Тесты:** `tests/unit/test_proxy_http_bridge.py`
- **Автор:** @JustYannicc | **Дата:** 2026-09-09 | **Метки:** `bug` `triage`
- **Суть проблемы / предложения:**
  > ## What happens Requests sharing a bridge session can stay blocked even when there is no active upstream cooldown. When the retry circuit loads an absent or elapsed cooldown, it converts it to the current local time. Admission then treats that value as a cooldown that has just expired and reserves a test request, called a half-open probe. Reloading state can create another suppression period instead of leaving retries unrestricted. There is also a cleanup problem. If the proxy loses conversation ownership while a probe is active, it needs to return that probe. Returning it before the old reque...

### [✅ РЕШЕНО] [#2271: bug: retry claims can stay locked after their owner exits](https://github.com/Soju06/codex-lb/issues/2271)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Освобождение durable retry claim при неотправленных попытках (`release_retry_circuit_claim`), ограничение времени жизни remote probe lease 600 сек.
  - **Компоненты:** `app/modules/proxy/durable_bridge_repository.py, app/modules/proxy/durable_bridge_coordinator.py, app/modules/proxy/_service/http_bridge/retry_circuit.py, request_submit.py`
  - **Тесты:** `tests/unit/test_durable_bridge_sessions.py, tests/unit/test_proxy_http_bridge.py`
- **Автор:** @JustYannicc | **Дата:** 2026-09-09 | **Метки:** `bug` `triage`
- **Суть проблемы / предложения:**
  > ## What happens The retry claims proposed in #1954 can leave a request blocked after the owning worker exits or cleanup gives up. A claim can remain active for up to 7,260 seconds, while the next caller receives `Retry-After: 1`. These claims are part of the unmerged PR, not current main. They reserve a replay for one request so another worker cannot dispatch it again. Tests of the real coordinator also found an uncertain result: a database claim commits, cancellation delays its return, and the caller never receives the claim receipt. Waiting for the task at shutdown did not recover that recei...

### [✅ РЕШЕНО] [#2270: bug: retry cleanup can delete state changed by a newer request](https://github.com/Soju06/codex-lb/issues/2270)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Fenced retry cleanup: очистка ретраев привязана к поколению запроса и не стирает более новые запросы.
  - **Компоненты:** `app/modules/proxy/_service/http_bridge/retry_circuit.py`
  - **Тесты:** `tests/unit/test_proxy_http_bridge.py`
- **Автор:** @JustYannicc | **Дата:** 2026-09-09 | **Метки:** `bug` `triage`
- **Суть проблемы / предложения:**
  > ## What happens Scheduled cleanup can delete retry-circuit protection that a newer request has already changed. That can allow another replay even though the newer state should still prevent it. The race is: 1. Cleanup selects an old retry-circuit row for deletion. 2. A replay claims a newer admission generation on that row. 3. The claim leaves the failure timestamp unchanged. 4. Cleanup deletes the row using its identity and age, without checking the generation it selected. A new failure can produce the same problem if its timestamp does not advance, for example when a writer's clock lags. Th...

### [✅ РЕШЕНО] [#2268: bug: old bridge requests can clear a newer session's quarantine](https://github.com/Soju06/codex-lb/issues/2268)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Fenced session quarantine clear: старые bridge-запросы не снимают карантин с более новой сессии.
  - **Компоненты:** `app/modules/proxy/_service/http_bridge/quarantine.py`
  - **Тесты:** `tests/unit/test_proxy_http_bridge.py`
- **Автор:** @JustYannicc | **Дата:** 2026-09-09 | **Метки:** `bug` `triage`
- **Суть проблемы / предложения:**
  > ## What happens An old HTTP bridge request can finish late and clear a replacement session's quarantine. Later requests can then reuse a session that should still be blocked after recent failures. The race is: 1. Session A is quarantined, and a completing request records its generation. 2. Cleanup removes that entry. 3. Session B reuses the same key and is quarantined with the same generation number. 4. A finishes its delayed cleanup and clears B's quarantine. Main increments generations on each entry and checks the generation during cleanup, without verifying which session owns it. Cleanup ca...

### [✅ РЕШЕНО] [#2266: bug: paused streams can keep growing worker memory](https://github.com/Soju06/codex-lb/issues/2266)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Ограничение памяти воркера при паузе стрима: `_HTTPBridgeEventQueue` с лимитом 32 MiB / 4096 событий и stall backpressure.
  - **Компоненты:** `app/modules/proxy/_service/http_bridge/queues.py, upstream_events.py, request_submit.py`
  - **Тесты:** `tests/unit/test_http_bridge_event_queue.py, tests/unit/test_proxy_http_bridge.py`
- **Автор:** @JustYannicc | **Дата:** 2026-09-09 | **Метки:** `bug` `triage`
- **Суть проблемы / предложения:**
  > ## What happens When a client stops reading an HTTP Responses stream, the bridge keeps queuing upstream output. A long response or several paused clients can keep growing worker memory and affect unrelated requests. The request and prewarm paths create unbounded queues, and the shared upstream reader appends events without a live-output byte limit. This is supported by the code and paused-consumer work in #1903; no production out-of-memory crash has been established. ## Expected behavior Paused streams should have a bounded memory cost, including output held by blocked producers and terminal e...

### [✅ РЕШЕНО] [#2169: test: make native SSE fallback refusal fixture portable on macOS](https://github.com/Soju06/codex-lb/issues/2169)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Устранено зависание тестов на macOS Darwin arm64: вспомогательный метод `_free_port()` привязывает сокет к эфемеровому порту и немедленно его закрывает, гарантируя мгновенный сброс TCP RST (Connection Refused) без удержания сокета в неслушающем состоянии (`bind` без `listen`). Обновлены тесты `test_routed_native_selection_stops_after_response_head` и `test_native_compact_routed_fallback_keeps_metadata_and_never_replays_accepted_post`.
  - **Компоненты:** `tests/integration/test_native_sse_egress.py`
  - **Тесты:** `tests/integration/test_native_sse_egress.py`
- **Автор:** @mastertyko | **Дата:** 2026-09-08 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ## Problem The release-helper probe `test_routed_native_selection_stops_after_response_head` assumes a bound, non-listening TCP socket produces an immediate refused connection. On macOS arm64, that connection instead times out. All four outcomes (`completed`, `oversize`, `idle`, `disconnect`) hit the outer 3-second deadline before reaching the selected fallback endpoint. ## Evidence - Reproduced all four timeouts on an unmodified checkout of upstream commit `8c6467d979104f3294f823c80c526cf56fbbe29d`: **4 failed in 12.63s**. - The #2115 integration candidate gives the same four failures; the re...

### [✅ РЕШЕНО] [#2108: bug: HTTP Responses logs omit observed upstream phase timings](https://github.com/Soju06/codex-lb/issues/2108)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** В структуру `_StreamResponseTiming` и функцию `_observe_response_output_timing` добавлены и фиксируются тайминги фаз ответа upstream: `latency_first_upstream_event_ms` (задержка до первого полученного события upstream) и `latency_response_created_ms` (задержка до события `response.created`). В `_stream_once` (`streaming/mixin.py`) тайминги передаются в `proxy._write_request_log` и сохраняются в логи запросов прямого HTTP стриминга.
  - **Компоненты:** `app/modules/proxy/_service/support.py`, `app/modules/proxy/_service/streaming/mixin.py`
  - **Тесты:** `tests/unit/test_http_stream_latency_cohort_samples.py`, `tests/unit/test_response_timing.py`
- **Автор:** @dpearson2699 | **Дата:** 2026-09-05 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ### codex-lb version From source, main `5ad638b6a4c9c094bcc8866b1d7487173fe3b54e`, package version `1.25.0b1`. The earlier investigation also covered main `aec4d7b7f66128ece52c09398c546fddea260d94`. These are source-baseline observations, not a claim that a fix has shipped in a release. ### Deployment method From source; isolated tests through the owning production client/teardown seam or actual HTTP route, as described below. Database tests use temporary SQLite data; external provider responses are controlled where needed. ### Client used against codex-lb Direct HTTP Responses clients, includ...

### [✅ РЕШЕНО] [#2090: fix(proxy): reconcile reservations after late HTTP-bridge anchor injection](https://github.com/Soju06/codex-lb/issues/2090)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Согласование резерваций API-ключей при поздней инжекции якорей в HTTP-мосте.
  - **Компоненты:** `app/modules/api_keys/service.py, app/modules/proxy/_service/api_key_usage.py`
  - **Тесты:** `tests/unit/test_api_keys_service.py, tests/unit/test_proxy_http_bridge.py`
- **Автор:** @mastertyko | **Дата:** 2026-09-04 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ## Problem The HTTP bridge can persist an API-key usage reservation while a request is still self-contained, then inject `previous_response_id` later when advancing a durable hard-turn operation. The persisted reservation is not updated before the final anchored frame is dispatched. This is a pre-existing generic late-anchor behavior, verified at baseline `dd28d7dff94cdd4919067c1986fd9606b9bbc6b9`; it is outside the Astra protocol PR's fix scope. ## Baseline evidence A deterministic local probe used this unanchored request: ```json {"model":"gpt-6-astra","instructions":"","reasoning":{"effort"...

### [✅ РЕШЕНО] [#2074: bug: post-output frame-less bridge drops still penalize account health](https://github.com/Soju06/codex-lb/issues/2074)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Дропы стрим-фреймов после завершения вывода (post-output) больше не штрафуют здоровье аккаунта.
  - **Компоненты:** `app/modules/proxy/_service/websocket/helpers.py, upstream_events.py`
  - **Тесты:** `tests/unit/test_proxy_http_bridge.py`
- **Автор:** @e1ektr0 | **Дата:** 2026-09-04 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ## Summary Closed issue #1754 made a frame-less HTTP bridge transport drop account-neutral only when `response_events_seen == 0`. The same transport shape remains account-attributable after response events or buffered model output have started. Application progress should govern replay safety, not account-health attribution. A missing upstream-authored close frame (`None` or adapter-synthesized RFC 6455 `1006`) is transport evidence; valid response events are positive evidence that authentication, model admission, and application processing worked. The interrupted request must still fail close...

### [✅ РЕШЕНО] [#2033: proxy: a failing post-terminal health write emits a second terminal stream frame](https://github.com/Soju06/codex-lb/issues/2033)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Предотвращена эмиссия повторного терминального фрейма при ошибке записи post-terminal health.
  - **Компоненты:** `app/modules/proxy/_service/streaming/retry.py`
  - **Тесты:** `tests/unit/test_proxy_http_bridge.py`
- **Автор:** @mastertyko | **Дата:** 2026-09-02 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ## Gap In `app/modules/proxy/_service/streaming/retry.py`, the keyed later-event / caught `ProxyResponseError` rewrite path and the first-event `_TerminalStreamError` path yield the terminal SSE frame first and only then write account health (`proxy._handle_stream_error(...)` → `mark_quota_exceeded` / `mark_rate_limit` / `record_error`). If that health write raises (for example a database error while persisting the rate-limit or quota state), the exception escapes to the broad `except Exception:` handler at the bottom of the attempt loop, which yields a second terminal `response.failed` (`upst...

### [✅ РЕШЕНО] [#1935: feat: retry upstream model-capacity responses for Codex goals](https://github.com/Soju06/codex-lb/issues/1935)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Автоматический ретрай ошибок перегрузки емкости модели (`"Selected model is at capacity. Please try a different model."` / transient capacity error) в рамках единого жизненного цикла ответа (`accepted_replay.py`, `streaming/retry.py`, `websocket/helpers.py`, `is_upstream_model_capacity_error`). Для длительных задач (/goal) запросы перенаправляются на резервные доступные аккаунты без аварийного прерывания сессии Codex.
  - **Компоненты:** `app/modules/proxy/helpers.py, app/modules/proxy/_service/http_bridge/accepted_replay.py, app/modules/proxy/_service/streaming/retry.py, app/modules/proxy/_service/websocket/helpers.py`
  - **Тесты:** `tests/integration/test_proxy_transient_retry.py, tests/unit/test_proxy_http_bridge.py, tests/integration/test_http_responses_bridge.py`
- **Автор:** @cowwoc | **Дата:** 2026-08-27 | **Метки:** `enhancement`
- **Суть проблемы / предложения:**
  > ## Pre-flight checklist ## Problem / motivation Codex can receive this upstream response: ```text ⚠ Selected model is at capacity. Please try a different model. ``` Today this response causes an active `/goal` workflow to abort and become blocked. Codex does not retry the request on its own, so a temporary upstream-capacity condition stops a long-running goal even though retrying later could succeed. Users have been asking OpenAI for built-in handling of this condition for months, without a response to those requests. A proxy is the appropriate place to absorb this transient upstream failure w...

### [✅ РЕШЕНО] [#1898: fix(proxy): persist complete HTTP bridge replay transcripts](https://github.com/Soju06/codex-lb/issues/1898)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Надежное хранение и чанкование транскрипта сессий HTTP-моста (`HttpBridgeOperationEventChunk`, `chunks_v2`), bounded replay codec (`durable_bridge_transcript_codec.py`), лимит размера операций и событий (32 MiB / 4096 событий) с дедупликацией tool continuation.
  - **Компоненты:** `app/db/models.py`, `app/modules/proxy/complete_transcript.py`, `app/modules/proxy/_service/http_bridge/durable_bridge_transcript_codec.py`, `app/modules/proxy/_service/http_bridge/durable_bridge_repository.py`, `app/modules/proxy/_service/http_bridge/durable_bridge_coordinator.py`, `app/db/alembic/versions/20260919_000000_add_http_bridge_transcript_core.py`
  - **Тесты:** `tests/unit/test_complete_transcript.py`, `tests/unit/test_durable_bridge_transcript_codec.py`, `tests/unit/test_bridge_ring_lifecycle.py`, `tests/integration/test_migrations.py`
- **Автор:** @shaqman | **Дата:** 2026-08-24 | **Метки:** `enhancement`
- **Суть проблемы / предложения:**
  > ## Problem The HTTP Responses bridge can lose an upstream `previous_response_id` after a timeout, clean WebSocket close, or upstream session cleanup. Durable operation/event state exists, but recovery is only safe when it has a complete, account-neutral replay transcript. Before this change, root operations could be omitted from the replay chain, terminal output could be missing from the materialized snapshot, and a tool continuation could duplicate a function call when it sent only the new `function_call_output` delta. ## Proposed scope - Persist the root operation in the durable transcript. ...

### [✅ РЕШЕНО] [#1870: feat: add an upstream facet to dashboard request logs](https://github.com/Soju06/codex-lb/issues/1870)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** В `recent-requests-table.tsx` для запросов внешних model sources без привязанного аккаунта (`accountId: null`) колонка Account теперь отображает идентификатор модели `modelSourceId` вместо `Unassigned`. В диалоге детального просмотра запроса добавлены поля `Model Source` и `Source Kind`. Добавлена полная локализация на английском, корейском и упрощенном китайском языках (`en.json`, `ko.json`, `zh-CN.json`).
  - **Компоненты:** `frontend/src/features/dashboard/components/recent-requests-table.tsx`, `frontend/src/i18n/locales/en.json`, `ko.json`, `zh-CN.json`, `openspec/specs/frontend-architecture/spec.md`
  - **Тесты:** `frontend/src/features/dashboard/components/recent-requests-table.test.tsx`
- **Автор:** @joschi655 | **Дата:** 2026-08-21 | **Метки:** `enhancement`
- **Суть проблемы / предложения:**
  > ### Problem / motivation Request logs already persist and return `modelSourceId` and `modelSourceKind` for configured model-source traffic (#1129), but the dashboard neither displays nor filters by them. As a result: - model-source requests appear as `Unassigned` in the Account column; - two sources serving the same model slug cannot be distinguished; - operators cannot isolate source-specific failures, latency, or cost; - historical traffic from a deleted source retains its stable source ID, but the dashboard provides no way to find or identify it. ### Proposed change Add an **Upstream** mult...

### [✅ РЕШЕНО] [#1799: bug: HTTP responses session bridge returns 503: "preserving an incompatible admission handoff"](https://github.com/Soju06/codex-lb/issues/1799)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Устранено застревание закрытых сессий с несовместимым admission handoff в `_http_bridge_sessions`. При карантине ключа или stale/retiring закрытой сессии на том же аккаунте выполняется detach сессии, шедулинг закрытия и сброс handoff для перехода на свежую сессию / durable takeover, исключая бесконечный цикл 503 на ретраях.
  - **Компоненты:** `app/modules/proxy/_service/http_bridge/activity.py`
  - **Тесты:** `tests/unit/test_proxy_http_bridge.py`
- **Автор:** @you-n-g | **Дата:** 2026-08-17 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ### codex-lb version 1.21.0 ### Deployment method pip install codex-lb ### Client used against codex-lb Codex CLI ### ChatGPT account plan(s) involved Pro ### Model(s) involved gpt-5.6-sol ### What happened? A request to `/backend-api/codex/responses` started returning repeated 503 responses with: `HTTP responses session bridge is preserving an incompatible admission handoff` The same session kept failing on retry, with the bridge returning `upstream_unavailable` immediately instead of admitting the request. This appears to be session-scoped, not a global outage. ### What did you expect to hap...

### [✅ РЕШЕНО] [#1758: http-bridge: evicting an inflight waiter does not cancel its creator, so multiple creators race one session key](https://github.com/Soju06/codex-lb/issues/1758)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** При вытеснении (`_evict_http_bridge_inflight_waiter`) или сбое (`_fail_http_bridge_inflight_session_creation`) inflight waiter теперь отменяется задача создателя (`_creator_task.cancel()`), если она еще выполняется и не является текущей задачей. Это устраняет гонку нескольких параллельных creator task за один и тот же ключ сессии. Реализация вынесена в `helpers.py`, снизив размер `mixin.py` до 2409 строк.
  - **Компоненты:** `app/modules/proxy/_service/http_bridge/mixin.py`, `app/modules/proxy/_service/http_bridge/helpers.py`
  - **Тесты:** `tests/unit/test_proxy_http_bridge.py`
- **Автор:** @Soju06 | **Дата:** 2026-08-14 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > Structural follow-up split out of #1751 (which fixes #1695). `_evict_http_bridge_inflight_waiter` removes the inflight future but does **not** cancel the creator that is still running. From that moment two (or more) creators can be in flight for the same session key, each independently selecting an account, opening an upstream socket, and claiming the same durable row. #1751 hardened every consequence of that race it could reach: - every claim advances the owner epoch, so a retiring predecessor's release cannot close a successor's row; - a creator that has already lost its inflight slot aborts...

### [✅ РЕШЕНО] [#1711: WebSocket mid-turn interruptions regressed sharply in 1.23.0-beta.x vs 1.22.0 (new "scope cleanup exceeded its remaining drain budget" warning)](https://github.com/Soju06/codex-lb/issues/1711)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Устранена регрессия ложного синтеза `previous_response_owner_unavailable` при получении терминальных ошибок upstream (например `rate_limit_exceeded`) на continuity owner. Сохраняется аутентичный upstream error envelope. Устранено дублирование `_handle_stream_error`. Добавлена защита свидетельств транспорта и владельца.
  - **Компоненты:** `app/modules/proxy/_service/websocket/mixin.py`, `app/modules/proxy/_service/websocket/helpers.py`
  - **Тесты:** `tests/unit/test_websocket_terminal_cancellation.py`, `tests/integration/test_proxy_websocket_responses.py`
- **Автор:** @crystal150 | **Дата:** 2026-08-13 | **Метки:** `bug` `needs-info` `stale`
- **Суть проблемы / предложения:**
  > ## Summary After upgrading from `1.22.0` to `1.23.0-beta.5`, Codex clients using `supports_websockets = true` frequently see `websocket closed by server before response.completed`, followed by reconnect/retry loops. Server-side, two things changed: 1. A warning that **never appeared once on 1.22.0** now fires continuously: `Websocket scope cleanup exceeded its remaining drain budget` 2. Mid-turn interruption/resend markers rose by roughly **28–35x per request** `v1.23.0` (stable) contains no WebSocket changes relative to `v1.23.0-beta.5`, so this is presumably still present on stable. This is ...

### [✅ РЕШЕНО] [#1304: WebSocket clean-close handoff can consume a queued turn](https://github.com/Soju06/codex-lb/issues/1304)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Устранена отмена ASGI receive корутины при тайм-аутах опроса downstream WebSocket на границе clean-close handoff. Запущенный таск `downstream_receive_task` сохраняется между итерациями через `scheduler.wait({downstream_receive_task}, timeout=poll_timeout)` без отмены нижележащего Starlette receive, предотвращая потерю и проглатывание входящих `response.create` ходов при ротации соединения.
  - **Компоненты:** `app/modules/proxy/_service/websocket/mixin.py`
  - **Тесты:** `tests/unit/test_proxy_utils.py`
- **Автор:** @dmdfami | **Дата:** 2026-07-14 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ## Summary A downstream `response.create` can be consumed by an ASGI receive that is cancelled and recreated while the current upstream WebSocket generation clean-closes. The turn may then be absent from both the retiring upstream generation and its replacement, leaving the downstream session waiting indefinitely. ## Impact This affects native Responses WebSocket clients when a second turn arrives at the clean-close rollover boundary. The existing downstream connection remains open, but the queued turn can be lost. ## Root cause The proxy polls `websocket.receive()` with repeated `asyncio.wait...

---

<a id="responses_and_history"></a>
## 3. Responses API, Context Compaction, якоря и `previous_response_id`
*Ошибки невалидных `previous_response_id`, рассинхронизация контекста диалогов, сбои ротации при смене модели/аккаунта, поломка компактинга с картинками.*

### [✅ РЕШЕНО] [#2356: bug(proxy): experimental context management returns 405 for native notes v2 calls](https://github.com/Soju06/codex-lb/issues/2356)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Реализована полная поддержка 10 нативных операций экспериментального контекстного управления Codex под префиксами `/alpha/history/v2` и `/alpha/notes/v2` (включая `/backend-api/codex/...` и `/v1/...`, как со слешем на конце, так и без). Поддержаны методы GET и POST для заметок (notes) и POST для истории (history). Неизвестные операции возвращают 404 `not_found` в каноническом формате ошибок OpenAI. В `_sticky_key_for_codex_control_request` добавлено связывание аффинити с аккаунтом по идентификатору треда (`_thread_codex_session_affinity`) и наследование происхождения субагентов (`x-openai-subagent`, `x-codex-parent-thread-id`). Все маршруты включены в fail-closed инвентарь Daybreak capability.
  - **Компоненты:** `app/modules/proxy/api.py, app/modules/proxy/affinity.py, openspec/changes/proxy-native-history-notes-routes/`
  - **Тесты:** `tests/integration/test_proxy_native_history_notes.py, tests/integration/test_daybreak_capability_routes.py`
- **Автор:** @dianshili | **Дата:** 2026-09-10 | **Метки:** `untriaged`
- **Суть проблемы / предложения:**
  > ## Compatibility gap The published v1.25.0-beta.7 proxy API is missing the native history/notes v2 operations used by experimental Codex context management. The public description of #2101 reports that these missing routes return HTTP 405, and its [OpenSpec proposal](https://github.com/Soju06/codex-lb/blob/bc9dfedf2d202bff5307e2ac77497e14af20d1c1/openspec/changes/proxy-native-history-notes-routes/proposal.md) identifies the initial `thread_hint` request as an affected call. OpenAI documents experimental context management as using notes and searchable history to retain accumulated details ([of...

### [✅ РЕШЕНО] [#2318: feat(proxy): forward explicit compact requests to Responses model sources](https://github.com/Soju06/codex-lb/issues/2318)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Проведено архитектурное исследование контракта компактинга внешних источников моделей (PR #2451 / `refuse-model-source-remote-compaction`). Зарегистрированные внешние источники моделей не могут генерировать синтетические output-элементы компактинга; попытка направить запрос компактинга во флоу подписных аккаунтов приводит к ложным 503 `no_accounts` или ошибочным 429. До выбора аккаунта явные запросы компактинга (`/responses/compact` и `compaction_trigger`) для model sources отклоняются чистым отказом HTTP 400 с кодом `compaction_unsupported` и типом `invalid_request_error`, что корректно инициирует локальный клиентский компакт. Добавлены регрессионные тесты для обоих endpoint (`/backend-api/codex/responses/compact` и `/v1/responses/compact`).
  - **Компоненты:** `app/modules/proxy/api.py, app/modules/proxy/_service/compact.py, openspec/changes/refuse-model-source-remote-compaction/`
  - **Тесты:** `tests/integration/test_proxy_compact.py (test_proxy_compact_refuses_model_source_with_compaction_unsupported)`
- **Автор:** @JustYannicc | **Дата:** 2026-09-10 | **Метки:** `untriaged`
- **Суть проблемы / предложения:**
  > Explicit compact requests for a registered external Responses model currently enter subscription account selection. With no subscription accounts, both `/v1/responses/compact` and `/backend-api/codex/responses/compact` return `503 no_accounts`; the configured source receives no request. This is a feature request extending today's subscription-only compact contract. It is needed for external models to retain the existing Codex compaction workflow through the model-source bridge. Reproduced on upstream main `0f6a31c56ac30804ca1c0fac27ca02c6f59bf2b0` using the public model-source registration API...

### [✅ РЕШЕНО] [#2269: bug: forwarded continuations can lose required conversation history](https://github.com/Soju06/codex-lb/issues/2269)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Добавлен строгий предикат проверки самодостаточности входных элементов (`_responses_input_items_are_self_contained`) с поддержкой `function_call`, `custom_tool_call`, `apply_patch_call`, и `computer_call`. В `_http_bridge_payload_looks_like_full_resend` строковые и одноэлементные входные данные классифицируются как продолжения (`False`), а массивы валидируются на наличие всех вызовов инструментов для соответствующих выходов, предотвращая ложную классификацию продолжений как полных перепосылок и потерю сохраненных ссылок на ответы.
  - **Компоненты:** `app/modules/proxy/_service/support.py, app/modules/proxy/_service/websocket/helpers.py, app/modules/proxy/_service/http_bridge/helpers.py`
  - **Тесты:** `tests/unit/test_proxy_http_bridge.py`
- **Автор:** @JustYannicc | **Дата:** 2026-09-09 | **Метки:** `bug` `triage`
- **Суть проблемы / предложения:**
  > ## What happens The HTTP bridge can mistake a continuation for a complete conversation and drop the stored response reference it still needs. Two cases in the current code cause this: - Validation converts a raw input string into a one-item array. Near the 4,096-character cutoff, JSON formatting can make that short string look like a full resend. Forwarding it to another bridge owner can change the classification again. - Every array with multiple items is treated as a full resend. Two parallel tool outputs therefore look self-contained even when their tool calls exist only in the previous res...

### [✅ РЕШЕНО] [#2068 / PR #2398: bug(proxy): quota failover stalls unanchored full-resend threads](https://github.com/Soju06/codex-lb/issues/2068)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Проекция портативного полного тела повтора WebSocket (`_project_websocket_full_resend_for_replay`): очистка привязанных к аккаунту ID и шифрованного reasoning, сохранение canonical Responses-Lite `reasoning.context = "all_turns"`, отложенная запись здоровья аккаунта до фиксации резерваций API-ключей. Успешный failover на другой аккаунт пула при pre-output quota error.
  - **Компоненты:** `app/modules/proxy/_service/support.py, app/modules/proxy/_service/websocket/helpers.py, app/modules/proxy/_service/websocket/mixin.py`
  - **Тесты:** `tests/unit/test_websocket_full_resend_projection.py, tests/integration/test_proxy_websocket_responses.py`
- **Автор:** @msmahdinejad | **Дата:** 2026-09-04 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ## Summary A long Codex thread can fail with `usage_limit_reached` even while another pool account is healthy. The affected request is an unanchored local full resend (`previous_response_id`/`conversation` absent) with prompt-cache affinity and response-owned input bookkeeping such as reasoning ciphertext or server item ids. ## Reproduction 1. Configure at least two eligible subscription accounts. 2. Send a streaming Responses request with a retained user/assistant transcript, fresh user input, `prompt_cache_key`, and response-owned reasoning/item state. 3. Make account A return a pre-visible ...

### [✅ РЕШЕНО] [PR #2332: fix(proxy): fail over account-local model rejection](https://github.com/Soju06/codex-lb/pull/2332)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Классификация upstream-ошибки `model_not_found` как модели-специфичной (`is_model_scoped_upstream_rejection`) с сохранением нейтральности здоровья аккаунта. Разрешение failover для перемещаемых предварительно созданных Responses WebSocket запросов до фазы `response.created`. Для pinned continuity owner сохраняется аутентичная upstream ошибка модели.
  - **Компоненты:** `app/modules/proxy/helpers.py, app/modules/proxy/_service/streaming/helpers.py, app/modules/proxy/_service/websocket/mixin.py, app/modules/proxy/_service/streaming/retry.py`
  - **Тесты:** `tests/unit/test_failover_foundation.py, tests/integration/test_proxy_transient_retry.py, tests/integration/test_proxy_websocket_responses.py`

### [✅ РЕШЕНО] [#1950: bug(compact): hosted computer screenshots can still hard-fail compaction and wedge image-heavy threads](https://github.com/Soju06/codex-lb/issues/1950)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Включен тип `computer_call_output` в `_SLIMMABLE_TOOL_CALL_OUTPUT_ITEM_TYPES` и добавлена поддержка сжатия частей содержимого `computer_screenshot` в `_slim_historical_response_content_part` (с заменой на inline image notice part). Предотвращает превышение байтового лимита WebSocket (16 MiB) и зависание потоков с интенсивным использованием скриншотов окружения.
  - **Компоненты:** `app/core/clients/proxy.py`
  - **Тесты:** `tests/unit/test_proxy_utils.py`
- **Автор:** @dianshili | **Дата:** 2026-08-28 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ### codex-lb version `1.24.0b4`, with the relevant runtime file verified byte-for-byte against stable `v1.24.0`. ### Deployment method Other: `uv tool` installation, running as a macOS LaunchAgent. ### Client used against codex-lb Codex desktop app; bundled `codex-cli 0.150.0-alpha.12.2`. ### ChatGPT account plan(s) involved Mixed pool. ### Model(s) involved `gpt-5.6-sol` ### What happened? There is still a terminal size-failure gap for hosted computer screenshots represented as: ```json { "type": "computer_call_output", "output": { "type": "computer_screenshot", "image_url": "data:image/png;b...

### [✅ РЕШЕНО] [#1942: bug: Regression: /v1/responses becomes unusable after upgrading from 1.22.0 to 1.24.0 (PR #1943)](https://github.com/Soju06/codex-lb/issues/1942)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Предотвращение уничтожения сокетов и преждевременного завершения сессий HTTP bridge при cooldown suppression (`_retire_idle_http_bridge_session_on_cooldown_suppression`). Сохранение сессий, занятых параллельными half-open probe или зарегистрированными admission waiters (`_release_http_bridge_admission_preregistration`, `_http_bridge_session_unowned_locked`).
  - **Компоненты:** `app/modules/proxy/_service/http_bridge/request_submit.py, app/modules/proxy/_service/http_bridge/streaming.py, app/modules/proxy/_service/http_bridge/protocol.py, app/modules/proxy/_service/support.py`
  - **Тесты:** `tests/unit/test_proxy_http_bridge.py`
- **Автор:** @Brook-ning | **Дата:** 2026-08-28 | **Метки:** `bug` `needs-info` `stale`
- **Суть проблемы / предложения:**
  > ### codex-lb version 1.24.0 ### Deployment method Docker (ghcr.io/Soju06/codex-lb) ### Client used against codex-lb Codex app (desktop / web) ### ChatGPT account plan(s) involved Pro ### Model(s) involved _No response_ ### What happened? After upgrading codex-lb from version 1.22.0 (revision 4c0dbc9ceb2b5d70204ea7603cf1b4bef83db234) to version 1.24.0 (revision 84fde5a1ed5e0d5a58ccb3ec4b82938b059bf8c5), our Codex /v1/responses traffic became unusable in production. Before the upgrade, this deployment used /v1/responses successfully. After the upgrade, affected Responses requests establish an SS...

### [✅ РЕШЕНО] [PR #2469: fix(proxy): preserve routed file failover provenance](https://github.com/Soju06/codex-lb/pull/2469)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Сохранение типизированной информации о фазе сбоя транспорта (`failure_phase`, `retryable_same_contract`, `failure_detail="transport_error"`) через цепочку `CodexTransportError -> FileProxyError -> ProxyResponseError`, позволяя pre-visible unary failover циклу безопасно перенаправлять загрузку файла на резервный аккаунт при сбое прокси-соединения до отправки запроса.
  - **Компоненты:** `app/core/clients/files.py, app/modules/proxy/_service/file_ops.py, app/modules/proxy/service.py`
  - **Тесты:** `tests/unit/test_unary_transport_failover.py, tests/integration/test_proxy_files.py`

### [✅ РЕШЕНО] [PR #2451: fix(proxy): refuse remote compaction for model-source models before account selection](https://github.com/Soju06/codex-lb/pull/2451)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Предотвращение ошибочного попадания моделей внешних model sources (например, OpenRouter/Ollama) в subscription compact flow при наличии terminal `compaction_trigger` или на `/responses/compact`. До выбора аккаунта возвращается HTTP 400 `compaction_unsupported` (для отключенных источников — 503 `model_source_disabled`), что заставляет Codex CLI компактно сжимать контекст локально без траты квот ChatGPT аккаунтов и ложных 429 ошибок.
  - **Компоненты:** `app/modules/proxy/api.py, openspec/changes/refuse-model-source-remote-compaction/`
  - **Тесты:** `tests/integration/test_model_source_routing.py, tests/integration/test_api_keys_api.py`

### [✅ РЕШЕНО] [#1921: bug: existing Codex threads repeatedly fail with invalid previous_response_id](https://github.com/Soju06/codex-lb/issues/1921)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Разрешено в рамках PR #2423: немедленное завершение с ошибкой `previous_response_not_found` (404) при обращении с явно мертвым клиентским якорем вместо бесконечных циклов retryable 503, что предотвращает блокировку существующих диалогов в клиентах Codex и позволяет сбросить устаревший якорь продолжения.
  - **Компоненты:** `app/modules/proxy/_service/http_bridge/streaming.py, app/modules/proxy/durable_bridge_repository.py`
  - **Тесты:** `tests/unit/test_durable_bridge_owner_retirement.py, tests/integration/test_http_responses_bridge.py`
- **Автор:** @nicefellow1234 | **Дата:** 2026-08-25 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ## Summary An existing Codex thread cannot be continued because every follow-up attempt repeatedly fails with an invalid `previous_response_id` error. This makes the affected conversation unusable instead of allowing it to recover by dropping the stale continuation anchor and replaying the available context. ## Environment - codex-lb version: `1.23.0` (from the Docker Compose deployment artifact available locally; please verify the running image) - Deployment: Docker Compose (`ghcr.io/Soju06/codex-lb:1.23.0`) - Client: Codex app (desktop) - Model/account plan: not captured ## What happened? Wh...

### [✅ РЕШЕНО] [#1895: bug(warmup): /v1/warmup fails with 404 (compact payload) and account probe fails with 400 (max_output_tokens=1) — windows cannot be auto-started](https://github.com/Soju06/codex-lb/issues/1895)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Обе части проблемы полностью устранены:
    1. Ошибка 400 при Force Probe: ранее в PR #1963 порог поднимался до 16, а по свежему PR #2496 параметр `max_output_tokens` полностью исключен из запроса Force Probe (в `app/modules/accounts/service.py`), так как обновленный Codex Responses API отвергает его с кодом 400 (`Unsupported parameter: max_output_tokens`). Запрос отправляется без `max_output_tokens` со `stream=True, store=False` и возвращает HTTP 200.
    2. Ошибка 404 при `POST /v1/warmup` из-за `compaction_trigger`: в `_submit_warmup_request` (`app/modules/proxy/_service/warmup.py`) добавлен прозрачный фоллбэк на минимальный plain Responses API запрос (`_send_warmup_fallback_plain_request` с `max_output_tokens=16`, `stream=True`, `store=False`) при получении HTTP 404 от эндпоинта компактинга. Успешный фоллбэк активирует окно квоты, фиксирует успех в балансировщике и записывает корректный лог.
  - **Компоненты:** `app/modules/accounts/service.py, app/modules/proxy/_service/warmup.py, openspec/specs/usage-refresh-policy/spec.md, openspec/specs/proxy-warmup/spec.md`
  - **Тесты:** `tests/unit/test_accounts_service_probe.py, tests/integration/test_accounts_api_probe.py, tests/integration/test_proxy_warmup.py`
- **Автор:** @BrunoMarc | **Дата:** 2026-08-24 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ## Summary On **1.23.0**, every code path that is supposed to start / verify an account's usage window fails against the current Codex upstream: 1. **`POST /v1/warmup`** → every account lands in `failed` with `upstream_error / "Not Found"`. This appears to be the same underlying problem as #1811 (automations): the warm-up ping goes through `core_compact_responses()`, whose payload appends a `{"type": "compaction_trigger"}` input item, and upstream now answers **404** to it. 2. **Dashboard probe `POST /api/accounts/{account_id}/probe`** → returns `probeStatusCode: 400` for *every* active accoun...

### [✅ РЕШЕНО] [#986: feat: optional sticky account switchover only after compaction boundary](https://github.com/Soju06/codex-lb/issues/986)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Политика переключения sticky-аккаунтов (`sticky_threads`) сохраняет привязку к текущему аккаунту в обычных промежуточных запросах (`reallocate_sticky=False`), предотвращая промахи промпт-кэша и повторную тарификацию токенов. Переключение на более здоровый аккаунт разрешается и явно активируется только на границах компактинга контекста (`reallocate_sticky=True` в `app/modules/proxy/_service/compact.py`).
  - **Компоненты:** `app/modules/proxy/_service/compact.py`, `app/modules/proxy/_load_balancer/sticky_selection.py`, `openspec/specs/sticky-session-operations/spec.md`
  - **Тесты:** `tests/unit/test_select_with_stickiness.py`, `tests/integration/test_proxy_compact.py`
- **Автор:** @cowwoc | **Дата:** 2026-06-11 | **Метки:** `enhancement`
- **Суть проблемы / предложения:**
  > ## Summary Request option or policy for sticky-account reallocation to defer account switchover until the next compaction boundary, instead of switching immediately mid-conversation when sticky budget pressure is crossed. ## Background Current sticky reallocation can switch the pinned account during an ordinary follow-up request once the configured primary or secondary sticky threshold is exceeded and another account is healthier. That behavior is reasonable from pure quota-pressure perspective, but it can be expensive for long-running conversations: - mid-conversation switchover lands on acco...

### [✅ РЕШЕНО] [#568: follow-up: side effects of response.create history slimming (#560)](https://github.com/Soju06/codex-lb/issues/568)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Отменен опасный подход наивной обрезки истории диалога (PR #569, коммит `9910e95a`), приводивший к инвалидации промпт-кэша, галлюцинациям модели из-за фиктивных ассистент-нотисов и рассинхронизации WebSocket `turn_state`. Реализовано безопасное сжатие только тяжелых исторических tool-outputs (`_should_slim_historical_tool_output`) и скриншотов/изображений (`_slim_historical_response_content_part`), сохраняющее структуру диалога и целостность сессий, в сочетании с нативным компактингом (`core_compact_responses()`).
  - **Компоненты:** `app/core/clients/proxy.py`, `app/modules/proxy/_service/compact.py`, `openspec/specs/responses-api-compat/spec.md`
  - **Тесты:** `tests/unit/test_proxy_utils.py`
- **Автор:** @Soju06 | **Дата:** 2026-05-09 | **Метки:** `enhancement`
- **Суть проблемы / предложения:**
  > ## Background #560 (`fix(proxy): slim oversized response.create history`, merged in `e42af5e`) added a second slimming pass that omits the oldest historical input items when image/tool-output slimming is still over the upstream WebSocket budget. It also injects a single assistant-role notice (`[codex-lb omitted N historical input items]`) and the slimming runs on both the HTTP and WebSocket `response.create` paths. The PR fixes a real `413` failure mode (#556 is closed by it), and on net the new behavior is strictly better than the previous hard 413. But there are several second-order effects ...

---

<a id="accounts_and_quotas"></a>
## 4. Управление аккаунтами, OAuth, квоты, лимиты и Warmup
*Сбои автопрогрева (/v1/warmup), учет квот Edu/Team/Pro, циклическая реаутентификация сброшенных токенов, зависание в rate_limited.*

### [✅ РЕШЕНО] [#2442: bug(proxy): early token_expired reauth account poisons fresh Codex HTTP routing](https://github.com/Soju06/codex-lb/issues/2442)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Блокировка роутинга аккаунтов с `token_revoked` / `token_expired` до успешной реаутентификации.
  - **Компоненты:** `app/core/balancer/logic.py, app/modules/proxy/account_eligibility.py`
  - **Тесты:** `tests/unit/test_proxy_account_eligibility.py, tests/unit/test_load_balancer.py`
- **Автор:** @leventov | **Дата:** 2026-09-15 | **Метки:** `untriaged`

### [✅ РЕШЕНО] [PR #2468: fix(quota): validate planner timezones and tolerate legacy malformed keys](https://github.com/Soju06/codex-lb/pull/2468)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Строгая валидация имени таймзоны через `ZoneInfo` при обновлении настроек Quota Planner (возврат 400 `invalid_quota_planner` при некорректных путях вроде `/Europe/Stockholm` или `Europe/../Stockholm`), а также перехват `(ZoneInfoNotFoundError, ValueError)` в логике прогнозирования и роутинга с безопасным фоллбэком на UTC для уже сохраненных некорректных ключей.
  - **Компоненты:** `app/modules/quota_planner/api.py, app/modules/quota_planner/logic.py`
  - **Тесты:** `tests/integration/test_quota_planner_api.py, tests/unit/test_quota_planner.py`
- **Суть проблемы / предложения:**
  > ### codex-lb version `1.25.0-beta.9`, built from current upstream `main` at `d1fd2f21fa0e0f3b5fcad3af5fada19693cd1fc1`. ### Deployment method Docker image built locally from upstream `main`; single replica with SQLite. ### Client used against codex-lb Codex CLI `0.154.0` using the native Codex HTTP Responses endpoint. ### ChatGPT account plan(s) involved Pro pool. ### Model(s) involved `gpt-5.6-luna` (the same unusable account was also observed entering WebSocket selection for another model). ### What happened? A pool contained five healthy `active` accounts and one `reauth_required` account. ...

### [✅ РЕШЕНО] [#2426: bug(metrics): populate account counts and expose availability for alerting](https://github.com/Soju06/codex-lb/issues/2426)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Экспорт метрик `accounts_total` и `accounts_available` (с `livemax`), синхронизация с кэшем роутинга.
  - **Компоненты:** `app/core/metrics/prometheus.py, app/modules/proxy/account_cache.py, app/main.py`
  - **Тесты:** `tests/unit/test_metrics.py, tests/unit/test_account_metrics.py`
- **Автор:** @slumbi | **Дата:** 2026-09-14 | **Метки:** `untriaged`
- **Суть проблемы / предложения:**
  > ## Problem Operators need to alert when the pool has too few active or available accounts, especially when no account can serve requests. `codex_lb_accounts_total` is declared as a gauge with a `status` label in `app/core/metrics/prometheus.py`, but a repository-wide search found no producer that updates it. Consequently, `codex_lb_accounts_total{status="active"}` cannot currently provide a reliable account count for alerting. No dedicated available-account count gauge was found either. This finding comes from source inspection; a live deployment scrape has not been checked. ## Evidence / repr...

### [✅ РЕШЕНО] [#2420: bug(accounts): Hard-coded Pro and Pro Lite credit capacities disagree with observed quota consumption, distorting pooled credit reporting](https://github.com/Soju06/codex-lb/issues/2420)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Реализован механизм калибровки и переопределения емкости планов в `app/core/usage/__init__.py` (`set_plan_capacity_override`, `clear_plan_capacity_overrides`, `get_plan_capacity_overrides`), позволяющий задавать точные калиброванные значения емкостей для любых планов и окон (включая Pro и Pro Lite в смешанных пулах). Функция `capacity_for_plan` приоритетно использует зарегистрированные переопределения, устраняя искажения расчёта оставшихся кредитов и недельного темпа на дашборде.
  - **Компоненты:** `app/core/usage/__init__.py`, `openspec/specs/usage-refresh-policy/spec.md`
  - **Тесты:** `tests/unit/test_usage.py`
- **Автор:** @andrew-adamson-proteros | **Дата:** 2026-09-14 | **Метки:** `bug` `triage`
- **Суть проблемы / предложения:**
  > ### codex-lb version 1.25.0-beta.1 ### Affected account plan(s) Plus, Pro, Mixed pool ### Symptom category Quota / usage values are wrong ### What does the dashboard / logs show? ```markdown Dashboard distorts credit remaining display and suggests there is more credit remaining than there actually is, when prolite and pro exist in a mixed pool. ``` ### What did you expect? ## Summary The hard-coded weekly capacities appear inconsistent with token usage observed across complete quota-exhaustion cycles: | Plan | codex-lb capacity | Observed token-priced consumption | Likely capacity | |---|---:|...

### [✅ РЕШЕНО] [#2413: feat: Luna Reserve (gpt-reserve) fallback when chat quota is exhausted](https://github.com/Soju06/codex-lb/issues/2413)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Поддержка пула Luna Reserve (`gpt-reserve` / `base_model_inference`) при исчерпании основной чат-квоты. Исправлена утечка политики `"disabled"` в `AccountState.routing_policy` в `load_balancer.py` (`_additional_quota_routing_policy_override`), обеспечен корректный выбор и ротация аккаунтов с доступным резервом.
  - **Компоненты:** `app/modules/proxy/load_balancer.py, app/modules/proxy/account_eligibility.py`
  - **Тесты:** `tests/unit/test_luna_reserve_routing.py, tests/unit/test_load_balancer.py`
- **Автор:** @AndresASJ | **Дата:** 2026-09-13 | **Метки:** `untriaged`
- **Суть проблемы / предложения:**
  > ## Problem When a ChatGPT Plus/Pro account's regular quota (Sol/Terra/Luna) is exhausted, codex-lb currently marks the account as `QUOTA_EXCEEDED` and either rotates to the next account or returns a rate-limit error. However, eligible accounts have a separate **Luna Reserve** quota bucket (`gpt-reserve` / `base_model_inference`) that provides additional GPT-5.6 Luna capacity — this reserve goes unused. The dashboard confirms this: requests fall back to other accounts or fail, even though the exhausted account's Luna Reserve bucket shows capacity remaining. ## Expected behavior When an account'...

### [✅ РЕШЕНО] [#2327: fix(accounts): recover stale holds after verified matching operator probes](https://github.com/Soju06/codex-lb/issues/2327)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Добавлен флаг `probe_verified=(200 <= probe_status < 300)` в цепочку принудительного обновления квоты (`AccountsService.probe_account` -> `UsageUpdater.force_refresh_result` -> `UsageUpdater._refresh_account` -> `UsageUpdater._recover_quota_status_from_usage`). Когда подтвержденный операторский зонд (2xx) доказывает доступность апстрима и снимок использования подтверждает доступную квоту (< 100%), заблокированный статус `AccountStatus.RATE_LIMITED` принудительно восстанавливается в `AccountStatus.ACTIVE`, минуя устаревший кулдаун `cooldown_deadline`, с очисткой маркеров `blocked_at` и `reset_at`. В `LoadBalancer.record_probe_result` также сбрасываются runtime-поля `blocked_at` и `cooldown_until`.
  - **Компоненты:** `app/modules/accounts/service.py, app/modules/usage/updater.py, app/modules/proxy/load_balancer.py, openspec/specs/usage-refresh-policy/spec.md`
  - **Тесты:** `tests/unit/test_usage_updater.py, tests/integration/test_accounts_api_probe.py`
- **Автор:** @JustYannicc | **Дата:** 2026-09-10 | **Метки:** `untriaged`
- **Суть проблемы / предложения:**
  > An account can remain excluded after a restart even when upstream accepts the same model again. The persisted rate-limit deadline survives, while the process-local evidence needed for early recovery does not. Current account-routing requirements deliberately retain that deadline; fixing this needs an explicit verified-recovery exception. On a two-account deployment, a historical Astra `429 usage_limit_reached` left one account held despite fresh 0% usage. A bounded account-pinned Astra/default request then returned HTTP 200 and `response.completed`. After an exact guarded correction of that ol...

### [✅ РЕШЕНО] [#2288: feat: pool reset credits across accounts in Codex Desktop](https://github.com/Soju06/codex-lb/issues/2288)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Объединение (pooling) кредитов сброса лимитов (`rate-limit-reset-credits`) со всех импортированных подходящих аккаунтов пула через `RateLimitResetCreditsStore.list_all()`. Codex Desktop видит общий счетчик и доступные кредиты пула. Действие Reset автоматически выбирает ближайший к истечению кредит (`_find_target_reset_credit_account`), выполняет списание через `_ensure_v1_reset_credit_account_fresh` с учетными данными владельца и принудительно обновляет снимки квот как целевого аккаунта, так и вызывающего. Добавлены канонические алиасы эндпоинтов `/backend-api/wham/rate-limit-reset-credits/consume` и `/backend-api/codex/rate-limit-reset-credits/consume`.
  - **Компоненты:** `app/modules/rate_limit_reset_credits/store.py, app/modules/proxy/api.py, openspec/specs/rate-limit-reset-credits/spec.md`
  - **Тесты:** `tests/integration/test_codex_usage_api.py`

### [✅ РЕШЕНО] [#2285: feat: show pooled quota in Codex Desktop while staying signed in](https://github.com/Soju06/codex-lb/issues/2285)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Поддержка показа суммарной квоты пула балансировщика в нативном интерфейсе Codex Desktop с сохранением `plan_type` и аутентичности вошедшего аккаунта. Запросы `/backend-api/wham/usage` и `/backend-api/codex/usage` принимают токен вошедшего пользователя, сохраняют `plan_type` во избежание клиентских ограничений Desktop на Luna, агрегируя остаток квот и кредитов со всех активных аккаунтов пула.
  - **Компоненты:** `app/modules/proxy/api.py, openspec/specs/account-quota-presentation/spec.md`
  - **Тесты:** `tests/integration/test_codex_usage_api.py`

### [✅ РЕШЕНО] [#2274: bug: continuations can be routed to the wrong account](https://github.com/Soju06/codex-lb/issues/2274)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Устранена эвристика единственного подходящего аккаунта в `compact.py` и `streaming/retry.py`. При отсутствии подтвержденного владельца `previous_response_id` прокси безоговорочно завершает запрос отказом (fail closed) с ошибкой HTTP 502 `previous_response_owner_unavailable`. На уровне WebSocket connect и socket reuse добавлена валидация владельца сессии с возвратом терминальной ошибки при lookup miss. В `_select_responses_model_source_with_continuity` и WebSocket guards обеспечено распознавание принадлежности turn-state (`x-codex-turn-state`) сессиям подписки, что предотвращает ложное срабатывание `model_source_requires_http_transport` и перехват продолжающихся сессий модельными источниками.
  - **Компоненты:** `app/modules/proxy/_service/compact.py, app/modules/proxy/_service/streaming/retry.py, app/modules/proxy/_service/websocket/mixin.py, app/modules/proxy/api.py, openspec/specs/responses-api-compat/spec.md`
  - **Тесты:** `tests/integration/test_proxy_responses.py, tests/unit/test_proxy_websocket_model_source_guard.py, tests/unit/test_proxy_model_source_continuity.py`
- **Автор:** @JustYannicc | **Дата:** 2026-09-09 | **Метки:** `bug` `triage`
- **Суть проблемы / предложения:**
  > ## What happens A continuation can be sent to the wrong account when its recorded owner is missing. It can also fail unnecessarily when a model source takes precedence over a known subscription owner. For example, an API key can use accounts A and B, but only A currently supports the requested model. If a previous-response lookup misses, the proxy counts model-filtered accounts and treats A as the only possible owner. The response could belong to B. Being available for routing does not prove ownership. The inverse also happens: a key restricted to A can be rejected because the count includes u...

### [✅ РЕШЕНО] [#2076: bug: default Docker port 1455 mapping can intercept Codex Desktop OAuth callbacks](https://github.com/Soju06/codex-lb/issues/2076)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Корректный жизненный цикл и остановка фонового локального callback-сервера порта 1455 при истечении 15-минутного TTL заброшенных Browser (PKCE) сессий авторизации (`_expire_browser_flows`, `_ensure_browser_flow_expiry_task_locked` в `app/modules/oauth/service.py`).
  - **Компоненты:** `app/modules/oauth/service.py`
  - **Тесты:** `tests/integration/test_oauth_flow.py`
- **Автор:** @shuhulx | **Дата:** 2026-09-04 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ### codex-lb version 1.24.0 ### Deployment method Docker (ghcr.io/Soju06/codex-lb) ### Client used against codex-lb Codex app (desktop / web) ### ChatGPT account plan(s) involved Pro ### Model(s) involved N/A — failure occurs during OAuth before model selection ### What happened? An abandoned dashboard Browser (PKCE) account flow can leave codex-lb's callback server listening on port 1455 after the flow's 15-minute TTL has expired. With the documented Docker `1455:1455` publication, a later Codex Desktop “Sign in with ChatGPT” callback was handled by codex-lb instead of Codex Desktop. The brow...

### [✅ РЕШЕНО] [#2064: bug(proxy): revoked access tokens repeatedly re-enter reauth routing](https://github.com/Soju06/codex-lb/issues/2064)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Предотвращение повторного входа отозванных access токенов в цикл реаутентификации.
  - **Компоненты:** `app/core/balancer/logic.py, app/modules/proxy/account_eligibility.py`
  - **Тесты:** `tests/unit/test_proxy_account_eligibility.py, tests/unit/test_load_balancer.py`
- **Автор:** @nhdong1993 | **Дата:** 2026-09-04 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ### codex-lb version 1.25.0-beta.1 (source deployment including PR #1877) ### Deployment method Docker Compose, single-host HAProxy blue/green deployment. ### Client used against codex-lb Codex Desktop over HTTP and WebSocket Responses transports. ### ChatGPT account plan(s) involved Free and Plus in a mixed pool. ### Models involved gpt-5.6-terra and gpt-5.6-sol. ### What happened? After PR #1877 made unexpired `reauth_required` accounts request-routable, accounts whose refresh credentials are already invalid can continue to be selected because the stored access-token JWT still has a future `...

### [✅ РЕШЕНО] [#1976: bug(warmup): staggered idle slots can be unreachable for sliding reset_at](https://github.com/Soju06/codex-lb/issues/1976)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** В `_staggered_idle_due` (`app/modules/limit_warmup/service.py`) добавлена детекция скользящего горизонта `reset_at` (`cycle_start ≈ now_epoch`). При скользящем сбросе точка отсчета цикла (`cycle_start`) вычисляется от стабильного эпохального цикла (`now_epoch - (now_epoch % window_seconds)`), обеспечивая достижимость ненулевых слотов прогрева для всех аккаунтов пула без голодания.
  - **Компоненты:** `app/modules/limit_warmup/service.py, openspec/specs/usage-refresh-policy/spec.md`
  - **Тесты:** `tests/unit/test_limit_warmup.py`
- **Автор:** @dianshili | **Дата:** 2026-08-30 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ### codex-lb version `v1.24.0` The production observation was made on `v1.24.0-beta.4`. `app/modules/limit_warmup/service.py` is byte-identical in `v1.24.0-beta.4`, the supported `v1.24.0` tag, and current `main` at `02113fd`. ### Deployment method Other: native arm64, uv-managed local installation, one process, SQLite. ### Client used against codex-lb Codex app (desktop / web) ### ChatGPT account plan(s) involved Mixed pool (Plus and Pro). ### Model(s) involved The configured limit warm-up model was `auto`. ### What happened? Staggered idle warm-up can permanently starve every non-zero slot w...

### [✅ РЕШЕНО] [#1975 / PR #2326: bug(warmup): live usage ingestion can consume reset evidence without invoking limit warm-up](https://github.com/Soju06/codex-lb/issues/1975)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Восстановление сохраненных свидетельств сброса квот (`recover_current_reset_evidence`) независимо от того, записал ли текущий опрос изменения (`usage_written`). Оценка warm-up по сбросу квоты выполняется даже при пропущенных циклах опроса; дедупликация через атомарные попытки в БД.
  - **Компоненты:** `app/core/usage/refresh_scheduler.py, app/modules/limit_warmup/reset_evidence.py, app/modules/limit_warmup/service.py, app/modules/usage/repository.py`
  - **Тесты:** `tests/unit/test_usage_refresh_scheduler_recovery.py, tests/integration/test_live_reset_warmup.py`
- **Автор:** @dianshili | **Дата:** 2026-08-30 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ### codex-lb version `v1.24.0` The production observation was made on `v1.24.0-beta.4`. I verified that these three relevant files are byte-identical in `v1.24.0-beta.4`, the supported `v1.24.0` tag, and current `main` at `02113fd`: - `app/modules/usage/live_ingest.py` - `app/core/usage/refresh_scheduler.py` - `app/modules/limit_warmup/service.py` ### Deployment method Other: native arm64, uv-managed local installation, one process, SQLite. ### Client used against codex-lb Codex app (desktop / web) ### ChatGPT account plan(s) involved Pro. The race does not appear plan-specific. ### Model(s) i...

### [✅ РЕШЕНО] [#1946: UI account section bug](https://github.com/Soju06/codex-lb/issues/1946)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Проверено по исходному коду и тестам компонентов фронтенда. Проблема переполнения списка аккаунтов на высоких экранах (наследие #1132 в 1.24) решена в PR #1149 и PR #1195 ограничением высоты скролла (`max-h-[min(32rem,calc(100dvh-16rem))]` и `max-h-[calc(100dvh-15rem)]`). Тесты компонентов (`account-list.test.tsx`, `accounts-page.test.tsx`) и Playwright-тесты отображения подтверждают корректный рендеринг без наложений.
  - **Компоненты:** `frontend/src/features/accounts/account-list.tsx, frontend/src/features/accounts/accounts-page.tsx`
  - **Тесты:** `frontend/src/features/accounts/account-list.test.tsx, frontend/src/features/accounts/accounts-page.test.tsx, frontend/screenshots/capture.spec.ts`
- **Автор:** @K4leri | **Дата:** 2026-08-28 | **Метки:** `bug` `needs-info` `stale`
- **Суть проблемы / предложения:**
  > ### codex-lb version 1.24.0 ### What happened? https://github.com/Soju06/codex-lb/issues/1132 the same problem in 1.24, that was solved in 1.23

### [✅ РЕШЕНО] [#1919 / PR #2429: bug: Need to reauthenticate accounts with Advanced Account Security every single day](https://github.com/Soju06/codex-lb/issues/1919)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Синхронизация политики обновления учетных данных Auth Guardian с канонической общей политикой preflight (`should_refresh(last_refresh, now)`). Удален отдельный жесткий лимит 12 часов (`_MAX_REFRESH_AGE_SECONDS`), устранены преждевременные принудительные циклы обновления и инвалидации сессий для защищенных аккаунтов. Обновлены локали фронтенда и спецификации OpenSpec.
  - **Компоненты:** `app/core/auth/guardian.py, frontend/src/i18n/locales/, openspec/specs/usage-refresh-policy/`
  - **Тесты:** `tests/unit/test_auth_guardian.py, tests/integration/test_auth_guardian_multi_replica.py, tests/integration/test_background_jobs_runtime.py`
- **Автор:** @vitobotta | **Дата:** 2026-08-25 | **Метки:** `bug` `needs-info` `stale`
- **Суть проблемы / предложения:**
  > ### codex-lb version 1.23.0 ### Deployment method Docker (ghcr.io/Soju06/codex-lb) ### Client used against codex-lb Codex CLI, Codex app (desktop / web) ### ChatGPT account plan(s) involved Pro ### Model(s) involved gpt-5.6-sol, gpt-5.6-luna ### What happened? Hi! First of all, huge thanks for this awesome project! It makes it easier to use two ChatGPT subscriptions without having to log out and log back in to change the subscription. I am both a coder and a security researcher so I had to enroll in the Advanced Account Security otherwise OpenAI would have restricted me from using the models f...

### [✅ РЕШЕНО] [#1918: bug: codex-lb incorrectly calculates usage for edu accounts](https://github.com/Soju06/codex-lb/issues/1918)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Проверено в кодовой базе: баг некорректного расчета квот и сброса статуса исчерпания для Edu-аккаунтов закрыт в коммите `3d34092d` (PR #2078). Метод `apply_usage_quota` сохраняет статус `AccountStatus.QUOTA_EXCEEDED` при наблюдаемом сбросе, предотвращая преждевременный перевод в `ACTIVE`. Для Edu-аккаунтов заданы точные кредитные веса (`PLAN_CAPACITY_CREDITS_PRIMARY["edu"] = 225.0`, `PLAN_CAPACITY_CREDITS_SECONDARY["edu"] = 7560.0`).
  - **Компоненты:** `app/modules/usage/service.py, app/core/balancer/capacity.py`
  - **Тесты:** `tests/unit/test_usage.py, tests/integration/test_additional_usage_flow.py`
- **Автор:** @Lok3rn3t | **Дата:** 2026-08-25 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ### codex-lb version 1.24.0-beta.4 ### Deployment method Docker (ghcr.io/Soju06/codex-lb) ### Client used against codex-lb Codex app (desktop / web) ### ChatGPT account plan(s) involved Edu ### Model(s) involved _No response_ ### What happened? When the total weekly usage allowance runs out, codex-lb considers that the usage has not been exhausted <img width="484" height="299" alt="Image" src="https://github.com/user-attachments/assets/7ae40ff8-e42d-4a37-8454-c09211e68309" /> ### What did you expect to happen? + ### Steps to reproduce ```markdown + ``` ### Relevant logs ```shell ``` ### Config...

### [✅ РЕШЕНО] [#1793: feat: weekly limits estimation in $](https://github.com/Soju06/codex-lb/issues/1793)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** В карточку Weekly Limits dashboard (`weekly_pace.py`, `service.py`, `schemas.py`) и фронтенд (`weekly-credits-pace-card.tsx`) добавлен расчет и отображение оценочной стоимости полного недельного лимита в долларах США (`estimated_full_weekly_limit_cost_usd` = `activity_cost_usd / (used_percent / 100)`). Добавлены локали в `en.json`, `ko.json`, `zh-CN.json` и атрибут `data-testid="weekly-estimated-limit-cost"`.
  - **Компоненты:** `app/modules/dashboard/weekly_pace.py, app/modules/dashboard/service.py, app/modules/dashboard/schemas.py, frontend/src/features/dashboard/components/weekly-credits-pace-card.tsx, openspec/specs/frontend-architecture/spec.md`
  - **Тесты:** `tests/unit/test_dashboard_weekly_pace.py, frontend/src/features/dashboard/components/weekly-credits-pace-card.test.tsx`

### [✅ РЕШЕНО] [#1708: ux/docs: make routing, sticky affinity, quota thresholds, warm-up, and account eligibility understandable in the dashboard](https://github.com/Soju06/codex-lb/issues/1708)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Разделены и понятно документированы концепции роутинга в UI и документации: soft sticky routing vs hard affinity owner, quota thresholds, warming up и статусы доступности аккаунтов. Добавлены подсказки (tooltips), обновлены переводы (`en`, `ko`, `zh-CN`), документация `docs/routing.md` и OpenSpec delta `openspec/changes/clarify-routing-quota-help-copy/`.
  - **Компоненты:** `frontend/src/features/routing/routing-settings.tsx`, `frontend/src/features/accounts/account-list.tsx`, `frontend/src/features/accounts/account-list-item.tsx`, `frontend/src/features/accounts/status-badge.tsx`, `frontend/src/i18n/locales/*.json`, `docs/routing.md`, `openspec/specs/account-quota-presentation/`
  - **Тесты:** `frontend/src/features/routing/routing-settings.test.tsx`, `frontend/src/features/accounts/account-list.test.tsx`, `frontend/src/features/accounts/account-list-item.test.tsx`, `openspec validate --specs`
- **Автор:** @myudak | **Дата:** 2026-08-13 | **Метки:** `documentation` `enhancement` `frontend`
- **Суть проблемы / предложения:**
  > ### Problem The dashboard exposes powerful routing controls, but several of the labels are ambiguous enough that it is very difficult to understand what codex-lb will actually do during a failure. This became especially confusing while debugging #1707: the dashboard showed healthy accounts with quota remaining, `Sticky threads` was toggled off, yet an existing Codex thread still behaved as if it was pinned to an unavailable account. The main issue is that the UI currently collapses several different concepts into similar wording: - soft sticky routing - hard Codex continuation / affinity owner...

### [✅ РЕШЕНО] [#1632: feat: support model sources via model_catalog_json for ChatGPT OAuth users](https://github.com/Soju06/codex-lb/issues/1632)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** При отдаче каталога моделей `model_catalog_json` для внешних модельных источников (`model_sources/catalog.py`) добавлено автоматическое заполнение поля `available_in_plans` стандартным списком планов ChatGPT (`free`, `plus`, `pro`, `team`, `edu`). Это предотвращает клиентскую ошибку валидации Codex Desktop ("The model is not supported when using Codex with a ChatGPT account") при работе через ChatGPT OAuth без API ключей.
  - **Компоненты:** `app/modules/model_sources/catalog.py, openspec/specs/model-source-routing/spec.md`
  - **Тесты:** `tests/unit/test_model_sources_catalog.py`

### [✅ РЕШЕНО] [#1576: feat: add strict model-to-ChatGPT OAuth account routing](https://github.com/Soju06/codex-lb/issues/1576)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Реализован строгий роутинг конкретных моделей на назначенные аккаунты (`app/modules/proxy/model_account_routing.py`). Маршрутизация настраивается программно, через конфигурационный файл (`config/model_account_routing.json`) или динамический заголовок `x-codex-model-account-routing`. Таргет-аккаунт сопоставляется по id, email, alias или chatgpt_account_id. При недоступности, квотном исчерпании или исключении целевого аккаунта маршрутизация завершается fail-closed ошибкой (`model_account_not_found`, `model_account_unavailable`, `model_account_scope_mismatch`) без непреднамеренного перехода на чужие аккаунты.
  - **Компоненты:** `app/modules/proxy/model_account_routing.py`, `app/modules/proxy/service.py`, `openspec/specs/account-routing/spec.md`
  - **Тесты:** `tests/unit/test_model_account_routing.py` (все 7 тестов пройдены)
- **Автор:** @bazhand | **Дата:** 2026-08-03 | **Метки:** `enhancement`
- **Суть проблемы / предложения:**
  > ### Problem / motivation I am running codex-lb 1.22.0 with multiple ChatGPT OAuth accounts. The current API-key workaround requires separate keys or client providers. For example, one key can be restricted to gpt-5.6-sol and assigned to Account A, while another key can be restricted to gpt-5.6-luna and assigned to Account B. This works, but the client must select the correct key/provider. A single key or endpoint cannot automatically route different models to different OAuth accounts. ### Proposed change I would like a first-class model-to-account routing configuration. Example: gpt-5.6-sol ->...

### [✅ РЕШЕНО] [#1415: perf(balancer): optimize low-TTFT routing for large account pools under bursts](https://github.com/Soju06/codex-lb/issues/1415)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Реплико-локальный учет времени первого токена (TTFT) и пропускной способности (TPS per model) для взвешенных стратегий (`capacity_weighted`, `relative_availability`). Медленные когорты дисконтируются до 0.5x с объединением по минимуму, без исключения аккаунтов. В парсере verbatim-тайминга `response_timing.py` поддержаны output-события и снэпшоты завершения (`response.refusal.done`, `function_call_arguments.done`, `custom_tool_call_input.done`).
  - **Компоненты:** `app/modules/proxy/_load_balancer/ttft_cohort.py, throughput_cohort.py, latency_cohort.py, app/modules/proxy/_service/response_timing.py, app/modules/proxy/load_balancer.py`
  - **Тесты:** `tests/unit/test_throughput_cohort_weighting.py, tests/unit/test_ttft_optimization.py, tests/unit/test_response_timing.py` (все 70 тестов пройдены)
- **Автор:** @yjx-git001 | **Дата:** 2026-07-20 | **Метки:** `enhancement`
- **Суть проблемы / предложения:**
  > ## Summary Please add an explicit low-TTFT routing objective for large account pools under burst concurrency. The desired outcome is not only to prevent pathological 60-600s bridge stalls (#1393), but also to increase the share of normal interactive text requests receiving their first model output in roughly 0.3-1s and reduce P90/P95 tail latency when many eligible accounts are available. ## Production observation In a single-instance deployment with a large pool (historically up to 147 active accounts), `round_robin` repeatedly produced better perceived TTFT than quota/capacity-oriented strat...


### [✅ РЕШЕНО] [#1413: feat(accounts): support explicit access-token-only credential imports](https://github.com/Soju06/codex-lb/issues/1413)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Поддержан импорт учетных записей, содержащих только валидный `access_token` без `id_token` и `refresh_token` (`app/core/auth/__init__.py`, `app/modules/accounts/schemas.py`, `app/modules/accounts/service.py`). При отсутствии refresh token в базу данных сохраняется зашифрованная пустая строка без изменения схемы БД; статус рефреша аккаунта выставляется в `non_refreshable` (`app/modules/accounts/mappers.py`), а попытки обновления токена завершаются немедленным постоянным отказом `RefreshError(code="non_refreshable_account")` без сетевых вызовов в upstream (`app/modules/accounts/auth_manager.py`).
  - **Компоненты:** `app/core/auth/__init__.py`, `app/modules/accounts/schemas.py`, `app/modules/accounts/service.py`, `app/modules/accounts/auth_manager.py`, `app/modules/accounts/mappers.py`, `openspec/specs/account-import/spec.md`
  - **Тесты:** `tests/unit/test_access_token_account_import.py`, `tests/integration/test_account_auth_export.py`
- **Автор:** @yjx-git001 | **Дата:** 2026-07-20 | **Метки:** `enhancement`
- **Суть проблемы / предложения:**
  > ## Summary Please support importing a valid access-token-only Codex credential when explicit account metadata is supplied, while clearly marking the account as non-refreshable. This is useful when migrating credentials from an account manager/export that provides a currently valid ChatGPT/Codex access token but does not provide an ID token or refresh token. ## Current behavior Current `main` defines all three fields as required strings in `AuthTokens`: ```python id_token: str access_token: str refresh_token: str ``` `claims_from_auth()` also derives email, plan, workspace, and account identity...

### [✅ РЕШЕНО] [#1367: bug(accounts): Team 30d quota is displayed as 5h](https://github.com/Soju06/codex-lb/issues/1367)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Добавлен кредитный лимит Team в `PLAN_CAPACITY_CREDITS_MONTHLY` (`7560.0`), нормализация первичного 30-дневного окна в `monthly_usage` при отсутствии активного secondary weekly quota (`app/core/usage/__init__.py`, `app/modules/usage/live_ingest.py`, `app/modules/accounts/mappers.py`). На фронтенде окна >= 28 дней рендерятся как "Monthly", а не "5h" (`account-card.tsx`, `account-list.tsx`).
  - **Компоненты:** `app/core/usage/__init__.py`, `app/modules/usage/live_ingest.py`, `app/modules/accounts/mappers.py`, `frontend/src/features/dashboard/components/account-card.tsx`, `frontend/src/features/dashboard/components/account-list.tsx`
  - **Тесты:** `tests/unit/test_account_mappers.py`, `tests/integration/test_accounts_api_extended.py`, `account-card.test.tsx`, `account-list.test.tsx`
- **Автор:** @paiams | **Дата:** 2026-07-16 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ### codex-lb version 1.21.0 (`ghcr.io/soju06/codex-lb:1.21.0`) ### Affected account plan(s) Team ### Symptom category Dashboard display bug only ### What does the dashboard / logs show? ```markdown Team accounts with a 30-day quota window are rendered as `5h`. Example: `5h 96%`, reset `in 30d 9h`, while `Weekly` is `--`. Free accounts on the same dashboard correctly show `Monthly`. ``` <img width="886" height="458" alt="Team 30-day quota displayed as 5h" src="https://github.com/user-attachments/assets/0f16e159-8264-457f-a080-89dcbc4ce44f" /> ### What did you expect? The label should follow the...

### [✅ РЕШЕНО] [#1340: Simplicity backlog: settings-surface reduction (164 → ~110 fields) & deferred follow-ups](https://github.com/Soju06/codex-lb/issues/1340)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Поверхность конфигурации успешно сокращена и зафиксирована на уровне 97 полей (бюджет max=97 в `.github/simplicity-budgets.toml`). Классификация уровней: T0=13, T1=51, T2=0, T3=30, T4=3. Автоматизированные проверки `scripts/check_settings_tiers.py` и `tests/unit/test_settings_reference.py` полностью защищают настройки от разрастания.
  - **Компоненты:** `app/core/config/settings.py`, `scripts/check_settings_tiers.py`, `.github/simplicity-budgets.toml`
  - **Тесты:** `scripts/check_settings_tiers.py`, `tests/unit/test_settings_reference.py`
- **Автор:** @Soju06 | **Дата:** 2026-07-15 | **Метки:** `enhancement`
- **Суть проблемы / предложения:**
  > # Simplicity backlog: settings-surface reduction & deferred follow-ups Tracking issue for the simplicity effort (audit 2026-07-15). The effort's PR stack: #1336 (principles & gates), #1337 (docs site + README diet), #1338 (CI budgets), #1339 (dashboard progressive disclosure). This issue tracks everything the audit found that was deliberately **not** included in those PRs. ## Why The settings surface is **164 env-settable fields** (`app/core/config/settings.py`), of which only ~8 are essential; zero are required for first boot. The audit ranked reductions by (fields removed × user-facing confu...

### [✅ РЕШЕНО] [#1130: feat: support for (personal) access token accounts (for business/enterprise)](https://github.com/Soju06/codex-lb/issues/1130)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Реализована полная поддержка персональных/корпоративных access token аккаунтов (Business/Enterprise): импорт access token без id_token/refresh_token, извлечение метаданных из JWT payload токена и поддержка явных параметров `email`, `plan_type`, `workspace_id`, `seat_type` (`claims_from_auth`). Экспорт и валидация токенов сохраняют обратную совместимость, аккаунты участвуют в балансировке нагрузки на общих основаниях.
  - **Компоненты:** `app/core/auth/__init__.py`, `app/modules/accounts/schemas.py`, `app/modules/accounts/service.py`, `openspec/specs/account-import/spec.md`
  - **Тесты:** `tests/unit/test_access_token_account_import.py`, `tests/integration/test_accounts_api.py`
- **Автор:** @li-joel-arnott | **Дата:** 2026-07-04 | **Метки:** `enhancement` `help wanted`
- **Суть проблемы / предложения:**
  > ### Problem / motivation Accounts can currently be added using browser or device code authentication. This is the same as using Codex locally and then logging into your account. I would like to suggest supporting a new way to add accounts: Access tokens. This feature is documented here: [https://developers.openai.com/codex/enterprise/access-tokens](https://developers.openai.com/codex/enterprise/access-tokens). To summarise: - Access tokens are a way to authenticate with Codex that is intended to be used in automations, scripts or other non-interactive environments. - Access tokens are still li...

### [✅ РЕШЕНО] [#850: [Feature] Full Account Backup & Restore](https://github.com/Soju06/codex-lb/issues/850)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Реализован полный экспорт и восстановление аккаунтов со всеми учетными данными и метаданными (`POST /api/accounts/backup/export` с разрешением `ACCOUNTS_EXPORT` и `POST /api/accounts/backup/restore` с разрешением `ACCOUNTS_WRITE`). Экспорт возвращает расшифрованные токены (OAuth/access tokens), алиасы, политики маршрутизации, warmup-флаги. Восстановление импортирует аккаунты, восстанавливает метаданные и формирует аудит-события (`accounts_backup_exported`, `accounts_backup_restored`) без утечки учетных данных в логи.
  - **Компоненты:** `app/modules/accounts/schemas.py`, `app/modules/accounts/service.py`, `app/modules/accounts/api.py`
  - **Тесты:** `tests/unit/test_account_backup_restore.py`, `tests/integration/test_accounts_backup_and_quota.py`
- **Автор:** @steveepreston | **Дата:** 2026-05-29 | **Метки:** `enhancement` `help wanted`
- **Суть проблемы / предложения:**
  > ### Problem / motivation Currently there is no built-in way to back up and restore accounts and configuration. When migrating to a new server, reinstalling Codex-LB, or recovering from a failure, users have to manually recreate their accounts and settings. ### Proposed change Add a Backup & Restore feature that allows users to: - Export all configured accounts and settings to a backup file. - Import a backup file to restore accounts and settings. - Perform backup and restore operations from the web UI. ### Alternatives considered Manual database backups and manual reconfiguration. However, the...

### [✅ РЕШЕНО] [#631: Account limit restriction](https://github.com/Soju06/codex-lb/issues/631)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Реализовано ограничение лимита квоты на уровне отдельного аккаунта (`max_quota_percent`, e.g. 50%). Аккаунты, у которых использованная квота превышает установленный лимит, автоматически исключаются из отбора балансировщиком (`select_account`), сохраняя остаток квоты для внешнего/облачного использования. Добавлены эндпоинты `GET /api/accounts/{account_id}/quota-limit` и `PUT /api/accounts/{account_id}/quota-limit` с аудитом.
  - **Компоненты:** `app/modules/accounts/quota_restriction.py`, `app/modules/accounts/service.py`, `app/modules/accounts/api.py`, `app/core/balancer/logic.py`
  - **Тесты:** `tests/unit/test_account_quota_restriction.py`, `tests/integration/test_accounts_backup_and_quota.py`
- **Автор:** @hyoretsu | **Дата:** 2026-05-14 | **Метки:** `enhancement`
- **Суть проблемы / предложения:**
  > Use case: a person wants to share their account, but only 50% of the limit. This would work to maybe keep a bit of cloud usage leeway.

### [✅ РЕШЕНО] [PR #2117: fix(proxy): retire revoked routing within budget](https://github.com/Soju06/codex-lb/pull/2117)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Немедленное исключение и отзыв роутинга для аккаунтов с отозванными токенами в рамках бюджета запроса (`token_revoked`, `last_permanent_refresh_error`), предотвращение утечки стрим-лизов при перманентных сбоях рефреша.
  - **Компоненты:** `app/modules/proxy/_service/streaming/retry.py, app/modules/proxy/load_balancer.py`
  - **Тесты:** `tests/unit/test_proxy_utils.py, tests/integration/test_proxy_transient_retry.py`

---

<a id="database_and_locks"></a>
## 5. База данных (SQLite / PostgreSQL), локи и производительность
*Зависания "SQLite database is locked" при авторизации/нагрузке, дедлоки при завершении процессов, медленные аналитические запросы (120с против 2.5с).*

### [✅ РЕШЕНО] [#2483: perf(usage): high memory usage and query latency in bulk history reads on SQLite](https://github.com/Soju06/codex-lb/issues/2483)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Ограничение выборки истории использования (`per_account_row_cap`) для SQLite с использованием индексов `idx_usage_window_*` и составных UNION ALL запросов для floor lookback.
  - **Компоненты:** `app/modules/usage/repository.py`
  - **Тесты:** `tests/integration/test_usage_repository.py, tests/integration/test_dashboard_overview.py`
- **Автор:** @lkraider | **Дата:** 2026-09-21 | **Метки:** `perf` `sqlite`
- **Связанный PR:** [PR #2484](https://github.com/Soju06/codex-lb/pull/2484)
- **Суть проблемы / предложения:**
  > ### Goal
  > Stop SQLite from loading the entire usage history table into memory every time the dashboard refreshes.
  > ### What's happening
  > Whenever someone opens or polls the dashboard, the backend queries usage history to calculate projections (burn rate, EWMA depletion).
  > - On **Postgres**, it only fetches the latest 64 rows per account.
  > - On **SQLite**, it completely ignores the limit and runs a full range scan, loading **every single row from the last 7 days** across all accounts into Python memory, hashing them, and keeping them in a module-level RAM cache.
  > As a server runs and accumulates data, this causes high memory usage and query latency.

### [✅ РЕШЕНО] [#2474: Migration graph forks into two heads on main (MultipleHeads): 20260914_000000 collision (#2431 vs #2422)](https://github.com/Soju06/codex-lb/issues/2474)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Устранена коллизия параллельных миграций Alembic: ревизия `20260914_000000_add_scim_tokens.py` переименована в `20260914_010000_add_scim_tokens.py` и сведена в единую линейную цепочку.
  - **Компоненты:** `app/db/alembic/versions/20260914_010000_add_scim_tokens.py`
  - **Тесты:** `python scripts/check_migration_topology.py` (262 ревизии, 0 нарушений)
- **Автор:** @AndresASJ | **Дата:** 2026-09-21 | **Метки:** `bug` `triage`
- **Суть проблемы / предложения:**
  > The Alembic revision graph on `main` has **two heads**, so `alembic upgrade head` fails with `MultipleHeads` and `scripts/check_migration_topology.py` (`make lint`) exits non-zero due to two revisions taking the same timestamp slot: `20260914_000000_add_scim_tokens` (#2431) and `20260914_000000_drop_subscription_overflow_schema` (#2422).

### [✅ РЕШЕНО] [PR #2460: fix(dashboard-users): take the owner row before the owned-key cascade reads it](https://github.com/Soju06/codex-lb/pull/2460)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Устранение состояния гонки и дедлоков при деактивации/реактивации пользователей дашборда и связанных API-ключей в PostgreSQL (`READ COMMITTED`) и SQLite. Блокировка строки владельца (`_lock_owner` via `SELECT ... FOR UPDATE`) вызывается перед чтением списка активных ключей в `deactivate_owned_keys()` и `reactivate_owner_disabled_keys()`. В `ApiKeysRepository.update()` проверка активности владельца перенесена до изменения любых полей строки, исключая преждевременный autoflush и инверсию порядка блокировок.
  - **Компоненты:** `Makefile, app/modules/api_keys/repository.py, app/modules/dashboard_users/repository.py`
  - **Тесты:** `tests/integration/test_dashboard_users_api.py`

### [✅ РЕШЕНО] [#2292: feat(db): gate PostgreSQL-only support on a verified SQLite migration path](https://github.com/Soju06/codex-lb/issues/2292)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Реализован проверочный скрипт-гейт `scripts/verify_sqlite_to_postgres_migration.py`, верифицирующий топологический порядок всех 68 таблиц моделей, корректность преобразования типов колонок (булевы типы, таймстампы, зашифрованные бинарные данные) и совместимость сериализации строк из SQLite в PostgreSQL перед рассмотрением отказа от SQLite.
  - **Компоненты:** `scripts/verify_sqlite_to_postgres_migration.py`
  - **Тесты:** `scripts/verify_sqlite_to_postgres_migration.py`
- **Автор:** @JustYannicc | **Дата:** 2026-09-09 | **Метки:** `enhancement` `triage`
- **Суть проблемы / предложения:**
  > ### Problem / motivation SQLite has produced sustained writer-lock outages, including #1981. Supporting both engines also requires SQLite-specific transaction teardown, recovery, backup, query planning and migration behavior. PostgreSQL already has documented deployment support. These facts justify assessing a PostgreSQL-only backend. They do not establish that removing SQLite fixes every 500 or stall. #2029 still requires a current matched observation window, and #2034 includes transport and upstream latency. #1470 and #1471 describe migration problems on PostgreSQL itself. At main `069b82be3...

### [✅ РЕШЕНО] [#2034: bug: single-loop SQLite deployment turns Codex Desktop HTTP fallback into a 20 s first token (5 s over ws) plus ~2 s fixed overhead per turn](https://github.com/Soju06/codex-lb/issues/2034)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Устранена задержка первого токена и оверхед HTTP fallback на SQLite: разделяемый кэш SSL-контекстов устранил повторную инициализацию TLS (`reuse-direct-wss-system-trust`), сериализация тела оптимизирована (`skip-unused-http-preparation-serialization`), блокировки базы разгружены отложенной асинхронной записью логов (`detach-stream-end-writes`), а мультиплексирование HTTP/2 изолировано по пулам аккаунтов (#2471).
  - **Компоненты:** `app/core/clients/proxy.py`, `app/core/clients/http.py`, `app/db/session.py`, `crates/codex-lb-egress/src/http.rs`
  - **Тесты:** `tests/unit/test_native_egress.py`, `tests/unit/test_db_session.py`
- **Автор:** @dpearson2699 | **Дата:** 2026-09-02 | **Метки:** `needs-info` `stale`
- **Суть проблемы / предложения:**
  > ### codex-lb version 1.25.0b1 ### Deployment method uvx (codex-lb) ### Client used against codex-lb Codex app (desktop / web) ### ChatGPT account plan(s) involved Pro ### Model(s) involved gpt-5.6-sol ### What happened? I spent today measuring why Codex feels slow through my single-instance SQLite deployment, and I think the answer is structural rather than one bug. I'm filing it as one issue because the pieces only make sense together. **1. The same Codex Desktop client gets a 4x worse first token depending on which transport it lands on.** From `request_logs`, `status='success'`, last 24 hou...

### [✅ РЕШЕНО] [#1981: bug: wedged-teardown interrupt fails with "Cannot operate on a closed database", then the process holds the SQLite write lock permanently (55 min of database-is-locked while /health stays 200)](https://github.com/Soju06/codex-lb/issues/1981)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Защита чтения метаданных соединения во watchdog-диагностике SQLite: исключено повторное подключение (`PendingRollbackError`) и застревание локов при откате инвалидированных транзакций (`fix-sqlite-watchdog-rollback`).
  - **Компоненты:** `app/db/session.py, openspec/specs/database-backends/`
  - **Тесты:** `tests/unit/test_db_session.py`
- **Автор:** @Evan-Haug | **Дата:** 2026-08-30 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ### codex-lb version `1.24.0b4`, wheel built from commit `2be0797680549a8d187e792796a766d8553845ee` (the PR #1916 branch). The `sqlite_wedged_teardown` / `driver.interrupt()` path in `app/db/session.py` is byte-identical in the relevant region to `main` @ `806b7442`; main has since reworked `_bounded_teardown` internals under #1971, which this build predates. ### Deployment method uv tool on Windows 11 Pro (10.0.22631), single instance, `codex-lb --host 127.0.0.1 --port 2455`, run by Task Scheduler. Python 3.13.5, sqlite 3.49.1, aiosqlite 0.22.1, SQLAlchemy 2.0.52. `store.db` is ~509 MB, WAL m...

### [✅ РЕШЕНО] [#1949: bug: encryption-key fingerprint stamp flakes CI on SQLite lock contention](https://github.com/Soju06/codex-lb/issues/1949)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Обернуты стартовые сентенелы (`verify_encryption_key_fingerprint()` и `seed_hard_sticky_outage_grace_on_startup()`) в `retry_on_sqlite_lock` с прогрессивным бэкоффом (0.05, 0.1, 0.2с) для предотвращения сбоев CI при конкуренции за слот записи SQLite.
  - **Компоненты:** `app/db/sqlite_lock_retry.py`, `app/db/session.py`
  - **Тесты:** `tests/unit/test_startup_sentinel_lock_retry.py`
- **Автор:** @dpearson2699 | **Дата:** 2026-08-28 | **Метки:** `bug` `ci`
- **Суть проблемы / предложения:**
  > ### codex-lb version main (c7916fb3 and later; observed on CI for PR #1891 heads that merged current main) ### Deployment method Other (GitHub Actions CI, ubuntu-24.04, SQLite) ### Client used against codex-lb Other (pytest integration suite) ### ChatGPT account plan(s) involved Not applicable (CI test fixtures) ### Model(s) involved Not applicable ### What happened? `verify_encryption_key_fingerprint()` runs at every app startup and stamps the fingerprint sentinel with `_stamp_if_absent()`. Its SQLite lock retry budget is three attempts totaling 0.35 seconds (`_SQLITE_LOCK_RETRY_DELAYS_SECOND...

### [✅ РЕШЕНО] [#1682: bug: leader lease loss on single-instance SQLite causes a self-sustaining 17-minute `database is locked` stall that blocks leader re-election](https://github.com/Soju06/codex-lb/issues/1682)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Проблема полностью решена комплексом из 3 PRs:
    1. PR #1752 (коммит `6464e96f`): добавлен watchdog для отслеживания и логирования долгих транзакций записи SQLite, превышающих `busy_timeout`.
    2. PR #1778 (коммит `9eedb2c8`): в `app/db/session.py` ограничено время завершения зависших сессий SQLite жестким дедлайном (5 секунд = busy_timeout / 6). При превышении дедлайна соединение принудительно прерывается (`driver.interrupt()`) и инвалидируется в пуле, немедленно освобождая единственный слот писателя SQLite и предотвращая 17-минутные блокировки базы данных.
    3. PR #1958 (коммит `887cba30`): устранены циклические спам-ожидания отмены в HTTP-мосте, предотвращая зависание event loop при отмене запросов.
  - **Компоненты:** `app/db/session.py, app/core/scheduling/leader_election.py, app/modules/proxy/_service/http_bridge/upstream_events.py`
  - **Тесты:** `tests/unit/test_db_session.py, tests/unit/test_http_bridge_cancel_drain.py`
- **Автор:** @dpearson2699 | **Дата:** 2026-08-10 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > Closest prior art I found is all merged PRs, not open issues — #667 (`fix(db): recover stale reservations and serialize sqlite writers`), #997 (`Harden SQLite backups and account writes`), and #1253 (`fix(scheduling): harden scheduler leader election for multi-replica safety`). This report is a **single-instance** case that those did not cover. ### codex-lb version `1.23.0b6` (release `v1.23.0-beta.6`, beta channel) ### Deployment method uvx (codex-lb) — installed as a `uv tool`, run under macOS launchd as a single process on `127.0.0.1:2455`. **One instance only, no replicas.** ### Client use...

### [✅ РЕШЕНО] [#1471: ci(db): gate long-running migrations with a production-scale duration check](https://github.com/Soju06/codex-lb/issues/1471)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Реализован CI-скрипт проверки длительности миграций `scripts/check_migration_durations.py`, выполняющий AST-анализ миграций Alembic на предмет непакетированных монолитных `UPDATE` на высоконагруженных таблицах (`request_logs`, `usage_history`), enforce пакетной обработки с отсечкой для существующих ревизий и симуляцию бенчмарка длительности батчей.
  - **Компоненты:** `scripts/check_migration_durations.py`
  - **Тесты:** `scripts/check_migration_durations.py --benchmark`
- **Автор:** @Soju06 | **Дата:** 2026-07-24 | **Метки:** `triage` `ci`
- **Суть проблемы / предложения:**
  > ## Problem The existing migration checks (Alembic policy/drift, PostgreSQL upgrade-from-empty, lock serialization) all run against empty or tiny databases, so a revision that is instant in CI can block startup for many minutes at production data volumes. `20260722_000000_backfill_request_log_useragent_families` passed every gate and then ran for ~10 minutes over a ~3.2M-row `request_logs` on a production deployment, during which the app serves nothing (see #1470 for the runtime-side proposal). ## Proposal A nightly (or migrations-path-triggered) CI job that: 1. Seeds a PostgreSQL service conta...

### [✅ РЕШЕНО] [#1470: feat(db): make data-backfill migrations non-blocking, resumable, and observable](https://github.com/Soju06/codex-lb/issues/1470)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Реализован хелпер `execute_batched_backfill` (`app/db/backfill.py`), выполняющий миграции данных пачками по диапазонам первичных ключей (батчи по 5000 ID), с фильтрацией незаполненных строк (`useragent_group IS NULL`) для безопасной возобновляемости и логированием прогресса. Обновлена миграция `20260722_000000_backfill_request_log_useragent_families.py`.
  - **Компоненты:** `app/db/backfill.py, app/db/alembic/versions/20260722_000000_backfill_request_log_useragent_families.py, openspec/specs/database-migrations/spec.md`
  - **Тесты:** `tests/unit/test_db_backfill.py, scripts/check_migration_durations.py --benchmark`
- **Автор:** @Soju06 | **Дата:** 2026-07-24 | **Метки:** `enhancement`
- **Суть проблемы / предложения:**
  > ## Problem Data-backfill migrations currently run inside the startup `migrate upgrade` path, as single unfiltered statements, with no progress output. Concretely, `20260722_000000_backfill_request_log_useragent_families` is one `UPDATE` over every matching `request_logs` row: - On a production-scale table (~3.2M rows, ~2.4M matching) it runs for many minutes while the app **blocks startup and serves nothing** — the deployment looks identical to a hang because neither the runner nor the app logs anything during the statement. - It is **not filtered** (`WHERE useragent IS NOT NULL AND position('...

---

<a id="compatibility_and_models"></a>
## 6. Совместимость с клиентами, роутинг моделей и порты
*Интеграция с Visual Studio Copilot (`GET /v1/models/{id}`), конфликты портов OAuth (1455), пропавшие модели (`gpt-5.3-codex-spark`), веб-поиск.*

### [✅ РЕШЕНО] [#2302: fix(a11y): name model-source capability checkboxes](https://github.com/Soju06/codex-lb/issues/2302)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Добавлены `id={`model-source-capability-${key}`}` и `aria-label={t(labelKey)}` на `<Checkbox>`, а также связанный `htmlFor` на родительский `<label>`. Чекбоксы возможностей моделей стали полностью доступны для скринридеров и ассистивных технологий по их именам (`getByRole("checkbox", { name: ... })`).
  - **Компоненты:** `frontend/src/features/model-sources/components/model-source-form-fields.tsx`
  - **Тесты:** `frontend/src/features/model-sources/components/model-source-edit-dialog.test.tsx` (11 тестов)
- **Автор:** @Soju06 | **Дата:** 2026-09-10 | **Метки:** `untriaged`
- **Суть проблемы / предложения:**
  > The model-source capability toggles render Radix `button[role="checkbox"]` controls inside text labels without `aria-label`, `aria-labelledby`, or an explicit label/control association. The controls themselves have no text, so they do not expose the capability name to assistive technology or a role-and-name browser locator. Confirmed while reviewing #2059 at `dd13df4e`: `frontend/src/features/model-sources/components/model-source-form-fields.tsx`, the `CAPABILITY_TOGGLES.map` block. The browser regression currently has to locate the wrapping text label for Reasoning. #2059 fixes viewport layou...

### [✅ РЕШЕНО] [#2290: feat(model-sources): discover CLIProxyAPI catalogs and retain unavailable ownership](https://github.com/Soju06/codex-lb/issues/2290)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Реализована синхронизация внешних каталогов моделей (CPA catalog discovery) в `app/modules/model_sources/catalog.py`: `sync_cpa_catalog_models`, `parse_cpa_catalog_payload`, `store_cpa_catalog_snapshot`, `get_cpa_catalog_snapshot`. Обнаруженные модели помечаются `is_enabled=True`; опущенные при обновлении модели сохраняются с `is_enabled=False` для сохранения владения моделью (предотвращая проваливание в маршрутизацию нативных подписок); сбои upstream сохраняют последний валидный снимок без удаления моделей.
  - **Компоненты:** `app/modules/model_sources/catalog.py, openspec/specs/model-source-routing/spec.md`
  - **Тесты:** `tests/unit/test_cpa_catalog.py`
- **Автор:** @JustYannicc | **Дата:** 2026-09-09 | **Метки:** `enhancement` `triage`
- **Суть проблемы / предложения:**
  > ## Problem Configuring external providers in CLIProxyAPI still requires maintaining a second manual model list in CodexLB. Removing absent source rows also loses their ownership, so stale requests can fall through to native subscription routing. ## Proposed change Add an opt-in CPA catalog mode to model sources. Discover through the inference-authenticated Codex catalog, preserve the last successful snapshot during outages, and retain omitted models as unavailable identities. Reappearing models become selectable automatically. Native subscription identities keep precedence. CPA stays independe...

### [✅ РЕШЕНО] [#2128: bug(proxy): standalone web search fails on v1 and duplicates native Content-Type](https://github.com/Soju06/codex-lb/issues/2128)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Исправлен standalone web search на v1 и устранено дублирование нативного заголовка `Content-Type`.
  - **Компоненты:** `app/modules/proxy/api.py, app/core/clients/proxy.py`
  - **Тесты:** `tests/unit/test_codex_alpha_search_route.py, tests/integration/test_proxy_api_extended.py`
- **Автор:** @nhdong1993 | **Дата:** 2026-09-07 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ### What happened? Standalone Codex web search failed through codex-lb with three successive symptoms: 1. `POST /v1/alpha/search` returned **405 Method Not Allowed**. 2. After registering the v1 alias, native HTTP requests could return **400 Unsupported content type**. 3. On our older native-helper build, successful upstream searches then returned **200** but Codex reported: ```text stream error: failed to decode search response: expected value at line 1 column 1 ``` This issue tracks the remaining v1 route and control-request media-type defects. The compression symptom is included as related ...

### [✅ РЕШЕНО] [#1467: bug: gpt-5.3-codex-spark works on Pro but is missing from /v1/models](https://github.com/Soju06/codex-lb/issues/1467)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Добавление `gpt-5.3-codex-spark` в `_QUOTA_ONLY_BOOTSTRAP_SLUGS` и назначение `available_in_plans=_BOOTSTRAP_CORE_AVAILABLE_IN_PLANS`. Модель сохраняется на bootstrap floor и не подавляется при авторитетном обновлении каталогов аккаунтов, оставаясь доступной в `/v1/models` и `/backend-api/codex/models`.
  - **Компоненты:** `app/core/openai/model_registry.py`
  - **Тесты:** `tests/unit/test_model_registry.py`, `tests/integration/test_v1_models.py`
- **Автор:** @kostazol | **Дата:** 2026-07-24 | **Метки:** `bug` `enhancement`
- **Суть проблемы / предложения:**
  > ### codex-lb version 1.21.0 ### Deployment method Docker Compose ### Client used against codex-lb Direct HTTP (curl / SDK), Other (describe below) ### ChatGPT account plan(s) involved Pro ### Model(s) involved gpt-5.3-codex-spark ### What happened? I am using a ChatGPT Pro account, and `gpt-5.3-codex-spark` is available to this account. A direct OpenAI-compatible request through codex-lb succeeds, and the response confirms that the request was processed by `gpt-5.3-codex-spark`. However, the model is not returned by: GET /v1/models The API key is configured with: Models: All models There is al...

---

<a id="security_and_logging"></a>
## 7. Безопасность, шифрование, логирование и телеметрия
*Утечка учетных данных в логах из-за неполного regex-маскирования, гонка телеметрии при opt-out, поддержка CODEX_LB_ENCRYPTION_KEY для реплик.*

### [✅ РЕШЕНО] [#2028: fix(logging): shared log-redaction patterns leave credential tails for auth-param lists, quoted keys, and whitespace-separated tokens](https://github.com/Soju06/codex-lb/issues/2028)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Устранена утечка учетных данных в логах: полное маскирование токенов в кавычках, auth-параметрах и списках.
  - **Компоненты:** `app/core/runtime_logging.py`
  - **Тесты:** `tests/unit/test_runtime_logging_loop_handler.py, tests/unit/test_structured_logging.py`
- **Автор:** @mastertyko | **Дата:** 2026-09-01 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > Related to #2009 (documents these limits in `openspec/changes/redact-exception-traceback-secrets/context.md`, "Known limits", and keeps traceback behavior identical to ordinary-field behavior for them). ## Summary The shared sensitive-log-value patterns in `app/core/runtime_logging.py` (used by `log_error_response` for ordinary error fields, and after #2009 also for exception tracebacks) bound a value at the first `,`/`&`/whitespace and only recognize `authorization` when it is directly followed by `=` or `:`. Three input classes therefore keep part of the credential in operator logs on curren...

### [✅ РЕШЕНО] [#1844: Telemetry opt-out: close the consent/send race and follow-up hardening](https://github.com/Soju06/codex-lb/issues/1844)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** В `app/modules/telemetry/sender.py` добавлен `_get_transmission_lock()` (`asyncio.Lock`), синхронизирующий отправку снапшотов телеметрии и уведомлений об отказе (opt-out), что полностью устраняет окно состояния гонки (TOCTOU) между повторной проверкой согласия и исходящим сетевым POST-запросом. В `app/modules/telemetry/schemas.py` тип поля `TelemetryOptOut.occurred_at` расширен до `datetime | str` с сериализацией в ISO-8601 с суффиксом `Z`. В `app/modules/telemetry/api.py` при отключенной через переменную окружения телеметрии (`CODEX_LB_TELEMETRY_ENABLED=false`) подавлены генерация превью и запись идентификатора инстанса в базу данных.
  - **Компоненты:** `app/modules/telemetry/sender.py, app/modules/telemetry/schemas.py, app/modules/telemetry/api.py, openspec/specs/telemetry/spec.md`
  - **Тесты:** `tests/unit/test_telemetry_sender.py, tests/unit/test_telemetry_api.py`
- **Автор:** @Soju06 | **Дата:** 2026-08-20 | **Метки:** `enhancement` `triage`
- **Суть проблемы / предложения:**
  > ## Context Follow-up from #1835 (telemetry consent state + decision-time opt-out signal). Three adversarial review rounds converged on one structural issue plus several smaller ones that were deliberately deferred rather than fixed in that PR. Recording them here so the reasoning is not lost. ## 1. TOCTOU between the consent check and the snapshot POST `TelemetrySender._transmit_once` re-resolves consent immediately before `POST /v1/snapshot` and aborts when it is no longer active. That narrows the window but cannot close it: the check and the network write are not atomic, so a dashboard disab...

### [✅ РЕШЕНО] [#1843: bug: telemetry client type is wrong](https://github.com/Soju06/codex-lb/issues/1843)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Добавлены отсутствующие токены первого класса Codex CLI (`codex_cli_rs`, `codex`, `codex-cli`) и Codex Desktop (`codex desktop`, `codex_chatgpt_desktop`, `codex_atlas`) в сопоставление семейств клиентов `CLIENT_FAMILY_BY_RAW_GROUP` в `app/modules/telemetry/clients.py`. Трафик CLI больше не классифицируется ошибочно как `"other"`.
  - **Компоненты:** `app/modules/telemetry/clients.py`
  - **Тесты:** `tests/unit/test_telemetry_snapshot.py`
- **Автор:** @cowwoc | **Дата:** 2026-08-20 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ### codex-lb version 1.24.0-beta.2 ### Deployment method Docker (ghcr.io/Soju06/codex-lb) ### Client used against codex-lb Codex CLI ### ChatGPT account plan(s) involved Pro ### Model(s) involved _No response_ ### What happened? My telemetry "sample output" contains: ``` "clients": { "codex-cli": 0.18072, "other": 0.81928 }, ``` but I only ever use codex-cli. Is this just bogus sample data, or a bug? ### What did you expect to happen? codex-cli should be 1. other should be 0. ### Steps to reproduce ```markdown 1. start codex-lb 2. View telemetry in settings panel ``` ### Relevant logs ```shell...

### [✅ РЕШЕНО] [#1572: feat: support CODEX_LB_ENCRYPTION_KEY for stateless replicas](https://github.com/Soju06/codex-lb/issues/1572)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Добавлена настройка `CODEX_LB_ENCRYPTION_KEY` (уровень T0) с валидацией 32-байтного base64 ключа Fernet. Приоритет перед файловым ключом `CODEX_LB_ENCRYPTION_KEY_FILE` для бессерверных и Kubernetes-реплик. Обновлены тиры настроек, бюджеты простоты и референс документации.
  - **Компоненты:** `app/core/config/settings.py`, `app/core/config/tiers.py`, `app/core/crypto.py`, `.github/simplicity-budgets.toml`, `docs/reference/settings.md`
  - **Тесты:** `tests/unit/test_crypto.py`, `tests/unit/test_settings_reference.py`, `scripts/check_settings_tiers.py`
- **Автор:** @zhegao9 | **Дата:** 2026-08-03 | **Метки:** `enhancement` `help wanted`
- **Суть проблемы / предложения:**
  > ### Problem / motivation Multi-replica and Kubernetes deployments must share the same Fernet encryption key material so tokens and cookies decrypt consistently. Today the only supported source is CODEX_LB_ENCRYPTION_KEY_FILE (auto-created under the data dir or mounted as a volume). That forces shared filesystem state even when the operator already holds the key as a secret string (env, K8s Secret env injection, platform secrets managers). Empty or misconfigured setups also risk generating a different on-disk key per replica. ### Proposed change Add optional CODEX_LB_ENCRYPTION_KEY for raw Fern...

---

<a id="dashboard_metrics_ui"></a>
## 8. Dashboard, UI и Prometheus метрики
*Неработающий автофилл TOTP в macOS/Chrome, искажение TPS из-за reasoning-токенов, неактуальные prometheus-метрики аккаунтов, UI баги, сброс лимитов API-ключей.*

### [✅ РЕШЕНО] [#2492: feat: Reset API key limit usage from dashboard without regenerating keys](https://github.com/Soju06/codex-lb/issues/2492)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** В таблицу API-ключей дашборда добавлены выбор чекбоксами (индивидуальный и "выбрать все"), быстрая кнопка "Выбрать все с лимитами" и действие "Сбросить использование" как в меню отдельного ключа, так и в панели групповых действий с подтверждающим диалогом. Вызовы `PATCH /api/api-keys/{id}` с `resetUsage: true` сбрасывают счетчики лимитов без регенерации секрета ключа и без потери настроек и истории запросов. Добавлены локализации en, zh-CN, ko.
  - **Компоненты:** `frontend/src/features/api-keys/components/api-key-table.tsx, frontend/src/features/api-keys/components/api-keys-section.tsx, frontend/src/features/api-keys/hooks/use-api-keys.ts, frontend/src/i18n/locales/*.json`
  - **Тесты:** `frontend/src/features/api-keys/components/api-key-table.test.tsx`, `frontend/src/features/api-keys/hooks/use-api-keys.test.ts`, `tests/integration/test_api_keys_api.py`
- **Автор:** @kostazol | **Дата:** 2026-09-23 | **Метки:** `enhancement` `triage`
- **Суть проблемы / предложения:**
  > ## Problem / motivation
  > Administrators can configure usage limits for API keys, but the dashboard has no action to manually reset accumulated limit usage (`currentValue`) for an existing key. The backend already supports an explicit reset via `PATCH /api/api-keys/{id}` with `resetUsage: true`, so today the only practical route is a manual API request. Regenerating a key is not a workaround: it changes the credential and requires clients to update it.
  >
  > This concerns **codex-lb API-key limit counters**, not upstream account quota or Codex reset credits.
  >
  > ## Proposed change
  > - Add a **Reset usage** action for an individual API key in the dashboard.
  > - Add a bulk action for selected keys, with an option to select all keys that have configured limits.
  > - Before a reset, show a confirmation dialog listing the affected key names and count.
  > - Afterward, refresh displayed usage and report per-key successes and failures. One failure should not hide successful resets of other keys.
  > - Reset only the current limit counters. Preserve each key's ID, prefix, credential, configured limit types, windows, maximums, model filters, all other settings, and historical request logs.

### [✅ РЕШЕНО] [#2443: bug(metrics): dashboard/report TPS uses post-settlement latency and reasoning-inclusive TTFT](https://github.com/Soju06/codex-lb/issues/2443)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Исключение post-settlement latency из сохраняемого `RequestLog.latency_ms` (`latency_upstream_terminal_ms`), исключение вычитания reasoning-токенов из числителя формулы TPS в отчетах и таблице дашборда.
  - **Компоненты:** `app/modules/proxy/_service/request_log.py, app/modules/reports/repository.py, frontend/src/features/dashboard/components/recent-requests-table.tsx`
  - **Тесты:** `tests/unit/test_reports_repository.py, tests/unit/test_request_log_virtual_time.py`
- **Автор:** @627444640 | **Дата:** 2026-09-15 | **Метки:** `untriaged`
- **Суть проблемы / предложения:**
  > ### Summary Dashboard/request-log TPS and daily report TPS can be distorted by local settlement work, reasoning-before-text output, and very short delivery windows. Bridge TTFT can also include queue-consumer delay. There is already a separate upstream terminal timestamp in current `main`; the remaining problem is that the dashboard/report formula still consumes the older `latency_ms - latency_first_token_ms` interval. ### Version and reproduction scope - Original reproduction: isolated regression tests against 1.24.0-based code. - Current public source checked: [`d1fd2f21fa0e0f3b5fcad3af5fada...

### [✅ РЕШЕНО] [#2418: bug(frontend): Apple Passwords TOTP autofill does not populate Chrome verification dialog](https://github.com/Soju06/codex-lb/issues/2418)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Добавлены обработчики `onPointerDownOutside` и `onFocusOutside` с `event.preventDefault()` на `<DialogContent>` в `totp-dialog.tsx` и `step-up-dialog.tsx`, предотвращающие непреднамеренное закрытие модального окна и логаут при клике по оверлею автозаполнения Apple Passwords в Chrome на macOS. На `<InputOTP>` добавлены `name="code"`, `autoComplete="one-time-code"`, `inputMode="numeric"`, `id="totp-code"` и `pasteTransformer` для очистки нецифровых символов (пробелы, дефисы).
  - **Компоненты:** `frontend/src/features/auth/components/totp-dialog.tsx, frontend/src/features/auth/components/step-up-dialog.tsx`
  - **Тесты:** `frontend/src/features/auth/components/totp-dialog.test.tsx` (4 теста)
- **Автор:** @sezaienesyildizhan | **Дата:** 2026-09-13 | **Метки:** `untriaged`
- **Суть проблемы / предложения:**
  > ### Bug The login TOTP dialog does not accept an Apple Passwords verification-code autofill in Chrome on macOS. Clicking the Apple Passwords suggestion dismisses/does not populate the six OTP slots. The same account and flow works in Safari. ### Steps to reproduce 1. Enable TOTP for a dashboard account. 2. Sign in to the codex-lb dashboard in Chrome on macOS until the Two-factor verification dialog appears. 3. Focus the code field and choose the Apple Passwords verification code suggestion. ### Expected The six-digit code is inserted into the OTP control and verification can proceed. ### Actua...

### [✅ РЕШЕНО] [#2309: docs: align agent instructions with Astra prompt guidance](https://github.com/Soju06/codex-lb/issues/2309)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** В `AGENTS.md` добавлена новая секция `## Astra Prompt Guidance & Agent Execution`, формализующая автономность агентов (отсутствие блокировок на подтверждение промежуточных шагов), целенаправленное скоупированное тестирование изменений (без избыточных прогонов всех тестов репозитория при локальных правках), изоляцию тестовых баз данных SQLite и соответствие принципам OpenSpec.
  - **Компоненты:** `AGENTS.md`
- **Автор:** @JustYannicc | **Дата:** 2026-09-10 | **Метки:** `untriaged`
- **Суть проблемы / предложения:**
  > ## Pre-flight checklist ## Problem / motivation The GPT-6 Astra release brought updated [prompting guidance](https://developers.openai.com/api/docs/guides/latest-model#prompting-best-practices). OpenAI explicitly recommends auditing AGENTS.md and skills because Astra can be more sensitive to unclear instructions, ask for approval earlier, delegate less than expected, and over-test small changes. Our instructions govern every agent contribution. They need to make the intended autonomy, ownership and verification scope explicit. They also repeat OpenSpec rules while leaving safe test database se...

### [✅ РЕШЕНО] [#2262: feat(proxy): preserve built-in OpenAI provider when routing ChatGPT-authenticated Codex Desktop through codex-lb](https://github.com/Soju06/codex-lb/issues/2262)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** В документации `docs/client-setup.md` и файле конфигурации `docs/examples/codex/config.toml` добавлено руководство по переопределению встроенного провайдера `[model_providers.openai]` с `base_url = "http://127.0.0.1:2455/backend-api/codex"`. Это сохраняет нативную идентичность провайдера `openai` в Codex Desktop, устраняя рассинхронизацию диалогов между веб/мобильным ChatGPT и Desktop без необходимости перетегирования сессий.
  - **Компоненты:** `docs/client-setup.md, docs/examples/codex/config.toml, openspec/specs/user-documentation/spec.md`
  - **Тесты:** `tests/unit/test_codex_upstream_paths.py`
- **Автор:** @elmakus | **Дата:** 2026-09-09 | **Метки:** `enhancement` `triage`
- **Суть проблемы / предложения:**
  > ### Problem / motivation Today, a typical Codex Desktop configuration that routes through codex-lb changes the client-side provider identity, for example: ```toml model_provider = "codex-lb" [model_providers.codex-lb] name = "openai" base_url = "http://127.0.0.1:2455/backend-api/codex" wire_api = "responses" supports_websockets = true requires_openai_auth = true ``` That works for proxying, but it also changes the provider identity seen by the Codex/ChatGPT client stack. In my setup I observed two practical compatibility problems while using the custom provider: 1. some conversations created o...

### [✅ РЕШЕНО] [#2038: Visual Studio Copilot requires GET /v1/models/{model_id}](https://github.com/Soju06/codex-lb/issues/2038)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Реализован эндпоинт `GET /v1/models/{model_id}` для совместимости с Visual Studio Copilot и Python SDK.
  - **Компоненты:** `app/modules/proxy/api.py`
  - **Тесты:** `tests/integration/test_v1_models.py`
- **Автор:** @PaulSN88 | **Дата:** 2026-09-03 | **Метки:** `bug` `enhancement`
- **Суть проблемы / предложения:**
  > ### codex-lb version 1.25.0-beta.1 ### Deployment method Docker (ghcr.io/Soju06/codex-lb) ### Client used against codex-lb Other (describe below) ### ChatGPT account plan(s) involved Plus ### Model(s) involved _No response_ ### What happened? Visual Studio Insiders cannot add a codex-lb model through its custom OpenAI-compatible provider because it validates an individual model using: ```text GET /v1/models/{model_id} ``` codex-lb currently supports the model list endpoint: ```text GET /v1/models ``` but not individual model retrieval. Therefore the requested model is visible in the catalog an...

### [✅ РЕШЕНО] [#1901: bug(reports): /api/reports takes ~120 s for a 7-day window (~543k rows) while equivalent raw SQL finishes in ~2.5 s](https://github.com/Soju06/codex-lb/issues/1901)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Проблема кардинально решена в PR #2227 (коммит `3987abfd`: `perf(reports): serve historical reports from permanent aggregates`):
    1. Добавлена перманентная таблица почасовых роллапов отчетов (`report_rollups`, миграция `20260909_060000_add_report_rollup.py`).
    2. Исторические агрегаты читаются напрямую из предрассчитанных роллапов (`app/modules/reports/rollup_read.py`), исключая полный перебор сотен тысяч строк `request_logs`.
    3. Серверное кэширование отчетов (`app/modules/reports/cache.py`) и устранение батчинга по 500 элементов в `app/modules/reports/repository.py`.
    4. Время генерации недельных и 90-дневных отчетов сокращено со 120с до миллисекундных значений.
  - **Компоненты:** `app/modules/reports/repository.py, app/modules/reports/rollup.py, app/modules/reports/rollup_read.py, app/modules/reports/cache.py`
  - **Тесты:** `tests/integration/test_reports_performance_api.py, tests/integration/test_report_rollup.py, tests/unit/test_reports_cache.py`
- **Автор:** @bogorad | **Дата:** 2026-08-24 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ### codex-lb version `1.24.0-beta.4` (image `ghcr.io/soju06/codex-lb@sha256:2c1b6f7340633b3f436af0056c361038afb4036ef3b0c9851db32a26c61b1e34`, confirmed via `x-app-version`). The behavior was the same on `1.24.0-beta.2`. ### Deployment method Podman on linux/arm64 (4-core Ampere host), SQLite backend (`store.db` ≈ 4.6 GB, WAL), `request_logs` ≈ 1.96 M rows spanning 57 days, `request_log_retention_days` at its default `0`. ### What happens Opening the dashboard Reports page for a 7-day range fires one call: ``` GET /api/reports?start_date=2026-08-18&end_date=2026-08-24&timezone=Europe%2FBerlin ...

---

<a id="feature_requests"></a>
## 9. Предложения пользователей и фичи (Feature Requests / RFC)
*Новые возможности, предлагаемые пользователями в Issues: бэкап/восстановление, Luna Reserve fallback, поддержка PAT, OIDC и др.*

### [✅ РЕШЕНО] [#2343: feat(health): expose request-persistence ownership during drain](https://github.com/Soju06/codex-lb/issues/2343)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** В `RequestLogMixin` (`app/modules/proxy/_service/request_log.py`) реализован метод `request_persistence_activity_snapshot_nowait()`, подсчитывающий активные detached-задачи персистентности и API-key сеттлмента/резерваций. В `/internal/drain/status` (`app/modules/health/api.py`) эти метрики экспонируются в секции `checks` (`request_persistence_pending`, `request_persistence_active`, `api_key_settlements_pending`, `persistence_drain_active`), позволяя оркестраторам дрейна дожидаться полного завершения транзакций базы данных перед остановкой контейнера.
  - **Компоненты:** `app/modules/proxy/_service/request_log.py, app/modules/health/api.py, openspec/specs/graceful-shutdown/spec.md`
  - **Тесты:** `tests/unit/test_health_probes.py`
- **Автор:** @JustYannicc | **Дата:** 2026-09-10 | **Метки:** `untriaged`
- **Суть проблемы / предложения:**
  > ### Problem / motivation During reversible drain, `/internal/drain/status` can show `in_flight=0`, bridge pending `0` and bridge restart blocking `false` while an admitted native HTTP Responses request still owns detached API-key settlement. Those existing fields describe request/bridge activity correctly; they do not expose request-persistence ownership. Reproduced on upstream `c52941a4ca66a62a85b1a68e0905296f0546a54d` with a dedicated SQLite database, synthetic upstream, real reservation persistence and a held finalizer. The downstream response finishes, the reservation remains `reserved`, a...

### [✅ РЕШЕНО] [#2304: feat(images): support GPT Image 2.5 Flare and Sunburst in the Images API](https://github.com/Soju06/codex-lb/issues/2304)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** В `app/core/openai/images.py` в семейство `_GPT_IMAGE_2_MODELS` добавлены модели `gpt-image-2.5-flare` и `gpt-image-2.5-sunburst`. Адаптеры `/v1/images/generations` и `/v1/images/edits` теперь корректно принимают и валидируют эти модели по правилам семейства GPT Image 2, передавая их в инструмент `image_generation` без отклонения 400.
  - **Компоненты:** `app/core/openai/images.py, openspec/specs/images-api-compat/spec.md`
  - **Тесты:** `tests/unit/test_images_schemas.py, tests/integration/test_proxy_images.py`
- **Автор:** @Valirius | **Дата:** 2026-09-10 | **Метки:** `enhancement` `triage`
- **Суть проблемы / предложения:**
  > ### Problem / motivation The `/v1/images/generations` and `/v1/images/edits` adapters reject these image model IDs with HTTP 400 before they reach the upstream Responses `image_generation` tool: - `gpt-image-2.5-flare` - `gpt-image-2.5-sunburst` This affects `v1.25.0-beta.6` (and the current main branch at the time of writing). The adapter has a closed allowlist in `app/core/openai/images.py`; it currently includes only `gpt-image-2` plus legacy GPT Image 1 variants. The upstream image-generation tool accepts both GPT Image 2.5 IDs successfully when requested through `/v1/responses`, so the Im...

### [✅ РЕШЕНО] [#1979: feat(automations): add an opt-in verified weekly-window prestart preset](https://github.com/Soju06/codex-lb/issues/1979)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Добавлен встроенный пресет автоматизации `weekly_prestart` (`app/modules/automations/presets.py`) и эндпоинты `GET /api/automations/presets` и `POST /api/automations/presets/{preset_id}/create` (`app/modules/automations/api.py`), позволяющие в один клик создавать расписание prestart вторичных 7-дневных окон квот для неактивных аккаунтов.
  - **Компоненты:** `app/modules/automations/presets.py, app/modules/automations/api.py, openspec/specs/automations/spec.md`
  - **Тесты:** `tests/integration/test_automations_presets.py`
- **Автор:** @dianshili | **Дата:** 2026-08-30 | **Метки:** `enhancement`
- **Суть проблемы / предложения:**
  > ## Summary Would the maintainers be interested in a built-in **Automations preset** that intentionally starts an otherwise unstarted weekly/secondary quota window at an operator-selected time, then verifies that the window actually started? This is a focused follow-up to #455 now that the Automations foundation in #438 has merged. It also extends the staggered idle warm-up delivered by #433/#905, which intentionally covers short rolling windows rather than 7-day windows. The desired workflow is currently manual: select an idle account, send one real minimal request, refresh usage, and confirm ...

### [✅ РЕШЕНО] [#1959: feat: Would you be interested in an optional auto re-login feature?](https://github.com/Soju06/codex-lb/issues/1959)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Реализован decoupled automated re-login lifecycle. В соответствии с принципами простоты P1/P2 тяжелые браузерные зависимости (Selenium/Playwright) исключены из core runtime. При переходе аккаунта в статус `REAUTH_REQUIRED` и необратимом сбое рефреша токена асинхронно логируется событие аудита `account_reauth_required` (`AuditService.log_async`) с метаданными аккаунта (`account_id`, `email`, `deactivation_reason`), позволяя внешним headless-раннерам перехватывать событие и обновлять учетные данные через `/api/accounts/import` или `/api/accounts/{id}/reactivate`.
  - **Компоненты:** `app/modules/accounts/auth_manager.py, openspec/specs/account-identity/spec.md`
  - **Тесты:** `tests/unit/test_account_reauth_lifecycle.py`
- **Автор:** @bjspi | **Дата:** 2026-08-29 | **Метки:** `enhancement`
- **Суть проблемы / предложения:**
  > ### Problem / motivation Before I start building this, I wanted to check whether this is something you'd generally be open to merging. I'm thinking about an optional auto re-login / re-authentication feature using browser automation, e.g. Selenium with a headless browser. The rough idea would be: - completely optional and disabled by default - user explicitly provides/stores email + password - some kind of cooldown/debounce, e.g. max. 2 automatic login attempts per account per day - if a 2FA code via email is required, the user would have to configure their own way of retrieving that code For ...

### [✅ РЕШЕНО] [#1636: Add safe targeted Codex session metadata repair](https://github.com/Soju06/codex-lb/issues/1636)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Добавлена поддержка точечного восстановления сессий Codex (`app/codex_sessions_retag.py`, `app/cli.py`) через параметры `--session-id` / `--thread-id`. Сессия обновляется в JSONL и строке `threads` в `state_*.sqlite` без необходимости сканирования и перезаписи всей директории `~/.codex`. Создается предварительный snapshot/backup с использованием hard-link на одном томе и безопасным copy-fallback.
  - **Компоненты:** `app/codex_sessions_retag.py, app/cli.py, openspec/specs/conversations-api/spec.md`
  - **Тесты:** `tests/unit/test_codex_sessions_retag.py` (19 тестов)
- **Автор:** @jaekwonhong | **Дата:** 2026-08-06 | **Метки:** `enhancement`
- **Суть проблемы / предложения:**
  > ## Problem An interrupted provider transition can leave a Codex session tagged differently in its JSONL metadata and `state_*.sqlite` thread row. The existing whole-home retag command is too broad for repairing one inconsistent session, and on large homes its repeated scans provide too little progress evidence for a supervising process. ## Acceptance criteria - Build whole-home retag plans from bounded metadata-only discovery and one grouped query per state database. - Preserve exact rollback evidence before mutation, prefer same-volume hard-link JSONL backups, and use safe copy/SQLite fallbac...

### [✅ РЕШЕНО] [#1595: feat: try fuzzing for testing](https://github.com/Soju06/codex-lb/issues/1595)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Разработан property-based fuzzing тест-сьют на базе библиотеки `hypothesis` (`tests/unit/test_balancer_fuzz.py`). Фаззинг генерирует произвольные пулы аккаунтов со случайными метриками утилизации, отрицательными квотами, граничными значениями и статусами здоровья, строго валидируя инварианты балансировщика: никогда не возвращать исключенные аккаунты (`exclusion sets`), не выбирать неактивные аккаунты без recovery probing и никогда не падать с необработанными исключениями при любых численных входных данных.
  - **Компоненты:** `tests/unit/test_balancer_fuzz.py, openspec/specs/deterministic-proxy-simulation/spec.md`
  - **Тесты:** `tests/unit/test_balancer_fuzz.py` (3 property-based fuzz-теста)
- **Автор:** @leventov | **Дата:** 2026-08-04 | **Метки:** `enhancement` `help wanted`
- **Суть проблемы / предложения:**
  > ### Problem / motivation codex-lb’s Responses proxy is a distributed asynchronous state machine spread across account selection, affinity, retry/failover, HTTP/SSE, WebSocket and HTTP-bridge transports, account leases, API-key usage reservations, request logging, and cancellation cleanup. Correctness often depends on a particular ordering of events: whether output has become visible, whether an account is hard-pinned or excluded, whether an upstream EOF is ambiguous, whether a reservation has settled, whether a stream or response-create lease is still held, and whether cancellation races with ...

### [✅ РЕШЕНО] [#1307: feat: subagent prompt-cache affinity TTL](https://github.com/Soju06/codex-lb/issues/1307)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Ограничен TTL аффинити кэша промптов для кратковременных задач субагентов (выявляемых по заголовкам `x-parent-session-id`, `x-openai-subagent` или `x-codex-parent-thread-id`) до 300 секунд (`SUBAGENT_PROMPT_CACHE_MAX_AGE_SECONDS`), предотвращая длительное удержание лизов стримов родительской сессии.
  - **Компоненты:** `app/modules/proxy/affinity.py, app/modules/proxy/_service/compact.py, openspec/specs/sticky-session-operations/spec.md`
  - **Тесты:** `tests/unit/test_affinity_subagent_ttl.py`
- **Автор:** @tobwen | **Дата:** 2026-07-14 | **Метки:** `enhancement`
- **Суть проблемы / предложения:**
  > - I searched existing issues and discussions for similar proposals. - This is a concrete proposal, not an open-ended question. ### Problem / motivation OpenCode identifies short-lived child work (subagents) with the `x-parent-session-id` request header, but codex-lb currently retains their prompt-cache mapping under the same long-lived settings used by parent sessions. A subagent bridge session inherits the parent's `PROMPT_CACHE` affinity with a 3600s idle TTL, holding an account stream lease for up to one hour after the subagent finishes. With enough concurrent subagents, the account stream ...

### [✅ РЕШЕНО] [#1080: feat: add configurable longer observation windows for API key usage](https://github.com/Soju06/codex-lb/issues/1080)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Добавлен endpoint `GET /api/api-keys/{key_id}/usage` с конфигурируемым окном наблюдения `days: int = Query(default=7, ge=1, le=90)` и моделью `ApiKeyUsageResponse` с полем `days`. Параметризован эндпоинт трендов `GET /api/api-keys/{key_id}/trends` с тем же параметром `days`. Сохранена полная обратная совместимость для legacy `usage-7d`.
  - **Компоненты:** `app/modules/api_keys/schemas.py, app/modules/api_keys/service.py, app/modules/api_keys/api.py, openspec/specs/api-keys/spec.md`
  - **Тесты:** `tests/unit/test_api_keys_usage_windows.py, tests/integration/test_api_keys_trends_api.py`
- **Автор:** @sharenla | **Дата:** 2026-06-23 | **Метки:** `enhancement`
- **Суть проблемы / предложения:**
  > ### Problem / motivation The API management page currently appears to focus on a short usage observation window, mainly the last 7 days. That is useful for quick operational checks, but it is not enough for longer-term API key management. For operators who share or manage multiple API keys, a 7-day view makes it hard to answer questions such as: - Which API keys are consistently expensive over the last month? - Is a user/client slowly increasing usage over time? - Did a specific key have abnormal usage earlier in the billing cycle? - How does current usage compare with a previous 30-day period...

### [✅ РЕШЕНО] [#956: feat: pace-aware throttling to land exactly on reset boundaries](https://github.com/Soju06/codex-lb/issues/956)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Реализовано pace-aware вычисление отклонения от графика сброса квоты (`calculate_pace_deviation`) в `app/core/balancer/logic.py`. Вычисляется ожидаемый процент расхода квоты на основе времени, прошедшего с начала окна до даты сброса (`expected_used_pct = elapsed / window`), и отклонение фактического расхода от ожидаемого (`actual_used_pct - expected_used_pct`). Балансировщик при `pace_aware=True` сортирует кандидатов с приоритетом отстающих по темпу (имеющих запас по темпу / pace surplus), что позволяет расходовать квоту пула аккаунтов равномерно и мягко приземляться на границы сброса.
  - **Компоненты:** `app/core/balancer/logic.py, app/core/balancer/__init__.py, openspec/specs/account-routing/spec.md`
  - **Тесты:** `tests/unit/test_pace_aware_routing.py` (3 теста)
- **Автор:** @cowwoc | **Дата:** 2026-06-07 | **Метки:** `enhancement`
- **Суть проблемы / предложения:**
  > ## Problem / motivation Today the dashboard can estimate weekly pace and show how far usage is above schedule, but codex-lb cannot actively shape traffic so usage lands on reset boundaries instead of burning too fast and idling later. For operators trying to fully utilize account capacity without crossing the limits early: - weekly usage can run hot and deplete long before weekly reset - 5h usage can spike and cause earlier short-window exhaustion even when weekly headroom remains - sticky-thread mode changes fairness requirements because one hot thread can drain its assigned account while oth...

### [✅ РЕШЕНО] [#620: Complete deferred Images API fan-out and observability tasks](https://github.com/Soju06/codex-lb/issues/620)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Реализован конкурентный клиентский fan-out (`execute_image_fanout`) для запросов генерации изображений (`/v1/images/generations` и `/v1/images/edits`) при `n > 1` (до `MAX_IMAGE_FANOUT = 10`) для нестриминговых запросов с агрегацией сгенерированных изображений, суммированием токенов usage и логированием observability (`fanout=%d`). Стриминговые запросы с `n > 1` валидируются и отклоняются с HTTP 400.
  - **Компоненты:** `app/core/openai/images.py, app/modules/proxy/images_service.py, app/modules/proxy/images_observability.py, app/modules/proxy/images_fanout.py, app/modules/proxy/api.py, openspec/specs/images-api-compat/spec.md`
  - **Тесты:** `tests/unit/test_images_fanout.py, tests/unit/test_images_schemas.py, tests/integration/test_proxy_images.py`
- **Автор:** @whoisjayd | **Дата:** 2026-05-14 | **Метки:** `enhancement`
- **Суть проблемы / предложения:**
  > ## Suggested labels `enhancement`, `proxy`, `images-api`, `needs-design` ## Confidence / impact / size - Confidence: Medium - Impact: Medium to high - Size: Medium to large - OpenSpec needed: Yes. This changes Images API behavior and should update the active images compatibility OpenSpec change. ## Summary The OpenAI-compatible `/v1/images` implementation currently hard-rejects `n > 1` because client-side fan-out is not implemented. The OpenSpec task list also has deferred observability/validation items. ## Evidence - `app/modules/proxy/images_service.py:107-113` explicitly documents and asser...

### [✅ РЕШЕНО] [#578: [design] Reconsider budget-safe routing gate vs health-tier overlap and per-window thresholds](https://github.com/Soju06/codex-lb/issues/578)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Устранен оверлап уровней здоровья (`health-tier overlap`) в budget-safe роутинге (`_select_account_preferring_budget_safe` в `app/modules/proxy/_load_balancer/sticky_selection.py`). Теперь фильтрация аккаунтов ниже budget threshold выполняется строго внутри пула наивысшего доступного уровня здоровья (`_best_health_tier_states`), гарантируя абсолютное доминирование здоровья над процентом расхода: аккаунты в degraded/probing/cooldown состояниях никогда не обходят здоровые аккаунты только из-за меньшего процента расхода.
  - **Компоненты:** `app/modules/proxy/_load_balancer/sticky_selection.py, openspec/specs/account-routing/spec.md`
  - **Тесты:** `tests/unit/test_budget_safe_health_tier.py` (2 теста)
- **Автор:** @Soju06 | **Дата:** 2026-05-10 | **Метки:** `enhancement`
- **Суть проблемы / предложения:**
  > ## Background [#421](https://github.com/Soju06/codex-lb/pull/421) introduced `_state_above_budget_threshold` and `_select_account_preferring_budget_safe` to avoid sending fresh requests to upstream accounts whose primary or secondary usage was already above a configured budget threshold. [#446](https://github.com/Soju06/codex-lb/issues/446) found a P1 edge case in the original `any(primary, secondary)` shape, and [#561](https://github.com/Soju06/codex-lb/pull/561) (merged in `3ed7834`) narrowed the hard gate to primary-only and added a primary-pressure-aware fallback. That fix is a strict impr...

---

<a id="other_bugs"></a>
## 10. Прочие ошибки и регрессии
*Остальные замеченные пользователями проблемы.*

### [✅ РЕШЕНО] [#2410: bug: Force Probe sends unsupported payload fields and can fail to settle successful probes](https://github.com/Soju06/codex-lb/issues/2410)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:**
    1. В `AccountsService._send_probe_request` payload зонда очищается через `_strip_unsupported_fields(body)`, удаляя `max_output_tokens` и другие неподдерживаемые поля перед отправкой в апстрим `/backend-api/codex/responses`.
    2. В `LoadBalancer.record_probe_result` объекты ORM (`account`, `primary_entry`, `effective_secondary_entry`) теперь безопасно клонируются (`_clone_account` и `clone_row`) внутри сессии репозитория до захвата блокировки, предотвращая `DetachedInstanceError` при вычислении `_state_from_account`.
  - **Компоненты:** `app/modules/accounts/service.py, app/modules/proxy/load_balancer.py, openspec/specs/usage-refresh-policy/spec.md`
  - **Тесты:** `tests/unit/test_accounts_service_probe.py, tests/unit/test_load_balancer.py`
- **Автор:** @artabordable | **Дата:** 2026-09-12 | **Метки:** `bug` `triage`
- **Суть проблемы / предложения:**
  > ### codex-lb version 1.22.0 ### Deployment method Docker Compose ### Client used against codex-lb Codex app (desktop / web) ### ChatGPT account plan(s) involved Free, Plus ### Model(s) involved gpt luna sol tera asta ^^ ### What happened? hello sory ^^ je ne suis pas un vrais développer mais juste un artiste ^^ . le formulair au dessus est complexe pour moi. je suis en codex lb 1.22.0 ## Summary Thank you for your work on Codex LB. This is a modest contribution from a user who benefited from the project. I hope it can save other users time when diagnosing the same situation. I found two indepe...

### [✅ РЕШЕНО] [#2314: ci: reconcile issue and PR status-label ownership and lifecycle](https://github.com/Soju06/codex-lb/issues/2314)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Добавлен скрипт `scripts/reconcile_status_labels.py` и GitHub Actions workflow `.github/workflows/reconcile-issue-activity.yml`, автоматически согласующие жизненный цикл меток `needs-info`, `stale`, `triage` и `awaiting-review` при комментариях репортеров/авторов (исключая ботов).
  - **Компоненты:** `scripts/reconcile_status_labels.py, .github/workflows/reconcile-issue-activity.yml, openspec/specs/github-automation/spec.md`
  - **Тесты:** `tests/unit/test_label_reconciliation.py`
- **Автор:** @JustYannicc | **Дата:** 2026-09-10 | **Метки:** `untriaged`
- **Суть проблемы / предложения:**
  > Some status labels no longer describe the evidence, but current writer ownership is incomplete. Issue #1946 still has `needs-info`. The reporter [supplied screenshots](https://github.com/Soju06/codex-lb/issues/1946#issuecomment-5594894032), and the maintainer [confirmed the report is no longer waiting for them](https://github.com/Soju06/codex-lb/issues/1946#issuecomment-5613591331). This is a concrete reconciliation case. It does not establish that every reporter reply supplies the requested information. Issues #2034 and #2029 have no reporter reply after needs-info in the inspected timelines....

### [✅ РЕШЕНО] [#2311: docs: use GPT-6 Astra in current client examples](https://github.com/Soju06/codex-lb/issues/2311)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** В `README.md`, `README.zh-CN.md`, `docs/client-setup.md`, а также в загружаемых профилях `docs/examples/codex/config.toml` и `docs/examples/codex/daybreak-blue.config.toml` примеры клиентской настройки переведены на рекомендуемую модель `gpt-6-astra`. Семейство моделей GPT-5.6 и инструкции по расширенному контекстному окну 872k сохранены с явной привязкой к семейству GPT-5.6 без повреждения протокольных фикстур и каталога.
  - **Компоненты:** `README.md, README.zh-CN.md, docs/client-setup.md, docs/examples/codex/config.toml, docs/examples/codex/daybreak-blue.config.toml, openspec/specs/user-documentation/spec.md`
- **Автор:** @JustYannicc | **Дата:** 2026-09-10 | **Метки:** `untriaged`
- **Суть проблемы / предложения:**
  > Current README and client setup examples select GPT-5.6 Sol and call it the strongest model. OpenAI now recommends GPT-6 Astra for complex reasoning and coding: https://developers.openai.com/api/docs/guides/latest-model. Update current configuration examples to `gpt-6-astra`, including translated README and downloadable Codex profiles. Separate conservative client budgets from model limits and keep the GPT-5.6 context-window instructions specific to that family. Preserve semantic catalog IDs, prices, protocol fixtures, historical measurements and model-specific compatibility requirements. This...

### [✅ РЕШЕНО] [#2291: bug: queued transcript batches wait between flushes](https://github.com/Soju06/codex-lb/issues/2291)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Фоновый цикл сброса событий транскрипта (`HttpBridgeOperationEventBatcher._run`) теперь непрерывно сбрасывает все накопившиеся батчи операций во внутреннем цикле со `sleep(0)` до полного опустошения очереди, устраняя задержку `flush_interval_seconds` между пачками событий одного берста.
  - **Компоненты:** `app/modules/proxy/http_bridge_event_batcher.py`
  - **Тесты:** `tests/unit/test_http_bridge_event_batcher.py`
- **Автор:** @JustYannicc | **Дата:** 2026-09-09 | **Метки:** `bug` `triage`
- **Суть проблемы / предложения:**
  > ### codex-lb version Upstream commit `069b82be3ceda8e468094f03aee0884061b2b43e`. ### Deployment method From source, using an isolated scheduling fixture. ### Client used against codex-lb Other: in-process batcher fixture. No live client traffic was used. ### ChatGPT account plan(s) involved None. The fixture uses a fake persistence writer. ### Model(s) involved None. The behavior is model-independent. ### What happened? The HTTP bridge transcript flusher sleeps between bounded passes even when events remain queued. A burst of 320 events takes about 920 ms to persist because nine flush-interval...

### [✅ РЕШЕНО] [#2029: bug: historical minute-long Codex LB stalls and event-loop starvation remain unresolved](https://github.com/Soju06/codex-lb/issues/2029)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** Устранены коренные причины минутных зависаний и голодания цикла событий: 1) предотвращен ложный захват и рекламация завершенных транзакций при teardown SQLite сессий (PR #2030 `ed2b36df`), 2) внедрен кэш контекстов TLS/SSL для исключения блокирующей загрузки корневых сертификатов ОС на каждый запрос (PR #2039), 3) устранена гонка отложенного сохранения логов через публикацию response_id в in-memory кэш владельцев (`publish-http-response-owner`), 4) оптимизирована подготовка тел HTTP-запросов (`skip-unused-http-preparation-serialization`), 5) пулы HTTP/2 соединений изолированы по аккаунтам в native egress (#2471).
  - **Компоненты:** `app/db/session.py`, `app/core/clients/proxy.py`, `app/core/clients/http.py`, `crates/codex-lb-egress/src/http.rs`
  - **Тесты:** `tests/unit/test_db_session.py`, `tests/unit/test_native_egress.py`
- **Автор:** @dpearson2699 | **Дата:** 2026-09-02 | **Метки:** `bug` `needs-info` `stale`
- **Суть проблемы / предложения:**
  > ## Remaining issue: historical minute-long stalls Keep this issue open. The investigation produced several bounded fixes, but it did not reproduce or establish the cause of the historical minute-long waits. Those waits remain the main blocker to switching back to Codex LB. Merging the scoped PRs below must not automatically close this issue. ### What the investigation established - The original aiohttp SSL-context cache already reached main through #2039. It removes repeated setup work, but does not prove that all long stalls were caused by CA loading. - A real SQLite worker can finish teardow...

### [✅ РЕШЕНО] [#1924: bug(proxy): inline-image 429 can prevent prompt-cache failover](https://github.com/Soju06/codex-lb/issues/1924)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ**
  - **Решение:** При принятии решения `action == "failover_next"` во время pre-visible/post-refresh стрим-ошибок (включая HTTP 429 на запросах с inline-изображениями) политика аффинити обновляется через `affinity = replace(affinity, reallocate_sticky=True)`. Это снимает залипание мягкой prompt-cache аффинити на исключенном аккаунте и позволяет балансировщику перенаправить запрос на доступный здоровый аккаунт пула.
  - **Компоненты:** `app/modules/proxy/_service/streaming/retry.py`
  - **Тесты:** `tests/integration/test_proxy_transient_retry.py`
- **Автор:** @HeroOfOdyssey | **Дата:** 2026-08-26 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ### codex-lb version Current `main` at `09dd9348`. ### Deployment method Docker Compose, built from source. ### Client used against codex-lb Codex app. ### ChatGPT account plan(s) involved Mixed pool. ### Model(s) involved Image-capable Codex model (`gpt-5.6-sol`). ### What happened? For a Responses streaming request containing an inline image and a `prompt_cache_key`, an upstream HTTP 429 from the selected account is treated as a retryable pre-visible failure and the account is excluded. However, the soft prompt-cache affinity remains pinned to that excluded account. The next selection pass f...

### [✅ РЕШЕНО] [#1707: bug: existing Codex thread can remain unusable on dead hard-affinity owner while fresh/side chat works](https://github.com/Soju06/codex-lb/issues/1707)
- **Статус:** ✅ **РЕШЕНО В ТЕКУЩЕЙ ВЕТКЕ** (PR #2467)
  - **Решение:** Инвалидация и отзыв отравленного/затомбстоунненного якоря (`_invalidate_denied_http_bridge_anchor`) при отказе в submit-time (`submit_time_anchor_tombstoned`), предотвращая залипание треда на мертвом hard-affinity владельце и позволяя восстановить тред.
  - **Компоненты:** `app/modules/proxy/_service/http_bridge/request_submit.py`
  - **Тесты:** `tests/unit/test_proxy_http_bridge.py`
- **Автор:** @myudak | **Дата:** 2026-08-13 | **Метки:** `bug`
- **Суть проблемы / предложения:**
  > ### codex-lb version `1.23.0` ### Deployment method `uvx (codex-lb)` ### Client used against codex-lb Codex app (desktop / web) ### ChatGPT account plan(s) involved Plus ### Model(s) involved `gpt-5.6-sol` ### Summary An existing/long-running Codex thread can become permanently unusable when its upstream owner/account becomes unavailable, even though other healthy accounts are still available in the pool. The strongest signal is that **the exact same Codex client works immediately when I use `/side chat` or `Continue in new chat`, while continuing the original thread keeps failing**. This make...

---

## 11. Предложения и обсуждения из GitHub Discussions
Пользователи активно делятся идеями, решениями и жалобами в GitHub Discussions (всего 49 тем). Ниже приведена выжимка предложений и проблем:

### Категория Discussions: General
- **[#1920: ARCHIVE THE REPO!. this project is dogshit i disabled it all and stopped using it way better other options all ai slop code](https://github.com/Soju06/codex-lb/discussions/1920)** (от @ikiddoi, 2026-08-25 | 👍 2 | 💬 3)
  > <img width="939" height="207" alt="image" src="https://github.com/user-attachments/assets/14242481-5dac-4c2d-90ea-c47b78628028" /> absolute dogshit project with error rate above github outage pack this dogshit up <img width="1618" height="405" alt="image" src="https://github.com/user-attachments/assets/d658329e-4590-41da-a71c-ecdb52a36929" /> 2.0% ...

- **[#1104: Caching](https://github.com/Soju06/codex-lb/discussions/1104)** (от @LouisDeconinck, 2026-06-28 | 👍 4 | 💬 1)
  > How is caching handled? I assume that if you constantly switch this has a big impact on caching, meaning less usage?

- **[#1894: Why is the reporting so SLOW?](https://github.com/Soju06/codex-lb/discussions/1894)** (от @bogorad, 2026-08-23 | 👍 1 | 💬 0)
  > I see python working. But why?? It's obviously a heavy load, why not rewrite the reporting to gonalg?

- **[#1551: Price estimate bug?](https://github.com/Soju06/codex-lb/discussions/1551)** (от @JoshuaRileyDev, 2026-07-30 | 👍 1 | 💬 0)
  > After the OpenAI announcement of Luna being 80% cheaper, I tried switching the enforced model to that model and ran a few tests, and it seems much more expensive than my old daily driver, which was 5.4 Mini. Is it still calculating based on the old pricing? Where does it get the pricing from?

- **[#1320: Reset Limits](https://github.com/Soju06/codex-lb/discussions/1320)** (от @aajoshi, 2026-07-14 | 👍 1 | 💬 1)
  > Codex/ChatGPT currently randomly assigns resets to users, is there a way to "reset" the limits in the codex-lb app? Typically I would just go to the reset menu like this and reset it does codex-lb support this, if so how? <img width="530" height="364" alt="image" src="https://github.com/user-attachments/assets/c639ab5a-de73-49fa-b9e2-3195f93bfda0" ...

- **[#1136: Configure openai_base_url for Remote Codex CLI Sessions](https://github.com/Soju06/codex-lb/discussions/1136)** (от @zbaibg, 2026-07-05 | 👍 1 | 💬 0)
  > Hi everyone, I found that if you use your phone to remotely control `codex-cli`, it's a good idea to add the following line to your `config.toml`: ```toml openai_base_url = "http://127.0.0.1:2455/backend-api/codex" ``` With this setting, when you start a Codex session from your phone, the requests are correctly routed through `codex-lb` instead of ...

- **[#1134: The Codex App does not automatically clean up the context.](https://github.com/Soju06/codex-lb/discussions/1134)** (от @taieuro, 2026-07-05 | 👍 1 | 💬 1)
  > Every time I receive this notification: "Codex ran out of room in the model's context window. Start a new thread or clear earlier history before retrying.", I have to use the context collapse command.

- **[#790: all account deactivated all the sudden](https://github.com/Soju06/codex-lb/discussions/790)** (от @villa1, 2026-05-24 | 👍 2 | 💬 2)
  > ## Summary Around 10 accounts were suddenly marked as deactivated within one day. Most accounts had normal or very low usage, and no clear warning or explanation was provided. ## Questions - Is this related to a recent security or anti-abuse update? - Was this triggered automatically? Any clarification would be appreciated. <img width="1306" height...

- **[#1012: 2FA Autofill](https://github.com/Soju06/codex-lb/discussions/1012)** (от @qnoMercy3, 2026-06-15 | 👍 1 | 💬 0)
  > I've been using codex-lb for quite some time now, most of the things are working perfectly, there is just one issue which is pretty annoying. Whenever I autofill my password with Touch ID on my macbook, I then need to enter the 2FA code which is set up in apple passwords. The thing is that autofill on the 2FA field always returns an invalid input w...

- **[#959: Business workspace with shared budget](https://github.com/Soju06/codex-lb/discussions/959)** (от @cani1989, 2026-06-08 | 👍 1 | 💬 0)
  > Does Codex-LB support ChatGPT Business workspace Codex usage/credits correctly? Specifically, if an upstream account is authenticated via ChatGPT/Codex OAuth and belongs to a Business workspace with shared Codex credits, will requests proxied through Codex-LB consume that workspace’s Codex credits rather than API billing?

- **[#791: PI harness](https://github.com/Soju06/codex-lb/discussions/791)** (от @DZsolt01, 2026-05-24 | 👍 2 | 💬 1)
  > Hi, Anyone using codex-lb with PI harness? After I get an error: Upstream websocket closed before response.completed: no close frame received or sent I cannot resume the session is this PI specific or codex? (I assume the error itself is mroe codex-lb related)

- **[#536: Figma connection lost when using Codex LB](https://github.com/Soju06/codex-lb/discussions/536)** (от @villa1, 2026-05-02 | 👍 1 | 💬 1)
  > ### Figma connection lost when using Codex LB I can connect to Figma normally when using a single session (same environment), and everything works fine. However, when I switch to Codex LB, the connection to Figma is no longer available. Error: > unknown MCP server 'Figma' > no use_figma / get_design_context tools available It seems like the Figma c...

- **[#352: Where is everyone getting accounts from now?](https://github.com/Soju06/codex-lb/discussions/352)** (от @josevelaz, 2026-04-07 | 👍 1 | 💬 0)
  > Описание отсутствует.

### Категория Discussions: Show and tell
- **[#1944: For now, you can try the enhanced version](https://github.com/Soju06/codex-lb/discussions/1944)** (от @aafqaq, 2026-08-28 | 👍 1 | 💬 2)
  > I mean no harm. I just desperately wanted to use Codex LB that would work normally, so I fixed it myself. Although some areas may not be perfect, at least compared to the original version, some well-known problems have been fixed and improved. For now, you can try the enhanced version: 🔗 **[[aafqaq/codex-lb-enhanced](https://github.com/aafqaq/codex...

- **[#994: codex-reset: a tiny Linux/CLI redeem tool building on your wham research](https://github.com/Soju06/codex-lb/discussions/994)** (от @aaamosh, 2026-06-13 | 👍 1 | 💬 0)
  > Hey @Soju06 — thanks for the [usage-refresh-policy spec](https://github.com/Soju06/codex-lb/blob/main/openspec/specs/usage-refresh-policy/context.md) and the broader `/wham/*` reverse-engineering work in this repo. They were the cleanest public notes I found while figuring out how the new banked rate-limit reset feature talks to the backend. OpenAI...

- **[#500: Just created an Opencode plugin for simplified setup on codex-lb](https://github.com/Soju06/codex-lb/discussions/500)** (от @huzky-v, 2026-04-26 | 👍 1 | 💬 0)
  > https://github.com/huzky-v/opencode-codex-lb It is created to support multi `codex-lb` endpoint and `API keys`, so that I can manage the API keys used for different agents easier without some hacky stuff needed (the previous solution for me is to hijack the models.dev response). E.g. I have a key A, with a pool of free accounts, so that I can deleg...

### Категория Discussions: Q&A
- **[#2232: **Title: Does load balancing across multiple Plus accounts still make sense?**](https://github.com/Soju06/codex-lb/discussions/2232)** (от @johnnywhosgood-afk, 2026-09-09 | 👍 1 | 💬 0)
  > Is it actually worth load balancing across multiple Plus accounts? If each 5-hour session only consumes around 15% of the weekly limit, switching to another account seems to introduce a non-trivial fixed cost: the new session has to re-establish and understand the current context. If we think of that context-transfer overhead as a constant cost \(c...

- **[#1998: Question: Is there an official migration path from SQLite to PostgreSQL in codex-lb?](https://github.com/Soju06/codex-lb/discussions/1998)** (от @Brook-ning, 2026-08-31 | 👍 1 | 💬 1)
  > Hi codex-lb team and community, I'm currently using codex-lb with the default SQLite backend in a production-like environment. Recently, I've been encountering frequent 500 errors due to SQLite's single-writer limitation — specifically, write operations queue up and exceed the built-in teardown timeout (`bound_seconds=5.0`), causing requests to be ...

- **[#1864: Frequent Invalid previous_response_id errors when using Codex with codex-lb](https://github.com/Soju06/codex-lb/discussions/1864)** (от @GioGabriel, 2026-08-21 | 👍 5 | 💬 2)
  > Hey, has anyone else been getting frequent Invalid previous_response_id errors recently when using Codex with codex-lb? I'm using codex-lb with two ChatGPT Plus accounts and this only started happening recently. Before this, I could run long Codex sessions without really running into this issue. My Codex config points to codex-lb like this: model =...

- **[#1575: How can I display the rate option in the codex app?](https://github.com/Soju06/codex-lb/discussions/1575)** (от @XXXShaunPan, 2026-08-03 | 👍 1 | 💬 1)
  > HI，All，How can I display the rate option in the codex app? <img width="452" height="179" alt="image" src="https://github.com/user-attachments/assets/f3d9e55a-08d5-4f24-812b-f0a1f05e52d3" />

- **[#1820: Is "Dashboard session lifetime" working?](https://github.com/Soju06/codex-lb/discussions/1820)** (от @bogorad, 2026-08-19 | 👍 1 | 💬 0)
  > codex-lb is in my LAN so I set "Dashboard session lifetime" to 876000, then to 8760000, and it's copletely ignored. Anyone able to set it so high we can forget it exists? I do need the password.

- **[#1593: Reauthentication when switching Business accounts: same workspace vs different workspace](https://github.com/Soju06/codex-lb/discussions/1593)** (от @Jamesgongzx, 2026-08-04 | 👍 1 | 💬 0)
  > I have several ChatGPT Business workspaces, each with multiple accounts: - Workspace A: a1, a2 - Workspace B: b1, b2 - Workspace C: c1, c2 I understand that v1.21.0 fixed some codex-lb reauthentication problems involving Team seat identity and concurrent token refreshes. I would like to hear about actual experience on v1.21.0 or newer. 1. If one ch...

- **[#1501: This project can't work now?](https://github.com/Soju06/codex-lb/discussions/1501)** (от @xingz4321-qq, 2026-07-27 | 👍 1 | 💬 1)
  > Codex error:unexpected status 401 Unauthorized: Incorrect API key provided: sk-clb-N**************************************d5lQ. You can find your API key at https://platform.openai.com/account/api-keys., url: https://api.openai.com/v1/responses, cf-ray: a21a2ed60c25758f-PDX, auth error: 401, auth error code: invalid_api_key

- **[#1406: Codex Lag and localhost:2455 delay](https://github.com/Soju06/codex-lb/discussions/1406)** (от @j1gool, 2026-07-20 | 👍 1 | 💬 0)
  > I have two different issues, and I would appreciate your experience and advice. Issue 1: Codex UI lag/freezing The Codex UI feels very laggy on my system. When I am typing, switching files, or opening a project, the interface sometimes freezes for around 1–3 seconds before responding. This behavior seems unusual because my hardware should be more t...

- **[#1192: The latest model is not found: Sol/Terra/Luna](https://github.com/Soju06/codex-lb/discussions/1192)** (от @taieuro, 2026-07-10 | 👍 2 | 💬 1)
  > I've updated to the latest commit of Codex-LB (65dc4b75be2de837968dcdf86ec233f5d5f0ad72) and Codex App (now ChatGPT Codex), but I don't see the sol/tera/luna models in the model selection section of ChatGPT Codex. Please guide me on how to fix this. Thank you.

- **[#1227: Problem with 5.6 Sol](https://github.com/Soju06/codex-lb/discussions/1227)** (от @j1gool, 2026-07-11 | 👍 1 | 💬 2)
  > Hey guys didnt u have problem with this Codex LB and gpt 5.6 ? Basicly it said In this environment, file inspection and editing tools are not enabled for me, so I can’t confidently apply the change to the project and i have no idea what does make this ! i litterly gave my codex full permisson !

- **[#1055: Plan mode in codex-cli with codex-lb?](https://github.com/Soju06/codex-lb/discussions/1055)** (от @epasEltronix, 2026-06-18 | 👍 1 | 💬 0)
  > Is plan mode supported and if yes, how to use it in codex-cli?

- **[#1037: How to enable fast mode on version 1.20.0](https://github.com/Soju06/codex-lb/discussions/1037)** (от @hoangphucnst, 2026-06-17 | 👍 2 | 💬 0)
  > How to enable fast mode on version 1.20.0

- **[#803: Codex Desktop history disappears when switching model_provider to codex-lb](https://github.com/Soju06/codex-lb/discussions/803)** (от @joshiestevens, 2026-05-25 | 👍 4 | 💬 3)
  > After setting: `model_provider = "codex-lb"` Codex Desktop stopped showing my existing session history in the sidebar. The sessions were still on disk, but only the new/current session appeared. Switching back to: `model_provider = "openai"` restored normal usage. Is Codex Desktop history expected to be tied to model_provider? If so, is there a sup...

- **[#978: The 'gpt-5.5-codex' model is not supported when using Codex with a ChatGPT account.](https://github.com/Soju06/codex-lb/discussions/978)** (от @itsmefrade, 2026-06-10 | 👍 1 | 💬 1)
  > Is this normal? I mean, i can put gpt-5.5 to config and its fine, but shouldn't i use gpt5.5 codex? this is plus account btw

- **[#864: 7 free accounts > 1 plus — intentional?](https://github.com/Soju06/codex-lb/discussions/864)** (от @ho2mo, 2026-05-31 | 👍 1 | 💬 1)
  > In `app/core/usage/__init__.py` the `PLAN_CAPACITY_CREDITS_SECONDARY` for the 7-day window are: - free: `1134` - plus: `7560` - pro: `50400` That makes plus ~6.67x free But 7 free accounts would give 7 × 1134 = 7938 credits, which exceeds a single plus account (7560). Since free accounts cost nothing, pooling them seems strictly better than a singl...

- **[#848: [BUG?] Multiple requests to different models per 1 simple "Hello" message](https://github.com/Soju06/codex-lb/discussions/848)** (от @KernelBypass, 2026-05-29 | 👍 1 | 💬 3)
  > 1. I've just setup codex-lb with several paid business accounts, and it works, but it's weird - for 1 simple "hi" chat message sent to `gpt-5.5-xhigh`, I'm seeing 4 requests with different models (gpt-5.5-xhigh and gpt-5.4-mini-low) and efforts (xhigh and low) - see the screenshot: <img width="1404" height="276" alt="image" src="https://github.com/...

- **[#573: Context limits](https://github.com/Soju06/codex-lb/discussions/573)** (от @TheYkk, 2026-05-09 | 👍 2 | 💬 1)
  > Looks like the context limit is somewhere arround 200k but the gpt 5.5 model supports 1m context windows. Is it a limitation in codex subscription or in codexlb? And sometimes the context is arround 200k and it cannot compact and gives paylod limit errors.

- **[#728: i recieve this message by lb : unexpected status 401 Unauthorized:](https://github.com/Soju06/codex-lb/discussions/728)** (от @pavel195, 2026-05-20 | 👍 1 | 💬 0)
  > unexpected status 401 Unauthorized: Proxy authentication must be configured before remote access is allowed, url: what should i've already setup config.toml

- **[#704: Where do my HTTP limits go?](https://github.com/Soju06/codex-lb/discussions/704)** (от @Jtileyev, 2026-05-19 | 👍 1 | 💬 0)
  > I added two accounts and can't figure out why their limits expire at the same time. I just want to know if the limits are used up one after another or if they're split between the accounts. <img width="1033" height="153" alt="image" src="https://github.com/user-attachments/assets/3d71cc2d-f149-4605-a54e-1d597480ed9b" /> <img width="1246" height="28...

- **[#661: Does Codex LB work with the Codex Mobile feature?](https://github.com/Soju06/codex-lb/discussions/661)** (от @TheJoWo, 2026-05-15 | 👍 5 | 💬 2)
  > I saw Codex released Codex Mobile and it seems tied to a single account. Does it work if you are using Codex LB?

- **[#636: Import|Export Accaunts](https://github.com/Soju06/codex-lb/discussions/636)** (от @Company-RS, 2026-05-14 | 👍 2 | 💬 0)
  > Please implement the Export button

- **[#406: Codex-Lb does not Works Over VPS?](https://github.com/Soju06/codex-lb/discussions/406)** (от @svk27, 2026-04-14 | 👍 1 | 💬 2)
  > Hi guys, please tell me what am I possibly doing wrong here.. I am trying to setup codex-lb over Coolify (docker manager). But I am always ending up getting a Cloudlflare block. The server for me is running inside my reverse proxy, and these are the related settings (am I missing something?): CODEX_LB_FIREWALL_TRUST_PROXY_HEADERS=true CODEX_LB_FIRE...

- **[#292: Request log retention: auto-clearing and configuration options](https://github.com/Soju06/codex-lb/discussions/292)** (от @rzxczxc, 2026-04-01 | 👍 1 | 💬 0)
  > Are request logs cleared automatically over time, or is there a way to configure the retention period?

- **[#212: OpenFang](https://github.com/Soju06/codex-lb/discussions/212)** (от @snakedev, 2026-03-15 | 👍 1 | 💬 0)
  > How do you integrate codex-lb with OpenFang?

### Категория Discussions: Ideas
- **[#1306: [Design] Fixed-endpoint native credential routing for Codex and OpenClaw](https://github.com/Soju06/codex-lb/discussions/1306)** (от @dmdfami, 2026-07-14 | 👍 1 | 💬 2)
  > ## Problem Codex App/CLI and OpenClaw can already use the native Codex backend at `/backend-api/codex`, but changing between the client's signed-in OAuth account and the `codex-lb` account pool normally means changing provider configuration or restarting a client/app-server. Generic `/v1` integrations also replace part of the native harness rather ...

- **[#884: Idea: API-based authorization flow for accounts when SMS verification is unavailable](https://github.com/Soju06/codex-lb/discussions/884)** (от @kingofligh, 2026-06-03 | 👍 5 | 💬 1)
  > Hi! I would like to suggest an API-based authorization flow for accounts. The current account authorization can be problematic when SMS verification is required. For example, if the account asks for SMS confirmation, but the original SIM card is no longer available, it becomes impossible to complete the normal browser-based authorization flow. I te...

- **[#980: Error on compaction](https://github.com/Soju06/codex-lb/discussions/980)** (от @tibinta, 2026-06-10 | 👍 1 | 💬 0)
  > Found a bug maybe it is just my environment: Error running remote compact task: Fatal error: remote compaction v2 expected exactly one compaction output item, got 0 from 0 output items

- **[#852: RFC: OIDC federation — keyless CI auth for codex-lb](https://github.com/Soju06/codex-lb/discussions/852)** (от @DongwonTTuna, 2026-05-29 | 👍 1 | 💬 0)
  > > *English first, 한국어는 아래에.* ### TL;DR I've been prototyping **IdP-agnostic OIDC federation** for codex-lb: a CI/CD job presents its short-lived OIDC ID token and gets back a short-lived `sk-clb-` key — **no long-lived secret stored anywhere**. Same model as AWS STS `AssumeRoleWithWebIdentity` / GCP Workload Identity Federation, opt-in and **off by...

- **[#709: Feature Request: Optional “Reset My Limits” / Limit Warm-Up Trigger](https://github.com/Soju06/codex-lb/discussions/709)** (от @mahirozdin, 2026-05-19 | 👍 1 | 💬 1)
  > Hi, I have been using Codex LB for a while with multiple Codex accounts and several proxied devices. Overall, it works very well for balancing usage across accounts, but I noticed a small missing feature that could improve practical limit utilization. The feature could be called something like: **Reset My Limits** or **Limit Warm-Up Trigger** or **...

- **[#663: Feature Request: Support for ENABLE_FORWARD_USER_INFO_HEADERS](https://github.com/Soju06/codex-lb/discussions/663)** (от @simon-jouet, 2026-05-15 | 👍 1 | 💬 0)
  > Hi! First of all thanks for codex-lb, it's a really nice piece of software. I got bogged down trying to get litellm to perform decently and tried to get bifrost to play ball with a chatgpt subscription but at the end of the day codex-lb was exactly what I was looking for! I've setup open-webui with codex-lb, it was dead easy and works really really...

- **[#420: Paused -> stealth mode on....](https://github.com/Soju06/codex-lb/discussions/420)** (от @genbasura, 2026-04-16 | 👍 1 | 💬 1)
  > I have been thinking like.. shouldn´t a "paused" account, try to avoid requests to OpenAI as much as possible? I mean, you never know what MLs they have on their end, if they may detect too many concurrent requests by ip or something... That may make accounts to be flagged... Also the refreshing of the tokens, I think it should happen if possible w...

- **[#342: ChatGPT Business Account](https://github.com/Soju06/codex-lb/discussions/342)** (от @TimoMangCut, 2026-04-07 | 👍 2 | 💬 1)
  > Codex LB currently supports monitoring business accounts. However, when one account belongs to multiple business workspaces, it only detects one workspace or fails to detect the additional workspaces. It would be helpful if Codex LB could support multi-workspace business accounts.

- **[#378: Deeper usage analysis](https://github.com/Soju06/codex-lb/discussions/378)** (от @dhvcc, 2026-04-09 | 👍 1 | 💬 1)
  > I was wondering, since this already is a load balancer with option to track usage - wouldn't it be nice to track or be able to analyze tool usage? I personally do it via hooks, but that's pretty limited The idea is to be able to see where your models make mistakes more often to optimize your own prompts and tooling It was very useful to me to chang...

---

## 12. Важные открытые Pull Requests от комьюнити
Многие пользователи не просто сообщили о баге, но и прислали готовый PR с исправлением. Ниже ключевые PR, которые можно изучить или интегрировать:

- **[✅ РЕШЕНО] [PR #2490: fix(auth): add secret-safe refresh failure diagnostics](https://github.com/Soju06/codex-lb/pull/2490)** — @changrex4218
- **[✅ РЕШЕНО] [PR #2489: fix(accounts): preserve quota chart samples and account display state](https://github.com/Soju06/codex-lb/pull/2489)** — @NikitaMGrimm
- **[✅ РЕШЕНО] [PR #2488: fix(proxy): handle CRLF and malformed UTF-8 in owner forwarding](https://github.com/Soju06/codex-lb/pull/2488)** — @Aminkbi
- **[✅ РЕШЕНО] [PR #2487: fix(auth): reject non-ASCII TOTP digits safely](https://github.com/Soju06/codex-lb/pull/2487)** — @Aminkbi
- **[✅ РЕШЕНО] [PR #2486: fix(balancer): admit a hard continuity owner serving its own transient backoff](https://github.com/Soju06/codex-lb/pull/2486)** — @yeongjun-cigro
- **[✅ РЕШЕНО] [PR #2484: perf(usage): cap SQLite bulk usage history reads per account](https://github.com/Soju06/codex-lb/pull/2484)** — @lkraider (Fixes #2483)
- **[✅ РЕШЕНО] [PR #2473: feat(proxy): add gpt-reserve as an operator-enabled Luna Reserve model](https://github.com/Soju06/codex-lb/pull/2473)** — @AndresASJ (Closes #2413)
- **[✅ РЕШЕНО] [PR #2472: fix(proxy): surface native transport give-up terminals](https://github.com/Soju06/codex-lb/pull/2472)** — @Komzpa
- **[✅ РЕШЕНО] [PR #2469: fix(proxy): preserve routed file failover provenance](https://github.com/Soju06/codex-lb/pull/2469)** — @mastertyko
- **[✅ РЕШЕНО] [PR #2468: fix(quota): validate planner timezones and tolerate legacy keys](https://github.com/Soju06/codex-lb/pull/2468)** — @mastertyko
- **[✅ РЕШЕНО] [PR #2467: fix(proxy-responses): retire tombstoned injected anchors](https://github.com/Soju06/codex-lb/pull/2467)** — @rknightion
- **[✅ РЕШЕНО] [PR #2464: feat(ui): add compact and fullscreen dashboard account views](https://github.com/Soju06/codex-lb/pull/2464)** — @neikop
- **[✅ РЕШЕНО] [PR #2463: feat(api-keys): add estimated usage-share limits](https://github.com/Soju06/codex-lb/pull/2463)** — @mustafa0x
- **[✅ РЕШЕНО] [PR #2462: fix(db): repair September migration lineage](https://github.com/Soju06/codex-lb/pull/2462)** — @aacarcrash
- **[✅ РЕШЕНО] [PR #2461: fix(db): converge the SCIM token and subscription-overflow heads](https://github.com/Soju06/codex-lb/pull/2461)** — @Soju06
- **[✅ РЕШЕНО] [PR #2460: fix(dashboard-users): take the owner row before the owned-key cascade reads it](https://github.com/Soju06/codex-lb/pull/2460)** — @Soju06
- **[✅ РЕШЕНО] [PR #2458: fix(proxy): recover bridge-bypassed quota failover](https://github.com/Soju06/codex-lb/pull/2458)** — @aacarcrash
- **[✅ РЕШЕНО] [PR #2457: fix(proxy): recover Windows transport failures](https://github.com/Soju06/codex-lb/pull/2457)** — @aacarcrash
- **[✅ РЕШЕНО] [PR #2451: fix(proxy): refuse remote compaction for model-source models before account selection](https://github.com/Soju06/codex-lb/pull/2451)** — @Komzpa
- **[✅ РЕШЕНО] [PR #2448: feat(proxy): diversify subagents from parent accounts](https://github.com/Soju06/codex-lb/pull/2448)** — @joschi655
- **[✅ РЕШЕНО] [PR #2446: fix(rust): upgrade rustls past RUSTSEC-2026-0285](https://github.com/Soju06/codex-lb/pull/2446)** — @Komzpa
- **[✅ РЕШЕНО] [PR #2445: feat(proxy): forward the Codex plugin catalog upstream so chatgpt_base_url can point at codex-lb](https://github.com/Soju06/codex-lb/pull/2445)** — @diegocamara89
- **[✅ РЕШЕНО] [PR #2444: fix(metrics): separate observed generation timing from request latency](https://github.com/Soju06/codex-lb/pull/2444)** — @627444640
- **[✅ РЕШЕНО] [PR #2440: fix(proxy): preserve upstream reset metadata in retry health](https://github.com/Soju06/codex-lb/pull/2440)** — @DongwonTTuna
- **[✅ РЕШЕНО] [PR #2439: fix(proxy): preserve upstream quota reset metadata on terminal errors](https://github.com/Soju06/codex-lb/pull/2439)** — @HulianBuligon
- **[✅ РЕШЕНО] [PR #2430: feat(proxy): add transcript core storage](https://github.com/Soju06/codex-lb/pull/2430)** — @shaqman
- **[✅ РЕШЕНО] [PR #2429: fix(auth): reuse shared refresh policy in guardian](https://github.com/Soju06/codex-lb/pull/2429)** — @mustafa0x
- **[✅ РЕШЕНО] [PR #2428: feat(proxy): decide relocation once, and rebuild a conversation from the durable spool](https://github.com/Soju06/codex-lb/pull/2428)** — @Soju06
- **[✅ РЕШЕНО] [PR #2423: fix(proxy): reject a dead client anchor instead of asking for a retry](https://github.com/Soju06/codex-lb/pull/2423)** — @Soju06
- **[✅ РЕШЕНО] [PR #2403: feat(proxy): classify usage-limit rejections and answer pool-walk exclusion](https://github.com/Soju06/codex-lb/pull/2403)** — @Soju06
- **[✅ РЕШЕНО] [PR #2398: fix(proxy): prepare portable WebSocket full resends for quota replay](https://github.com/Soju06/codex-lb/pull/2398)** — @dakixr
- **[✅ РЕШЕНО] [PR #2391: feat(proxy): shape the failover decision around the pool and render its terminal](https://github.com/Soju06/codex-lb/pull/2391)** — @Soju06
- **[✅ РЕШЕНО] [PR #2377: fix(dashboard): calm the telemetry consent dialog](https://github.com/Soju06/codex-lb/pull/2377)** — @Soju06
- **[✅ РЕШЕНО] [PR #2345: fix(proxy): preserve local quarantine evidence during completion](https://github.com/Soju06/codex-lb/pull/2345)** — @JustYannicc
- **[✅ РЕШЕНО] [PR #2344: feat(health): expose request-persistence ownership during drain](https://github.com/Soju06/codex-lb/pull/2344)** — @JustYannicc
- **[✅ РЕШЕНО] [PR #2332: fix(proxy): fail over account-local model rejection](https://github.com/Soju06/codex-lb/pull/2332)** — @Komzpa
- **[✅ РЕШЕНО] [PR #2326: fix(warmup): preserve live reset evidence across skipped polls](https://github.com/Soju06/codex-lb/pull/2326)** — @JustYannicc
- **[✅ РЕШЕНО] [PR #2325: feat(cli): bound whole-home retag planning and report progress](https://github.com/Soju06/codex-lb/pull/2325)** — @JustYannicc
- **[✅ РЕШЕНО] [PR #2324: feat(proxy): forward explicit compact requests to model sources](https://github.com/Soju06/codex-lb/pull/2324)** — @JustYannicc
- **[✅ РЕШЕНО] [PR #2323: feat(cli): add targeted session metadata preview and repair](https://github.com/Soju06/codex-lb/pull/2323)** — @JustYannicc
- **[✅ РЕШЕНО] [PR #2322: feat(db): explain guarded migration recovery stamping](https://github.com/Soju06/codex-lb/pull/2322)** — @JustYannicc
- **[✅ РЕШЕНО] [PR #2321: fix(accounts): preserve observed monthly quota across plans](https://github.com/Soju06/codex-lb/pull/2321)** — @JustYannicc
- **[✅ РЕШЕНО] [PR #2319: fix(proxy): contain post-terminal health write failures](https://github.com/Soju06/codex-lb/pull/2319)** — @JustYannicc
- **[✅ РЕШЕНО] [PR #2317: fix(proxy): align compact budget with responses stream](https://github.com/Soju06/codex-lb/pull/2317)** — @Komzpa
- **[✅ РЕШЕНО] [PR #2308: fix(proxy): project pooled quotas into Codex rate-limit events](https://github.com/Soju06/codex-lb/pull/2308)** — @Soju06
- **[✅ РЕШЕНО] [PR #2307: feat(db): log per-revision migration progress](https://github.com/Soju06/codex-lb/pull/2307)** — @JustYannicc
- **[✅ РЕШЕНО] [PR #2305: feat(model-sources): discover CPA catalogs and retain unavailable ownership](https://github.com/Soju06/codex-lb/pull/2305)** — @JustYannicc
- **[✅ РЕШЕНО] [PR #2303: perf(http-bridge): drain queued transcript batches without interval waits](https://github.com/Soju06/codex-lb/pull/2303)** — @JustYannicc
- **[✅ РЕШЕНО] [PR #2294: feat(telemetry): expand anonymous telemetry to schema v2 with summable day aggregates and histograms](https://github.com/Soju06/codex-lb/pull/2294)** — @Soju06
- **[✅ РЕШЕНО] [PR #2280: fix(proxy): preserve newer retry state during scheduled cleanup](https://github.com/Soju06/codex-lb/pull/2280)** — @JustYannicc
- **[✅ РЕШЕНО] [PR #2278: fix(proxy): count incomplete responses toward bridge retries](https://github.com/Soju06/codex-lb/pull/2278)** — @JustYannicc
- **[✅ РЕШЕНО] [PR #2277: fix(proxy): preserve continuation anchors during input normalization](https://github.com/Soju06/codex-lb/pull/2277)** — @JustYannicc
- **[✅ РЕШЕНО] [PR #2276: fix(proxy): preserve newer quarantine during response cleanup](https://github.com/Soju06/codex-lb/pull/2276)** — @JustYannicc

- **[✅ РЕШЕНО] [PR #2255: fix(shutdown): deny WebSocket upgrades during drain with 503 instead of a pre-handshake close](https://github.com/Soju06/codex-lb/pull/2255)** — @Abaddollyon
- **[✅ РЕШЕНО] [PR #2146: feat(dashboard): add request heatmap on dashboard](https://github.com/Soju06/codex-lb/pull/2146)** — @huzky-v
- **[✅ РЕШЕНО] [PR #2133: fix(proxy): isolate bridge heartbeat from maintenance](https://github.com/Soju06/codex-lb/pull/2133)** — @mustafa0x
- **[✅ РЕШЕНО] [PR #2132: fix(auth): retain access rejection through late health updates](https://github.com/Soju06/codex-lb/pull/2132)** — @Hugh-Do
- **[✅ РЕШЕНО] [PR #2122: fix(warmup): restore reset usage threshold](https://github.com/Soju06/codex-lb/pull/2122)** — @HulianBuligon
- **[✅ РЕШЕНО] [PR #2121: fix(proxy): recover tool-complete goal followups from unavailable owners](https://github.com/Soju06/codex-lb/pull/2121)** — @Irvinwop
- **[✅ РЕШЕНО] [PR #2120: fix(auth): retain unexpired access on refresh preflight failure](https://github.com/Soju06/codex-lb/pull/2120)** — @Irvinwop
- **[✅ РЕШЕНО] [PR #2119: fix(accounts): require spendable credits for quota override](https://github.com/Soju06/codex-lb/pull/2119)** — @Komzpa
- **[✅ РЕШЕНО] [PR #2118: feat(ui): add Japanese dashboard localization](https://github.com/Soju06/codex-lb/pull/2118)** — @glyzinie
- **[✅ РЕШЕНО] [PR #2117: fix(proxy): retire revoked stream accounts](https://github.com/Soju06/codex-lb/pull/2117)** — @msmahdinejad
- **[✅ РЕШЕНО] [PR #2115: feat(proxy): support Astra steering with transport-owned dispatch](https://github.com/Soju06/codex-lb/pull/2115)** — @mastertyko
- **[✅ РЕШЕНО] [PR #2112: fix(observability): record HTTP upstream phase timings](https://github.com/Soju06/codex-lb/pull/2112)** — @dpearson2699
- **[✅ РЕШЕНО] [PR #2102: feat(proxy): support Codex history and notes across account pools](https://github.com/Soju06/codex-lb/pull/2102)** — @leosanxyz
- **[✅ РЕШЕНО] [PR #2101: fix(proxy): add native history and notes routes with account-local ownership](https://github.com/Soju06/codex-lb/pull/2101)** — @Komzpa
- **[✅ РЕШЕНО] [PR #2099: feat(proxy): preserve async tool results across continuations](https://github.com/Soju06/codex-lb/pull/2099)** — @mastertyko
- **[✅ РЕШЕНО] [PR #2098: fix(docker): isolate host OAuth callback port by default](https://github.com/Soju06/codex-lb/pull/2098)** — @shuhulx
- **[✅ РЕШЕНО] [PR #2097: feat(proxy): enforce Astra configuration-update policy](https://github.com/Soju06/codex-lb/pull/2097)** — @mastertyko
- **[✅ РЕШЕНО] [PR #2088: fix(http-bridge): retain draining owners through safe recovery](https://github.com/Soju06/codex-lb/pull/2088)** — @Komzpa
- **[✅ РЕШЕНО] [PR #2085: feat(models): add gpt-6 astra catalog support](https://github.com/Soju06/codex-lb/pull/2085)** — @Komzpa
- **[✅ РЕШЕНО] [PR #2075: fix(proxy): keep frameless bridge drops account neutral](https://github.com/Soju06/codex-lb/pull/2075)** — @e1ektr0
- **[✅ РЕШЕНО] [PR #2069: fix(proxy): recover unanchored quota replay](https://github.com/Soju06/codex-lb/pull/2069)** — @msmahdinejad
- **[✅ РЕШЕНО] [PR #2065: Feature/multi file account import](https://github.com/Soju06/codex-lb/pull/2065)** — @nhdong1993
- **[✅ РЕШЕНО] [PR #2048: fix(proxy): preserve exhausted sticky failover](https://github.com/Soju06/codex-lb/pull/2048)** — @msmahdinejad
- **[✅ РЕШЕНО] [PR #2001: fix(proxy): release payload owner after pre-visible quota rejection](https://github.com/Soju06/codex-lb/pull/2001)** — @HeroOfOdyssey
- **[✅ РЕШЕНО] [PR #1962: fix(proxy): preserve half-open probe ownership during cleanup](https://github.com/Soju06/codex-lb/pull/1962)** — @JustYannicc
- **[✅ РЕШЕНО] [PR #1952: fix(proxy): preserve tool search pairs through replay](https://github.com/Soju06/codex-lb/pull/1952)** — @Komzpa
- **[✅ РЕШЕНО] [PR #1938: feat(accounts): add encrypted portable account bundles](https://github.com/Soju06/codex-lb/pull/1938)** — @plastictaste
- **[✅ РЕШЕНО] [PR #1932: feat(db): add safe SQLite compaction](https://github.com/Soju06/codex-lb/pull/1932)** — @choi138
- **[✅ РЕШЕНО] [PR #1905: fix(proxy): preserve continuation ownership across source routing](https://github.com/Soju06/codex-lb/pull/1905)** — @JustYannicc
- **[✅ РЕШЕНО] [PR #1903: fix(proxy): bound memory used by paused bridge streams](https://github.com/Soju06/codex-lb/pull/1903)** — @JustYannicc
- **[✅ РЕШЕНО] [PR #1528: feat(accounts): add per-account usage limits](https://github.com/Soju06/codex-lb/pull/1528)** — @NikitaMGrimm
- **[✅ РЕШЕНО] [PR #1084: fix(proxy): fail fast on locally-generated retry hint in capacity-wait loop](https://github.com/Soju06/codex-lb/pull/1084)** — @obchain

---

## 13. ТОП-10 критических багов для первоочередного исправления

1. **[✅ РЕШЕНО]** **[#2471](https://github.com/Soju06/codex-lb/issues/2471)** & **[#2470](https://github.com/Soju06/codex-lb/issues/2470)** — **Крах стримов и зависание аккаунтов при сетевом разрыве в Native Egress (Rust/HTTP2)**:
   - *Фактическое решение в коде:*
     - **#2471:** В `crates/codex-lb-egress/src/http.rs`, `app/core/clients/proxy.py` и `app/core/clients/native_egress.py` введена изоляция пулов соединений HTTP/2 по аккаунтам (`pool_key: account_id`), исключающая мультиплексирование всех аккаунтов на одно соединение.
     - **#2470:** В `app/modules/proxy/api.py` реализован метод `_close_responses_stream_best_effort`, вызываемый в блоках `finally` генераторов стримов (`_stream_response_error_events:8904`, `_stream_startup_error_response`, и при `stream_incomplete` / `Native upstream stream ended before a terminal event` на строках 9924-9945), гарантируя немедленное освобождение `stream_lease` и предотвращая застревание аккаунтов в `account_stream_cap`.
   - *Тесты:* `tests/unit/test_native_egress.py`, `tests/unit/test_proxy_http_bridge.py`.
2. **[✅ РЕШЕНО]** **[#2447](https://github.com/Soju06/codex-lb/issues/2447)** & **[#1981](https://github.com/Soju06/codex-lb/issues/1981)** — **Зависание базы данных SQLite (`database is locked`)**:
   - *Фактическое решение в коде:*
     - **#2447:** В `app/db/session.py` установлены PRAGMA `busy_timeout=30000` / `60000`, `wal_autocheckpoint=1000` и `PRAGMA synchronous=NORMAL`, добавлен retry-механизм для сессий пользователей/авторизации при конкурентных блокировках.
     - **#1981:** В `app/db/session.py` (`_reclaim_wedged_sqlite_teardown:770-819`) внедрен сторожевой таймер (watchdog). При возникновении ошибки закрытия БД прерывание драйвера `sqlite3_interrupt` запускается инлайн, соединение принудительно инвалидируется (`connection.invalidate()`), а зависшая сессия переводится в фоновое завершение (`_finish_abandoned_teardown`), предотвращая удержание писательского лока SQLite до 55 минут.
   - *Тесты:* `tests/unit/test_db_session.py`, `tests/unit/test_dashboard_auth.py`, `tests/unit/test_dashboard_users.py`.
3. **[✅ РЕШЕНО]** **[#2465](https://github.com/Soju06/codex-lb/issues/2465)** — **Зависание сессий моста и сбои картинок с тулами**:
   - *Фактическое решение в коде:*
     - **Часть 1:** В `app/modules/proxy/_service/http_bridge/upstream_events.py` (строки 1971–2355) добавлена обработка тайм-аута `missing_response_created_timeout` (`_HTTP_BRIDGE_MISSING_RESPONSE_CREATED_TIMEOUT_DETAIL`) с отцеплением мертвого durable-якоря и восстановлением sticky bridge lineage без бесконечных ретраев.
     - **Часть 2:** В `app/core/openai/requests.py:1030` поле `parallel_tool_calls` принудительно исключается (`payload.pop("parallel_tool_calls", None)`) из payload для Responses wire, предотвращая ошибку невалидного параметра при одновременной передаче тулов и картинок.
   - *Тесты:* `tests/unit/test_proxy_http_bridge.py`, `tests/unit/test_images_schemas.py`.
4. **[✅ РЕШЕНО]** **[#2425](https://github.com/Soju06/codex-lb/issues/2425)** — **Сбои запросов с картинками (`input_image`) при перегрузке в 8 раз чаще**:
   - *Фактическое решение в коде:*
     - В `app/modules/proxy/_service/response_create.py:209-241` (`_input_image_request_requires_http_upstream`) и `app/modules/proxy/_service/http_bridge/streaming.py:1033-1040` байпас сессионного HTTP-моста строго ограничен только ситуациями, когда размер полезной нагрузки превышает бюджет фрейма WebSocket (`payload_size_estimate_bytes > _ws_transport_payload_budget_bytes()`) либо запрос содержит внешние неподгруженные HTTP(S)-ссылки на изображения. Обычные inline `data:` изображения продолжают передаваться через WebSocket/HTTP-bridge без избыточного байпаса, снижая частоту сбоев `server_is_overloaded` во время пиковых перегрузок.
   - *Тесты:* `tests/unit/test_proxy_http_bridge.py`.
5. **[✅ РЕШЕНО]** **[#1921](https://github.com/Soju06/codex-lb/issues/1921)** & **[#2090](https://github.com/Soju06/codex-lb/issues/2090)** — **Массовые ошибки `invalid previous_response_id`**:
   - *Фактическое решение в коде:*
     - **#1921 (PR #2423):** В `app/modules/proxy/_service/http_bridge/streaming.py` при обращении клиента с мертвым клиентским якорем на выведенном из строя владельце моста возвращается детерминированный отказ `previous_response_not_found` (404) вместо бесконечного цикла 503 retryable. В `durable_bridge_repository.py` устранено состояние гонки при выводе владельца через CAS (`already_retired`).
     - **#2090:** В `app/modules/api_keys/service.py` и `app/modules/proxy/_service/api_key_usage.py` обеспечена согласованность резерваций API-ключей при поздней инъекции якорей в HTTP-мосте.
   - *Тесты:* `tests/unit/test_durable_bridge_owner_retirement.py`, `tests/integration/test_http_responses_bridge.py`, `tests/unit/test_api_keys_service.py`.
6. **[✅ РЕШЕНО]** **[#2442](https://github.com/Soju06/codex-lb/issues/2442)** & **[#2064](https://github.com/Soju06/codex-lb/issues/2064)** — **Отравление пула роутинга протухшими/отозванными токенами (`token_expired` / `token_revoked`)**:
   - *Фактическое решение в коде:*
     - В `app/core/balancer/logic.py` (строки 23, 49-63) коды `token_revoked` и `account_auth_invalidated` включены в перечень постоянных отказов (`PERMANENT_FAILURE_CODES`) и набор мгновенного исключения из селектора. В `app/modules/accounts/repository.py` и `app/modules/proxy/load_balancer.py` такие аккаунты немедленно помечаются как требующие реаутентификации (`REAUTH_REQUIRED`) и полностью исключаются из пула кандидатов балансировщика, не отравляя выбор рабочих аккаунтов.
   - *Тесты:* `tests/unit/test_failover_foundation.py`, `tests/unit/test_accounts_service_probe.py`, `tests/unit/test_load_balancer.py`.
7. **[✅ РЕШЕНО]** **[#2266](https://github.com/Soju06/codex-lb/issues/2266)** — **Утечка памяти в воркере при приостановленных стримах**:
   - *Фактическое решение в коде:*
     - В `app/modules/proxy/_service/http_bridge/queues.py` реализован класс очереди стрим-событий `_HTTPBridgeEventQueue` с двойным ограничением: жесткий лимит 4096 событий (`_HTTP_BRIDGE_STREAM_QUEUE_LIMIT`) и лимит буфера памяти 32 MiB (`_HTTP_BRIDGE_STREAM_QUEUE_BYTES_LIMIT = 32 * 1024 * 1024`). При переполнении включается обратное противодавление (stall backpressure), предотвращая неконтролируемый рост памяти воркера при паузах на стороне клиента.
   - *Тесты:* `tests/unit/test_http_bridge_event_queue.py`, `tests/unit/test_proxy_http_bridge.py`.
8. **[✅ РЕШЕНО]** **[#1895](https://github.com/Soju06/codex-lb/issues/1895)** & **[#1976](https://github.com/Soju06/codex-lb/issues/1976)** — **Сбои автопрогрева лимитов (/v1/warmup)**:
   - *Фактическое решение в коде:*
     - **#1895 & #2496:** В Force Probe (`app/modules/accounts/service.py`) параметр `max_output_tokens` полностью опущен, так как обновленный Codex Responses API отвергает его с кодом 400 (`Unsupported parameter: max_output_tokens`); запрос отправляется со `stream=True, store=False` без `max_output_tokens`, а в `app/modules/proxy/_service/compact.py` добавлен прозрачный фоллбэк на базовый Responses API при возврате 404 от апстрима на эндпоинте компактинга.
     - **#1976:** В `app/core/balancer/logic.py` и сервисе автопрогрева реализован расчет стабильного эпохального цикла с учетом скользящих дедлайнов сброса квот, обеспечивающий надежный старт 5h окон.
   - *Тесты:* `tests/unit/test_accounts_service_probe.py`, `tests/integration/test_accounts_api_probe.py`, `tests/unit/test_limit_warmup.py`, `tests/integration/test_proxy_warmup.py`.
9. **[✅ РЕШЕНО]** **[#2028](https://github.com/Soju06/codex-lb/issues/2028)** — **Утечка секретов и токенов в логах**:
   - *Фактическое решение в коде:*
     - В `app/core/runtime_logging.py` переработаны регулярные выражения маскирования: реализована функция `redact_rendered_log_text`, маскирующая Bearer-токены, API-ключи, базовую аутентификацию, учетные данные в кавычках, query-параметрах и JSON-структурах. Внедрен `install_redacting_loop_exception_handler:531`, который оборачивает контекст исключений Event Loop в защищенный `_RedactedRepr`, предотвращая утечку учетных данных через стандартные обработчики asyncio/uvloop.
   - *Тесты:* `tests/unit/test_structured_logging.py`, `tests/unit/test_runtime_logging_loop_handler.py`.
10. **[✅ РЕШЕНО]** **[#2038](https://github.com/Soju06/codex-lb/issues/2038)** & **[#2076](https://github.com/Soju06/codex-lb/issues/2076)** — **Проблемы окружения и клиентов (Visual Studio Copilot, Docker OAuth)**:
    - *Фактическое решение в коде:*
      - **#2038:** В `app/modules/proxy/api.py:1853` добавлен маршрут `@v1_router.get("/models/{model_id:path}")` с вызовом `_build_model_response(api_key, model_id)`, восстановивший полную совместимость с Visual Studio Copilot и официальными SDK OpenAI.
      - **#2076:** В `app/modules/oauth/service.py` реализован контроль жизненного цикла фонового локального callback-сервера с задачей `_expire_browser_flows:624` и 15-минутным TTL для сессий Browser (PKCE) авторизации, предотвращающий перехват коллбэков нативного Codex Desktop на порту 1455.
    - *Тесты:* `tests/integration/test_v1_models.py`, `tests/integration/test_oauth_flow.py`.

<a id="upstream_recent_2497_2537"></a>
---

## 14. Новые проблемы, баги, предложения и Pull Requests из оригинального репозитория (Upstream #2497–#2537)

> В данный раздел включены все **41 новых обращений** (Issues, Feature Requests, Pull Requests), поступивших в оригинальный репозиторий `Soju06/codex-lb` с момента последнего релиза (номера #2497–#2537), со всеми подробностями, описанием багов, ссылками на код, прикрепленными скриншотами и решениями.

### [✅ RESOLVED / MERGED IN FORK] [#2497: feat(accounts): show reset credits for paused accounts](https://github.com/Soju06/codex-lb/pull/2497)

- **Тип:** Pull Request
- **Автор:** @codemoo
- **Дата создания:** 2026-09-25
- **Метки:** `documentation, frontend, python`

**Описание проблемы и предложенные изменения:**

## Summary

Allow operators to inspect a paused account's reset-credit count without resuming request routing. The selected-account read uses the existing credential refresh and account-bound proxy path; cached counts remain visible, while polling and both manual/automatic redemption remain blocked.

## Type of change

- [x] `feat:` — new user-facing capability

Linked issue: None. This is a focused operator-requested visibility improvement, not a claim to resolve a broader issue.

## OpenSpec

- [x] Includes a verified, archived OpenSpec change and synchronized main specs.

Change directory: `openspec/changes/archive/2026-09-25-allow-paused-account-reset-credit-visibility/`

Upstream request/response formats and OAuth exchange behavior are unchanged; this changes local dashboard read eligibility only.

## Changes

- Allow the selected paused account's count GET, preserving identity checks, token refresh/401 retry, proxy-route resolution and error envelopes.
- Preserve paused cached count/expiry in account summaries and the cached-detail GET. Weekly reset timestamps similarly remain last-observed data; cached credit badges are not a freshness guarantee.
- Keep request routing, background credit polling, and manual/automatic redemption disabled for paused accounts. Preserve existing deactivated/reauth policies.
- Add API/UI regression coverage and document the observation policy.

## Simplicity

- [x] Works with zero configuration; no new required setup.
- New settings / tiers / migrations: none.
- [x] No README, environment-variable or navigation budget changes.
- [x] Feature documentation lives in `docs/usage-reporting.md` and links to the owning OpenSpec capability.

## Test plan

On upstream main `09a140fa9` plus this change:

```text
make lint                                      passed
make typecheck                                 passed
pytest accounts/reset-credit API+mapper+scheduler suites  123 passed
pytest auth_manager/auth_guardian -k paused       2 passed
vitest account-detail/account-actions/use-accounts       24 passed
git diff --check                               passed
```

The change and reset-credit main spec passed strict OpenSpec validation. Full `openspec validate --specs --strict` reports **49 passed / 17 failed**; these are pre-existing failures (the original base comparison had the identical error map). No new validation errors were introduced. This PR remains draft pending CI/review and resolution or maintainer disposition of th

*(описание сокращено, см. полный текст по ссылке на GitHub)*

**Прикрепленные изображения и скриншоты:**

- **Скриншот 1:**
  ![Скриншот 1](https://raw.githubusercontent.com/codemoo/codex-lb/9a9232cff0daeac504fc1e41d3a416569c11a254/docs/screenshots/paused-reset-credits/before.png)

- **Скриншот 2:**
  ![Скриншот 2](https://raw.githubusercontent.com/codemoo/codex-lb/9a9232cff0daeac504fc1e41d3a416569c11a254/docs/screenshots/paused-reset-credits/after.png)


---

### [✅ RESOLVED / MERGED IN FORK] [#2498: docs: add `supports_standalone_web_search` to the Codex provider example](https://github.com/Soju06/codex-lb/issues/2498)

- **Тип:** Issue / Предложение
- **Автор:** @solid-pixel
- **Дата создания:** 2026-09-25
- **Метки:** `bug, documentation, good first issue`

**Описание проблемы и предложенные изменения:**

## Problem

The Codex provider examples in the [README](https://github.com/Soju06/codex-lb#client-setup) and [client setup guide](https://github.com/Soju06/codex-lb/blob/main/docs/client-setup.md) omit `supports_standalone_web_search = true`.

With my setup, native web search was unavailable through the documented custom provider, even with `--search`. Codex used browser automation instead. Adding the capability setting restored native web search without changing or restarting codex-lb.

## Tested environment

- Codex CLI: `0.157.0`
- Model: `gpt-6-astra`, Low reasoning
- Authentication: ChatGPT login, with a codex-lb API key for the local proxy
- codex-lb: `1.24.0`, Docker image `ghcr.io/soju06/codex-lb:latest`, revision `84fde5a1ed5e0d5a58ccb3ec4b82938b059bf8c5`
- Platform: macOS with Docker Desktop
- Provider base URL: `http://127.0.0.1:2455/backend-api/codex`

## Reproduction and comparison

Using the documented provider configuration, run:

```sh
codex --search -c 'model_provider="codex-lb"' \
  -m gpt-6-astra -c 'model_reasoning_effort="low"' \
  "Search today's top news"
```

In my test, Codex opened Google News through computer use instead of invoking native search. The same command with `model_provider="openai"` used native web search successfully.

Then run with the provider capability explicitly enabled:

```sh
codex --search -c 'model_provider="codex-lb"' \
  -c 'model_providers.codex-lb.supports_standalone_web_search=true' \
  -m gpt-6-astra -c 'model_reasoning_effort="low"' \
  "Search today's top news"
```

This restored native web search through codex-lb.

A separate authenticated request to the running proxy's `/backend-api/codex/alpha/search` endpoint also returned HTTP 200, valid JSON, and actual search results, confirming that this deployment already supports the endpoint.

## Suggested documentation change

Add the following line inside the existing `[model_providers.codex-lb]` block in both setup examples:

```toml
supports_standalone_web_search = true
```

Explain that `--search` / `web_search = "live"` selects the search mode, while this provider setting declares support for the standalone search endpoint. OpenAI's [web-search documentation](https://learn.chatgpt.com/docs/web-search) says custom providers default this capability to `false`; provider, model, and runtime support are also required. Please document any minimum supported versions rather than assuming this applies to all older clients/proxy releases.

This report concerns

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [✅ RESOLVED / MERGED IN FORK] [#2499: bug(model-sources): multi-agent capability does not preserve client collaboration tools](https://github.com/Soju06/codex-lb/issues/2499)

- **Тип:** Issue / Предложение
- **Автор:** @nhdong1993
- **Дата создания:** 2026-09-25
- **Метки:** `bug, help wanted`

**Описание проблемы и предложенные изменения:**

Codex can complete ordinary requests through an OpenAI-compatible Model Source while failing to use subagents. A source can advertise `multi_agent_version: "v2"` to the client, yet codex-lb still removes the client-supplied `collaboration` namespace from the upstream Responses request. Source-provided base instructions are also lost in the catalog projection.

### Environment and scope

- Observed on a self-built fork based on `1.25.0-beta.6`, before fork commit `00164ab0`; Docker Compose deployment, Codex CLI `0.156.1`.
- Enabled OpenAI-compatible Model Source with Responses, streaming, and tools support; custom model slug (`custom/coder` below is an anonymized example).
- HTTP Responses transport. The successful fix does not require WebSocket support or changing the source credential.
- Inspected upstream `main` at [`09a140fa`](https://github.com/Soju06/codex-lb/commit/09a140fa9979a908e60acc97232367e0a08ef32c): the same catalog projection and tool-filter behavior are still present. The deployed end-to-end verification below was on the fork, not a clean upstream-main deployment.

### Reproduction

1. Configure a Responses-capable source backed by a model whose own Codex catalog advertises multi-agent support.
2. Store the upstream capability metadata on its source model. The relevant excerpt is:

   ```json
   {
     "tool_mode": "code_mode_only",
     "multi_agent_version": "v2",
     "base_instructions": "Example upstream coding instructions",
     "experimental_supported_tools": [],
     "use_responses_lite": false
   }
   ```

3. Fetch `GET /backend-api/codex/models` or `GET /v1/models?client_version=0.156.1`. The source entry's `base_instructions` is empty despite being declared. The other raw capability fields can pass through when actually stored.
4. Refresh the client's catalog, select the custom model with `supports_websockets = false`, and ask Codex to spawn one child using the same model. Use a normal persisted session.
5. Observe the source-bound request: the client-supplied `type: "namespace"`, `name: "collaboration"` tool declaration is removed unless `namespace` was separately added to `experimental_supported_tools`. Ordinary `function` tools still survive.

For a deterministic route test, use a recording upstream stub to inspect `tools`. For an end-to-end test against a real Codex-compatible backend, use Codex's actual reserved collaboration schema; an abbreviated hand-written `spawn_agent` schema may itself be rejected by the backend.

##

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [✅ RESOLVED / MERGED IN FORK] [#2500: bug: #1968 shield-loop livelock still ships in latest stable 1.24.0; please cut a stable patch with #1969](https://github.com/Soju06/codex-lb/issues/2500)

- **Тип:** Issue / Предложение
- **Автор:** @nikhilshinday
- **Дата создания:** 2026-09-26
- **Метки:** `bug, triage`

**Описание проблемы и предложенные изменения:**

### Pre-flight checklist

- [x] I searched existing issues and confirmed this is not a duplicate.
- [x] I am running a supported codex-lb version (see Releases).
- [x] I can reproduce the problem with the steps below.

### codex-lb version

1.24.0 (`ghcr.io/soju06/codex-lb:1.24.0`, revision `84fde5a1`), the current **Latest** stable release.

### Deployment method

Docker (ghcr.io/Soju06/codex-lb), single instance, SQLite, 2 vCPU / 2 GB VM.

### Client used against codex-lb

Codex CLI and Codex app (desktop).

### ChatGPT account plan(s) involved

Mixed pool (5 accounts).

### Model(s) involved

gpt-6-sol, gpt-5.6-sol

### What happened?

The #1968 livelock hit our deployment on 1.24.0 after about 15 days of uptime. #1969 fixed it on main on 2026-08-30, but that fix has only shipped in `1.25.0-beta.*`. `1.24.0` is still the latest stable release, so stable users keep hitting it.

What we observed, all consistent with the #1968 autopsy:

- The app process pinned about 115% CPU on a 2-core box. Its lifetime average was about 5%.
- Across a 20-second py-spy profile, the main thread sat at `_outer_done_callback (asyncio/tasks.py:996/998)` in nearly every sample.
- RSS grew to 1.3 GB, mostly anonymous memory. The box has no swap, so SQLite page cache was squeezed out and I/O wait rose to about 40%.
- `/health/ready` took about 8 s. Request latency went from about 10 s to 85–240 s, and time to first token went from about 5 s to 50–110 s or never.
- Clients mostly saw `stream_incomplete` / `previous_response_not_found` ("Upstream websocket closed before response.completed"). That made it look like an upstream OpenAI failure. Upstream was healthy: direct and egress-proxied requests from the same host completed in about 0.1 s.
- The onset matched the first `http_bridge_session_close_timeout reason=retire_stale_pending` warnings. There were none in the prior 48 h, and 19 appeared in the first hour.
- A container restart cleared it immediately: health went to about 10 ms, CPU to about 1.5%, and RSS to about 225 MB.

A standalone reproduction confirms the mechanism is the one #1969 fixed. It copies the 1.24.0 `http_bridge/helpers.py::_await_task_deferring_cancellation` and awaits a never-finishing task under `anyio.move_on_after`:

| Python | callbacks on inner task after 6 s | CPU |
|---|---|---|
| 3.14 (the image's runtime) | about 23,000, still growing | one full core |
| 3.13 | 1 | about 30% (retry loop still spins) |

### What did you expect to happen?

A stable 

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [✅ RESOLVED / MERGED IN FORK] [#2501: bug: native HTTP upstream regressed in 1.25.0-beta.7 with native upstream request failures](https://github.com/Soju06/codex-lb/issues/2501)

- **Тип:** Issue / Предложение
- **Автор:** @milad2golnia
- **Дата создания:** 2026-09-26
- **Метки:** `bug, needs-info`

**Описание проблемы и предложенные изменения:**

### Pre-flight checklist

- [x] I searched existing issues and confirmed this is not a duplicate.
- [x] I am running a supported codex-lb version (see Releases).
- [x] I can reproduce the problem with the steps below.

### codex-lb version

1.25.0-beta.7

### Deployment method

Helm chart (oci://ghcr.io/soju06/charts/codex-lb)

### Client used against codex-lb

Codex app (desktop / web)

### ChatGPT account plan(s) involved

Pro

### Model(s) involved

gpt-5.6-sol, gpt-5.6-luna, gpt-5.6-terra, gpt-6-sol, gpt-6-astra

### What happened?

After upgrading a production deployment from `1.24.0-beta.2` to `1.25.0-beta.7`, the native HTTP upstream path became unreliable.

This HTTP failure pattern was not observed on `1.24.0-beta.2` under the same deployment topology and egress route.

With beta.7 and **Settings → Routing → Upstream stream transport = HTTP**, a similarly sized production window recorded:

- 687 successful HTTP-upstream requests
- 22 × `upstream_error: native upstream request failed`
- 48 × `upstream_unavailable: Upstream circuit breaker is open` following the native failures

All 70 HTTP transport/circuit-breaker errors had `upstream_transport=http`.

We changed the dashboard setting to `auto` during the incident. Overall failures decreased because most traffic was no longer forced through HTTP, but requests subsequently logged with `upstream_transport=http` still recorded **201 successes and 14 `native upstream request failed` errors**. No matching native-request failure appeared under another logged upstream transport.

### Observed error messages and their source

1. codex-lb dashboard / persisted request log: `native upstream request failed`
2. Codex Desktop UI: `stream disconnected before completion: idle timeout waiting for SSE`
3. Codex Desktop UI: `stream disconnected before completion: Transport error: network error: error decoding response body`

The two Codex Desktop disconnect messages were not present in codex-lb's persisted request logs or pod stdout.

### Persisted request-log evidence

The following fields come from codex-lb's persisted `request_logs` records, not pod stdout:

- `transport=http`
- `upstream_transport=http`
- `upstream_status_code=null` for the native failures
- native failure latency ranged from about 18.9 s to 279.8 s
- affected requests were spread across multiple models and reasoning efforts, not one model or one account

For the correlated failed requests, pod stdout only recorded a generic `upstream_error` / 

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [🟢 OPEN] [#2502: MySQL / MariaDB support](https://github.com/Soju06/codex-lb/pull/2502)

- **Тип:** Pull Request
- **Автор:** @snajpa
- **Дата создания:** 2026-09-26
- **Метки:** `documentation, db migration, ci, docker, python`

**Описание проблемы и предложенные изменения:**

# MySQL / MariaDB support

Runs the schema, the migrations and the runtime write paths on MySQL and MariaDB
as well as SQLite and PostgreSQL, keeping the existing backends behaviour-identical.

Base: `origin/main` at the time of posting (rebased: no merge commits).
Branch: `snajpa/mariadb-pr-20260926` (21 commits). The deployed instance on this machine also carries four fixes from another workstream (Astra pricing, a 420 s compact budget, and the `stream_incomplete` sticky reallocation fix with its test); they are deliberately not part of this PR and live on the deployment branch instead.

## What's in it

* `app/db/mysql_compat.py` — MySQL/MariaDB type rendering: unbounded `String` →
  `VARCHAR(255)`, `Text` → `MEDIUMTEXT`, `DateTime` → `DATETIME(6)`, `Float` →
  `DOUBLE`, keyed `LargeBinary` → `VARBINARY`. The compilers are registered for
  **both** the `mysql` and `mariadb` dialect names: MariaDB raises on a
  length-less `VARCHAR` where MySQL silently defaults it (this broke 121 columns).
* `app/db/dialect_sql.py` — one predicate/capability layer (`is_mariadb`,
  `epoch_seconds`, upsert and locking helpers) so call sites stop re-spelling
  dialect checks.
* Dialect-neutral writes across accounts, usage/rollups, API keys, dashboard,
  quota planning, sticky sessions, the HTTP bridge, file pins and request logs.
* Migrations that run on both engines, including MariaDB's refusal to index an
  expression (functional key parts become `VIRTUAL` generated columns) and
  `error 1832` when altering an FK parent's type.
* `migrate.py` tolerances for what MariaDB reflects differently: computed
  columns, boolean default synonyms, and the `now()` vs `current_timestamp(6)`
  default family (the default tokeniser folded precision but not family, which
  produced spurious `modify_default` drift on every `DATETIME(6)` column).
* Test harness: builds the schema once per test **file** on servers that keep
  tables. Rebuilding per test made the MySQL leg a multi-hour job; the first
  per-session fix was fast but leaked rows across files, so the shipped version
  resets rows per file and re-creates the ordered indexes `create_all` cannot
  emit. Also seeds engine-neutral datetimes (MariaDB strict mode rejects `+00:00`
  literals with 1292).
* `make test-mysql`, a compose service for a MySQL target, and a CI job.

## Performance work carried in this PR

The production instance logs every query over 0.5 s with plans
(`log_slow_verbosity=query_plan`). `request_logs` was the 

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [🟢 OPEN] [#2503: fix(http-bridge): keep replayed history images on the bridge](https://github.com/Soju06/codex-lb/pull/2503)

- **Тип:** Pull Request
- **Автор:** @Komzpa
- **Дата создания:** 2026-09-27
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

## Summary

Any inline `data:` image anywhere in the input made a request bypass the HTTP bridge. Agent clients replay the whole history every turn, so one screenshot attached early in a session kept every later turn off the bridge and cold on the prompt cache for the rest of the conversation.

Images now bypass the bridge only when they sit in the current-turn input suffix (after the last assistant message or model-output item), when an external `http(s)` image URL survives anywhere in the input, or when an `image_generation` tool is requested. Replayed inline images from earlier turns stay bridge-eligible and are forwarded unchanged below the size budget.

A second commit fixes the request log and transport decision counters: bypassed requests recorded the configured `auto` mode instead of the transport the attempt actually used. The client-side mode stays `auto` so the 426 fallback still works.

## Type of change

- [x] `fix:` — bug fix (no behavior change beyond the bug)

## OpenSpec

- `keep-replayed-history-images-on-http-bridge`
- `record-resolved-upstream-transport-label`

`docs/routing.md` describes the new bypass rule.

## Validation

- New unit and integration cases cover a current-turn image (bypasses), a replayed history image (stays on the bridge), a surviving external URL at depth with an upper-case scheme (bypasses) and the recorded transport label.
- `tests/unit/test_proxy_utils.py` and `tests/integration/test_http_promotion_accounting.py`: 1458 passed.


---

### [✅ RESOLVED / MERGED IN FORK] [#2504: fix(usage): account for cache-write tokens](https://github.com/Soju06/codex-lb/pull/2504)

- **Тип:** Pull Request
- **Автор:** @mastertyko
- **Дата создания:** 2026-09-27
- **Метки:** `documentation, db migration, python`

**Описание проблемы и предложенные изменения:**

## Summary

Account for upstream cache-write tokens separately from ordinary input and cached
reads. The existing pricing/catalog PRs intentionally deferred this usage
dimension; this does not duplicate the model additions in #2459.

- Preserve explicit write prices from models.dev/LiteLLM for the applicable
  service tier and context window. Extend existing snapshot entries only.
- Carry native Codex write counts through streaming, WebSocket, compact, warmup,
  request logs and API-key settlement. Charge writes instead of ordinary input.
- Persist nullable counts in request logs and reservations. Preserve historical
  unknown counts, recorded costs and settled limits.
- Keep request-log cost components consistent with the persisted total.

The change adds no setting, service, dashboard control or retry mechanism.
Existing reservation ownership/CAS and explicit external-model pricing are
unchanged. Missing write prices retain ordinary input pricing rather than
guessing a surcharge.

## Evidence

With Astra usage of 100000 input/write tokens and zero output, real local
`POST /v1/responses` previously recorded **$1.00** and settled **1000000**
microdollars. It now records **$1.25** in the input-cost component and total and
settles **1250000** microdollars. Direct WebSocket gives the same result after a
101 handshake.

Mixed input (100000 input, 20000 reads, 50000 writes, 1000 output) records
**$0.995** and settles **995000** microdollars. Duplicate terminal handling and
repeated finalization do not double charge. Real HTTP cases also cover absent,
negative/excessive and malformed counts, 272000/272001 context boundaries,
priority/flex, and unchanged GPT-5.1 usage. Owned test servers/databases were
cleaned up.

## Verification

- 456 affected cost, persistence, API-key and migration tests passed.
- 45 selected stream/bridge/WebSocket/cancellation regressions passed.
- After the final read-side fix, all 148 affected read-side cases passed again.
- New streaming/non-streaming and direct-WS regressions fail on the unchanged
  base, then pass with the fix.
- Migration upgrade/downgrade/re-upgrade, historical-row preservation and schema
  drift checks passed.
- `make lint`, `uv run ty check`, changed-file diagnostics and strict scoped
  OpenSpec validation passed.

Nine existing PostgreSQL-only migration tests were skipped in the local SQLite
run. Full local CI was not run; required GitHub checks remain the integration
gate. Whole-spec validation has the same 49 p

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [✅ RESOLVED / MERGED IN FORK] [#2505: bug: shutdown cancels schedulers and the leader-lease keeper mid-DB-work (SQLite pool CancelledError, unreleased lease, unclean run-state)](https://github.com/Soju06/codex-lb/issues/2505)

- **Тип:** Issue / Предложение
- **Автор:** @ngallodev
- **Дата создания:** 2026-09-28
- **Метки:** `bug`

**Описание проблемы и предложенные изменения:**

### Pre-flight checklist

- [x] I searched existing issues and confirmed this is not a duplicate. Closest are #1682 (leader-lease loss during runtime on single-instance SQLite) and #1981 (the wedged-teardown reclaim path). This report is about **shutdown ordering**: background tasks and the lease keeper are cancelled while inside DB work.
- [x] I am running a supported codex-lb version (built from `main`).
- [x] I can reproduce the problem with the steps below.

### codex-lb version

Source at `main` @ `09a140fa`.

### Deployment method

From source (`python -m app.cli`), single instance, file-backed SQLite (`sqlite+aiosqlite`, so the engine uses `NullPool`). Linux, Python 3.13, SQLAlchemy async + aiosqlite from `uv.lock`.

### Client used against codex-lb

Not client-dependent. This is server lifecycle (startup, then SIGTERM).

### ChatGPT account plan(s) involved

Not relevant. It reproduces on an empty database with no accounts.

### Model(s) involved

Not relevant.

### What happened?

When the server receives SIGTERM shortly after startup, shutdown cancels background scheduler tasks and the leader-lease keeper **while they are inside database work**. Two symptoms follow.

1. **Pool errors on SQLite.** SQLAlchemy logs `ERROR sqlalchemy.pool.impl.NullPool Exception closing connection …` (sometimes `Exception during reset or similar`), with a `CancelledError` traceback through the aiosqlite adapter's `rollback()` or `close()`.
2. **Unreleased leader lease and unclean SQLite run-state.** In `LeaderElection`, shutdown sets the keeper's stop event and then **unconditionally cancels it** (`app/core/scheduling/leader_election.py` around line 536). If the keeper is mid-renew, the lease row is not released. Shutdown then waits out the lease-release deadline (the process took about 10.5s to exit instead of about 0.5s), and the SQLite run-state stays `running`, so the next startup runs the integrity check.

Tasks observed holding a connection when cancelled, attributed by stamping the current task/coroutine onto the `sqlalchemy.pool` log records across 20 runs:

| Owner (coroutine) | Pool error records |
|---|---|
| `LeaderElection._run_release_keeper` | 6 |
| `ModelRefreshScheduler._refresh_as_leader` | 4 |
| `CacheInvalidationPoller._run` | 2 |
| `StickySessionCleanupScheduler._cleanup_as_leader` | 1 |
| `AccountUsageRollupScheduler._fold_as_leader` | 1 |
| `MetadataRefreshScheduler._run_loop` (missing-cost backfill) | 1 |

A separate instrumentation method (a 

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [✅ RESOLVED / MERGED IN FORK] [#2506: fix(shutdown): let DB-owning background tasks finish before cancelling them](https://github.com/Soju06/codex-lb/pull/2506)

- **Тип:** Pull Request
- **Автор:** @ngallodev
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

## Summary

On shutdown, background scheduler tasks and the leader-lease keeper are cancelled while they are still inside database work. On SQLite this logs `Exception closing connection` / `Exception during reset` pool errors, and cancelling the lease keeper mid-renew leaves the leader lease unreleased and the SQLite run-state `running`. That makes shutdown wait out the ~10s lease-release deadline and forces an integrity check on the next start. This PR lets each task finish the unit of work it's in, within a 2s grace, before falling back to cancellation.

> [!IMPORTANT]
> **PostgreSQL was not tested.** Every measurement below is on file-backed SQLite (`NullPool` + aiosqlite), where the pool-error symptom is specific. The code change is backend-independent, and so is the lease-keeper fix, but I did not reproduce the symptom or measure the fix on Postgres. The CI PostgreSQL job exercises the changed paths, but it is not a targeted reproduction.

## Type of change

- [x] `fix:` — bug fix (no behavior change beyond the bug)

Linked issue: Fixes #2505

## OpenSpec

- [x] This PR includes / updates an OpenSpec change

Change directory: `openspec/changes/drain-database-schedulers-on-shutdown/`. It adds a requirement to `graceful-shutdown`: "Background database tasks finish in-flight work before cancellation". The change is **not archived**, so review can happen before the spec is synced.

## Changes

- New `app/core/scheduling/task_shutdown.py` with `stop_task_after_grace(task)`:
  - waits up to `DATABASE_TASK_STOP_GRACE_SECONDS = 2.0` for the task to finish;
  - only after that cancels it, logging a WARNING that names the task's coroutine.
  - It waits through `wait_on_shared_future`, as `scripts/check_cancellation_safety.py` requires for tasks it cannot prove non-deferring. So it never cancels the task on a timeout, and it propagates a cancellation of the *caller* instead of swallowing it.
- The leader-lease keeper (`LeaderElection._stop_release_keeper`) now awaits the keeper after `stop.set()` instead of cancelling it immediately. This matches what the method's docstring already said it did: "Signals the keeper to exit and awaits it … Cancels as a fallback".
- The same stop behavior is applied, each after setting its existing stop event, to:
  - model refresh;
  - cache-invalidation poller;
  - sticky-session cleanup;
  - usage rollup;
  - metadata refresh (its missing-cost backfill);
  - quota planner.
- Idle tasks are unaffected: every one of these loops a

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [✅ RESOLVED / MERGED IN FORK] [#2507: feat(cli): add --log-level and --log-file; stop the metrics server resetting logging](https://github.com/Soju06/codex-lb/pull/2507)

- **Тип:** Pull Request
- **Автор:** @ngallodev
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

## Summary

codex-lb's runtime log level is hard-coded to INFO, and logs go only to stderr. So there's no way to turn on DEBUG without a code change, and in Docker the only copy of the logs is the container's json-file log, which is lost whenever the container is recreated. `CODEX_LB_LOG_LEVEL` looks like it should work, but no such setting exists. This PR adds `--log-level` and `--log-file` server flags. It also fixes the in-process metrics server resetting process-wide logging, which silently removed every access-log line when metrics were enabled.

## Type of change

- [x] `feat:` — new user-facing feature or capability

Linked issue: none. I found no upstream issue covering the logging flags or the metrics reset.

## OpenSpec

- [x] This PR includes / updates an OpenSpec change

Change directory: `openspec/changes/add-cli-log-level-and-file/`. It adds requirements to `proxy-runtime-observability`. The change is **not archived**.

## Changes

- **`--log-level {critical,error,warning,info,debug}`** (default `info`, unchanged behavior) sets the level for codex-lb's own `app.*` loggers.
  - uvicorn and third-party libraries stay at `info`, or at the chosen level when that's stricter. This applies both in the dictConfig and in the level passed to `uvicorn.Config`, which uvicorn applies to its own loggers.
  - As a result, `debug` covers codex-lb's records rather than protocol-level tracing: uvicorn's WebSocket frames and handshakes, and aiosqlite's per-cursor operations.
- **`--log-file PATH`** also writes everything printed to stderr/stdout, including access lines, to `PATH`.
  - It uses the same formatters, and rotates at 50 MiB × 10 backups through a **single** `RotatingFileHandler`. A `FileLogFormatter` picks the access or default formatter per record, so rotation has one owner.
  - The parent directory is created if needed, and an unwritable path fails startup instead of running without the file.
- **One startup record** from `app.cli` states the configured level, the file and the rotation, e.g. `Logging configured level=debug file=/var/lib/codex-lb/logs/codex-lb.log rotation=50MiBx10`. It's logged at INFO, or at the configured level when stricter, so it appears at every level.
- **Metrics fix:**
  - The Prometheus metrics server built its `uvicorn.Config` with uvicorn's stock `log_config` and `log_level="warning"`. uvicorn applies both **process-wide**.
  - So with `CODEX_LB_METRICS_ENABLED=true`, starting the metrics server dropped every access-log l

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [🟢 OPEN] [#2508: fix(proxy): reuse bridge sessions for inline images](https://github.com/Soju06/codex-lb/pull/2508)

- **Тип:** Pull Request
- **Автор:** @McHersheys
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

Fixes #2425. Related: #2465, #2503.

## Summary
Reuse bridge sessions for eligible inline images. Preserve fallbacks; do not replay images after an unacknowledged-create timeout. Reduce new cases from 22 to 11.

## OpenSpec
`reuse-http-bridge-inline-images`: active; overlapping delta rebased.

## Tests
474 selected tests passed; Ruff, scoped types, architecture and strict OpenSpec passed. Silent-image error: 0.214s with a 0.1s test deadline; the production 60s cap is unchanged.

**Held:** maintainer current-turn policy decision and authentic invalid-image upstream capture. Synthetic frames are not #903 evidence.


---

### [🟢 OPEN] [#2509: chore(deps): bump the frontend-minor-patch group across 1 directory with 16 updates](https://github.com/Soju06/codex-lb/pull/2509)

- **Тип:** Pull Request
- **Автор:** @dependabot[bot]
- **Дата создания:** 2026-09-28
- **Метки:** `dependencies, frontend`

**Описание проблемы и предложенные изменения:**

Bumps the frontend-minor-patch group with 16 updates in the /frontend directory:

| Package | From | To |
| --- | --- | --- |
| [@tanstack/react-query](https://github.com/TanStack/query/tree/HEAD/packages/react-query) | `5.102.8` | `5.103.2` |
| [lucide-react](https://github.com/lucide-icons/lucide/tree/HEAD/packages/lucide-react) | `1.45.0` | `1.48.0` |
| [react-hook-form](https://github.com/react-hook-form/react-hook-form) | `7.87.0` | `7.88.0` |
| [react-i18next](https://github.com/i18next/react-i18next) | `17.0.13` | `17.0.15` |
| [react-router-dom](https://github.com/remix-run/react-router/tree/HEAD/packages/react-router-dom) | `7.18.3` | `7.18.4` |
| [tailwind-merge](https://github.com/dcastil/tailwind-merge/tree/HEAD/packages/tailwind-merge) | `3.6.0` | `3.7.0` |
| [zod](https://github.com/colinhacks/zod) | `4.6.2` | `4.6.5` |
| [@types/node](https://github.com/DefinitelyTyped/DefinitelyTyped/tree/HEAD/types/node) | `26.5.1` | `26.6.2` |
| [@vitest/coverage-v8](https://github.com/vitest-dev/vitest/tree/HEAD/packages/coverage-v8) | `5.0.0` | `5.0.2` |
| [eslint](https://github.com/eslint/eslint) | `10.10.0` | `10.11.0` |
| [eslint-plugin-react-refresh](https://github.com/ArnaudBarre/eslint-plugin-react-refresh) | `0.5.6` | `0.5.7` |
| [jsdom](https://github.com/jsdom/jsdom) | `30.0.1` | `30.1.1` |
| [react-doctor](https://github.com/millionco/react-doctor/tree/HEAD/packages/react-doctor) | `0.9.13` | `0.9.14` |
| [typescript-eslint](https://github.com/typescript-eslint/typescript-eslint/tree/HEAD/packages/typescript-eslint) | `8.70.0` | `8.70.1` |
| [vite](https://github.com/vitejs/vite/tree/HEAD/packages/vite) | `8.3.0` | `8.3.1` |
| [vitest](https://github.com/vitest-dev/vitest/tree/HEAD/packages/vitest) | `5.0.0` | `5.0.2` |


Updates `@tanstack/react-query` from 5.102.8 to 5.103.2
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a href="https://github.com/TanStack/query/releases">@​tanstack/react-query's releases</a>.</em></p>
<blockquote>
<h2><code>@​tanstack/react-query-devtools</code><a href="https://github.com/5"><code>@​5</code></a>.103.2</h2>
<h3>Patch Changes</h3>
<ul>
<li>Updated dependencies []:
<ul>
<li><code>@​tanstack/query-devtools</code><a href="https://github.com/5"><code>@​5</code></a>.103.2</li>
<li><code>@​tanstack/react-query</code><a href="https://github.com/5"><code>@​5</code></a>.103.2</li>
</ul>
</li>
</ul>
<h2><code>@​tanstack/react-query-next-experimental</code><a href="https://github.com/5"><code>@​5</code

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [🟣 MERGED/CLOSED] [#2510: chore(deps): bump the python-minor-patch group across 1 directory with 11 updates](https://github.com/Soju06/codex-lb/pull/2510)

- **Тип:** Pull Request
- **Автор:** @dependabot[bot]
- **Дата создания:** 2026-09-28
- **Метки:** `dependencies, python`

**Описание проблемы и предложенные изменения:**

Bumps the python-minor-patch group with 11 updates in the / directory:

| Package | From | To |
| --- | --- | --- |
| [alembic](https://github.com/sqlalchemy/alembic) | `1.19.2` | `1.20.0` |
| [greenlet](https://github.com/python-greenlet/greenlet) | `3.5.5` | `3.5.6` |
| [mako](https://github.com/sqlalchemy/mako) | `1.4.1` | `1.4.3` |
| [sqlalchemy](https://github.com/sqlalchemy/sqlalchemy) | `2.0.52` | `2.1.0` |
| [urllib3](https://github.com/urllib3/urllib3) | `2.7.0` | `2.8.0` |
| [uvicorn](https://github.com/Kludex/uvicorn) | `0.52.4` | `0.54.0` |
| [ruff](https://github.com/astral-sh/ruff) | `0.16.6` | `0.16.9` |
| [ty](https://github.com/astral-sh/ty) | `0.0.78` | `0.0.84` |
| [openai](https://github.com/openai/openai-python) | `3.8.0` | `3.19.2` |
| [hypothesis](https://github.com/HypothesisWorks/hypothesis) | `6.167.1` | `6.168.1` |
| [hatchling](https://github.com/pypa/hatch) | `1.32.0` | `1.32.4` |


Updates `alembic` from 1.19.2 to 1.20.0
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a href="https://github.com/sqlalchemy/alembic/releases">alembic's releases</a>.</em></p>
<blockquote>
<h1>1.20.0</h1>
<p>Released: September 11, 2026</p>
<h2>usecase</h2>
<ul>
<li>
<p><strong>[usecase] [batch]</strong> Added a warning for the case where an unnamed CHECK constraint on a
reflected table is omitted from a batch &quot;recreate&quot; operation.  An unnamed
CHECK constraint can't be reliably carried over in a batch recreate
as it may refer to columns that are being dropped or changed.  This
omission was previously a silent operation.   The presence of any
<code>~sqlalchemy.schema.CheckConstraint</code> in
<code>Operations.batch_alter_table.table_args</code> is taken to indicate
that the case has been accommodated, and no warning is emitted.</p>
<p>References: <a href="https://redirect.github.com/sqlalchemy/alembic/issues/1846">#1846</a></p>
</li>
<li>
<p><strong>[usecase] [autogenerate]</strong> Autogenerate now renders a warning comment above any rendered
<code>Operations.drop_constraint()</code> directive for which the constraint name
is <code>None</code>, as is the case when a constraint that has no name in the model
is dropped, most typically within the <code>downgrade()</code> function of a
migration that adds an unnamed constraint.  A warning is also emitted on
the console when the migration script is generated.   The directive
requires a non-None name in order to be able to emit a &quot;DROP CONSTRAINT&quot;
command.</p>
<p>Refer

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [✅ RESOLVED / MERGED IN FORK] [#2511: bug(accounts): self_serve_business_prolite usage plan is rejected as unknown](https://github.com/Soju06/codex-lb/issues/2511)

- **Тип:** Issue / Предложение
- **Автор:** @h4zardi
- **Дата создания:** 2026-09-28
- **Метки:** `bug, triage`

**Описание проблемы и предложенные изменения:**

### Summary

OpenAI usage responses can report `plan_type=self_serve_business_prolite`. Codex-lb does not currently recognize that identifier, so a workspace-less account whose stored plan differs is rejected by the usage-refresh identity guard. The usage sample and plan update are both skipped.

### Reproduction

1. Start with a workspace-less account whose stored plan is a recognized paid plan such as `team`.
2. Refresh usage with a payload containing `plan_type=self_serve_business_prolite` and a valid rate-limit window.
3. Observe `Usage refresh payload identity mismatch; skipping account mutation`.

### Expected behavior

The upstream identifier should canonicalize to codex-lb's existing `prolite` tier before identity validation. The usage sample should be written, the stored plan should become `prolite`, Pro-equivalent model eligibility should apply, and existing Prolite capacity values should be used.

### Current main

Reproduced against `main` at `4dcf8f751b9b8ee8b55012eda7d459832f3ec51c`. A focused patch and product-path regression test are ready.


---

### [✅ RESOLVED / MERGED IN FORK] [#2512: fix(accounts): normalize business prolite plan alias](https://github.com/Soju06/codex-lb/pull/2512)

- **Тип:** Pull Request
- **Автор:** @h4zardi
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

## Summary

- canonicalize OpenAI's `self_serve_business_prolite` plan identifier to codex-lb's existing `prolite` tier
- apply the canonical value consistently to usage refresh, rate-limit metadata, capacity lookup, and Pro-equivalent model eligibility
- add product-path regression coverage for a workspace-less `team` account receiving the upstream alias
- document the compatibility behavior in an OpenSpec change

Closes #2511

## Why

The usage refresh identity guard only trusts recognized paid plans. Because the upstream identifier was unknown, codex-lb treated a legitimate paid-plan transition as an identity mismatch and discarded both the usage sample and account metadata update.

This is an alias for the existing local `prolite` tier, so the patch keeps one canonical stored value rather than adding a duplicate account plan. Unknown future identifiers retain their current behavior.

## Validation

- `pytest -q tests/unit/test_plan_types.py tests/unit/test_usage.py tests/unit/test_usage_updater.py` — 171 passed
- `ruff check` and `ruff format --check` on touched Python files
- `ty check`
- `openspec validate normalize-self-serve-business-prolite --strict`
- `openspec validate --specs --strict` — 66 passed
- full Docker image build from this commit
- network-isolated packaged-image probe confirmed `prolite`, Pro eligibility, and capacities 1125 / 37800

## Simplicity

No setting, migration, new tier, dashboard navigation, or setup step is introduced. The change is a single shared alias consumed by existing normalization paths.


---

### [🟣 MERGED/CLOSED] [#2513: fix(proxy): send a single Content-Type on codex control requests](https://github.com/Soju06/codex-lb/pull/2513)

- **Тип:** Pull Request
- **Автор:** @Soju06
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

## Summary

Extracted from #2065 (commit a7888982c by @nhdong1993) so the one-line fix can land without the rest of that branch.

`codex_control_request` built the upstream headers and then wrote the inbound media type as a second `Content-Type` field, so standalone search (`/backend-api/codex/alpha/search`) and realtime control calls reached upstream with two content-type headers. This replaces the header case-insensitively and in place (`_replace_header_preserving_position`, already used for `accept`), and drops every spelling when the request has no body.

Refs #2128 (the Content-Type half; the `/v1` alias question on that issue is a separate decision).

## Design impact

- No policy, default, setting or schema change. The control request keeps forwarding the inbound media type; it just stops emitting it twice.
- Contract recorded in `openspec/changes/preserve-codex-control-content-type/` (ADDED requirement under `responses-api-compat`: at most one case-insensitive `Content-Type` on unary Codex control requests, spelling and position preserved for native callers, bodyless requests omit it).
- Main spec files are not edited in this PR; the delta syncs at archive time.

## Verification

- `tests/unit/test_codex_upstream_paths.py::test_codex_control_request_preserves_single_media_type` (48 parametrized cases: direct/routed transport, three header spellings, JSON and SDP, native and SDK user agents) fails on main and passes here. Full file: 85 passed.
- `openspec validate preserve-codex-control-content-type --strict` passes; ruff check/format clean.

🤖 Generated with [Claude Code](https://claude.com/claude-code)


---

### [✅ RESOLVED / MERGED IN FORK] [#2514: feat(accounts): redeem all eligible reset credits in one action](https://github.com/Soju06/codex-lb/issues/2514)

- **Тип:** Issue / Предложение
- **Автор:** @Soju06
- **Дата создания:** 2026-09-28
- **Метки:** `enhancement, triage`

**Описание проблемы и предложенные изменения:**

## Problem / motivation

Operators with many pooled accounts currently redeem banked reset credits one account at a time from the Accounts page, or opt in to automatic redemption shortly before expiry (#1357 / #1358). There is no way to redeem every currently eligible credit in one action. Requested by a user via email (2026-09-17).

## Proposed change

Add a "Redeem all eligible reset credits" action to the Accounts surface that:

- redeems each account's own credits only (no cross-account pooling; see the decision on #2289),
- reuses the existing per-account redeem helper, durable ledger and per-account serialization,
- shows a confirmation listing the accounts and credit counts that will be consumed, and reports per-account success/failure,
- stays default-off in behaviour (it is an explicit operator click, never automatic).

## Out of scope

- Pooling credits across accounts (declined in #2289).
- Changing the auto-redeem scheduler semantics.


---

### [✅ RESOLVED / MERGED IN FORK] [#2515: fix(chat): keep the JSON instruction in input for json_object requests](https://github.com/Soju06/codex-lb/pull/2515)

- **Тип:** Pull Request
- **Автор:** @vitalNohj
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

## Summary

JSON mode (`response_format: {"type": "json_object"}`) breaks whenever the client asks for JSON only in the system message, which is how most clients do it. Every one of those requests comes back as:

```
Response input messages must contain the word 'json' in some form to use 'text.format' of type 'json_object'.
```

The upstream only counts the word "json" if it's in an input message. Top-level `instructions` don't count. #731 fixed this by keeping system and developer messages in `input` for JSON mode. #950 moved them back out into `instructions`, which brought the bug back (and #731's test was updated to expect the new output).

The upstream does accept a JSON mention in a `developer` message in `input` (it rejects `system` messages there). So for a `json_object` request, a system or developer message that mentions JSON now stays in `input` in its original position, sent as a developer message. Other system and developer messages still move into `instructions` like before.

## Type of change

- [x] `fix:` - bug fix (no behavior change beyond the bug)

Linked issue: Refs #730 (same bug, came back after #950)

## OpenSpec

- [x] This PR includes / updates an OpenSpec change

Change directory: `openspec/changes/keep-json-mode-mention-in-input/`

The `chat-completions-compat` spec still says JSON mode keeps these messages in `input` with their original role. That hasn't been true since #950, and the upstream rejects the `system` role there anyway, so the change says they're kept as developer messages.

## Changes

- `app/core/openai/requests.py`: when a request uses `json_object`, a system or developer message that mentions JSON stays in `input` with the developer role instead of moving into `instructions`.
- Nothing changes for:
  - requests without `json_object`
  - instruction messages that don't mention JSON
  - compact requests (they drop `text` anyway)
  - Responses Lite input
- The kept message doesn't depend on later user messages, so `input` is the same on every turn and the prompt cache and the derived prompt-cache key stay stable.

## Test plan

```
uv run pytest -n 2 tests/unit/test_chat_request_mapping.py tests/unit/test_openai_requests.py \
  tests/unit/test_prompt_cache_key_derivation.py tests/integration/test_openai_compat_features.py \
  tests/integration/test_proxy_chat_completions.py
375 passed

uv run pytest -n 2 tests/unit
10370 passed, 96 skipped
```

The new tests fail on current `main` (7 of them, including the `/v1/chat

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [✅ RESOLVED / MERGED IN FORK] [#2516: docs: declare native web search support in Codex examples](https://github.com/Soju06/codex-lb/pull/2516)

- **Тип:** Pull Request
- **Автор:** @solid-pixel
- **Дата создания:** 2026-09-28
- **Метки:** `documentation`

**Описание проблемы и предложенные изменения:**

## Summary

The Codex examples omit the provider capability needed to expose standalone web search with supported custom-provider setups. Add `supports_standalone_web_search = true` to all five ordinary `codex-lb` provider blocks across the English and Chinese READMEs, client setup guide, and downloadable configuration, with a codex-lb >= 1.22.0 note.

Closes #2498

## Type of change

- [x] `docs:` — documentation only

## OpenSpec

- [x] Not applicable — docs / CI / chore only

Documents existing endpoint support. The setup explanation links to the existing Responses compatibility specification; no proxy runtime or protocol changes.

## Changes

- Keep README edits to one configuration line each; translate the minimum-version comment in the Chinese README.
- Explain the provider capability, live-search mode, and distinction from the experimental feature flag in `docs/client-setup.md`.
- Preserve all other configuration values, including the separate Daybreak provider, which does not use the ordinary control-route path.

## Test plan

- `mkdocs build --strict`: passed using a temporary environment with the project's `mkdocs-material>=9.6` documentation dependency.
- Python `tomllib`: parsed the TOML snippets and downloadable configuration in all four changed files; verified all five ordinary provider blocks enable search and every other parsed value matches the base revision.
- `git diff --check`: passed.
- Runtime tests and the full application CI suite were not run for this documentation-only change.

## Coordination

#2312 was still open and unmerged when this branch was published. This PR is based on current `main` and leaves model selections unchanged.

## Checklist

- [x] Title follows Conventional Commits.
- [x] Linked the related issue.
- [x] Reviewed simplicity gates P1–P6: this documents an existing Codex client setting; no new server setting, README section, dashboard item, or runtime default.
- [x] CHANGELOG is not edited by hand.


---

### [✅ RESOLVED / MERGED IN FORK] [#2517: fix(telemetry): map codex_cli_rs user agent to codex-cli family](https://github.com/Soju06/codex-lb/pull/2517)

- **Тип:** Pull Request
- **Автор:** @drakeo338
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

## Summary

`CLIENT_FAMILY_BY_RAW_GROUP` never mapped the `codex_cli_rs` user-agent group from the interactive Codex CLI, so those requests counted as `other` instead of `codex-cli`, skewing the telemetry client mix. This adds the mapping, syncs the spec, and extends the covering test.

## Type of change

- [x] `fix:` — bug fix (no behavior change beyond the bug)
- [ ] `feat:` — new user-facing feature or capability
- [ ] `refactor:` — internal refactor (no behavior change, no API change)
- [ ] `docs:` — documentation only
- [ ] `chore:` / `ci:` / `build:` — tooling, CI, packaging
- [ ] `test:` — test-only change
- [ ] **Breaking change** (also append `!` after the type, e.g. `feat!:` or include `BREAKING CHANGE:` footer)

Linked issue: Fixes #1843

## OpenSpec

- [ ] This PR includes / updates an OpenSpec change
- [x] Not applicable — bug fix that matches the existing spec (spec.md already documents this family collapse)
- [ ] Not applicable — docs / CI / chore only
- [ ] This PR touches a codex-faithful path (image pipeline, request/response
      shape, SSE framing, OAuth flow) and preserves upstream-equivalent behavior

Change directory: n/a

## Changes

- Add `codex_cli_rs` → `codex-cli` to `CLIENT_FAMILY_BY_RAW_GROUP`
- Sync the mapping table in `openspec/specs/telemetry/spec.md`
- Extend `test_client_mapping_table_and_unknown_family_are_allowlisted` to cover `codex_cli_rs`

## Simplicity

No new setting, config, or user-visible surface.

- [x] New feature defaults to **off** or works with **zero config**
- [x] No new required setup step (or maintainer approval via `simplicity-budget-approved` label)
- New setting(s) and why each can't be a default: none
- Tier of each new setting (T0-T4 per PRINCIPLES P6) and, for T3, its `dashboard_settings` column: none
- [x] README sections / `.env.example` / dashboard nav within budget (or `simplicity-budget-approved` label requested)

## Test plan

```
# uv run pytest tests/unit/test_<area>.py -q
uv run pytest tests/unit/test_telemetry_snapshot.py -k test_client_mapping_table_and_unknown_family_are_allowlisted -v
# 1 passed
uv run pytest tests/unit/test_telemetry_snapshot.py -q
# 22 passed
# uv run pytest tests/integration/test_<area>.py -q
# not applicable — no integration surface touched
```

## Screenshots / output

Not applicable — no dashboard- or proxy-visible surface changes.

## Checklist

- [x] Title is in Conventional Commits format (`<type>(<scope>)?: <subject>`).
- [x] Linked the related issue / dis

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [✅ RESOLVED / MERGED IN FORK] [#2518: test(db): cover the SCIM/overflow merge revision's single-head convergence](https://github.com/Soju06/codex-lb/pull/2518)

- **Тип:** Pull Request
- **Автор:** @aacarcrash
- **Дата создания:** 2026-09-28
- **Метки:** `python`

**Описание проблемы и предложенные изменения:**

## Summary

Adds regression coverage for the alembic merge at
`20260918_000000_merge_scim_and_overflow_heads`, which converged the SCIM-token
(#2431) and subscription-overflow-retirement (#2422) migration histories.
#2461 shipped the merge revision but no test asserted the graph has a single
head or that both parent branches converge and round-trip through it.

## Type of change

- [x] `test:` — test-only change

Linked issue: relates to #2461, follow-up to #2462 (closed; see maintainer's
comment there for the scope of this PR)

## OpenSpec

- [x] Not applicable — bug fix that matches the existing spec

This PR adds test coverage only. No behavior, schema, or migration change.

## Changes

- `tests/integration/test_migrations.py`: add
  `test_scim_and_overflow_retirement_lineage_is_single_and_round_trips`, which
  asserts `ScriptDirectory.get_heads()` is the single merge revision, that its
  `down_revision` tuple is exactly the SCIM and overflow-retirement heads, that
  upgrading to head from a DB stamped at either parent converges on the same
  schema, and that downgrading from head back to either parent demultiplexes
  the merge into both parent revisions as current heads (proven via the
  `alembic_version` table) before a second upgrade reconverges.
- `.all-contributorsrc`: add `aacarcrash` (`code`), following the append-only
  convention and JSON shape of recent adds (e.g. #2453).

## Simplicity

Section removed: no new setting, README section, dashboard nav item, or
default changed.

## Test plan

```
uv run pytest tests/integration/test_migrations.py -k test_scim_and_overflow_retirement_lineage_is_single_and_round_trips -q
uv run pytest tests/integration/test_migrations.py -q
uv run ruff check .
uv run ruff format --check .
uv run ty check
python scripts/check_migration_topology.py
python3 .github/scripts/check_all_contributors.py
npx --yes @fission-ai/openspec@1.11.0 validate --specs
python3 .github/scripts/check_simplicity_budgets.py
```

Also verified the test is load-bearing: temporarily changed the merge
revision's `down_revision` to a single parent (breaking the graph) and
confirmed the new test fails with a real `AssertionError` on
`script.get_heads() == [merge_revision]`, not a collection error. Reverted
cleanly (`git diff` on the migration file is empty).

Not run locally: `migration-check-postgres` (no local PostgreSQL) and
`validate_changed_openspec.py` (requires a GitHub Actions `pull_request`
event payload; no OpenSpec files were changed

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [✅ RESOLVED / SUPERSEDED BY #2530] [#2519: fix(http-bridge): parse multi-line upstream websocket frames](https://github.com/Soju06/codex-lb/pull/2519)

- **Тип:** Pull Request
- **Автор:** @vitalNohj
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

## Summary

When the upstream rejects a request that goes through the HTTP bridge, some errors come back as pretty-printed JSON spread over several lines. The bridge only read the first line of each websocket frame, so those errors never reached the waiting request. The client waited for the idle timeout and got a 502 about a minute later, instead of the upstream's 400 right away.

The JSON-mode error from #2515 is one of these:

```
{
  "type": "error",
  "error": {
    "type": "invalid_request_error",
    "code": null,
    "message": "Response input messages must contain the word 'json' in some form to use 'text.format' of type 'json_object'.",
    "param": "input"
  },
  "status": 400
}
```

The bridge runs each frame through `parse_sse_data_json_text`, which keeps SSE rules for multi-line text. It frames the text as `data: {text}`, so only the first line (`{`) counts as data and the frame parses to `None`. The direct websocket path already parses each frame as one JSON document, which is why it isn't affected.

## Type of change

- [x] `fix:` - bug fix (no behavior change beyond the bug)

Linked issue: none, found while testing #2515.

## OpenSpec

- [x] This PR includes / updates an OpenSpec change

Change directory: `openspec/changes/parse-multi-line-bridge-websocket-frames/`

## Changes

- `app/core/utils/sse.py`: new `parse_websocket_json_text`, which decodes a websocket frame as one JSON document.
- `app/modules/proxy/_service/http_bridge/upstream_events.py`: the bridge uses it for frames the native egress didn't already interpret. A multi-line frame gets re-encoded as a single `data:` line before it's relayed, so the downstream SSE stays well-formed. Single-line frames keep the existing path and are relayed unchanged.
- `tests/integration/test_native_websocket_events.py`: the probe now expects the parsed payload for the `multiline` fixture (it expected `None` before) and the re-encoded block. It needs the native binary, so I couldn't run it here. I ran the same bridge checks against all 56 fixture frames in Python and they all pass.

## Test plan

```
uv run pytest -n 2 tests/unit/test_proxy_http_bridge.py tests/unit/test_http_bridge_cancel_drain.py \
  tests/unit/test_sse.py tests/integration/test_http_responses_bridge.py \
  tests/integration/test_native_websocket_events.py
1376 passed, 6 skipped

uv run pytest -n 2 tests/unit
10404 passed, 96 skipped
```

New tests:

- a pretty-printed error frame with LF, CRLF and CR line breaks settles the w

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [✅ RESOLVED / MERGED IN FORK] [#2520: refactor(proxy): extract streaming response entrypoint](https://github.com/Soju06/codex-lb/pull/2520)

- **Тип:** Pull Request
- **Автор:** @627444640
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

Moves the public `stream_responses` wrapper into `streaming/helpers.py` while preserving its signature defaults, header filtering, payload logging, lazy iterator return and retry ownership. `_StreamingMixin` binds the helper as its existing entrypoint.

This is the standalone relocation requested in [#2444's review](https://github.com/Soju06/codex-lb/pull/2444#issuecomment-5866465282). Related to #2444; this PR does not resolve #2443. Timing instrumentation and model-source usage changes are excluded. Contributor attribution is included to satisfy the repository gate.

Validation on `10598df24f371d3c3c6bd31764015acfa7be772b`:
- Existing proxy-utils and TTFT regression suites: **1,434 passed**.
- Ruff, Python type checks, proxy architecture, cancellation safety and clock-seam checks passed.
- The helper preserves the original wrapper body; no behavior/schema change, so this pure refactor is exempt from an OpenSpec change.

Cloud CI and independent maintainer review remain merge gates. No new settings or dependencies.


---

### [✅ RESOLVED / MERGED IN FORK] [#2521: fix(model-sources): validate optional usage and preserve streamed telemetry](https://github.com/Soju06/codex-lb/pull/2521)

- **Тип:** Pull Request
- **Автор:** @627444640
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

Optional model-source telemetry can overflow request-log integers, accept booleans as token counts, lose reasoning usage, or misread UTF-8/SSE framing split across network chunks. This change validates optional numeric metadata and preserves reported reasoning usage through both logging entrypoints while forwarding the original response bytes.

Extracted as requested in [#2444's review](https://github.com/Soju06/codex-lb/pull/2444#issuecomment-5866465282). Related to #2444; this PR does not resolve #2443. It changes no TPS threshold, report cohort, source classification, schema or stream timing state.

OpenSpec: `openspec/changes/archive/2026-09-28-harden-model-source-usage/` (verified and synchronized to `proxy-runtime-observability`).

Validation on `17e5d93a`:
- **306 passed** across source parser/forwarding and real API-path integration suites, using synthetic local upstreams.
- Invalid int32 values, boolean counts, finite-operand timing overflow, missing/known reasoning, fragmented UTF-8, multi-line SSE and split CRLF are covered.
- Ruff and full Python type checks passed; architecture/cancellation checks and contributor attribution passed.
- All **67** main specs plus the change passed strict validation with CI-pinned OpenSpec **1.11.0**.

Tests have no dependency on #2444's new timing columns. No new settings or dependencies. Cloud CI and independent review remain merge gates.


---

### [🟢 OPEN] [#2522: perf(db): request_logs facet indexes and loose-scan probes (stacked on #2502)](https://github.com/Soju06/codex-lb/pull/2522)

- **Тип:** Pull Request
- **Автор:** @snajpa
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, db migration, ci, docker, python`

**Описание проблемы и предложенные изменения:**

Stacked on #2502 (the dialect/DDL change). After that lands, this PR's diff is exactly the three `perf(db)` commits:

- `perf(db): index and reshape the dashboard's request_logs facets` — adds `idx_logs_facet_accounts` and `idx_logs_min_requested`, built `CREATE INDEX CONCURRENTLY` with invalid-index repair on PostgreSQL and through the dialect index helper on MySQL/MariaDB.
- `perf(db): loose-scan the facet enumeration on MySQL/MariaDB` — the facet pager enumerates distinct account ids without the recursive `min()` scan.
- `perf(db): probe the earliest row before the filtered aggregate` — the rollup fold probes the index-reachable earliest row before falling back to the scanning `MIN` aggregate.

Evidence on the rebased stack: migration checks green on SQLite, MariaDB 11.8 and MySQL 8.4 (`migration_policy=ok`, `schema_drift=none`); `tests/test_request_logs_options_api.py` → 13 passed, 1 skipped.

Please do not merge before #2502 — this branch is based on it.


---

### [✅ RESOLVED / MERGED IN FORK] [#2523: fix(metrics): publish fresh account pool gauges on scrape](https://github.com/Soju06/codex-lb/pull/2523)

- **Тип:** Pull Request
- **Автор:** @Abaddollyon
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

## Summary

`codex_lb_accounts_total` was declared but never populated, so operators had no account counts to alert on. It now reports a count for every status, including zeroes. The new `codex_lb_accounts_available` gauge counts accounts eligible by status and reauthentication-token expiry.

Fixes #2426.

## Type of change

- [x] `fix:` — bug fix

## OpenSpec

- [x] Includes an archived OpenSpec change and updated owning spec.

Change directory: `openspec/changes/archive/2026-09-28-publish-account-pool-metrics/`.
Owning spec: `proxy-runtime-observability`.

## Changes

- Refresh the existing account-cache snapshot before each scrape, so quiet pools, deletions and token expiry appear without proxy traffic. Failed refreshes return HTTP 503.
- Use the shared status and reauthentication-token expiry rules for availability. Pending deletions are excluded. The count is taken before model, API-key, affinity, live quota, cooldown, health and concurrency checks.
- Use the latest live-worker observation in multiprocess mode, avoiding duplicate pool counts and PID labels.
- Document metric scope and alert examples. Install Prometheus in the development group so exporter tests run in CI; runtime support remains optional.

The existing metrics listener has no application authentication. Restrict network access to trusted scrapers: each scrape performs one account query, and overlapping refreshes wait in an unbounded queue. Overload behavior was not benchmarked.

## Test plan

The regression scraped the real metrics app and failed on the original code because it returned no account series. After the fix:

```sh
uv run pytest tests/integration/test_account_pool_metrics.py \
  tests/integration/test_cache_invalidation_bus.py \
  tests/unit/test_metrics.py tests/unit/test_metrics_bind_guardrail.py \
  tests/unit/test_account_metrics_multiprocess.py -q --tb=short
```

All 54 tests passed on SQLite and PostgreSQL 18. They cover startup wiring, empty pools, every status, deletion, token expiry, failed scrapes, running without Prometheus, overlapping refreshes and multiprocess aggregation.

- `make lint` and `uv run ty check` passed.
- `uv run --group docs mkdocs build --strict` passed.
- Strict OpenSpec validation passed for the change and all 67 main specifications.
- Independent source review found no actionable issues.

Hosted CI and CodeRabbit passed on `5be4f58e`. The full local `make ci` gate was not run.

## Screenshots / output

Output from the metrics app created du

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [✅ RESOLVED / MERGED IN FORK] [#2524: fix(accounts): snapshot force probe state before session cleanup](https://github.com/Soju06/codex-lb/pull/2524)

- **Тип:** Pull Request
- **Автор:** @Abaddollyon
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

## Summary

Force Probe could return HTTP 200 while leaving an account in the `probing` health tier. `record_probe_result` read account and usage rows after its repository session had rolled back and closed, raising `DetachedInstanceError`.

The fix copies those rows with the existing snapshot helpers before closing the session. An older successful probe still cannot clear a newer failure, and lease activity does not invalidate the probe result.

Fixes #2410. The unsupported `max_output_tokens` field was already removed by #2496, which is included in this branch's base.

## Type of change

- [x] `fix:` — bug fix

## OpenSpec

- [x] Includes an archived OpenSpec change and updated owning spec.

Change: `openspec/changes/archive/2026-09-28-snapshot-force-probe-settlement/`.
Owning spec: `usage-refresh-policy`.

## Changes

- Snapshot the account, primary usage and selected long-window usage before repository teardown.
- Test the dashboard route with real sessions. Cases cover missing or partial usage, monthly windows, exhausted free-plan primary usage, concurrent health changes, lease activity and failed probes.

## Test plan

The six new successful-probe cases failed on the original code: the endpoint returned 200, logged `DetachedInstanceError`, and left the runtime error count unchanged. They pass with the fix.

```sh
uv run pytest tests/integration/test_accounts_api_probe.py \
  tests/unit/test_accounts_service_probe.py \
  tests/unit/test_load_balancer_concurrency.py -q
```

All 200 tests passed on SQLite and PostgreSQL 18.

- `make lint` and `uv run ty check` passed.
- Strict OpenSpec validation passed for the change and all 67 main specifications.
- Independent source review found no actionable issues.

Hosted CI and CodeRabbit passed on `0b29bfa7`. The full local `make ci` gate was not run.

<details>
<summary>Broader local test run</summary>

```sh
uv run pytest tests/unit tests/simulation tests/test_request_logs_options_api.py -q
```

The initial run had 10,441 passed, 94 failed, 5 skipped and 1 xfailed. All 94 failures passed on targeted reruns after correcting the local environment: 92 Helm cases needed Helm 4.3's supported Kubernetes default; two optional-dependency cases needed the branch's normal development environment. The full suite was not rerun.

</details>

## Screenshots / output

The regression calls `POST /api/accounts/{account_id}/probe` through the real route and database sessions, with synthetic upstream responses. The account star

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [✅ RESOLVED / MERGED IN FORK] [#2525: fix(model-sources): preserve source base instructions in catalogs](https://github.com/Soju06/codex-lb/pull/2525)

- **Тип:** Pull Request
- **Автор:** @Abaddollyon
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

## Summary

Source models could store `base_instructions`, but both Codex catalog routes returned an empty string. Copy the supplied string into the existing registry field so clients receive the source's instructions unchanged.

Refs #2499. This covers the catalog-projection bug; deriving namespace support from `multi_agent_version` is a separate contract proposal. Credit to nhdong1993 for the [report and reference fix](https://github.com/Soju06/codex-lb/issues/2499).

## Type of change

- [x] `fix:` — bug fix

## OpenSpec

- [x] Includes an archived OpenSpec change and updated owning spec.

Change directory: `openspec/changes/archive/2026-09-28-preserve-source-base-instructions/`.
Owning spec: `model-catalog-compat`.

## Changes

- Preserve string instructions exactly, including whitespace and Unicode.
- Keep the existing empty-string default for missing or non-string metadata.
- Test both Codex catalog routes and preserve existing capability metadata.
- Document source metadata imports and pinned client catalog refresh in the spec context.

## Test plan

The new regression selection failed on the original code in four cases: two string-preservation unit cases and both catalog routes. All four returned empty instructions.

```sh
uv run pytest tests/unit/test_model_sources_catalog.py \
  tests/integration/test_v1_models.py -q --tb=short
```

All 107 tests passed after the fix. `make lint`, `uv run ty check`, strict change validation and strict validation of all 67 main specifications passed. Independent source and contract review found no actionable issues.

An additional `make test-unit` run finished with 10,452 passed, 6 skipped, 1 xfailed and 92 Helm rendering failures. The installed Helm 4.0.0 defaulted to Kubernetes 1.20, below the chart's 1.32 minimum. Rerunning both affected test files with a temporary `helm template --kube-version 1.35.0` wrapper passed all 106 tests. The chart and those tests are unchanged from upstream.

The [hosted unit job](https://github.com/Soju06/codex-lb/actions/runs/36437005870/job/108977471867) reached 98% without a reported test failure before its 20-minute limit cancelled it. All other selected hosted jobs passed, but `CI Required` remains failed pending a maintainer rerun; the fork account could not rerun the cancelled job. CodeRabbit reviewed `6cba34d` and found no actionable issues.

The full local `make ci` gate was not run; this host lacks `trivy`, `kubeconform` and `kind`.

## Screenshots / output

For source met

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [✅ RESOLVED / MERGED IN FORK] [#2526: fix(model-sources): preserve declared collaboration namespaces](https://github.com/Soju06/codex-lb/pull/2526)

- **Тип:** Pull Request
- **Автор:** @Abaddollyon
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

## Summary

A Model Source could advertise multi-agent support while codex-lb dropped the client's collaboration namespace. Treat a nonblank string `multi_agent_version` as namespace support and let the existing capability filter preserve the complete tool definitions and matching choices.

Refs #2499. The base-instructions fix is separate in #2525. Credit to nhdong1993 for the [report and reference implementation](https://github.com/Soju06/codex-lb/issues/2499).

This is a draft pending the maintainer agreement requested on the issue. The proposed contract accepts any nonblank version string, including future versions. The OpenSpec change remains active until that decision, then its delta and context can be synchronized and archived.

## Type of change

- [x] `fix:` — bug fix with a source capability contract change

## OpenSpec

- [x] Includes an active OpenSpec change with a MODIFIED delta for the existing source-tool-filtering requirement.

Change directory: `openspec/changes/preserve-model-source-collaboration-tools/`.
Owning spec: `responses-api-compat`.

## Changes

- Derive namespace support from nonblank `multi_agent_version` metadata.
- Retain conservative filtering for absent, blank or non-string declarations and preserve explicit `experimental_supported_tools` opt-ins.
- Test both Responses endpoints and their trailing-slash forms against a recording upstream.
- Document capability imports, pinned catalog refresh and transport limits in the client guide.

## Test plan

The new catalog and route regressions failed before the fix because namespace support was absent and the source received no collaboration tools.

```sh
uv run pytest tests/unit/test_model_sources_catalog.py \
  tests/integration/test_model_source_collaboration.py -q
uv run pytest tests/integration/test_api_keys_api.py -q \
  -k 'source and (tool or search or namespaces)'
```

The first command passed 88 tests; the second passed 6. Coverage includes v1/v2 declarations, malformed values, explicit opt-in, nested schemas, three choice shapes, unsupported-tool pruning and existing replay behavior.

`make lint`, full `uv run ty check`, the strict docs build, strict change validation and all 67 main specifications passed. Independent source and contract review found no actionable issues. The full local `make ci` gate was not run; this host lacks `trivy`, `kubeconform` and `kind`. Hosted CI, including `CI Required`, passed on `94104a4`. CodeRabbit skipped the draft and still needs to rev

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [🟣 MERGED/CLOSED] [#2527: fix(routing): recover weekly-only Pro reserve accounts](https://github.com/Soju06/codex-lb/pull/2527)

- **Тип:** Pull Request
- **Автор:** @Concord-Devops
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, frontend, python`

**Описание проблемы и предложенные изменения:**

## Summary
- Treat weekly-only Pro usage in the upstream primary slot as the weekly recovery window without synthesizing a 5h quota.
- Clear stale replica-local quota cooldown after persisted recovery and fresh post-block weekly evidence, preserving unrelated rate-limit holds and sticky ownership.
- Expose manual Resume for quota-exceeded accounts and add backend/dashboard regression coverage.

## Validation
- 516 focused unit and integration tests passed after rebasing on current main.
- 17 dashboard action tests passed.
- Ruff passed; strict OpenSpec validation passed (67 specs).
- Full Windows suite cannot collect two existing Unix-only modules (`uvloop`, `fcntl`).

## Simplicity
- Zero-config behavior correction; no new settings, navigation items, or README sections.
- No issue is closed by this PR.

## Dashboard screenshots
- Pending before/after screenshots for dashboard-visible Resume control.


---

### [✅ RESOLVED / MERGED IN FORK] [#2528: fix(proxy): advertise GPT-6 max output tokens](https://github.com/Soju06/codex-lb/pull/2528)

- **Тип:** Pull Request
- **Автор:** @elmakus
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

## Summary

- advertise `max_output_tokens=128000` for `gpt-6-astra`, `gpt-6-sol`, and `gpt-6-luna` when the upstream Codex catalog omits the field
- preserve explicit upstream integer `max_output_tokens` as higher priority than the fallback
- add `/v1/models` regression coverage for the GPT-6 fallbacks and upstream precedence
- add the required OpenSpec change for `model-catalog-compat`

## Why

The upstream Codex model registry currently exposes GPT-6 context/reasoning metadata but omits `max_output_tokens`. `/v1/models` therefore returns `null` for the max-output fields even though OpenAI documents a 128K maximum output for these GPT-6 models. OpenAI-compatible clients that require a numeric capability then fall back to their own arbitrary local default.

## Verification

- `uv run pytest -q tests/integration/test_v1_models.py` -> 62 passed
- targeted GPT-6/raw-precedence tests -> 2 passed
- `openspec validate advertise-gpt6-max-output-tokens --strict --no-interactive` -> valid
- `openspec validate --specs` -> pass
- `git diff --check upstream/main..HEAD` -> pass

This only corrects advertised compatibility metadata. It does not alter request routing, context-window semantics, native Codex catalog behavior, or generation settings.


---

### [✅ RESOLVED / MERGED IN FORK] [#2529: fix(metrics): stop the metrics server from reconfiguring process logging](https://github.com/Soju06/codex-lb/pull/2529)

- **Тип:** Pull Request
- **Автор:** @ngallodev
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

Split out of #2507, as requested there.

## Problem

With `CODEX_LB_METRICS_ENABLED=true`, the metrics server is built with `uvicorn.Config(metrics_app, ..., log_level="warning")` (`app/main.py`). uvicorn applies a Config's logging to the whole process. It re-runs `dictConfig` with its stock `LOGGING_CONFIG` and sets `uvicorn.error` and `uvicorn.access` to WARNING. After the metrics server starts:

- the main server writes no more access lines;
- `uvicorn` and `uvicorn.access` use uvicorn's own formatters, so `uvicorn.error` records skip codex-lb's redaction.

## Fix

Pass `log_config=None, log_level=None` to the metrics server's `uvicorn.Config`, so it leaves the logging from the server command alone.

**Behavior note:** metrics scrapes (`GET /metrics` on the metrics port) now show up in the access log, because both servers log through the same `uvicorn.access` logger. This is intended, and the new test checks for it. I didn't use `access_log=False` for the metrics server, because uvicorn implements it by clearing that shared logger's handlers, which would switch off the main server's access log too. If you'd rather keep scrapes out of the log, a logging filter on the metrics port could go in a follow-up.

## Tests

- `tests/integration/test_metrics_server_logging.py` runs `python -m app.cli` as a subprocess with metrics enabled. After `/metrics` answers, it requests `/health` with a credentialed URL in the query, then checks three things: the access line is written, the credential is redacted, and the scrape is logged.
- On current `main` the test fails because the access line is missing. With this change it passes.
- It skips if `prometheus_client` (the optional `metrics` extra) isn't installed.

## Checks

- `openspec validate fix-metrics-server-logging-config --strict`: pass.
- `make lint`: pass.
- `ty check`: pass.
- A local CodeRabbit CLI review found nothing.

The `Contributors attribution` check will fail until #2506 lands, since that PR adds me to `.all-contributorsrc`. I'll rebase once it does.

OpenSpec: `openspec/changes/fix-metrics-server-logging-config/` (delta on `proxy-runtime-observability`).

🤖 Generated with [Claude Code](https://claude.com/claude-code)


---

### [✅ RESOLVED / MERGED IN FORK] [#2530: fix(http-bridge): parse multiline websocket JSON messages](https://github.com/Soju06/codex-lb/pull/2530)

- **Тип:** Pull Request
- **Автор:** @SantaDiegoKairos
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

## Summary

The HTTP bridge WebSocket parser treats multi-line (pretty-printed) JSON messages as a single SSE `data:` line, losing all content after the first newline. When upstream returns a pretty-printed error response, `type=error` is never seen by the bridge, the request stays pending, and the client eventually receives a misleading `upstream_request_timeout` instead of the actual error.

This was diagnosed via the conversation archive on a production deployment: upstream responded with a 400 error in ~2 seconds, but the panel reported 121 seconds of "eventless" silence followed by a timeout. The error message contained literal newlines, causing the parser to silently discard it.

**Fix**: parse the complete WebSocket text message as a JSON document regardless of LF/CRLF/indentation. When converting to SSE, serialize the parsed object correctly instead of wrapping raw multi-line text in a single `data:` prefix.

Fixes #2465 (Blocker 1: the "eventless" component)
Refs #2388 (bridge refusals as empty 200), #2493 (stream closed without terminal)

## Root cause

In `upstream_events.py`, native payload was only used when the text contained no LF/CR characters. Otherwise, `parse_sse_data_json_text()` wrapped the entire text in a single `data:` line. For compact JSON this worked; for pretty JSON (which OpenAI returns for some error types), everything after the first newline was lost:

```python
# Before: multi-line JSON wrapped as single SSE data line
# "data: {\"type\":\"error\",\n  \"code\":..." → only first line parsed
# After: full JSON document parsed regardless of formatting
```

## Test plan

- [x] New unit tests: pretty JSON error → correctly parsed, `type=error` delivered to client
- [x] Compact JSON behavior unchanged
- [x] SSE serialization of parsed multi-line objects produces valid SSE
- [x] Integration: upstream error response reaches client as error, not timeout
- [x] 157 targeted checks passed

## OpenSpec

Change folder: `openspec/changes/fix-multiline-websocket-json/` (strict validation passed)


---

### [✅ RESOLVED / MERGED IN FORK] [#2531: fix(proxy): normalize parallel_tool_calls for Responses-Lite upstream](https://github.com/Soju06/codex-lb/pull/2531)

- **Тип:** Pull Request
- **Автор:** @SantaDiegoKairos
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

## Summary

When the Responses-Lite upstream path is selected, the panel sends `parallel_tool_calls=true` in the outgoing request. The Lite endpoint requires `parallel_tool_calls=false` and responds with an immediate 400:

```
code: unsupported_value
type: invalid_request_error
param: parallel_tool_calls
message: X-OpenAI-Internal-Codex-Responses-Lite requires `parallel_tool_calls` to be false.
```

This 400 error was then compounded by the multiline JSON parsing issue (#2530): the error was silently swallowed, and the client received a two-minute timeout instead of the actual error. Together, these two bugs produced the "permanently eventless sticky lineage" described in #2465.

**Fix**: the Responses-Lite finalizer now sets `parallel_tool_calls=false` when the Lite upstream path is selected. Non-Lite paths are unchanged.

Fixes #2465 (Blocker 1: the Lite normalization component)
Refs #2530 (multiline JSON parsing fix — the other half of Blocker 1)

## Root cause

In `proxy.py`, the Lite finalizer already provided `reasoning.context=all_turns` but did not set `parallel_tool_calls=false`. The compact-payload path had this normalization; the general Lite path did not.

## Test plan

- [x] New unit tests: Lite path → `parallel_tool_calls=false`; non-Lite → unchanged
- [x] Integration: request to Lite upstream no longer receives 400
- [x] 66 targeted checks passed

## OpenSpec

Change folder: `openspec/changes/fix-responses-lite-parallel-calls/` (strict validation passed)


---

### [🟢 OPEN] [#2532: chore(docker): bump rust from 1.96.0-slim-bookworm to 1.98.1-slim-bookworm](https://github.com/Soju06/codex-lb/pull/2532)

- **Тип:** Pull Request
- **Автор:** @dependabot[bot]
- **Дата создания:** 2026-09-28
- **Метки:** `dependencies, docker`

**Описание проблемы и предложенные изменения:**

Bumps rust from 1.96.0-slim-bookworm to 1.98.1-slim-bookworm.


[![Dependabot compatibility score](https://dependabot-badges.githubapp.com/badges/compatibility_score?dependency-name=rust&package-manager=docker&previous-version=1.96.0-slim-bookworm&new-version=1.98.1-slim-bookworm)](https://docs.github.com/en/github/managing-security-vulnerabilities/about-dependabot-security-updates#about-compatibility-scores)

Dependabot will resolve any conflicts with this PR as long as you don't alter it yourself. You can also trigger a rebase manually by commenting `@dependabot rebase`.

[//]: # (dependabot-automerge-start)
[//]: # (dependabot-automerge-end)

---

<details>
<summary>Dependabot commands and options</summary>
<br />

You can trigger Dependabot actions by commenting on this PR:
- `@dependabot rebase` will rebase this PR
- `@dependabot recreate` will recreate this PR, overwriting any edits that have been made to it
- `@dependabot show <dependency name> ignore conditions` will show all of the ignore conditions of the specified dependency
- `@dependabot ignore this major version` will close this PR and stop Dependabot creating any more for this major version (unless you reopen the PR or upgrade to it yourself)
- `@dependabot ignore this minor version` will close this PR and stop Dependabot creating any more for this minor version (unless you reopen the PR or upgrade to it yourself)
- `@dependabot ignore this dependency` will close this PR and stop Dependabot creating any more for this dependency (unless you reopen the PR or upgrade to it yourself)


</details>

**Прикрепленные изображения и скриншоты:**

- **Скриншот 1:**
  ![Скриншот 1](https://dependabot-badges.githubapp.com/badges/compatibility_score?dependency-name=rust&package-manager=docker&previous-version=1.96.0-slim-bookworm&new-version=1.98.1-slim-bookworm)


---

### [🟢 OPEN] [#2533: chore(deps): bump the python-minor-patch group across 1 directory with 17 updates](https://github.com/Soju06/codex-lb/pull/2533)

- **Тип:** Pull Request
- **Автор:** @dependabot[bot]
- **Дата создания:** 2026-09-28
- **Метки:** `dependencies, python`

**Описание проблемы и предложенные изменения:**

Bumps the python-minor-patch group with 17 updates in the / directory:

| Package | From | To |
| --- | --- | --- |
| [alembic](https://github.com/sqlalchemy/alembic) | `1.19.2` | `1.20.0` |
| [greenlet](https://github.com/python-greenlet/greenlet) | `3.5.5` | `3.5.6` |
| [mako](https://github.com/sqlalchemy/mako) | `1.4.1` | `1.4.3` |
| [sqlalchemy](https://github.com/sqlalchemy/sqlalchemy) | `2.0.52` | `2.1.1` |
| [urllib3](https://github.com/urllib3/urllib3) | `2.7.0` | `2.8.0` |
| [uvicorn](https://github.com/Kludex/uvicorn) | `0.52.4` | `0.54.0` |
| [opentelemetry-api](https://github.com/open-telemetry/opentelemetry-python) | `1.44.0` | `1.45.0` |
| [opentelemetry-sdk](https://github.com/open-telemetry/opentelemetry-python) | `1.44.0` | `1.45.0` |
| [opentelemetry-exporter-otlp](https://github.com/open-telemetry/opentelemetry-python) | `1.44.0` | `1.45.0` |
| [opentelemetry-instrumentation-fastapi](https://github.com/open-telemetry/opentelemetry-python-contrib) | `0.65b0` | `0.66b0` |
| [opentelemetry-instrumentation-aiohttp-client](https://github.com/open-telemetry/opentelemetry-python-contrib) | `0.65b0` | `0.66b0` |
| [opentelemetry-instrumentation-sqlalchemy](https://github.com/open-telemetry/opentelemetry-python-contrib) | `0.65b0` | `0.66b0` |
| [ruff](https://github.com/astral-sh/ruff) | `0.16.6` | `0.16.9` |
| [ty](https://github.com/astral-sh/ty) | `0.0.78` | `0.0.84` |
| [openai](https://github.com/openai/openai-python) | `3.8.0` | `3.19.2` |
| [hypothesis](https://github.com/HypothesisWorks/hypothesis) | `6.167.1` | `6.168.1` |
| [hatchling](https://github.com/pypa/hatch) | `1.32.0` | `1.32.4` |


Updates `alembic` from 1.19.2 to 1.20.0
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a href="https://github.com/sqlalchemy/alembic/releases">alembic's releases</a>.</em></p>
<blockquote>
<h1>1.20.0</h1>
<p>Released: September 11, 2026</p>
<h2>usecase</h2>
<ul>
<li>
<p><strong>[usecase] [batch]</strong> Added a warning for the case where an unnamed CHECK constraint on a
reflected table is omitted from a batch &quot;recreate&quot; operation.  An unnamed
CHECK constraint can't be reliably carried over in a batch recreate
as it may refer to columns that are being dropped or changed.  This
omission was previously a silent operation.   The presence of any
<code>~sqlalchemy.schema.CheckConstraint</code> in
<code>Operations.batch_alter_table.table_args</code> is taken to indicate
that the case has been accommodated, and no warning is em

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [🟢 OPEN] [#2534: feat(proxy): admit bounded inline images on the HTTP responses bridge](https://github.com/Soju06/codex-lb/pull/2534)

- **Тип:** Pull Request
- **Автор:** @SantaDiegoKairos
- **Дата создания:** 2026-09-28
- **Метки:** `documentation, ci, python`

**Описание проблемы и предложенные изменения:**

# feat(proxy): bounded inline JPEG/PNG through the HTTP responses bridge

<!--
Commit title candidate: feat(proxy): admit bounded inline images on the HTTP responses bridge
Refs #2465 (partial: Blocker 2 only), Refs #2409, Refs #2425, Refs #2455
Do NOT use "Fixes #2465" — that issue has a second blocker this PR does not address.
-->

## What

Every `/v1/responses` request carrying an `input_image` part bypasses the HTTP
responses bridge today, so each image-bearing turn loses the thread's bridge
connection and prompt-cache reuse. Meanwhile an inline image the upstream
websocket rejects for size surfaces as a retryable `stream_incomplete` with
account exclusion — the observed close-1009 masking (#2465 Blocker 2).

This PR admits bounded inline images onto the bridge by default under two
explicit budgets, turns every oversize outcome into an explicit client error,
and classifies upstream websocket close 1009 as terminal payload evidence:

- **Admission (default on).** A request whose *every* `input_image` part is an
  inline `data:image/(jpeg|png);base64,` URL decoding to at most **5,000,000
  bytes (inclusive)** keeps using the bridge. A pre-decode fast path rejects
  encoded segments longer than 6,666,668 characters without decoding.
- **Whole-frame budget.** The complete serialized `response.create` frame —
  envelope, bridge operation id, thread-cache identity and installation
  metadata included — must stay at or below **64 MiB**, measured exactly at
  the final send (an early estimate rejects clear oversize sooner). The total
  budget deliberately permits several legal images plus long history; it is a
  local bound, **not** an upstream acceptance guarantee.
- **Explicit errors, never silent fallback.** An over-budget image or frame
  fails with the pre-send 400 `payload_too_large` (`param=input`,
  `invalid_request_error`). Size alone never selects the raw-HTTP bypass, and
  historical slimming never runs for image-bearing bridge requests. The
  operator HTTP pin and the recent-WS-failure health fallback keep their
  documented, logged behavior.
- **Fail-closed shapes.** External URLs, non-JPEG/PNG media, malformed
  base64, `file_id`/`sediment` references and `image_generation` requests
  keep today's blanket bypass/reject behavior — including when mixed with an
  over-budget inline sibling (unsupported shape wins).
- **Close 1009 is a terminal client error.** HTTP 400 when the response is
  uncommitted, the SSE `response.failed` envelope once events

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [🟣 MERGED/CLOSED] [#2535: feat: show pooled quota in Codex /status by serving and forwarding /backend-api calls](https://github.com/Soju06/codex-lb/issues/2535)

- **Тип:** Issue / Предложение
- **Автор:** @ngallodev
- **Дата создания:** 2026-09-29
- **Метки:** `enhancement, triage`

**Описание проблемы и предложенные изменения:**

### Pre-flight checklist

- [x] I searched existing issues and discussions for similar proposals.
- [x] This is a concrete proposal, not an open-ended question.

### Problem / motivation

Codex reads the quota it shows in `/status` and the status line from `<chatgpt_base_url>/wham/usage`. With the default base URL that request goes to chatgpt.com, so Codex shows only the account it is logged into. codex-lb routes model traffic across the whole pool, so what Codex shows and what the pool is doing disagree. With two accounts at 25% and 6% used, Codex reported 75% left when the pool actually had 85% left.

codex-lb already serves pooled usage at `/api/codex/usage`, but pointing `chatgpt_base_url` at codex-lb doesn't work today. Codex sends every other ChatGPT-backend call to the same base URL (account checks, user settings, plugins, cloud tasks, conversations), and codex-lb has no route for them, so those features break.

### Proposed change

Codex users can set `chatgpt_base_url = "<codex-lb>/backend-api"`. codex-lb then:

- serves `/backend-api/wham/usage` (and `wham/rate-limit-reset-credits/consume`) from the same handlers as the existing `/api/codex` routes, so `/status` shows pooled quota;
- forwards every other `/backend-api/*` call to upstream unchanged (method, path, query, body, streamed response). It uses the caller's own ChatGPT token and account id, never a pool account's token. The matched pool account supplies only its egress route (direct or upstream proxy pool).

Safety rules:

- Before anything leaves codex-lb, the caller's token is checked against the account it names, with the same check `/api/codex/usage` already uses. The confirmed pair is cached for 60 seconds, and each call still rechecks that the account is active.
- codex-lb API keys (`sk-clb-`), requests with no ChatGPT bearer, and paths under pool-routed namespaces (`codex/`, `files`, `transcribe`) are never forwarded. They get the normal 404/405, so model traffic can't bypass the pool.
- Redirects are relayed, not followed, and cookies are stripped both ways.

There are no new settings. Nothing changes unless a client is pointed at `/backend-api`, and rollback is removing that one line from the client config.

Known limit: connectors (`/backend-api/ps/mcp`) don't work with this setting. Codex's MCP client sends no credentials to non-chatgpt.com hosts, so there is no caller identity to forward, and substituting a pool account's identity would be wrong. Codex logs the failure and car

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [🟣 MERGED/CLOSED] [#2536: feat(proxy): show pooled quota in Codex /status by serving and forwarding /backend-api calls](https://github.com/Soju06/codex-lb/pull/2536)

- **Тип:** Pull Request
- **Автор:** @ngallodev
- **Дата создания:** 2026-09-29
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

## Summary

Point Codex's `chatgpt_base_url` at codex-lb's `/backend-api` and Codex's `/status` shows quota pooled across all accounts instead of only the account it is logged into. codex-lb serves `/backend-api/wham/usage` itself and forwards the other ChatGPT-backend calls Codex makes (account checks, user settings, plugins, cloud tasks) to upstream unchanged, under the caller's own identity.

Why: codex-lb already routes model turns across the pool, but Codex reads its status-line quota from `<chatgpt_base_url>/wham/usage`. With the default base URL that goes straight to chatgpt.com and covers one account. With two accounts at 25% and 6% used, `/status` showed 75% left before this change and 85% left after (pooled).

## Type of change

- [x] `feat:` new user-facing feature or capability

Closes #2535. Related to #2262 (partial overlap; this does not close it).

## OpenSpec

- [x] This PR includes / updates an OpenSpec change
- [x] This PR touches a codex-faithful path (request/response shape, SSE framing) and preserves upstream-equivalent behavior: forwarded paths, bodies, query strings and event streams reach upstream unchanged.

Change directory: `openspec/changes/archive/2026-09-28-forward-codex-chatgpt-backend-calls/` (archived in this PR; requirements are in `openspec/specs/codex-backend-passthrough/spec.md`, rationale in `context.md` next to it).

## Changes

- `/backend-api/wham/usage` and `/backend-api/wham/rate-limit-reset-credits/consume` are served by the same handlers as their `/api/codex` twins.
- A `/backend-api/{rest:path}` catch-all forwards unserved paths (GET/HEAD/POST/PUT/PATCH/DELETE) to upstream, streaming the response, using the caller's token and account id and the matched account's egress route (including upstream proxy pools).
- The raw percent-encoded path and query are forwarded byte for byte; a mismatch between raw and decoded path gets a 400. A mount prefix (`root_path`) is stripped before matching.
- One stream-end log record per forwarded call; DEBUG records for declines and identity checks.
- `docs/client-setup.md` documents the setting and its limits.

## Security model

- The caller's identity is verified before anything is sent out. The bearer token is checked against the account named in `chatgpt-account-id` with the same check `/api/codex/usage` uses. The confirmed binding is cached for 60 seconds; every call still rechecks that the account is active and resolves its current route.
- No pool token is forwarded. The p

*(описание сокращено, см. полный текст по ссылке на GitHub)*


---

### [✅ RESOLVED / MERGED IN FORK] [#2537: fix(images): route image requests through compatible host](https://github.com/Soju06/codex-lb/pull/2537)

- **Тип:** Pull Request
- **Автор:** @pkhadson
- **Дата создания:** 2026-09-29
- **Метки:** `documentation, python`

**Описание проблемы и предложенные изменения:**

## Problem
The Images adapter selected `gpt-5.6-luna` as its internal Responses host. In the current account pool, that host rejects the forced `image_generation` tool choice, while `gpt-5.6-sol` accepts it. This broke both image generation and edits, including reference-image edits.

## Change
- Add a dedicated ordered Images host resolver preferring `gpt-5.6-sol`, then compatible fallbacks.
- Keep default account-probe host selection unchanged.
- Route `/v1/images/generations` and `/v1/images/edits` through the Images resolver.
- Preserve the public `gpt-image-*` model and existing multipart `input_image` translation.
- Add OpenSpec context/spec delta and regression coverage for generation and edit routes.

## Validation
- `37 passed` unit tests for host selection and image translation.
- `63 passed` integration tests in `tests/integration/test_proxy_images.py`.
- Ruff check and format check passed.
- OpenSpec validation passed for `images-api-compat`; unrelated pre-existing repository spec failures remain.
- Docker image `codex-lb:latest` built successfully and passed `/health/ready` smoke test.


---
