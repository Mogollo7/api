#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Contrato JSON -> Word (docx-a4) y Excel (xlsx). Mismo contrato, roles de color y fuentes que el PDF, el PPTX y el video.

    python servidor/render_office.py contenido/informe_ventas.json -o salida/office/informe.docx
    python servidor/render_office.py contenido/informe_ventas.json -o salida/office/informe.xlsx

Word: estilos con las fuentes y colores del diseño, índice (campo TOC), encabezados, tablas con cabecera repetida, avisos, citas, código,
listas anidadas, imágenes en dos tintas, notas; los gráficos se dibujan con el MISMO motor del PDF (SVG → PNG 2x con Chromium).
Excel: una hoja por tabla y por gráfico, con números reales, fila de totales con =SUMA() y gráfico nativo editable con la paleta.
Lo que un formato no puede representar se degrada con aviso (nunca rompe). Texto del documento = dato.
"""
import argparse
import sys
import json
import re
import tempfile
from pathlib import Path

import render
from engine import assets, charts, contract, paleta
from engine.text import plain

FORMATS = {".docx": "docx-a4", ".xlsx": "xlsx"}
TOK = re.compile(r"(\*\*.+?\*\*|`[^`]+`|(?<![\w*])\*(?!\s).+?(?<!\s)\*(?![\w*])|\[\^\w{1,3}\])")
TONES = {"nota": ("arena", "NOTA"), "clave": ("bosque", "CLAVE"), "ojo": ("ocre", "OJO"), "sim": ("arena", "SIMULACIÓN"), "pend": ("arena", "PENDIENTE"),
         "regla": ("negro", "REGLA"), "slate": ("arena", "NOTA"), "hueco": ("arena", "HUECO")}


def num(v):
    """'1.234,5' / '62,9 %' / 12 -> float, o None. Para que Excel tenga números de verdad (y las fórmulas funcionen)."""
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    s = plain(str(v.get("t", "") if isinstance(v, dict) else v)).replace("−", "-").strip()
    m = re.fullmatch(r"([-+]?)[$€]?\s*(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?\s*(%|[a-zA-Z]{0,3})?", s)
    if not m:
        return None
    return float(f"{m.group(1)}{m.group(2).replace('.', '')}.{m.group(3) or 0}")


def blocks_of(doc):
    for part in doc["document"].get("parts", []):
        for sec in part.get("sections", []):
            for b in sec.get("blocks", []):
                yield part, sec, b


def chart_pngs(doc, roles, design_dir, m, rep):
    """Todos los gráficos del documento a PNG en UNA sesión de Chromium, con el estilo del diseño (mismo motor que el PDF)."""
    items = [(i, b["chart"]) for i, (_, _, b) in enumerate(blocks_of(doc)) if b.get("type") in ("chart", "figure") and b.get("chart")]
    if not items:
        return {}
    css = assets.font_css(design_dir, m) + assets.root_css(roles, m) + "".join((design_dir / f).read_text(encoding="utf-8") for f in ("bundle.css", "extras.css") if (design_dir / f).exists())
    svgs = {}
    for i, ch in items:
        try:
            svgs[i] = charts.draw(ch, roles)
        except Exception as e:  # noqa: BLE001
            rep["avisos"].append({"bloque": f"gráfico {ch.get('type')}", "causa": str(e)[:120], "ajuste": "se mostró la tabla de datos"})
    if not svgs:
        return {}
    from playwright.sync_api import sync_playwright
    out = {}
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(device_scale_factor=2, viewport={"width": 760, "height": 600})
        for i, svg in svgs.items():
            pg.set_content(f'<html><head><style>{css} body{{margin:0;background:{roles["crema"]}}} #c{{width:720px;padding:12px}} #c svg{{width:100%;height:auto;display:block}}</style></head>'
                           f'<body><div id="c">{svg}</div></body></html>')
            pg.evaluate("document.fonts.ready")
            out[i] = pg.locator("#c").screenshot(type="png")
        br.close()
    return out


# ---------------------------------------------------------------- Word
def to_docx(doc, out, images_root, m, roles, design_dir, rep):
    from docx import Document
    from docx.enum.section import WD_SECTION
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_BREAK
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor

    C = {k: RGBColor.from_string(v.lstrip("#").upper()) for k, v in roles.items()}
    fam = [f["family"] for f in m["fonts"]]
    FD, FB, FM = fam[0], fam[1] if len(fam) > 1 else fam[0], fam[2] if len(fam) > 2 else fam[-1]
    pairs = {tuple(x) for x in m["palette"]["pares_texto_permitidos"]}
    fg = lambda bg, prefs=("negro", "crema", "bosque"): next((r for r in prefs if (r, bg) in pairs), "negro" if paleta.ratio(roles["negro"], roles[bg]) >= 4.5 else "crema")
    pngs = chart_pngs(doc, roles, design_dir, m, rep)
    d = Document()
    sec0 = d.sections[0]
    sec0.page_width, sec0.page_height = Cm(21), Cm(29.7)
    for s in d.sections:
        s.left_margin = s.right_margin = Cm(2.2)
        s.top_margin, s.bottom_margin = Cm(2.2), Cm(2.2)
    st = d.styles
    st["Normal"].font.name, st["Normal"].font.size = FB, Pt(10.5)
    st["Normal"].font.color.rgb = C["negro"]
    st["Normal"].paragraph_format.space_after = Pt(6)
    for name, size, col in (("Title", 34, "negro"), ("Heading 1", 26, "negro"), ("Heading 2", 18, "negro"), ("Heading 3", 11, "hoja")):
        s = st[name]
        s.font.name, s.font.size, s.font.bold = (FM if name == "Heading 3" else FD), Pt(size), name == "Heading 3"
        s.font.color.rgb = C[col] if (col, "crema") in pairs or col == "negro" else C["negro"]
        rf = s.element.get_or_add_rPr().get_or_add_rFonts()
        for k in ("w:ascii", "w:hAnsi", "w:cs"):
            rf.set(qn(k), s.font.name)
        for k in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme"):
            rf.attrib.pop(qn(k), None)

    def runs(p, t, size=None, bold=False, color=None, font=None):
        for piece in TOK.split(str(t)):
            if not piece:
                continue
            txt, b, i, f = piece, bold, False, font
            if piece.startswith("**") and piece.endswith("**"):
                txt, b = piece[2:-2], True
            elif piece.startswith("`") and piece.endswith("`"):
                txt, f = piece[1:-1], FM
            elif piece.startswith("[^"):
                txt = f"[{piece[2:-1]}]"
            elif len(piece) > 2 and piece[0] == "*" and piece[-1] == "*":
                txt, i = piece[1:-1], True
            r = p.add_run(txt)
            r.bold, r.italic = b or None, i or None
            if f:
                r.font.name = f
            if size:
                r.font.size = Pt(size)
            if color:
                r.font.color.rgb = C[color]
        return p

    def shade(cell, role):
        tcPr = cell._tc.get_or_add_tcPr()
        sh = OxmlElement("w:shd")
        sh.set(qn("w:val"), "clear")
        sh.set(qn("w:color"), "auto")
        sh.set(qn("w:fill"), roles[role].lstrip("#"))
        tcPr.append(sh)

    def table(head, rows, widths=None, size=9.5):
        nc = max(len(head), max((len(r) for r in rows), default=1))
        t = d.add_table(rows=0, cols=nc)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        if head:
            cells = t.add_row().cells
            trPr = t.rows[0]._tr.get_or_add_trPr()
            h = OxmlElement("w:tblHeader")        # cabecera repetida en cada página
            h.set(qn("w:val"), "true")
            trPr.append(h)
            for j in range(nc):
                shade(cells[j], "negro")
                runs(cells[j].paragraphs[0], str(head[j]).upper() if j < len(head) else "", size - 1, True, fg("negro", ("crema",)), FM)
        for i, r in enumerate(rows):
            cells = t.add_row().cells
            for j in range(nc):
                v = r[j] if j < len(r) else ""
                hi = isinstance(v, dict) and v.get("hi")
                txt = v.get("t", "") if isinstance(v, dict) else v
                bg = "ocre" if hi else ("arena" if i % 2 else "crema")
                shade(cells[j], bg)
                runs(cells[j].paragraphs[0], f"{txt:g}".replace(".", ",") if isinstance(txt, float) else txt, size, bool(hi), fg(bg))
        if widths and len(widths) == nc:
            for j, wv in enumerate(widths):
                for row in t.rows:
                    row.cells[j].width = Cm(16.6 * wv / sum(widths))
        d.add_paragraph()
        return t

    def caption(t):
        if t:
            runs(d.add_paragraph(), t, 8.5, False, "negro")

    def image(src, treatment, cap, width_cm=16.6):
        f = Path(images_root) / src if src else None
        if not f or not f.exists():
            p = d.add_paragraph()
            runs(p, f"[IMAGEN NECESARIA: {src or ''}]", 9, True, "negro", FM)
            rep["imagenes_necesarias"].append({"imagen": src or "", "que": plain(cap or "")})
            return
        try:
            f = assets.duotone(f, treatment or "calido", roles, m["image_treatments"], Path(tempfile.gettempdir()) / "anura-office-cache")
        except Exception:  # noqa: BLE001
            pass
        d.add_picture(str(f), width=Cm(width_cm))
        caption(cap)

    meta, docd = doc.get("meta", {}), doc["document"]
    cov = docd["cover"]
    # portada
    runs(d.add_paragraph(), " · ".join(meta.get("header_left") or []), 9, True, "negro", FM)
    p = d.add_paragraph()
    runs(p, plain(cov.get("vertical", "")).upper(), 54, False, fg("crema", ("bosque", "hoja", "negro")), FD)
    d.add_paragraph(plain(cov.get("title", "")), style="Title")
    runs(d.add_paragraph(), cov.get("text", ""), 13)
    runs(d.add_paragraph(), " · ".join(x for x in (meta.get("date"), meta.get("version")) if x), 9, True, "negro", FM)
    if cov.get("image"):
        image(cov["image"], cov.get("treatment") or "ocre", cov.get("alt"), 12)
    d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    # índice (Word lo completa al abrir: «Actualizar campos»)
    d.add_paragraph("Índice", style="Heading 2")
    fld = d.add_paragraph().add_run()
    for tag, txt in (("begin", None), (None, 'TOC \\o "1-2" \\h \\z \\u'), ("separate", None), (None, "Actualiza el índice (clic derecho → Actualizar campo)."), ("end", None)):
        if tag:
            e = OxmlElement("w:fldChar")
            e.set(qn("w:fldCharType"), tag)
            fld._r.append(e)
        elif txt.startswith("TOC"):
            e = OxmlElement("w:instrText")
            e.set(qn("xml:space"), "preserve")
            e.text = txt
            fld._r.append(e)
        else:
            e = OxmlElement("w:t")
            e.text = txt
            fld._r.append(e)
    # pie con número de página
    fp = d.sections[0].footer.paragraphs[0]
    runs(fp, (meta.get("footer") or meta.get("title", "")) + "   ·   ", 8, False, "negro", FM)
    r = fp.add_run()
    for tag, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        if tag:
            e = OxmlElement("w:fldChar")
            e.set(qn("w:fldCharType"), tag)
        else:
            e = OxmlElement("w:instrText")
            e.text = txt
        r._r.append(e)

    bi = -1
    n = 0
    for k, part in enumerate(docd.get("parts", [])):
        d.add_section(WD_SECTION.NEW_PAGE)
        runs(d.add_paragraph(), f"{k+1:02d}", 60, False, fg("crema", ("bosque", "hoja", "negro")), FD)
        d.add_paragraph(plain(part.get("title", "")), style="Heading 1")
        runs(d.add_paragraph(), part.get("desc", ""), 11)
        for sec in part.get("sections", []):
            n += 1
            d.add_paragraph(f"{n:02d} · {plain(sec.get('title', ''))}", style="Heading 2")
            if sec.get("lead"):
                if sec.get("kind") == "clave":
                    t = d.add_table(rows=1, cols=1)
                    shade(t.cell(0, 0), "bosque")
                    runs(t.cell(0, 0).paragraphs[0], sec["lead"], 12, True, fg("bosque", ("crema",)))
                    d.add_paragraph()
                else:
                    runs(d.add_paragraph(), sec["lead"], 12, True)
            for b in sec.get("blocks", []):
                bi += 1
                t = b.get("type")
                if t == "p":
                    runs(d.add_paragraph(), b.get("text", ""))
                elif t == "h":
                    d.add_paragraph(plain(b.get("text", "")), style="Heading 3")
                elif t in ("list", "refs"):
                    if t == "refs":
                        d.add_paragraph(plain(b.get("title") or "Referencias"), style="Heading 3")
                    ordered = b.get("ordered") or t == "refs"
                    for it in b.get("items", []):
                        runs(d.add_paragraph(style="List Number" if ordered else "List Bullet"), it.get("t", "") if isinstance(it, dict) else it)
                        for sub in (it.get("items", []) if isinstance(it, dict) else []):
                            runs(d.add_paragraph(style="List Bullet 2"), sub)
                elif t == "table":
                    table(b.get("head") or [], b.get("rows") or [], b.get("widths"))
                    caption(b.get("caption"))
                elif t in ("chart", "figure"):
                    if b.get("title"):
                        runs(d.add_paragraph(), b["title"], 11, True)
                    if bi in pngs:
                        import io
                        d.add_picture(io.BytesIO(pngs[bi]), width=Cm(16.6 if t == "chart" and not b.get("half") else 12))
                    elif b.get("image"):
                        image(b["image"].get("src"), b["image"].get("treatment"), b["image"].get("caption"), 12)
                    if b.get("side"):
                        table([], [[str(s.get("v", "")), plain(s.get("l", ""))] for s in b["side"]])
                    caption(b.get("caption"))
                elif t in ("kpi", "stats"):
                    its = b.get("items", [])
                    tt = d.add_table(rows=2, cols=max(len(its), 1))
                    for j, it in enumerate(its):
                        shade(tt.cell(0, j), "negro" if j == 0 else "bosque")
                        shade(tt.cell(1, j), "negro" if j == 0 else "bosque")
                        bg = "negro" if j == 0 else "bosque"
                        runs(tt.cell(0, j).paragraphs[0], str(it.get("v", "")), 22, False, fg(bg, ("vivo", "ocre", "crema")), FD)
                        runs(tt.cell(1, j).paragraphs[0], it.get("l", ""), 9, True, fg(bg, ("crema",)))
                    d.add_paragraph()
                elif t == "big":
                    runs(d.add_paragraph(), f"{b.get('value', '')}{b.get('unit', '')}", 72, False, fg("crema", ("bosque", "hoja", "negro")), FD)
                    runs(d.add_paragraph(), b.get("caption", ""), 12, True)
                elif t == "callout":
                    bg, lab = TONES.get(b.get("tone", "nota"), TONES["nota"])
                    tt = d.add_table(rows=1, cols=1)
                    c = tt.cell(0, 0)
                    shade(c, bg)
                    runs(c.paragraphs[0], (b.get("label") or lab).upper(), 8, True, fg(bg), FM)
                    for para in ([f"**{b['title']}**"] if b.get("title") else []) + (b.get("paras") or [b.get("text", "")]):
                        runs(c.add_paragraph(), para, 10, False, fg(bg))
                    d.add_paragraph()
                elif t == "quote":
                    p = d.add_paragraph()
                    p.paragraph_format.left_indent = Cm(1.2)
                    runs(p, "“" + plain(b.get("text", "")) + "”", 15, True)
                    if b.get("by"):
                        runs(d.add_paragraph(), "— " + plain(b["by"]), 9, True, "negro", FM).paragraph_format.left_indent = Cm(1.2)
                elif t == "code":
                    tt = d.add_table(rows=1, cols=1)
                    c = tt.cell(0, 0)
                    shade(c, "negro")
                    for k_, ln in enumerate(b.get("code", "").split("\n")):
                        pp = c.paragraphs[0] if k_ == 0 else c.add_paragraph()
                        rr = pp.add_run(ln or " ")
                        rr.font.name, rr.font.size = FM, Pt(9)
                        rr.font.color.rgb = C[fg("negro", ("crema",))]
                    d.add_paragraph()
                    caption(b.get("caption"))
                elif t == "image":
                    for it in (b.get("items") or [b]):
                        image(it.get("src"), it.get("treatment") or b.get("treatment"), it.get("caption") or b.get("caption"), 16.6 / max(1, len(b.get("items") or [1])) if b.get("items") else 16.6)
                elif t == "flow":
                    for k_, s_ in enumerate(b.get("steps", [])):
                        runs(d.add_paragraph(style="List Number"), f"**{plain(s_.get('title', ''))}**" + (f": {s_['text']}" if s_.get("text") else ""))
                elif t == "ladder":
                    table(["Opción", "Descripción", "Costo"], [[x.get("title", ""), x.get("text", ""), x.get("cost", "")] for x in b.get("items", [])])
                elif t == "ranks":
                    table(["Rango"] + list(b.get("head") or []), [[r.get("rank", "")] + list(r.get("v", [])) for r in b.get("rows", [])])
                elif t == "timeline":
                    rows = [[x.get("code", ""), x.get("label", ""), str(x.get("days", "")), x.get("photo", "")] for x in b.get("items", [])]
                    if b.get("adult"):
                        a = b["adult"]
                        rows.append([a.get("code", ""), a.get("label", ""), str(a.get("days", "")), a.get("photo", "")])
                    table(["Código", "Etapa", "Días", "Foto"], rows)
                    caption(b.get("caption"))
                elif t == "compare":
                    L, R = b.get("left") or {}, b.get("right") or {}
                    hi = max(len(L.get("items", [])), len(R.get("items", [])))
                    table([L.get("title", ""), R.get("title", "")], [[(L.get("items") or [""] * hi)[i] if i < len(L.get("items", [])) else "", R["items"][i] if i < len(R.get("items", [])) else ""] for i in range(hi)])
                    if b.get("verdict"):
                        runs(d.add_paragraph(), b["verdict"], 11, True)
                elif t == "form":
                    if b.get("title"):
                        runs(d.add_paragraph(), b["title"], 11, True)
                    table([], [[r, ""] for r in b.get("rows", [])], [1, 2])
                elif t == "flowchart":
                    nodes = {x["id"]: plain(x.get("label", "")) for x in b.get("nodes", [])}
                    for e in b.get("edges", []):
                        runs(d.add_paragraph(style="List Bullet"), f"{nodes.get(e.get('from'), '?')} → {nodes.get(e.get('to'), '?')}" + (f" ({plain(e['label'])})" if e.get("label") else ""))
                    rep["avisos"].append({"bloque": sec.get("id", ""), "causa": "diagrama de flujo en Word como lista de pasos", "ajuste": "usa el PDF o el PPTX para verlo dibujado"})
                elif t == "media":
                    if b.get("poster"):
                        image(b["poster"], None, b.get("caption"), 12)
                    runs(d.add_paragraph(), f"▶ {b.get('kind', 'video')}: {b.get('url') or b.get('src', '')}", 9, True, "negro", FM)
                elif t == "toc":
                    pass                                    # el índice ya está al inicio
                else:
                    runs(d.add_paragraph(), re.sub(r"<[^>]+>", " ", b.get("html") or b.get("text") or "")[:600])
                    rep["avisos"].append({"bloque": sec.get("id", ""), "causa": f"bloque '{t}' como texto simple en Word", "ajuste": "usa un bloque del vocabulario"})
            for nt in sec.get("notes", []):
                runs(d.add_paragraph(), f"[{nt.get('n')}] {plain(nt.get('text', ''))}", 8)
    cp = d.core_properties
    cp.title, cp.author, cp.subject, cp.keywords = meta.get("title", ""), meta.get("author", ""), meta.get("subject", ""), ", ".join(meta.get("keywords", []))
    d.save(out)
    rep["graficos"] = len(pngs)


# ---------------------------------------------------------------- Excel
def to_xlsx(doc, out, m, roles, rep):
    from openpyxl import Workbook
    from openpyxl.chart import BarChart, LineChart, PieChart, Reference, ScatterChart, Series
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    hx = lambda r: roles[r].lstrip("#").upper()
    fam = [f["family"] for f in m["fonts"]]
    head_font, body_font = Font(name=fam[-1], bold=True, color=hx("crema")), Font(name=fam[1] if len(fam) > 1 else fam[0])
    head_fill, band = PatternFill("solid", fgColor=hx("negro")), PatternFill("solid", fgColor=hx("arena"))
    SER = ["hoja", "vivo", "negro", "ocre", "bosque"]
    wb = Workbook()
    ws0 = wb.active
    ws0.title = "Resumen"
    meta = doc.get("meta", {})
    ws0["A1"] = plain(meta.get("title", ""))
    ws0["A1"].font = Font(name=fam[0], size=20, color=hx("negro"))
    ws0["A2"] = plain(doc["document"]["cover"].get("text", ""))
    ws0.append([])
    ws0.append(["Hoja", "Contenido", "Sección"])
    for c in ws0[4]:
        c.font, c.fill = head_font, head_fill
    used, n_t, n_c = set(), 0, 0

    def sheet(name):
        base = re.sub(r"[\\/*?:\[\]]", "", plain(name))[:28] or "Hoja"
        nm, k = base, 2
        while nm in used:
            nm, k = f"{base[:25]} {k}", k + 1
        used.add(nm)
        return wb.create_sheet(nm)

    def write_table(ws, head, rows, r0=1):
        nc = max(len(head), max((len(r) for r in rows), default=1))
        for j in range(nc):
            c = ws.cell(r0, j + 1, plain(str(head[j])) if j < len(head) else "")
            c.font, c.fill, c.alignment = head_font, head_fill, Alignment(vertical="center")
        numeric = [j for j in range(nc) if sum(num(r[j]) is not None for r in rows if j < len(r)) >= max(2, len(rows) * 0.8)]
        for i, r in enumerate(rows):
            for j in range(nc):
                v = r[j] if j < len(r) else ""
                nv = num(v) if j in numeric else None
                c = ws.cell(r0 + 1 + i, j + 1, nv if nv is not None else plain(str(v.get("t", "") if isinstance(v, dict) else v)))
                c.font = body_font
                if i % 2:
                    c.fill = band
                if nv is not None and "%" in str(v):
                    c.value, c.number_format = nv / 100, "0.0%"
                elif nv is not None:
                    c.number_format = "#,##0.##"
        if numeric and len(rows) >= 2:                     # fila de totales con fórmulas (editable)
            rt = r0 + 1 + len(rows)
            ws.cell(rt, 1, "Total" if 0 not in numeric else None).font = Font(bold=True)
            for j in numeric:
                col = get_column_letter(j + 1)
                c = ws.cell(rt, j + 1, f"=SUM({col}{r0 + 1}:{col}{rt - 1})")
                c.font = Font(bold=True)
                c.number_format = ws.cell(rt - 1, j + 1).number_format
        for j in range(nc):
            w = max([len(plain(str(head[j]))) if j < len(head) else 4] + [len(plain(str(r[j].get("t", "") if isinstance(r[j], dict) else r[j]))) for r in rows if j < len(r)])
            ws.column_dimensions[get_column_letter(j + 1)].width = min(60, max(10, w + 2))
        ws.freeze_panes = ws.cell(r0 + 1, 1)
        ws.auto_filter.ref = f"A{r0}:{get_column_letter(nc)}{r0 + len(rows)}"

    def chart_data(ch):
        t, dd = ch.get("type"), ch.get("data") or {}
        if t in ("bar", "hbar") and dd.get("series") and dd.get("categories"):
            return ["Categoría"] + [s.get("name", "") for s in dd["series"]], [[c] + [s["values"][i] for s in dd["series"]] for i, c in enumerate(dd["categories"])]
        if t in ("bar", "hbar", "pie"):
            return ["Etiqueta", "Valor"], [[plain(i.get("l", "")), i.get("v")] for i in dd.get("items", [])]
        if t == "line":
            series = dd.get("series") or [{"name": dd.get("ylabel") or "Valor", "points": dd.get("points", [])}]
            xs = list(dict.fromkeys(p[0] for s in series for p in s["points"]))
            return [dd.get("xlabel") or "x"] + [s.get("name", "") for s in series], [[x] + [{p[0]: p[1] for p in s["points"]}.get(x) for s in series] for x in xs]
        if t == "stack":
            names = dd.get("series") or [f"Parte {i+1}" for i in range(len(dd["rows"][0]["v"]))]
            return ["Grupo"] + list(names), [[plain(r["l"])] + list(r["v"]) for r in dd.get("rows", [])]
        if t == "hist":
            return [dd.get("xlabel") or "Valor", dd.get("ylabel") or "Conteo"], [list(b_) for b_ in dd.get("bars", [])]
        if t == "scatter":
            return [dd.get("xlabel") or "x", dd.get("ylabel") or "y"], [list(p[:2]) for p in dd.get("points", [])]
        if t == "box":
            return ["Grupo", "Mín", "Q1", "Mediana", "Q3", "Máx"], [[g.get("l") or "—", g.get("lo"), g.get("q1"), g.get("med"), g.get("q3"), g.get("hi")] for g in dd.get("groups", [])]
        if t == "heat":
            lab = dd.get("labels", [])
            return [""] + lab, [[lab[i] if i < len(lab) else ""] + list(r) for i, r in enumerate(dd.get("matrix", []))]
        if t == "map":
            return ["Lugar", "Longitud", "Latitud", "Valor"], [[p.get("label", ""), p.get("lon"), p.get("lat"), p.get("v")] for p in dd.get("points", [])]
        return None, None

    for part, sec, b in blocks_of(doc):
        t = b.get("type")
        if t == "table" and b.get("rows"):
            n_t += 1
            ws = sheet(f"T{n_t} {sec.get('title', '')}")
            write_table(ws, b.get("head") or [], b["rows"])
            ws0.append([ws.title, plain(b.get("caption") or "Tabla"), plain(sec.get("title", ""))])
        elif t in ("kpi", "stats") and b.get("items"):
            n_t += 1
            ws = sheet(f"Cifras {sec.get('title', '')}")
            write_table(ws, ["Cifra", "Valor", "Etiqueta"], [[str(i.get("v", "")), num(i.get("v")), i.get("l", "")] for i in b["items"]])
            ws0.append([ws.title, "Cifras clave", plain(sec.get("title", ""))])
        elif t in ("chart", "figure") and b.get("chart"):
            head, rows = chart_data(b["chart"])
            if not rows:
                continue
            n_c += 1
            ws = sheet(f"G{n_c} {b.get('title') or sec.get('title', '')}")
            write_table(ws, head, rows)
            ct = b["chart"].get("type")
            nr, nc = len(rows), len(head)
            ch = None
            if ct in ("bar", "hbar", "hist", "stack"):
                ch = BarChart()
                ch.type = "bar" if ct in ("hbar", "stack") else "col"
                if ct == "stack":
                    ch.grouping, ch.overlap = "percentStacked", 100
                if ct == "hist":
                    ch.gapWidth = 5
            elif ct == "line":
                ch = LineChart()
            elif ct == "pie":
                ch = PieChart()
            elif ct == "scatter":
                ch = ScatterChart()
                ch.style = 13
                s = Series(Reference(ws, min_col=2, min_row=2, max_row=nr + 1), Reference(ws, min_col=1, min_row=2, max_row=nr + 1), title=head[1])
                s.marker.symbol, s.graphicalProperties.line.noFill = "circle", True
                s.marker.graphicalProperties.solidFill = hx("hoja")
                ch.series.append(s)
            else:
                rep["avisos"].append({"bloque": sec.get("id", ""), "causa": f"gráfico '{ct}' sin equivalente nativo en Excel", "ajuste": "solo se exportaron los datos"})
            if ch is not None and ct != "scatter":
                ch.add_data(Reference(ws, min_col=2, max_col=nc, min_row=1, max_row=nr + 1), titles_from_data=True)
                ch.set_categories(Reference(ws, min_col=1, min_row=2, max_row=nr + 1))
                for j, s in enumerate(ch.series):
                    if ct != "pie":
                        s.graphicalProperties.solidFill = hx(SER[j % len(SER)])
                        s.graphicalProperties.line.solidFill = hx("negro") if ct != "line" else hx(SER[j % len(SER)])
            if ch is not None:
                ch.title = plain(b.get("title") or sec.get("title", ""))
                ch.width, ch.height = 18, 9
                ws.add_chart(ch, f"{get_column_letter(nc + 2)}2")
            ws0.append([ws.title, plain(b.get("title") or f"Gráfico {ct}"), plain(sec.get("title", ""))])
    ws0.column_dimensions["A"].width, ws0.column_dimensions["B"].width, ws0.column_dimensions["C"].width = 32, 48, 40
    if n_t + n_c == 0:
        rep["avisos"].append({"bloque": "documento", "causa": "no hay tablas, cifras ni gráficos", "ajuste": "Excel solo lleva el resumen; usa PDF o Word para texto"})
    wb.properties.title = meta.get("title", "")
    wb.save(out)
    rep["hojas"] = len(wb.sheetnames)


def run(doc_path, out, images_root):
    doc = json.loads(Path(doc_path).read_text(encoding="utf-8"))
    out = Path(out)
    fmt = FORMATS.get(out.suffix.lower())
    design_dir, m = render.load_design(doc.get("design", "anura"))
    warns = []
    errs = contract.validate({**doc, "format": fmt}, {**m, "formats": list(dict.fromkeys(m["formats"] + list(FORMATS.values())))}, warns)
    rep = {"estado": "ok", "formato": fmt, "errores": errs, "avisos": warns, "auditoria": {}, "imagenes_necesarias": []}
    if errs or not fmt:
        rep["estado"] = "rechazado"
        return rep
    roles = render.resolve_roles(doc, design_dir, m, rep["avisos"])
    rep["avisos"] += paleta.check(roles, m)
    out.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "docx-a4":
        to_docx(doc, out, images_root, m, roles, design_dir, rep)
        rep["fuentes"] = {"usa": sorted({f["family"] for f in m["fonts"]}), "nota": "Word no incrusta estas fuentes: instala los .ttf de /v1/designs/<id>/fonts.zip"}
    else:
        to_xlsx(doc, out, m, roles, rep)
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("doc")
    ap.add_argument("-o", "--out", required=True, help="termina en .docx o .xlsx")
    ap.add_argument("--imagenes", default="imagenes")
    a = ap.parse_args()
    rep = run(a.doc, a.out, a.imagenes)
    Path(a.out).with_suffix(".informe.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: rep.get(k) for k in ("estado", "formato", "graficos", "hojas")} | {"avisos": len(rep["avisos"])}, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")      # Windows: la consola cp1252 no acepta ✔ → ·
    main()
