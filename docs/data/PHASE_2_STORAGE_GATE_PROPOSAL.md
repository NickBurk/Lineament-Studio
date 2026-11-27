# Phase 2 Storage Gate Proposal

**Статус:** предложение на рассмотрение; архитектурное решение не утверждено.
**База:** eab8396dc358ccf888b5ade00e5a76553c1fc602.
**Связанные документы:** ADR-0001 (Accepted), ADR-0003 (Proposed), OQ-25 (Proposed), OQ-26 (Proposed), OQ-27 (Open), OQ-18.

Этот документ не утверждает ADR-0003, не закрывает OQ-25–27 и не разрешает Phase 2 implementation. Принятые изменения должны пройти Architecture/Contract Change Request и review Agent01/владельца проекта. Статусы вопросов остаются без изменений.

## 1. Цель и ограничения

Проект — каталог с UTF-8 JSON manifest project.lspx, SQLite project.sqlite и spatial files. Manifest является точкой входа; SQLite — каталогом и хранилищем транзакционных метаданных; GeoPackage хранит векторы, GeoTIFF/COG — растры. Reference и Copy выбираются пользователем. Исходный DEM нельзя скрытно перемещать или перезаписывать; backup остаётся ручным согласно DEC-U13.

Единица записи — логическая мутация проекта: публикация проверенного набора неизменяемых staged artifacts, обновление manifest и SQLite projection, создание единственного результата операции. Нет общей атомарной транзакции через SQLite, NTFS и произвольные пространственные файлы. Начальная гарантия предлагается только для одного каталога проекта на поддерживаемом локальном томе; сетевые, синхронизируемые и разные тома требуют отдельных решений.

Термины:

- **Asset record:** identity и метаданные входного или производного ресурса.
- **Manifest authority:** источник истины для identity проекта, конфигурации и пользовательских source declarations.
- **SQLite projection:** индекс этих значений с revision/digest исходного manifest.
- **Operation:** стабильный UUID и digest запроса для дедупликации и повторов.
- **PREPARED:** долговечная запись восстановления, созданная до любой замены manifest.

## 2. Data Ownership: варианты и последствия

| Вариант | Источник истины | Преимущества | Последствия и риски |
|---|---|---|---|
| A. Manifest владеет пользовательскими источниками; SQLite — каталогом производных/операционных данных (предлагается) | Manifest: project identity, конфигурация, source asset IDs, режимы и URI. SQLite: jobs, experiments, results, events и реляционные индексы. Копии manifest-owned полей в SQLite — revision-tagged projection. | Сохраняет направление текущих спецификаций; manifest остаётся читаемой точкой входа; каталог остаётся реляционным. | Каждое изменение manifest-owned поля проходит единый протокол. Несовпадение требует recovery или диагностики; независимые правки копий запрещены. |
| B. SQLite владеет всеми asset records, manifest содержит identity/config/catalog pointer | Только SQLite. | Единая транзакционная модель каталога. | Противоречит текущему контракту assets в manifest; нужен ACR, миграция и решение о работе при повреждённой/отсутствующей БД. |
| C. Manifest владеет всеми asset records, SQLite — полностью перестраиваемый индекс | Manifest. | Проще inspect/copy без специальных инструментов. | Большой manifest, конкурирующие записи, медленные выборки и дополнительная система для jobs/events. |
| D. SQLite владеет данными, manifest — материализованный snapshot | SQLite, manifest обновляется после commit. | Обычная DB-first projection. | Crash после DB commit оставляет stale entry point; recovery всё равно нужен; меняет заявленную роль manifest. |

**Предложение для review:** вариант A, без утверждения. Agent01/владелец должны подтвердить владение по полям; иной вариант требует контрактного изменения до схемы/кода.

### 2.1 Предлагаемое владение полями

| Данные | Источник истины | Проекция | Рассогласование |
|---|---|---|---|
| project_id, project CRS, storage policy, defaults, catalog URI | Manifest | SQLite Project row | Сначала recovery; необъяснённое расхождение блокирует запись и открывает diagnostic/read-only режим. |
| Source asset ID, Reference/Copy, URI, checksum, захваченные метаданные | Manifest | SQLite Asset rows | Сверить manifest revision и digest. Если intent отсутствует и manifest валиден, projection можно транзакционно перестроить из manifest с audit event. |
| Jobs, experiments, operation receipts, event log, производные asset records | SQLite | Неизменяемые JSON snapshots и файлы | SQLite владеет индексами/связями; payload snapshot проверяется digest. |
| Геометрии и пространственные атрибуты | GeoPackage | SQLite URI/table/checksum/CRS/bounds | GPKG — источник payload; каталог ссылается после валидации. |
| Raster payload | GeoTIFF/COG либо внешний Reference | SQLite metadata; manifest для source declaration | Проверять digest и геометаданные; исчезновение DEM не удаляет результаты. |
| Experiment inputs/parameters/provenance | Неизменяемый experiment JSON snapshot | SQLite ссылки и индексы | JSON snapshot — авторитетный run record; каталог проверяется по digest. |
| Independent Annotation Set | Версионированные данные набора | SQLite metadata/index | Импорт не затирает другой набор по имени; merge — явный новый derived set. |

