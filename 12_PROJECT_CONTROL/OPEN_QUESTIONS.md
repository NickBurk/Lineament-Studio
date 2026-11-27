# Open Questions and Technical Validation

| ID | Вопрос | Метод закрытия | Владелец |
|---|---|---|---|
| OQ-01 | Производительность собственного Map Canvas | Прототип на больших GeoTIFF/GPKG | Desktop |
| OQ-02 | Минимальная QGIS LTR | CI на чистой среде | GIS |
| OQ-03 | Совместимые GDAL/PROJ версии | Lock + integration tests | Build |
| OQ-04 | LoG zero-crossing и шум | Synthetic benchmark | Detection |
| OQ-05 | Matching thresholds | Labeled synthetic/real data | Ensemble |
| OQ-06 | LSM weights | Ablation study и benchmark | Science |
| OQ-07 | Радиус пространственной поддержки | Resolution sensitivity study | LSM |
| OQ-08 | Переносимые геометрические пороги | Cross-region benchmark | Ranking |
| OQ-09 | Геологические классы | Domain review | Product |
| OQ-10 | OSM endpoints/providers | Policy, limits, offline tests | GIS |
| OQ-11 | Приоритетные GEE datasets | Use-case/terms review | Integration |
| OQ-12 | Лицензии bundle | Dependency SBOM и legal review | Release |
| OQ-13 | Поддерживаемые Windows versions | Clean VM tests | Build |
| OQ-14 | Оптимальные tile/halo | Performance benchmark | Core |
| OQ-15 | Нужна ли GPU в будущем | CPU bottleneck measurements | Core |
| OQ-16 | Экспорт labels для целевых ML frameworks | Dataset prototype | ML |
| OQ-17 | Потребуется ли в будущем импорт ранее созданных пользовательских project files | Только отдельное решение пользователя и отдельная спецификация импорта | Product / Data Architecture |
| OQ-18 | Какие дополнительные проверки новой `.lspx` schema нужны после реализации | Schema, round-trip и fault-injection tests в новом репозитории | Data Architecture / QA |
| OQ-19 | Обнаруживает ли выбранный coding agent `.agents/skills` автоматически | Проверка в целевом Codex Web environment на чистом checkout | Developer Experience |
| OQ-20 | Точные численные допуски каждого научного алгоритма | Аналитические fixtures и scientific benchmark | Scientific Computing |

OQ-17 не блокирует старт разработки: импорт ранее созданных project files не входит в базовый scope
без отдельного решения пользователя. OQ-18 закрывается тестами новой реализации `.lspx` в чистом
репозитории. Ни один вопрос не предполагает перенос или исследование старого кода.
