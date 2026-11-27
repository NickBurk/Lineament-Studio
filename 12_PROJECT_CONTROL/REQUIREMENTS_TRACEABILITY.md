# Requirements Traceability Matrix

Матрица связывает требование, спецификацию, модуль и приёмочный тест.
Implementation/test evidence заполняются только по фактическим результатам.
`SPECIFIED` не означает `IMPLEMENTED`.

| Requirement ID | Спецификация | Модуль | Приоритет | Приёмочный тест |
|---|---|---|---:|---|
| PROJ-001 | PROJECT_STORAGE | project | P0 | create/save/reopen E2E |
| PROJ-002 | PROJECT_STORAGE | project | P0 | create/save/reopen E2E |
| PROJ-003 | PROJECT_STORAGE | source resolver | P0 | reference/copy/missing/relink |
| PROJ-004 | PROJECT_STORAGE | source resolver | P0 | reference/copy/missing/relink |
| PROJ-008 | PROJECT_STORAGE | source resolver | P0 | reference/copy/missing/relink |
| PROJ-005 | DATA_MODEL | catalog.jobs/events | P1 | журнал эксперимента и событий, сохранение связей |
| PROJ-006 | METADATA_SCHEMA | project manifest | P0 | Project manifest schema |
| PROJ-007 | METADATA_SCHEMA | project manifest | P1 | Project schema migration |
| DATA-001 | DEM_PROCESSING | data.raster/preflight | P0 | raster fixture matrix |
| DATA-002 | DEM_PROCESSING | data.raster/preflight | P0 | raster fixture matrix |
| DATA-008 | DEM_PROCESSING | data.raster/preflight | P0 | raster fixture matrix |
| DATA-009 | DEM_PROCESSING | data.raster/preflight | P0 | raster fixture matrix |
| DATA-003 | INPUT_OUTPUT_FORMATS | data.adapters | P1 | Raster import integration |
| DATA-004 | INPUT_OUTPUT_FORMATS | data.adapters | P1 | Vector import integration |
| DATA-006 | INPUT_OUTPUT_FORMATS | data.adapters | P0 | CRS regression with source unchanged |
| DATA-005 | OSM_INTEGRATION | integrations.osm | P1 | local/online provenance |
| OSM-001 | OSM_INTEGRATION | integrations.osm | P1 | local/online provenance |
| DATA-007 | PERFORMANCE_REQUIREMENTS | data.windowed | P0 | large-raster benchmark |
| PRE-001 | DEM_PROCESSING | preprocessing | P0 | analytic surface fixtures |
| PRE-002 | DEM_PROCESSING | preprocessing | P1 | analytic surface fixtures |
| PRE-003 | DEM_PROCESSING | preprocessing | P1 | analytic surface fixtures |
| DET-001 | DETECTION_ENGINE | detection.canny/log | P0 | synthetic edge/step/impulse |
| DET-002 | DETECTION_ENGINE | detection.canny/log | P0 | synthetic edge/step/impulse |
| DET-003 | DETECTION_ENGINE | detection.lsd/edlines/hough | P1 | synthetic line fixtures |
| DET-004 | DETECTION_ENGINE | detection.lsd/edlines/hough | P1 | synthetic line fixtures |
| DET-005 | DETECTION_ENGINE | detection.lsd/edlines/hough | P1 | synthetic line fixtures |
| DET-006 | CORE_ARCHITECTURE | algorithm registry | P2 | adapter version/parameter contract |
| POST-001 | DETECTION_ENGINE | postprocessing | P0 | geometry/merge regression |
| POST-002 | DETECTION_ENGINE | postprocessing | P0 | geometry/merge regression |
| POST-003 | DETECTION_ENGINE | postprocessing | P0 | geometry/merge regression |
| ENS-001 | ENSEMBLE_ANALYSIS | ensemble | P0 | single/matching tests |
| ENS-002 | ENSEMBLE_ANALYSIS | ensemble | P0 | single/matching tests |
| MSC-001 | MULTISCALE_ANALYSIS | multiscale | P0 | resolution/matching tests |
| LSM-001 | LSM_SPECIFICATION | support | P0 | range/NoData/ablation |
| LSM-002 | LSM_SPECIFICATION | support | P1 | range/NoData/ablation |
| STR-001 | STRUCTURAL_ANALYSIS | structural | P0 | geometry/circular/density tests |
| STR-002 | STRUCTURAL_ANALYSIS | structural | P1 | geometry/circular/density tests |
| STR-003 | STRUCTURAL_ANALYSIS | structural | P1 | geometry/circular/density tests |
| STR-004 | STRUCTURAL_ANALYSIS | structural | P1 | geometry/circular/density tests |
| RANK-001 | RANKING_SYSTEM | ranking | P0 | profile/geological separation |
| RANK-002 | RANKING_SYSTEM | ranking | P1 | profile/geological separation |
| RANK-003 | RANKING_SYSTEM | ranking | P1 | profile/geological separation |
| REV-001 | INDEPENDENT_ANNOTATION | review | P1 | independent import/compare/consensus |
| REV-002 | INDEPENDENT_ANNOTATION | review | P1 | independent import/compare/consensus |
| REV-003 | INDEPENDENT_ANNOTATION | review | P1 | independent import/compare/consensus |
| REV-004 | INDEPENDENT_ANNOTATION | review | P1 | independent import/compare/consensus |
| REV-005 | INDEPENDENT_ANNOTATION | review | P1 | independent import/compare/consensus |
| REV-006 | INDEPENDENT_ANNOTATION | review | P1 | independent import/compare/consensus |
| DS-001 | DATASET_BUILDER | datasets | P1 | chips/spatial split/provenance |
| DS-002 | DATASET_BUILDER | datasets | P1 | chips/spatial split/provenance |
| DS-003 | DATASET_BUILDER | datasets | P1 | chips/spatial split/provenance |
| ML-001 | ML_ENGINE | ml | P1 | train/evaluate/version |
| ML-002 | ML_ENGINE | ml | P1 | train/evaluate/version |
| UI-001 | UI_UX_SPECIFICATION | desktop.ui | P0 | GUI state/accessibility |
| UI-002 | UI_UX_SPECIFICATION | desktop.ui | P1 | GUI state/accessibility |
| UI-003 | UI_UX_SPECIFICATION | desktop.ui | P1 | GUI state/accessibility |
| UI-004 | UI_UX_SPECIFICATION | desktop.ui | P0 | GUI state/accessibility |
| BAT-001 | FUNCTIONAL_REQUIREMENTS | workflow.batch | P1 | batch integration |
| QGIS-001 | QGIS_PLUGIN | qgis_adapter | P1 | clean QGIS execution |
| GEE-001 | GEE_INTEGRATION | integrations.gee | P2 | optional adapter test |
| EXP-001 | INPUT_OUTPUT_FORMATS | export/report | P0 | Export round-trip |
| REP-001 | FUNCTIONAL_REQUIREMENTS | reports | P1 | Report fixture |
| NFR-REL-001 | NON_FUNCTIONAL_REQUIREMENTS | jobs/worker | — | crash isolation, cancel/restart |
| NFR-REL-002 | NON_FUNCTIONAL_REQUIREMENTS | jobs/worker | — | crash isolation, cancel/restart |
| NFR-DATA-001 | PROJECT_STORAGE | storage/catalog | — | write recovery, traversal rejection |
| NFR-DATA-002 | PROJECT_STORAGE | storage/catalog | — | write recovery, traversal rejection |
| NFR-PERF-001 | PERFORMANCE_REQUIREMENTS | resources/desktop | — | 1k–20k, RAM, event-loop latency |
| NFR-PERF-002 | PERFORMANCE_REQUIREMENTS | resources/desktop | — | 1k–20k, RAM, event-loop latency |
| NFR-PERF-003 | PERFORMANCE_REQUIREMENTS | resources/desktop | — | 1k–20k, RAM, event-loop latency |
| NFR-REPRO-001 | METADATA_SCHEMA / SCIENTIFIC_VALIDATION | provenance | — | manifest completeness, repeatability |
| NFR-REPRO-002 | METADATA_SCHEMA / SCIENTIFIC_VALIDATION | provenance | — | manifest completeness, repeatability |
| NFR-COMP-001 | CORE_ARCHITECTURE / API_CONTRACTS | contracts/worker | — | запрет GUI imports, IPC compatibility |
| NFR-COMP-002 | CORE_ARCHITECTURE / API_CONTRACTS | contracts/worker | — | запрет GUI imports, IPC compatibility |
| NFR-UX-001 | UI_UX_SPECIFICATION | desktop | — | error states, keyboard/focus inspection |
| NFR-UX-002 | UI_UX_SPECIFICATION | desktop | — | error states, keyboard/focus inspection |
| NFR-OFF-001 | MASTER_TZ / NON_FUNCTIONAL_REQUIREMENTS | core/adapters | — | network-disabled E2E |
| NFR-SEC-001 | NON_FUNCTIONAL_REQUIREMENTS | contracts/storage | — | secret scan, malformed manifest/archive fixtures |
| NFR-SEC-002 | NON_FUNCTIONAL_REQUIREMENTS | contracts/storage | — | secret scan, malformed manifest/archive fixtures |

