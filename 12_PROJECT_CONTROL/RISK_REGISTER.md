# Risk Register

| ID | Риск | Последствие | Мера |
|---|---|---|---|
| R-01 | Слишком большой scope | MVP не завершён | P0/P1 gates |
| R-02 | Недоказанная точность детекторов | Ошибочные научные выводы | Benchmark и экспертная проверка |
| R-03 | Сложность собственного Map Canvas | Рост сроков | Ранний вертикальный прототип |
| R-04 | Конфликты GDAL/PROJ/Qt | Сбои сборки | Раздельные Runtime и lock |
| R-05 | Недостаток RAM | OOM | Tiling, memory budget |
| R-06 | Ошибки на границах тайлов | Разрывы/дубли | Halo и stitching tests |
| R-07 | Неверная трактовка LSM | Псевдовероятность | Ясные определения и UI |
| R-08 | Spatial leakage в Dataset | Завышенные ML metrics | Spatial split |
| R-09 | Потеря экспертной разметки | Потеря научной работы | Immutable sets, versioning, manual backup |
| R-10 | Ограничения источников | Нарушение условий | Attribution/license metadata |
| R-11 | ИИ-агенты меняют чужие модули | Конфликты интеграции | Ownership и PR review |
| R-12 | Зависимость от API | Недоступность offline | Offline-first |
| R-13 | Неверная проекция/единицы | Искажённые измерения | Preflight и CRS tests |
| R-14 | Зависимые детекторы завышают agreement | Ложная поддержка | Detector Family model |
| R-15 | EXE работает только на машине разработчика | Невозможность распространения | Чистые Windows VM |
| R-16 | `.lspx` manifest и SQLite расходятся | Повреждение/потеря проекта | System-of-record rules, transaction tests |
| R-17 | Позднее может потребоваться импорт пользовательских проектов из иных форматов | Дополнительная стоимость импорта/миграции данных | Отдельное решение пользователя, import requirements и явный migration design; не переносить старый код |
| R-18 | Coding agent не обнаруживает Skills | Игнорирование инструкций | Проверить discovery; передавать пути явно |
| R-19 | Произвольные научные пороги выдаются за валидированные | Некорректные выводы | Status labels, sources, benchmark |
| R-20 | Import archive/path traversal | Чтение/изменение файлов вне проекта | Strict validation and security tests |
