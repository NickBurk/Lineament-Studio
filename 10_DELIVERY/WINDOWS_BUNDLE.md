# Windows Bundle

## Поставка
Portable ZIP и Installer.

## Архитектура
Предварительный вариант — PyInstaller Onedir. Один стартовый `LineamentStudio.exe` запускает Runtime из папки поставки. Onefile не является предпочтительным из-за GIS-зависимостей.

## Состав
Python runtime; PySide6/Qt; GDAL/PROJ; Rasterio; NumPy/SciPy; OpenCV; Shapely; Core Worker; документация; примеры, если лицензии разрешают.

## Требования
Чистая Windows x64; проверка DLL и PROJ data; отсутствие зависимости от системного Python; диагностика; корректное удаление; сохранение пользовательских проектов при обновлении.

## Installer
Inno Setup — предварительный выбор. Версия и параметры фиксируются в release pipeline.
