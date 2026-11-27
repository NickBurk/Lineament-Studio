# Metadata Schema

## 1. Project manifest — `project.lspx`
Формат: UTF-8 JSON. Расширение `.lspx` обозначает файл проекта Lineament Studio.
Не сериализовать Python objects/pickle. Все входные поля валидируются по versioned schema.

```json
{
  "format_id": "org.lineament-studio.project",
  "format_version": "1.0",
  "schema_version": "1",
  "project_id": "UUID",
  "application_version": "0.2.0",
  "created_at": "ISO-8601",
  "modified_at": "ISO-8601",
  "project_crs": "EPSG:XXXX",
  "storage_policy": "mixed",
  "catalog_uri": "project.sqlite",
  "assets": [
    {
      "asset_id": "UUID",
      "role": "primary_dem",
      "storage_mode": "reference",
      "uri": "file:///absolute/or/relative/path/dem.tif",
      "checksum": "sha256:...",
      "crs": "EPSG:XXXX",
      "width": 10000,
      "height": 10000,
      "band": 1,
      "dtype": "float32",
      "nodata": -9999
    }
  ],
  "default_profiles": {}
}
```

Пример схематический: `EPSG:XXXX`, checksum и URI должны быть реальными. Manifest проверяется
schema validator; обработка неизвестных полей определяется правилами совместимости версии.

## 2. Path rules
- Внутренний asset: относительный путь внутри project folder.
- Внешний asset: URI/путь к исходнику с `storage_mode=reference`.
- Абсолютный внешний путь не считается переносимым.
- Path traversal и выход внутреннего пути за пределы project folder запрещены.
- При relink старый и новый URI фиксируются в provenance event.

## 3. Project manifest
`format_id`, `format_version`, `schema_version`, `project_id`, `application_version`,
`created_at`, `modified_at`, `project_crs`, `storage_policy`, `catalog_uri`, `assets`,
`default_profiles`.

## 4. Experiment manifest
`experiment_id`, `project_id`, `created_at`, `dem_asset_id`, `dem_checksum`,
`algorithm_versions`, `parameters`, `crs`, `software_versions`, `dependency_versions`,
`resource_profile`, `random_seed` (если применимо), `outputs`, `output_checksums`, `warnings`.

## 5. Source asset
`asset_id`, `path/URI`, `storage_mode`, `format`, `checksum`, `CRS`, `dimensions`,
`pixel_size`, `extent`, `NoData`, `dtype`, `band`, `source/provider`, `license/terms`
(если известны), `acquisition_date` (если известна).

## 6. Provenance
Для каждого производного результата сохраняются входные asset IDs/checksums, параметры,
версия алгоритма, версия приложения/зависимостей, дата, CRS, единицы, предупреждения и checksum.

## 7. Экспертная разметка
Annotation Set содержит устойчивый ID, автора/идентификатор эксперта, дату, версию схемы,
источник, критерии, словарь классов и историю импорта/экспорта. Consensus Set хранит ссылки
на исходные Annotation Sets и явные решения конфликтов.

## 8. Безопасность
Секреты доступа к сервисам не сохраняются в открытом manifest. Абсолютные пользовательские
пути не коммитятся в Git. Импортируемые manifests проверяются до использования.
