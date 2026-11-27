# Phase 0 — Repository Bootstrap & Architecture Baseline

Дата: 2026-11-27. База: Master Specification v0.2.1. Ветка: `bootstrap/repository-foundation` от `origin/main`, SHA `57e7cc767766ef2b6a629980d1c8f8b6298b31a7`. Все 82 файла в базовом коммите, исходной рабочей копии и приложенном ZIP совпали побайтно. Локальная копия изначально не имела Git-коммита, поэтому существующий стартовый коммит GitHub использован как база ветки. Материалы Phase 0 находятся в рабочем дереве. Baseline commit и PR ожидают пользовательской проверки по правилам проекта. [New Repository Baseline](../12_PROJECT_CONTROL/NEW_REPOSITORY_BASELINE.md)

## Результат и границы

Проверены все разделы 00–12, корневые инструкции и manifests, архитектура, ADR-0001, четыре шаблона и 11 Skills. Зафиксированы расхождения, исправлены однозначные несогласованности метаданных и ссылок. Архитектурные варианты по IPC, данным и Windows runtime имеют статус Proposed. Реализация и тестовые suites приложения относятся к последующим фазам. [Master Specification](../README_MASTER.md) · [Исторический аудит v0.2.0](../12_PROJECT_CONTROL/DOCUMENTATION_AUDIT.md)

| Результат | Материалы |
|---|---|
| Границы Core, Desktop, Worker, Data/GIS, Registry, Job Manager, Storage и Catalog | [Архитектура репозитория](architecture/REPOSITORY_ARCHITECTURE_PROPOSAL.md) |
| PyPI metadata, Windows x64 wheel resolution, DLL/data inventory, условия runtime lock | [Совместимость зависимостей](architecture/DEPENDENCY_COMPATIBILITY.md) |
| Минимальное дерево, `pyproject.toml`, tooling, CI, security и PR policy | [Структура репозитория](REPOSITORY_STRUCTURE.md) |
| Рабочие пакеты, зависимости, GWT и evidence Phase 1 | [План Core Contracts](PHASE_1_CORE_CONTRACTS_PLAN.md) |
| Статусы, владельцы, способ и фазы закрытия решений | [Open Questions](../12_PROJECT_CONTROL/OPEN_QUESTIONS.md) · [Decision Register](../12_PROJECT_CONTROL/DECISION_REGISTER.md) |
| IPC lifecycle, владение данными и источник Windows GIS runtime | [ADR-0002](architecture/adr/ADR-0002-IPC-AND-JOB-LIFECYCLE.md) · [ADR-0003](architecture/adr/ADR-0003-PROJECT-DATA-OWNERSHIP.md) · [ADR-0004](architecture/adr/ADR-0004-WINDOWS-GIS-RUNTIME.md) |
| Исправления существующей документации | [README](../README.md) · [README Master](../README_MASTER.md) · [Roadmap](../11_DEVELOPMENT/DEVELOPMENT_ROADMAP.md) · [Project Storage](../04_DATA/PROJECT_STORAGE.md) · [Traceability](../12_PROJECT_CONTROL/REQUIREMENTS_TRACEABILITY.md) |

## Реестр несогласованностей и пробелов

Критичность относится к риску ошибочной реализации. Открытые вопросы закрываются до затронутого контракта или компонента. Статусы ранее согласованных продуктовых решений сохранены.

