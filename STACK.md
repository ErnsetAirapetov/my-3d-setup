# Опенсурс-стек: решения, бюджет памяти и план сборки

Что и почему мы ставим, как не упереться в 128 МБ RAM принтера, и в каком порядке всё поднимать.

> 🗺 **Полная визуальная архитектура** (что где работает, почему именно там, как подключается, схемы
> и потоки данных) — в [ARCHITECTURE.md](ARCHITECTURE.md). Этот документ — про **решения и план**.

Связанные: [ARCHITECTURE.md](ARCHITECTURE.md) · [firmware roadmap](firmware/README.md) ·
[CB1 — спеки и роль](mods/planned.md) · [что докупить](tools/shopping-list.md) · [сеть](printer/network.md).

## 0. Реальность про память — читать первым

Центральный факт, вокруг которого строится вся архитектура:

- Хост принтера — **Allwinner T113-S3, 128 МБ RAM**, память **впаяна**. Нарастить штатно **нельзя**
  (только перепайка SoC на T113-S4/256 МБ — экстремально, не наш путь).
- 128 МБ — **задокументированный потолок**. При перегрузе RAM — реальные вылеты, перезагрузки,
  ошибки `Timer too close`. Главные пожиратели: **тач-экран**, **камера**, **тяжёлые плагины**.
- **Вывод:** «добавить мощности» = внешний **CB1**. Это и есть «мод доп.мощности», к которому мы
  пришли. CB1 нужен **не** для базового Klipper (он крутится на принтере), а чтобы снять с принтера
  весь удобный обвес и не жить на грани OOM.

## 1. Принцип: тонкий принтер + толстый сервер

- **Принтер** несёт только control core: Forge-X **Headless** + Klipper + Moonraker (+ KAMP/макросы,
  они почти бесплатны по RAM). Встроенная камера — пока работает здесь, через экономный стример.
- **CB1** несёт весь «фарш»: Telegram-бот, Spoolman, удалёнку (Tailscale), push для мобилки,
  таймлапсы, бэкапы.
- Связь — **по сети** через Moonraker API принтера. Никакого провода между платами.

