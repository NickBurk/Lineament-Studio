# Предлагаемая структура репозитория

Статус `PROPOSED`. Phase 0 добавляет документацию и уточняет существующие проектные реестры. Ниже указаны каталоги, которые создаются при появлении первого владельца и проверяемого артефакта. [Архитектурное предложение](architecture/REPOSITORY_ARCHITECTURE_PROPOSAL.md)

```text
Lineament-Studio/
  AGENTS.md, README.md, README_MASTER.md, MASTER_TZ.md
  .agents/skills/                    # Engineering Skills Pack
  00_PROJECT/ … 12_PROJECT_CONTROL/  # v0.2.1 и проектные реестры
  docs/
    architecture/adr/
    templates/
    REPOSITORY_BOOTSTRAP_REPORT.md
    REPOSITORY_STRUCTURE.md
    PHASE_1_CORE_CONTRACTS_PLAN.md
  pyproject.toml                      # Phase 1
  .github/workflows/core.yml          # Phase 1
  src/
    lineament_core/
      domain/                        # Phase 1
      application/                   # Phase 1 — ports, registry, состояния
      contracts/                     # Phase 1 — JSON/JSONL и схемы
      infrastructure/                # Phase 2 — данные и файловые реализации
        gis/                          # GIS/Raster Engine
        storage/                      # Project Storage, SQLite Catalog
      adapters/                      # общий IPC client по необходимости
      worker/                        # интеграция процесса после контрактов
    lineament_desktop/               # Phase 9, кроме раннего Map Canvas spike
  tests/
    unit/                             # Phase 1
    contracts/                        # Phase 1
    fixtures/                         # Phase 1 — маленькие JSON + описание происхождения
    integration/                      # Phase 2 — real-file и fault injection
    regression/                       # по мере появления критических сценариев
    scientific/                       # с первого численного метода
    e2e/                              # Desktop, QGIS и Windows acceptance
    performance/                     # отдельный запуск и артефакты
  integrations/qgis/                 # Phase 13 — отдельный ZIP и метаданные QGIS
  packaging/windows/                 # spike, затем Onedir spec и Inno Setup
```

Минимум для Phase 1 — `pyproject.toml`, один лёгкий дистрибутив с `src/lineament_core/{domain,application,contracts}`, `tests/{unit,contracts,fixtures}` и workflow Core. Manifest/IPC schemas размещаются рядом с их владельцами. Если схемы нужны внешним клиентам, они включаются в wheel как ресурсы и проверяются из установленного артефакта. Алгоритмические модули добавляются по фазам. Qt runtime, QGIS provider и installer имеют собственные точки входа. [План Phase 1](PHASE_1_CORE_CONTRACTS_PLAN.md)

## Проект настройки `pyproject.toml`

| Секция | Предложение |
|---|---|
| `[build-system]` | PEP 517 backend Hatchling. Один backend для Core wheel и sdist. Версию инструмента фиксировать в dev/build lock после проверки |
| `[project]` | Имя `lineament-core`, `requires-python = ">=3.11,<3.12"` как стартовая поддерживаемая линия. Runtime зависимости ядра Phase 1 отсутствуют. Версия пакета независима от v0.2.1 спецификации |
| `[tool.hatch.build.targets.wheel]` | Явно включить `src/lineament_core` и схемы, когда они появятся |
| `[dependency-groups]` | `dev` для pytest, Ruff и mypy. `audit` для pip-audit. Окружения Windows Bundle и QGIS проектируются отдельно после runtime spike |
| `[tool.ruff]`, `[tool.mypy]` | Ruff format и Ruff check для стиля, импортов и простых ошибок. Mypy для typed public contracts/domain. Проверку межслойных импортов добавить в contract suite |
| `[tool.pytest.ini_options]` | `testpaths = ["tests"]`, проверка неизвестных markers через `--strict-markers`, `--import-mode=importlib`. Регистрировать markers при появлении соответствующих тестов |

Менеджер зависимостей к согласованию — uv с проверяемым lock для Core/dev. В CI установка через `uv sync --locked`, build и установка wheel в новом окружении. Для Windows Bundle — отдельный lock целевой платформы и хеши артефактов либо `conda-lock`, если выбран согласованный conda-forge runtime. Изменения lock проверяются по лицензии, размеру, ABI и security advisories. Дистрибутивы QGIS и Windows не добавляются в обязательные зависимости Core. [Совместимость](architecture/DEPENDENCY_COMPATIBILITY.md)

## Проверки и CI

- Каждый PR в проекте после появления Core запускает на Windows и Linux с Python 3.11 форматирование, линт, типизацию, pytest и сборку wheel. Linux проверяет переносимость Core, Windows — целевую платформу и пути. Критичные тесты форматов проверяют реальные синтетические файлы. [Testing Strategy](../09_SCIENCE_AND_QA/TESTING_STRATEGY.md)
- Предложенные команды Phase 1 включают `uv sync --locked`, `uv run --locked ruff format --check .`, `uv run --locked ruff check .`, `uv run --locked mypy src/lineament_core`, `uv run --locked pytest -ra` и `uv build`. Отдельный job устанавливает готовый wheel в чистое окружение и проверяет импорт из временного каталога.
- Для security использовать secret scanning/push protection при доступности, аудит Python lock, Dependency Review при доступности и проверку SBOM нативных компонентов перед релизом. Findings получают источник, версию, владельца и решение. Workflow на `pull_request` имеет `contents: read` по умолчанию. Сторонние Actions фиксируются по проверенным commit SHA. Секреты и право публикации доступны только доверенным release jobs.
- Тяжёлые Windows/GIS, QGIS, performance и научные suites запускаются отдельно по расписанию, вручную или на release candidate. Публиковать JUnit, версии runtime, параметры benchmark, peak memory и воспроизводимые файлы отчёта. Щадящие PR-проверки включают unit, contract и малые regression. [Release Requirements](../10_DELIVERY/RELEASE_REQUIREMENTS.md)
- Fixtures содержат синтетические данные, лицензию/происхождение и expected values. Проектные `.lspx`, SQLite sidecars, runtime caches, внешние DEM, секреты, локальные пути и сборки исключаются правилами с узкими исключениями для одобренных маленьких fixtures.

## Git и Pull Requests

Ветки ведутся по действующему Git Workflow. Для Phase 0 используется `bootstrap/repository-foundation`. Для будущих фаз PR содержит requirement/ADR IDs, ограниченный scope, тестовые команды и evidence, а также применимые migration notes, UI-материалы, benchmark и список рисков. Предложение для branch protection — обязательные проверки и независимое review перед merge, запрет force-push, разрешение merge по правилам владельца. Выбор базы PR следует подтвердить при настройке веток. [Git Workflow](../11_DEVELOPMENT/GIT_WORKFLOW.md) · [OQ-32](../12_PROJECT_CONTROL/OPEN_QUESTIONS.md)

### Phase 1 layout used by Core

The Core candidate starts with flat `domain.py`, `application.py`, `diagnostics.py`, `lifecycle.py`
and `wire.py` modules inside `src/lineament_core/`. Tests are grouped by boundary in `tests/`.
The repository currently uses locked Hatchling, Ruff and pytest. The architecture and tooling table
above remains a proposal for repository growth, including any dedicated static type checker.
[Installed wheel and CI evidence](PHASE_1_REPORT.md) · [Workstream paths](parallel/WORKSTREAM_OWNERSHIP.md)
