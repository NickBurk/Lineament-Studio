# Input and Output Formats

## Растры
Основные: GeoTIFF, BigTIFF, COG. Поддержка иных форматов — по GDAL и после тестирования. Чтение CRS, transform, NoData, datatype и overviews обязательно.

## Векторы
GeoPackage, GeoJSON, Shapefile. Shapefile импортируется с учётом ограничений полей/кодировок; для внутренних результатов предпочтителен GeoPackage.

## Геологические карты
Основной сценарий — геопривязанные растровые карты. Инструмент georeferencing не разрабатывается. Векторные разломы также поддерживаются.

## OSM
Локальный PBF, GeoPackage, GeoJSON и доступные онлайн-запросы. Сохраняются источник, дата, лицензия/атрибуция и фильтр категорий.

## Выходы
GeoPackage — векторы; GeoTIFF/COG — LSM и производные; GeoJSON — обмен; CSV — статистика; JSON — конфигурации; PDF — отчёт; dataset archive — chips, masks, labels, manifest.

## CRS
Экспорт не должен молча терять CRS или преобразовывать единицы.
