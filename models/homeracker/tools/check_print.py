"""Проверка печатаемости STL в текущей ориентации: нависания (overhangs), которым нужны поддержки.

Использование:
    python -I check_print.py <model.stl> [<base.stl>] [--angle 45]

Модель ставится на стол (min z -> 0). Грань считается нависанием, если смотрит вниз круче
порога от вертикали (по умолчанию 45° — типичный предел печати без поддержек) и не лежит на столе.
Связные нависающие грани объединяются в зоны; горизонтальные зоны (плоский «потолок»)
помечаются как мосты (bridge): короткие мосты до ~10 мм печатаются без поддержек.

Если передан base.stl (исходная модель до модификации), зоны, совпадающие с зонами base,
помечаются «было в исходнике» — так видно, что именно добавила модификация.
Только стандартная библиотека.
"""
import math
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # python -I не кладёт папку скрипта в sys.path
from check_mount import read_stl  # noqa: E402


def overhang_zones(tris, angle):
    z0 = min(v[2] for t in tris for v in t)
    lim = -math.sin(math.radians(angle))  # n_z ниже этого — нависание
    picked = []
    for t in tris:
        a, b, c = [(v[0], v[1], v[2] - z0) for v in t]
        e1 = [b[i] - a[i] for i in range(3)]
        e2 = [c[i] - a[i] for i in range(3)]
        n = [e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]]
        ln = math.sqrt(sum(x * x for x in n))
        if ln == 0:
            continue
        nz = n[2] / ln
        if nz < lim and max(a[2], b[2], c[2]) > 0.05:  # не грань на столе
            picked.append(((a, b, c), ln / 2, nz))
    # связность по общим вершинам
    by_v = defaultdict(list)
    for i, (t, _, _) in enumerate(picked):
        for v in t:
            by_v[tuple(round(x, 3) for x in v)].append(i)
    seen, zones = set(), []
    for i in range(len(picked)):
        if i in seen:
            continue
        stack, comp = [i], []
        seen.add(i)
        while stack:
            j = stack.pop()
            comp.append(j)
            for v in picked[j][0]:
                for k in by_v[tuple(round(x, 3) for x in v)]:
                    if k not in seen:
                        seen.add(k)
                        stack.append(k)
        pts = [v for j in comp for v in picked[j][0]]
        lo = [min(p[i] for p in pts) for i in range(3)]
        hi = [max(p[i] for p in pts) for i in range(3)]
        area = sum(picked[j][1] for j in comp)
        flat = all(picked[j][2] < -0.99 for j in comp)
        zones.append({"lo": lo, "hi": hi, "area": area, "flat": flat})
    return sorted(zones, key=lambda z: -z["area"])


def same(z, others, tol=0.3):
    return any(abs(z["area"] - o["area"]) < max(0.05 * o["area"], 0.05)
               and abs(z["lo"][2] - o["lo"][2]) < tol and abs(z["hi"][2] - o["hi"][2]) < tol
               for o in others)


def main(argv):
    angle = 45.0
    if "--angle" in argv:
        i = argv.index("--angle")
        angle = float(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    zones = overhang_zones(read_stl(argv[0]), angle)
    base = overhang_zones(read_stl(argv[1]), angle) if len(argv) > 1 else []
    print(f"Нависаний круче {angle:.0f}°: {len(zones)} зон, {sum(z['area'] for z in zones):.1f} мм²")
    new = 0
    for z in zones:
        span = min(z["hi"][0] - z["lo"][0], z["hi"][1] - z["lo"][1])
        kind = f"мост {span:.1f} мм" if z["flat"] else "наклон"
        origin = "было в исходнике" if base and same(z, base) else "НОВОЕ" if base else ""
        new += origin == "НОВОЕ"
        print(f"  {z['area']:7.1f} мм²  z {z['lo'][2]:5.1f}..{z['hi'][2]:5.1f}  "
              f"x {z['lo'][0]:6.1f}..{z['hi'][0]:6.1f}  y {z['lo'][1]:6.1f}..{z['hi'][1]:6.1f}  {kind}  {origin}")
    if base:
        print(f"Модификация добавила зон: {new}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # консоль Windows по умолчанию cp1251
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
