# Engineering Skills Integration

## Источник
Встроен пользовательский `lineament_studio_skills_pack_v1` (Engineering Skills Pack v1.0).
Исходные файлы `SKILL.md`, `AGENTS.md`, `SKILL_ROUTING.md` и четыре шаблона сохранены
без пересказа в исходных путях.

## 11 Skills
1. `software-architect`
2. `requirements-engineer`
3. `python-desktop-developer`
4. `gis-geospatial-engineer`
5. `qa-test-engineer`
6. `ui-ux-designer`
7. `code-reviewer`
8. `release-engineer`
9. `scientific-computing-engineer`
10. `geomorphology-structural-geology-expert`
11. `data-architecture-engineer`

## Пути
- `AGENTS.md` — общие инструкции в корне проекта.
- `.agents/skills/<skill-name>/SKILL.md` — переносимые инструкции ролей.
- `docs/SKILL_ROUTING.md` — выбор Skills по типу задачи.
- `docs/templates/ADR.md` — архитектурные решения.
- `docs/templates/REQUIREMENT.md` — спецификации требований.
- `docs/templates/TEST_REPORT.md` — QA evidence.
- `docs/templates/PHASE_REPORT.md` — отчёт фазы.

## Правила использования
- Skills — инструкции для совместимых coding agents, а не автоматически устанавливаемые
  системные Skills ChatGPT.
- Совместимый агент должен обнаруживать `.agents/skills` и читать `AGENTS.md`.
- В обычном чате нужный Skill прикладывается к конкретному запросу.
- Не вызывать все роли одновременно; маршрутизатор выбирает минимально необходимый набор.
- Skills не заменяют Master TZ, ADR, требования или проверку фактического кода.

## Приоритет источников
1. Последнее явное решение пользователя.
2. Принятый ADR, не противоречащий решению пользователя.
3. Decision Register (`USER_APPROVED` выше `ARCHITECT_SELECTED`).
4. Master TZ и профильные спецификации.
5. `AGENTS.md` и Skills как процессные правила и постоянные ограничения.
6. Конкретная задача агента.

Если обнаружен конфликт — агент не выбирает вариант молча, а фиксирует конфликт и запрашивает решение.
