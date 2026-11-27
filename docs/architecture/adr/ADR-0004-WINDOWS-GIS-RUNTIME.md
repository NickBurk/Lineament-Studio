# ADR-0004 — Происхождение нативного GIS runtime для Windows

- Статус: Proposed
- Дата: 2026-11-27
- Авторы: Phase 0 Architecture
- Связанные требования: DATA-001/006/007, EXP-001, NFR-COMP-001/002, NFR-OFF-001, AC-REL-001. Вопросы OQ-03/12/13/28.

## Контекст

DEC-A01/A06–A08 задают PySide6, Python 3.11, PyInstaller Onedir и Inno Setup с проверками. Windows wheels Rasterio, pyproj и Pyogrio содержат разные PROJ layouts и vendor DLL. Для поставки нужны рабочие raster/vector/CRS операции и воспроизводимый источник DLL. [Результаты Phase 0](../DEPENDENCY_COMPATIBILITY.md)

## Решение к согласованию

Сначала проверить Windows wheel profile с минимальным набором runtime packages и явным владением ресурсами GDAL/PROJ. Начать с Rasterio для raster IO. Отдельный pyproj допускать при необходимости его API и подтверждённом совместном использовании DLL и data directories. Для GeoPackage отдельно выбрать vector adapter. При необходимости `osgeo` или конфликте wheels проверить профиль из единого канала с проверяемым lock. Каждый профиль загружает библиотеки из своего Bundle. Core Contracts используют лёгкий профиль без GIS.

## Рассмотренные альтернативы

Использовать GIS wheels как есть — минимальная стоимость первого эксперимента, но вероятны отдельные DLL и разные datasets. Единый build из согласованного канала, например conda-forge, позволяет сопоставить GIS-библиотеки и bindings, но требует отдельной проверки сборки PyInstaller, redistribution и lock. Собственная нативная сборка повышает контроль и требует сопровождения обновлений и воспроизводимости. Использование DLL из системного QGIS несовместимо с автономной поставкой.

## Последствия и риски

Нужны Windows VM, driver and DLL inventory, лицензионная проверка и offline smoke. Если одна среда содержит несколько native runtimes, должны быть проверены их ресурсы, порядок импортов и точность трансформаций. QGIS использует внешний Worker с диагностикой версий. Изменение версии geospatial runtime требует проверок регрессии геометрии, CRS и научной воспроизводимости.

## Миграции и совместимость

Runtime lock отделён от версии протокола и проекта. Зафиксировать версию зависимостей в manifests экспериментов. Обновление runtime проходит проверку чтения ранее опубликованных artifacts и регрессию результатов. Научные расхождения требуют анализа и документирования.

## Проверка корректности

Пройти Windows checks из Dependency Compatibility, включая GeoPackage/GeoTIFF round-trip, операцию reprojection, чистую Windows без Python/QGIS, coexistence, offline, provenance, SBOM и сборку Onedir. До проверки ADR сохраняет статус Proposed.
