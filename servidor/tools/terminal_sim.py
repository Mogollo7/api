#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Enmarca terminales con una ventana brutalista (barra gris, tres puntos con borde negro, esquinas rectas, sin caja alrededor). Dibuja las simuladas (estilo Kali) y enmarca las capturas reales.
"""python servidor/tools/terminal_sim.py contenido/medios/informe_linux/terminales.json -o contenido/medios/informe_linux [--fondo "#F8F7F2"]

El JSON es una lista de entradas, cada una con "nombre" y "titulo":
  · simulada: "bloques": [{"cmd": "ls", "salida": ["línea 1"]}], "sim": true  → se dibuja la terminal; la barra lleva el sello SIMULACIÓN.
  · real:     "origen": "captura.png", "recorte": [x0, y0, x1, y1]            → se enmarca la captura tal cual (recorte opcional).
Escribe <nombre>.png. Una simulada muestra lo que el sistema DEBE responder según los permisos; no es una captura real."""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BG, TXT, DIM, AZUL, VERDE = (27, 34, 48), (230, 233, 240), (170, 178, 192), (92, 156, 255), (80, 220, 140)


ANCHO = 820


def dibujar(bloques, ancho=ANCHO, px=17, pad=22):
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


NEGRO, HOJA, VIVO, CREMA, ARENA = (5, 30, 36), (12, 70, 81), (230, 255, 43), (248, 247, 242), (137, 136, 143)


def marco_brutal(im, titulo, sim=False, fondo=(248, 247, 242), margen=6, barra=36):
    """Ventana plana: barra de arena con regla negra, tres puntos con borde negro (lima, crema, hoja) y esquinas rectas."""
    k = 2
    im = im.convert("RGB")
    w, h = im.size
    W, H = (w + 2 * margen) * k, (h + barra + 2 * margen) * k
    lienzo = Image.new("RGB", (W, H), tuple(fondo))
    d = ImageDraw.Draw(lienzo)
    x0, y0 = margen * k, margen * k
    d.rectangle((x0, y0, x0 + w * k, y0 + barra * k), fill=ARENA)
    d.rectangle((x0, y0 + barra * k - 3 * k, x0 + w * k, y0 + barra * k), fill=NEGRO)
    cy = y0 + (barra - 3) * k // 2
    for i, col in enumerate((VIVO, CREMA, HOJA)):
        cx = x0 + (20 + i * 24) * k
        r = 8 * k
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col, outline=NEGRO, width=2 * k)
    f = ImageFont.truetype(MONO_B, 13 * k)
    d.text((x0 + 104 * k, cy), titulo.upper(), font=f, fill=NEGRO, anchor="lm")
    if sim:
        t = "SIMULACIÓN"
        tw = d.textlength(t, font=f)
        d.rectangle((x0 + w * k - tw - 28 * k, cy - 11 * k, x0 + w * k - 10 * k, cy + 11 * k), fill=NEGRO)
        d.text((x0 + w * k - 19 * k - tw, cy), t, font=f, fill=VIVO, anchor="lm")
    lienzo.paste(im.resize((w * k, h * k), Image.LANCZOS), (x0, y0 + barra * k))
    return lienzo.resize((W // k, H // k), Image.LANCZOS)


def hex_rgb(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("-o", "--salida", default=".")
    ap.add_argument("--fondo", default="#F8F7F2")
    a = ap.parse_args()
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)
    base = Path(a.spec).resolve().parent
    for t in json.loads(Path(a.spec).read_text(encoding="utf-8")):
        if t.get("origen"):
            im = Image.open(base / t["origen"])
            if t.get("recorte"):
                im = im.crop(tuple(t["recorte"]))
        else:
            im = dibujar(t["bloques"])
        if im.width != ANCHO:        # mismo ancho en todas: la barra y los puntos salen del mismo tamaño en el documento
            im = im.convert("RGB").resize((ANCHO, round(im.height * ANCHO / im.width)), Image.LANCZOS)
        res = marco_brutal(im, t.get("titulo", "brand@brandmachine: ~"), bool(t.get("sim")), hex_rgb(a.fondo))
        res.save(out / f'{t["nombre"]}.png')
        print("→", out / f'{t["nombre"]}.png', res.size)


if __name__ == "__main__":
    main()
