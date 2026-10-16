#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Salida WEB del mismo contrato JSON (formato `web-1col`). Mismos roles de color, tipografías y bloques; CSS fluido de web/web.css.

    python servidor/web.py contenido/guia.json -o salida/web/index.html --imagenes teoria/imagenes [--estilo]
    --estilo  también escribe estilo.html: la guía de estilo atómica (átomos → moléculas → organismos → plantillas → página)

Bloques soportados en web: p, h, list, table, callout, kpi, stats, big, chart, figure, image, flow, ladder, compare, form, flowchart.
Los demás (timeline, ranks, toc, custom…) se degradan a una nota con su texto, igual que en PDF: nada rompe la página.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from engine import assets, blocks, charts, diagram, pages  # noqa: E402
from engine.text import esc, inline, plain  # noqa: E402


def w_block(b, ctx):
    t = b.get("type")
    try:
        if t == "p":
            return f'<p>{inline(b["text"])}</p>'
        if t == "h":
            return f'<div class="a-mono" style="border-bottom:.12rem solid var(--negro);padding-bottom:.3rem">{inline(b["text"])}</div>'
        if t == "list":
            tag = "ol" if b.get("ordered") else "ul"
            return f'<{tag} class="m-list">' + "".join(f"<li><span>{inline(i)}</span></li>" for i in b["items"]) + f"</{tag}>"
        if t == "table":
            th = "".join(f"<th>{inline(x)}</th>" for x in b.get("head", []))
            rows = "".join("<tr>" + "".join(f"<td>{inline(c['t'] if isinstance(c, dict) else str(c))}</td>" for c in r) + "</tr>" for r in b["rows"])
            return f'<div class="m-table"><table><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div>'
        if t == "callout":
            tone = b.get("tone", "nota")
            lab = b.get("label", blocks.LABELS.get(tone, "Nota"))
            body = b.get("paras") or [b.get("text", "")]
            return f'<aside class="m-callout {esc(tone)}"><span class="a-mono">{esc(lab)}</span>' + (f'<p><b>{inline(b["title"])}</b></p>' if b.get("title") else "") + "".join(f"<p>{inline(x)}</p>" for x in body) + "</aside>"
        if t == "kpi":
            return '<div class="m-stats">' + "".join(f'<div class="m-kpi"><b>{esc(i["v"])}</b><span>{inline(i["l"])}</span></div>' for i in b["items"]) + "</div>"
        if t == "stats":
            return '<div class="m-stats">' + "".join(f'<div class="m-stat"><b>{esc(i["v"])}</b><span>{inline(i["l"])}</span></div>' for i in b["items"]) + "</div>"
        if t == "big":
            return f'<div class="m-stat"><b style="font-size:clamp(4rem,14vw,9rem)">{esc(b["value"])}{esc(b.get("unit",""))}</b><span>{inline(b["caption"])}</span></div>'
        if t in ("chart", "figure") and b.get("chart"):
            try:
                svg = charts.draw(b["chart"], ctx.roles, ctx.outlines())
            except Exception as e:  # noqa: BLE001
                ctx.warn.append({"bloque": b.get("title", "gráfico"), "causa": str(e), "ajuste": "tabla"})
                svg = blocks._chart_table(b["chart"])
            fig = f'<figure class="m-figure"><h4>{inline(b.get("title",""))}</h4>{svg}' + (f'<figcaption>{inline(b["caption"])}</figcaption>' if b.get("caption") else "") + "</figure>"
            if b.get("side"):
                return f'<div class="t-split">{fig}<div class="m-stats" style="align-content:start">' + "".join(f'<div class="m-stat"><b>{esc(i["v"])}</b><span>{inline(i["l"])}</span></div>' for i in b["side"]) + "</div></div>"
            return fig
        if t == "flowchart":
            try:
                body = diagram.draw(b)
            except Exception as e:  # noqa: BLE001
                ctx.warn.append({"bloque": "flowchart", "causa": str(e), "ajuste": "lista"})
                body = '<ol class="m-list">' + "".join(f"<li><span>{inline(n['label'])}</span></li>" for n in b.get("nodes", [])) + "</ol>"
            return f'<figure class="m-figure"><h4>{inline(b.get("title","Diagrama"))}</h4>{body}</figure>'
        if t == "image":
            items = b.get("items") or [b]
            out = []
            for it in items:
                p = ctx.images_root / it["src"] if it.get("src") else None
                if p and p.exists():
                    import base64
                    f = assets.duotone(p, it.get("treatment", "acento"), ctx.roles, ctx.manifest["image_treatments"], ctx.cache, 1000)
                    out.append(f'<figure class="m-figure"><img src="data:image/png;base64,{base64.b64encode(f.read_bytes()).decode()}" alt="{esc(plain(it.get("caption","")))}"><figcaption>{inline(it.get("caption",""))}</figcaption></figure>')
                else:
                    ctx.missing.append({"src": it.get("src"), "need": it.get("need", "")})
                    out.append(f'<figure class="m-figure"><div style="padding:3rem 1rem;text-align:center;background:var(--arena);border:.18rem dashed var(--negro)"><b class="a-title" style="font-size:2rem">Imagen necesaria</b><br>{inline(it.get("need",""))}</div></figure>')
            return '<div class="t-grid">' + "".join(out) + "</div>"
        if t in ("flow", "ladder"):
            items = b.get("steps") or b.get("items")
            return '<div class="t-steps">' + "".join(f'<div class="m-step{" on" if s.get("on") else ""}"><b>{inline(s["title"])}</b>{inline(s.get("text",""))}</div>' for s in items) + "</div>"
        if t == "compare":
            col = lambda x: f'<div class="m-callout"><b class="a-title" style="font-size:1.6rem">{inline(x["title"])}</b>' + '<ul class="m-list">' + "".join(f"<li><span>{inline(i)}</span></li>" for i in x["items"]) + "</ul></div>"
            return f'<div class="t-grid">{col(b["left"])}{col(b["right"])}</div>' + (f'<aside class="m-callout regla">{inline(b["verdict"])}</aside>' if b.get("verdict") else "")
        if t == "form":
            return '<form class="o-form" onsubmit="return false"><b class="a-mono">' + inline(b.get("title", "Datos")) + "</b>" + "".join(f'<label><span class="a-label">{inline(r)}</span><input class="a-field" type="text"></label>' for r in b["rows"]) + "</form>"
    except Exception as e:  # noqa: BLE001
        ctx.warn.append({"bloque": str(t), "causa": f"{type(e).__name__}: {e}", "ajuste": "nota"})
    ctx.warn.append({"bloque": str(t), "causa": "sin equivalente web estándar", "ajuste": "se muestra como nota"})
    txt = b.get("text") or b.get("title") or b.get("caption") or ""
    return f'<aside class="m-callout"><span class="a-mono">Bloque {esc(t)}</span><p>{inline(txt)}</p></aside>'


