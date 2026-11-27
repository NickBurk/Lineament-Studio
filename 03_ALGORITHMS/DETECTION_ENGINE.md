# Detection Engine Specification

## Семейства
**Edge Detection:** Canny, LoG zero-crossing.  
**Line Segment Extraction:** LSD, EDLines, Hough Transform.  
**Adapters:** PyLineament — необязательный адаптер, не обязательная зависимость.

## Контракт результата
Каждый сегмент содержит segment_id, геометрию/координаты концов, длину и единицы, осевую ориентацию, detector_id/version/family, scale_id, preprocessing_id, параметры запуска, raster/run ID и диагностические признаки качества.

## Canny
Параметры: Gaussian sigma, low/high threshold, absolute или percentile threshold mode, aperture size, L2 gradient. Обязательна проверка `low < high`. Percentile mode сохраняет статистику, на основании которой рассчитаны пороги.

## LoG
Gaussian Laplacian с sigma и zero-crossing extraction. Сохраняются sigma, kernel, response threshold, noise suppression и нормализация. Конкретные правила zero-crossing и подавления шума фиксируются в ADR и тестах.

## LSD / EDLines
Работают с grayscale raster или edge map в зависимости от реализации. Сохраняются исходные параметры и score, если он предоставляется. Score разных детекторов нельзя считать напрямую сопоставимым без калибровки.

## Hough
Параметры: rho resolution, theta resolution, vote threshold, minimum line length, maximum gap.

## Важное правило
Canny/LoG — edge detectors; LSD/EDLines/Hough — line extraction. Несколько близких комбинаций одного семейства не должны искусственно увеличивать Detector Agreement.

## Preview
Preview Grid выполняется на выбранном репрезентативном окне, показывает вход, результат, число линий и метрики. Preview не должен незаметно использовать иной pipeline, чем полный запуск.