| ID | Риск | Наблюдение и источники | Статус и действие |
|---|---|---|---|
| B0-01 | Высокий | Project Storage и Decision Register связывали подсистему импорта иных проектов с аудитом. Clean start и ADR-0001 требуют отдельного решения о таком импорте. README Master также отсылал к аудиту существующих проектов. [Storage](../04_DATA/PROJECT_STORAGE.md) · [ADR-0001](architecture/adr/ADR-0001-LSPX-PROJECT-MANIFEST.md) | Исправлено в трёх документах, OQ-17 отложен |
| B0-02 | Средний | Roadmap перечислял 18 работ под заголовком «Фазы», а Breakdown закрепляет Phase 0–14. GEE и релизные работы сгруппированы по-разному. [Roadmap](../11_DEVELOPMENT/DEVELOPMENT_ROADMAP.md) · [Breakdown](../11_DEVELOPMENT/PHASE_BREAKDOWN.md) | Исправлено сопоставление направлений и ID фаз |
| B0-03 | Высокий | PRE-002 делает Multi-directional Hillshade P1, DEM Processing — P0. Slope тоже P0 в DEM Processing и P1 в PRE-003. Gaussian smoothing и Median filtering не имеют собственных FR. [FR](../01_REQUIREMENTS/FUNCTIONAL_REQUIREMENTS.md) · [DEM](../03_ALGORITHMS/DEM_PROCESSING.md) | Открыто, OQ-30/33 до Phase 3 |
| B0-04 | Высокий | DEC-A12 включает LSD в стартовый Balanced. DET-003 — P1, Canny и LoG — P0. Нужен профиль P0, который можно принять в Single/Ensemble. Детекторный scope и правила benchmark уточняются. [Decision Register](../12_PROJECT_CONTROL/DECISION_REGISTER.md) · [FR](../01_REQUIREMENTS/FUNCTIONAL_REQUIREMENTS.md) | Открыто, OQ-04/30 до Phase 4–6 |
| B0-05 | Высокий | MVP в Roadmap не перечисляет Desktop Bundle, а UI-001/004 — P0. AC-REL-001 проверяет чистый Windows Bundle, полный packaging в Roadmap указан для 1.0. Release Requirements явно требует все P0, отдельный порог готовности P1 отсутствует. [Roadmap](../11_DEVELOPMENT/DEVELOPMENT_ROADMAP.md) · [Acceptance](../01_REQUIREMENTS/ACCEPTANCE_CRITERIA.md) · [Release](../10_DELIVERY/RELEASE_REQUIREMENTS.md) | Открыто, OQ-30/34. Зафиксировать минимальную поставку MVP и отдельную приёмку v1.0 |
| B0-06 | Критический | `assets` в manifest дублируют данные источников в сфере ответственности SQLite. Владение полями relink/checksum, различие storage policy / per-asset mode и расхождение записей не определены. [Metadata Schema](../04_DATA/METADATA_SCHEMA.md) · [Data Model](../04_DATA/DATA_MODEL.md) | Предложен ADR-0003, OQ-25/27 |
| B0-07 | Высокий | В примере manifest placeholders `UUID`, `EPSG:XXXX` и URI `file:///absolute/or/relative/...`. Нет исполняемой схемы, точного URI grammar, required/nullable и правил неизвестных ключей. Контракт версий должен различать формат manifest и SQLite schema. [Metadata Schema](../04_DATA/METADATA_SCHEMA.md) · [Storage](../04_DATA/PROJECT_STORAGE.md) | Открыто, OQ-18/27 до Phase 2 |
| B0-08 | Критический | Атомарная замена manifest и транзакция SQLite описаны по отдельности. Нет общей границы публикации файла, rollback/recovery, lock writer и повторной попытки. [Storage](../04_DATA/PROJECT_STORAGE.md) · [NFR](../01_REQUIREMENTS/NON_FUNCTIONAL_REQUIREMENTS.md) | Предложен ADR-0003, OQ-24/26 |
| B0-09 | Высокий | API перечисляет события, но не связывает их с точным framing, отменой, совместимостью minor, ошибками, закрытием Worker и терминальным исходом. [API Contracts](../02_ARCHITECTURE/API_CONTRACTS.md) | Предложен ADR-0002, OQ-21–24 |
| B0-10 | Высокий | Desktop допускает собственные GIS-компоненты и оконное чтение. Worker обслуживает вычисления отдельно. Владелец IO карты и общий путь к данным не определены. [Desktop](../02_ARCHITECTURE/DESKTOP_ARCHITECTURE.md) · [System](../02_ARCHITECTURE/SYSTEM_ARCHITECTURE.md) | Открыто, OQ-01/29. Проверить на прототипе через Data Engine |
| B0-11 | Средний | Трассировка пропускала PROJ-005 и DET-006, ссылалась на PERF-001 и BUILD-001 вне нормативного каталога, агрегировала NFR без точных ID. [Traceability](../12_PROJECT_CONTROL/REQUIREMENTS_TRACEABILITY.md) · [FR](../01_REQUIREMENTS/FUNCTIONAL_REQUIREMENTS.md) · [NFR](../01_REQUIREMENTS/NON_FUNCTIONAL_REQUIREMENTS.md) | Исправлена адресация известных ID. Приоритеты NFR и отдельный release ID открыты, OQ-33 |
| B0-12 | Высокий | У 60 P0/P1 FR есть методы проверки. В Acceptance Criteria 10 сквозных GWT, отдельные ожидаемые результаты и evidence refs отсутствуют у части требований. PROJ-003/008, PRE/DET/LSM, BAT, UI и форматы экспорта требуют детализации. [Requirements Standard](../01_REQUIREMENTS/REQUIREMENTS_ENGINEERING_STANDARD.md) · [Acceptance](../01_REQUIREMENTS/ACCEPTANCE_CRITERIA.md) | Открыто, OQ-33. План Phase 1 задаёт собственные GWT на контракты |
| B0-13 | Высокий | DEC-U13 определяет ручной Backup. Storage задаёт поведение и предупреждение. Нет атомарного FR/AC на backup, scope транзакционно согласованного снимка требует уточнения. Smart Workflow для v1.0 тоже не имеет отдельного набора FR/AC при наличии спецификации. [Decision Register](../12_PROJECT_CONTROL/DECISION_REGISTER.md) · [FR](../01_REQUIREMENTS/FUNCTIONAL_REQUIREMENTS.md) · [Smart Workflow](../07_AI_ML/SMART_WORKFLOW.md) | Открыто, OQ-33/34 |
| B0-14 | Средний | DATA-005 формулирует online **или** local, OSM Integration перечисляет оба режима и несколько форматов. Для P1 приёмки нужен явный профиль обязательных режимов. [FR](../01_REQUIREMENTS/FUNCTIONAL_REQUIREMENTS.md) · [OSM](../08_INTEGRATIONS/OSM_INTEGRATION.md) | Открыто, OQ-10/30 |
| B0-15 | Высокий | Dataset Builder вводит Artifact, Review Studio вводит Needs Field Check. Каталог статусов и Annotation fields не описывают, являются ли они флагом, классом или внешней схемой. Dataset Builder и AC-DS-001 требуют явно согласовать допустимость spatial split override и интерпретацию отчётных метрик. [Review](../06_EXPERT_REVIEW/REVIEW_STUDIO.md) · [Dataset](../06_EXPERT_REVIEW/DATASET_BUILDER.md) · [Acceptance](../01_REQUIREMENTS/ACCEPTANCE_CRITERIA.md) | Открыто, OQ-35 |
| B0-16 | Высокий | Есть уровни научной валидации, metrics и fixtures. Отсутствуют зафиксированные holdout corpus, значения допусков по алгоритмам, критерии релиза и ответственные за независимость labels/полевых свидетельств. [Scientific Validation](../09_SCIENCE_AND_QA/SCIENTIFIC_VALIDATION.md) · [Benchmarks](../09_SCIENCE_AND_QA/BENCHMARK_DATASETS.md) | Открыто, OQ-20/31. Численные пороги выбираются по evidence |
| B0-17 | Высокий | LSM задаёт перенормировку после исключения группы. Нет результата для отсутствия всех групп, амбивалентного NoData на уровне пикселя и нулевой суммы весов. [LSM](../03_ALGORITHMS/LSM_SPECIFICATION.md) | Открыто, OQ-36. Уточнить mask, output semantics и тесты |
| B0-18 | Высокий | Технологические документы перечисляют GDAL, Rasterio и PyProj. Bundle не задаёт источник нативных библиотек и vector I/O. GDAL wheel отсутствует на целевой матрице, обнаружены три разных layout `proj.db`. [Desktop](../02_ARCHITECTURE/DESKTOP_ARCHITECTURE.md) · [Совместимость](architecture/DEPENDENCY_COMPATIBILITY.md) | Предложен ADR-0004, OQ-03/12/13/28 |
| B0-19 | Средний | Skills Integration описывает исходный набор. SHA-256 таблица содержит оригинальный хеш AGENTS.md, текущий AGENTS.md уже адаптирован для clean start. Оба значения имеют разное происхождение. [Source integrity](../11_DEVELOPMENT/AGENT_SKILLS/SOURCE_SHA256.md) · [AGENTS](../AGENTS.md) | Исторический digest сохранён. Актуальный hash и различие зафиксированы ниже |
| B0-20 | Средний | Ручное чтение правил в текущем workspace подтверждено. Инвентаризация Skills текущей сессии не служит проверкой их автоматического обнаружения на чистом Codex checkout. [Skills Integration](../11_DEVELOPMENT/SKILLS_INTEGRATION.md) | Открыто, OQ-19 |
| B0-21 | Низкий | Decision Register ссылался на v0.2.0 при статусе v0.2.1. MANIFEST.md и MANIFEST.json содержат инвентаризацию входного архива из 82 файлов. | Версия Decision Register синхронизирована. Manifests сохранены как инвентаризация исходной поставки. [Manifest](../MANIFEST.md) |
| B0-22 | Средний | Часть критериев производительности — ориентиры без подтверждённой целевой задержки и peak memory. Проверка 20k×20k нужна для tiled processing. [Performance](../09_SCIENCE_AND_QA/PERFORMANCE_REQUIREMENTS.md) · [NFR](../01_REQUIREMENTS/NON_FUNCTIONAL_REQUIREMENTS.md) | Открыто, OQ-14/29/31. Сохранить TBD до benchmark |
| B0-23 | Низкий | В Markdown спецификаций LSM и ranking двойное экранирование TeX-команд затрудняет чтение формул. [LSM](../03_ALGORITHMS/LSM_SPECIFICATION.md) · [Ranking](../03_ALGORITHMS/RANKING_SYSTEM.md) | Исправлено отображение формул. Их математический смысл и параметры сохранены |

