# Lineament Studio

**Исследовательское desktop-приложение для анализа DEM и линейных форм рельефа.**

Lineament Studio предназначен для обнаружения и анализа кандидатов на линейные геоморфологические
и потенциальные структурно-тектонические элементы, экспертной проверки, подготовки датасетов
и воспроизводимых научных экспериментов.

> Обнаруженная линия — кандидат для дальнейшей интерпретации, а не автоматически доказанный разлом.

## Project status

Новый репозиторий. Разработка начинается с нуля. Исходный код и Git history старого `linia-app`
не переносятся и не используются.

Текущая версия репозитория — документационная и архитектурная базовая линия. Наличие спецификаций
не означает, что функции уже реализованы.

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

## First milestone

**Phase 0 — Repository Bootstrap & Architecture Baseline.**

Prepare the repository, verify Codex instructions and Skills discovery, establish the minimal
developer workflow, and resolve architecture decisions before implementing application features.

Материалы Phase 0 включают [отчёт аудита](docs/REPOSITORY_BOOTSTRAP_REPORT.md),
[предлагаемую структуру](docs/REPOSITORY_STRUCTURE.md) и
[план Core Contracts](docs/PHASE_1_CORE_CONTRACTS_PLAN.md).