Стабильный project_id не меняется. Предлагается монотонный manifest_revision, начиная с 1, и digest точных установленных UTF-8 байтов manifest. Перед записью caller передаёт expected_revision и expected_digest; сравнение выполняется под lock. Несовпадение — stale-writer conflict, не автоматическое слияние.

При открытии recovery выполняется до обычных запросов каталога. Затем сравниваются project identity/revision/digest. Если projection устарела, но нет незавершённого intent, допускается её восстановление из валидного manifest с audit event. При конфликте project_id, неизвестном advancement или невалидном manifest автоматический выбор запрещён: открыть диагностический режим и сохранить обе копии.

## 3. Предложенный durable publication protocol

### 3.1 Варианты журнала

Предпочтительный кандидат — PREPARED row в project.sqlite, зафиксированный до замены manifest. Intent и финальная публикация каталога используют один транзакционный движок; между SQLite, manifest и файлами остаётся recovery-протокол, а не distributed atomic commit.

1. **Sidecar journal:** независим от SQLite и помогает при недоступности DB, но требует отдельной гарантии долговечной записи/создания файла, синхронизации с DB и добавляет вторую систему состояния.
2. **SQLite intent (предлагается):** один источник operation state и catalog commit; при повреждённой SQLite автоматическое recovery невозможно, поэтому проект fail-closed.
3. **Manifest-first или одна SQLite transaction без intent:** не обеспечивает долговечного намерения до межфайлового изменения и для этого gate отклоняется.

### 3.2 State machine и intent

Состояния: STAGING (временное, не опубликовано), PREPARED (durable intent committed), MANIFEST_INSTALLED (определяется проверкой digest), CATALOG_COMMITTED (projection/result transaction committed), COMPLETED (durable receipt), CLEANUP_PENDING (результат завершён, остатки не удалены), ABORTED (старый manifest подтверждён, результат не публиковался).

Intent хранит минимум:

- operation_id UUID, уникальный idempotency_key, canonical request_digest;
- project_id, expected revision/digest, target revision/digest;
- полные новые manifest bytes (или immutable prepared file с проверенными length/digest), старые bytes/digest для rollback;
- список artifacts: asset/result IDs, stage path, final relative path, length, digest, type и validation summary;
- publication/cleanup progress и terminal outcome.

Если prepared manifest хранится отдельным файлом, его содержимое и directory entry должны быть durable до SQLite PREPARED commit. Temp path сам по себе этого не обеспечивает. Выбор способа хранения — решение ACR/ADR.

### 3.3 Упорядоченные шаги