## Проверка формата, приёмки и науки

Граница `.lspx` согласована в Master TZ, Project Storage и ADR-0001. В точке входа лежит JSON manifest, каталог — `project.sqlite`, векторы — GeoPackage, растры — GeoTIFF/COG. У папки есть группы inputs, processing, experiments, results, annotations, datasets, reports, cache и logs. Reference/Copy, ручной backup и сохранение результата при недоступном DEM отражены последовательно. Файл-пример является сугубо схематическим. Формальная схема и запись в несколько файлов требуют OQ-25–27. [Master TZ](../MASTER_TZ.md) · [Storage](../04_DATA/PROJECT_STORAGE.md)

| Область | Уже предусмотрено | До приёмки соответствующей фазы |
|---|---|---|
| P0, 27 FR | Методы проверки во всех строках. Сквозные GWT для create/reopen, missing source, Preflight, CRS, отмены, offline, clean Windows и path security | Детализировать Reference/Copy и checksum, явные ожидаемые значения и аспекты PRE/DET/POST/ENS/MSC/LSM/STR/RANK/EXP, GUI states и release profile |
| P1, 33 FR | Методы проверки во всех строках. GWT для независимой разметки и spatial split. Миграции, история и round-trip описаны в QA | Уточнить migration/rollback, геология/OSM/QGIS, Batch, форматы, UX, типы экспертных наборов/flags, ML/reports и отдельные Smart Workflow criteria |
| 16 NFR | Для всех указаны метод и метрика/порог либо потребность в benchmark. В трассировке заданы все точные ID | Присвоить приоритеты, измеримые thresholds, test references, владельца и evidence в профильных фазах |
| Тестирование | Unit, contract/integration, regression/recovery, security, GUI/E2E, scientific/performance, compatibility и packaging | Проверять позитивные, отрицательные, граничные и аварийные сценарии. Использовать реальные синтетические файлы и fault-injection, фиксировать команды, окружение и фактический результат |
| Научная валидация | Analytic surfaces, synthetic/real datasets, четыре уровня проверки, spatial holdout и provenance | До каждой научной фазы закрепить источник/формулу, accuracy и numeric tolerances, tile seam и NoData assertions. Отделить tuning от test. Документировать ошибки, spatial tolerance и чувствительность, ablation и независимую экспертную/геологическую проверку |

