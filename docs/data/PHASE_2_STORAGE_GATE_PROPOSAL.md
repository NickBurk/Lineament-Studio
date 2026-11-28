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
- **job_id:** UUID вычислительного задания согласно Core Contracts.
- **publication_id:** предлагаемый внутренний UUID одной долговечной публикации уже созданных artifacts.
- **result_id:** UUID опубликованного результата.
- **Committed PREPARED:** intent committed SQLite transaction и видим через согласованное чтение; это не доказательство power-loss durability.
- **Required durability:** требование пережить поддерживаемый класс отказов до замены manifest.
- **Verified durability:** требование подтверждено испытаниями точной конфигурации; сейчас NOT VERIFIED.

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

Состояния протокола публикации (не новые Core Lifecycle states): STAGING (подготовка, не опубликовано), PREPARED_COMMITTED (SQLite transaction committed и intent читаем; physical durability NOT VERIFIED), MANIFEST_INSTALLED (bytes совпадают с target digest), CATALOG_COMMITTED (projection/result transaction committed), COMPLETED (publication terminal state), CLEANUP_PENDING (публикация завершена, cleanup остался), ABORTED (старый manifest подтверждён, result не виден). Required durability остаётся обязательным; Verified durability отсутствует до испытаний.

Intent хранит минимум:

- publication_id UUID, canonical publication-request digest; job_id и result_id — отдельные значения/ссылки; внешний idempotency key не вводится без решения OQ-24;
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
5. **Commit PREPARED.** SQLite BEGIN IMMEDIATE; записать intent со статусом PREPARED_COMMITTED и publication_id/result_id; commit с candidate profile. Read-after-commit подтверждает только наблюдаемую committed запись, не физическую долговечность. Перед заменой manifest требуется Verified durability для поддерживаемого класса отказов; сейчас она NOT VERIFIED, поэтому production replacement не разрешён до испытаний и решения владельца. До успешного commit и проверки вызов замены manifest запрещён. При ошибке — не заменять manifest и не публиковать файлы.
6. **Atomic manifest replacement.** Для существующего manifest использовать same-volume Windows ReplaceFileW с сохранением восстанавливаемой старой версии; создание первого manifest — same-volume rename с отдельно проверенной семантикой. Повторно открыть и проверить digest. При ошибке/неоднозначном результате оставить PREPARED и проверять старый/новый/backup digest; не делать delete-then-rename.
7. **Artifact promotion и SQLite projection.** Переместить staged immutable artifacts в детерминированные result paths тем же томом без перезаписи. Существующий target допустим только при полном совпадении ID и digest. Затем одна SQLite transaction проверяет PREPARED и старую revision, обновляет projection, вставляет result references с уникальными operation/result IDs, пишет success event и меняет статус на CATALOG_COMMITTED. Читатель не видит частичные строки.
8. **Завершение.** Следующей SQLite transaction отметить COMPLETED и сохранить receipt. Повтор recovery по тому же publication_id продолжает ту же публикацию и не создаёт второй result_id. Внешняя receipt/idempotency-key семантика этим proposal не задаётся.
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

1. Committed PREPARED и читаемый intent предшествуют единственному пути replacement. Это не равно durability. Требование durability не снимается; Verified durability сейчас NOT VERIFIED, поэтому production replacement не разрешён до профильно привязанных испытаний.
2. Результат виден только после catalog transaction и согласования manifest/catalog revision.
3. Уникальность operation/result ID исключает повторную публикацию при replay.
4. Конечные пути валидируются, relative, same-volume; existing target не перезаписывается без точного совпадения.
5. Неопределённое состояние блокирует запись; никакого silent choice между конфликтующими копиями.
6. Исходники неизменяемы; удаление — отдельный внерамочный протокол.

## 4. Windows: границы гарантий

Одна транзакция не может атомарно охватить SQLite, NTFS namespace и множество spatial files. Гарантия основана на durable intent и идемпотентном recovery.

- **Process crash и power loss различны.** FlushFileBuffers запрашивает запись буферизованных данных, но фактическая гарантия зависит от filesystem, контроллера, устройства, драйвера и соблюдения flush-команд аппаратурой. Нужны отдельно документированные предположения и power-fault evidence. Успешный process-kill тест не доказывает power-loss durability.
- **SQLite:** зафиксировать/проверять journal mode и synchronous согласно выбранной после испытаний комбинации из S-01; не полагаться на defaults. В WAL учитывать WAL/SHM и восстановление/копирование БД. Проверить Windows VFS на поддерживаемом локальном NTFS. SMB/removable пока не покрыты.
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

## 9. CHAT02 consistency revisions (proposals only)

### S-01. SQLite durability matrix

SQLite commit semantics depend on journal mode, synchronous level, VFS, OS/filesystem, and the storage device. A successful API return does not overcome a VFS/device that fails to honor flush requests. The following is SQLite's documented behavior, not a durability guarantee for the combined manifest/files protocol.

