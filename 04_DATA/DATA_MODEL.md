# Data Model

## Принципы
- `project.lspx` — главный project manifest.
- SQLite — system of record для каталога сущностей, связей, событий и транзакционных метаданных.
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
| Project identity, paths, defaults, format version | `project.lspx` |
| Catalog, relational metadata, jobs, event log | `project.sqlite` |
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