Тестовые каталоги и способы запуска предложены в структуре репозитория. Значения 6 ГБ Worker RAM и 1024×1024 tile остаются стартовыми параметрами. В Phase 1 проверяются инварианты контрактов. Проверка научных формул и геопространственных результатов начинается с первой соответствующей реализации. Результат исследования отделяет измеряемые линии, ранги, экспертные гипотезы и независимые свидетельства. [Трассировка](../12_PROJECT_CONTROL/REQUIREMENTS_TRACEABILITY.md) · [Scientific Validation](../09_SCIENCE_AND_QA/SCIENTIFIC_VALIDATION.md) · [Testing Strategy](../09_SCIENCE_AND_QA/TESTING_STRATEGY.md)

## Skills и инженерные правила

Все 11 `SKILL.md` прочитаны, их имена совпали с каталогами и их SHA-256 совпали с источником. Прикладные роли выбраны по маршрутизатору. Остальные пункты ниже проверены на согласованность требований. [Skill Routing](SKILL_ROUTING.md) · [Source SHA-256](../11_DEVELOPMENT/AGENT_SKILLS/SOURCE_SHA256.md)

| Skill | Что проверено в Phase 0 |
|---|---|
| `requirements-engineer` | Применён. Источники, scope, приоритеты, GWT, проверяемость и трассировка |
| `software-architect` | Применён. Зависимости Core, единый Worker, явные границы и ADR |
| `data-architecture-engineer` | Применён. Папка `.lspx`, источники истины, форматы, пути и recovery |
| `qa-test-engineer` | Применён. Evidence, статусы, матрица покрытий, real-file и fault-injection план |
| `gis-geospatial-engineer` | CRS, единицы, NoData, metadata, release drivers и offline grids |
| `scientific-computing-engineer` | Детерминированность, допуски, analytic fixtures и benchmark |
| `geomorphology-structural-geology-expert` | Отдельные geometric rank и geological order, provenance и независимые свидетельства |
| `python-desktop-developer` | Python 3.11, поток UI, закрытие процессов и файлов, ограничения packaging |
| `ui-ux-designer` | Доступность, keyboard/focus, состояния операций и восстановление |
| `code-reviewer` | Независимое review gate, severity, evidence и риски целостности |
| `release-engineer` | Чистая Windows, offline, DLL/driver inventory, лицензии и rollback |

