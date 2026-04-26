# 2026-04-26 — сетевая разведка принтера

## Что произошло

Пробил порты `192.168.1.134` и собрал максимум информации без авторизации.

## Открытые порты

- `8080` — HTTP, mjpg-streamer (камера, поток MJPEG).
- `8898` — HTTP REST API Flashforge (требует **LAN-mode** на принтере + SN/checkCode).
- `8899` — **TCP plain text M-code API**, отвечает без авторизации. Это главный канал разведки на стоке.

Закрыты на стоке: 80, 443, 7125 (Moonraker), 5000/5001.

## Что удалось вытащить через `~M115` / `~M105` / `~M119` / `~M661`

| Параметр | Значение |
| --- | --- |
| Модель | Flashforge Adventurer 5M Pro |
| Прошивка | **v3.2.7** |
| Serial Number | `SNMOME9C00678` |
| MAC | `24:A1:0D:B2:AA:8E` |
| Рабочее поле X×Y×Z | 220 × 220 × 220 mm |
| Tool count | 1 |
| Эндстопы | X-max, Y-max, Z-min |
| Статус на момент опроса | READY (стоит после демо), LED ON |
| Hotend / стол | 39.5 °C / 33.8 °C (остывает) |
| Хранилище gcode | `/data/` (8 заводских моделей) |

CheckCode (с экрана принтера): `a3356b04`.

## Заметки

- HTTP API на 8898 отвечает `{"code":-2,"message":"Lan mode error"}` — на принтере выключен LAN-режим. Нужно зайти `Settings → Network` и включить.
- TCP API на 8899 — рабочий канал «всегда». Для скриптов и наблюдения в этой сессии и далее можно использовать `/dev/tcp/192.168.1.134/8899` из bash или `New-Object Net.Sockets.TcpClient` из PowerShell.
- Пример из bash:
  ```bash
  exec 3<>/dev/tcp/192.168.1.134/8899
  printf '~M115\r\n' >&3
  timeout 1 cat <&3
  exec 3<&-; exec 3>&-
  ```
- Эндпоинт `?action=snapshot` камеры **не работает** — стоковый сервер отдаёт только `?action=stream`.

## Что обновлено в репе

- [printer/README.md](../printer/README.md) — спеки, SN/MAC/checkCode, отметка ✅ для подтверждённых значений.
- [printer/network.md](../printer/network.md) — таблица портов, описание TCP/HTTP API, шпаргалка по M-кодам, AP-точка.
- [printer/stock-firmware.md](../printer/stock-firmware.md) — версия v3.2.7, список заводских моделей, ограничения.

## Следующие шаги

1. На экране принтера включить **LAN Mode** — это разблокирует HTTP API (POST `/detail`, `/product`, `/control`).
2. Сделать DHCP-резервацию IP по MAC `24:A1:0D:B2:AA:8E` на роутере.
3. После окончания обкатки — стартовая калибровка (см. [calibration/README.md](../calibration/README.md)).
4. Проверить datasheet-значения скоростей и температур на практике в калибровочных тестах.