def build(doc_path, out_path, images_root):
    doc = json.loads(Path(doc_path).read_text(encoding="utf-8"))
    design_dir = HERE / "designs/anura"
    m = json.loads((design_dir / "manifest.json").read_text())
    pals = json.loads((design_dir / "palettes.json").read_text())
    roles = dict(m["palette"]["roles"])
    pal = doc.get("palette", "default")
    roles.update(pals.get(pal, {}) if isinstance(pal, str) else pal)
    sym = assets.Symbols(design_dir)
    credits = assets.load_credits(Path(images_root))
    ctx = blocks.Ctx(m, roles, images_root, credits, HERE / ".cache", [], design_dir)
    pc = pages.PageCtx(design_dir, m, roles, sym, images_root, HERE / ".cache", ctx.warn)
    meta, d = doc.get("meta", {}), doc["document"]
    cov = d["cover"]
    img = pages.art(pc, None, cov.get("image"), cov.get("treatment"), cov.get("tint") or ["bosque", "vivo"])
    nav = "".join(f'<a href="#{esc(p["id"])}">{esc(p["title"])}</a>' for p in d["parts"])
    hero = (f'<header class="o-hero grain"><div class="in"><div><p class="a-mono">{esc(" · ".join(meta.get("header_left", [])))}</p><h1>{esc(cov["vertical"])}</h1>'
            f'<h2 class="a-title" style="font-size:clamp(1.6rem,4vw,3rem)">{esc(cov["title"])}</h2><p>{esc(cov["text"])}</p><p><a class="a-btn" href="#{esc(d["parts"][0]["id"])}">Empezar</a> <span class="a-chip">{esc(meta.get("version",""))}</span></p></div>'
            + (f'<div class="pic"><img src="{img}" alt="{esc(cov.get("alt",""))}"></div>' if img else "") + "</div></header>")
    body = []
    for pi, part in enumerate(d["parts"]):
        pimg = pages.art(pc, None, part.get("image"), part.get("treatment"), part.get("tint") or ["bosque", "vivo"])
        body.append(f'<section class="o-band grain" id="{esc(part["id"])}" aria-label="{esc(part["title"])}"><div class="in"><div><p class="n" aria-hidden="true">{pi+1:02d}</p><h2>{esc(part["title"])}</h2><p>{esc(part["desc"])}</p></div>'
                    + (f'<div class="pic"><img src="{pimg}" alt=""></div>' if pimg else "") + "</div></section>")
        for sec in part["sections"]:
            lead = f'<p class="a-mono">{inline(sec["lead"])}</p>' if sec.get("lead") else ""
            body.append(f'<article class="o-section t-article" id="{esc(sec["id"])}"><h3>{inline(sec["title"])}</h3>{lead}' + "".join(w_block(b, ctx) for b in sec.get("blocks", [])) + "</article>")
    css = "\n".join([assets.font_css(design_dir, m), assets.root_css(roles), (HERE / "web/web.css").read_text()])
    html = (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(plain(meta.get("title","Documento")))}</title><style>{css}</style></head><body>'
            f'<a class="skip" href="#main">Saltar al contenido</a><div class="o-header"><div class="in"><b class="a-title" style="font-size:1.4rem">{esc(cov["vertical"])}</b><nav aria-label="Secciones">{nav}</nav></div></div>'
            f'{hero}<main id="main">{"".join(body)}</main><footer class="o-footer"><div class="in"><span>{esc(meta.get("footer",""))}</span><span>{esc(meta.get("date",""))}</span></div></footer></body></html>')
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return ctx.warn, ctx.missing


