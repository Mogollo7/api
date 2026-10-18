#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Encierra una captura en un marco de ventana (tres puntos de colores, barra con la dirección) y la guarda como PNG. Para el README y la documentación.
"""python servidor/tools/marco.py captura.png -o docs/media/home.png [--url http://127.0.0.1:8765/] [--fondo "#0b1020"] [--oscuro]
Sin --fondo la imagen sale con fondo transparente alrededor de la ventana."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ESC = 2  # supermuestreo para bordes suaves


def fuente(px):
    for f in ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if Path(f).exists():
            return ImageFont.truetype(f, px)
    return ImageFont.load_default()


def enmarcar(ruta, salida, url="", fondo=None, oscuro=False, margen=48, barra=46, radio=16):
    im = Image.open(ruta).convert("RGB")
    w, h = im.size
    W, H = (w + 2 * margen) * ESC, (h + barra + 2 * margen) * ESC
    lienzo = Image.new("RGBA", (W, H), fondo or (0, 0, 0, 0))
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ventana = (margen * ESC, margen * ESC, (margen + w) * ESC, (margen + barra + h) * ESC)
    ImageDraw.Draw(sombra).rounded_rectangle((ventana[0], ventana[1] + 14 * ESC, ventana[2], ventana[3] + 14 * ESC), radio * ESC, fill=(0, 0, 0, 110))
    lienzo.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(22 * ESC)))
    d = ImageDraw.Draw(lienzo)
    c_barra = (43, 46, 58, 255) if oscuro else (232, 232, 236, 255)
    d.rounded_rectangle(ventana, radio * ESC, fill=c_barra)
    cy = (margen + barra / 2) * ESC
    for i, col in enumerate(((255, 95, 87), (254, 188, 46), (40, 200, 64))):
        cx = (margen + 24 + i * 22) * ESC
        d.ellipse((cx - 7 * ESC, cy - 7 * ESC, cx + 7 * ESC, cy + 7 * ESC), fill=col + (255,))
    if url:
        f = fuente(13 * ESC)
        tw = d.textlength(url, font=f)
        ux0 = (margen + w / 2) * ESC - max(tw / 2 + 18 * ESC, 150 * ESC)
        d.rounded_rectangle((ux0, cy - 14 * ESC, W - ux0, cy + 14 * ESC), 8 * ESC, fill=(30, 32, 40, 255) if oscuro else (250, 250, 252, 255))
        d.text((W / 2, cy), url, font=f, fill=(190, 194, 206, 255) if oscuro else (90, 94, 106, 255), anchor="mm")
    cont = Image.new("RGBA", (w * ESC, h * ESC))
    cont.paste(im.resize((w * ESC, h * ESC), Image.LANCZOS))
    mascara = Image.new("L", cont.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, -radio * ESC, cont.width, cont.height), radio * ESC, fill=255)      # esquinas redondas solo abajo
    lienzo.paste(cont, (margen * ESC, (margen + barra) * ESC), mascara)
    out = lienzo.resize((W // ESC, H // ESC), Image.LANCZOS)
    Path(salida).parent.mkdir(parents=True, exist_ok=True)
    out.save(salida)
    return out.size


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--") and x not in ("-o",)]
    opt = lambda k, d="": sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d      # noqa: E731
    if not a:
        print(__doc__)
    else:
        print(enmarcar(a[0], opt("-o", "marco.png"), opt("--url"), opt("--fondo") or None, "--oscuro" in sys.argv))
