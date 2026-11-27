# QGIS Architecture

## Принцип
QGIS Plugin — тонкий адаптер к Lineament Core Runtime. Вычислительные алгоритмы внутри плагина не переписываются.

## Компоненты
`metadata.txt`; `__init__.py`; plugin entry point; Processing Provider; `QgsProcessingAlgorithm` wrapper; Job Client; Runtime discovery; result loader.

## Processing
Один алгоритм с параметром `SINGLE` / `ENSEMBLE`. Поддержка Toolbox, Modeler, Batch Processing и `qgis_process` подтверждается тестами выбранной версии QGIS.

## Worker
Плагин запускает внешний Core Worker. Параметры — версионированный JSON job manifest. Результаты — GPKG/GeoTIFF. Прогресс и отмена связаны с QGIS feedback.

## Runtime
Плагин не загружает Desktop PySide6 в процесс QGIS. Путь к Core Runtime настраивается и проверяется. При отсутствии Runtime показывается диагностическая инструкция.

## Совместимость
Минимальная QGIS LTR выбирается после CI-прототипа. Нельзя заявлять совместимость без теста на чистом профиле QGIS.
