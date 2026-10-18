#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Convierte las fuentes .woff2 de un diseño a .ttf (PowerPoint y Word no leen woff2) y las empaqueta en un zip.
"""python servidor/tools/fuentes_ttf.py anura   -> designs/anura/fonts/ttf/*.ttf y designs/anura/fonts/fuentes-anura.zip"""
import sys
import zipfile
from pathlib import Path

from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parents[1]


def build(design: str) -> Path:
    src = HERE / "designs" / design / "fonts"
    out = src / "ttf"
    out.mkdir(exist_ok=True)
    z = src / f"fuentes-{design}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(src.glob("*.woff2")):
            t = TTFont(f)
            t.flavor = None
            dst = out / (f.stem + ".ttf")
            t.save(dst)
            zf.write(dst, dst.name)
        lic = [p for p in src.glob("*") if p.suffix.lower() in (".txt", ".md")]
        for p in lic:
            zf.write(p, p.name)
    return z


if __name__ == "__main__":
    for d in sys.argv[1:] or [p.name for p in (HERE / "designs").iterdir() if (p / "fonts").is_dir()]:
        print(build(d))
