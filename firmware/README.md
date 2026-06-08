# firmware/ — прошивки и roadmap

Здесь живут все артефакты, связанные с прошивкой принтера: бэкапы стоковой, заметки и конфиги Forge-X, конфиги Klipper, история переходов.

## Roadmap

| Этап | Что даёт | Что ломает | Статус |
| --- | --- | --- | --- |
| 1. **stock** | заводская прошивка, всё работает «из коробки» через приложение Flashforge | потолок по тонкой настройке, нет PA / IS, закрытая экосистема | **текущий** |
| 2. **Forge-X mod** | разблокировка root, рут-доступ к системе, шаг к Klipper | гарантия | _TBD_ |
| 3. **Klipper** | полный контроль (printer.cfg, макросы, PA, IS, bed mesh, Mainsail/Fluidd UI) | полностью своя ответственность за конфиг | _TBD_ |

Решение по переходу принимается после полной обкатки и калибровки на стоке — иначе невозможно отделить «дефекты железа» от «эффекта прошивки».

> Прошивка — лишь часть целевого опенсурс-стека. Полная архитектура (принтер + внешний сервер CB1,
> веб-интерфейс, камера, Telegram-бот, удалёнка) — в [ARCHITECTURE.md](../ARCHITECTURE.md) и
> [STACK.md](../STACK.md). Важно: на этом принтере Forge-X разворачивает Klipper + Moonraker +
> Mainsail/Fluidd прямо на бортовом хосте (128 МБ) — внешняя плата для **базового** Klipper не нужна,
> CB1 берёт на себя тяжёлый обвес. Режим прошивки выбран **Headless** (ради экономии RAM).

## Чек-лист **перед** прошивкой (любой)

- [ ] Сделать бэкап текущей прошивки и настроек.
- [ ] Сохранить результаты последних калибровочных тестов.
- [ ] Записать версию текущей прошивки в [../printer/stock-firmware.md](../printer/stock-firmware.md).
- [ ] Прочитать актуальные инструкции к новой прошивке.
- [ ] Убедиться, что есть способ откатиться обратно.
- [ ] Сделать запись в [../journal/](../journal/) до начала и после.

## Структура папки

- [stock/](stock/) — бэкапы заводских настроек.
- [forge-x/](forge-x/) — заметки и конфиги Forge-X mod.
- [klipper/](klipper/) — конфиги Klipper (`printer.cfg`, макросы, Moonraker, Mainsail/Fluidd).

## Источники

- **Forge-X** (выбранный мод): [github.com/DrA1ex/ff5m](https://github.com/DrA1ex/ff5m) · [FAQ](https://github.com/DrA1ex/ff5m/blob/main/docs/FAQ.md)
- **Klipper-mod (xblax)** — оригинал, на котором основан Forge-X: [github.com/xblax/flashforge_ad5m_klipper_mod](https://github.com/xblax/flashforge_ad5m_klipper_mod)
- **ZMod** (родственный форк): [wiki.zmod.link](https://wiki.zmod.link/Zmod/)
- Гайд по установке Klipper на AD5M (для новичка): [blog.octoeverywhere.com](https://blog.octoeverywhere.com/how-to-install-klipper-on-your-flashforge-adventurer-5m-or-5m-pro/)
- Документация Klipper: [klipper3d.org](https://www.klipper3d.org/) · Moonraker: [moonraker.readthedocs.io](https://moonraker.readthedocs.io/)