1. **Lock и precondition.** Открыть постоянный project lock file, взять эксклюзивный byte-range lock через Windows LockFileEx и удерживать handle до конца записи/recovery. Наличие файла не означает, что он залочен. Под lock проверить project_id, expected revision/digest. Читатели ждут recovery либо входят в явно диагностический read-only режим.
2. **STAGING.** Писать артефакты в уникальный operation-scoped каталог на том же томе, что и конечные пути. Опубликованные файлы неизменяемы; источники Reference доступны только для чтения.
3. **Flush и проверка staging.** Закрыть GDAL/SQLite/file handles; выполнить FlushFileBuffers; проверить длину, digest и read-back. Для GeoTIFF проверить открытие, CRS, transform, размеры, dtype, NoData, bands; для GPKG — SQLite integrity и таблицы/геометаданные. Использовать документированную Windows/filesystem процедуру для durability directory entries. Если порядок нельзя подтвердить, strong guarantee не заявлять.
4. **Prepare manifest.** Сформировать новую revision без изменения project_id; сериализовать детерминированный UTF-8 JSON; провалидировать schema; записать temp в том же каталоге; FlushFileBuffers, перечитать и проверить digest. Сохранить старые bytes/digest для восстановления. Текущий manifest пока не трогать.
5. **Durable PREPARED.** SQLite BEGIN IMMEDIATE; вставить operation/artifact/manifest intent со статусом PREPARED и уникальными operation/result IDs; commit с явными PRAGMA synchronous=FULL и заранее выбранным journal mode. Проверить read-after-commit и digest intent. До успешного commit и проверки вызов замены manifest запрещён. При ошибке — не заменять manifest и не публиковать файлы.
6. **Atomic manifest replacement.** Для существующего manifest использовать same-volume Windows ReplaceFileW с сохранением восстанавливаемой старой версии; создание первого manifest — same-volume rename с отдельно проверенной семантикой. Повторно открыть и проверить digest. При ошибке/неоднозначном результате оставить PREPARED и проверять старый/новый/backup digest; не делать delete-then-rename.
7. **Artifact promotion и SQLite projection.** Переместить staged immutable artifacts в детерминированные result paths тем же томом без перезаписи. Существующий target допустим только при полном совпадении ID и digest. Затем одна SQLite transaction проверяет PREPARED и старую revision, обновляет projection, вставляет result references с уникальными operation/result IDs, пишет success event и меняет статус на CATALOG_COMMITTED. Читатель не видит частичные строки.
8. **Завершение.** Следующей SQLite transaction отметить COMPLETED и сохранить receipt. Точный повтор operation/request возвращает тот же receipt; тот же key с другим request digest — conflict. Не вычислять и не публиковать результат повторно.
9. **Cleanup.** Только после durable COMPLETED и проверки согласованности удалять staging debris/старый manifest backup. Ошибка cleanup оставляет CLEANUP_PENDING; результат не откатывается. Cleanup повторяем и не касается исходников/shared artifacts.

### 3.4 Восстановление

Перед обычным открытием: получить эксклюзивный lock; прочитать operation rows; обработать все nonterminal intents по порядку; проверить manifest/catalog identity и digest; затем разрешить обычный доступ. При ошибке recovery блокирует запись и сохраняет все кандидаты.

| Intent | Manifest на диске | Файлы | Действие recovery |
|---|---|---|---|
| Нет | Старый digest | Может быть stage | Удалить только после доказательства отсутствия PREPARED/catalog reference под lock. Старое состояние остаётся доступным. |
| PREPARED | Старый digest | Stage валиден | Перепроверить stage/manifest; установить manifest; продвинуть artifacts; commit projection/results; завершить. |
| PREPARED | Target digest | Stage или совпадающий final | Продолжить публикацию/commit; повторно manifest не заменять. |
| PREPARED | Старый digest | Stage повреждён/отсутствует, target отсутствует | Подтвердить старый manifest, записать ABORTED, результат не создавать; оставить диагностику. |
| PREPARED | Target digest | Обязательный artifact невозможно восстановить | Восстановить старый manifest из durable bytes/backup, проверить старый digest; оставить старый catalog; ABORTED. При неудаче — quarantine. |
| PREPARED | Не старый и не target digest | Любые | Ничего не перезаписывать; сохранить файлы/БД/backup; блокировать обычный доступ. |
| CATALOG_COMMITTED/COMPLETED | Target digest | Совпадающие artifacts | Проверить и завершить/cleanup idempotently. Отсутствующий committed artifact — integrity failure, не подмена другим payload. |
| Nonterminal | SQLite недоступна/повреждена | Любые | Fail-closed: не менять manifest, не удалять файлы; diagnostic/manual repair. |

Инварианты:

1. PREPARED commit и read-after-commit предшествуют единственному пути вызова manifest replacement. Проверки непосредственно до/после commit и вокруг replacement должны доказать: после fault либо старый manifest, либо доступный durable intent.
2. Результат виден только после catalog transaction и согласования manifest/catalog revision.
3. Уникальность operation/result ID исключает повторную публикацию при replay.
4. Конечные пути валидируются, relative, same-volume; existing target не перезаписывается без точного совпадения.
5. Неопределённое состояние блокирует запись; никакого silent choice между конфликтующими копиями.
6. Исходники неизменяемы; удаление — отдельный внерамочный протокол.

## 4. Windows: границы гарантий

Одна транзакция не может атомарно охватить SQLite, NTFS namespace и множество spatial files. Гарантия основана на durable intent и идемпотентном recovery.