Кто где и почему — подробно в [ARCHITECTURE.md](ARCHITECTURE.md#полная-карта-компонентов).

## 2. Решения (зафиксировано)

| Что | Решение | Почему |
| --- | --- | --- |
| Прошивка | **Forge-X**, режим **Headless** | OSS, dual-boot со стоком, OTA; headless экономит ~10–12 МБ RAM |
| Веб-интерфейс | **Mainsail** (основной), Fluidd рядом | индустрия-стандарт, оба в комплекте мода |
| Камера | **встроенная, на принтере** (low-RAM стример) | USB-вебку на CB1 осознанно отложили |
| Удалёнка из интернета | **Tailscale** (subnet router на CB1) | бесплатно, без проброса портов, безопасно |
| Telegram-бот | **moonraker-telegram-bot** на CB1 | статус/фото/кнопки/уведомления + таймлапсы; интернет и рендер — на CB1 |
| Учёт филамента | **Spoolman** на CB1 | «resource-intensive» — не на 128 МБ |
| Мобильное приложение | **Mobileraker** + companion на CB1 | нативное OSS-приложение + push |
| Адаптивный стол/очистка | **KAMP** на принтере | чистый конфиг Klipper, почти ноль RAM |
| CB1 — роль | сетевой сервер-разгрузчик | Moonraker остаётся на принтере |

Отложено осознанно: USB-вебка на CB1, self-hosted Obico (AI-детект брака) — вернёмся при желании.

## 3. Бюджет памяти 128 МБ — как не словить вылеты

Рычаги по убыванию выигрыша:

| Рычаг | Что даёт | Где |
| --- | --- | --- |
| **Headless** вместо Stock-экрана | освобождает больше всего RAM (~10–12 МБ) | принтер |
| **Весь обвес на CB1** (бот, Spoolman, таймлапсы) | это самые тяжёлые сервисы | CB1 |
| **Не ставить тяжёлые плагины на принтер** | каждый ест RAM | принтер |
| Камеру — экономный стример Forge-X | встроенная камера ест ~18 МБ | принтер |
| _Будущее:_ вынести камеру на USB-вебку CB1 | снимет ~18 МБ + CPU с принтера | CB1 |
| Если ошибки на сложном g-code: проще infill, без **Gyroid/Fuzzy Skin**, печать по одному объекту | крайняя мера из FAQ Forge-X | слайсер |

## 4. План сборки по этапам

Этапы 1–2 уже дают рабочий Klipper с веб-интерфейсом и камерой по LAN. CB1 (3–4) добавляет
Telegram-бота, удалёнку, учёт филамента. Детали подключения — в [ARCHITECTURE.md](ARCHITECTURE.md).

### Этап 0 — страховка
- [ ] Бэкап стоковой прошивки (чек-лист в [firmware/README.md](firmware/README.md)).
- [ ] LAN-mode включён _(готово)_; версия прошивки записана в [printer/stock-firmware.md](printer/stock-firmware.md).

### Этап 1 — Forge-X на принтер (сразу Headless)
- [ ] Прочитать актуальный INSTALL и FAQ Forge-X.
- [ ] Прошить, проверить **dual-boot** (сток на месте).
- [ ] Режим **Headless** (или Feather, если нужен экран).
- [ ] Открыть Mainsail по LAN, проверить камеру на `:8080`. SSH (`root`/`root`) → сменить пароль.

### Этап 2 — обязательная пост-настройка
- [ ] Заново **z-offset**, перекалибровать **bed mesh**, обновить стартовый **g-code в OrcaSlicer**.
- [ ] Подключить **KAMP**, базовые макросы (START/END_PRINT). Прогнать калибровки (PA, flow).

### Этап 3 — CB1 как Linux-сервер
- [ ] Купить мелочёвку для CB1 (точные спеки — [tools/shopping-list.md §8](tools/shopping-list.md)).
- [ ] Записать ОС на microSD (BTT CB1-образ или Armbian) → в сеть → DHCP-резервация `192.168.1.135`.
- [ ] SSH, обновить пакеты.

### Этап 4 — обвес на CB1
- [ ] **Tailscale** на CB1 + телефон + ПК; на CB1 включить **subnet router** (`192.168.1.0/24`).
- [ ] **moonraker-telegram-bot** → указать на Moonraker принтера + камеру; создать бота у @BotFather.
- [ ] **Spoolman** → связать с Moonraker принтера.
- [ ] **mobileraker-companion** → push-уведомления.

### Этап 5 — клиенты
- [ ] **ПК:** профиль OrcaSlicer с Moonraker. **Телефон:** Mobileraker + бот в Telegram.

## 5. Открытые вопросы (TBD)

- Версия/релиз Forge-X на момент установки — зафиксировать в [firmware/forge-x/](firmware/forge-x/).
- ОС для CB1: готовый BTT-образ vs чистый Armbian — решить на этапе 3.
- Вернуться к USB-вебке на CB1 и/или Obico — по желанию после этапа 4.

## Источники

- Forge-X: [github.com/DrA1ex/ff5m](https://github.com/DrA1ex/ff5m) · [FAQ](https://github.com/DrA1ex/ff5m/blob/main/docs/FAQ.md)
- Klipper-mod (xblax): [github.com/xblax/flashforge_ad5m_klipper_mod](https://github.com/xblax/flashforge_ad5m_klipper_mod) · [внешний хост (#216)](https://github.com/xblax/flashforge_ad5m_klipper_mod/discussions/216)
- moonraker-telegram-bot: [github.com/nlef/moonraker-telegram-bot](https://github.com/nlef/moonraker-telegram-bot)
- Spoolman: [github.com/Donkie/Spoolman](https://github.com/Donkie/Spoolman) · Mobileraker: [github.com/Clon1998/mobileraker](https://github.com/Clon1998/mobileraker)
- KAMP: [github.com/kyleisah/Klipper-Adaptive-Meshing-Purging](https://github.com/kyleisah/Klipper-Adaptive-Meshing-Purging)
- Гайд Klipper на AD5M: [blog.octoeverywhere.com](https://blog.octoeverywhere.com/how-to-install-klipper-on-your-flashforge-adventurer-5m-or-5m-pro/) · CB1 wiki: [global.bttwiki.com/CB1.html](https://global.bttwiki.com/CB1.html)
