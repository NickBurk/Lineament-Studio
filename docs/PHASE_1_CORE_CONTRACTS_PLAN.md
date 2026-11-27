# Phase 1 — Core Contracts

Phase 1 разрешена пользователем и представлена на ревью. Цель — зафиксировать и проверить независимый Python Core, общий wire contract и правила эволюции API. Границы заданы Phase Breakdown и предложением по архитектуре. [Phase Breakdown](../11_DEVELOPMENT/PHASE_BREAKDOWN.md) · [Архитектурное предложение](architecture/REPOSITORY_ARCHITECTURE_PROPOSAL.md)

## Зависимости и рабочие пакеты

| Работа | Требования | Предлагаемые артефакты и проверки |
|---|---|---|
| P1-02 — Bootstrapping toolchain | NFR-COMP-001 | `pyproject.toml`, Core/dev lock, CI Windows/Linux CPython 3.11, wheel import smoke. По OQ-32 сначала создать skeleton, собрать wheel и установить его в чистом окружении CPython 3.11. Domain/Wire начинаются после smoke |
| P1-01 — Уточнить контракты | NFR-COMP-001/002, NFR-REL-001/002, NFR-SEC-001 | Рассмотреть ADR-0002, согласовать OQ-21–24. Определить UTF-8 framing, версию, handshake, errors, lifecycle, job ID и compatibility cases. Финальный review согласует общие JSON examples |
| P1-03 — Domain и error model | PROJ-003/006/008, DATA-002/009, RANK-001/003, NFR-UX-001, NFR-REPRO-001 | Минимальные модели Project/SourceAsset references, CRS и единицы, UUID, Job ID, ArtifactRef, error code и диагностический контекст. Разнести геометрический ранг и геологический порядок при затрагивании типов. Проверить инварианты и сериализацию |
| P1-04 — Wire contracts | NFR-COMP-002, NFR-REL-001/002, NFR-SEC-001/002, AC-JOB-001 | Версионированные schemas job/error/events/control, сериализация, валидация, compatibility matrix. Тестовые JSONL и subprocess harness для interop, UTF-8, malformed input, cancel, EOF и exit |
| P1-05 — Registry и правила задания | DEC-A22, NFR-REL-002, BAT-001 | Единственный реестр с типами входов/выходов, версией алгоритма, параметрами, ресурсами, progress/cancellation и семантикой ошибок. Чистые переходы состояний без IO. Проверить unknown/duplicate registration, unsupported version и cancel в тестовых fixtures |
| P1-06 — QA и handoff | NFR-COMP-001/002, NFR-SEC-001/002, NFR-REPRO-001 | Связать checks с требованиями и ADR, сохранить результаты и evidence для обеих ОС. Документировать публичный контракт, ограничения и входные условия Phase 2 |

Primary Skills — Requirements Engineer, Software Architect и QA Engineer. Python Desktop Developer применяется к Python tooling и исполняемым контрактам. Data Architecture Engineer проверяет модели ссылок и версии. Code Reviewer проводит независимое review до merge. Владение файлами и test IDs задаются при декомпозиции. [Skill Routing](SKILL_ROUTING.md)

Phase 1 включает contract-level версии и типы, необходимые downstream. Schema `.lspx`, SQL schema и механику хранения реализует Phase 2. Критерии ниже проверяют контракт и тестовый обмен. Desktop UI, полноценный production Worker, GIS runtime, SQLite persistence, DEM preprocessing, детекторы, LSM и пользовательские функции переходят в профильные фазы.

## Приёмка Phase 1

| ID | Given | When | Then |
|---|---|---|---|
| AC-CORE-001 | Чистые Windows x64 и Linux с Python 3.11, установлен Core wheel | Импортировать Domain и contract modules вне корня репозитория | Импорт успешен без GUI/GIS/runtime, проверка запрещённых зависимостей проходит |
| AC-CORE-002 | Зафиксированные положительные и отрицательные fixtures спецификации | Сериализовать/прочитать job и replay событий | Валидные messages round-trip, UTF-8 сохраняется, неизвестный job ID, повреждённый JSON и oversized input диагностируются |
| AC-CORE-003 | Совместимый и несовместимый handshake, неизвестное поле согласно таблице совместимости | Попытаться начать задание | Поддерживаемая версия принимается по правилам minor, несовместимая отклоняется стабильным кодом до выполнения |
| AC-CORE-004 | Тестовая операция на стадиях running, commit и terminal | Отменить дважды, потерять поток, получить stderr burst, смоделировать terminal race | Переходы проверены, terminal status единственный, transport failure видим клиенту, опубликованный результат сохраняется согласно состояниям |
| AC-CORE-005 | Registry с тестовыми дескрипторами и заведомо неизвестной операцией | Проверить версию, уникальность и schema параметров | Registry отклоняет неизвестную операцию/версию/дубликат и сообщает структурированную ошибку без выполнения |
| AC-CORE-006 | Error и event payload со строками Unicode и тестовым secret field | Сериализовать ошибку и diagnostic logs | Стабильный код и пояснение доступны, конфиденциальные поля исключены, event framing валиден |

Для проверки отсутствия публикации и восстановления в Phase 1 служат модели переходов и test doubles. Фактический commit/rollback, повреждённые файлы и reopen проверяются в Phase 2. Результаты, платформы, версии, команды и дефекты вносятся в QA report. Перед Phase 2 действуют OQ-25–28 и обязательный P1 gate по durable PREPARED journal, порядку восстановления и fault-injection. [ADR-0003](architecture/adr/ADR-0003-PROJECT-DATA-OWNERSHIP.md) [Открытые решения](../12_PROJECT_CONTROL/OPEN_QUESTIONS.md)