- **Process crash и power loss различны.** FlushFileBuffers запрашивает запись буферизованных данных, но фактическая гарантия зависит от filesystem, контроллера, устройства, драйвера и соблюдения flush-команд аппаратурой. Нужны отдельно документированные предположения и power-fault evidence. Успешный process-kill тест не доказывает power-loss durability.
- **SQLite:** зафиксировать/проверять journal mode (DELETE или WAL) и synchronous=FULL; не полагаться на defaults. В WAL учитывать WAL/SHM и восстановление/копирование БД. Проверить Windows VFS на поддерживаемом локальном NTFS. SMB/removable пока не покрыты.
- **ReplaceFileW:** same-volume replacement даёт атомарную видимость namespace для readers, но сама по себе не доказывает power-durable directory metadata. Сохранять старую версию; тестировать sharing violations, antivirus/indexer, ACL, read-only и replacement errors. Не делать delete-then-rename.
- **Directory entries/rename:** нет универсального portable directory fsync с идентичными гарантиями на всех Windows filesystems. Документировать точные APIs и проверить порядок durable directory entries. Если гарантия не доказана — отключить strong mode или вернуться к ACR, не утверждать, что успешный rename flush-ит каталог.
- **Locking:** SQLite locks плюс эксклюзивный LockFileEx project lock. OS снимает lock после смерти процесса; возраст lock file не является доказательством stale ownership. Проверить busy/read-only поведение.
- **Disk full / open handles:** preflight свободного места лишь advisory. Ошибка на любой записи/flush/commit/replace/move оставляет intent и данные для recovery. Закрывать GDAL/file handles; при sharing violation не удалять/обнулять target.
- **Filesystem scope:** кандидат гарантии — локальный NTFS, один том для staging/final/manifest и storage stack, который соблюдает flush. FAT/exFAT, UNC/SMB, cloud-sync и removable volume требуют проверок и могут быть отклонены.

## 5. Предлагаемый контракт manifest .lspx

Это schema proposal. Текущие документы используют schema_version для SQLite, поэтому введение отдельного manifest schema version или переименование поля требует contract review.

| Поле | Тип и nullability | Предлагаемое правило |
|---|---|---|
| format_id | обязательная непустая строка | org.lineament-studio.project |
| format_version | обязательная строка major.minor | Неподдерживаемый major отклоняется до записи; точная политика требует OQ-27. |
| schema_version | обязательная строка | Версия SQLite schema, не версия manifest. |
| project_id | обязательный UUID | Не меняется при операциях. |
| manifest_revision | предлагаемое обязательное положительное целое | CAS revision; новое поле требует контракта. |
| application_version | обязательная строка | Версия producer. |
| created_at, modified_at | обязательный UTC RFC 3339 timestamp | UTC с Z или явным offset. |
| project_crs | обязательная строка или null | Null только при отсутствии объявленной CRS; не выводить молча. |
| storage_policy | обязательный enum | reference, copy или mixed; должен согласоваться с asset modes. |
| catalog_uri | обязательная строка URI/path | По умолчанию relative внутри проекта с containment check. |
| assets | обязательный массив | Может быть пустым; уникальные asset IDs. |
| default_profiles | обязательный object | Пустой допустим; значения проверяются версионированной схемой. |

**Неизвестные поля:** предлагается strict validation в рамках заявленной schema version, чтобы ловить typo и неоднозначность. Расширение требует новой явно совместимой версии и fixtures. Старый reader не переписывает неизвестные поля и не мутирует неподдерживаемую major. Forward/minor tolerance решить через OQ-27 до реализации.

Каждый asset предлагает поля:

- asset_id: обязательный уникальный UUID, сохраняется при relink;
- role: обязательная bounded enum/string с версионированным registry;
- storage_mode: обязательный reference или copy; mixed — только политика проекта;
- uri: обязательная строка, грамматика зависит от режима;
- checksum: обязательное поле, nullable только для явно incomplete/import state; опубликованный asset требует digest, кандидат SHA-256;
- format: обязательная строка для валидированного asset;
- crs, width, height, band_count, dtype, nodata, transform, pixel_size, extent: поля обязательны/nullable по типу asset; raster validation требует фактических значений; NaN NoData кодируется стандартно, без JSON NaN;
- source_uri, captured_at, license: provenance, nullable; секреты запрещены.

**Path/URI предложение:** Copy хранит нормализованный project-relative POSIX-style путь без root/drive и проверяет containment после canonicalization. Reference сохраняет canonical URI; локальный Windows пример — file:///C:/... с percent encoding; UNC — явно согласованная file://server/share/... грамматика. Drive-relative C:folder\file invalid. Предлагается запретить relative Reference URI из-за неоднозначной базы, но это вопрос OQ-27.

