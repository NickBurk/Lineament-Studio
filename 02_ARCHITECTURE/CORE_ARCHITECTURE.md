# Core Architecture

## Независимость и слои
`lineament_core` — библиотека и Worker Runtime, не зависящие от интерфейса. Рекомендуемое
разделение:
- `domain` — сущности, value objects, правила предметной области;
- `application` — use cases, orchestration, ports;
- `infrastructure` — raster/vector IO, SQLite, filesystem, process/resource adapters;
- `adapters` — Desktop/QGIS/OSM/GEE integration boundaries;
- `worker` — JSON/JSONL IPC entry point.

Core не импортирует PySide6, PyQt, PyQGIS или GUI widgets. Domain не зависит от infrastructure.

## Пакеты
```text
lineament_core/
  domain/
  application/
  infrastructure/
  adapters/
  worker/
  preprocessing/
  detection/
  postprocessing/
  ensemble/
  multiscale/
  support/
  structural/
  ranking/
  review/
  datasets/
  ml/
  smart/
  workflow/
  resources/
  export/
  provenance/
```

Фактическое дерево репозитория может отличаться. Агент обязан сначала проверить существующие
модули и не создавать дублирующую структуру без ADR/обоснования.

## Контракт алгоритма
Каждый алгоритм объявляет:
- `algorithm_id`, `algorithm_version`;
- схему параметров и defaults;
- типы входов и выходов;
- требования к CRS и единицам;
- NoData/NaN/Inf-поведение;
- численные допуски и граничные случаи;
- схему результатов;
- warnings/errors;
- поддержку progress/cancellation;
- минимальные аналитические и synthetic fixtures;
- ожидаемую сложность и память.

## Адаптеры
Дополнительный детектор подключается через интерфейс адаптера и не меняет общий контракт
результата. Адаптер не должен скрывать различия в detector family и семантике score.

## Версионирование
Версии пакета, алгоритма, project format, SQLite schema, IPC protocol и result schema независимы.
Изменение математического поведения требует изменения версии алгоритма и regression/benchmark report.
