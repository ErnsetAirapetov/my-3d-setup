# flow-rate — Flow ratio (Extrusion Multiplier)

Коэффициент потока филамента. Завышен → толстые стенки, вспученный верх; занижен → щели, слабая адгезия. Делается на каждый филамент после температуры.

## Как

Orca-Flashforge → `Calibration → Flow rate`. Сначала **Pass 1 (coarse)**, шаг 5% — выбрать куб с самой гладкой верхней гранью. Потом **Pass 2 (fine)** вокруг него, шаг 1–2%. Итог → `Filament → Flow ratio`.

## Результаты

### ESUN PLA+ — 2026-06

- Pass 1: лучший 0.98 → +5 → 1.029.
- Pass 2: −2 → **Flow ratio 1.008**.

На стоке катушка чуть недоливала, добавили ~3%. → записано в профиль Orca и [filaments/notes/esun-pla-plus.md](../../../filaments/notes/esun-pla-plus.md).
