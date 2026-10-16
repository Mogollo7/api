#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Regresión visual: renderiza los documentos de aceptación y compara cada hoja (gris, 16 ppp) con la versión «golden» guardada.

    python servidor/regresion.py --comprobar          # falla si alguna hoja cambió más del umbral
    python servidor/regresion.py --actualizar         # acepta el resultado actual como nuevo golden (hazlo tras revisar el cambio)
    python servidor/regresion.py --comprobar --solo cine_ejemplo

Los golden están en servidor/tests/golden/<doc>.npz (hojas en gris a 16 ppp). Umbral: diferencia media > 1,5 niveles o > 0,6 % de píxeles cambiados más de 40 niveles.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render  # noqa: E402

ROOT = HERE.parent
GOLD = HERE / "tests/golden"
DOCS = {  # nombre: (contenido, carpeta de imágenes)
    "guia": ("contenido/guia.json", "teoria/imagenes"),
    "cine_ejemplo": ("contenido/cine_ejemplo.json", "teoria/imagenes"),
    "informe_ventas": ("contenido/informe_ventas.json", "contenido"),
    "manual_procedimiento": ("contenido/manual_procedimiento.json", "contenido"),
    "ficha_proyecto": ("contenido/ficha_proyecto.json", "contenido"),
}


def paginas(pdf: Path):
    with tempfile.TemporaryDirectory() as t:
        subprocess.run(["pdftoppm", "-r", "16", "-gray", "-png", str(pdf), str(Path(t) / "p")], check=True)
        return np.stack([np.asarray(Image.open(f)) for f in sorted(Path(t).glob("p-*.png"))]).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--comprobar", action="store_true")
    g.add_argument("--actualizar", action="store_true")
    ap.add_argument("--solo")
    a = ap.parse_args()
    GOLD.mkdir(parents=True, exist_ok=True)
    fallos = 0
    for name, (doc, imgs) in DOCS.items():
        if a.solo and a.solo != name:
            continue
        with tempfile.TemporaryDirectory() as t:
            out = Path(t) / "x.pdf"
            rep = render.run(ROOT / doc, out, ROOT / imgs)
            if rep["estado"] == "rechazado":
                print(f"✘ {name}: rechazado {rep['errores'][:1]}")
                fallos += 1
                continue
            cur = paginas(out)
        f = GOLD / f"{name}.npz"
        if a.actualizar or not f.exists():
            np.savez_compressed(f, p=cur)
            print(f"golden {'actualizado' if a.actualizar else 'creado'}: {name} ({cur.shape[0]} hojas, {f.stat().st_size//1024} KB)")
            continue
        old = np.load(f)["p"]
        if old.shape != cur.shape:
            print(f"✘ {name}: {old.shape[0]} hojas antes, {cur.shape[0]} ahora")
            fallos += 1
            continue
        bad = []
        for i, (o, c) in enumerate(zip(old.astype(int), cur.astype(int))):
            d = np.abs(o - c)
            if d.mean() > 1.5 or (d > 40).mean() > 0.006:
                bad.append((i + 1, round(float(d.mean()), 2), round(float((d > 40).mean()) * 100, 2)))
        print(("✔" if not bad else "✘"), name, f"{cur.shape[0]} hojas", ("" if not bad else f"· cambian: {bad[:8]}"))
        fallos += bool(bad)
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
