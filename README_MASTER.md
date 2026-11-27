# Lineament Studio — Master Specification

**Версия:** 0.2.1 | **Дата:** 2026-11-27 | **Статус:** Integrated engineering baseline

## Назначение
Единая система требований, архитектуры, алгоритмов, данных, интерфейса, научной валидации,
тестирования, поставки и управления ИИ-агентами Lineament Studio.

## Изменения v0.2.1
- Зафиксирован clean start: новый GitHub-репозиторий `Lineament-Studio` без переноса кода и истории `linia-app`.
- Phase 0 заменена с legacy Repository Audit на Repository Bootstrap & Architecture Baseline.
- Удалён устаревший документ `LEGACY_BASELINE.md`, добавлен `NEW_REPOSITORY_BASELINE.md`.
- Уточнены правила Codex, Git workflow и открытые вопросы для нового репозитория.

## Изменения v0.2.0
- Встроен исходный Engineering Skills Pack v1.0: 11 Skills, `AGENTS.md`, маршрутизатор и 4 шаблона.
- Устранено противоречие формата проекта: главный файл проекта — `project.lspx`.
- Зафиксирована модель: папка проекта + JSON manifest `.lspx` + SQLite catalog + GeoPackage/GeoTIFF.
- Усилены DEM Preflight, CRS, affine transform, NoData, NaN/Inf, единицы и обработка больших растров.
- Добавлены Requirements Engineering, Given/When/Then, независимое Code Review и QA evidence.
- Усилены научная и геоморфологическая валидация, UX states, accessibility и release gates.

## Статусы решений
- `USER_APPROVED` — явно подтверждено заказчиком.
- `ARCHITECT_SELECTED` — технический выбор в рамках делегированного полномочия.
- `PROPOSED` — предложение, не обязательное требование.
- `OPEN` — требует проверки или решения.
- `DEFERRED` — отложено.
- `REJECTED` — исключено.

`ARCHITECT_SELECTED` нельзя представлять как ранее высказанное предпочтение заказчика.
При конфликте агент фиксирует противоречие и запрашивает решение.

## Порядок чтения
1. `AGENTS.md` — общие правила для coding agent.
2. `README_MASTER.md` и `MASTER_TZ.md` — продукт и нормативная база.
3. `DECISION_REGISTER.md`, `OPEN_QUESTIONS.md` и связанные ADR.
4. `docs/SKILL_ROUTING.md` — выбор компетенций.
5. Соответствующие `.agents/skills/<skill>/SKILL.md`.
6. Профильная спецификация и шаблоны.
7. `REQUIREMENTS_TRACEABILITY.md` — тесты и evidence.

## Структура
- `00_PROJECT` — видение, scope, словарь.
- `01_REQUIREMENTS` — функциональные/нефункциональные требования и приёмка.
- `02_ARCHITECTURE` — система, ядро, Desktop, QGIS, API.
- `03_ALGORITHMS` — DEM, детекторы, ансамбль, LSM, структурный анализ.
- `04_DATA` — модель данных, `.lspx`, форматы и метаданные.
- `05_INTERFACE` — UX, дизайн-система, рабочие пространства.
- `06_EXPERT_REVIEW` — экспертная проверка и датасеты.
- `07_AI_ML` — Smart Workflow, ML и локальная работа.
- `08_INTEGRATIONS` — QGIS, OSM, GEE.
- `09_SCIENCE_AND_QA` — научная валидация, тесты, производительность.
- `10_DELIVERY` — Windows Bundle, лицензирование, релиз.
- `11_DEVELOPMENT` — roadmap, Skills, агентный процесс, Git.
- `12_PROJECT_CONTROL` — решения, вопросы, риски, трассировка.
- `.agents/skills` — исходные инструкции 11 ролей.
- `docs/SKILL_ROUTING.md`, `docs/templates` — маршрутизация и шаблоны.
- `docs/architecture/adr` — Architecture Decision Records.

## Использование Skills
Skills — переносимые файлы-инструкции для совместимых coding agents. Их наличие в архиве не
означает автоматическую установку в аккаунт ChatGPT. Совместимый агент должен обнаруживать
`.agents/skills/<skill-name>/SKILL.md` и читать корневой `AGENTS.md`. В обычном чате
соответствующий Skill нужно предоставить в контекст задачи.

## Управление изменениями
Каждое изменение требований/архитектуры имеет ID, автора, дату, причину, затронутые документы,
миграции и тесты. Decision Register, ADR и Traceability Matrix обновляются. Исторические
эксперименты и экспертные наборы не перезаписываются молча.

## Граница версии
v0.2.1 описывает целевую документационную и инженерную базу нового репозитория. Реализация,
проверки формата нового проекта и результаты тестов фиксируются по фазам разработки.
Импорт пользовательских проектов из других форматов регулирует OQ-17.
