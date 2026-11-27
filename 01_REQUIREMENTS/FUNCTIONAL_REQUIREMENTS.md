# Functional Requirements

Формулировки ниже являются нормативным каталогом. `Method` обозначает минимально необходимую
проверку. Конкретные test IDs и доказательства заносятся в Traceability Matrix.

| ID | Требование | Приоритет | Method |
|---|---|---:|---|
| PROJ-001 | Система ДОЛЖНА создавать, открывать, сохранять и закрывать проект | P0 | Project integration test |
| PROJ-002 | Система ДОЛЖНА повторно открывать проект с восстановлением слоёв и результатов | P0 | Restart/reopen E2E |
| PROJ-003 | Пользователь ДОЛЖЕН выбирать Reference или Copy для исходного DEM | P0 | UI + storage test |
| PROJ-004 | Система ДОЛЖНА обнаруживать отсутствующий внешний источник и предоставлять Locate/Relink | P0 | Missing-source regression |
| PROJ-005 | Система ДОЛЖНА вести журнал экспериментов и событий | P1 | DB integration |
| PROJ-006 | Проект ДОЛЖЕН иметь главный файл `project.lspx` с versioned manifest | P0 | Schema validation |
| PROJ-007 | Система ДОЛЖНА проверять совместимость `format_version` и выполнять явные миграции | P1 | Migration tests |
| PROJ-008 | Система ДОЛЖНА обнаруживать недоступность и изменение checksum источника | P0 | Source integrity test |
| DATA-001 | Система ДОЛЖНА импортировать GeoTIFF DEM | P0 | Real-file integration |
| DATA-002 | Система ДОЛЖНА выполнять Preflight CRS/resolution/NoData/units/transform | P0 | Raster fixtures |
| DATA-003 | Система ДОЛЖНА импортировать геопривязанные геологические растры | P1 | Raster integration |
| DATA-004 | Система ДОЛЖНА импортировать векторные геологические данные | P1 | Vector integration |
| DATA-005 | Система ДОЛЖНА импортировать OSM online или из локального файла | P1 | Offline/online integration |
| DATA-006 | Система ДОЛЖНА явно преобразовывать CRS без молчаливого изменения исходника | P0 | CRS regression |
| DATA-007 | Система ДОЛЖНА читать большие растры оконно/блоками, если алгоритм это допускает | P0 | Large-raster benchmark |
| DATA-008 | Preflight ДОЛЖЕН проверять bands, dtype, NaN/Inf, mask, rotation/skew, extent и dimensions | P0 | Synthetic raster matrix |
| DATA-009 | Система ДОЛЖНА различать отсутствующий CRS, неизвестный CRS и CRS с угловыми единицами | P0 | CRS edge tests |
| PRE-001 | Система ДОЛЖНА строить Hillshade | P0 | Analytic surface test |
| PRE-002 | Система ДОЛЖНА строить Multi-directional Hillshade | P1 | Directional fixture |
| PRE-003 | Система ДОЛЖНА поддерживать Slope, Curvature, TPI и LRM согласно приоритетам Roadmap | P1 | Numerical fixtures |
| DET-001 | Система ДОЛЖНА поддерживать Canny | P0 | Synthetic edge test |
| DET-002 | Система ДОЛЖНА поддерживать LoG zero-crossing | P0 | Synthetic step/impulse test |
| DET-003 | Система ДОЛЖНА поддерживать LSD | P1 | Synthetic line test |
| DET-004 | Система ДОЛЖНА поддерживать EDLines | P1 | Synthetic line test |
| DET-005 | Система ДОЛЖНА поддерживать Hough | P1 | Synthetic line test |
| DET-006 | Дополнительные детекторы ДОЛЖНЫ подключаться через versioned adapter contract | P2 | Adapter contract test |
| POST-001 | Система ДОЛЖНА фильтровать артефакты по документированным признакам | P0 | Positive/negative fixtures |
| POST-002 | Система ДОЛЖНА векторизовать результат с сохранением CRS и provenance | P0 | Raster-to-vector test |
| POST-003 | Система ДОЛЖНА объединять и дедуплицировать сегменты без неконтролируемого chain-merging | P0 | Geometry regression |
| ENS-001 | Система ДОЛЖНА поддерживать Single и Ensemble | P0 | Pipeline integration |
| ENS-002 | Система ДОЛЖНА сопоставлять линии между прогонами с учётом угла, расстояния и overlap | P0 | Synthetic matching |
| MSC-001 | Система ДОЛЖНА поддерживать несколько пространственных масштабов | P0 | 1x/2x/4x fixture |
| LSM-001 | Система ДОЛЖНА строить LSM_DEM | P0 | Component/range tests |
| LSM-002 | Система ДОЛЖНА экспортировать карты компонентов и disagreement | P1 | Raster output test |
| STR-001 | Система ДОЛЖНА рассчитывать длину, ориентацию, straightness и curvature metrics | P0 | Geometry fixtures |
| STR-002 | Система ДОЛЖНА строить rose diagram и осевую статистику modulo 180° | P1 | Circular-statistics test |
| STR-003 | Система ДОЛЖНА строить карты плотности с явными units/kernel/radius | P1 | Density fixture |
| STR-004 | Система ДОЛЖНА выделять потенциальные геометрические узлы без автоматического геологического вывода | P1 | Node geometry tests |
| RANK-001 | Система ДОЛЖНА рассчитывать отдельный Geometric Rank | P0 | Rank unit tests |
| RANK-002 | Система ДОЛЖНА поддерживать пользовательские ranking profiles и веса | P1 | Profile persistence test |
| RANK-003 | Geological Order ДОЛЖЕН храниться отдельно и назначаться экспертом/импортом | P1 | Data model test |
| REV-001 | Каждый эксперт ДОЛЖЕН иметь независимый Annotation Set | P1 | Multi-set integration |
| REV-002 | Annotation ДОЛЖНА поддерживать Pending/Accepted/Rejected/Uncertain | P1 | State tests |
| REV-003 | Система ДОЛЖНА сохранять историю решений и версий геометрии | P1 | Audit/history test |
| REV-004 | Система ДОЛЖНА сравнивать независимые Annotation Sets | P1 | Comparison test |
| REV-005 | Consensus Set ДОЛЖЕН быть отдельным производным набором | P1 | Provenance test |
| REV-006 | Импорт Annotation Set НЕ ДОЛЖЕН перезаписывать другой набор по имени | P1 | Import collision test |
| DS-001 | Система ДОЛЖНА формировать chips и masks с manifest/provenance | P1 | Dataset fixture |
| DS-002 | Система ДОЛЖНА поддерживать spatial Train/Validation/Test split | P1 | Spatial leakage test |
| DS-003 | Каждый sample ДОЛЖЕН иметь источник и annotation provenance | P1 | Manifest validation |
| ML-001 | Система ДОЛЖНА поддерживать базовые классические модели | P1 | Train/evaluate test |
| ML-002 | Система ДОЛЖНА сохранять версии модели, признаков, split и метрик | P1 | Model registry test |
| UI-001 | Desktop ДОЛЖЕН предоставлять единое главное окно с рабочими пространствами | P0 | GUI acceptance |
| UI-002 | Параметры ДОЛЖНЫ иметь контекстную справку, units, range и default | P1 | UI inspection |
| UI-003 | Система ДОЛЖНА показывать сопоставимые графические примеры влияния параметров | P1 | Preview regression |
| UI-004 | Основные экраны ДОЛЖНЫ поддерживать empty/loading/ready/running/success/warning/error/disabled | P0 | GUI state tests |
| BAT-001 | Система ДОЛЖНА поддерживать Batch Processing | P1 | Batch integration |
| OSM-001 | OSM ДОЛЖЕН импортироваться с source/date/filter/provenance metadata | P1 | OSM metadata test |
| QGIS-001 | QGIS Plugin ДОЛЖЕН предоставлять Processing Provider к Core Runtime | P1 | Clean QGIS test |
| GEE-001 | GEE-интеграция МОЖЕТ предоставлять авторизацию/экспорт/импорт как optional adapter | P2 | Adapter integration |
| EXP-001 | Система ДОЛЖНА экспортировать GPKG, GeoTIFF, GeoJSON и таблицы | P0 | Round-trip export |
| REP-001 | Система ДОЛЖНА формировать научный отчёт с картами, графиками и параметрами | P1 | Report fixture |

Наличие UI-кнопки не является доказательством выполнения FR.
