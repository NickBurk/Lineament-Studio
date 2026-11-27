# Non-functional Requirements

| ID | Требование | Метрика / порог | Метод проверки |
|---|---|---|---|
| NFR-REL-001 | Ошибка Worker не должна автоматически завершать GUI | Все критические сценарии Worker | Fault-injection integration |
| NFR-REL-002 | Отмена не должна повреждать ранее подтверждённые результаты | 0 повреждённых финальных артефактов | Cancel/restart regression |
| NFR-DATA-001 | Запись `.lspx` и SQLite должна быть безопасной | Валидный manifest/DB после commit или rollback | Fault-injection |
| NFR-DATA-002 | Внутренние пути не должны выходить за project folder | 0 успешных path traversal | Security tests |
| NFR-PERF-001 | Поддерживать целевой ноутбук 16 GB RAM / integrated graphics | Точные лимиты — benchmark required; стартовый Worker budget 6 GB | Peak-RAM benchmark |
| NFR-PERF-002 | Большие растры обрабатываются блоками | 20k×20k — целевой benchmark fixture | Performance suite |
| NFR-PERF-003 | GUI остаётся отзывчивым во время Worker jobs | Нет блокировки event loop на длительное вычисление | GUI stress test |
| NFR-REPRO-001 | Каждый запуск сохраняет версии, параметры, CRS, units и checksums | Все обязательные поля присутствуют | Manifest schema tests |
| NFR-REPRO-002 | Детерминированные методы воспроизводимы в заданном tolerance | Tolerance задаётся для каждого алгоритма | Repeatability tests |
| NFR-COMP-001 | Core не зависит от PySide6/PyQt/PyQGIS | Нет запрещённых импортов | Static dependency check |
| NFR-COMP-002 | QGIS Plugin и Desktop используют совместимый versioned Worker protocol | Protocol compatibility matrix | Integration tests |
| NFR-UX-001 | Ошибки содержат user-facing explanation и technical diagnostic context | Все error states покрыты | GUI/error tests |
| NFR-UX-002 | Критические действия доступны с клавиатуры и имеют корректный focus order | UX checklist | Manual accessibility review |
| NFR-OFF-001 | Основной pipeline, проект, review, classic ML и export работают offline | Нет сетевого запроса в offline test | Network-disabled E2E |
| NFR-SEC-001 | Секреты не сохраняются в открытых manifests/logs | 0 обнаруженных секретов | Secret scan/review |
| NFR-SEC-002 | Импортируемые manifests и archives валидируются до использования | Invalid payload rejected safely | Security tests |

Порог, не подтверждённый benchmark или пользовательским решением, обозначается TBD.
Стартовые инженерные параметры не становятся научными критериями приёмки.