Нормализовать Unicode identifiers/relative paths в NFC; для внешних Windows путей сохранить нужное исходное написание отдельно. Не сравнивать Windows пути простым case-sensitive string equality. Однократно декодировать URI; отклонять NUL, неоднозначные encoded separators, . / .. traversal, alternate data streams, reserved device names и выход из project root. Разрешить symlink/junction до containment; по умолчанию запретить внутренний путь, указывающий наружу. Внешний абсолютный путь допускается только явно как Reference. Не читать URI до валидации scheme/root/policy и не принимать произвольные сетевые схемы.

Relink сохраняет asset_id; provenance фиксирует old/new URI, checksum, время, источник/actor и результат проверки. Совпадение checksum не отменяет проверку format/CRS/dimensions/transform. Несовпадение требует явного выбора пользователя.

**Совместимость:** валидировать encoding, размер/depth, duplicate JSON keys, IDs/timestamps/enums/paths до открытия внешних данных. Неподдерживаемые format/schema major отклоняются до mutation; diagnostic read-only допустим. Миграция явная, версионированная и журналируемая; сохраняет исходные manifest/DB и пользовательские данные до проверки результата. Никакого silent field dropping и destructive migration.

## 6. Предложения по OQ-25–27 (статусы сохраняются)

| OQ | Предлагаемое закрытие | Evidence до решения владельца |
|---|---|---|
| OQ-25 — владелец asset records/projection | Вариант A, field ownership из §2.1, stable asset_id/project_id, revision и digest точных manifest bytes, fail-closed reconciliation. | ACR на таблицу владения; schema fixtures для rebuild/mismatch; доказать, что stale SQLite не затирает source declaration. Оставить PROPOSED. |
| OQ-26 — publish/recovery/concurrency | State machine §3; committed SQLite PREPARED и read-after-commit до replacement; ReplaceFileW; immutable same-volume artifacts; unique operation/result IDs; эксклюзивный OS lock; recovery до normal open. | Полная fault matrix из RECOVERY_FAULT_MATRIX.md; Windows NTFS evidence на каждой границе; power-fault ограничения; replay/retry/two-writer/DB-failure tests. Оставить PROPOSED. |
| OQ-27 — schema/path/version contract | §5 nullable/required contract; strict unknown fields per version; запрет silent forward rewrite; URI/path containment. | Решить manifest schema vs SQLite schema_version, minor/forward compatibility, relative Reference, UNC, symlink/junction, nullable fields и checksum migration. Добавить schema/round-trip/security fixtures. Оставить OPEN. |

## 7. Gate и тестовая стратегия после отдельного принятия

Не начинать Phase 2 по одному этому proposal. После принятия:

1. Зафиксировать schema и transaction record в reviewed ADR/contracts.
2. Создать disposable Windows/local-NTFS harness с fault hooks для каждой строки fault matrix.
3. Генерировать реальные синтетические fixtures: .lspx JSON, project.sqlite, GeoTIFF с известными CRS/transform/dtype/NoData и GeoPackage с известной таблицей/геометрией/CRS.
4. После каждого fault открыть проект обычным open path в свежем процессе. Проверить format-specific validity, digest, project_id, manifest/catalog revision и digest, видимые results и единственный operation receipt.
5. Отдельно тестировать process kill и power interruption в disposable VM/virtual disk. Process kill нельзя объявлять доказательством power-loss.
6. Проверить no space, sharing violation, damaged temp, SQLite busy/corrupt/read-only. Ни один сценарий не удаляет единственную good copy.
7. Replay: тот же operation/request возвращает тот же receipt; тот же key с другим digest — conflict; два writer не публикуют два результата; повтор recovery сходится к тем же bytes и одному result.

Gate требует passing process-crash tests, явно ограниченного power-loss evidence и отсутствия необъяснённого manifest/catalog mismatch. Этот документ задаёт проверки, но исполняемых тестов в архитектурном scope нет.

## 8. Риски и вопросы владельцу

- SQLite предлагается anchor для intent; при её повреждении автоматическое recovery блокируется. Нужно ли независимое sidecar journal — решение владельца.
- Flush и power-loss обещания зависят от hardware; перечислить поддерживаемые filesystems/devices и evidence.
- ReplaceFileW не доказывает durable directory metadata. При недостаточном evidence вернуться к ACR, не вводить альтернативный механизм самовольно.
- UNC/network/cloud-synced roots и несколько томов не покрыты.
- Неоднозначность schema_version и forward compatibility требует OQ-27.
- Locking, projection, receipts и manifest_revision — контрактные изменения; Agent01 и владелец утверждают до реализации.
