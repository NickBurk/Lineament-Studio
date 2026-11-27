# API and Job Contracts

## Общие правила
JSON UTF-8; `protocol_version` обязателен; UUID для job IDs; CRS и единицы передаются явно;
ошибки имеют стабильный `error_code`; секреты не попадают в логи.

## Job manifest
```json
{
  "protocol_version": "1.0",
  "job_id": "UUID",
  "operation": "ensemble_detection",
  "project_id": "UUID",
  "inputs": {"dem": "inputs/dem/main_dem.tif"},
  "parameters": {
    "scales": [1, 2, 4],
    "azimuths_deg": [0, 45, 90, 135, 180, 225, 270, 315],
    "sun_altitude_deg": 45
  },
  "resource_profile": "standard",
  "outputs": {"directory": "experiments/EXP_001/results"}
}
```

## JSONL events
`started`, `stage_started`, `progress`, `warning`, `artifact_created`, `stage_completed`,
`cancel_requested`, `cancelled`, `failed`, `completed`. Каждое событие содержит
`protocol_version`, `job_id`, `timestamp`.

## Отмена и lifecycle
Кооперативная отмена между безопасными блоками и этапами. GUI закрытие во время вычисления
должно иметь определённую политику: дождаться, запросить отмену или оставить Worker под контролем
Job Manager. Нельзя оставлять orphan processes/threads. Принудительное завершение — аварийный
механизм. Незавершённые файлы не публикуются как финальные.

## Версионирование
Несовместимые изменения повышают major-версию протокола. Worker и клиент проверяют совместимость
до запуска. Desktop и QGIS используют один утверждённый контракт.
