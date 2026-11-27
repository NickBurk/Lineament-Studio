# Recovery Fault-Injection Matrix

**Статус:** план проверок; исполняемые тесты не запускались.
**Протокол:** [PHASE_2_STORAGE_GATE_PROPOSAL.md](PHASE_2_STORAGE_GATE_PROPOSAL.md), ADR-0003 (Proposed), OQ-26 (Proposed).

## Harness и общий oracle

Выполнять только после отдельного принятия архитектуры. Каждый сценарий начинается с disposable project на поддерживаемом Windows/local-NTFS томе. Fault injection привязан к именованному hook. Process termination и VM power-off — разные классы evidence. Реальные пользовательские проекты не использовать.

В проекте должны быть синтетические, но реальные файлы: UTF-8 .lspx, project.sqlite, маленький GeoTIFF с известными CRS, affine transform, размерами, dtype и NoData, GeoPackage с геометрической таблицей, feature и CRS. Операция stages artifact, меняет manifest и публикует result.

После каждого fault открыть проект свежим процессом через обычный project-open path. Recovery выполняется до mutable view. Проверять exact bytes/digests, SQLite integrity_check, project identity, manifest revision/digest, catalog projection revision/digest, существование и format metadata artifacts, publication state, ровно одну result row и один видимый результат. При fail-closed ожидании проверить отсутствие записи/удаления и стабильную диагностику. Повторить recovery не менее двух раз: конечное состояние идентично, лишних results/events нет.

Записывать Windows build, filesystem/volume, SQLite version/journal/synchronous settings, fault hook, команду/harness ID, содержимое диска, reopen assertions и evidence. Process-kill подтверждает только process-crash recovery. Power-loss evidence требует disposable VM/virtual disk или контролируемого стенда.

## Fault matrix

