# Metadata Schema

## Restricted development profile (Phase 2–3)

`project.lspx` is UTF-8 JSON, validated before use by
`src/lineament_core/infrastructure/data/manifest.py`. The current implementation
accepts only `format_id=org.lineament-studio.project`, `format_version=1.1`,
`schema_version="2"`, with exactly the fields below. This example passes the
manifest validator; opening also requires a valid catalog and real source file.

```json
{
  "format_id": "org.lineament-studio.project",
  "format_version": "1.1",
  "schema_version": "2",
  "project_id": "285c458f-3ea7-4e13-bc71-b7ce29784142",
  "application_version": "0.2.0",
  "created_at": "2026-11-27T19:00:00+00:00",
  "modified_at": "2026-11-27T19:00:00+00:00",
  "project_crs": "EPSG:32632",
  "storage_policy": "reference",
  "catalog_uri": "project.sqlite",
  "assets": [
    {
      "asset_id": "701019e8-f2a0-43fd-8123-a8a0d2631087",
      "source_version_id": "7d37d49f-856d-4a8e-886a-7e84b5d4590d",
      "role": "primary_dem",
      "storage_mode": "reference",
      "uri": "/data/dem.tif",
      "checksum": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "metadata": {}
    }
  ],
  "default_profiles": {}
}
```

The path and checksum illustrate valid syntax; actual source availability and digest
are checked separately. On Windows a Reference `uri` is a native absolute path
(for example `C:\\data\\dem.tif`), not a `file://` URL. Copy uses a contained
relative path beginning with `inputs/dem/`. Network/device paths and links/reparse
points crossing the project boundary are rejected. `storage_policy` is `reference`,
`copy`, or `mixed`; each asset must match a non-mixed policy. `project_crs` may be
null; `default_profiles` and `metadata` are JSON objects.

The manifest owns source declarations: stable `asset_id`, immutable content
identity `source_version_id`, source checksum and path. Relinking to identical
content preserves both IDs. An explicitly accepted changed-content relink keeps
`asset_id`, assigns a new `source_version_id` and checksum, and preserves historical
result provenance bound to the old source version. SQLite's `assets` table is a
catalog projection and consistency witness, not an independent editor of these
declarations. Project Storage is the single write authority (DEC-A33).

The reader accepts a restricted self-contained GeoTIFF DEM profile. It rejects
external sidecars (including world files, PAM `.aux.xml`, external overviews and
masks) at import, availability, relink and processing boundaries. This is a
development profile, not a final GeoTIFF compatibility claim.

## SQLite catalog schema 2

`src/lineament_core/infrastructure/data/project.py` defines the actual DDL and
sets `PRAGMA user_version=2`:

| Table | Current purpose and relationships |
|---|---|
| `project` | Project UUID primary key and committed manifest bytes. |
| `assets` | Source UUID primary key, project foreign key; projection of manifest source identity. |
| `results` | Result UUID primary key, project and source foreign keys, job UUID, unique artifact path, checksum and canonical provenance JSON. |
| `pending` | Single slot (`slot=1`) publication intent with publication UUID, before/after manifest bytes and payload for recovery. |
| `receipts` | Publication UUID primary key; optional relink JSON or unique result UUID foreign key. |
| `migrations` | Version primary key and applied timestamp; no automatic migration is implemented. |

SQLite owns results, publication intents and receipts. Writes to duplicated
metadata go through Project Storage only. This schema does not implement the
future experiment, annotation, event or job tables described in the product data
model.

## Compatibility and future requirements

Manifest 1.0 / catalog 1 is unsupported. Unsupported versions are rejected
before mutation. Automatic migration from 1.0 / 1 to 1.1 / 2, rollback and full
product migration support are not implemented. PROJ-007 remains in progress;
OQ-25–27 and ADR-0003 remain open/proposed. A future product profile must define
compatibility, migration and path interoperability separately.

The product specification also calls for experiment manifests, derived result
provenance, annotation sets and reproducibility metadata. Their eventual schemas
remain separate from the restricted project manifest and current catalog DDL.
Current Hillshade result provenance is validated by
`src/lineament_core/infrastructure/data/provenance.py`.

## Future product schema requirements

These normative requirements retain their original priorities and optionality. This
section does not formally defer them or claim they are implemented. The current
Manifest 1.1 / SQLite 2 and Hillshade provenance specification above remain applicable.

### Experiment manifest
`experiment_id`, `project_id`, `created_at`, `dem_asset_id`, `dem_checksum`,
`algorithm_versions`, `parameters`, `crs`, `software_versions`, `dependency_versions`,
`resource_profile`, `random_seed` (если применимо), `outputs`, `output_checksums`, `warnings`.

### Source asset
`asset_id`, `path/URI`, `storage_mode`, `format`, `checksum`, `CRS`, `dimensions`,
`pixel_size`, `extent`, `NoData`, `dtype`, `band`, `source/provider`, `license/terms`
(если известны), `acquisition_date` (если известна).

### Provenance
Для каждого производного результата сохраняются входные asset IDs/checksums, параметры,
версия алгоритма, версия приложения/зависимостей, дата, CRS, единицы, предупреждения и checksum.

### Экспертная разметка
Annotation Set содержит устойчивый ID, автора/идентификатор эксперта, дату, версию схемы,
источник, критерии, словарь классов и историю импорта/экспорта. Consensus Set хранит ссылки
на исходные Annotation Sets и явные решения конфликтов.

### Безопасность
Секреты доступа к сервисам не сохраняются в открытом manifest. Абсолютные пользовательские
пути не коммитятся в Git. Импортируемые manifests проверяются до использования.

Unsafe serialization, including Python objects/pickle, is prohibited.
