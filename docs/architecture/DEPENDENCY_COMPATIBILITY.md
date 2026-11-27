# Совместимость зависимостей для Windows Bundle

Статус `PRELIMINARY`, проверка 2026-11-27. Цель — CPython 3.11 и Windows x64 (`win_amd64`). В Phase 0 проверены метаданные опубликованных пакетов, разрешение wheel-кандидатов и содержимое отдельных wheel-архивов. Проверки выполнялись на Linux x64. Установленный Windows runtime, драйверы, геопространственные результаты и Bundle требуют Windows-испытаний. [Технологическая база Master TZ](../../MASTER_TZ.md#6-технологии--предварительная-базовая-линия) · [Windows Bundle](../../10_DELIVERY/WINDOWS_BUNDLE.md)

## Кандидаты для проверки

| Компонент | Версия или линия для проверки | Что подтверждено и что проверять дальше |
|---|---|---|
| CPython | 3.11.x x64. Выбрать свежий воспроизводимый security build | Платформа определена DEC-A06. Проверить источник runtime, VC runtime и обновления на оставшемся сроке поддержки. Официальный 3.11.9 был последним регулярным bugfix release с Windows installer, выбор security build остаётся открытым. [Python versions](https://devguide.python.org/versions/) · [Python 3.11.9](https://www.python.org/downloads/release/python-3119/) |
| PySide6 | 6.11.3 | Разрешился `cp310-abi3-win_amd64` на 3.11 со всеми Qt/Shiboken packages той же версии. Проверить `qwindows`, imageformats, offscreen/clean VM и лицензию выбранных модулей. [PyPI](https://pypi.org/project/PySide6/6.11.3/) · [Qt deployment](https://doc.qt.io/qt-6/windows-deployment.html) |
| Rasterio | 1.4.4, ветка 1.4.x для CPython 3.11 | Найден нативный CP311 Windows wheel. Опубликованная ветка 1.5.x требует Python ≥3.12. Проверить локальные GeoTIFF/COG, окна и ресурсы wheel. [PyPI 1.4.4](https://pypi.org/project/rasterio/1.4.4/) · [PyPI 1.5.2](https://pypi.org/project/rasterio/1.5.2/) · [Rasterio installation](https://rasterio.readthedocs.io/en/stable/installation.html) |
| GDAL | Runtime из Rasterio 1.4.4 как кандидат. В DLL найдена строка релиза 3.10.3 | Самостоятельный пакет `GDAL` в PyPI не разрешился с `--only-binary :all:` для цели. Уточнить загруженную версию и драйверы на Windows. При необходимости `osgeo` проверять совместимую пару bindings/runtime из одного канала. [GDAL bindings](https://gdal.org/en/stable/api/python/python_bindings.html) · [PyPI GDAL](https://pypi.org/project/GDAL/) |
| PROJ / pyproj | PROJ data 9.6.0 из Rasterio. pyproj 3.7.2 с PROJ data 9.5.1 — кандидат при нужде в его API | В архивах разные PROJ DLL и разные layouts `proj.db`. Допускать их в одной среде только после проверки загрузки и соответствия data directories. Для трансформаций проверить axis order, grids, offline и фактический pipeline. [PyPI pyproj](https://pypi.org/project/pyproj/3.7.2/) · [PROJ resource files](https://proj.org/en/stable/resource_files.html) |
| NumPy / SciPy | NumPy 2.4.6, SciPy 1.17.1 | Оба CP311 wheels разрешились одновременно с Rasterio, OpenCV и Shapely. Импорт, арифметика, ABI, numeric tolerances и peak memory требуют проверки. [NumPy](https://pypi.org/project/numpy/2.4.6/) · [SciPy](https://pypi.org/project/scipy/1.17.1/) |
| OpenCV | `opencv-python-headless` 4.14.0.94 | Разрешился Windows ABI3 wheel. Проверить `cv2` и нужные функции, особенно требования к EDLines. Поставлять один выбранный OpenCV wheel, чтобы варианты не делили namespace `cv2`. [PyPI](https://pypi.org/project/opencv-python-headless/4.14.0.94/) |
| Shapely | 2.1.2 | CP311 wheel с собственными GEOS DLL. Geometry serialization через WKB/GeoPackage и metadata CRS. Нативные указатели не передаются между DLL. [PyPI](https://pypi.org/project/shapely/2.1.2/) |
| SQLite | Модуль `sqlite3` используемого CPython 3.11 build | SQLite runtime зависит от сборки интерпретатора. GIS wheels могут содержать свои SQLite DLL. Проверить `sqlite3.sqlite_version`, foreign keys, RTree при использовании, locking/recovery и работу на целевом FS. [Python sqlite3](https://docs.python.org/3.11/library/sqlite3.html) |
| GeoPackage | Спецификация OGC 1.4 как ориентир. Writer/version profile выбрать после round-trip | Формат через проверенный GDAL/OGR vector adapter. Проверить GPKG driver/read-write, geometry type, CRS, encoding, null/empty, RTree и round-trip в выбранной QGIS LTR. SQLite Catalog использует отдельный файл и собственную схему. [OGC GeoPackage](https://www.ogc.org/standard/geopackage/) · [GDAL GPKG](https://gdal.org/en/stable/drivers/vector/gpkg.html) |
| GeoTIFF / BigTIFF / COG | GTiff/COG drivers выбранной сборки GDAL. Профили I/O определить по fixtures | Проверить round-trip CRS, affine, nodata/mask, dtype, overviews, tiled/block reads, компрессию и BigTIFF. COG проверяется структурным валидатором и локальным чтением. [GDAL GTiff](https://gdal.org/en/stable/drivers/raster/gtiff.html) · [GDAL COG](https://gdal.org/en/stable/drivers/raster/cog.html) |
| PyInstaller / Inno Setup | PyInstaller Onedir 6.22.3 как wheel-кандидат. Inno Setup подбирается при проверке installer | Метаданные PyInstaller и Windows transitives разрешились. Зафиксировать hook versions и inventory Bundle. Проверить portable ZIP, upgrade, uninstall и сохранение данных. [PyInstaller](https://pypi.org/project/pyinstaller/6.22.3/) · [Inno Setup](https://jrsoftware.org/isinfo.php) |

## Фактические проверки Phase 0

Запросы к PyPI JSON сравнили `Requires-Python`, wheel tags и yanked status. Следующий опыт воспроизводит разрешение восьми прямых кандидатов на платформу Windows x64. Разрешилось 24 пакета. С теми же флагами вход из одной строки `GDAL` завершился ошибкой `No solution found` из-за отсутствия подходящего wheel. Wheel-only режим исключил локальную компиляцию. Версии приведены для воспроизведения опыта.

```text
# windows-candidates.in (временный файл)
PySide6==6.11.3
rasterio==1.4.4
pyproj==3.7.2
numpy==2.4.6
scipy==1.17.1
opencv-python-headless==4.14.0.94
shapely==2.1.2
pyinstaller==6.22.3
```

```sh
# uv 0.13.9, host CPython 3.12.14
uv --no-config pip compile --no-cache --no-python-downloads \
  --default-index https://pypi.org/simple \
  --python-platform x86_64-pc-windows-msvc --python-version 3.11 \
  --only-binary :all: windows-candidates.in
```

Четыре Windows wheel проверены по SHA-256 из PyPI JSON. ZIP inventory показал отдельные vendor DLL. Запрос к таблице `metadata` каждого `proj.db` выполнен в SQLite in-memory. Строки версии GDAL извлечены из PE-файлов без запуска.

| Wheel | Обнаруженные компоненты | Данные PROJ |
|---|---|---|
| Rasterio 1.4.4 | GDAL (строка 3.10.3), PROJ, GEOS, SQLite, GTiff, `gdal_data` | 9.6.0, layout 1.5, EPSG v12.004 |
| pyproj 3.7.2 | Отдельные PROJ и SQLite DLL | 9.5.1, layout 1.4, EPSG v11.022 |
| Shapely 2.1.2 | Отдельные GEOS и GEOS C DLL | — |
| Pyogrio 0.13.0, отдельная оценка vector I/O | Дополнительные GDAL (строка 3.12.4), PROJ, GEOS и SQLite DLL | 9.8.1, layout 1.6, EPSG v12.029 |

Наличие Pyogrio wheel подтверждено. Он не входит в набор из 24 пакетов. Разный layout баз PROJ делает общую настройку `PROJ_DATA` для несогласованных runtimes рискованной. Проверить действительный путь загруженной библиотеки и database для каждого компонента, затем оценить, можно ли обслужить raster/vector I/O и reprojection из согласованной GIS-сборки. [PyPI Pyogrio](https://pypi.org/project/pyogrio/0.13.0/) · [ADR-0004](adr/ADR-0004-WINDOWS-GIS-RUNTIME.md)

## Допуск к фиксации версий

1. На Windows x64 под целевой сборкой CPython 3.11 проверить wheel-кандидат и сравнить с согласованной сборкой из одного канала, если требуется OGR или конфликтуют DLL/данные. Снять версии Python, Qt, GDAL, PROJ, EPSG database, GEOS, SQLite и BLAS. Снять inventory драйверов, DLL, data paths и notices.
2. На синтетических файлах проверить GeoTIFF/COG и GPKG, reprojection с осью lat/lon и метрической CRS, grid с отключённой сетью, Unicode/пробелы/длинные пути, reopen, закрытие дескрипторов, отмену и fault recovery. Версии SQLite и RTree отдельно фиксировать для каталога и GIS runtime.
3. Собрать Onedir на Windows и проверить portable и installer на чистой поддерживаемой Windows без Python/QGIS. Отдельно проверить работу рядом с QGIS, отсутствие захвата чужих DLL и запуск QGIS adapter с внешним Worker. Опубликовать команды и forensic inventory в QA evidence, размеры и перечень допущений.
4. После passing checks, SBOM, проверки advisory и лицензий зафиксировать платформенный lock с хешами и источниками. Возможность обновлять security patches CPython 3.11 и нативных библиотек входит в решение о поставке. Версии Windows и QGIS LTR определяются отдельно.

Главные открытые риски — ABI NumPy 2 и OpenCV/SciPy/Rasterio, разные GDAL/PROJ/GEOS/SQLite DLL, отсутствие или несовместимость `proj.db` и grid files, покрытие GPKG/GTiff drivers, Qt plugins и VC runtime. Для защиты от захвата DLL проверяются пути из установленного Bundle и поведение при изменённом `PATH`. Сборку и установку проверять в каталоге с пробелами и Unicode, под обычным пользователем и без сети. [Риски R-04/R-15](../../12_PROJECT_CONTROL/RISK_REGISTER.md) · [Release Requirements](../../10_DELIVERY/RELEASE_REQUIREMENTS.md)
