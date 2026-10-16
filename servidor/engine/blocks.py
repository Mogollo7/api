# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Bloques declarativos -> HTML. El agente no escribe HTML ni CSS: aquí se decide cómo se ve cada bloque."""
from pathlib import Path

from . import charts
from .assets import duotone
from .text import esc, inline, num, plain

LABELS = {"nota": "Nota", "clave": "Punto clave", "ojo": "Ojo", "sim": "Simulación", "pend": "Dato pendiente", "regla": "Regla"}
TONES = {"f": "t-f", "p": "t-p", "l": "t-l", "n": "t-n"}


class Ctx:
    def __init__(self, manifest, roles, images_root, credits, cache, toc=None):
        self.manifest, self.roles = manifest, roles
        self.images_root, self.credits, self.cache = Path(images_root), credits, Path(cache)
        self.images_used = []   # (archivo, credit_row) para la página de créditos automática
        self.missing = []       # imágenes marcadas "IMAGEN NECESARIA"
        self.no_credit = []     # imágenes usadas sin fila en creditos.csv
        self.toc = toc or []
        self.img_i = 0


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
    return f'<div class="tabw"><table class="tab">{colg}{th}<tbody>{rows}</tbody></table>{cap}</div>'


# ---------- llamadas, cifras ----------
def callout(b, c):
    tone = b.get("tone", "nota")
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


def chart(b, c):
    ch = b["chart"]
    svg = charts.draw(ch)
    cls = "ch sim" if b.get("sim") else "ch"
    tag = f'<div class="tg">{inline(b["tag"])}</div>' if b.get("tag") else ""
    leg = charts.legend(ch)
    cap = f"<figcaption>{inline(b['caption'])}</figcaption>" if b.get("caption") else ""
    return f'<figure class="{cls}"><p class="ct">{inline(b["title"])}</p>{tag}{svg}{leg}{cap}</figure>'


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
    "p": p, "h": h, "callout": callout, "big": big, "kpi": kpi, "chart": chart, "image": image,
    "flow": flow, "ladder": ladder, "ranks": ranks, "timeline": timeline, "compare": compare, "toc": toc,
}


def render(b, c):
    t = b["type"]
    if t == "list":
        return list_part(b, 0, len(b["items"]))
    if t == "table":
        return table_part(b, 0, len(b["rows"]))
    return RENDER[t](b, c)
