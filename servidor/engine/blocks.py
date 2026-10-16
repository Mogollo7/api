# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Bloques declarativos -> HTML. El agente no escribe HTML ni CSS: aquí se decide cómo se ve cada bloque."""
from pathlib import Path

import json
from html.parser import HTMLParser

from . import charts, diagram
from .assets import duotone
from .text import esc, inline, num, plain

LABELS = {"nota": "Nota", "clave": "Punto clave", "ojo": "Ojo", "sim": "Simulación", "pend": "Dato pendiente", "regla": "Regla",
          "slate": "Atención", "hueco": "Nota"}
CALLOUT_TONES = set(LABELS)
TONES = {"f": "t-f", "p": "t-p", "l": "t-l", "n": "t-n"}


class Ctx:
    def __init__(self, manifest, roles, images_root, credits, cache, toc=None, design_dir=None):
        self.manifest, self.roles = manifest, roles
        self.design_dir = Path(design_dir) if design_dir else None
        self.warn = []          # degradaciones: bloque no estándar, gráfico inválido, variante desconocida...
        self._outlines = None
        self.images_root, self.credits, self.cache = Path(images_root), credits, Path(cache)
        self.images_used = []   # (archivo, credit_row) para la página de créditos automática
        self.missing = []       # imágenes marcadas "IMAGEN NECESARIA"
        self.no_credit = []     # imágenes usadas sin fila en creditos.csv
        self.toc = toc or []
        self.img_i = 0


    def outlines(self):
        if self._outlines is None:
            self._outlines = {}
            if self.design_dir and (self.design_dir / "geo").exists():
                for f in (self.design_dir / "geo").glob("*.json"):
                    self._outlines[f.stem] = json.loads(f.read_text())["poligonos"]
        return self._outlines


# ---------- texto ----------
def p(b, c):
    return f'<p class="bp">{inline(b["text"])}</p>'


def h(b, c):
    return f'<div class="bh">{inline(b["text"])}</div>'


def _li(items):
    return "".join(f"<li><span>{inline(t)}</span></li>" for t in items)


def list_part(b, i0, i1):
    cls = "bl num" if b.get("ordered") else "bl"
    start = f' style="counter-reset:n {i0}"' if b.get("ordered") and i0 else ""
    return f'<ul class="{cls}"{start}>{_li(b["items"][i0:i1])}</ul>'


# ---------- tabla ----------
def _cell(c, tag="td", first=False):
    if isinstance(c, dict):
        tone = TONES.get(c.get("tone", ""), "")
        cls = (tone + (" hi" if c.get("hi") else "")).strip()
        txt = c.get("t", "")
    else:
        cls, txt = "", c
    s = str(txt)
    if cls == "" and isinstance(c, (int, float)):
        cls = "num"
    return f'<{tag}{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}>{inline(s)}</{tag}>'


def table_part(b, r0, r1, with_head=True):
    head = b.get("head") or []
    widths = b.get("widths")
    colg = ""
    if widths:
        t = sum(widths)
        colg = "<colgroup>" + "".join(f'<col style="width:{100*w/t:.1f}%">' for w in widths) + "</colgroup>"
    th = "<thead><tr>" + "".join(f"<th>{inline(x)}</th>" for x in head) + "</tr></thead>" if head and with_head else ""
    rows = "".join("<tr>" + "".join(_cell(c) for c in r) + "</tr>" for r in b["rows"][r0:r1])
    cap = f'<div class="k" style="margin-top:1cqw">{inline(b["caption"])}</div>' if b.get("caption") and r1 >= len(b["rows"]) else ""
    v = b.get("variant")
    vc = f" v-{v}" if v in ("compact", "ficha") else ""
    return f'<div class="tabw"><table class="tab{vc}">{colg}{th}<tbody>{rows}</tbody></table>{cap}</div>'


# ---------- llamadas, cifras ----------
def callout(b, c):
    tone = b.get("tone", "nota")
    if tone not in CALLOUT_TONES:
        c.warn.append({"bloque": b.get("label", "callout"), "causa": f"tono '{tone}' no estándar", "ajuste": f"se usó 'nota'; estándar: {sorted(CALLOUT_TONES)}"})
        tone = "nota"
    lab = b.get("label", LABELS.get(tone, "Nota"))
    body = b.get("paras") or [b.get("text", "")]
    ps = "".join(f"<p>{inline(t)}</p>" for t in body)
    title = f'<p><b>{inline(b["title"])}</b></p>' if b.get("title") else ""
    return f'<aside class="co {tone}"><span class="lb">{esc(lab)}</span>{title}{ps}</aside>'


