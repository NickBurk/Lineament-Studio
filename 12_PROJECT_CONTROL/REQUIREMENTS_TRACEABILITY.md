# Requirements Traceability Matrix

Матрица связывает требование, спецификацию, модуль и приёмочный тест.
Implementation/test evidence заполняются только по фактическим результатам.
Статус реализации определяется словарём ниже; проектный приёмочный тест в нормативном каталоге не является evidence.

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
| NFR-COMP-001 | Stdlib-only Core and isolation smoke in Core CI | VERIFIED_IN_SUPPORTED_PROFILE; product packaging remains open |
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
reference, status и evidence. Статусы: `NOT_STARTED` — работы нет; `IN_PROGRESS` — часть требования реализуется или проверена;
`IMPLEMENTED_UNVERIFIED` — заявленная реализация не имеет выполненной проверки;
`VERIFIED_IN_SUPPORTED_PROFILE` — реализованный объём прошёл проверки в документированном
ограниченном development profile, но полное продуктовое требование не принято;
`VERIFIED` — полностью принято всё нормативное требование; `BLOCKED` — продолжение
зависит от открытого решения или внешнего условия; `DEFERRED` — явно перенесено.
Изменение требования обновляет матрицу. Ни одна строка ниже не имеет статуса `VERIFIED`.

## Phase 2–3 vertical slice evidence

