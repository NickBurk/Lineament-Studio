# AI Agent Development Instructions

## Обязательные источники
Перед каждой задачей прочитать:
1. Корневой `AGENTS.md`.
2. `README_MASTER.md` и профильную спецификацию.
3. `DECISION_REGISTER.md`, `OPEN_QUESTIONS.md` и связанные ADR.
4. `docs/SKILL_ROUTING.md`.
5. Только необходимые `.agents/skills/<skill-name>/SKILL.md`.
6. Существующие модули, тесты и Git diff.

## До изменения кода
Текущий репозиторий — clean start. Не обращаться к `linia-app`, не клонировать его, не читать его ветки/коммиты и не переносить оттуда код, тесты, конфигурации или сборки. Не выполнять legacy audit. Использовать только текущий репозиторий и Master Specification.

Проверить реальное дерево репозитория, текущую ветку, `git status`, базовый commit,
точки входа, зависимости и тесты. Описывать существующую архитектуру только по фактам.
Не создавать вторую реализацию функции.

## Маршрутизация ролей
- Новая крупная функция: Requirements Engineer → Software Architect → профильный Developer/Expert → QA → Code Reviewer.
- Архитектурное изменение: Software Architect; Requirements/Code Reviewer по необходимости.
- DEM алгоритм: GIS Geospatial + Scientific Computing + QA; Domain Expert при интерпретации.
- Геологическая интерпретация: Geomorphology & Structural Geology Expert + Requirements; Scientific Computing по необходимости.
- `.lspx`, импорт/экспорт, хранение: Data Architecture + Requirements + QA.
- Python/PySide6: Python Desktop Developer + UI/UX при изменении интерфейса + QA.
- Исправление дефекта: Python Desktop Developer + профильный эксперт + QA.
- Перед merge: независимый Code Reviewer; QA для тестовых доказательств.
- Перед выпуском: QA → Code Reviewer → Release Engineer → clean Windows verification.

Не запускать все 11 ролей на каждую задачу. Выбирать минимальный набор, покрывающий изменяемые слои и риски.

## Порядок выполнения
1. Requirements — атомарные FR/NFR, scope, Out of Scope, GWT.
2. Architect — границы модулей, контракты, зависимости, ADR при необходимости.
3. Specialist — реализация в назначенных каталогах.
4. QA — независимые тесты и evidence.
5. Code Review — diff, security, compatibility, data integrity, scientific/geospatial correctness.
6. Release Engineer — только для сборки/поставки.

## Запрещено
- подменять алгоритм заглушкой или возвращать фиктивные результаты;
- показывать фиктивный progress;
- скрывать исключения;
- менять чужие API без согласования;
- удалять тесты ради прохождения CI;
- менять научную формулу без источника/обоснования и ADR;
- считать предложение утверждённым;
- переписывать существующий код без сравнения с baseline;
- включать сетевые/API зависимости в обязательный pipeline;
- заявлять тест passed, если он не запускался.

## Обязательный результат
Код; тесты; документация; список изменённых файлов; точные команды проверки и фактические результаты;
ограничения; известные дефекты; незавершённые задачи; branch/commit reference.

## Definition of Done
Функция реально работает, имеет тесты и проходит интеграцию. UI-кнопка без backend не считается
завершением. P0/P1 review findings закрыты или явно приняты с ограничениями.

## Multi-agent
Каждому агенту назначаются владелец каталога, scope, запретные зоны, входные/выходные контракты,
тесты и acceptance criteria. Общие API меняет интеграционный агент после согласования.