def estilo(out_path):
    """Guía de estilo atómica: una página por nivel, con los componentes reales."""
    design_dir = HERE / "designs/anura"
    m = json.loads((design_dir / "manifest.json").read_text())
    roles = m["palette"]["roles"]
    sw = "".join(f'<div style="background:var(--{k});color:{"var(--crema)" if k in ("negro","bosque","hoja") else "var(--negro)"};padding:1rem;border:.15rem solid var(--negro)"><b>{k}</b><br><span class="a-mono">{v}</span></div>' for k, v in roles.items())
    css = "\n".join([assets.font_css(design_dir, m), assets.root_css(roles), (HERE / "web/web.css").read_text()])
    sec = lambda t, s, inner: f'<article class="o-section"><h3>{t}</h3><p class="a-mono">{s}</p>{inner}</article>'
    html = (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Guía de estilo web · diseño atómico</title><style>{css}</style></head><body>'
            '<div class="o-header"><div class="in"><b class="a-title" style="font-size:1.4rem">Estilo web</b><nav><a href="#atomos">átomos</a><a href="#moleculas">moléculas</a><a href="#organismos">organismos</a><a href="#plantillas">plantillas</a></nav></div></div><main>'
            + '<div id="atomos"></div>' + sec("1 · Átomos", "Lo mínimo indivisible: color, tipografía, regla, chip, botón, campo.", f'<div class="t-grid">{sw}</div>'
              '<div class="t-grid"><div><span class="a-title" style="font-size:3rem">Anton títulos</span><p>Archivo texto corrido.</p><p class="a-mono">IBM Plex Mono datos</p></div><div><a class="a-btn" href="#">Primario</a> <a class="a-btn s" href="#">Secundario</a> <a class="a-btn k" href="#">Oscuro</a></div>'
              '<div><span class="a-chip">FUENTE</span> <span class="a-chip c">CALC</span> <span class="a-chip i">INF</span> <span class="a-chip s">SIN FUENTE</span> <span class="a-pend">dato pendiente</span></div>'
              '<div><label class="a-label" for="c">Campo</label><input id="c" class="a-field"></div><hr class="a-rule"><hr class="a-rule fina"></div>')
            + '<div id="moleculas"></div>' + sec("2 · Moléculas", "Átomos combinados con una función: cifra, aviso, tabla, figura, lista, paso.",
              '<div class="m-stats"><div class="m-kpi"><b>62,9 %</b><span>top-1</span></div><div class="m-kpi"><b>86,1 %</b><span>top-3</span></div><div class="m-kpi"><b>91,1 %</b><span>top-5</span></div></div>'
              '<aside class="m-callout clave"><span class="a-mono">Punto clave</span><p>Una idea que hay que llevarse.</p></aside><aside class="m-callout slate"><span class="a-mono">Atención</span><p>Aviso con tono pizarra.</p></aside>'
              '<div class="m-table"><table><thead><tr><th>Variable</th><th>Tipo</th></tr></thead><tbody><tr><td>edad</td><td>int8</td></tr></tbody></table></div>')
            + '<div id="organismos"></div>' + sec("3 · Organismos", "Bloques de interfaz completos: cabecera, héroe, banda de sección, sección, formulario, pie.", '<p>Mira arriba (cabecera fija) y en <code class="a-code">index.html</code> (héroe, bandas, secciones y pie).</p>')
            + '<div id="plantillas"></div>' + sec("4 · Plantillas y página", "Plantillas: artículo (una columna), rejilla, dos columnas 7/3. Página = plantilla + contenido real.", '<div class="t-split"><div class="m-callout">Columna principal 7/10</div><div class="m-callout">Lateral 3/10</div></div>')
            + "</main></body></html>")
    Path(out_path).write_text(html, encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("doc")
    ap.add_argument("-o", "--out", default="salida/web/index.html")
    ap.add_argument("--imagenes", default="imagenes")
    ap.add_argument("--estilo", action="store_true")
    a = ap.parse_args()
    warn, miss = build(a.doc, a.out, a.imagenes)
    if a.estilo:
        estilo(Path(a.out).with_name("estilo.html"))
    print(json.dumps({"avisos": warn, "imagenes_necesarias": miss}, ensure_ascii=False)[:1500])
