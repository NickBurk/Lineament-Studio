# Lineament Studio — Engineering Skills Pack

Версия 1.0. Набор из 11 специализированных Agent Skills для разработки Lineament Studio, общие правила репозитория, маршрутизатор ролей и шаблоны инженерной документации.

## Skills
1. `software-architect` — архитектура, границы модулей, интерфейсы и ADR.
2. `requirements-engineer` — требования, спецификации и критерии приёмки.
3. `python-desktop-developer` — Python 3.11, PySide6 и desktop-разработка.
4. `gis-geospatial-engineer` — GDAL, Rasterio, GeoTIFF, DEM и геоданные.
5. `qa-test-engineer` — тестовая стратегия, регрессии и приёмка.
6. `ui-ux-designer` — сценарии использования и интерфейс PySide6.
7. `code-reviewer` — независимый аудит изменений.
8. `release-engineer` — Windows-сборка, runtime и выпуск.
9. `scientific-computing-engineer` — численные методы и воспроизводимые вычисления.
10. `geomorphology-structural-geology-expert` — геоморфология и структурно-геологическая интерпретация.
11. `data-architecture-engineer` — `.lspx`, хранение, миграции и экспертные датасеты.

## Установка
Распакуйте архив в корень репозитория. Сохраните структуру `.agents/skills/<skill-name>/SKILL.md` и разместите `AGENTS.md` в корне.

Путь `.agents/skills/` используется Codex и рядом инструментов, поддерживающих Agent Skills. Проверьте правила обнаружения Skills в конкретном агенте.

## Использование в ChatGPT
Файлы `SKILL.md` — переносимые инструкции, а не встроенные системные Skills ChatGPT и не устанавливаются автоматически в аккаунт. В обычном чате прикрепите нужный файл или вставьте его содержимое в контекст задачи. В ChatGPT Work используйте файлы как материалы проекта, если они доступны в рабочем пространстве.

## Маршрутизация
- Новая функция: Requirements + Architect + профильный Developer/Expert + QA.
- Алгоритм DEM: GIS + Scientific Computing + QA; Domain Expert — если затрагивается интерпретация.
- `.lspx`, импорт/экспорт, датасеты: Data Architecture + Requirements + QA.
- UI: UI/UX + Python Developer + QA.
- Перед merge: Code Reviewer.
- Перед выпуском: QA + Code Reviewer + Release Engineer.

Не запускайте все 11 ролей на каждую задачу. Подключайте только необходимые компетенции.
