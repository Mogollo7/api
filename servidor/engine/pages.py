# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Plantillas de hoja de ANURA: portada (CV-1, CV-2, CV-3), divisores (DV-A … DV-F) y hoja clara.
Coordenadas del sistema (documentos.md) sin moverlas; el agente solo rellena campos y elige variante."""
import base64
from pathlib import Path

from . import assets, atoms_svg
from .assets import Symbols, sym_html
from .text import esc, inline, plain


class PageCtx:
    """Todo lo que una plantilla necesita: rutas, paleta, símbolos y caché."""

    def __init__(self, design_dir, manifest, roles, sym, images_root, cache, warn):
        self.design_dir, self.m, self.roles, self.sym = Path(design_dir), manifest, roles, sym
        self.images_root, self.cache, self.warn = Path(images_root), Path(cache), warn


def _b64(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def art(pc: PageCtx, default_rel, custom=None, treatment=None, tint=None):
    """Imagen de una plantilla: la foto del agente en dos tintas, o el arte del sistema repintado a la paleta. None = sin imagen."""
    if custom:
        f = pc.images_root / custom
        if f.exists():
            dk, lt = (tint or ["negro", "vivo"])
            tr = {"_t": [dk, lt]} if not treatment else pc.m["image_treatments"]
            out = assets.duotone(f, treatment if treatment else "_t", pc.roles, tr, pc.cache)
            return _b64(out)
        pc.warn.append({"bloque": custom, "causa": "imagen de plantilla no encontrada", "ajuste": "se usó el arte del sistema"})
    if not default_rel:
        return None
    return _b64(assets.recolor(pc.design_dir / default_rel, pc.roles, pc.cache))


def _syms(pc, items, ids):
    return "".join(
        sym_html(pc.sym, sid, f'left:{s["left"]}cqw;top:{s["top"]}cqw;width:{s["size"]}cqw;height:{s["size"]}cqw;color:var(--{s["color"]})', "sc sym")
        for s, sid in zip(items, ids)
    )


def cover(pc: PageCtx, meta, cov, variant="CV-1"):
    t = pc.m["templates"]["cover"]
    left = cov.get("header", meta.get("header_left", ["Documento", "Para estudiantes"]))
    foot = t["foot_symbol"]
    syms = _syms(pc, t["symbols"], cov.get("symbols", ["g90", "g84", "g32"]))
    head = (f'<div class="cv-h"><div class="cv-h1 micro">{"<br>".join(esc(x) for x in left)}</div>'
            f'<div class="cv-h3"><span class="caja">{esc(meta.get("version",""))}</span></div></div>')
    bot = (f'<div class="cv-bot"><div class="cv-tit"><h2 data-fit="w">{esc(cov["title"])}</h2><p class="micro">{esc(cov["text"])}</p></div>'
           f'<div class="cv-pie micro"><span>{esc(meta.get("date",""))}</span>'
           f'{sym_html(pc.sym, cov.get("foot_symbol","g97"), f"width:{foot["size"]}cqw;height:{foot["size"]}cqw;color:var(--{foot["color"]})")}</div></div>')
    tint = cov.get("tint", ["bosque", "ocre"])
    if variant == "CV-4":
        return cover_poster(pc, meta, cov)
    if variant == "CV-2":
        words = (cov.get("stack") or str(cov["vertical"]).split())[:3]
        mh = int(70 / (len(words) * 0.82))
        rows = "".join(f'<div class="cv2-row" data-fit="f" data-maxh="{mh}"><span>{esc(w)}</span></div>' for w in words)
        return (f'<article class="page cover cv2 grain" aria-label="Portada">{head}'
                f'<div class="cv2-t">{rows}</div>{syms}{bot}</article>')
    img = art(pc, t["image"], cov.get("image"), cov.get("treatment"), tint)
    if variant == "CV-3":
        pic = f'<img src="{img}" alt="{esc(cov.get("alt",""))}">' if img else ""
        return (f'<article class="page cover cv3 grain" aria-label="Portada">{head}<div class="cv3-win">{pic}</div>'
                f'<div class="cv3-t" data-fit="w">{esc(cov["vertical"])}</div>{syms}{bot}</article>')
    return (f'<article class="page cover grain" aria-label="Portada">{head}'
            f'<div class="cv-v" aria-hidden="true" data-fit="v">{esc(cov["vertical"])}</div>'
            f'<div class="cv-frame"><img src="{img}" alt="{esc(cov.get("alt","Rana en dos tintas"))}"></div>{syms}{bot}</article>')


def divider(pc: PageCtx, variant, number, total, part, label="Parte"):
    t = pc.m["templates"]["divider"][variant]
    lo = t["loose"]
    loose = sym_html(pc.sym, lo["id"], f'left:{lo["left"]}cqw;top:{lo["top"]}cqw;width:{lo["size"]}cqw;height:{lo["size"]}cqw;color:var(--{lo["color"]})', "sc sym")
    img = art(pc, t["image"], part.get("image"), part.get("treatment"), part.get("tint") or t.get("tint")) if variant != "F" else None
    cls = f"page dv d{variant} grain"
    style = []
    if part.get("bg"):
        cls += " bgc"
        style.append(f"--bg:var(--{part['bg']})")
    if part.get("num_color"):
        cls += " nc"
        style.append(f"--num:var(--{part['num_color']})")
    if part.get("title_color"):
        cls += " tc"
        style.append(f"--ttl:var(--{part['title_color']})")
    st = f' style="{";".join(style)}"' if style else ""
    if len(part["title"]) > 34:
        pc.warn.append({"bloque": f"divisor {number}", "causa": f"título de {len(part['title'])} caracteres", "ajuste": "se recortó a 34; usa un título corto"})
        part = {**part, "title": part["title"][:33].rstrip() + "…"}
    desc_cls = "desc micro" + (" dsc" if any(ch in part["title"] for ch in "gjpqy,") and variant not in ("A",) else "")
    head = f'<div class="hd micro"><span>{label} {number} / {total:02d}</span>{sym_html(pc.sym, t["head_symbol"])}</div>'
    base = (f'{head}<div class="num" aria-hidden="true">{number}</div><h4 class="ttl" data-fit="w">{esc(part["title"])}</h4>'
            f'<p class="{desc_cls}">{esc(part["desc"])}</p>')
    alt = esc(part.get("alt", ""))
    if variant == "A":
        pic = f'<div class="disc"><img src="{img}" alt="{alt}"></div>'
    elif variant == "B":
        pic = f'<div class="foto"><img src="{img}" alt="{alt}"></div><svg class="drips" viewBox="0 0 100 40" aria-hidden="true"><use href="#drip"/></svg>'
    elif variant == "C":
        pic = f'<div class="franja"><img src="{img}" alt="{alt}"></div>'
    elif variant == "E":
        pic = f'<div class="arco"><img src="{img}" alt="{alt}"></div>'
    elif variant == "F":
        pic = ""
    else:
        pic = f'<div class="foto"><img src="{img}" alt="{alt}"></div>'
    return f'<article class="{cls}"{st} aria-label="Divisor {number}">{base}{pic}{loose}</article>'


DRIP = Path(__file__).resolve().parent.parent / "designs/anura/drip.svg.txt"


def light(inner: str, tope: str, pie_l: str, page_no: int, sym: Symbols, sid: str, label: str, clave=False) -> str:
    tag = '<span class="caja-clave">Punto clave</span>' if clave else ""
    return f'''<article class="page lp" aria-label="{esc(label)}">
  <div class="tope">{sym_html(sym, sid)}<span class="tope-txt">{tag}{esc(tope)}</span></div>
  <div class="cont">{inner}</div>
  <div class="pie"><span>{esc(pie_l)}</span><span>{page_no:02d}</span></div>
</article>'''


def cover_poster(pc: PageCtx, meta, cov):
    """CV-4 · Cartel. Coordenadas medidas con descomponer.py sobre el cartel de referencia (A4, cqw). Campos opcionales:
    stack (filas del titular), badge {lines, tag}, image, quote, strip, number, list, notes, tagline, code, kicker."""
    left = cov.get("header", meta.get("header_left", ["Documento", "Para estudiantes"]))
    rows = cov.get("stack") or [w for w in str(cov["vertical"]).split()]
    rows = rows[:4]
    mh = int(62 / (len(rows) * 0.86))
    stack = "".join(f'<div class="cv4-row" data-fit="f" data-maxh="{mh}" style="height:{mh*0.86:.1f}cqw"><span>{esc(r)}</span></div>' for r in rows)
    bd = cov.get("badge") or {"lines": left[:1] + [meta.get("version", "")], "tag": ""}
    img = art(pc, None, cov.get("image"), cov.get("treatment"), cov.get("tint") or ["negro", "crema"])
    photo = f'<div class="cv4-foto"><img src="{img}" alt="{esc(cov.get("alt", ""))}"></div>' if img else '<div class="cv4-foto"></div>'
    notes = "".join(f'<div class="cv4-note" style="top:{y}cqw">{esc(t)}<i></i></div>' for t, y in zip(cov.get("notes", [])[:3], (42, 47.5, 59)))
    items = "".join(f"<li>{esc(t)}</li>" for t in cov.get("list", [])[:4])
    strip = " <u></u> ".join(esc(w) for w in cov.get("strip", []))
    quote = "<br>".join(esc(x) for x in cov.get("quote", []))
    tag = f'<div class="tag">{esc(bd.get("tag",""))}</div>' if bd.get("tag") else ""
    return f'''<article class="page cover cv4 grainm" aria-label="Portada">
  <div class="cv4-k"><b>{esc(cov.get("kicker", left[0]))}</b><span>{"<br>".join(esc(x) for x in left[1:])}</span><i></i></div>
  <div class="cv4-badge"><p>{"<br>".join(esc(x) for x in bd["lines"])}</p><i></i>{atoms_svg.cross().replace("atm-cross","atm-globe")}{tag}</div>
  <div class="cv4-stack">{stack}</div>
  {photo}
  <div class="cv4-quote"><p>{quote}</p><i></i></div>
  {notes}
  <div class="cv4-xb">{atoms_svg.xbox()}{atoms_svg.hazard()}</div>
  <div class="cv4-strip">{strip}</div>
  <div class="cv4-num">{esc(cov.get("number", ""))}</div>
  <ul class="cv4-list">{items}</ul>
  <div class="cv4-x">{atoms_svg.big_x()}</div>
  <div class="cv4-tagl">{esc(cov.get("tagline_l", "")) }</div>
  <div class="cv4-code">{atoms_svg.barcode(cov.get("code", cov["title"]))}<small>{esc(cov.get("code", ""))}</small><em>{esc(cov["text"])}</em></div>
  <div class="cv4-title">{esc(cov["title"])}</div>
  {atoms_svg.cross().replace("atm-cross","atm-cross c1")}{atoms_svg.cross().replace("atm-cross","atm-cross c2")}
</article>'''
