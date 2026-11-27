# Data Model

## Принципы
- `project.lspx` — главный project manifest.
- Для restricted Phase 2–3 profile Manifest — источник деклараций и версий источников;
  SQLite — проекция каталога источников и источник результатов, publication intents и receipts.
  Project Storage — единственный владелец записи (DEC-A33). Event/job tables — будущая модель.
- GeoPackage — внутренние пространственные векторы.
- GeoTIFF/COG — большие растры и производные.
- JSON — manifests экспериментов и версионируемые конфигурации.
- У каждой сущности стабильный UUID; геометрии и разметка имеют provenance.

## Основные сущности
Project, SourceAsset, Experiment, ProcessingRun, Algorithm, Candidate, CandidateEvidence,
RankingProfile, AnnotationSet, Annotation, GeometryVersion, ConsensusSet, Dataset,
DatasetSample, MLModel, Workflow, Job, EventLog.

## System of record
| Тип данных | Источник истины |
|---|---|
| Project identity, source declarations and versions, paths, defaults, format version | `project.lspx` |
| Source catalog projection, results, publication intents and receipts | `project.sqlite` |
| Future jobs and event log | Требует отдельной продуктовой схемы; в SQLite 2 не реализовано |
| Vector geometries and spatial attributes | GeoPackage, registered in SQLite |
| Raster sources and derived rasters | GeoTIFF/COG, registered in SQLite |
| Experiment parameters and reproducibility manifest | Experiment JSON + SQLite reference |
| Independent expert decisions | AnnotationSet data + SQLite metadata |
| Dataset sample manifests | Versioned dataset manifest |

Не хранить одну изменяемую сущность независимо в нескольких местах без явного правила синхронизации.

## Candidate
`candidate_id`; `experiment_id`; `geometry_ref`; `length_m`; `azimuth_deg`; `straightness`;
`curvature_metric`; `stability`; `detector_agreement`; `scale_persistence`; `support_score`;
`geometric_rank`; `ranking_profile_id`; `geological_order` (nullable); `provenance_ref`.

## Annotation
`annotation_id`; `candidate_id`; `annotation_set_id`; `reviewer_id`; `status`; `feature_type`;
`expert_confidence` (optional); `notes`; `geometry_version`; `created_at`; `modified_at`.

## Разделение и история
Изменяемый статус конкретного эксперта не хранится в исходном Candidate. Решения хранятся
в Annotation. Геометрия и экспертные решения версионируются. Импорт не перезаписывает набор
по совпадению имени. Объединение наборов — явная операция с preview конфликтов и подтверждением.
Удаление/перезапись истории без явной операции и аудита запрещено.