def big(b, c):
    unit = f"<small>{esc(b['unit'])}</small>" if b.get("unit") else ""
    return (f'<div class="bigd"><div class="disco" aria-hidden="true"></div><div class="big">{esc(b["value"])}{unit}</div>'
            f'<div class="cap">{inline(b["caption"])}</div></div>')


def kpi(b, c):
    items = b["items"]
    cards = "".join(
        f'<div class="kpi"><b>{esc(i["v"])}</b><span>{inline(i["l"])}</span>'
        + (f'<i>{inline(i["note"])}</i>' if i.get("note") else "") + "</div>"
        for i in items
    )
    return f'<div class="kpis n{min(len(items),4)}">{cards}</div>'


def _chart_table(ch):
    """Degradación estándar: los mismos datos en una tabla, sin perder nada."""
    d = ch.get("data", {})
    rows, total = [], 0
    for k in ("items", "bars", "groups", "points", "rows"):
        total += len(d.get(k, []))
        for it in d.get(k, [])[:12]:
            if isinstance(it, dict):
                rows.append([str(it.get("l", "")), ", ".join(f"{kk}={vv}" for kk, vv in it.items() if kk != "l")[:80]])
            else:
                rows.append([str(it[0]) if len(it) else "", ", ".join(str(x) for x in it[1:])])
    if not rows:
        return '<p class="bp">Sin datos que mostrar.</p>'
    cap = f"Se muestran {len(rows)} de {total} filas." if total > len(rows) else ""
    return table_part({"head": ["Dato", "Valores"], "rows": rows, "caption": cap}, 0, len(rows))


def chart(b, c):
    ch = b["chart"]
    try:
        svg = charts.draw(ch, c.roles, c.outlines())
    except Exception as e:  # noqa: BLE001  nada de lo que mande el agente debe romper el documento
        c.warn.append({"bloque": b.get("title", "gráfico"), "causa": f"gráfico no estándar ({e})", "ajuste": "se muestra una tabla con los mismos datos"})
        svg = _chart_table(ch)
    cls = "ch sim" if b.get("sim") else "ch"
    tag = f'<div class="tg">{inline(b["tag"])}</div>' if b.get("tag") else ""
    leg = charts.legend(ch)
    cap = f"<figcaption>{inline(b['caption'])}</figcaption>" if b.get("caption") else ""
    return f'<figure class="{cls}"><p class="ct">{inline(b["title"])}</p>{tag}{svg}{leg}{cap}</figure>'


def stats(b, c):
    items = "".join(f'<div><b>{esc(i["v"])}</b><span>{inline(i["l"])}</span></div>' for i in b["items"])
    note = f'<p class="sn">{inline(b["note"])}</p>' if b.get("note") else ""
    head = f'<div class="sh">{inline(b["title"])}</div>' if b.get("title") else ""
    return f'<aside class="stats">{head}{items}{note}</aside>'


def figure(b, c):
    inner = chart(b, c) if b.get("chart") else image(b["image"] if isinstance(b.get("image"), dict) else b, c)
    if not b.get("side"):
        return inner
    side = {"items": b["side"], "note": b.get("side_note"), "title": b.get("side_title")}
    return f'<div class="figrow">{inner}{stats(side, c)}</div>'


def form(b, c):
    rows = "".join(f"<div><b>{inline(r)}</b><i></i></div>" for r in b["rows"])
    return f'<div class="form"><div class="fh">{inline(b.get("title", "Datos"))}</div>{rows}</div>'


def flowchart(b, c):
    try:
        body = diagram.draw(b)
    except Exception as e:  # noqa: BLE001
        c.warn.append({"bloque": b.get("title", "flowchart"), "causa": f"diagrama no estándar ({e})", "ajuste": "se muestra una lista numerada"})
        steps = "".join(f"<li><span>{inline(n['label'])}</span></li>" for n in b.get("nodes", []))
        body = f'<ul class="bl num">{steps}</ul>'
    cap = f"<figcaption>{inline(b['caption'])}</figcaption>" if b.get("caption") else ""
    tag = f'<div class="tg">{inline(b["tag"])}</div>' if b.get("tag") else ""
    return f'<figure class="ch fc"><p class="ct">{inline(b.get("title", "Diagrama"))}</p>{tag}{body}{cap}</figure>'


