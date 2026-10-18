# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Portadas y divisores: el motor NO conoce ningún diseño. Cada diseño trae sus plantillas en designs/<id>/templates/
(`cover.<ID>.html`, `divider.<ID>.html`) con campos {{…}} (ver engine/tpl.py y designs/LEEME.md); aquí solo se arma el contexto.
Las coordenadas, clases y símbolos sueltos viven en el manifiesto y en el CSS del diseño."""
import base64
from pathlib import Path

from . import assets, atoms_svg, tpl
from .assets import Symbols, sym_html
from .text import esc, plain


class PageCtx:
    """Todo lo que una plantilla necesita: rutas, paleta, símbolos y caché."""

    def __init__(self, design_dir, manifest, roles, sym, images_root, cache, warn):
        self.design_dir, self.m, self.roles, self.sym = Path(design_dir), manifest, roles, sym
        self.images_root, self.cache, self.warn = Path(images_root), Path(cache), warn
        self.missing = []       # fotos de portada/divisor pedidas con `need` y aún sin archivo


def _b64(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def _need_art(pc: PageCtx, custom, need):
    """Recuadro «IMAGEN NECESARIA» (SVG) para una foto de plantilla pedida con `need` que aún no existe: nunca se sustituye por arte por defecto."""
    from html import escape
    pc.missing.append({"src": custom, "need": need})
    arena, negro = pc.roles.get("arena", "#cccccc"), pc.roles.get("negro", "#000000")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid slice"><rect width="100" height="100" fill="{arena}"/>'
           f'<path d="M0 0L100 100M100 0L0 100" stroke="{negro}" stroke-opacity=".25" stroke-width=".5"/>'
           f'<text x="50" y="48" text-anchor="middle" font-family="monospace" font-weight="700" font-size="7" fill="{negro}">IMAGEN</text>'
           f'<text x="50" y="57" text-anchor="middle" font-family="monospace" font-weight="700" font-size="7" fill="{negro}">NECESARIA</text></svg>')
    return "data:image/svg+xml;utf8," + svg.replace("#", "%23").replace("<", "%3C").replace(">", "%3E").replace('"', "'")


def art(pc: PageCtx, default_rel, custom=None, treatment=None, tint=None, need=None):
    """Imagen de una plantilla: la foto del agente en dos tintas, o el arte del diseño repintado a la paleta. None = sin imagen.
    Con `need` y sin archivo, dibuja «IMAGEN NECESARIA» en vez del arte del diseño."""
    if custom:
        f = pc.images_root / custom
        if not f.exists() and need:
            return _need_art(pc, custom, need)
        if f.exists():
            dk, lt = (tint or ["negro", "vivo"])
            tr = {"_t": [dk, lt]} if not treatment else pc.m["image_treatments"]
            return _b64(assets.duotone(f, treatment if treatment else "_t", pc.roles, tr, pc.cache))
        pc.warn.append({"bloque": custom, "causa": "imagen de plantilla no encontrada", "ajuste": "se usó el arte del diseño"})
    if not default_rel:
        return None
    f = pc.design_dir / default_rel
    return _b64(assets.recolor(f, pc.roles, pc.cache)) if f.exists() else None


def _template(pc: PageCtx, kind: str, vid: str):
    f = pc.design_dir / "templates" / f"{kind}.{vid}.html"
    if f.exists():
        return f.read_text(encoding="utf-8"), vid
    alts = sorted((pc.design_dir / "templates").glob(f"{kind}.*.html"))
    if not alts:
        raise FileNotFoundError(f"el diseño no trae plantillas {kind}.*.html")
    pc.warn.append({"bloque": f"{kind} {vid}", "causa": "el diseño no trae esa plantilla", "ajuste": f"se usó {alts[0].stem.split('.', 1)[1]}"})
    return alts[0].read_text(encoding="utf-8"), alts[0].stem.split(".", 1)[1]


def _atoms():
    return {"barcode": None, "hazard": atoms_svg.hazard(), "xbox": atoms_svg.xbox(), "big_x": atoms_svg.big_x(),
            "globe": atoms_svg.cross().replace("atm-cross", "atm-globe"), "cross1": atoms_svg.cross().replace("atm-cross", "atm-cross c1"),
            "cross2": atoms_svg.cross().replace("atm-cross", "atm-cross c2")}


def cover(pc: PageCtx, meta, cov, variant="CV-1"):
    t = pc.m["templates"]["cover"]
    src, variant = _template(pc, "cover", variant)
    left = cov.get("header", meta.get("header_left", ["Documento", "Para estudiantes"]))
    foot = t["foot_symbol"]
    slots = (t.get("symbols_by_variant") or {}).get(variant, t["symbols"])
    syms = "".join(
        sym_html(pc.sym, sid, f'left:{s["left"]}cqw;top:{s["top"]}cqw;width:{s["size"]}cqw;height:{s["size"]}cqw;color:var(--{s["color"]})', "sc sym")
        for s, sid in zip(slots, cov.get("symbols", ["g90", "g84", "g32"])))
    tint = cov.get("tint", ["bosque", "ocre"])
    img = art(pc, t.get("image"), cov.get("image"), cov.get("treatment"), tint if variant != "CV-4" else (cov.get("tint") or ["negro", "crema"]), cov.get("need"))
    if variant == "CV-4":
        img = art(pc, None, cov.get("image"), cov.get("treatment"), cov.get("tint") or ["negro", "crema"], cov.get("need"))
    words = (cov.get("stack") or str(cov["vertical"]).split())
    n2, n4 = min(len(words), 3), min(len(words), 4)
    bd = cov.get("badge") or {"lines": left[:1] + [meta.get("version", "")], "tag": ""}
    atoms = _atoms()
    atoms["barcode"] = atoms_svg.barcode(cov.get("code", cov["title"]))
    ctx = {
        "meta": meta, "cover": cov, "header_html": "<br>".join(esc(x) for x in left), "img": img or "", "alt": cov.get("alt", "Imagen en dos tintas"),
        "syms": syms, "foot_sym": sym_html(pc.sym, cov.get("foot_symbol", "g97"), f'width:{foot["size"]}cqw;height:{foot["size"]}cqw;color:var(--{foot["color"]})'),
        "words": [{"text": w, "mh": int((t.get("words_height", 70) - (n2 - 1) * 1.8) / (n2 * 0.86))} for w in words[:3]],
        "stack_rows": [{"text": w, "mh": int(62 / (n4 * 0.86)), "h": f"{int(62 / (n4 * 0.86)) * 0.86:.1f}"} for w in words[:4]],
        "kicker": cov.get("kicker", left[0]), "kicker_rest_html": "<br>".join(esc(x) for x in left[1:]),
        "badge": bd, "badge_lines_html": "<br>".join(esc(x) for x in bd["lines"]), "quote_html": "<br>".join(esc(x) for x in cov.get("quote", [])),
        "strip_html": " <u></u> ".join(esc(w) for w in cov.get("strip", [])), "list_items": cov.get("list", [])[:4],
        "note_items": [{"text": tx, "y": y} for tx, y in zip(cov.get("notes", [])[:3], (42, 47.5, 59))], "atoms": atoms,
    }
    return tpl.render(src, ctx)


def divider(pc: PageCtx, variant, number, total, part, label="Parte"):
    vid = variant if str(variant).startswith("DV-") else "DV-" + str(variant)
    src, vid = _template(pc, "divider", vid)
    key = vid[-1]
    t = pc.m["templates"]["divider"].get(key) or next(iter(pc.m["templates"]["divider"].values()))
    lo = t["loose"]
    loose = sym_html(pc.sym, lo["id"], f'left:{lo["left"]}cqw;top:{lo["top"]}cqw;width:{lo["size"]}cqw;height:{lo["size"]}cqw;color:var(--{lo["color"]})', "sc sym")
    img = art(pc, t.get("image"), part.get("image"), part.get("treatment"), part.get("tint") or t.get("tint"), part.get("need")) if t.get("image") is not None or part.get("image") else None
    cls = f"page dv d{key} grain"
    style = []
    for k, c in (("bg", "bgc"), ("num_color", "nc"), ("title_color", "tc")):
        if part.get(k):
            cls += f" {c}"
            style.append(f"--{ {'bg':'bg','num_color':'num','title_color':'ttl'}[k] }:var(--{part[k]})")
    if len(part["title"]) > 34:
        pc.warn.append({"bloque": f"divisor {number}", "causa": f"título de {len(part['title'])} caracteres", "ajuste": "se recortó a 34; usa un título corto"})
        part = {**part, "title": part["title"][:33].rstrip() + "…"}
    ctx = {"cls": cls, "style_attr": f' style="{";".join(style)}"' if style else "", "number": number, "total": f"{total:02d}", "label": label, "part": part,
           "desc_cls": "desc micro" + (" dsc" if any(ch in part["title"] for ch in "gjpqy,") and key != "A" else ""),
           "head_sym": sym_html(pc.sym, t["head_symbol"]), "loose_sym": loose, "img": img or "", "alt": esc(part.get("alt", ""))}
    return tpl.render(src, ctx)


def light(inner: str, tope: str, pie_l: str, page_no: int, sym: Symbols, sid: str, label: str, clave=False) -> str:
    tag = '<span class="caja-clave">Punto clave</span>' if clave else ""
    return f'''<article class="page lp" aria-label="{esc(label)}">
  <div class="tope">{sym_html(sym, sid)}<span class="tope-txt">{tag}{esc(tope)}</span></div>
  <div class="cont">{inner}</div>
  <div class="pie"><span>{esc(pie_l)}</span><span>{page_no:02d}</span></div>
</article>'''
