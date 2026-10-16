# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Plantillas de hoja de ANURA: portada, divisores A-D y hoja clara. Coordenadas del sistema (documentos.md), sin cambios.
El agente solo rellena campos (texto, variante); no se mueve ninguna coordenada."""
import base64
from pathlib import Path

from .assets import Symbols, sym_html
from .text import esc, inline, plain


def _img(design_dir: Path, rel: str) -> str:
    return "data:image/png;base64," + base64.b64encode((design_dir / rel).read_bytes()).decode()


def cover(doc_meta, cov, design_dir: Path, m, sym: Symbols, seed: int) -> str:
    t = m["templates"]["cover"]
    left = cov.get("header", doc_meta.get("header_left", ["Documento", "Para estudiantes"]))
    syms = "".join(
        sym_html(sym, sid, f'left:{s["left"]}cqw;top:{s["top"]}cqw;width:{s["size"]}cqw;height:{s["size"]}cqw;color:var(--{s["color"]})', "sc sym")
        for s, sid in zip(t["symbols"], cov.get("symbols", ["g90", "g84", "g32"]))
    )
    foot = t["foot_symbol"]
    return f'''<article class="page cover grain" aria-label="Portada">
  <div class="cv-h"><div class="cv-h1 micro">{"<br>".join(esc(x) for x in left)}</div><div class="cv-h3"><span class="caja">{esc(doc_meta.get("version",""))}</span></div></div>
  <div class="cv-v" aria-hidden="true" data-fit="v">{esc(cov["vertical"])}</div>
  <div class="cv-frame"><img src="{_img(design_dir, t["image"])}" alt="Rana de ojos grandes en monocromo negro y ocre"></div>
  {syms}
  <div class="cv-bot">
    <div class="cv-tit"><h2 data-fit="w">{esc(cov["title"])}</h2><p class="micro">{esc(cov["text"])}</p></div>
    <div class="cv-pie micro"><span>{esc(doc_meta.get("date",""))}</span>{sym_html(sym, cov.get("foot_symbol","g97"), f'width:{foot["size"]}cqw;height:{foot["size"]}cqw;color:var(--{foot["color"]})')}</div>
  </div>
</article>'''


def divider(variant, number, total, part, design_dir: Path, m, sym: Symbols, label="Parte") -> str:
    t = m["templates"]["divider"][variant]
    img = _img(design_dir, t["image"])
    lo = t["loose"]
    loose = sym_html(sym, lo["id"], f'left:{lo["left"]}cqw;top:{lo["top"]}cqw;width:{lo["size"]}cqw;height:{lo["size"]}cqw;color:var(--{lo["color"]})', "sc sym")
    head = f'<div class="hd micro"><span>{label} {number} / {total:02d}</span>{sym_html(sym, t["head_symbol"])}</div>'
    base = f'{head}<div class="num" aria-hidden="true">{number}</div><h4 class="ttl" data-fit="w" data-maxw="90">{esc(part["title"])}</h4><p class="desc micro{" dsc" if any(ch in part["title"] for ch in "gjpqy,") and variant != "A" else ""}">{esc(part["desc"])}</p>'
    if variant == "A":
        pic = f'<div class="disc"><img src="{img}" alt=""></div>'
    elif variant == "B":
        pic = f'<div class="foto"><img src="{img}" alt=""></div><svg class="drips" viewBox="0 0 100 40" aria-hidden="true"><use href="#drip"/></svg>'
    elif variant == "C":
        pic = f'<div class="franja"><img src="{img}" alt=""></div>'
    else:
        pic = f'<div class="foto"><img src="{img}" alt=""></div>'
    return f'<article class="page dv d{variant} grain" aria-label="Divisor {number}">{base}{pic}{loose}</article>'


DRIP = (Path(__file__).resolve().parent.parent / "designs/anura/drip.svg.txt")


def light(inner: str, tope: str, pie_l: str, page_no: int, sym: Symbols, sid: str, label: str, clave=False) -> str:
    tag = '<span class="caja-clave">Punto clave</span>' if clave else ""
    return f'''<article class="page lp" aria-label="{esc(label)}">
  <div class="tope">{sym_html(sym, sid)}<span class="tope-txt">{tag}{esc(tope)}</span></div>
  <div class="cont">{inner}</div>
  <div class="pie"><span>{esc(pie_l)}</span><span>{page_no:02d}</span></div>
</article>'''