`—` в колонке приоритета NFR означает, что нормативный каталог не присваивает priority.
[OQ-33](OPEN_QUESTIONS.md)

`AC-REL-001` — сценарий приёмки bundle из [Acceptance Criteria](../01_REQUIREMENTS/ACCEPTANCE_CRITERIA.md)
и [Release Requirements](../10_DELIVERY/RELEASE_REQUIREMENTS.md). Отдельный нормативный ID
`BUILD-001` в каталоге требований отсутствует. Вопрос регистрации релизных требований — OQ-33.

FR priorities come from the [functional requirements catalogue](../01_REQUIREMENTS/FUNCTIONAL_REQUIREMENTS.md).
The preprocessing discrepancy remains recorded in ACR-004 and OQ-30.
[Change requests](../docs/parallel/CONTRACT_CHANGE_REQUESTS.md)

## Phase 1 evidence

The acceptance test column above describes full requirement verification. Product-level acceptance
remains pending for requirements whose behavior depends on later phases. The following rows
record the Phase 1 contribution without assigning a product-level VERIFIED status on that basis.
The wheel and contract results are recorded in the [Phase 1 report](../docs/PHASE_1_REPORT.md).

| Requirement | Phase 1 contribution and evidence | Full requirement status |
|---|---|---|
| NFR-COMP-001 | Stdlib-only Core and isolation smoke in Core CI | Core verified on platforms listed in the report |
| NFR-COMP-002 | Preflight, version matrix and job/event round-trips in test_wire_lifecycle and test_worker_exchange | IN_PROGRESS. Desktop and QGIS integration pending |
| NFR-REL-001 | Subprocess early exit detected by replay in test_worker_exchange | IN_PROGRESS. GUI fault-injection pending |
| NFR-REL-002 | Cancel vs. finalization and result visibility in test_wire_lifecycle | IN_PROGRESS. Durable recovery gate remains mandatory |
| NFR-SEC-001 | Fixed public diagnostics and unknown diagnostic field rejection in test_wire_lifecycle | IN_PROGRESS. Logs and product manifests pending |
| NFR-SEC-002 | Bounded strict JSONL framing in test_wire_lifecycle | IN_PROGRESS. Manifest/archive import remains pending |
| NFR-UX-001 | Stable codes with fixed explanations in test_wire_lifecycle | IN_PROGRESS. GUI error states pending |
| DET-006 | Versioned registry and parameter validation in test_domain_application | IN_PROGRESS. Detector adapter implementation pending |
| RANK-001 / RANK-003 | Distinct rank and geological values in test_domain_application | IN_PROGRESS. Calculation and expert assignment pending |
| DATA-002 / DATA-009 | Explicit CRS states and units in test_domain_application | IN_PROGRESS. Dataset preflight and transformations pending |
| PROJ-003 / PROJ-006 / PROJ-008 | Project/source UUID references in test_domain_application | NOT_STARTED at product level. Storage remains in Phase 2 |
| BAT-001 | One-job ordering and new UUID per retry documented in API Contracts | NOT_STARTED at product level. Batch integration remains pending |
| NFR-REPRO-001 | Exact algorithm and result versions in test_wire_lifecycle | IN_PROGRESS. Persistent provenance remains pending |

