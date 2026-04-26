# Запрос на DHCP-резервацию принтера на OpenWRT

Это записка для агента, который настраивает домашний OpenWRT-роутер. Хочется зафиксировать IP 3D-принтера, чтобы он не менялся со временем.

## Что нужно сделать

Создать DHCP static lease в OpenWRT:

| Параметр | Значение |
| --- | --- |
| Hostname | `adventurer5m-pro` |
| MAC | `24:A1:0D:B2:AA:8E` |
| IP | `192.168.1.134` |

После применения — клиент должен оставаться доступным по этому IP вне зависимости от перезагрузок и времени аренды.

## Зачем

- Это **Flashforge Adventurer 5M Pro** в домашней сети.
- IP `192.168.1.134` уже зафиксирован как «адрес принтера» во второй репе [`my-3d-setup`](https://github.com/Air-Erik/my-3d-setup) (`printer/network.md`, `CLAUDE.md`). Если он сменится — придётся править документацию, скрипты опроса и профили слайсера.
- Принтер слушает на портах 8080 (камера, MJPEG), 8898 (HTTP REST API Flashforge), 8899 (TCP plain text M-code API). Стабильный IP нужен для бесперебойного доступа из слайсера и скриптов мониторинга.

## Как сделать в OpenWRT

**Через LuCI:** Network → DHCP and DNS → Static Leases → Add.

**Через CLI** — добавить блок в `/etc/config/dhcp`:

```
config host
	option name 'adventurer5m-pro'
	option mac '24:A1:0D:B2:AA:8E'
	option ip '192.168.1.134'
```

После правки:

```sh
service dnsmasq restart
```

## Проверка после применения

С машины, где живёт репа `my-3d-setup`:

```bash
ping -c 1 192.168.1.134

# опрос принтера через TCP M-code API
exec 3<>/dev/tcp/192.168.1.134/8899
printf '~M115\r\n' >&3; timeout 1 cat <&3
exec 3<&-; exec 3>&-
```

Если ответ `~M115` начинается с `Machine Type: Flashforge Adventurer 5M Pro` — всё ок, IP стабилен.

Бонус: после успешной резервации на OpenWRT-стороне зарегистрировать DNS-имя `adventurer5m-pro.lan` (или аналог в текущем домене) тоже не помешает — это позволит в репе `my-3d-setup` уйти от хардкода IP в дальнейшем.

---

_Записка сгенерирована из репы `my-3d-setup` 2026-04-26._
