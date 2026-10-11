"""Проверка STL крепления HomeRacker: цельность меша, габариты, отверстия по сетке.

Использование:
    python -I check_mount.py <mount.stl> [gap_units=5] [width_units=2]

Ожидает систему координат hr_front_mount (см. homeracker.scad):
лицевой торец в x = 0, высота стойки по Y (центр в 0), слот по Z от 0.
Только стандартная библиотека. Код возврата 1, если что-то не сошлось.
"""
import struct
import sys
from collections import Counter

UNIT, CLEAR, HOLE, EAR_T = 15, 0.25, 4.25, 2


def read_stl(path):
    data = open(path, "rb").read()
    if data[:5] == b"solid" and b"facet" in data[:300]:
        tris, cur = [], []
        for line in data.decode().splitlines():
            p = line.split()
            if p and p[0] == "vertex":
                cur.append(tuple(map(float, p[1:4])))
                if len(cur) == 3:
                    tris.append(tuple(cur))
                    cur = []
        return tris
    n = struct.unpack_from("<I", data, 80)[0]
    return [
        tuple(struct.unpack_from("<3f", data, 84 + i * 50 + 12 + k * 12) for k in range(3))
        for i in range(n)
    ]


def inside(tris, p, d=(0.5773, 0.5774, 0.5773)):
    """Чётность пересечений луча (Möller–Trumbore)."""
    hits = 0
    for a, b, c in tris:
        e1 = [b[i] - a[i] for i in range(3)]
        e2 = [c[i] - a[i] for i in range(3)]
        h = [d[1] * e2[2] - d[2] * e2[1], d[2] * e2[0] - d[0] * e2[2], d[0] * e2[1] - d[1] * e2[0]]
        det = sum(e1[i] * h[i] for i in range(3))
        if abs(det) < 1e-12:
            continue
        s = [p[i] - a[i] for i in range(3)]
        u = sum(s[i] * h[i] for i in range(3)) / det
        if u < 0 or u > 1:
            continue
        q = [s[1] * e1[2] - s[2] * e1[1], s[2] * e1[0] - s[0] * e1[2], s[0] * e1[1] - s[1] * e1[0]]
        v = sum(d[i] * q[i] for i in range(3)) / det
        if v < 0 or u + v > 1:
            continue
        if sum(e2[i] * q[i] for i in range(3)) / det > 1e-9:
            hits += 1
    return hits % 2 == 1


def main(path, gap_units=5, width_units=2):
    tris = read_stl(path)
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        ok &= cond
        print(f"[{'OK ' if cond else 'FAIL'}] {name} {detail}")

    # 1. Цельность: каждое ребро ровно у двух треугольников.
    edges = Counter()
    for t in tris:
        vs = [tuple(round(c, 4) for c in v) for v in t]
        for i in range(3):
            edges[tuple(sorted((vs[i], vs[(i + 1) % 3])))] += 1
    bad = sum(1 for n in edges.values() if n != 2)
    check("меш замкнут (manifold)", bad == 0, f"треугольников {len(tris)}, плохих рёбер {bad}")

    # 2. Габариты.
    xs, ys, zs = zip(*[v for t in tris for v in t])
    w = width_units * UNIT - 2 * CLEAR
    y_ear = (gap_units / 2 + 1) * UNIT - CLEAR
    check("ширина слота по Z", abs(min(zs)) < 0.01 and abs(max(zs) - w) < 0.01, f"{min(zs):.2f}..{max(zs):.2f}, ждём 0..{w}")
    check("высота по Y (с ушками)", abs(max(ys) - y_ear) < 0.01 and abs(min(ys) + y_ear) < 0.01,
          f"{min(ys):.2f}..{max(ys):.2f}, ждём ±{y_ear}")
    check("лицевой торец в x = 0", abs(max(xs)) < 0.01, f"max x = {max(xs):.2f}")

    # 3. Отверстия: центр пуст, материал вокруг на месте.
    y_pin = (gap_units + 1) * UNIT / 2
    centers = [-CLEAR + UNIT / 2 + i * UNIT for i in range(width_units)]
    x_mid = -EAR_T / 2
    for sy in (1, -1):
        for zc in centers:
            p = (x_mid, sy * y_pin, zc)
            check(f"отверстие y={sy * y_pin:+.1f} z={zc:.2f} сквозное", not inside(tris, p))
            ring = [(x_mid, sy * y_pin + dy, zc + dz) for dy, dz in
                    ((HOLE / 2 + 0.6, 0), (-HOLE / 2 - 0.6, 0), (0, HOLE / 2 + 0.6), (0, -HOLE / 2 - 0.6))
                    if 0 < zc + dz < w]
            check(f"  стенки вокруг отверстия", all(inside(tris, q) for q in ring))
        y_sp = gap_units * UNIT / 2 - CLEAR - 1  # у грани опоры
        check(f"проставка y={sy * y_sp:+.1f} на месте", inside(tris, (-EAR_T - 5, sy * y_sp, w - 2)))

    print("ИТОГ:", "всё сходится" if ok else "есть проблемы")
    return ok


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # консоль Windows по умолчанию cp1251
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(0 if main(sys.argv[1], *map(int, sys.argv[2:])) else 1)