## Правило завершения
Ни одно требование не считается завершённым, пока не указаны implementation reference, test
reference, status и evidence. Статусы: `NOT_STARTED`, `IN_PROGRESS`, `IMPLEMENTED_UNVERIFIED`,
`VERIFIED`, `BLOCKED`, `DEFERRED`. Изменение требования обновляет матрицу.

## Phase 2–3 vertical slice evidence

| Requirements | Evidence |
|---|---|
| PROJ-001–008, NFR-DATA-001/002 | `tests/data/test_project.py`: process death/reopen, unsupported manifest preservation, traversal denial, source drift and explicit relink, failed recovery, concurrent access, damaged SQLite, staging space failure |
| DATA-001–009, NFR-COMP-001/002 | `tests/gis/test_raster.py` and `tests/gis/test_runtime.py`: actual GeoTIFF, long Unicode path, CRS/NoData and bounded reads, candidate runtime/GeoPackage raster evidence. Standalone Windows bundle evidence pending. |
| PRE-001, NFR-REPRO-001 | `tests/science/test_hillshade.py`: numeric oracles, tile equivalence, affine rotation, edge/mask, dtype and cancellation. `tests/integration/test_vertical_slice.py`: fresh-process reopen and original checksum. |
| NFR-REL-002 and ACR-003 | Process termination tested across eight publication boundaries. Hardware power-loss evidence remains pending. |
