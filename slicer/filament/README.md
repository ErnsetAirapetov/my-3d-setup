# slicer/filament/

Профили филаментов для OrcaSlicer. **Один филамент = один профиль.** Не «PLA вообще», а «PLA Sunlu чёрный 1.75» — потому что характеристики разнятся даже между батчами.

Имя файла: `<тип>_<бренд>_<цвет>.json`, например `pla_sunlu_black.json`.

Что в профиле:
- Температуры сопла и стола (откалиброванные башней — см. [../../calibration/tests/temperature-tower/](../../calibration/tests/temperature-tower/)).
- Скорости печати, охлаждения.
- Retraction (откалиброван — см. [../../calibration/tests/retraction/](../../calibration/tests/retraction/)).
- Flow rate / Extrusion Multiplier (см. [../../calibration/tests/flow-rate/](../../calibration/tests/flow-rate/)).
- Pressure Advance (после Klipper).

Заметки по типам филаментов (общие, не привязанные к конкретной катушке) — в [../../filaments/notes/](../../filaments/notes/).
