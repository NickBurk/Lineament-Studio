# DEM Processing Specification

## 1. Preflight — обязательные проверки
До обработки проверить и зарегистрировать:
- формат и фактическую читаемость файла;
- число bands и выбранную band;
- CRS, тип CRS, наличие/отсутствие CRS и единицы координат;
- affine/geotransform, включая rotation/skew;
- pixel size X/Y, физическое resolution, width/height и extent/bounds;
- NoData value и mask band;
- dtype, NaN/Inf, nodata-only и константные данные;
- вертикальные единицы и совместимость с горизонтальными единицами;
- диапазон высот, долю валидных пикселей;
- доступность файла, права, свободное место и оценку RAM.

Нельзя считать любой GeoTIFF корректной DEM. Отсутствующий CRS и неизвестный CRS — разные
состояния. CRS нельзя назначать наугад.

## 2. Изменение входных данных
Программа не изменяет исходный DEM. Reprojection, resampling, изменение resolution,
назначение CRS, vertical unit conversion и исправление NoData выполняются только на
производной копии с явным действием пользователя и записью provenance.

## 3. Производные
Нормативный источник приоритетов — `01_REQUIREMENTS/FUNCTIONAL_REQUIREMENTS.md`
(DEC-A35, Option A, TASK-AG01-10):

- PRE-001 — P0: Hillshade.
- PRE-002 — P1: Multi-directional Hillshade.
- PRE-003 — P1: Slope, Curvature, TPI, Local Relief Model (LRM), единое требование.
  Реализация одного Slope не закрывает PRE-003.

Gaussian smoothing и Median filtering — незарегистрированные кандидаты, не входят
в текущий разрешённый объём реализации. Их прежние профильные метки P0/P1 не
являются зарегистрированными FR-приоритетами. Нужны отдельная регистрация и criteria.
OQ-30 остаётся OPEN по остальным вопросам MVP/Balanced/OSM/release scope.

## 4. Единицы и CRS
Расстояния рассчитываются в подходящих линейных единицах или геодезически. Метрические
пороги нельзя применять напрямую к координатам в градусах. Вертикальные и горизонтальные
единицы согласуются при slope/hillshade. Для векторных данных проверяются CRS, валидность,
пустые геометрии и правила преобразования.

## 5. Hillshade
Параметры: azimuth, altitude, z-factor, scale/units, multidirectional option.
Конвенция азимута фиксируется в metadata/UI. Проверяется соответствие реализации GDAL/QGIS;
скрытый сдвиг направления недопустим.

## 6. Tile processing
Каждый блок получает halo, соответствующий максимальному радиусу фильтров/операторов.
Финальная область тайла не включает halo. NoData boundaries и краевые зоны обрабатываются
явно. Тестируются rotated transform, частичные тайлы и размеры меньше kernel.

## 7. Выход
Каждый производный растр сопровождается metadata: источник, band, параметры, версия алгоритма,
CRS, transform, bounds, resolution, dtype, NoData, дата и checksum.

## 8. Обязательные fixtures
Плоскость с известным уклоном; синусоидальная поверхность; константа; импульс; ступень;
NoData mask; NaN/Inf; rotated transform; разные dtype и масштабы значений; пустой/повреждённый
файл; разные разрешения; Unicode и длинный Windows path.

## 9. Научная проверка
Для численных методов заранее определить математическое ожидание, допуск, поведение на
вырожденных входах, среднюю/максимальную ошибку и локальные артефакты. Визуально правдоподобный
результат не считается доказательством математической корректности.

## 10. Slope 1.0.0 — authorized contract, integration prerequisite pending

Owner integrated PR #10 at `d958322bdc95e51001a6d6d037d736c0a391a272`.
The hardening baseline requires successful Core CI and JUnit verification on Ubuntu
and Windows for that merge SHA on the integration ref. Publish the verified baseline
after those checks. Slope implementation also requires acceptance of the Phase 3 contract.

Rasterio `Affine(a,b,c,d,e,f)` maps `(column,row)` through `A=[[a,b],[d,e]]`.
Horn raw pixel derivatives `p_raw,q_raw` become `p_m=p_raw*s*v`, `q_m=q_raw*s*v`,
where s is band scale, v is vertical metres/unit. With h horizontal metres/unit,
`A_m=h*A`, `g=inverse(transpose(A_m))@[p_m,q_m]` and
`slope_deg=degrees(atan(hypot(gx,gy)))`. Constant band offset cancels before
arithmetic but remains in provenance. No vertical exaggeration in Slope v1.0.0.
Reject unknown/incompatible units, missing/unknown/geographic CRS and singular
or nonfinite affine. No implicit reprojection or CRS assignment.

Output: algorithm `slope`, version `1.0.0`, Horn 3×3, degrees, single-band float32
GeoTIFF, NoData -1 and internal validity mask; input CRS/affine unchanged. Full
stencil with invalid/nonfinite data or outside-raster neighbors yields invalid output.
Initial tile 1024×1024, halo 1, CPU-only, bounded memory. Worker 6 GB is a starting
profile, not a proven guarantee. Only existing NumPy/Rasterio dependencies allowed.

Analytical-plane engineering tolerance: maximum absolute error <=1e-5 degrees;
no relative error near zero. This fixture criterion does not close OQ-20/OQ-31.
Benchmark sizes 1k/5k/10k/20k squared require runtime, peak RSS, temporary disk and
cancellation measurements. No benchmark results are asserted by this contract.

Strict provenance and Project Storage publication are mandatory. Algorithm-specific
adapter/provenance changes require a proposed CCR and architecture review before
implementation; no manifest/catalog/public Wire contract change is approved here.
