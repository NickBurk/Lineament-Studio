# Lineament Studio

**Исследовательское desktop-приложение для анализа DEM и линейных форм рельефа.**

Lineament Studio предназначен для обнаружения и анализа кандидатов на линейные геоморфологические
и потенциальные структурно-тектонические элементы, экспертной проверки, подготовки датасетов
и воспроизводимых научных экспериментов.

> Обнаруженная линия — кандидат для дальнейшей интерпретации, а не автоматически доказанный разлом.

## Project status

Phase 1 Core Contracts интегрирована. Restricted Phase 2–3 development vertical slice
принята в `integration/phase-2-3-baseline` на `f7a52f7dd5d96b89ccdd34bf1b820e66a3bd483a`.
Реализованы backend Project Storage и Horn Hillshade; GUI и Detection пока отсутствуют.
PR #9 остаётся OPEN / DRAFT / NOT MERGED. Hardening проходит отдельное ревью.

Development acceptance не означает полную продуктовую приёмку Phase 2–3.
Открыты power-loss durability, миграции/rollback, standalone Windows GIS Bundle,
PROJ grids, QGIS coexistence, native licensing и научное сравнение. Phase 4 требует
отдельного разрешения. ADR-0003/0004 и OQ сохраняют действующие статусы.

## Source of truth

- [`MASTER_TZ.md`](MASTER_TZ.md) — Master Technical Specification.
- [`README_MASTER.md`](README_MASTER.md) — навигация по мастер-документации.
- [`00_PROJECT/`](00_PROJECT/) — назначение и scope.
- [`01_REQUIREMENTS/`](01_REQUIREMENTS/) — функциональные и нефункциональные требования.
- [`02_ARCHITECTURE/`](02_ARCHITECTURE/) — системная архитектура и контракты.
- [`03_ALGORITHMS/`](03_ALGORITHMS/) — DEM и аналитические алгоритмы.
- [`04_DATA/`](04_DATA/) — данные и формат проекта `.lspx`.
- [`06_EXPERT_REVIEW/`](06_EXPERT_REVIEW/) — экспертная разметка и датасеты.
- [`09_SCIENCE_AND_QA/`](09_SCIENCE_AND_QA/) — научная валидация и тестирование.
- [`11_DEVELOPMENT/`](11_DEVELOPMENT/) — roadmap и правила разработки.
- [`12_PROJECT_CONTROL/`](12_PROJECT_CONTROL/) — решения, риски, вопросы и трассировка.

## Codex engineering instructions

- [`AGENTS.md`](AGENTS.md) — постоянные правила для coding agent.
- [`.agents/skills/`](.agents/skills/) — 11 repo-local engineering Skills.
- [`docs/SKILL_ROUTING.md`](docs/SKILL_ROUTING.md) — выбор Skills для конкретной задачи.
- [`docs/templates/`](docs/templates/) — ADR, requirements, QA и phase report templates.

## Historical first milestone

**Phase 0 — Repository Bootstrap & Architecture Baseline.**

Prepare the repository, verify Codex instructions and Skills discovery, establish the minimal
developer workflow, and resolve architecture decisions before implementing application features.

Материалы Phase 0 включают [отчёт аудита](docs/REPOSITORY_BOOTSTRAP_REPORT.md),
[предлагаемую структуру](docs/REPOSITORY_STRUCTURE.md) и
[план Core Contracts](docs/PHASE_1_CORE_CONTRACTS_PLAN.md).

### Core and Desktop development checks

Use CPython 3.11. Core and GIS checks run with the locked default groups.

```sh
uv run --locked pytest --ignore=tests/desktop
```

Desktop presentation tests use the optional desktop group. The tested development
pin is PySide6 6.10.2, superseding the earlier unverified 6.11.3 compatibility
candidate for this component. Windows bundle validation remains pending.
Linux requires libegl1 for Qt loading, including offscreen tests.

```sh
QT_QPA_PLATFORM=offscreen uv run --locked --group desktop pytest tests/desktop
```

On PowerShell set `$env:QT_QPA_PLATFORM="offscreen"` before the same uv command.
