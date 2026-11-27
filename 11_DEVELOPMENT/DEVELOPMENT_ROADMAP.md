# Development Roadmap

## Принцип
Сначала вертикальный рабочий сценарий и стабильное ядро, затем расширение функций. Не строить весь UI до проверки данных и вычислительных контрактов.

## Направления работ по порядку
1. Repository Bootstrap & Architecture Baseline.
2. Core Contracts & Domain Model.
3. Data Engine & Project Storage.
4. DEM Preprocessing.
5. Detection Engine.
6. Postprocessing & Vectorization.
7. Ensemble & Multi-scale.
8. LSM.
9. Structural Analysis & Ranking.
10. Desktop Shell & Map Canvas.
11. Review Studio.
12. Dataset Builder & Classical ML.
13. Smart Workflow.
14. OSM & QGIS Integration.
15. GEE Adapter.
16. Reports & Export.
17. Scientific Validation & Performance.
18. Packaging & Release.

## MVP
Проект, DEM, preprocessing, базовая детекция, постобработка, Single/Ensemble, Multi-scale, LSM_DEM, базовый Structural Analysis, экспорт и стабильное повторное открытие.

## Version 1.0
Полный Review, Independent Annotation, Dataset Builder, пользовательское ранжирование, Smart Workflow, OSM, QGIS, отчёты и упаковка.

## Нумерация
ID фаз 0–14 определяет [Phase Breakdown](PHASE_BREAKDOWN.md). Направления 1–14 выше
соответствуют фазам 0–13. GEE входит в Phase 13. Reports & Export, Scientific Validation &
Performance и Packaging & Release входят в Phase 14. Контрактные и научные проверки
начинаются в фазах соответствующих компонентов.

Состав приёмки P0/MVP и P1/v1.0, включая минимальный Desktop Bundle, уточняется по OQ-30.
[Open Questions](../12_PROJECT_CONTROL/OPEN_QUESTIONS.md)