Сверены все 18 строк source hash manifest. Совпали 17. Исключение — корневой AGENTS.md,
адаптированный в v0.2.1. Текущий SHA-256 `23e27a71b14a843ddd1d908acbf5d9cd4160df2fced0916c6cf09a7ca7bb98b5`.
Проверка воспроизводится через `hashlib.sha256(Path(path).read_bytes()).hexdigest()`. Создан отдельный
чистый checkout базового коммита. В этой среде запрос `skills/list` через локальный Codex app-server
не дошёл до сканирования, сервер завершился с `Read-only file system (os error 30)`. Для OQ-19
нужен запуск в целевой интеграции Codex Web.

## Основные риски и точки закрытия

| Риск | Как закрыть |
|---|---|
| R-04/R-15. DLL/data, ABI и неполная поставка | Нативный Windows spike и проверенные locks, затем Onedir и чистая Windows. OQ-03/12/13/28 |
| R-16/R-20. Прерывание записи и небезопасные пути | Один владелец записи, journal/recovery, version/schema и fault-injection. OQ-25–27 |
| R-01/R-03. Размытый MVP и сложность Map Canvas | Согласовать scope и прототип с измеримыми критериями. OQ-01/29/30/33 |
| R-02/R-06/R-07/R-08/R-13/R-14/R-19. Научная точность, tile seams и утечка выборки | Analytic/holdout fixtures, tolerances, detector family, ablation и независимое review. OQ-04–08/14/20/31/35/36 |
| R-18. Engineering Skills discovery | Чистый повторный checkout, inventory и evidence. Текущая работа сверена по файлам. OQ-19 |

