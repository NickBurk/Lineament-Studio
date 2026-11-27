# Release Requirements

## Release gates
- все P0 acceptance tests пройдены;
- regression/security suite пройдена;
- benchmark отчёт приложен;
- воспроизводимая сборка с commit SHA и toolchain versions зафиксирована;
- чистая Windows установка проверена без системного Python и QGIS;
- приложение открывает `.lspx`, загружает DEM, выполняет минимальный pipeline и экспорт;
- Qt plugins, GDAL drivers, GDAL data, PROJ database/data и DLL проверены;
- пути с пробелами, Unicode и нестандартной директорией установки проверены;
- offline-first сценарии проверены;
- лицензии и notices подготовлены;
- user manual, release notes и known issues готовы;
- checksums и rollback plan опубликованы.

## Артефакты
Desktop Portable ZIP; Windows Installer; QGIS Plugin ZIP; Core Runtime package; user manual;
developer documentation; changelog; third-party notices; dependency/SBOM manifest; checksums.

## Обновление
Обновление не изменяет исходные DEM, экспертные наборы или результаты прошлых экспериментов.
Перед schema migration проверяется совместимость и возможность отката.
