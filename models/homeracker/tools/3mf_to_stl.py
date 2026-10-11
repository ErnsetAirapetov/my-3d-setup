"""Вытащить меши из 3MF (Bambu/Orca) в бинарные STL — чтобы их можно было import() в OpenSCAD.

Использование:
    python -I 3mf_to_stl.py <file.3mf> <out_dir>

Каждый объект из 3D/Objects/*.model сохраняется как <out_dir>/<имя-объекта>.stl
в собственной системе координат меша (без трансформаций раскладки на столе).
Только стандартная библиотека.
"""
import re
import struct
import sys
import zipfile
from pathlib import Path

VERTEX = re.compile(r'<vertex x="([-\d.eE+]+)" y="([-\d.eE+]+)" z="([-\d.eE+]+)"')
TRIANGLE = re.compile(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"')


def write_stl(path, verts, tris):
    with open(path, "wb") as f:
        f.write(b"\0" * 80 + struct.pack("<I", len(tris)))
        for a, b, c in tris:
            f.write(struct.pack("<12fH", 0, 0, 0, *verts[a], *verts[b], *verts[c], 0))


def main(src, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(src) as z:
        for name in z.namelist():
            if not (name.startswith("3D/Objects/") and name.endswith(".model")):
                continue
            text = z.read(name).decode("utf-8")
            verts = [tuple(map(float, m)) for m in VERTEX.findall(text)]
            tris = [tuple(map(int, m)) for m in TRIANGLE.findall(text)]
            # "pi4b-top.stl_1.model" -> "pi4b-top"
            stem = Path(name).name.split(".stl")[0].removesuffix(".model")
            dst = out / f"{stem}.stl"
            write_stl(dst, verts, tris)
            print(f"{dst}: {len(verts)} вершин, {len(tris)} треугольников")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # консоль Windows по умолчанию cp1251
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
