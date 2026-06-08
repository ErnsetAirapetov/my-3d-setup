# calibration/tests/

Пройденные калибровочные тесты. На каждый — своя папка с методикой и результатами.

| Тест | Что даёт |
| --- | --- |
| [first-layer](first-layer/) | Z-offset (squish первого слоя) |
| [dimensional](dimensional/) | размерная точность X/Y/Z (cube + ortho + Соркин) |
| [temperature-tower](temperature-tower/) | температура сопла под филамент |
| [flow-rate](flow-rate/) | Flow ratio (Extrusion Multiplier) |
| [pressure-advance](pressure-advance/) | PA — чёткие углы, чистый шов |

Порядок под новый филамент: **temperature → flow → pressure-advance**. Размерные тесты — независимы от филамента, делаются один раз.

Сводка итоговых настроек — в [../README.md](../README.md).