Существующий [Risk Register](../12_PROJECT_CONTROL/RISK_REGISTER.md) сохраняет источник IDs и мер.

## Приёмка Phase 0 и evidence

| ID | Given | When | Then | Статус |
|---|---|---|---|---|
| AC-B0-01 | Стартовая документация и GitHub origin | Проверить Git, сравнить файлы и создать назначенную ветку | База совпадает с исходной спецификацией, работа ведётся в отдельной ветке без merge | Проверено |
| AC-B0-02 | Master v0.2.1, ADR, требования и Skills | Выполнить аудит перекрёстных требований и исходных файлов | Findings, scope конфликтов, evidence и владельцы открытых решений доступны | Проверено |
| AC-B0-03 | Целевые подсистемы и открытые архитектурные вопросы | Сверить границы и каталог решений | Есть одна роль каждой подсистемы, предложенное дерево и три ADR Proposed | Проверено по документам |
| AC-B0-04 | CPython 3.11, Windows x64 и заявленные технологии | Проверить wheel metadata, native inventory и риски | Есть проверяемые кандидаты, ограничения, воспроизведение и Windows gates, рабочий lock остаётся открытым | Проверено в границах metadata |
| AC-B0-05 | Требуется автоматическое discovery | Открыть чистый Codex Web checkout и сверить доступные инструкции | Корневой AGENTS и все 11 Skills обнаруживаются в целевой интеграции | Открыто, OQ-19. Ручное чтение подтверждено |
| AC-B0-06 | Есть Phase 1 scope и связанные требования | Сверить GWT и план по фазам | Описаны входные решения, артефакты, проверки и условия передачи в Phase 2 | Проверено по документам |
| AC-B0-07 | Пользователю переданы материалы | Проверить предложения и разночтения | Получено разрешение на вхождение в Phase 1 и решение о baseline commit/PR | Ожидается |

Фактически выполнены `git ls-remote --symref origin HEAD 'refs/heads/main' 'refs/heads/bootstrap/repository-foundation'`,
`git fetch --no-tags origin refs/heads/main:refs/remotes/origin/main`, `git ls-tree -r --name-only origin/main`,
побайтовое сравнение через `git show origin/main:<path>`, `git switch -c bootstrap/repository-foundation`,
инициализация индекса через `git reset --mixed origin/main` после сверки, `git rev-parse HEAD`,
`git status --short --branch`, SHA-256 audit и `uv pip compile` с платформой Windows x64.
Пройдены `git diff --check`, статическая проверка 146 относительных ссылок в 17 изменённых или новых
Markdown-файлах, 78 ID трассировки, 53 ранее принятых решений и 11 имён Skills. В SQLite in-memory
на Linux проверены foreign keys и RTree. Тесты приложения
относятся к будущим фазам. Windows runtime, GIS round-trip и автоматическое discovery остаются без
подтверждения. [Совместимость](architecture/DEPENDENCY_COMPATIBILITY.md)

Материалы готовы к рассмотрению. Приёмка discovery, решение о commit/PR и разрешение на Phase 1 остаются открытыми. [План Phase 1](PHASE_1_CORE_CONTRACTS_PLAN.md)
