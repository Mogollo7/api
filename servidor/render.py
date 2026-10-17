#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Servidor de documentos (fase 1: PDF). Recibe el contrato JSON del agente (solo datos) y devuelve PDF + informe breve.

Uso:  python servidor/render.py contenido/guia.json -o salida/guia.pdf --imagenes teoria/imagenes
"""
import re
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from engine import assets, blocks, contract, layout, pages, paleta, redundancia, variants  # noqa: E402
from engine.text import esc, inline, plain  # noqa: E402

AUDIT_JS = (HERE / "engine/audit.js").read_text()
FIT_JS = (HERE / "engine/fit.js").read_text()
FIX_JS = (HERE / "engine/contrast_fix.js").read_text()


def load_design(design_id: str):
    d = HERE / "designs" / design_id
    return d, json.loads((d / "manifest.json").read_text())


def heading_unit(sec, n):
    t = plain(sec["title"])
    cls = "sec" if len(t) <= 18 else "sec m" if len(t) <= 36 else "sec s"
    lead = f'<p class="lead">{inline(sec["lead"])}</p>' if sec.get("lead") and sec.get("kind") != "clave" else ""
    return {"html": f'<h3 class="{cls}" id="sec-{esc(sec["id"])}">{inline(sec["title"])}</h3>{lead}', "label": f"{sec['id']}.titulo", "keep_next": True}


def section_units(sec, ctx, gap_pair=True):
    units = [heading_unit(sec, 0)]
    if sec.get("kind") == "clave" and sec.get("lead"):
        units.append({"html": blocks.callout({"tone": "clave", "text": sec["lead"]}, ctx), "label": f"{sec['id']}.clave"})
    bl = [dict(b) for b in sec.get("blocks", [])]
    keep = []
    for k, b in enumerate(bl):
        t = b.get("type")
        if t == "h" and redundancia.similar(b.get("text", ""), sec["title"], laxo=(k == 0)):
            ctx.warn.append({"bloque": f"{sec['id']}.b{k}", "causa": f"subtítulo «{plain(b['text'])[:40]}» repite el titular", "ajuste": "se omitió (redundancia)"})
            continue
        if t in ("chart", "figure", "flowchart") and b.get("title") and redundancia.similar(b["title"], sec["title"]):
            ctx.warn.append({"bloque": f"{sec['id']}.b{k}", "causa": f"título de figura «{plain(b['title'])[:40]}» repite el titular", "ajuste": "se omitió el título de la figura (redundancia)"})
            b["title"] = ""
        keep.append(b)
    bl = keep
    i = 0
    while i < len(bl):
        b = bl[i]
        label = f"{sec['id']}.b{i}:{b['type']}"
        if b.get("half") and i + 1 < len(bl) and bl[i + 1].get("half"):
            a, c2 = blocks.render(b, ctx), blocks.render(bl[i + 1], ctx)
            units.append({"html": f'<div class="row2">{a}{c2}</div>', "label": f"{label}+b{i+1}"})
            i += 2
            continue
        if b["type"] == "refs":
            rb = {"type": "list", "ordered": True, "items": b["items"], "cls": "refs" if b.get("numbered", True) else "refs apa"}   # numbered:false = lista APA sin números
            if b.get("title"):
                units.append({"html": blocks.h({"text": b["title"]}, ctx), "label": f"{sec['id']}.b{i}:refs-h", "keep_next": True})
            units.append({"html": blocks.render(rb, ctx), "label": label, "split": "list", "block": rb})
            i += 1
            continue
        if b["type"] in ("table", "list"):
            units.append({"html": blocks.render(b, ctx), "label": label, "split": b["type"], "block": b})
        else:
            units.append({"html": blocks.render(b, ctx), "label": label, "keep_next": b["type"] == "h"})
        i += 1
    if sec.get("notes"):
        items = "".join(f'<li value="{esc(n.get("n", k+1))}"><span>{inline(n["text"])}</span></li>' for k, n in enumerate(sec["notes"]))
        units.append({"html": f'<div class="bh">Notas</div><ol class="bl fnotes">{items}</ol>', "label": f"{sec['id']}.notas"})
    return units


def render_part(u, r0, r1):
    b = u["block"]
    if u["split"] == "table":
        return blocks.table_part(b, r0, r1, with_head=True)
    return blocks.list_part(b, r0, r1)


def credits_section(ctx):
    rows, seen = [], set()
    for src, cr in ctx.images_used:
        if src in seen:
            continue
        seen.add(src)
        rows.append([cr.get("especie_o_tema", ""), cr.get("autor") or "autor no indicado", cr.get("licencia", ""), _origen(cr)])
    if not rows:
        return None
    return {"id": "creditos", "title": "Créditos de imágenes", "tema": "Créditos", "blocks": [
        {"type": "p", "text": f"Fotografías tomadas de {_fuentes(ctx)} y mostradas con el filtro de dos tintas del sistema. Cada imagen conserva su autoría y licencia."},
        {"type": "table", "head": ["Imagen", "Autor", "Licencia", "Origen"], "widths": [3, 2, 2, 5], "rows": rows},
    ]}


def _origen(cr):
    """Columna «Origen» de los créditos: URL de Commons (como siempre) o fuente + id de foto si el CSV trae `fuente`."""
    url = (cr.get("url_commons") or "").replace("https://", "")
    if not cr.get("fuente"):
        return url
    m = re.search(r"photos/(\d+)", url)
    return cr["fuente"] + (f" · foto {m.group(1)}" if m else "")


def _fuentes(ctx):
    fs = sorted({cr.get("fuente") or "Wikimedia Commons" for _, cr in ctx.images_used})
    return " y ".join(fs) if len(fs) < 3 else ", ".join(fs[:-1]) + " y " + fs[-1]


# opción `density: "aireado"`: texto más grande y más aire entre bloques (documentos académicos para leer en pantalla)
AIREADO = (".lp .cont{gap:4.6cqw}.int p{font-size:2.75cqw;line-height:1.62;margin-bottom:3cqw}"
           ".bl{font-size:2.65cqw;line-height:1.55}.bl li{padding:.9cqw 0}.bl.refs,.bl.fnotes{font-size:2.2cqw}")


def make_head(doc, design_dir, m, roles, ph=141.4):
    meta = doc.get("meta", {})
    css = "\n".join([
        assets.font_css(design_dir, m), assets.root_css(roles),
        (design_dir / "bundle.css").read_text(), (design_dir / "extras.css").read_text(),
        f".page{{aspect-ratio:1/{ph/100:.4f}}}@page{{size:{(m.get('formats_dims') or {}).get(doc.get('format'), {}).get('pdf', 'A4')};margin:0}}",
        ".page.measure{aspect-ratio:auto;height:auto;overflow:visible;border:0;box-shadow:none}"
        ".page.measure .cont{margin:0 5cqw;width:90cqw}",
        AIREADO if (doc.get("options") or {}).get("density") == "aireado" else "",
    ])
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{esc(plain(meta.get("title","Documento")))}</title>'
            f'<style>{css}</style></head><body style="margin:0">')


def expects_credits(doc, images_root, credits):
    for part in doc["document"]["parts"]:
        for sec in part["sections"]:
            for b in sec.get("blocks", []):
                if b.get("type") == "image":
                    for it in (b.get("items") or [b]):
                        if it.get("src") and (Path(images_root) / it["src"]).exists() and it["src"] in credits:
                            return True
    return False


def run(doc_path, out_pdf, images_root):
    t0 = time.time()
    doc = json.loads(Path(doc_path).read_text(encoding="utf-8"))
    design_dir, m = load_design(doc.get("design", "anura"))
    warns = []
    errs = contract.validate(doc, m, warns)
    report = {"estado": "ok", "errores": errs, "avisos": warns, "auditoria": {}, "imagenes_necesarias": [], "secciones": []}
    if errs:
        report["estado"] = "rechazado"
        return report
    palettes = json.loads((design_dir / "palettes.json").read_text(encoding="utf-8"))
    roles = dict(m["palette"]["roles"])
    pal = doc.get("palette", "default")
    if isinstance(pal, dict):
        roles.update(pal)
    elif pal in palettes and pal != "_marca":
        roles.update(palettes[pal])
    elif pal not in ("default", None):
        report["avisos"].append({"bloque": "palette", "causa": f"paleta '{pal}' no existe", "ajuste": "se usó la paleta por defecto"})
    report["avisos"] += paleta.check(roles, m)
    reg = variants.Registry(design_dir)
    seed = int(doc.get("options", {}).get("seed", 7))
    sym = assets.Symbols(design_dir)
    credits = assets.load_credits(Path(images_root))
    meta, d = doc.get("meta", {}), doc["document"]
    parts = [dict(p_) for p_ in d["parts"]]
    pg = m["page"]
    fmt = doc.get("format", "pdf-a4")
    dims = (m.get("formats_dims") or {}).get(fmt) or {"ph": 141.4, "pdf": "A4"}
    if fmt not in ("pdf-a4",) and fmt not in (m.get("formats_dims") or {}):
        report["avisos"].append({"bloque": "format", "causa": f"el diseño no declara '{fmt}'", "ajuste": "se usó pdf-a4"})
    ph = dims["ph"]
    capacity = ph - pg["cont_top"] - pg["cont_bottom"]
    gap = pg["gap"]

    # numeración continua de secciones (1..N, como la tabla de contenido) y TOC provisional
    n = 0
    for part in parts:
        for sec in part["sections"]:
            n += 1
            sec["n"] = f"{n:02d}"
    has_cred = expects_credits(doc, images_root, credits) and (doc.get("options") or {}).get("credits_section", True) is not False
    if has_cred:
        parts.append({"id": "creditos", "title": "Créditos", "desc": "", "_aux": True,
                      "sections": [{"id": "creditos", "title": "Créditos de imágenes", "tema": "Créditos", "n": f"{n+1:02d}", "blocks": []}]})

    def toc_struct(pages_of=None):
        out = []
        for pi, part in enumerate(parts):
            if part.get("_aux"):
                continue
            out.append({"number": f"{pi+1:02d}", "title": part["title"], "page": (pages_of or {}).get(("p", pi), "00"),
                        "sections": [{"n": s_["n"], "id": s_["id"], "title": s_["title"], "page": (pages_of or {}).get(("s", s_["id"]), "00")} for s_ in part["sections"] if s_.get("toc", True)]})
        if has_cred:
            out.append({"number": "··", "title": "Créditos", "page": (pages_of or {}).get(("s", "creditos"), "00"),
                        "sections": [{"n": parts[-1]["sections"][0]["n"], "id": "creditos", "title": "Créditos de imágenes", "page": (pages_of or {}).get(("s", "creditos"), "00")}]})
        return out

    ctx = blocks.Ctx(m, roles, images_root, credits, HERE / ".cache", toc_struct(), design_dir)
    pc = pages.PageCtx(design_dir, m, roles, sym, images_root, HERE / ".cache", report["avisos"])
    cov_alias = lambda w: w if str(w).startswith("CV-") else "CV-" + str(w).lstrip("Vv")
    div_alias = lambda w: w if str(w).startswith("DV-") else "DV-" + str(w).upper()
    cover_v = reg.resolve("portada", d["cover"].get("variant"), report["avisos"], cov_alias)

    # 1) unidades por sección
    secs = []
    for pi, part in enumerate(parts):
        for sec in part["sections"]:
            if sec["id"] == "creditos":
                continue
            secs.append((pi, sec, section_units(sec, ctx)))
    if has_cred:
        cs = credits_section(ctx)
        cs["n"] = parts[-1]["sections"][0]["n"]
        parts[-1]["sections"][0] = cs
        secs.append((len(parts) - 1, cs, section_units(cs, ctx)))
    toc_old = {u["html"] for _, _, us in secs for u in us if u.get("label", "").endswith(":toc")}

    from playwright.sync_api import sync_playwright
    head = make_head(doc, design_dir, m, roles, ph)
    shell = head + "<script>" + FIT_JS + "</script>%%MEASURE%%</body></html>"
    flat = [u for _, _, us in secs for u in us]
    with sync_playwright() as p:
        exe = os.environ.get("CHROMIUM_PATH") or ("/opt/pw-browsers/chromium" if Path("/opt/pw-browsers/chromium").exists() else None)
        browser = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
        page = browser.new_page(viewport={"width": 794, "height": 1123})
        page.emulate_media(media="print")
        meas = layout.measure(page, shell, flat)

        # 2) paginar y numerar
        pos, phys, plan, pages_of, cur_part = 0, 1, [], {}, None
        for pi, sec, us in secs:
            ms = meas[pos:pos + len(us)]
            pos += len(us)
            warn = []
            htmls = layout.pack(us, ms, capacity, gap, render_part, warn)
            report["avisos"] += warn
            if pi != cur_part:
                cur_part = pi
                if not parts[pi].get("_aux"):
                    phys += 1
                    plan.append(("div", pi, phys))
                    pages_of[("p", pi)] = f"{phys:02d}"
            first = phys + 1
            pages_of[("s", sec["id"])] = f"{first:02d}"
            report["secciones"].append({"id": sec["id"], "n": sec["n"], "pagina": first})
            for h_ in htmls:
                phys += 1
                plan.append(("lp", (pi, sec, h_), phys))
        ctx.toc = toc_struct(pages_of)
        toc_new = blocks.toc({}, ctx)

        # 3) ensamblar HTML
        body = [pages.cover(pc, meta, d["cover"], cover_v)]
        pool = m["templates"]["light"]["head_symbol_pool"]
        n_lp, part_i, nparts = 0, 0, len([x for x in parts if not x.get("_aux")])
        for item in plan:
            if item[0] == "div":
                part = parts[item[1]]
                v = part.get("divider", "auto")
                if v in (None, "auto"):
                    v = "ABCD"[part_i % 4]
                vid = reg.resolve("divisor", v, report["avisos"], div_alias)
                part_i += 1
                body.append(pages.divider(pc, vid[-1], f"{item[1]+1:02d}", nparts, part, ))
            else:
                pi, sec, htmls = item[1]
                inner = "".join(f'<div class="u">{h_}</div>' for h_ in htmls)
                for old in toc_old:
                    inner = inner.replace(old, toc_new)
                sid = pool[(seed + n_lp * 7) % len(pool)]
                n_lp += 1
                tema = plain(sec.get("tema") or "")
                heads = [sec["title"]] + [x.get("text", "") for x in sec.get("blocks", []) if x.get("type") == "h"] + [x.get("title", "") for x in sec.get("blocks", []) if x.get("title")]
                # la cabecera es una miga de pan: «NN · Parte» y, solo si aporta algo nuevo, el tema. Nunca repite lo que ya dice la hoja.
                partt = parts[pi]["title"]
                tope = partt if not redundancia.similar(partt, sec["title"], True) else ""
                if tema and not redundancia.similar(tema, partt, True) and not any(redundancia.similar(tema, h_, True) for h_ in heads):
                    tope = f"{tope} · {tema}" if tope else tema
                tope = f"{sec['n']}" + (f" · {tope}" if tope else "")
                tope = tope if len(tope) <= 54 else tope[:53] + "…"
                body.append(pages.light(inner, tope, meta.get("footer", "Documento"), item[2], sym, sid,
                                        f"{plain(sec['title'])} · {item[2]}", sec.get("kind") == "clave"))
        drip = ((design_dir / "defs.svg.txt").read_text() if (design_dir / "defs.svg.txt").exists() else "")
        defs = sym.defs().replace("</svg>", drip + "</svg>")
        final = head + defs + "".join(body) + "<script>" + FIT_JS + "</script></body></html>"
        out_pdf = Path(out_pdf)
        out_pdf.parent.mkdir(parents=True, exist_ok=True)
        html_path = out_pdf.with_suffix(".html")
        html_path.write_text(final, encoding="utf-8")

        # 4) PDF y auditoría (794 print, 1300 y 400 como pide auditoria.md)
        page2 = browser.new_page(viewport={"width": 794, "height": 1123})
        page2.emulate_media(media="print")
        page2.goto(html_path.resolve().as_uri())
        page2.evaluate("document.fonts.ready")
        page2.wait_for_timeout(800)
        page2.evaluate("window.__fit()")
        report["correcciones_contraste"] = page2.evaluate(FIX_JS)
        kw = dict(path=str(out_pdf), format=dims["pdf"], print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        try:
            page2.pdf(**kw, tagged=True, outline=True)
        except TypeError:
            page2.pdf(**kw)
        try:
            import pikepdf
            with pikepdf.open(str(out_pdf), allow_overwriting_input=True) as pdf:
                pdf.docinfo["/Title"] = plain(meta.get("title", ""))
                pdf.docinfo["/Author"] = meta.get("author", "")
                pdf.docinfo["/Subject"] = meta.get("subject", "")
                pdf.docinfo["/Keywords"] = ", ".join(meta.get("keywords", []))
                pdf.docinfo["/Creator"] = f"servidor de documentos · diseño {m['id']} {m['version']}"
                pdf.Root.Lang = pikepdf.String("es")
                pdf.Root.ViewerPreferences = pikepdf.Dictionary(DisplayDocTitle=True)
                pdf.save()
        except Exception as e:  # noqa: BLE001
            report["avisos"].append({"bloque": "metadatos", "causa": f"no se pudieron escribir ({type(e).__name__})", "ajuste": "instala pikepdf"})
        for label, width, media in (("794-print", 794, "print"), ("1300", 1300, "screen"), ("400", 400, "screen")):
            page2.set_viewport_size({"width": width, "height": 1123})
            page2.emulate_media(media=media)
            page2.wait_for_timeout(200)
            page2.evaluate("window.__fit()")
            res = page2.evaluate(AUDIT_JS)
            if res:
                report["auditoria"][label] = res[:40] + ([{"mas": len(res) - 40}] if len(res) > 40 else [])
        browser.close()
    report["avisos"] += ctx.warn
    report["variantes_usadas"] = sorted(reg.used)
    report["variantes_no_aprobadas"] = reg.not_approved()
    report["imagenes_necesarias"] = ctx.missing
    for src in sorted(set(ctx.no_credit)):
        report["avisos"].append({"bloque": src, "causa": "imagen usada sin fila en creditos.csv", "ajuste": "añade autor y licencia al CSV"})
    n_hojas = 1 + len(plan)
    try:
        info = subprocess.run(["pdfinfo", str(out_pdf)], capture_output=True, text=True).stdout
        report["paginas"] = int([l for l in info.splitlines() if l.startswith("Pages")][0].split()[1])
    except Exception:
        report["paginas"] = None
    if report["paginas"] and report["paginas"] != n_hojas:
        report["avisos"].append({"bloque": "pdf", "causa": f"el PDF tiene {report['paginas']} páginas y el documento {n_hojas} hojas", "ajuste": "revisa desbordes de hoja"})
    if report["auditoria"] or report["avisos"]:
        report["estado"] = "con_avisos"
    report["segundos"] = round(time.time() - t0, 1)
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("doc")
    ap.add_argument("-o", "--out", default="salida/documento.pdf")
    ap.add_argument("--imagenes", default="imagenes")
    a = ap.parse_args()
    rep = run(a.doc, a.out, a.imagenes)
    out = Path(a.out).with_name(Path(a.out).stem + ".informe.json")
    out.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: (v if k not in ("auditoria",) else {kk: len(vv) for kk, vv in v.items()}) for k, v in rep.items()}, ensure_ascii=False)[:3000])
    sys.exit(0 if rep["estado"] in ("ok", "con_avisos") else 1)


if __name__ == "__main__":
    main()