| ID / граница | Сбой | Ожидаемое состояние и восстановление | Проверки |
|---|---|---|---|
| FI-01 создание staging directory | Process crash/power fault во время mkdir | PREPARED отсутствует; старый проект доступен. Пустой staging удаляется только под lock после проверки ссылок. | Старые manifest/catalog согласованы; результата нет; источники не менялись. |
| FI-02 запись GeoTIFF/GPKG | Убить процесс в середине записи | PREPARED нет; частичный файл не каталогизируется. | Старый revision; partial отклонён digest/driver validation; reopen успешен. |
| FI-03 flush файла | Ошибка записи/flush, включая disk full | Не переходить к PREPARED/replacement; сохранить диагностику. | Нет result и нового manifest; частичные bytes не опубликованы. |
| FI-04 read-back/digest stage | Изменить один byte после записи | Проверка останавливает операцию до PREPARED. | Файл не публикуется; старый проект без изменений. |
| FI-05 format validation | Повредить CRS/table/transform/структуру | Ошибка до PREPARED. | Реальные drivers/SQLite integrity отвергают artifact; catalog row отсутствует. |
| FI-06 temp manifest | Crash, disk full или повреждение temp | Видимый manifest старый; PREPARED нет; temp игнорируется. | Старые bytes/revision точны; reopen использует старый state. |
| FI-07 begin/insert PREPARED | SQLite busy/locked, access denied, disk full | Transaction rollback; manifest нельзя заменять. | Старое состояние; нет final artifact/result link; диагностика различает busy/I/O. |
| FI-08 PREPARED commit | Fault прямо до commit и после commit до ack | До durable commit — intent отсутствует, manifest старый. После commit — intent восстанавливается. | Отдельно проверить обе стороны; target manifest никогда не без PREPARED. Запускать по отдельности на DELETE/FULL, DELETE/EXTRA, WAL/FULL и WAL/EXTRA. До commit intent отсутствует; после commit оно только observed/committed, а physical durability NOT VERIFIED до power-loss evidence. |
| FI-09 read-after-commit | Ошибка чтения intent после успешного commit | Live process не заменяет manifest; reopen обнаруживает PREPARED и восстанавливает. | Потеря in-memory ack не теряет intent; publication_id/result_id не дублируются. |
| FI-10 после PREPARED, до ReplaceFileW | Убить процесс | Старый manifest + durable PREPARED; recovery перепроверяет и продолжает. | Intent содержит target manifest и old digest; recovery повторяем. |
| FI-11 sharing violation manifest | Открыть handle с несовместимым sharing; simulate antivirus/indexer | Старый/target bytes определяются при recovery; PREPARED остаётся; обычная запись блокируется. | Нет delete-then-rename; нет partial JSON; старые bytes сохранены. |
| FI-12 во время ReplaceFileW | Убить процесс; отдельно power-off VM на границе | Manifest должен быть целиком old или target; PREPARED ведёт recovery. Если это не подтверждается, gate не пройден на платформе. | Проверить backup/digest, JSON parse; процессные и power результаты отдельно. |
| FI-13 ReplaceFileW error/потеря ack | API error или успешная замена без ack caller | Оставить PREPARED; сверить current/backup digest; продолжить или восстановить old. | Не делать слепой повтор; одна целевая revision. |
| FI-14 manifest установлен, artifacts ещё нет | Убить процесс | Блокировать обычный view; recovery публикует проверенный stage либо возвращает old manifest и abort при невалидном artifact. | Mixed state не виден; rollback подтверждает old digest; result 0 или 1 согласно terminal path. |
| FI-15 rename artifact в final | Crash до/после каждого move; создать совпадающий и конфликтующий target | PREPARED остаётся. Совпадающий ID+digest принимается, отсутствующий перемещается, конфликт не перезаписывается. | Финальные пути/digests точны; нет overwrite. |
| FI-16 disk full при promotion | Заполнить volume после preflight | Оставить PREPARED; retry после освобождения места или rollback/abort. | Старое состояние доступно; прошлые artifacts не удаляются ради места. |
| FI-17 SQLite publication transaction | Ошибка до commit, во время inserts, после commit до ack | До commit rollback/retry; после commit recovery распознаёт rows и завершает без повторной вставки. | Unique IDs: одна строка; projection равен target revision/digest. |
| FI-18 SQLite/project lock busy | Вторая DB connection/process удерживает lock | Второй writer получает явный busy/read-only; recovery ждёт или fail-closed. | LockFileEx определяет ownership, не timestamp файла; проверить освобождение после death. |
| FI-19 SQLite I/O failure/corruption | Запретить запись, повредить копию, отдельно удалить WAL | Fail-closed; не менять manifest, не публиковать и не чистить evidence. Требуется диагностика/manual repair. | Все bytes сохранены; WAL/SHM сценарии диагностируются без ложного восстановления. |
| FI-20 crash после catalog commit до COMPLETED | Убить процесс | Recovery проверяет manifest/files/catalog и записывает completion один раз. | Один receipt, один result, один terminal success event. |
| FI-21 cleanup failure | Disk full/permission/crash при удалении stage/backup | Completed либо CLEANUP_PENDING; result остаётся валиден; cleanup повторяется. | Нельзя удалить final/source/единственный старый manifest. |
| FI-22 сбой во время recovery | Инжектировать fault на replacement/restore/move/SQLite commit/completion/cleanup | PREPARED/terminal state сохраняет информацию для следующего запуска; обычный доступ заблокирован до консистентности. | Запускать recovery минимум 3 раза с fault на разных шагах; сходится к одному result или quarantine. |
| FI-23 повтор recovery без fault | Запустить после FI-10…FI-22 несколько раз | Нет новых изменений кроме безопасной terminal/cleanup фиксации. | Bytes стабильны; нет дублированных rows/events/publication/result. |
| FI-24 повтор recovery публикации | Повторить recovery с тем же publication_id до/во время/после restart | Продолжить или разрешить ту же публикацию. | Тот же result_id и одна result row; повтор не создаёт результат. |
| FI-25 повторное вычисление Worker | Retry вычисления создаёт новый job_id по Core Contracts; последующая публикация относится к этому job. | Это новое вычисление, не recovery прежнего publication_id. | Внешний idempotency key/dedup между jobs не определён; OQ-24 остаётся OPEN. |
| FI-26 два writer процесса | Синхронно конкурировать на одной expected revision, затем разные operation IDs | Один получает lock; второй busy/re-read. Stale revision отвергается. | Нет конкурирующих PREPARED с разными публикациями; нет дублей. |
| FI-27 writer умер под lock | Убивать в каждом состоянии и запускать второй процесс | OS освобождает lock; второй сначала выполняет recovery. | Нет очистки lock по возрасту; проект восстановлен либо quarantine. |
| FI-28 manifest/SQLite mismatch без PREPARED | Вручную изменить disposable manifest/projection | Diagnostic/read-only/quarantine, без silent authority selection. | Обычные записи запрещены; обе версии сохранены. |
| FI-29 traversal/link/path attacks | ../, absolute, drive-relative, encoded traversal, symlink/junction escape, ADS, device name | Отклонить до доступа/публикации; external path разрешён только как допустимый Reference. | Внешние files не читаются/пишутся/удаляются; дополнить Unicode и длинными путями. |
| FI-30 relink/checksum drift и Copy/Reference | Missing/moved source, совпавший/изменённый digest, изменённые CRS/transform, Copy | Сохранить декларацию до явного согласия; provenance; Copy только в staging после space check. | asset_id сохраняется; исходник не меняется; после reopen результаты остаются при missing DEM. |
| FI-31 rollback manifest replace failure | Запретить восстановление old manifest после target + повреждённый artifact | Не записывать ABORTED; остаться PREPARED/quarantine с сохранёнными bytes. | Не выдавать ложное rollback; каталог не показывается как согласованный. |
| FI-32 неподдерживаемый filesystem | SMB/UNC, cloud-sync, removable/FAT/exFAT, если не заявлены | Отклонить strong-write mode или использовать только отдельно принятую слабую гарантию. | Понятная диагностика; операция не начинается вне профиля. |