| Journal / synchronous | Commit and sync behavior | Process crash | Power-loss behavior/limits |
|---|---|---|---|
| DELETE / FULL | Rollback journal and database synchronization are performed through VFS xSync as required for rollback commit. | SQLite recovery handles an interrupted transaction when VFS operations behave as specified. | SQLite labels rollback-mode FULL “maybe not durable”: the journal unlink/directory update at commit may be lost, so the last commit may roll back (database should not be corrupt). |
| DELETE / EXTRA | FULL plus sync of the directory containing the rollback journal after unlink. | As DELETE/FULL. | Addresses the documented post-unlink window; remains dependent on VFS, filesystem and hardware honoring sync. Not an absolute device-failure guarantee. |
| WAL / FULL | WAL is synchronized at each commit; database synchronization occurs at checkpoint through VFS. | Committed WAL frames are recovered when DB/WAL are present. | SQLite documents WAL/FULL as ACID when VFS/device semantics hold. It does not make manifest replacement or spatial files part of that transaction. |
| WAL / EXTRA | EXTRA is equivalent to FULL in WAL mode. | As WAL/FULL. | No additional directory sync benefit over FULL. Same VFS/device limitations. |

FULL invokes VFS xSync on files required by the selected journal protocol. EXTRA adds directory sync after rollback journal unlink in DELETE mode; in WAL it makes no difference. Actual Windows guarantees depend on the SQLite VFS implementation, filesystem, drivers/controller and volatile write cache honoring flushes. Do not claim that SQLite syncs arbitrary Windows metadata or other files. Read back the effective journal_mode and configure/read back synchronous on each relevant connection. Do not select a final configuration here. Compare DELETE/EXTRA and WAL/FULL on supported Windows and SQLite versions with process termination, controlled VM power interruption, recovery checks, VFS sync evidence and DB/WAL lifecycle checks. Owner decides after evidence.

Official sources: [SQLite PRAGMA synchronous and journal_mode](https://www.sqlite.org/pragma.html#pragma_synchronous), [Atomic Commit](https://www.sqlite.org/atomiccommit.html), [Powersafe Overwrite](https://www.sqlite.org/psow.html), [VFS I/O methods and xSync](https://www.sqlite.org/c3ref/io_methods.html).

### S-02. Retry and identity boundaries; OQ-24 remains OPEN

The current API Contracts/ADR-0002 require a new UUID for retrying a Worker job. They do not define publication idempotency keys. These identities must remain distinct:

| Identity | Meaning and proposed lifecycle |
|---|---|
| job_id | Existing wire UUID for one accepted Worker execution. A new computation retry uses a new job_id as API Contracts specifies. No wire change here. |
| publication_id / operation_id | Internal storage ID for publishing already-created artifacts. Recovery repeats this same ID; it does not rerun the Worker. |
| result_id | Stable identity of a published result/artifact group; unique in the catalog and not duplicated by recovery. |
| idempotency key | Not currently part of the contract. Adding one requires decisions on scope, retention, canonical request digest, receipt replay and key reuse conflicts. |

Options: A) new job_id per computation retry, deduplicate only the same internal publication_id; B) add a later application/storage command key whose same-key/same-digest retry returns the existing receipt and changed-digest retry conflicts; C) derive result identity from job_id. A best matches current contract but cannot deduplicate distinct jobs from one user intent. B changes a shared contract. C may wrongly conflate fresh computation retries. Proposal: A at storage boundary and defer external receipt/key semantics. Not approved.

After process crash, a Worker transport failure is not proof that publication did or did not commit; inspect durable project state before retry. API currently directs computation retry to a new UUID. If a prior result is already cataloged, do not publish it again. Recovery repeats the same publication_id/result_id and is idempotent. OQ-24 stays OPEN; no Core API or wire protocol changes are made here.

### S-03. Asset-record ownership reconciliation

| Entity | Authoritative data (proposal) | SQLite projection/index | Immutable payload | Recovery metadata |
|---|---|---|---|---|
| Project identity | Manifest project_id | Project row | — | Old/target manifest bytes, revision and digest |
| Project configuration | Manifest CRS, defaults, storage policy and catalog location | Revision-tagged fields | — | Expected/target revision |
| Source declarations | Manifest role, mode, URI, declared checksum and captured metadata | SourceAsset query projection, not permission to rewrite declaration | External source or copied original bytes | Copy stage, digest and validation; relink provenance |
| SourceAsset | Manifest declaration owns identity/location; file is external or copied | Query/availability cache | Source raster/vector | Staging path and digest when copying |
| Derived assets | SQLite owns post-publication identity/registration | Authoritative result/asset relationship | GeoTIFF/GPKG/etc. | Publication ID, target, digest and state |
| Jobs | SQLite owns persisted lifecycle; wire job_id identifies execution | Job/event indexes | Optional logs/snapshot | Observed terminal state and publication link |
| Experiments | SQLite identity/state; experiment JSON is immutable reproducibility snapshot | Search references | Experiment JSON and outputs | Digests and input references |
| Results | SQLite result_id and publication state | Authoritative visible-result relation | Immutable artifact payload | PREPARED/promotion/terminal state |
| Events | SQLite append-only committed events | Event index | Optional export | Transaction/publication link |
| Artifact metadata | Catalog owns derived metadata; manifest owns declared source metadata | Indexed values with origin/revision | File contains payload | Expected length/digest/format checks |

