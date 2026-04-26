#!/usr/bin/env python3
"""
Простой интервальный таймлапс для Flashforge Adventurer 5M Pro.

Захватывает кадры из MJPEG-потока камеры (порт 8080), складывает их в папку
с временной меткой, по Ctrl+C собирает mp4 через ffmpeg.

Только стандартная библиотека Python. Для сборки видео нужен ffmpeg в PATH.

Примеры:
    python timelapse.py
    python timelapse.py --interval 30
    python timelapse.py --label benchy
    python timelapse.py --no-video
"""

import argparse
import json
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

DEFAULT_IP = "192.168.1.133"
DEFAULT_INTERVAL = 15
DEFAULT_FPS = 30
SERIAL = "SNMOME9C00678"
CHECK_CODE = "a3356b04"
DEFAULT_STREAM_PATH = "/?action=stream"

stop_requested = False


def grab_frame(stream_url, timeout=10):
    """Возвращает один JPEG (bytes) из MJPEG-потока камеры."""
    with urlopen(stream_url, timeout=timeout) as resp:
        buf = b""
        while len(buf) < 4_000_000:
            chunk = resp.read(8192)
            if not chunk:
                break
            buf += chunk
            start = buf.find(b"\xff\xd8")
            if start < 0:
                continue
            end = buf.find(b"\xff\xd9", start + 2)
            if end > start:
                return buf[start:end + 2]
    raise RuntimeError(
        "поток открылся, но JPEG не пришёл "
        "(возможно, камера занята другим клиентом)"
    )


def get_status(ip, port=8898, timeout=5):
    """Возвращает /detail JSON или None, если принтер не отвечает."""
    url = f"http://{ip}:{port}/detail"
    payload = json.dumps({
        "serialNumber": SERIAL,
        "checkCode": CHECK_CODE,
    }).encode()
    req = Request(
        url, data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except (URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None


def assemble_video(frames_dir, fps):
    """Склеивает frame_*.jpg → mp4. Возвращает Path или None."""
    pattern = str(frames_dir / "frame_%06d.jpg")
    output = frames_dir.parent / f"{frames_dir.name}.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", pattern,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        str(output),
    ]
    try:
        subprocess.run(cmd, check=True)
        return output
    except FileNotFoundError:
        print("ffmpeg не найден в PATH — кадры сохранены, видео не собрано.",
              file=sys.stderr)
    except subprocess.CalledProcessError as exc:
        print(f"ffmpeg вернул ошибку: {exc}", file=sys.stderr)
    return None


def handle_sigint(_signum, _frame):
    global stop_requested
    stop_requested = True
    print("\n[!] Получен сигнал остановки — завершаем после текущего кадра…")


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass

    parser = argparse.ArgumentParser(
        description="Интервальный таймлапс для Flashforge Adventurer 5M Pro"
    )
    parser.add_argument("--ip", default=DEFAULT_IP,
                        help=f"IP принтера (default: {DEFAULT_IP})")
    parser.add_argument(
        "--interval", type=float, default=DEFAULT_INTERVAL,
        help=f"интервал между кадрами в секундах "
             f"(default: {DEFAULT_INTERVAL})",
    )
    parser.add_argument(
        "--fps", type=int, default=DEFAULT_FPS,
        help=f"FPS итогового видео (default: {DEFAULT_FPS})",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("output"),
        help="куда складывать кадры и видео (default: ./output)",
    )
    parser.add_argument(
        "--label", default="",
        help="суффикс для имени папки (например, имя модели)",
    )
    parser.add_argument(
        "--no-video", action="store_true",
        help="не собирать mp4 после остановки, "
             "оставить только кадры",
    )
    parser.add_argument(
        "--stream-url", default="",
        help="полный URL MJPEG-потока "
             "(по умолчанию берём из /detail)",
    )
    parser.add_argument(
        "--probe", action="store_true",
        help="один раз дёрнуть камеру, сохранить кадр и выйти",
    )
    args = parser.parse_args()

    status = get_status(args.ip)
    if args.stream_url:
        stream_url = args.stream_url
    elif status and status.get("detail", {}).get("cameraStreamUrl"):
        stream_url = status["detail"]["cameraStreamUrl"]
    else:
        stream_url = f"http://{args.ip}:8080{DEFAULT_STREAM_PATH}"

    if args.probe:
        print(f"Проба камеры: {stream_url}")
        try:
            jpeg = grab_frame(stream_url, timeout=10)
        except Exception as exc:
            print(f"[!] Кадр не пришёл: {exc}")
            print(
                "Возможные причины: принтер в idle и "
                "стоковая камера не стримит,"
            )
            print(
                "FlashForge-приложение/веб-UI держит поток, "
                "или камера выключена."
            )
            sys.exit(1)
        out = Path("probe.jpg")
        out.write_bytes(jpeg)
        print(f"OK, {len(jpeg) // 1024} KB → {out.resolve()}")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f"{timestamp}_{args.label}" if args.label else timestamp
    frames_dir = args.output_dir / folder_name
    frames_dir.mkdir(parents=True, exist_ok=True)

    print("Таймлапс запущен.")
    print(f"  IP принтера: {args.ip}")
    print(f"  Поток:       {stream_url}")
    print(f"  Интервал:    {args.interval} сек")
    print(f"  FPS видео:   {args.fps}")
    print(f"  Папка:       {frames_dir}")
    print("  Стоп:        Ctrl+C")
    print()

    if status is None:
        print(
            "[i] /detail не отвечает — продолжаем, "
            "камеру всё равно попробуем дёргать."
        )
    else:
        printer_state = status.get("detail", {}).get("status")
        print(f"[i] /detail доступен, статус принтера: {printer_state}")

    signal.signal(signal.SIGINT, handle_sigint)

    frame_idx = 0
    failures = 0
    next_at = time.monotonic()

    while not stop_requested:
        try:
            jpeg = grab_frame(stream_url)
            path = frames_dir / f"frame_{frame_idx:06d}.jpg"
            path.write_bytes(jpeg)
            print(f"[{datetime.now():%H:%M:%S}] frame {frame_idx:06d}  "
                  f"{len(jpeg) // 1024} KB")
            frame_idx += 1
            failures = 0
        except Exception as exc:
            failures += 1
            ts = datetime.now().strftime("%H:%M:%S")
            print(
                f"[{ts}] ошибка кадра #{failures}: {exc}",
                file=sys.stderr,
            )
            if failures >= 10:
                print("[!] 10 ошибок подряд — выходим.", file=sys.stderr)
                break

        next_at += args.interval
        sleep_for = next_at - time.monotonic()
        if sleep_for < 0:
            next_at = time.monotonic()
            continue
        deadline = time.monotonic() + sleep_for
        while time.monotonic() < deadline and not stop_requested:
            time.sleep(min(0.5, deadline - time.monotonic()))

    print(f"\nОстановлено. Сохранено кадров: {frame_idx}")

    if frame_idx == 0:
        print("Кадров нет — видео не собираем.")
        return

    if args.no_video:
        print("Сборка видео пропущена (--no-video).")
        return

    print("Сборка видео через ffmpeg…")
    video = assemble_video(frames_dir, args.fps)
    if video:
        print(f"Готово: {video}")


if __name__ == "__main__":
    main()
