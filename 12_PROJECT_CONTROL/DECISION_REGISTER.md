# Decision Register

Дата базовой фиксации: 2026-11-27. Версия документации: 0.2.0.

## Статусы
- `USER_APPROVED` — явно подтверждено заказчиком.
- `ARCHITECT_SELECTED` — технический выбор в рамках делегированного полномочия.
- `PROPOSED` — не утверждено.
- `OPEN` — требует проверки/решения.
- `DEFERRED` — отложено.
- `REJECTED` — исключено.

## USER_APPROVED
| ID | Решение |
|---|---|
| DEC-U01 | Назначение: поиск тектонических кандидатов, структурный анализ, линейные формы, предварительная оценка перспективных участков, датасеты и научное сравнение |
| DEC-U02 | DEM-first как основной принцип с перспективой мультиисточникового анализа |
| DEC-U03 | Гибридная архитектура |
| DEC-U04 | Desktop Bundle |
| DEC-U05 | Геологические карты преимущественно как геопривязанные растры |
| DEC-U06 | Не разрабатывать georeferencing |
| DEC-U07 | Overlay основной; Swipe и Side-by-side дополнительные |
| DEC-U08 | Анализ профиля рельефа не является основной функцией |
| DEC-U09 | OSM import обязателен |
| DEC-U10 | Batch Processing обязателен |
| DEC-U11 | Хранение проекта — folder |
| DEC-U12 | DEM source — выбор Reference/Copy |
| DEC-U13 | Backup — manual |
| DEC-U14 | AI — Smart, без обязательных внешних API |
| DEC-U15 | Ranking — separate |
| DEC-U16 | User-defined ranking обязателен |
| DEC-U17 | Expert workflow — independent |
| DEC-U18 | Поддержка ноутбука с 16 ГБ RAM и встроенной графикой |
| DEC-U19 | Ядро должно быть переносимым между интерфейсами |
| DEC-U20 | В разработке использовать предоставленный Engineering Skills Pack как набор процессных инструкций |
| DEC-U21 | Lineament-Studio создаётся с нуля в новом GitHub-репозитории; код и Git-история `linia-app` не переносятся и не используются |

## ARCHITECT_SELECTED
| ID | Решение | Условие |
|---|---|---|
| DEC-A01 | Desktop GUI — PySide6 | Проверить bundle |
| DEC-A02 | Собственный облегчённый Qt Map Canvas | Обязателен вертикальный прототип |
| DEC-A03 | Core Worker — отдельный процесс | Проверить IPC/cancellation |
| DEC-A04 | QGIS Plugin — тонкий адаптер к Worker | Проверить QGIS LTR |
| DEC-A05 | JSON manifest + SQLite + GPKG + GeoTIFF | Утвердить schema |
| DEC-A06 | Python 3.11 target | Проверить зависимости |
| DEC-A07 | PyInstaller Onedir | Проверить чистую Windows |
| DEC-A08 | Inno Setup | Проверить upgrade/uninstall |
| DEC-A09 | Multi-scale 1×/2×/4× | Настраиваемо |
| DEC-A10 | 8 azimuths с шагом 45° | Настраиваемо |
| DEC-A11 | Sun altitude 45° | Настраиваемо |
| DEC-A12 | Balanced profile: Canny + LoG + LSD | Benchmark |
| DEC-A13 | EDLines/Hough как дополнительные методы | Benchmark |
| DEC-A14 | LSM groups: directional, detector, scale, morphometric | Проверить корреляции |
| DEC-A15 | Начальные LSM weights 0.25 each | Не считать оптимальными |
| DEC-A16 | Geometric score 0.7 length / 0.3 straightness | Benchmark/пересмотр |
| DEC-A17 | G1/G2/G3 как tertiles | Межрегионально нужен fixed profile |
| DEC-A18 | Annotation confidence optional 1–5 | Проверить UX |
| DEC-A19 | Dataset chips 256 px, overlap 50% | Настраиваемо |
| DEC-A20 | Dataset split 70/15/15 spatial | Не random adjacent split |
| DEC-A21 | Classical ML first | Deep Learning deferred |
| DEC-A22 | Smart agents use registered operations only | Security review |
| DEC-A23 | Worker memory budget initial 6 GB on 16 GB system | Измерить |
| DEC-A24 | Tile 1024×1024 initial | Benchmark |
| DEC-A25 | MIT as initial Core license target | Legal review |
| DEC-A26 | GPL-compatible QGIS plugin | Exact license review |
| DEC-A27 | Portable ZIP + Installer | Release test |
| DEC-A28 | OSM is context, not automatic deletion | Preserve provenance |
| DEC-A29 | GEE initially connector/script/export adapter | Backend deferred |
| DEC-A30 | Главный файл проекта — `project.lspx`, UTF-8 JSON manifest; `project.sqlite` — каталог | ADR-0001; schema/migration tests |
| DEC-A31 | Skills Pack v1.0 встроен в `.agents/skills`, `AGENTS.md`, `docs/SKILL_ROUTING.md` и `docs/templates` | Проверить discovery в целевом coding agent |
| DEC-A32 | Для межслойных/публичных архитектурных изменений требуется ADR | Проверять на PR |

## OPEN / PROPOSED
Точные версии QGIS LTR, GDAL, PROJ и зависимостей; финальные определения LoG zero-crossing и matching;
эмпирическая калибровка LSM weights/radii; межрегиональные пороги ranking; поддерживаемые версии
Windows; лицензии bundled packages; финальный список детекторов после benchmark; совместимость
legacy project formats после аудита фактического репозитория.

## DEFERRED
Local LLM в базовой поставке; Deep Learning; полноценный cloud detection backend в GEE;
real-time collaborative review; полноценная замена QGIS; автоматическое подтверждение разломов.


## Интерпретация численных стартовых параметров
Азимуты, масштабы, matching tolerances, LSM weights/radii, geometric score weights, chip size,
overlap, split ratios, tile size и memory budget — стартовые профили/инженерные настройки.
Они не являются универсальными геологическими или научными константами. Их нельзя объявлять
валидированными без источника, benchmark, ablation study или отдельного утверждения.
