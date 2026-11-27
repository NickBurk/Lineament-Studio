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

Evidence is scoped to CPython 3.11 with the candidate dependency group and supported local storage. Priorities remain those in the normative catalog above. GUI and standalone-release checks have their own gates.

| ID | Priority | Implemented scope | Test ID or command | Remaining scope | Status |
|---|---|---|---|---|---|
| PROJ-001 | P0 | Backend create/open/save/close, locked catalog | `test_missing_drift_and_relink`, `test_smoke_reopens_in_fresh_process` | Desktop workflow | PARTIAL |
| PROJ-002 | P0 | Fresh interpreter restores sources and published output | `test_smoke_reopens_in_fresh_process`, `test_result_process_death` | GUI restart and layer state E2E | VERIFIED_IN_SUPPORTED_PROFILE |
| PROJ-003 | P0 | Caller selects Reference or verified Copy | `test_smoke_reopens_in_fresh_process`, `test_external_dependencies_rejected_for_reference_and_copy` | User-facing choice | PARTIAL |
| PROJ-004 | P0 | Missing status, explicit relink and confirmation | `test_missing_drift_and_relink`, `test_relink_keeps_historical_provenance` | Desktop Locate/Relink UX | PARTIAL |
| PROJ-005 | P1 | Publication and relink receipts, job UUIDs | `test_result_process_death`, `test_recovery_can_itself_be_interrupted` | Full experiment and event journal | PARTIAL |
| PROJ-006 | P0 | Versioned UTF-8 JSON .lspx, catalog witness | `test_smoke_reopens_in_fresh_process`, `test_unsupported_manifest_is_preserved` | Broader product manifest interoperability | VERIFIED_IN_SUPPORTED_PROFILE |
| PROJ-007 | P1 | Unsupported formats refused without rewrite | `test_unsupported_manifest_is_preserved` | Explicit migrations and upgrade rollback | PARTIAL |
| PROJ-008 | P0 | Missing, drift, sidecar detection, verified source snapshots | `test_missing_drift_and_relink`, `test_source_changes_during_processing_leave_no_intent` | GUI error surface | VERIFIED_IN_SUPPORTED_PROFILE |
| DATA-001 | P0 | Self-contained GeoTIFF DEM import | `test_smoke_reopens_in_fresh_process`, `test_external_dependencies_rejected_for_reference_and_copy` | Other reader profiles | VERIFIED_IN_SUPPORTED_PROFILE |
| DATA-002 | P0 | Preflight grid, units, NoData, physical and raw statistics | `test_preflight`, `test_unsupported_calibration_fails_explicitly`, `test_smoke_reopens_in_fresh_process` | More CRS/vertical unit profiles | VERIFIED_IN_SUPPORTED_PROFILE |
| DATA-003 | P1 | GeoTIFF is exercised for DEM only | — | Geologic raster project import | NOT_STARTED |
| DATA-004 | P1 | Candidate vector GeoPackage driver smoke | `test_vector_geopackage_with_same_gdal` | Vector geology project import | PARTIAL |
| DATA-005 | P1 | — | — | OSM local and online import | NOT_STARTED |
| DATA-006 | P0 | Offline control-coordinate conversion in candidate runtime. Hillshade preserves source CRS | `test_offline_runtime_inventory_and_geopackage`, `test_analytic_oracle_and_tile_equivalence` | Explicit product reprojection and grid-dependent cases | PARTIAL |
| DATA-007 | P0 | Bounded windows and halo | `test_preflight`, `test_physical_scaled_integer_matches_float` | Representative 20k × 20k performance/peak RAM | PARTIAL |
| DATA-008 | P0 | Band, dimensions, dtype, rotated transform, mask and nonfinite inspection | `test_preflight`, `test_damaged_geotiff`, `test_unsupported_calibration_fails_explicitly` | Additional driver profiles | VERIFIED_IN_SUPPORTED_PROFILE |
| DATA-009 | P0 | Report absent, unknown and known angular/linear CRS | `test_preflight`, `test_crs_classification` | Additional exotic CRS profiles | VERIFIED_IN_SUPPORTED_PROFILE |
| PRE-001 | P0 | Single-azimuth calibrated Horn Hillshade v2.0.0 | `test_analytic_oracle_and_tile_equivalence`, `test_physical_scaled_integer_matches_float`, `test_cancellation_and_small_raster` | GDAL/QGIS encoding comparison and representative terrain validation | VERIFIED_IN_SUPPORTED_PROFILE |
| PRE-002 | P1 | — | — | Multidirectional method and OQ-30 priority decision | NOT_STARTED |
| PRE-003 | P1 | — | — | Slope, curvature, TPI and LRM, including OQ-30 priority decision | NOT_STARTED |
| NFR-REL-002 | — | Previous result survives process death, failed recovery and cancellation before PREPARED | `test_result_process_death`, `test_damaged_uncommitted_result_fails_closed`, `test_cancellation_and_small_raster` | Production Worker cancellation and bundle checks | VERIFIED_IN_SUPPORTED_PROFILE |
| NFR-DATA-001 | — | Manifest/catalog recovery on local developer profile | `test_process_death_and_repeated_reopen`, `test_result_process_death`, `test_recovery_can_itself_be_interrupted` | Device power-loss durability | VERIFIED_IN_SUPPORTED_PROFILE |
| NFR-DATA-002 | — | Strict local relative Copy paths, link/reparse denial | `test_unsafe_internal_paths` | Other filesystem profiles | VERIFIED_IN_SUPPORTED_PROFILE |
| NFR-PERF-001 | — | Explicit memory admission checks | `test_preflight` | Peak RAM on target hardware | PARTIAL |
| NFR-PERF-002 | — | Bounded tiled preprocessing | `test_analytic_oracle_and_tile_equivalence` | Target large-raster benchmark | PARTIAL |
| NFR-REPRO-001 | — | Canonical versioned Hillshade provenance and immutable source snapshots | `test_strict_provenance`, `test_relink_keeps_historical_provenance`, `test_source_changes_during_processing_leave_no_intent` | Other algorithms and export | VERIFIED_IN_SUPPORTED_PROFILE |
| NFR-REPRO-002 | — | Numerical tolerance and tile equivalence on calibrated synthetic fixtures | `test_analytic_oracle_and_tile_equivalence`, `test_physical_scaled_integer_matches_float` | Field data and cross-engine comparison | VERIFIED_IN_SUPPORTED_PROFILE |
| NFR-COMP-001 | — | Pure Core wheel imports without GIS, Qt or QGIS | `uv run --locked python scripts/check_wheel.py` | Standalone Windows delivery | VERIFIED_IN_SUPPORTED_PROFILE |
| NFR-COMP-002 | — | Existing Core contract covered by the existing JSONL suite | `tests/test_wire_lifecycle.py`, `tests/test_worker_exchange.py` | Desktop/QGIS interoperability matrix | PARTIAL |
| NFR-OFF-001 | — | Offline candidate coordinate test and local processing | `test_offline_runtime_inventory_and_geopackage`, `test_smoke_reopens_in_fresh_process` | Network-disabled full product E2E | PARTIAL |
| NFR-SEC-001 | — | Generated result provenance uses explicit fields | `test_strict_provenance` | Full manifests and diagnostics secret scan | PARTIAL |
| NFR-SEC-002 | — | Unsupported manifests and external sidecars rejected before publication | `test_unsupported_manifest_is_preserved`, `test_external_dependencies_rejected_for_reference_and_copy` | Archive import | PARTIAL |
