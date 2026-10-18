#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Recursos gráficos generados por código (patrones, fondos, ondas, iconos): SVG + PNG en imagenes/recursos/ y ficha en la biblioteca.
"""python servidor/recursos.py crear <tipo> <id> [--color "#7C3AED"] [--color2 "#F2E6F8"] [--tam 40] [--ancho 1600 --alto 900] [--icono leaf]
python servidor/recursos.py iconos [texto]       (busca entre los 2 100 iconos Lucide, licencia ISC)

Tipos: puntos, rejilla, lineas (diagonales), ondas, degradado, ruido, marco, icono.
El PNG se usa en un bloque `image` con src «recursos/<id>.png» (el motor solo lee rasters); el SVG queda al lado para web y edición.
Cada recurso lleva ficha en la biblioteca (tipo «recurso») con su licencia: lo generado por código es «propia»; los iconos Lucide son ISC."""
import argparse
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMG = HERE.parent / "imagenes" / "recursos"
LUCIDE = HERE / "tools" / "node" / "node_modules" / "lucide-static" / "icons"
TIPOS = ("puntos", "rejilla", "lineas", "ondas", "degradado", "ruido", "marco", "icono")


def svg(w, h, cuerpo, fondo=None):
    f = f'<rect width="{w}" height="{h}" fill="{fondo}"/>' if fondo else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{f}{cuerpo}</svg>'


