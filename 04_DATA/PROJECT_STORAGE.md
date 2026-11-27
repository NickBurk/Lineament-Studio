# Project Storage Specification

## 1. Нормативная модель
Проект хранится в каталоге. Главный файл проекта — `project.lspx`.
`project.lspx` является UTF-8 JSON manifest, а не ZIP-контейнером. Это выбранная техническая
модель на основе существующего решения о JSON manifest и требования Skills Pack о `.lspx`.
Каталог SQLite и пространственные данные хранятся рядом с manifest.

Главный файл новой схемы закреплён [ADR-0001](../docs/architecture/adr/ADR-0001-LSPX-PROJECT-MANIFEST.md).

## 2. Структура каталога
```text
MyProject/
  project.lspx
  project.sqlite
  inputs/
    dem/
    geology/
    osm/
  processing/
  experiments/
    EXP_0001/
      manifest.json
      results/
      logs/
  results/
  annotations/
  datasets/
  reports/
  cache/
  logs/
```

## 3. Содержимое `.lspx`
Обязательные поля: `format_id`, `format_version`, `schema_version`, `project_id`,
`application_version`, `created_at`, `modified_at`, `project_crs`, `storage_policy`,
`assets`, `catalog_uri`, `default_profiles`.
Подробная схема приведена в `METADATA_SCHEMA.md`.

Текущий restricted development profile принимает только manifest `format_version=1.1`,
`schema_version="2"` и каталог `PRAGMA user_version=2`. `format_version` относится к
формату файла проекта; `schema_version` — к структуре SQLite. Эти версии не
взаимозаменяемы. Фактический состав полей и DDL описаны в `METADATA_SCHEMA.md`.

## 4. Reference / Copy
- **Reference**: DEM остаётся по внешнему native absolute path (без `file://`). В manifest
  сохраняются путь, checksum, stable asset ID, source-version ID и metadata. Отсутствие
  источника не удаляет результаты проекта.
- **Copy**: исходный файл копируется внутрь `inputs/`; путь в manifest хранится относительно
  каталога проекта. Исходник не перемещается и не удаляется.
- Выбор делается пользователем для каждого источника или по явно выбранному профилю.
- Требования к UI-подтверждению и проверке свободного места сохраняются для продукта;
  текущий backend не реализует UI.

## 5. Разрешение путей и повторное открытие
1. При открытии читается и валидируется `project.lspx`.
2. Внутренние пути разрешаются относительно каталога проекта.
3. Внешние пути проверяются на доступность.
4. Если источник отсутствует, приложение показывает имя источника, сохранённый путь и действие
   Locate/Relink. Оно не подменяет источник молча.
5. После relink проверяются формат, CRS, размеры, transform и checksum. Совпадение
   содержимого сохраняет `source_version_id`; подтверждённая смена содержимого создаёт
   новый `source_version_id` при стабильном `asset_id`. Исторический provenance результатов
   остаётся привязан к прежней версии. UI выбора остаётся продуктовым требованием.
6. Приложение не теряет остальные слои и результаты из-за отсутствия одного DEM.
7. Повторное открытие приложения и проекта — обязательный regression сценарий.

## 6. Безопасная запись
Текущий local development profile использует SQLite WAL + FULL, один cooperating writer,
durable PREPARED intent до замены manifest и recovery с проверкой publication receipt.
Manifest валидируется до публикации; результат регистрируется после проверки артефакта.
Эти гарантии проверены для documented local profile, но не доказывают power-loss durability
на всех файловых системах. Project Storage — единственный write authority: manifest владеет
source declarations/versions, SQLite хранит их catalog projection и владеет results,
publication intents и receipts (DEC-A33). Исходный DEM не перемещается и не перезаписывается.

## 7. Backup
Backup запускается вручную. UI показывает дату последней резервной копии и предупреждает,
если проект изменён после неё. Кеш может исключаться. Автоматический backup не становится
обязательным поведением без отдельного решения пользователя.

## 8. Миграции
- Manifest 1.0 / SQLite catalog 1 текущей реализацией не поддерживаются: версии
  отвергаются до mutation. Автоматическая миграция 1.0/1 → 1.1/2 и rollback не реализованы.
- Следующие пункты — будущие продуктовые требования PROJ-007, а не реализованные функции.
- Валидировать `format_version` до загрузки.
- Поддерживать явные migration steps между версиями.
- Записывать migration history и результат.
- До изменения схемы проверять возможность rollback.
- Не удалять исходные поля/файлы до успешной проверки результата.
- Импорт пользовательских проектов из других форматов требует отдельного решения и спецификации.
  [ADR-0001](../docs/architecture/adr/ADR-0001-LSPX-PROJECT-MANIFEST.md) · [OQ-17](../12_PROJECT_CONTROL/OPEN_QUESTIONS.md)

## 9. Безопасность
Валидировать размер и структуру manifest и импортируемых файлов; запрещать path traversal;
не выполнять небезопасную десериализацию; учитывать права доступа, занятые файлы, длинные
Windows-пути, Unicode, нехватку диска и отключение носителя.
