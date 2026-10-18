#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Dibuja una terminal estilo Kali con la salida esperada de unos comandos y la enmarca con tres puntos (marco.py). Es una SIMULACIÓN: el título de la ventana lo dice.
"""python servidor/tools/terminal_sim.py contenido/medios/informe_linux/terminales.json -o contenido/medios/informe_linux [--fondo "#F8F7F2"]

El JSON es una lista de {"nombre": "x", "titulo": "brand@brandmachine: ~", "bloques": [{"cmd": "ls", "salida": ["línea 1", "línea 2"]}]}.
Escribe <nombre>.png. La salida es lo que el sistema DEBE mostrar según los permisos configurados; no es una captura real."""
import argparse
import json
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from marco import enmarcar  # noqa: E402

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BG, TXT, DIM, AZUL, VERDE = (27, 34, 48), (230, 233, 240), (170, 178, 192), (92, 156, 255), (80, 220, 140)


def dibujar(bloques, ancho=820, px=17, pad=22):
    f, fb = ImageFont.truetype(MONO, px), ImageFont.truetype(MONO_B, px)
    lh = int(px * 1.45)
    filas = []
    for b in bloques:
        filas.append(("prompt1", ""))
        filas.append(("prompt2", b["cmd"]))
        filas += [("out", s) for s in b.get("salida", [])]
        filas.append(("gap", ""))
    im = Image.new("RGB", (ancho, pad * 2 + lh * len(filas)), BG)
    d = ImageDraw.Draw(im)
    y = pad
    for tipo, s in filas:
        if tipo == "prompt1":
            d.text((pad, y), "┌──(", font=f, fill=VERDE)
            x = pad + d.textlength("┌──(", font=f)
            d.text((x, y), "brand@brandmachine", font=fb, fill=AZUL)
            x += d.textlength("brand@brandmachine", font=fb)
            d.text((x, y), ")-[~]", font=f, fill=VERDE)
        elif tipo == "prompt2":
            d.text((pad, y), "└─$ ", font=fb, fill=VERDE)
            d.text((pad + d.textlength("└─$ ", font=fb), y), s, font=f, fill=TXT)
        elif tipo == "out":
            d.text((pad, y), s, font=f, fill=DIM)
        y += lh
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("-o", "--salida", default=".")
    ap.add_argument("--fondo", default="#F8F7F2")
    a = ap.parse_args()
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)
    for t in json.loads(Path(a.spec).read_text(encoding="utf-8")):
        with tempfile.TemporaryDirectory() as tmp:
            crudo = Path(tmp) / "t.png"
            dibujar(t["bloques"]).save(crudo)
            enmarcar(str(crudo), str(out / f'{t["nombre"]}.png'), url=t.get("titulo", "brand@brandmachine: ~"), fondo=a.fondo, oscuro=True, margen=26, barra=40, radio=12)
        print("→", out / f'{t["nombre"]}.png')


if __name__ == "__main__":
    main()
