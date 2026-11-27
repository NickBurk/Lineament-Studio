# System Architecture

## Логическая схема
```text
Desktop UI (PySide6) ─┐
                      ├── Job Client ── JSON/JSONL IPC ── Lineament Core Worker
QGIS Plugin (PyQGIS) ─┘                                  │
                                                        ├── Domain / Application
                                                        ├── Data Engine
                                                        ├── Preprocessing
                                                        ├── Detection / Postprocessing
                                                        ├── Ensemble / Multi-scale
                                                        ├── LSM / Structural / Ranking
                                                        ├── Review / Dataset / ML
                                                        └── Export / Reporting
GEE Adapter ── external data/export ── project inputs
OSM Adapter ── online/local OSM data ── project inputs
```

## Архитектурные правила
1. Core не импортирует PySide6, PyQt или PyQGIS.
2. Domain не зависит от Qt, QGIS UI или Infrastructure.
3. GUI — представление и взаимодействие, не место для геоалгоритмов.
4. QGIS и Desktop используют общий Core Worker через отдельный процесс.
5. Для IPC используется versioned JSON job manifest и JSONL events.
6. Альтернативный транспорт не вводится без ADR.
7. Длительные задания выполняются Worker; отмена и закрытие ресурсов детерминированы.
8. Пространственные файлы хранятся отдельно от GUI.
9. Адаптеры не дублируют вычислительную реализацию.
10. Не создаётся второй источник истины для одного состояния.

## Подсистемы
Domain; Application; Data; Preprocessing; Detection; Postprocessing; Ensemble; Multiscale;
Support; Structural; Ranking; Review; Dataset; ML; Smart; Workflow; Resources; Export; Provenance.

## Desktop Map Engine
Выбран собственный облегчённый Qt Map Canvas (`ARCHITECT_SELECTED`). Решение требует
вертикального прототипа и нагрузочных испытаний; это не универсальная замена QGIS.

## Архитектурный процесс
Новая подсистема, публичный API/IPC, dependency change или multi-layer refactor требуют
Software Architect, проверки альтернатив и ADR. Агент сначала исследует фактическое дерево
репозитория, точки входа, тесты и незакоммиченные изменения.

## Ограничение
Отдельный процесс устраняет конфликт GUI bindings, но не гарантирует совместимость GDAL/PROJ.
Для каждого Runtime нужна зафиксированная среда и тестовая матрица.
