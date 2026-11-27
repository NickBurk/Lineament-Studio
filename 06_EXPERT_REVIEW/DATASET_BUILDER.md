# Dataset Builder

## Источники меток
- Accepted — положительный класс в рамках выбранной экспертной схемы;
- Rejected — отрицательная метка только если объект явно проверен;
- Uncertain — не включается в стандартное обучение;
- Artifact — отдельная категория помех, если размечена.

Отсутствие кандидата/метки не означает отрицательную метку.

## Chips
Стартовые значения: 256×256 px, overlap 50%. Настраиваемо. Размеры привязываются к разрешению DEM;
manifest содержит физический размер области, разрешение и CRS.

## Splitting
По умолчанию 70/15/15, но разделение выполняется spatial blocks или по независимым территориям.
Случайное распределение соседних chips между Train и Test не используется по умолчанию из-за
spatial leakage. Процентные доли — стартовый профиль, а не обязательная научная константа.

## Provenance
Каждый sample связан с исходным DEM/checksum, candidate/annotation, Annotation Set/version,
автором/критериями разметки, chip transform, CRS, физическим размером области и split.

## Выход
Raster chips; masks; labels; metadata; split manifest; source provenance; annotation set/version;
dataset version; checksums.

## Форматы
GeoTIFF/PNG для chips по выбранному профилю, GeoPackage/GeoJSON для векторных labels,
JSON/CSV manifest. Импорт/экспорт и versioning не должны перезаписывать исходные наборы.
