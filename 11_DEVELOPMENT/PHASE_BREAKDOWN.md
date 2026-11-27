# Phase Breakdown

Для каждой фазы обязательны: цель, scope, зависимости, Requirement IDs, Skills, выходные артефакты,
изменяемые каталоги, API contract, тесты, acceptance criteria Given/When/Then, риски и отчёт.

- **Phase 0 — Repository Bootstrap & Architecture Baseline:** чистая инициализация репозитория, интеграция Master Specification и Skills, проверка Codex discovery, минимальная структура, инструменты разработки и фиксация открытых ADR. Старый `linia-app` не исследуется и не используется.
- **Phase 1 — Core Contracts:** domain models, error model, JSON/JSONL job protocol, registry, versioning.
- **Phase 2 — Data Engine:** raster/vector IO, CRS, NoData, `.lspx`, SQLite catalog, source Reference/Copy.
- **Phase 3 — Preprocessing:** Hillshade, slope, curvature/TPI/LRM по приоритетам, tiled processing.
- **Phase 4 — Detection:** Canny, LoG, LSD, EDLines, Hough, preview, validation.
- **Phase 5 — Postprocessing:** filtering, geometry cleanup, merge, deduplication, vectorization.
- **Phase 6 — Ensemble & Multi-scale:** orchestration, matching, provenance, stability/persistence.
- **Phase 7 — LSM:** component maps, normalization, weighted aggregation, disagreement, tests.
- **Phase 8 — Structural:** orientation, density, nodes, geometric ranking, user profiles.
- **Phase 9 — Desktop:** main window, map canvas prototype, task manager, project workflows.
- **Phase 10 — Review:** independent annotations, geometry versions, comparison, consensus.
- **Phase 11 — Dataset & ML:** chips, masks, spatial split, manifests, classical ML.
- **Phase 12 — Smart:** Tuning, Labeling, QA using registered operations.
- **Phase 13 — Integrations:** OSM, QGIS plugin/worker, GEE adapter.
- **Phase 14 — Release:** reports, performance, regression, packaging, documentation.

Фазы можно объединять в один запрос агенту только после согласования контрактов и тестовых границ.
