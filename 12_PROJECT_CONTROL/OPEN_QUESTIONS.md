# Open Questions and Technical Validation

Владелец готовит evidence и предлагает решение. До подтверждения владельцем или пользователем
статусы OPEN и PROPOSED сохраняются. Фазы указаны по [Phase Breakdown](../11_DEVELOPMENT/PHASE_BREAKDOWN.md).

| ID | Открытое решение | Статус | Владелец | Когда и чем закрыть |
|---|---|---|---|---|
| OQ-01 | Производительность собственного Map Canvas | OPEN | Desktop | До масштабирования Phase 9 — прототип на больших GeoTIFF/GPKG. Проверить windowed reads, CRS, overlay/swipe, выбор линии, задержки и память. |
| OQ-02 | Минимальная QGIS LTR | OPEN | GIS / QA | До заявленной поддержки в Phase 13 — CI на чистом QGIS LTR, Toolbox, Modeler, Batch, qgis_process и handshake. |
| OQ-03 | Совместимые GDAL/PROJ версии | OPEN, выполнена проверка wheel metadata | Build / GIS | До фиксации GIS lock в Phase 2 — воспроизводимое Windows разрешение, ABI, drivers, данные PROJ, GPKG/GeoTIFF round-trip. [ADR-0004](../docs/architecture/adr/ADR-0004-WINDOWS-GIS-RUNTIME.md) |
| OQ-04 | LoG zero-crossing и шум | OPEN | Detection / Science | До Phase 4 — synthetic benchmark и допуски для zero-crossing, шумов и вырожденных входов. |
| OQ-05 | Matching thresholds | OPEN | Ensemble / Science | До фиксации Phase 6 — labeled synthetic/real data, sensitivity и holdout. |
| OQ-06 | LSM weights | OPEN | Science | До научной приёмки Phase 7 — benchmark и ablation study. |
| OQ-07 | Радиус пространственной поддержки | OPEN | LSM / Science | До фиксации Phase 7 — resolution sensitivity study, единицы и границы. |
| OQ-08 | Переносимые геометрические пороги | OPEN | Ranking / Science | До утверждения Phase 8 — cross-region benchmark и оценка переносимости. |
| OQ-09 | Геологические классы | OPEN | Product / Domain Expert | До Phase 10 — словарь классов, экспертные источники и domain review. |
| OQ-10 | OSM endpoints/providers | OPEN | GIS | До Phase 13 — провайдер, локальный/сетевой режимы, limits, policy и атрибуция. |
| OQ-11 | Приоритетные GEE datasets | OPEN | Integration | До работ по GEE в Phase 13 — use-case/terms review, ограничения сервиса. |
| OQ-12 | Лицензии bundle | OPEN | Release | До lock и распространения каждого компонента — SBOM, notices и legal review. |
| OQ-13 | Поддерживаемые Windows versions | OPEN | Build / QA | До выпуска Bundle — поддерживаемый Windows x64 matrix, security build CPython и clean VM tests. |
| OQ-14 | Оптимальные tile/halo | OPEN | Core / Science | С Phase 3 — seams/edge tests, memory и performance benchmark. |
| OQ-15 | Нужна ли GPU в будущем | DEFERRED | Core | После CPU bottleneck measurements. Базовый сценарий — CPU. |
| OQ-16 | Экспорт labels для целевых ML frameworks | OPEN | ML | До Phase 11 — dataset prototype, spatial split, provenance и round-trip. |
| OQ-17 | Потребуется ли в будущем импорт ранее созданных пользовательских project files | DEFERRED | Product / Data Architecture | По отдельному решению пользователя — требования и отдельная спецификация импорта. |
| OQ-18 | Какие дополнительные проверки новой `.lspx` schema нужны после реализации | OPEN | Data Architecture / QA | Phase 2 — schema, round-trip, path/security и fault-injection tests на реальных файлах. |
| OQ-19 | Обнаруживает ли выбранный coding agent `.agents/skills` автоматически | OPEN, чтение вручную подтверждено | Developer Experience | Чистый Codex Web checkout и свидетельство автоматического discovery. Для Phase 1 пользователь разрешил временный ручной handoff всех 11 Skills. |
| OQ-20 | Точные численные допуски каждого научного алгоритма | OPEN | Scientific Computing | До кодирования каждого метода — analytic fixtures, tolerances и scientific benchmark. |
| OQ-21 | Framing, transport binding, handshake, версии и лимиты JSON/JSONL | PROPOSED | Architect / QA | Кандидат Phase 1 реализован. Рассмотреть таблицу версий и replay в PR. [ADR-0002](../docs/architecture/adr/ADR-0002-IPC-AND-JOB-LIFECYCLE.md) |
| OQ-22 | Error taxonomy, event payloads, exit codes, UTC timestamps и неизвестные поля | OPEN | Core / QA | Кандидат Phase 1 реализован. Рассмотреть форму сообщений и fixtures в PR. [ADR-0002](../docs/architecture/adr/ADR-0002-IPC-AND-JOB-LIFECYCLE.md) |
| OQ-23 | Cancel/close/crash semantics, lifecycle процесса и семантика terminal status | PROPOSED | Core / Desktop / QA | Phase 1 — replay и fixture subprocess. Production process/GUI fault-injection и cleanup остаются открытыми. [ADR-0002](../docs/architecture/adr/ADR-0002-IPC-AND-JOB-LIFECYCLE.md) |
| OQ-24 | Job ID, retry/idempotency и lock для конкурентных заданий | OPEN | Core / Data Architecture | Phase 1 — инварианты IDs и lifecycle. Phase 2 — проверка дубликатов и восстановления на реальном каталоге. [ADR-0002](../docs/architecture/adr/ADR-0002-IPC-AND-JOB-LIFECYCLE.md) Development: new Worker job UUID for recomputation and stable publication/result IDs during recovery. Result-death tests verify one receipt per result. Product-level retry and duplicate-command policy remains open. |
| OQ-25 | Владелец asset records и правило проекции в SQLite | PROPOSED | Data Architecture / Architect | До утверждения продуктовой схемы согласовать ADR, identity/digest и сценарий расхождения. [ADR-0003](../docs/architecture/adr/ADR-0003-PROJECT-DATA-OWNERSHIP.md) Development: manifest owns stable asset UUID and content version UUID. Catalog is a consistency witness with result and receipt authority. Relink regression preserves historical source provenance. Product field ownership and migrations remain to be accepted. |
| OQ-26 | Оркестрация publish/recovery, concurrent writers и границы транзакций | PROPOSED | Data Architecture / QA | P1 gate перед приёмкой продуктовой Phase 2. Утвердить state machine и durable PREPARED до замены manifest, ordering, rollback и fault-injection на каждой границе. [ADR-0003](../docs/architecture/adr/ADR-0003-PROJECT-DATA-OWNERSHIP.md) Development: local filesystem, WAL + FULL and single cooperating writer. Copy/result process-death and repeat-recovery tests cover publication ordering. Final closure requires an agreed product durability scope and verification for that scope. |
| OQ-27 | Schema `.lspx`, grammar paths/URI, `mixed`, nullable fields, неизвестные поля и версии | OPEN | Data Architecture / QA | Для продуктового resolver и схемы — schema and contract fixtures для Reference/Copy, Windows path handling и future versions. [ADR-0003](../docs/architecture/adr/ADR-0003-PROJECT-DATA-OWNERSHIP.md) Development: strict manifest 1.1 / SQLite 2, local absolute Reference and contained Copy, safe refusal of unsupported versions. Product path/URI interoperability, upgrades and forward compatibility remain open. |
| OQ-28 | Источник native runtime, vector I/O, изоляция от QGIS и подход к data dirs | PROPOSED | Build / GIS | До утверждения продуктового runtime — driver smoke на Windows, сравнение wheel и согласованной сборки из одного канала. [ADR-0004](../docs/architecture/adr/ADR-0004-WINDOWS-GIS-RUNTIME.md) Development: Rasterio 1.4.4 / NumPy 2.4.6 candidate checked on Windows/Linux CI, GeoTIFF/GPKG and offline control transform. Bundle isolation, grid transforms, QGIS coexistence and redistribution remain to be verified before final closure. |
| OQ-29 | Оконное чтение Desktop, канал preview и критерии Map Canvas | OPEN | Desktop / GIS / QA | Прототип OQ-01 — замер end-to-end latency, memory и стабильности ресурсных ручек. |
| OQ-30 | P0/MVP и P1/v1.0. PRE-приоритеты, Balanced, обязательные режимы OSM и релизный минимум | OPEN | Product / Requirements | До планирования затронутой фазы — согласовать атомарные FR, трекер scope и GWT. [Аудит Phase 0](../docs/REPOSITORY_BOOTSTRAP_REPORT.md) |
| OQ-31 | Научные release gates, benchmark corpus, метрики, независимость и ответственность | OPEN | Science / QA / Domain Expert | До каждой научной фазы — согласованные manifests, held-out sites, thresholds/tolerances и evidence. Phase 14 — сводка. |
| OQ-32 | Core tooling, locks, CI и база PR | PROPOSED | Developer Experience / QA | В начале Phase 1 создать минимальный skeleton/toolchain. Собрать и установить wheel в чистое окружение CPython 3.11. Начать Domain/Wire после успешной проверки. CI проверяет Windows и Linux. [Структура](../docs/REPOSITORY_STRUCTURE.md) |
| OQ-33 | Недостающие GWT, NFR priorities и release IDs | OPEN | Requirements / QA | До реализации затронутой фазы — атомарные критерии, тест/процедура, phase, priority и evidence owner. |
| OQ-34 | Формальное правило backup и релизных проверок для P0/P1 | OPEN | Product / Requirements / Release | До Phase 2 согласовать покрытие DEC-U13, до выпуска — пороги готовности и зависимости чистой Windows. |
| OQ-35 | Семантика expert labels: Artifact, Needs Field Check и разрешённый spatial split override | OPEN | Data Architecture / Science / Product | До схемы Phase 10–11 — dictionary/version, flags/labels и критерии absence/explicit negative/leakage. |
| OQ-36 | Точная семантика LSM при отсутствии всех групп и при частично недоступных пикселях | OPEN | Science / QA | До реализации Phase 7 — правило mask/NoData и guards нулевого знаменателя, аналитические fixtures. |

OQ-17 не блокирует старт разработки: импорт ранее созданных project files не входит в базовый scope
без отдельного решения пользователя. OQ-18 закрывается тестами новой реализации `.lspx` в чистом
репозитории. Ни один вопрос не предполагает перенос или исследование старого кода.
