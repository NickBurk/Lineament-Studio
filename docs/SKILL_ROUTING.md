# Skill Routing — Lineament Studio

| Тип задачи | Обязательные Skills | Дополнительные по ситуации |
|---|---|---|
| Новая крупная функция | Requirements Engineer, Software Architect | GIS, Data Architecture, Domain Expert |
| Архитектурное изменение | Software Architect | Requirements, Code Reviewer |
| Python/PySide6 | Python Desktop Developer | UI/UX, QA |
| Алгоритм DEM | GIS, Scientific Computing | Domain Expert, QA |
| Геологическая интерпретация | Geomorphology & Structural Geology Expert | Scientific Computing, Requirements |
| `.lspx`, импорт/экспорт | Data Architecture, Requirements | Python Developer, QA |
| Экспертные датасеты | Data Architecture, Requirements, Domain Expert | QA |
| Редизайн UI | UI/UX, Python Desktop Developer | QA |
| Исправление дефекта | Python Desktop Developer | профильный эксперт, QA |
| Аудит перед merge | Code Reviewer | QA, Architect |
| Windows EXE / релиз | Release Engineer, QA | Python Developer, GIS |

## Рекомендуемые цепочки
- Новая функция: Requirements → Architect → профильный Developer/Expert → QA → Code Review.
- Научный алгоритм: Requirements → Scientific Computing + GIS → Domain Expert (если нужна интерпретация) → Developer → QA → Review.
- Формат проекта: Requirements → Data Architect → Architect → Developer → Migration/Regression QA → Review.
- Выпуск: QA → Code Review → Release Engineer → проверка на чистой Windows → release report.

Не запускай все роли одновременно. Выбирай минимальный набор, покрывающий изменяемые слои и риски.
