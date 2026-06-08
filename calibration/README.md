# calibration/ — калибровка

Принтер откалиброван и печатает стабильно. Здесь — итоговые настройки и пройденные тесты.

## Текущий профиль — ESUN PLA+

| Параметр | Значение | Где в Orca |
| --- | --- | --- |
| Сопло | **210 °C** (initial 215) | Filament → Nozzle temperature |
| Flow ratio | **1.008** | Filament → Flow ratio |
| Pressure advance | **0.045** | Filament → Pressure advance |
| Прошивка | v3.2.7 (stock) | — |

Подробности по катушке — в [filaments/notes/esun-pla-plus.md](../filaments/notes/esun-pla-plus.md).

## Статус тестов

| Тест | Статус | Результат |
| --- | --- | --- |
| [first-layer](tests/first-layer/) | базовый | Z-offset подобран |
| [dimensional](tests/dimensional/) | ✅ | X/Y точны из коробки; Z +0.5% (в backlog для Klipper) |
| [temperature-tower](tests/temperature-tower/) | ✅ | 210 °C |
| [flow-rate](tests/flow-rate/) | ✅ | 1.008 |
| [pressure-advance](tests/pressure-advance/) | ✅ | 0.045 |
| [bed-mesh](bed-mesh/) | ⏳ | сырой меш на стоке недоступен; только Z-offset |

## Backlog (после Klipper)

- **Z +0.5%** — steps/mm по Z завышен, на стоке не правится.
- **input-shaper**, **VFA** — резонансы и предельные скорости.
- Полноценный **bed mesh** (5×5 / 7×7) — недоступен на стоковой прошивке.
