# Licensing and Third-party Notices

## Предварительная модель
- Core: MIT как исходная цель после проверки совместимости.
- QGIS plugin: GPL-compatible; точная версия лицензии требует проверки.
- Desktop: соблюдение лицензий всех распространяемых компонентов.

## Проверка
Для каждой зависимости фиксировать package name, version, license identifier, notice location, bundled components, source URL и modifications.

## Qt
Проверить конкретный вариант PySide6/Qt, условия LGPL/GPL/коммерческой лицензии, динамическую линковку, notices и требования LGPL.

## GIS libraries
Проверить GDAL, PROJ, Rasterio, GEOS/Shapely, OpenCV и транзитивные зависимости выбранных версий.

## Данные
Отдельно учитывать лицензии DEM, геологических карт, спутниковых данных, OSM и GEE datasets. Возможность импорта не означает право распространения.

## Релиз
Обязательны LICENSE, THIRD_PARTY_NOTICES.md, SBOM/dependency manifest и инструкция сборки.