def puntos(w, h, c, c2, tam, **_):
    r = max(2, tam // 8)
    return svg(w, h, "".join(f'<circle cx="{x + tam // 2}" cy="{y + tam // 2}" r="{r}" fill="{c}"/>' for y in range(0, h, tam) for x in range(0, w, tam)), c2)


def rejilla(w, h, c, c2, tam, **_):
    return svg(w, h, "".join(f'<path d="M{x} 0V{h}" stroke="{c}" stroke-width="2"/>' for x in range(0, w + 1, tam)) + "".join(f'<path d="M0 {y}H{w}" stroke="{c}" stroke-width="2"/>' for y in range(0, h + 1, tam)), c2)


def lineas(w, h, c, c2, tam, **_):
    return svg(w, h, "".join(f'<path d="M{x} 0L{x - h} {h}" stroke="{c}" stroke-width="{max(2, tam // 10)}"/>' for x in range(0, w + h, tam)), c2)


def ondas(w, h, c, c2, tam, **_):
    cuerpo = ""
    for i, y in enumerate(range(tam, h + tam, tam)):
        d = f"M0 {y}" + "".join(f" q{tam} {-tam // 2 if k % 2 == 0 else tam // 2} {tam * 2} 0" for k in range(0, w // (tam * 2) + 2))
        cuerpo += f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{max(2, tam // 10)}"/>'
    return svg(w, h, cuerpo, c2)


def degradado(w, h, c, c2, **_):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c2}"/>'
            f'<stop offset="1" stop-color="{c}"/></linearGradient></defs><rect width="{w}" height="{h}" fill="url(#g)"/></svg>')


def ruido(w, h, c, c2, tam, **_):
    rnd = random.Random(7)
    return svg(w, h, "".join(f'<circle cx="{rnd.randrange(w)}" cy="{rnd.randrange(h)}" r="{rnd.choice((1, 1, 2, 3))}" fill="{c}" opacity="{rnd.choice((.2, .35, .5))}"/>' for _ in range(w * h // 900)), c2)


def marco(w, h, c, c2, tam, **_):
    g = max(4, tam // 4)
    return svg(w, h, f'<rect x="{tam}" y="{tam}" width="{w - 2 * tam}" height="{h - 2 * tam}" fill="none" stroke="{c}" stroke-width="{g}"/><rect x="{tam + 2 * g}" y="{tam + 2 * g}" width="{w - 2 * tam - 4 * g}" height="{h - 2 * tam - 4 * g}" fill="none" stroke="{c}" stroke-width="2"/>', c2)


def icono(w, h, c, c2, tam, nombre="leaf", **_):
    f = LUCIDE / f"{nombre}.svg"
    if not f.exists():
        raise ValueError(f"no hay icono '{nombre}'; busca con: python servidor/recursos.py iconos <texto>")
    cuerpo = re.sub(r"<svg[^>]*>|</svg>|<!--.*?-->", "", f.read_text(encoding="utf-8"), flags=re.S)
    lado = min(w, h)
    return svg(w, h, f'<g transform="translate({(w - lado) / 2} {(h - lado) / 2}) scale({lado / 24})" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{cuerpo}</g>', c2 if c2 != "none" else None)


GEN = {"puntos": puntos, "rejilla": rejilla, "lineas": lineas, "ondas": ondas, "degradado": degradado, "ruido": ruido, "marco": marco, "icono": icono}


def iconos(q=""):
    q = q.lower().strip()
    return [f.stem for f in sorted(LUCIDE.glob("*.svg")) if not q or q in f.stem][:60] if LUCIDE.exists() else []


def crear(tipo, id_, color="#7C3AED", color2="#FFFFFF", tam=40, ancho=1600, alto=900, icono_nombre="leaf"):
    """Escribe imagenes/recursos/<id>.svg y .png, y la ficha en la biblioteca. Devuelve {src, svg, ficha}."""
    import biblioteca
    import pymupdf
    if tipo not in GEN:
        raise ValueError(f"tipo debe ser uno de {', '.join(TIPOS)}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,40}", id_):
        raise ValueError("id en minúsculas (a-z, 0-9, - _)")
    for c in (color, color2):
        if c != "none" and not re.fullmatch(r"#[0-9a-fA-F]{6}", c):
            raise ValueError("los colores van como #rrggbb")
    ancho, alto, tam = (max(64, min(4000, int(v))) for v in (ancho, alto, tam))
    s = GEN[tipo](ancho, alto, color, color2, tam, nombre=icono_nombre)
    IMG.mkdir(parents=True, exist_ok=True)
    (IMG / f"{id_}.svg").write_text(s, encoding="utf-8")
    doc = pymupdf.open(stream=s.encode(), filetype="svg")
    doc[0].get_pixmap(matrix=pymupdf.Matrix(1, 1)).save(str(IMG / f"{id_}.png"))
    lic = "ISC (Lucide)" if tipo == "icono" else "propia (generado por código)"
    ficha = biblioteca.guardar({"id": f"recurso-{id_}", "tipo": "recurso", "nombre": f"{tipo.capitalize()} {id_}", "version": "1", "tags": [tipo, "recurso", "fondo", "patron", "imagen"],
                                "descripcion": f"Recurso gráfico «{tipo}» {ancho}×{alto}, colores {color} sobre {color2}.", "uso": f"Bloque image con src «recursos/{id_}.png»; úsalo de fondo o separador.",
                                "ejemplo": {"type": "image", "src": f"recursos/{id_}.png", "ratio": "16/9", "alt": f"{tipo} decorativo"}, "origen": "recursos.py", "licencia": lic}, sobrescribir=True)
    creditos = HERE.parent / "imagenes" / "creditos.csv"
    if creditos.exists() and f"recursos/{id_}.png" not in creditos.read_text(encoding="utf-8"):
        with creditos.open("a", encoding="utf-8", newline="") as fh:
            fh.write(f"recursos/{id_}.png,{tipo},recurso decorativo,,myStyle,{lic}\n")
    return {"src": f"recursos/{id_}.png", "svg": f"recursos/{id_}.svg", "ficha": ficha["id"], "licencia": lic}


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.path.insert(0, str(HERE))
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("crear")
    c.add_argument("tipo", choices=TIPOS)
    c.add_argument("id")
    c.add_argument("--color", default="#7C3AED")
    c.add_argument("--color2", default="#FFFFFF")
    c.add_argument("--tam", type=int, default=40)
    c.add_argument("--ancho", type=int, default=1600)
    c.add_argument("--alto", type=int, default=900)
    c.add_argument("--icono", default="leaf")
    i = sp.add_parser("iconos")
    i.add_argument("texto", nargs="?", default="")
    a = ap.parse_args()
    if a.cmd == "iconos":
        print(", ".join(iconos(a.texto)))
    else:
        print(json.dumps(crear(a.tipo, a.id, a.color, a.color2, a.tam, a.ancho, a.alto, a.icono), ensure_ascii=False))


if __name__ == "__main__":
    main()
