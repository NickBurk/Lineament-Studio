# QGIS Plugin Specification

## Назначение
Доступ к Lineament Core из QGIS Processing Toolbox.

## Обязательные возможности
Processing Provider; Single/Ensemble; DEM input; detector profiles; GPKG/GeoTIFF outputs; Batch Processing; Modeler support; progress; cancellation; Runtime diagnostics.

## Архитектура
Плагин остаётся тонким PyQGIS-адаптером. Он запускает Core Worker как отдельный процесс. Desktop PySide6 GUI не загружается внутрь процесса QGIS.

## Параметры
Названия и типы стабильны для Modeler и Batch. Изменение параметров требует versioning/migration policy.

## Установка
ZIP-плагин плюс совместимый Core Runtime, если он не обнаружен. Плагин объясняет отсутствие Runtime.

## Тесты
Загрузка Provider; запуск из Toolbox; Batch; Modeler; `qgis_process`, если поддерживается выбранной версией; отмена; CRS; ошибки Worker; чистый профиль QGIS.
