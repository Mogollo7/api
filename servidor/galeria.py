#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Galería de variantes: una tarjeta por plantilla, dibujada con el motor real (no con maquetas), para APROBARLAS.

    python servidor/galeria.py --imagenes teoria/imagenes            # escribe salida/galeria/galeria_<paleta>.html y .pdf
    # abre el HTML, marca cada variante (propuesta / aprobada / rechazada) y pulsa «Exportar aprobaciones»
    python servidor/aprobar.py aprobaciones.json                       # las aplica al registro (designs/anura/variantes.json)

Los datos de las muestras son de ejemplo (valores como 12, 34, 56 y una dispersión simulada): ninguna cifra es un resultado.
"""
import argparse
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from engine import assets, atoms_svg, blocks, pages, variants  # noqa: E402
from engine.text import esc  # noqa: E402

FIT_JS = (HERE / "engine/fit.js").read_text()


def samples(imgs_ok):
    rnd = random.Random(7)
    pts = [[x, round(5 + 0.6 * x + rnd.gauss(0, 2.2), 2)] for x in [rnd.uniform(1, 10) for _ in range(60)]]
    tab = {"head": ["Variable", "Rango", "Tipo"], "rows": [["variable_a", "0 a 100", "int8"], ["variable_b", "1972 a 2024", "int16"], ["variable_c", "texto", "category"]]}
    tones = {"head": ["Organismo", "Especie", "Etapa", "Edad"], "rows": [["Grupo A", {"t": "F", "tone": "f"}, {"t": "P", "tone": "p"}, {"t": "L", "tone": "l"}], ["Grupo B", {"t": "P", "tone": "p"}, {"t": "—", "tone": "n"}, {"t": "F", "tone": "f"}]]}
    bar = {"type": "bar", "data": {"max": 100, "items": [{"l": "A", "v": 40, "hi": True}, {"l": "B", "v": 62}, {"l": "C", "v": 85}]}}
    S = {}
    S["TB-1"] = {"type": "table", **tab}
    S["TB-2"] = {"type": "table", "variant": "compact", **tab}
    S["TB-3"] = {"type": "table", "variant": "ficha", "head": ["Revisión", "Resultado"], "rows": [["Registros", "Texto de muestra del resultado."], ["Faltantes", "Texto de muestra del resultado."]]}
    S["TB-4"] = {"type": "table", **tones}
    for t in blocks.CALLOUT_TONES:
        S[f"AV-{t}"] = {"type": "callout", "tone": t, "title": "Título de muestra", "text": "Texto de muestra del aviso, con una frase corta."}
    S["CF-1"] = {"type": "kpi", "items": [{"v": "12", "l": "etiqueta A", "note": "nota"}, {"v": "34 %", "l": "etiqueta B"}, {"v": "56", "l": "etiqueta C"}]}
    S["CF-2"] = {"type": "stats", "title": "Cifras", "items": [{"v": "0,00", "l": "primera medida"}, {"v": "00,0", "l": "segunda medida"}], "note": "Nota breve de lectura."}
    S["CF-3"] = {"type": "big", "value": "00,0", "unit": "%", "caption": "Texto de la cifra grande"}
    S["FG-1"] = {"type": "chart", "title": "Título del gráfico", "tag": "etiqueta · muestra", "chart": bar, "caption": "Figura 1. Pie de muestra."}
    S["FG-2"] = {"type": "figure", "title": "Título de la figura", "chart": bar, "caption": "Figura 2. Pie de muestra.", "side": [{"v": "0,00", "l": "medida A"}, {"v": "0,00", "l": "medida B"}]}
    S["FG-3"] = {"type": "image", "src": "dimorfismo/rana_arvalis_macho_azul.jpg" if imgs_ok else None, "ratio": "16/9", "caption": "Pie de imagen de muestra."}
    S["GR-bar"] = {"type": "chart", "title": "Barras", "tag": "estándar", "chart": bar}
    S["GR-hbar"] = {"type": "chart", "title": "Barras horizontales", "tag": "estándar", "chart": {"type": "hbar", "data": {"max": 10, "items": [{"l": "Categoría uno", "v": 8, "hi": True}, {"l": "Categoría dos", "v": 5}, {"l": "Categoría tres", "v": 3}]}}}
    S["GR-line"] = {"type": "chart", "title": "Líneas", "tag": "estándar", "chart": {"type": "line", "data": {"points": [[1, 20], [2, 45], [3, 40], [4, 70]], "xrange": [0, 5], "yrange": [0, 100], "xlabel": "eje x", "ylabel": "eje y"}}}
    S["GR-stack"] = {"type": "chart", "title": "Apiladas", "tag": "estándar", "chart": {"type": "stack", "data": {"rows": [{"l": "Perfil A", "v": [60, 30, 10]}, {"l": "Perfil B", "v": [30, 50, 20]}]}, "legend": [["Serie 1", "k"], ["Serie 2", "hi"], ["Serie 3", "w"]]}}
    S["GR-hist"] = {"type": "chart", "title": "Histograma", "tag": "estándar · datos de muestra", "chart": {"type": "hist", "data": {"bars": [[1, 3], [2, 8], [3, 14], [4, 22], [5, 17], [6, 9], [7, 4]], "width": 1, "xlabel": "valor", "ylabel": "frecuencia", "lines": [{"x": 4.1, "label": "Media", "style": "mean"}, {"x": 4, "label": "Mediana", "style": "median"}]}}}
    S["GR-box"] = {"type": "chart", "title": "Cajas", "tag": "estándar · datos de muestra", "chart": {"type": "box", "data": {"xrange": [0, 10], "xlabel": "valor", "groups": [{"l": "Grupo A", "lo": 2, "q1": 4, "med": 5, "q3": 7, "hi": 9, "out": [0.5]}, {"l": "Grupo B", "lo": 3, "q1": 5, "med": 6, "q3": 7.5, "hi": 9.5, "out": []}]}}}
    S["GR-scatter"] = {"type": "chart", "title": "Dispersión + tendencia", "tag": "SIMULACIÓN · puntos aleatorios", "chart": {"type": "scatter", "data": {"points": pts, "trend": "auto", "xlabel": "variable x", "ylabel": "variable y", "xrange": [0, 11], "yrange": [0, 16]}}, "sim": True}
    S["GR-heat"] = {"type": "chart", "title": "Mapa de calor", "tag": "estándar · datos de muestra", "chart": {"type": "heat", "data": {"labels": ["A", "B", "C", "D"], "matrix": [[1, .5, -.3, 0], [.5, 1, .1, -.6], [-.3, .1, 1, .8], [0, -.6, .8, 1]]}}}
    S["GR-map"] = {"type": "chart", "title": "Mapa de puntos", "tag": "contorno esquemático · coordenadas reales de ciudades", "chart": {"type": "map", "data": {"outline": "colombia", "size": True, "points": [{"lon": -74.07, "lat": 4.71, "label": "Bogotá", "v": 3}, {"lon": -75.57, "lat": 6.24, "label": "Medellín", "v": 2}, {"lon": -76.53, "lat": 3.45, "label": "Cali", "v": 2}, {"lon": -74.8, "lat": 10.96, "label": "Barranquilla", "v": 1}]}}}
    S["FL-1"] = {"type": "flow", "cols": 3, "steps": [{"title": "Paso uno", "text": "Descripción corta."}, {"title": "Paso dos", "text": "Descripción corta."}, {"title": "Paso tres", "text": "Descripción corta.", "on": True}]}
    S["FL-2"] = {"type": "flowchart", "title": "Diagrama de flujo", "nodes": [{"id": "a", "label": "Inicio", "kind": "start"}, {"id": "b", "label": "Leer datos", "kind": "io"}, {"id": "c", "label": "¿Datos válidos?", "kind": "decision"}, {"id": "d", "label": "Procesar"}, {"id": "e", "label": "Corregir"}, {"id": "f", "label": "Fin", "kind": "end"}], "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}, {"from": "c", "to": "d", "label": "sí"}, {"from": "c", "to": "e", "label": "no"}, {"from": "d", "to": "f"}, {"from": "e", "to": "b"}]}
    S["FL-3"] = {"type": "ladder", "items": [{"title": "Opción simple", "text": "Descripción.", "cost": "costo: bajo"}, {"title": "Opción media", "text": "Descripción.", "cost": "costo: medio"}, {"title": "Opción compleja", "text": "Descripción.", "cost": "costo: alto"}]}
    S["FL-4"] = {"type": "timeline", "items": [{"code": "E1", "label": "Etapa uno", "days": 3, "vis": "h", "photo": "texto"}, {"code": "E2", "label": "Etapa dos", "days": 2, "vis": "v", "photo": "texto"}, {"code": "E3", "label": "Etapa tres", "days": 1, "vis": "x", "photo": "texto"}], "adult": {"code": "A", "label": "Final", "days": "—", "photo": "texto"}, "legend": [["v", "visible"], ["h", "oculta"], ["x", "difícil"]], "caption": "Pie de muestra."}
    S["FL-5"] = {"type": "ranks", "head": ["Columna A", "Columna B"], "rows": [{"rank": "Nivel 1", "v": ["Valor", "Valor"]}, {"rank": "Nivel 2", "v": ["Valor", "Valor"]}, {"rank": "Nivel 3", "v": ["Valor", "Valor"]}]}
    S["FL-6"] = {"type": "compare", "left": {"title": "Opción A", "sub": "subtítulo", "items": ["Ventaja uno", "Ventaja dos"]}, "right": {"title": "Opción B", "sub": "subtítulo", "items": ["Ventaja uno", "Ventaja dos"]}, "verdict": "Veredicto de muestra."}
    S["FM-1"] = {"type": "form", "title": "Datos del estudiante", "rows": ["Nombre completo", "Ficha / grupo", "Fecha de entrega"]}
    return S


ATOMS = {
    "AT-color": lambda roles: '<div class="sw">' + "".join(f'<div class="a2" style="background:{roles[k]};color:{"#fff" if k in ("negro","bosque","hoja") else "#000"}"><b>{k}</b><span>{roles[k]}</span></div>' for k in roles) + "</div>",
    "AT-tipo": lambda roles: '<div class="tipo"><div><span style="font-family:var(--font-display);font-size:7cqw;text-transform:uppercase">Anton · Títulos</span></div><div><span style="font-family:var(--font-body);font-size:2.6cqw">Archivo · texto corrido de párrafos</span></div><div><span class="mono" style="font-size:2cqw">IBM PLEX MONO · DATOS Y ETIQUETAS</span></div></div>',
    "AT-regla": lambda roles: '<div style="display:flex;flex-direction:column;gap:3cqw"><div style="border-top:.35cqw solid var(--negro)">fina</div><div style="border-top:.7cqw solid var(--negro)">media</div><div style="border-top:.8cqw solid var(--negro)">gruesa</div><div style="border:.6cqw solid var(--negro);padding:2cqw">caja, radio 0</div></div>',
    "AT-etiqueta": lambda roles: blocks.inline("[FUENTE] [CALC] [INF] [SIN FUENTE] [SIM] dato pendiente"),
    "AT-boton": lambda roles: '<div class="fila-b"><span class="btn p">Primario</span><span class="btn s">Secundario</span><span class="btn c">Píldora</span></div>',
    "AT-campo": lambda roles: '<div class="form"><div class="fh">Campo</div><div><b>Etiqueta</b><i></i></div></div>',
}

PAGE_SAMPLES = {
    "HJ-1": ("normal", [{"type": "p", "text": "Texto de muestra de una hoja normal: titular, párrafos y bloques en flujo."}, {"type": "table", "head": ["A", "B"], "rows": [["uno", "dos"], ["tres", "cuatro"]]}]),
    "HJ-2": ("clave", [{"type": "p", "text": "Texto de muestra bajo la tarjeta de punto clave."}]),
    "HJ-3": ("tablero", [{"type": "kpi", "items": [{"v": "12", "l": "A"}, {"v": "34", "l": "B"}]}]),
}

CSS = """
*{box-sizing:border-box}body{margin:0;background:var(--crema);color:var(--negro);font-family:var(--font-body)}
.top{position:sticky;top:0;z-index:5;background:var(--negro);color:var(--crema);padding:12px 20px;display:flex;gap:14px;align-items:center;flex-wrap:wrap}
.top h1{font-family:var(--font-display);font-weight:400;font-size:26px;margin:0;text-transform:uppercase;letter-spacing:.02em}
.top a,.top button,.top .f{font-family:var(--font-mono);font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--crema);background:none;border:2px solid var(--crema);padding:6px 10px;cursor:pointer;text-decoration:none}
.top .f.on,.top button.p{background:var(--vivo);color:var(--negro);border-color:var(--vivo)}
.cnt{font-family:var(--font-mono);font-size:12px;margin-left:auto}
main{padding:20px;display:grid;grid-template-columns:repeat(auto-fill,minmax(470px,1fr));gap:20px;align-items:start}
.card{border:3px solid var(--negro);background:var(--crema);box-shadow:6px 6px 0 var(--negro);break-inside:avoid}
.card header{display:grid;grid-template-columns:auto 1fr auto;gap:8px;align-items:center;padding:8px 10px;border-bottom:3px solid var(--negro);background:var(--arena)}
.card header b{font-family:var(--font-mono);font-size:13px;background:var(--negro);color:var(--crema);padding:2px 6px}
.card header h3{margin:0;font-family:var(--font-display);font-weight:400;font-size:20px;text-transform:uppercase;line-height:1}
.card select{font-family:var(--font-mono);font-size:12px;border:2px solid var(--negro);background:var(--crema);padding:3px}
.card.aprobada{box-shadow:6px 6px 0 var(--vivo)}.card.aprobada header{background:var(--vivo)}
.card.rechazada{opacity:.45}
.stage{padding:12px;background:var(--crema);overflow:hidden}
.card p{margin:0;padding:8px 10px;font-family:var(--font-mono);font-size:11.5px;line-height:1.45;border-top:2px solid var(--negro)}
.nv{font-family:var(--font-mono);font-size:11px;text-transform:uppercase;letter-spacing:.08em}
.page.gp{aspect-ratio:auto;height:auto;overflow:visible;padding:4cqw 5cqw;box-shadow:none;border:0}
.page.gp .cont{position:static}
.sw{display:grid;grid-template-columns:repeat(6,1fr)}
@media print{.top,.card select{display:none}main{grid-template-columns:1fr 1fr;gap:10px;padding:0}.card{box-shadow:none}.stage{padding:6px}}
@page{size:A4;margin:10mm}
"""

JS = """
const KEY='galeria-aprobaciones';let st={};try{st=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
function paint(){let c={propuesta:0,aprobada:0,rechazada:0};document.querySelectorAll('.card').forEach(k=>{const s=k.querySelector('select').value;k.classList.remove('aprobada','rechazada');if(s!=='propuesta')k.classList.add(s);c[s]++});document.getElementById('cnt').textContent=`aprobadas ${c.aprobada} · propuestas ${c.propuesta} · rechazadas ${c.rechazada}`}
document.querySelectorAll('.card').forEach(k=>{const s=k.querySelector('select'),id=k.dataset.id;if(st[id])s.value=st[id];s.onchange=()=>{st[id]=s.value;try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}paint()}});
document.querySelectorAll('.f').forEach(b=>b.onclick=()=>{document.querySelectorAll('.f').forEach(x=>x.classList.remove('on'));b.classList.add('on');const t=b.dataset.k;document.querySelectorAll('.card').forEach(k=>k.style.display=(t==='*'||k.dataset.kind===t)?'':'none')});
document.getElementById('exp').onclick=()=>{const o={};document.querySelectorAll('.card').forEach(k=>o[k.dataset.id]=k.querySelector('select').value);const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(o,null,1)],{type:'application/json'}));a.download='aprobaciones.json';a.click()};
paint();
"""


def build(out_dir: Path, images_root: Path, palette: str):
    design_dir = HERE / "designs/anura"
    m = json.loads((design_dir / "manifest.json").read_text())
    pals = json.loads((design_dir / "palettes.json").read_text())
    roles = dict(m["palette"]["roles"])
    roles.update(pals.get(palette, {}))
    reg = variants.Registry(design_dir)
    sym = assets.Symbols(design_dir)
    warn = []
    ctx = blocks.Ctx(m, roles, images_root, assets.load_credits(images_root), HERE / ".cache", [], design_dir)
    pc = pages.PageCtx(design_dir, m, roles, sym, images_root, HERE / ".cache", warn)
    atoms = dict(ATOMS)
    atoms["AT-simbolo"] = lambda r: '<div style="display:flex;gap:4cqw;align-items:center">' + "".join(assets.sym_html(sym, g, "width:7cqw;height:7cqw", "sym") for g in ("g01", "g64", "g35", "g84", "g12")) + "</div>"
    atoms["AT-franja"] = lambda r: '<div style="width:40cqw;height:9cqw">' + atoms_svg.hazard() + "</div>"
    atoms["AT-codigo"] = lambda r: '<div style="width:50cqw;height:12cqw">' + atoms_svg.barcode("muestra 000") + "</div>"
    atoms["AT-cruz"] = lambda r: '<div style="display:flex;gap:6cqw">' + "".join(atoms_svg.cross() for _ in range(3)).replace("atm-cross", "atm-cross\" style=\"width:6cqw;height:6cqw") + "</div>"
    atoms["AT-xcaja"] = lambda r: '<div style="width:10cqw">' + atoms_svg.xbox() + "</div>"
    atoms["AT-pila"] = lambda r: '<div style="width:70cqw;display:flex;flex-direction:column;gap:1cqw">' + "".join(f'<div class="cv4-row" data-fit="f" data-maxh="14" style="height:12cqw"><span>{w}</span></div>' for w in ("TÍTULO", "DE", "MUESTRA")) + "</div>"
    imgs_ok = (images_root / "dimorfismo/rana_arvalis_macho_azul.jpg").exists()
    S = samples(imgs_ok)
    meta = {"title": "Muestra", "date": "Mes 2026", "version": "Vol. 01 · v0.1", "header_left": ["Título de muestra", "Subtítulo"]}
    cov = {"vertical": "TÍTULO MUESTRA", "title": "Título del documento", "text": "Contexto del texto de muestra, en pocas líneas."}
    part = {"title": "Sección", "desc": "Descripción de muestra de la sección en una o dos líneas."}
    cards = []
    for v in reg.data["variantes"]:
        i = v["id"]
        if i.startswith("CV-"):
            c2 = dict(cov)
            if i == "CV-4":
                c2.update({"stack": ["TÍTULO", "DE", "MUESTRA"], "badge": {"lines": ["TEXTO", "DE", "MUESTRA"], "tag": "NO.00"}, "quote": ["FRASE", "DE", "MUESTRA."], "strip": ["UNO", "DOS", "TRES"], "number": "00",
                           "list": ["Línea uno", "Línea dos", "Línea tres"], "notes": ["Nota uno", "Nota dos", "Nota tres"], "code": "MUESTRA 000", "tagline_l": "Frase corta.",
                           "image": "renacuajos/bufo_serie_metamorfosis.jpg" if imgs_ok else None})
            stage, w = pages.cover(pc, meta, c2, i), 300
        elif i.startswith("DV-"):
            stage, w = pages.divider(pc, i[-1], "01", 4, part), 300
        elif i.startswith("HJ-"):
            kind, bl = PAGE_SAMPLES[i]
            inner = f'<div class="u"><h3 class="sec">Titular</h3></div>' + "".join(f'<div class="u">{blocks.render(b, ctx)}</div>' for b in bl)
            if kind == "clave":
                inner += f'<div class="u">{blocks.callout({"tone": "clave", "text": "Idea que hay que llevarse."}, ctx)}</div>'
            stage, w = pages.light(inner, "01 · Parte · Tema", "PIE · muestra", 2, sym, "g01", "muestra", kind == "clave"), 300
        elif i in atoms:
            stage, w = f'<article class="page lp gp"><div class="cont">{atoms[i](roles)}</div></article>', 640
        else:
            stage, w = f'<article class="page lp gp"><div class="cont">{blocks.render(S[i], ctx)}</div></article>', 640
        cards.append(
            f'<section class="card {v["estado"]}" data-id="{i}" data-kind="{v["tipo"]}"><header><b>{i}</b><h3>{esc(v["nombre"])}</h3>'
            f'<select><option value="propuesta">propuesta</option><option value="aprobada">aprobada</option><option value="rechazada">rechazada</option></select></header>'
            f'<div class="stage"><div style="width:{w}px;zoom:{0.68 if w > 400 else 1}">{stage}</div></div>'
            f'<p><span class="nv">{v["nivel"]}</span> · {esc(v["uso"])} · origen: {esc(v["origen"])}</p></section>'
        )
    cards = [c.replace(f'<option value="{v["estado"]}">', f'<option value="{v["estado"]}" selected>') for c, v in zip(cards, reg.data["variantes"])]
    kinds = sorted({v["tipo"] for v in reg.data["variantes"]})
    other = [p for p in pals if p != "_marca" and p != palette]
    nav = "".join(f'<a href="galeria_{p}.html">paleta {p}</a>' for p in other)
    head = (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Galería de variantes · {palette}</title><style>{assets.font_css(design_dir, m)}{assets.root_css(roles)}'
            f'{(design_dir/"bundle.css").read_text()}{(design_dir/"extras.css").read_text()}{CSS}</style></head><body>')
    top = (f'<div class="top"><h1>Galería de variantes · {palette}</h1><button class="f on" data-k="*">todas</button>'
           + "".join(f'<button class="f" data-k="{k}">{k}</button>' for k in kinds) + nav
           + '<span class="cnt" id="cnt"></span><button class="p" id="exp">Exportar aprobaciones</button></div>')
    html = head + sym.defs().replace("</svg>", (design_dir / "drip.svg.txt").read_text() + "</svg>") + top + "<main>" + "".join(cards) + f"</main><script>{FIT_JS}</script><script>{JS}</script></body></html>"
    out_dir.mkdir(parents=True, exist_ok=True)
    f = out_dir / f"galeria_{palette}.html"
    f.write_text(html, encoding="utf-8")
    return f, warn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--imagenes", default="imagenes")
    ap.add_argument("--salida", default="salida/galeria")
    ap.add_argument("--pdf", action="store_true", help="también un PDF de la paleta por defecto")
    a = ap.parse_args()
    out = Path(a.salida)
    files = []
    for pal in ("anura", "cine"):
        f, w = build(out, Path(a.imagenes), pal)
        files.append(f)
        print(f, "avisos:", w)
    if a.pdf:
        import os
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            exe = os.environ.get("CHROMIUM_PATH") or ("/opt/pw-browsers/chromium" if Path("/opt/pw-browsers/chromium").exists() else None)
            b = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
            pg = b.new_page(viewport={"width": 1100, "height": 1400})
            pg.emulate_media(media="print")
            pg.goto(files[0].resolve().as_uri())
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(800)
            pg.evaluate("window.__fit()")
            pg.pdf(path=str(out / "galeria_anura.pdf"), format="A4", print_background=True)
            b.close()


if __name__ == "__main__":
    main()