# ---- bloque libre saneado: lo único donde se acepta HTML del agente ----
SAFE_TAGS = {"p", "b", "strong", "i", "em", "ul", "ol", "li", "h4", "span", "div", "table", "thead", "tbody", "tr", "th", "td", "br", "code", "small"}
SAFE_CLASSES = {"k", "micro", "mono", "caja", "pend", "num", "tab", "bp", "bh", "bl"}


class _San(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.dropped = [], 0

    def handle_starttag(self, tag, attrs):
        if tag not in SAFE_TAGS:
            self.dropped += 1
            return
        cls = ""
        for k, v in attrs:
            if k == "class" and v:
                cls = " ".join(x for x in v.split() if x in SAFE_CLASSES)
            else:
                self.dropped += 1
        self.out.append(f'<{tag} class="{cls}">' if cls else f"<{tag}>")

    def handle_endtag(self, tag):
        if tag in SAFE_TAGS and tag != "br":
            self.out.append(f"</{tag}>")

    def handle_data(self, data):
        self.out.append(esc(data))


def custom(b, c):
    p = _San()
    p.feed(b.get("html", ""))
    if p.dropped:
        c.warn.append({"bloque": b.get("label", "custom"), "causa": f"{p.dropped} etiquetas o atributos no permitidos eliminados",
                       "ajuste": f"permitidos: {sorted(SAFE_TAGS)} y class {sorted(SAFE_CLASSES)}"})
    return f'<div class="cust">{"".join(p.out)}</div>'


# ---------- imágenes ----------
def _one_image(it, c, ratio):
    src = it.get("src")
    cap = it.get("caption", "")
    path = (c.images_root / src) if src else None
    if path and path.exists():
        treat = it.get("treatment") or ["ocre", "crema", "verde", "negroverde"][c.img_i % 4]
        c.img_i += 1
        out = duotone(path, treat, c.roles, c.manifest["image_treatments"], c.cache)
        import base64
        data = base64.b64encode(out.read_bytes()).decode()
        cr = c.credits.get(src)
        if cr:
            c.images_used.append((src, cr))
        pos = it.get("pos", "50% 40%")
        credit = ""
        if cr:
            who = cr.get("autor") or "autor no indicado"
            credit = f' <span class="cr">Foto: {esc(who)} · {esc(cr.get("licencia",""))} · Wikimedia Commons</span>'
        else:
            c.no_credit.append(src)
            credit = ' <span class="cr">Crédito: <span class="pend">dato pendiente</span></span>'
        return (f'<figure class="im"><div class="foto" style="aspect-ratio:{ratio}"><img src="data:image/png;base64,{data}" '
                f'alt="{esc(plain(cap))}" style="object-position:{pos}"></div>'
                f'<figcaption>{inline(cap)}{credit}</figcaption></figure>')
    c.missing.append({"src": src, "need": it.get("need") or cap})
    need = it.get("need") or cap or "describe la imagen"
    cross = '<svg viewBox="0 0 100 50" preserveAspectRatio="none" aria-hidden="true"><line x1="0" y1="0" x2="100" y2="50"/><line x1="100" y1="0" x2="0" y2="50"/></svg>'
    return (f'<figure class="im need"><div class="foto" style="aspect-ratio:{ratio}">{cross}<b>Imagen necesaria</b>'
            f'<span>{inline(need)}</span></div><figcaption>{inline(cap)}</figcaption></figure>')


def image(b, c):
    items = b.get("items") or [b]
    ratio = b.get("ratio", "16/7" if len(items) == 1 else "4/3")
    body = "".join(_one_image(i, c, ratio) for i in items)
    if len(items) == 1:
        return body
    return f'<div class="imrow n{min(len(items),3)}">{body}</div>'


# ---------- diagramas ----------
def flow(b, c):
    cols = b.get("cols", 4)
    steps = "".join(
        f'<div class="st{" on" if s.get("on") else ""}"><span class="n">{esc(s.get("n", i+1))}</span><b>{inline(s["title"])}</b>'
        + (f'<span>{inline(s["text"])}</span>' if s.get("text") else "") + "</div>"
        for i, s in enumerate(b["steps"])
    )
    return f'<div class="flow c{cols}">{steps}</div>'


def ladder(b, c):
    rows = "".join(
        f'<div class="rg"><div class="no">{i+1}</div><div class="tx"><b>{inline(r["title"])}</b>'
        f'<span>{inline(r["text"])}</span>' + (f'<span class="cost">{inline(r["cost"])}</span>' if r.get("cost") else "") + "</div></div>"
        for i, r in enumerate(b["items"])
    )
    return f'<div class="ladder">{rows}</div>'


def ranks(b, c):
    head = b.get("head") or []
    hd = ""
    if head:
        hd = '<div class="hd"><span></span><div class="l">' + "".join(f"<span>{esc(x)}</span>" for x in head) + "</div></div>"
    rows = "".join(
        f'<div class="rk"><span class="nm">{esc(r["rank"])}</span><div class="bar" style="margin-left:{i*1.4}cqw">'
        + "".join(f"<span>{inline(x)}</span>" for x in r["v"]) + "</div></div>"
        for i, r in enumerate(b["rows"])
    )
    return f'<div class="ranks">{hd}{rows}</div>'


def timeline(b, c):
    items = b["items"]
    tot = sum(i["days"] for i in items)
    adult = b.get("adult")
    seg_w = 100 - (16 if adult else 0)
    segs = "".join(
        f'<div class="seg {i.get("vis","h")}" style="flex:0 0 {seg_w*i["days"]/tot:.2f}%"><span class="cd">{esc(i["code"])}</span>'
        f'<span class="dd">{num(i["days"])} d</span></div>' for i in items
    )
    if adult:
        segs += f'<div class="seg a" style="flex:1 1 0"><span class="cd">{esc(adult["code"])}</span><span class="dd">{esc(adult.get("days","—"))}</span></div>'
    allr = items + ([adult] if adult else [])
    rows = "".join(
        f'<div><b>{esc(r["code"])} · {inline(r["label"])}</b>{inline(r.get("photo",""))}</div>' for r in allr
    )
    leg = "".join(f'<span><i class="{k}"></i>{esc(t)}</span>' for k, t in b.get("legend", []))
    ax = f'<div class="ax"><span>0 d</span><span>{num(tot)} d (huevo a pupa, suma de etapas)</span></div>'
    cap = f'<div class="cap">{inline(b["caption"])}</div>' if b.get("caption") else ""
    return f'<div class="tl"><div class="bars">{segs}</div>{ax}<div class="rows" style="--n:{len(allr)}">{rows}</div><div class="leg">{leg}</div>{cap}</div>'


def compare(b, c):
    def col(x):
        sub = f'<div class="sub">{inline(x["sub"])}</div>' if x.get("sub") else ""
        return f'<div class="col"><h4>{inline(x["title"])}</h4>{sub}<ul>' + "".join(f"<li><span>{inline(t)}</span></li>" for t in x["items"]) + "</ul></div>"
    ver = f'<div class="ver">{inline(b["verdict"])}</div>' if b.get("verdict") else ""
    return f'<div class="cmp">{col(b["left"])}{col(b["right"])}{ver}</div>'


def toc(b, c):
    out = []
    for part in c.toc:
        out.append(f'<div class="pt"><span>{esc(part["number"])} · {esc(part["title"])}</span><small>pág. {part["page"]}</small></div>')
        for s in part["sections"]:
            out.append(f'<div class="ro"><i>{esc(s["n"])}</i><span>{inline(s["title"])}</span><b>{s["page"]}</b></div>')
    return f'<div class="toc">{"".join(out)}</div>'


RENDER = {
    "p": p, "h": h, "callout": callout, "big": big, "kpi": kpi, "chart": chart, "image": image, "figure": figure, "stats": stats,
    "form": form, "flowchart": flowchart, "custom": custom,
    "flow": flow, "ladder": ladder, "ranks": ranks, "timeline": timeline, "compare": compare, "toc": toc,
}


def _fallback(b, c, why):
    """Un bloque que no se puede dibujar nunca rompe el documento: se degrada a una nota con su texto."""
    c.warn.append({"bloque": str(b.get("type", "?")), "causa": why, "ajuste": "se mostró como nota; usa un bloque del vocabulario"})
    txt = b.get("text") or b.get("title") or b.get("caption") or json.dumps({k: v for k, v in b.items() if k != "type"}, ensure_ascii=False)[:300]
    return f'<aside class="co hueco"><span class="lb">Bloque no estándar · {esc(b.get("type", "?"))}</span><p>{inline(txt)}</p></aside>'


def render(b, c):
    t = b.get("type")
    try:
        if t == "list":
            return list_part(b, 0, len(b["items"]))
        if t == "table":
            return table_part(b, 0, len(b["rows"]))
        if t in RENDER:
            return RENDER[t](b, c)
        return _fallback(b, c, f"tipo de bloque '{t}' fuera del vocabulario")
    except Exception as e:  # noqa: BLE001
        return _fallback(b, c, f"el bloque '{t}' no se pudo dibujar ({type(e).__name__}: {e})")
