#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Lee una imagen de referencia (captura de una web, afiche, PDF de una página) y propone el estilo: modo claro/oscuro, acento, los 7 roles y el comando de la fábrica.
"""python servidor/referencia.py <imagen|pdf> [--id arcano] [--png salida.png]      → JSON con paleta, modo, acento, piel sugerida y el comando

No adivina la tipografía (una imagen no trae fuentes): da la clase (geométrica, display grueso, serif…) por la forma de los colores solo como pista; si el usuario nombra una fuente, esa manda.
Después del comando de la fábrica sigue el proceso de designs/LEEME.md: símbolos con tools/descomponer.py, variantes con fabrica_estilo.py variante, validar_diseno.py."""
import colorsys
import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent


def _lum(c):
    r, g, b = (x / 255 for x in c)
    return .2126 * r + .7152 * g + .0722 * b


def _sat(c):
    h, l, s = colorsys.rgb_to_hls(*(x / 255 for x in c))
    return s * (1 - abs(2 * l - 1))          # saturación visible: un gris muy oscuro o muy claro no cuenta


def _hex(c):
    return "#%02X%02X%02X" % tuple(c)


def cargar(ruta):
    p = Path(ruta)
    if p.suffix.lower() == ".pdf":
        import pymupdf
        pix = pymupdf.open(str(p))[0].get_pixmap(dpi=60)
        return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return Image.open(p).convert("RGB")


def analizar(ruta, id_="estilo-nuevo"):
    im = cargar(ruta)
    im.thumbnail((240, 240))
    q = im.quantize(colors=10, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[:30]
    cuentas = sorted(q.getcolors(), reverse=True)
    cols = [(n, tuple(pal[i * 3:i * 3 + 3])) for n, i in cuentas]
    total = sum(n for n, _ in cols)
    media = sum(n * _lum(c) for n, c in cols) / total
    oscuro = media < .35
    fondo = cols[0][1]
    px = list(im.getdata())
    bins = {}
    for c in px:                                           # los colores de marca son los vivos y claros, no el promedio del degradado
        h, l, sa = colorsys.rgb_to_hls(*(x / 255 for x in c))
        if sa > .55 and .3 < l < .75:
            bins.setdefault(int(h * 24), []).append(c)
    orden = sorted(bins.values(), key=len, reverse=True)
    media_c = lambda g: tuple(round(sum(c[i] for c in g) / len(g)) for i in range(3))      # noqa: E731
    acento = media_c(orden[0]) if orden else cols[1][1]
    segundo = None
    for g in orden[1:]:
        m = media_c(g)
        if len(g) > len(px) * .004 and abs(colorsys.rgb_to_hls(*(x / 255 for x in m))[0] - colorsys.rgb_to_hls(*(x / 255 for x in acento))[0]) > .12:
            segundo = m
            break
    claros = sorted((c for _, c in cols), key=_lum, reverse=True)
    roles = {"fondo": _hex(fondo), "acento": _hex(acento), "acento2": _hex(segundo) if segundo else None, "texto_claro": _hex(claros[0]), "texto_oscuro": _hex(sorted((c for _, c in cols), key=_lum)[0])}
    h, l, s = colorsys.rgb_to_hls(*(x / 255 for x in acento))
    piel = "redonda" if (s < .7 and not oscuro) else ("recta" if oscuro and s > .6 else "suave")
    cmd = f'python servidor/fabrica_estilo.py estilo {id_} --acento "{_hex(acento)}" --piel {piel}' + (" --modo oscuro" if oscuro else "")
    return {"modo": "oscuro" if oscuro else "claro", "luminancia_media": round(media, 2), "colores": [{"hex": _hex(c), "peso": round(n / total, 3)} for n, c in cols], "roles": roles,
            "piel_sugerida": piel, "comando": cmd,
            "siguiente": ["Pide al usuario la tipografía (o elige una de designs/*/fonts); si no hay, Archivo.", "Separa símbolos: python servidor/tools/descomponer.py <imagen> -o referencias/<id>",
                          f"Ejecuta el comando; después: python servidor/fabrica_estilo.py variante {id_} --tipo portada --fondo acento --nuevo CV-3", f"Valida: python servidor/validar_diseno.py {id_}",
                          "Mira el resultado con la herramienta screenshot y compara con la referencia."]}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not a:
        print(__doc__)
    else:
        print(json.dumps(analizar(a[0], sys.argv[sys.argv.index("--id") + 1] if "--id" in sys.argv else "estilo-nuevo"), ensure_ascii=False, indent=1))
