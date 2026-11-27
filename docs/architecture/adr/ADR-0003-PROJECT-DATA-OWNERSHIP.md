# ADR-0003 — Владение данными проекта и публикация результатов

- Статус: Proposed
- Дата: 2026-11-27
- Авторы: Phase 0 Architecture
- Связанные требования: PROJ-001–008, NFR-DATA-001/002, NFR-REPRO-001 и NFR-REL-002. Вопросы OQ-25–27.

## Контекст

ADR-0001 фиксирует папку, `project.lspx`, SQLite Catalog и spatial files. Project Storage и Metadata Schema требуют `assets` и хранят paths/CRS/checksums исходников в manifest. Data Model описывает SQLite как каталог сущностей. Слой, меняющий asset data, и порядок восстановления файла и SQLite после сбоя требуют явного правила. [ADR-0001](ADR-0001-LSPX-PROJECT-MANIFEST.md) · [Data Model](../../../04_DATA/DATA_MODEL.md)

## Решение к согласованию

- Manifest владеет Project ID, project CRS, defaults, StoragePolicy, каталогом и source declarations. `assets` содержит выбранные пользователем входные источники и их сохранённые значения `asset_id`, `storage_mode`, URI, checksum и метаданных согласно окончательной schema. Копируемые в SQLite значения служат проверяемой проекцией. Актуальность проверяется по revision или digest manifest. Поля проекции обновляются одним путём через Project Storage.
- SQLite владеет job/experiment IDs, ссылками на опубликованные результаты, event log и реляционными метаданными. GeoPackage хранит пространственные геометрии, GeoTIFF/COG — растр, experiment JSON — воспроизводимый snapshot с контрольными суммами. SQLite хранит ссылки и проверяемые индексы для этих снимков. Изменения Annotation Sets версионированы, права на экспертные состояния распределены по наборам.
- Предпочтительный механизм Phase 2 для согласованных записей — журнал операции с UUID, expected revision/digest и записями staging. Данные проверяются и готовятся вне видимого списка. После успешной проверки файл находится на целевом томе, manifest обновляется атомарной заменой, где она поддерживается, затем одна SQLite транзакция сверяет версию, фиксирует проекцию и публикует ссылки. При незавершённой операции reader выполняет/требует recovery до показа несогласованных данных. Восстановление может безопасно завершить операцию либо восстановить ранее подтверждённое состояние. Повтор команды не создаёт второй опубликованный результат.
- На раннем этапе предложен один writer на проект. Другой экземпляр приложения получает явную диагностику или поддерживаемый режим чтения. Конкретный механизм блокировки, crash recovery, commit order и политика read-only требует отдельного дизайна и тестов в Phase 2.
- Внутренний путь — относительный в корне проекта. Отдельно проверяются нормализация, разрешение symlink/junction и тип файла. Внешний Reference — явно обозначенный путь к выбранному DEM, при открытии определяется доступность. Manifest открывается до IO с источниками: валидируются версии и project ID. Политика UNC, URI, относительного Reference и доступа по стороннему manifest утверждается до реализации resolver.

## Рассмотренные альтернативы

Каталог как владелец всех asset records упрощает транзакции и требует изменить нормативное содержимое `assets`. Repository-wide journal в новом файле усложняет recovery и дублирует транзакционные возможности каталога. Транзакция только в SQLite оставляет окно несогласованности manifest и spatial files. ZIP-контейнер противоречит принятому ADR-0001.

## Последствия и риски

Чтение и экспорт смогут опираться на устойчивое состояние при отсутствии исходного DEM. Риск создают временные интервалы между записью manifest, перемещением файлов и commit SQLite. План проверки обязан покрыть каждую границу, включая повторное выполнение, диск, занятые файлы и два writer-процесса. Staging и журнал восстановления обслуживают целостность записи. Пользовательский backup остаётся ручным по DEC-U13.

## Миграции и совместимость

`format_version` относится к manifest, `schema_version` — к SQLite. Перед миграцией проверяются обе версии и identity, затем выполняется явный versioned migration с проверкой rollback. Неподдерживаемая версия диагностируется перед изменением. Грамматика URI, ограничения размера, список неизбежных полей и неизвестные поля утверждаются отдельно. Импорт внешних проектных форматов регулируется OQ-17.

## Проверка корректности

Schema и round-trip fixtures; Reference/Copy; missing/moved/checksum drift; Unicode, traversal, symlink/junction, drive-relative и UNC path; reopen после каждой fault-injection точки; две конкурирующие записи; повтор recovery; занятый каталог и нехватка диска; миграция и откат; расхождение manifest и SQLite identity/version. Проверки используют реальные синтетические GeoTIFF/GeoPackage и SQLite файлы в Phase 2.

## Обязательный P1 gate перед Phase 2

Ревью PR #1 выявило окно сбоя между заменой manifest и фиксацией записи в каталоге. До начала Phase 2 утвердить точную state machine и порядок долговечной записи. PREPARED intent должен переживать сбой до любой замены manifest. Утверждение включает ordering для staging, flush/commit PREPARED, замены manifest, публикации проекции и завершения/очистки записи. Для каждой границы предусмотрены fault-injection, проверка reopen и идемпотентное повторное восстановление, включая отказ во время самого recovery. Доказательство должно исключать необнаружимое расхождение manifest и каталога, а также повторную публикацию. Носитель журнала, поля, блокировка и политика восстановления остаются предметом OQ-25–28. Статус ADR остаётся Proposed. [ACR-003](../../parallel/CONTRACT_CHANGE_REQUESTS.md)

## Restricted development selection

ARCHITECT_SELECTED for the slice under TASK-AG01-08. Manifest 1.1 owns asset and source-version declarations. SQLite 2 owns publication, receipts and result provenance. WAL + FULL, a cooperating single writer and PREPARED-before-publication are selected for process-failure recovery on the documented local filesystem. See the [implemented state machine and evidence](../../PHASE_2_3_VERTICAL_SLICE.md#acr-003-process-failure-state-machine). Broader ADR status remains Proposed. Power-loss durability remains NOT VERIFIED.
