# Requirements Traceability Matrix

Матрица связывает требование, спецификацию, модуль и приёмочный тест.
Implementation/test evidence заполняются только по фактическим результатам.
`SPECIFIED` не означает `IMPLEMENTED`.

| Requirement ID | Спецификация | Модуль | Приоритет | Приёмочный тест |
|---|---|---|---:|---|
| PROJ-001/002 | PROJECT_STORAGE | project | P0 | create/save/reopen E2E |
| PROJ-003/004/008 | PROJECT_STORAGE | source resolver | P0 | reference/copy/missing/relink |
| PROJ-006/007 | METADATA_SCHEMA | project manifest | P0/P1 | `.lspx` schema/migration |
| DATA-001/002/008/009 | DEM_PROCESSING | data.raster/preflight | P0 | raster fixture matrix |
| DATA-003/004/006 | INPUT_OUTPUT_FORMATS | data.adapters | P1/P0 | raster/vector CRS tests |
| DATA-005 / OSM-001 | OSM_INTEGRATION | integrations.osm | P1 | local/online provenance |
| DATA-007 / PERF-001 | PERFORMANCE_REQUIREMENTS | data.windowed | P0 | large-raster benchmark |
| PRE-001/002/003 | DEM_PROCESSING | preprocessing | P0/P1 | analytic surface fixtures |
| DET-001/002 | DETECTION_ENGINE | detection.canny/log | P0 | synthetic edge/step/impulse |
| DET-003/004/005 | DETECTION_ENGINE | detection.lsd/edlines/hough | P1 | synthetic line fixtures |
| POST-001/002/003 | DETECTION_ENGINE | postprocessing | P0 | geometry/merge regression |
| ENS-001/002 | ENSEMBLE_ANALYSIS | ensemble | P0 | single/matching tests |
| MSC-001 | MULTISCALE_ANALYSIS | multiscale | P0 | resolution/matching tests |
| LSM-001/002 | LSM_SPECIFICATION | support | P0/P1 | range/NoData/ablation |
| STR-001/002/003/004 | STRUCTURAL_ANALYSIS | structural | P0/P1 | geometry/circular/density tests |
| RANK-001/002/003 | RANKING_SYSTEM | ranking | P0/P1 | profile/geological separation |
| REV-001..006 | INDEPENDENT_ANNOTATION | review | P1 | independent import/compare/consensus |
| DS-001..003 | DATASET_BUILDER | datasets | P1 | chips/spatial split/provenance |
| ML-001/002 | ML_ENGINE | ml | P1 | train/evaluate/version |
| UI-001..004 | UI_UX_SPECIFICATION | desktop.ui | P0/P1 | GUI state/accessibility |
| BAT-001 | FUNCTIONAL_REQUIREMENTS | workflow.batch | P1 | batch integration |
| QGIS-001 | QGIS_PLUGIN | qgis_adapter | P1 | clean QGIS execution |
| GEE-001 | GEE_INTEGRATION | integrations.gee | P2 | optional adapter test |
| EXP-001 / REP-001 | INPUT_OUTPUT_FORMATS | export/report | P0/P1 | round-trip/report fixture |
| NFR-REL/DATA/SEC | NON_FUNCTIONAL_REQUIREMENTS | system | P0 | fault/security tests |
| NFR-PERF | PERFORMANCE_REQUIREMENTS | resources | P0 | 1k–20k benchmark |
| NFR-REPRO | METADATA_SCHEMA | provenance | P0 | manifest/repeatability |
| BUILD-001 | RELEASE_REQUIREMENTS | packaging | P0 | clean Windows install |

## Правило завершения
Ни одно требование не считается завершённым, пока не указаны implementation reference, test
reference, status и evidence. Статусы: `NOT_STARTED`, `IN_PROGRESS`, `IMPLEMENTED_UNVERIFIED`,
`VERIFIED`, `BLOCKED`, `DEFERRED`. Изменение требования обновляет матрицу.