Scope: CPython 3.11 candidate dependencies and supported local storage. Implementation
references are repository-root-relative paths; test evidence is listed separately. Test IDs refer to
actual repository files; parametrized tests include all collected cases. Historical
execution evidence: [Push CI 46027699055](https://github.com/NickBurk/Lineament-Studio/actions/runs/46027699055)
and [PR CI 46027707459](https://github.com/NickBurk/Lineament-Studio/actions/runs/46027707459),
each with Ubuntu/Windows JUnit artifacts for HEAD `23599407`. New corrective HEAD
requires fresh CI before its evidence can be claimed. The CI run does not establish
Windows standalone GIS bundle compatibility or product acceptance.

| Requirement ID | Normative priority | Implemented scope | Implementation reference | Exact test ID or command | Evidence reference | Remaining scope | Status |
|---|---|---|---|---|---|---|---|
| PROJ-001 | P0 | Backend create/open/save/close | src/lineament_core/infrastructure/data/project.py | tests/integration/test_vertical_slice.py::test_smoke_reopens_in_fresh_process | Previous Push/PR CI JUnit | Desktop workflow | IN_PROGRESS |
| PROJ-002 | P0 | Fresh process restores source and result | src/lineament_core/infrastructure/data/project.py | tests/integration/test_vertical_slice.py::test_smoke_reopens_in_fresh_process | Previous Push/PR CI JUnit | GUI restart/layer state | VERIFIED_IN_SUPPORTED_PROFILE |
| PROJ-003 | P0 | Reference/Copy backend choice | src/lineament_core/infrastructure/data/project.py | tests/gis/test_raster.py::test_external_dependencies_rejected_for_reference_and_copy | Previous Push/PR CI JUnit | User-facing choice | IN_PROGRESS |
| PROJ-004 | P0 | Missing, drift and confirmed relink backend | src/lineament_core/infrastructure/data/project.py | tests/data/test_project.py::test_missing_drift_and_relink | Previous Push/PR CI JUnit | Desktop Locate/Relink | IN_PROGRESS |
| PROJ-005 | P1 | Publication/relink receipts and job IDs | src/lineament_core/infrastructure/data/project.py | tests/data/test_result_provenance.py::test_result_process_death | Previous Push/PR CI JUnit | Experiment/event journal | IN_PROGRESS |
| PROJ-006 | P0 | Versioned UTF-8 .lspx and catalog witness | src/lineament_core/infrastructure/data/manifest.py; src/lineament_core/infrastructure/data/project.py | tests/data/test_project.py::test_unsupported_manifest_is_preserved | Previous Push/PR CI JUnit | Product format interoperability | VERIFIED_IN_SUPPORTED_PROFILE |
| PROJ-007 | P1 | Reject unsupported versions without mutation | src/lineament_core/infrastructure/data/manifest.py; src/lineament_core/infrastructure/data/project.py | tests/data/test_result_provenance.py::test_legacy_manifest_is_rejected_without_rewrite | Previous Push/PR CI JUnit | Migration and rollback | IN_PROGRESS |
| PROJ-008 | P0 | Missing/drift/sidecar detection | src/lineament_core/infrastructure/data/project.py; src/lineament_core/infrastructure/gis/raster.py | tests/data/test_project.py::test_missing_drift_and_relink | Previous Push/PR CI JUnit | GUI error surface | VERIFIED_IN_SUPPORTED_PROFILE |
| DATA-001 | P0 | Self-contained GeoTIFF DEM import | src/lineament_core/infrastructure/data/project.py; src/lineament_core/infrastructure/gis/raster.py | tests/integration/test_vertical_slice.py::test_smoke_reopens_in_fresh_process | Previous Push/PR CI JUnit | Other reader profiles | VERIFIED_IN_SUPPORTED_PROFILE |
| DATA-002 | P0 | Preflight grid, units, NoData, statistics | src/lineament_core/infrastructure/gis/raster.py | tests/gis/test_raster.py::test_preflight | Previous Push/PR CI JUnit | More CRS/unit profiles | VERIFIED_IN_SUPPORTED_PROFILE |
| DATA-003 | P1 | No geology raster importer | — | — | — | Full geologic raster import | NOT_STARTED |
| DATA-004 | P1 | GeoPackage driver smoke | — (production vector import adapter not implemented) | tests/gis/test_runtime.py::test_vector_geopackage_with_same_gdal | Previous Push/PR CI JUnit | Geology vector project import | IN_PROGRESS |
| DATA-005 | P1 | No OSM import | — | — | — | Local and online OSM import | NOT_STARTED |
| DATA-006 | P0 | Hillshade keeps CRS; candidate coordinate transform verified only in runtime tests | src/lineament_core/science/hillshade.py | tests/gis/test_runtime.py::test_offline_runtime_inventory_and_geopackage | Previous Push/PR CI JUnit | Explicit product reprojection/grid cases | IN_PROGRESS |
| DATA-007 | P0 | Bounded window and halo processing | src/lineament_core/science/hillshade.py | tests/science/test_hillshade.py::test_analytic_oracle_and_tile_equivalence | Previous Push/PR CI JUnit | 20k × 20k performance/peak RAM | IN_PROGRESS |
| DATA-008 | P0 | Band, dtype, transform, mask and nonfinite checks | src/lineament_core/infrastructure/gis/raster.py | tests/gis/test_raster.py::test_preflight | Previous Push/PR CI JUnit | Additional driver profiles | VERIFIED_IN_SUPPORTED_PROFILE |
| DATA-009 | P0 | Absent/unknown/angular CRS classification | src/lineament_core/infrastructure/gis/raster.py | tests/gis/test_raster.py::test_crs_classification | Previous Push/PR CI JUnit | Additional CRS profiles | VERIFIED_IN_SUPPORTED_PROFILE |
| PRE-001 | P0 | Calibrated Horn Hillshade 2.0.0 | src/lineament_core/science/hillshade.py | tests/science/test_hillshade.py::test_analytic_oracle_and_tile_equivalence | Previous Push/PR CI JUnit | Terrain/cross-engine validation | VERIFIED_IN_SUPPORTED_PROFILE |
| PRE-002 | P1 | No multidirectional implementation | — | — | — | Method and OQ-30 decision | NOT_STARTED |
| PRE-003 | P1 | No slope/curvature/TPI/LRM | — | — | — | Four algorithms and OQ-30 | NOT_STARTED |
| NFR-REL-002 | — | Prior result survives crash/cancel in local profile | src/lineament_core/infrastructure/data/project.py | tests/data/test_result_provenance.py::test_result_process_death | Previous Push/PR CI JUnit | Worker/bundle tests | VERIFIED_IN_SUPPORTED_PROFILE |
| NFR-DATA-001 | — | Local manifest/catalog recovery | src/lineament_core/infrastructure/data/project.py | tests/data/test_project.py::test_process_death_and_repeated_reopen | Previous Push/PR CI JUnit | Power-loss durability | VERIFIED_IN_SUPPORTED_PROFILE |
| NFR-DATA-002 | — | Contained Copy paths and link denial | src/lineament_core/infrastructure/data/manifest.py | tests/data/test_project.py::test_unsafe_internal_paths | Previous Push/PR CI JUnit | Other filesystem profiles | VERIFIED_IN_SUPPORTED_PROFILE |
| NFR-PERF-001 | — | Memory admission checks | src/lineament_core/infrastructure/gis/raster.py | tests/gis/test_raster.py::test_preflight | Previous Push/PR CI JUnit | Peak RAM on target laptop | IN_PROGRESS |
| NFR-PERF-002 | — | Bounded tiled Hillshade | src/lineament_core/science/hillshade.py | tests/science/test_hillshade.py::test_analytic_oracle_and_tile_equivalence | Previous Push/PR CI JUnit | Target large-raster benchmark | IN_PROGRESS |
| NFR-REPRO-001 | — | Canonical Hillshade provenance and source versions | src/lineament_core/infrastructure/data/provenance.py; src/lineament_core/infrastructure/data/project.py | tests/data/test_result_provenance.py::test_strict_provenance | Previous Push/PR CI JUnit | Other algorithms/export | VERIFIED_IN_SUPPORTED_PROFILE |
| NFR-REPRO-002 | — | Synthetic numerical/tile equivalence | src/lineament_core/science/hillshade.py | tests/science/test_hillshade.py::test_physical_scaled_integer_matches_float | Previous Push/PR CI JUnit | Field/cross-engine comparison | VERIFIED_IN_SUPPORTED_PROFILE |
| NFR-COMP-001 | — | Core wheel isolation | src/lineament_core | uv run --locked python scripts/check_wheel.py | Previous Push/PR CI wheel step | Standalone Windows delivery | VERIFIED_IN_SUPPORTED_PROFILE |
| NFR-COMP-002 | — | Versioned JSONL Core contract | src/lineament_core | tests/test_worker_exchange.py::test_subprocess_version_preflight_and_completed_exchange | Previous Push/PR CI JUnit | Desktop/QGIS integration | IN_PROGRESS |
| NFR-OFF-001 | — | Local processing; offline candidate control transform is test evidence | src/lineament_core/infrastructure/data/project.py | tests/gis/test_runtime.py::test_offline_runtime_inventory_and_geopackage | Previous Push/PR CI JUnit | Network-disabled product E2E | IN_PROGRESS |
| NFR-SEC-001 | — | Explicit provenance fields | src/lineament_core/infrastructure/data/provenance.py | tests/data/test_result_provenance.py::test_strict_provenance | Previous Push/PR CI JUnit | Full manifest/log secret scan | IN_PROGRESS |
| NFR-SEC-002 | — | Reject unsupported manifests/sidecars | src/lineament_core/infrastructure/data/manifest.py; src/lineament_core/infrastructure/gis/raster.py | tests/data/test_project.py::test_unsupported_manifest_is_preserved | Previous Push/PR CI JUnit | Archive import validation | IN_PROGRESS |

## Hardening contribution (product statuses unchanged)

- NFR-REPRO-001: `src/lineament_core/infrastructure/data/provenance.py` historical allowlist;
  `tests/data/test_result_provenance.py::test_real_historical_project_survives_executable_upgrade`.
- NFR-REL-002: internal cancellation and observers in
  `src/lineament_core/infrastructure/execution.py` and `infrastructure/data/project.py`;
  `tests/data/test_result_provenance.py::test_cancellation_publication_boundary`,
  `test_callback_failure_does_not_change_publication`; production Worker remains future scope.
- NFR-REPRO-002 / PRE-001: `src/lineament_core/science/hillshade.py` offset-free derivatives;
  `tests/science/test_offset_stability.py::test_large_offset_preserves_plane_gradient`.

Exact-head CI evidence is attached to the hardening PR. These contributions do not
promote any full normative requirement to VERIFIED or authorize new algorithms.