This proposes a reconciliation between broad SQLite catalog ownership in DATA_MODEL and manifest source declarations/projected SQLite fields in ADR-0003. Option A preserves manifest authority for source declarations; option B makes SQLite authoritative for all SourceAssets and requires changing the manifest contract; option C puts every asset record in manifest and makes SQLite rebuildable, with query and manifest-size costs. No option is selected. Agent01/owner must decide. ADR-0003 and DATA_MODEL are not changed.

### S-04. SQLite corruption cases

| Failure point | Availability and automatic recovery | Prior manifest | Artifact state | Repeat/fail-safe behavior |
|---|---|---|---|---|
| SQLite corrupt before PREPARED | Diagnostic/read-only only if manifest independently validates; no writes. Projection rebuild is not safe if lost DB history is needed. | Current manifest retained. | No committed new artifact; staging may exist. | Preserve DB copy; manual repair/restore; do not infer missing events. |
| SQLite corrupt after PREPARED, before manifest replacement | SQLite-only intent cannot be trusted/read; do not replace manifest or infer commit. | Old likely remains; validate and preserve. | Staged files remain unadvertised. | No automatic resume; quarantine and retain evidence. |
| SQLite corrupt after manifest replacement | Target manifest may be installed, but intent/projection unavailable. Block normal access. | Previous bytes should be in verified recovery metadata/backup. | Stage/final artifacts may exist; visibility unknown. | No automatic resolution using SQLite-only journal; preserve all candidates for repair. |
| SQLite corrupt after artifact promotion | Commit status cannot be known. | Preserve prior copy. | Files may be orphaned; never delete/re-publish blindly. | Fail closed; manual recovery absent independent accepted journal. |
| Manifest corrupt, SQLite intact | Reconstruct only when a valid durable PREPARED record supplies exact target bytes/digest; otherwise no authority choice. | Restore only from verified bytes/backup. | Preserve and validate all artifacts before exposure. | Repeat only against the same verified record; else diagnostic repair. |
| Manifest and SQLite both corrupt | Project unavailable for normal use; automatic recovery unjustified. | Use only separately validated backup/journal copy. | Preserve all artifacts. | Quarantine/manual backup recovery; never synthesize manifest or delete data. |

SQLite-only journal is simpler and avoids two journals, but DB corruption prevents automatic recovery. A sidecar might preserve intent through DB corruption only if its own durable write, namespace ordering, checksum, locking and reconciliation protocol is designed/tested; it introduces disagreement between journals. Both remain owner options; no sidecar choice is made.

### S-05/S-06. ReplaceFileW and LockFileEx details

ReplaceFileW replacement/backup names must be on the same volume. The backup name receives displaced original content on successful replacement; it is not a transaction coordinator. Before retry, inspect existence and digests of current, replacement and backup. After API failure, treat state as ambiguous until those paths are checked; never delete a candidate or assume the old file is intact. Preserve prior manifest bytes in durable recovery metadata too. Verify exact old/target digest after the call. Atomic reader visibility differs from directory-entry durability after power loss. REPLACEFILE_WRITE_THROUGH is not proof of durability.

Every project writer, recovery tool and repair tool must use the same exclusive LockFileEx range. Acquire before writable DB access and hold through recovery/publication. Read-only readers wait or return busy while recovery is active; only expose normal reads once consistency is verified. Process termination closes handles and Windows releases locks, but retry acquisition with bounded backoff to handle close/scheduling delay. Report busy rather than deleting a lock file; the file is persistent and its existence is not ownership. UNC/network/cloud-sync locking is outside the proposal until tested.

### S-07. Manifest contract details (OQ-27 stays OPEN)

Propose checksum required for completed Copy and published derived assets. A Reference may have null checksum if unavailable/not calculated, paired with explicit validation status/reason; absence is not evidence of identity. Relative paths are proposed only for Copy/internal assets anchored to project root. Reference should use explicit absolute file URI unless a stable relative base is separately accepted. Normalize separators for internal serialized paths and reject Windows drive-relative paths. NFC for serialized identifiers and internal paths, but do not silently alter external filename lookup. Resolve symlink/junction and other reparse points before containment checks; reject a supposedly internal target escaping project root. Unknown fields, nullable rules and forward compatibility remain undecided; an older reader must never silently discard and rewrite unsupported fields. Define manifest schema version separately from, or unambiguously alongside, SQLite schema_version before implementation. OQ-27 remains OPEN.
