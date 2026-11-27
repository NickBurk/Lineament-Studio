# Testing Strategy

## Типы
Unit; Integration; Regression; Scientific Benchmark; Performance; GUI; E2E; Recovery;
Security; Packaging; Compatibility.

## QA procedure
QA Engineer читает требования, acceptance criteria, ADR и diff; строит матрицу
requirement → test → result → evidence; проверяет positive/negative/boundary/failure cases;
фиксирует точные команды и выводы; повторяет критические тесты после исправлений.
Production code не изменяется незаметно во время независимой проверки.

## Обязательные сценарии
1. Первый и повторный запуск с открытием DEM.
2. Создание, сохранение, закрытие и повторное открытие `.lspx`.
3. DEM внутри проекта и по внешнему пути.
4. Отсутствующий, перемещённый, изменённый, недоступный и повреждённый источник.
5. CRS, affine transform включая rotation/skew, NoData/mask, resolution, extent, dtype, units.
6. NoData-only, NaN/Inf и пустой растр.
7. Тайловые границы и halo.
8. Single и Ensemble.
9. Отмена, закрытие окна во время работы и повторный запуск Worker.
10. Ошибка Worker, нехватка диска и частичная запись.
11. Unicode и длинные Windows-пути.
12. GDAL/PROJ runtime, data, drivers и DLL.
13. Экспорт и round-trip import.
14. Independent Annotation: import, compare, conflict preview, consensus.
15. `.lspx` schema migration и backward compatibility.
16. Offline-first сценарии.
17. Чистая Windows-сборка без Python/QGIS.
18. Чистая QGIS-среда.

## Качество тестов
Тесты детерминированы и изолированы. Синтетические fixtures предпочтительнее пользовательских DEM.
Моки используются на внешних границах; критические форматы проверяются реальными файлами.
Не ослаблять assertions ради зелёного статуса.

## Severity
Blocker — потеря данных/невозможность запуска/критически неверный результат.
Critical — ключевой сценарий сломан без обхода.
Major — важная функция некорректна.
Minor — ограниченный дефект.
Cosmetic — визуальная проблема без функционального влияния.

## Code Review priority
P0 — потеря/повреждение данных, опасное выполнение кода, критическая уязвимость.
P1 — сломан основной сценарий или неверный научный/geospatial результат.
P2 — существенный функциональный дефект/регрессия/несовместимость.
P3 — ограниченный дефект/сопровождаемость.
P4 — косметика.

## CI
Каждый PR запускает быстрые unit/lint/type/security checks. Ночные/release pipelines —
интеграционные и тяжёлые тесты. Benchmark outputs сохраняются как артефакты.
