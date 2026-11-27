# ML Engine

## MVP
Random Forest; Extra Trees; Gradient Boosting / HistGradientBoosting при совместимости.

## Признаки
length; straightness; curvature; orientation family; detector agreement; stability; scale persistence; local LSM statistics; morphometric context; distance to infrastructure как контекстный признак.

## Обучение
Только на выбранной Dataset Version; spatial split; фиксированный seed; сохранение конфигурации; независимый test set; confusion matrix; calibration analysis, если выдаются вероятности.

## Вероятности
`ml_score` не называется вероятностью, если модель не откалибрована и не проверена на независимой выборке. Даже калиброванная вероятность относится к конкретной label schema, а не автоматически к существованию разлома.

## Deep Learning
Отложено. Базовая работа Dataset Studio не зависит от него.