## Requirement-to-evidence

| Требование | Evidence |
|---|---|
| PREPARED durable до manifest replacement | FI-08–FI-13, ordering trace, reopen после fault |
| Process crash и power-loss | Process-kill на каждой границе; отдельно VM power tests для FI-08, FI-12, FI-15, FI-17, FI-20–FI-22 |
| Idempotent recovery и однократная публикация | FI-17, FI-20–FI-25 |
| Disk full, locked files, corrupted temp, SQLite failure | FI-03, FI-06–FI-07, FI-11, FI-16, FI-18–FI-19 |
| Конкурирующие writers | FI-18, FI-26–FI-27 |
| Расхождение manifest/catalog и recovery | FI-28 и общий reopen oracle |
| Reference/Copy, relink/checksum | FI-29–FI-30 |
| Реальные GeoTIFF/GeoPackage и повторное открытие | FI-02–FI-05 и общий oracle |

Ни один сценарий не объявлен пройденным. Для принятия gate нужны реальные команды/артефакты/результаты после отдельного утверждения storage architecture.

## CHAT02 recovery consistency supplement

All rows below are **planned**, not executed. For every row, record the actual SQLite journal_mode/synchronous, VFS and Windows/filesystem environment. Test process termination separately from power interruption in a disposable VM. “Negative acceptance” means the test fails if it observes a mixed state as normal, loses the only prior manifest, silently chooses conflicting authority, duplicates a result, or deletes evidence.

| Fault point | Expected durable state | Process-crash test | Power-loss test | Recovery result and consistency | Artifact digest / repeat recovery | Negative acceptance |
|---|---|---|---|---|---|---|
| SQLite corruption before PREPARED | No intent; old manifest is sole valid entry point | Corrupt disposable DB, reopen | VM interruption during DB corruption is not a durability proof; separately test DB backup | Diagnostic/read-only; no automatic write | No new final artifacts; repeat gives same diagnostic | Fail if manifest is rewritten or lost DB history is synthesized |
| SQLite corruption after PREPARED, before manifest replacement | PREPARED may be unreadable; old manifest expected | Corrupt DB after verified intent, kill/reopen | VM fault after intent commit; report whether DB remains readable | Fail closed; no automatic replacement without readable intent | Stages preserved; repeated open does not publish | Fail if target manifest appears without recoverable intent |
| SQLite corruption after manifest replacement | Target manifest may coexist with unreadable DB | Corrupt DB after replacement, reopen | VM power fault after ReplaceFileW | Quarantine/manual repair; do not infer catalog commit | Keep old/target bytes, stage and finals; repeat preserves all | Fail if project appears consistent or files are deleted |
| SQLite corruption after artifact promotion | Some final files may be orphaned | Corrupt DB after rename, reopen | Separate VM fault after promotion | Quarantine/manual repair | Verify artifact digests; no second publication | Fail if orphan auto-registered without proof or removed |
| Manifest corruption with intact SQLite | DB may or may not contain valid PREPARED | Corrupt manifest before reopen | VM fault during manifest write/replacement | Restore only from validated durable target/old bytes; otherwise read-only repair | Verify restored digest; repeat converges | Fail if arbitrary catalog row is used to invent manifest fields |
| Manifest and SQLite both corrupt | No trusted coordination state | Corrupt both disposable copies | VM power fault followed by deliberate dual corruption test | Unavailable/quarantine; manual backup path | Preserve spatial payloads and all candidate files | Fail if system claims automatic recovery or deletes data |
| ReplaceFileW returns error | API outcome may be ambiguous | Inject error and inspect current/replacement/backup | VM interruption at same boundary | Classify only by exact old/target digests; retain PREPARED | Verify one known-good manifest; repeat same classification | Fail if delete-then-rename or blind retry occurs |
| Lock owner process exits | OS releases handle lock, not lock-file path | Kill writer then bounded retry by second writer | Power loss naturally drops process/handle; still validate files on reopen | Second writer acquires then recovers before write | Same publication identity; no stale-lock deletion | Fail if lock file is deleted as unlock mechanism |

For SQLite PREPARED, run this boundary suite separately for DELETE/FULL, DELETE/EXTRA, WAL/FULL and WAL/EXTRA. Record actual xSync/VFS behavior and hardware assumptions. A successful process-crash run does not count as power-loss evidence. No configuration passes by documentation alone.
