#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Mide cuántos tokens gasta un agente CON myStyle frente a SIN la herramienta. Escribe servidor/web/stats/tokens.json.
"""python servidor/tools/tokens.py            (regenera servidor/web/stats/tokens.json; metodología en servidor/tools/TOKENS.md)

CON  = Prompt Maestro corto + contrato JSON que escribe el agente + informe que devuelve la API + 1 corrección por parche (promedio).
SIN  = artefacto que el agente tendría que escribir a mano (HTML+CSS+SVG del PDF sin base64; script python-pptx / python-docx / openpyxl equivalente;
       composición HyperFrames del video) × factor de iteraciones (central 3; rango 2–4).
Contador: endpoint count_tokens de Anthropic si hay ANTHROPIC_API_KEY (conteo exacto); si no, caracteres / 3,6 marcado «estimado».
"""
import json
import math
import os
import re
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "servidor"))
sys.path.insert(0, str(ROOT / "servidor" / "tools"))
import render  # noqa: E402
import render_office  # noqa: E402
import render_pptx  # noqa: E402
import render_video  # noqa: E402
import herramientas  # noqa: E402
from engine import prompt as prompt_mod  # noqa: E402

CHARS_POR_TOKEN = 3.6
FACTOR = {"central": 3, "min": 2, "max": 4}
FORMATS = {"pdf": "pdf-a4", "pptx": "pptx-16x9", "docx": "docx-a4", "xlsx": "xlsx", "video": "video-16x9"}
KEY = os.environ.get("ANTHROPIC_API_KEY", "")
METODO = "exacto (count_tokens de Anthropic)" if KEY else f"estimado (caracteres / {CHARS_POR_TOKEN})"


def contar(texto):
    if KEY:
        try:
            req = urllib.request.Request("https://api.anthropic.com/v1/messages/count_tokens", json.dumps({"model": "claude-sonnet-5-5", "messages": [{"role": "user", "content": texto}]}).encode(),
                                         {"content-type": "application/json", "x-api-key": KEY, "anthropic-version": "2023-06-01"})
            return int(json.loads(urllib.request.urlopen(req, timeout=60).read())["input_tokens"])
        except Exception:  # noqa: BLE001
            pass
    return math.ceil(len(texto) / CHARS_POR_TOKEN)


def compacto(o):
    return json.dumps(o, ensure_ascii=False, separators=(",", ":"))


def sin_base64(html):
    """El agente no escribe imágenes ni fuentes incrustadas: se quitan los data: URI."""
    return re.sub(r"data:[\w/+.-]+;base64,[A-Za-z0-9+/=]+", "data:", html)


# ---------- SIN: el artefacto escrito a mano ----------
def tokens_pptx(path):
    from pptx import Presentation
    p, t = Presentation(str(path)), 650
    for s in p.slides:
        t += 90
        for sh in s.shapes:
            t += 60
            if sh.has_text_frame:
                t += contar(sh.text_frame.text)
            if getattr(sh, "has_table", False) and sh.has_table:
                t += sum(10 + contar(c.text) for r in sh.table.rows for c in r.cells)
            if getattr(sh, "has_chart", False) and sh.has_chart:
                t += 80 + sum(12 * len(list(pl.categories)) * max(1, len(list(pl.series))) for pl in sh.chart.plots)
    return t


def tokens_docx(path):
    from docx import Document
    d, t = Document(str(path)), 500
    for para in d.paragraphs:
        t += 25 + contar(para.text)
    for tb in d.tables:
        t += sum(10 + contar(c.text) for r in tb.rows for c in r.cells)
    t += 60 * len(d.inline_shapes)
    return t


def tokens_xlsx(path):
    import openpyxl
    wb, t = openpyxl.load_workbook(str(path)), 400
    for ws in wb:
        t += 15 * ws.max_row + 120 * len(ws._charts)
        t += sum(9 for row in ws.iter_rows() for c in row if c.value is not None)
    return t


def reporte_corto(rep):
    return compacto(herramientas.Cliente.short({k: v for k, v in rep.items()}))


def medir(tmp):
    docs = []
    for f in sorted((ROOT / "contenido").glob("*.json")):
        doc = json.loads(f.read_text(encoding="utf-8"))
        if "document" not in doc:
            continue
        design = doc.get("design", "anura")
        txt = compacto(doc)
        n_bl = sum(len(s.get("blocks", [])) for p in doc["document"]["parts"] for s in p["sections"]) or 1
        fila = {"id": f.stem, "design": design, "bloques": n_bl, "contrato": contar(txt), "formatos": {}}
        parche = contar(compacto({"ops": [{"op": "set", "section": "s1", "block": "kpi-ab12c", "value": {"type": "p", "text": "x" * 80}}], "motivo": "corrige"})) + math.ceil(fila["contrato"] / n_bl)
        for k, fmt in FORMATS.items():
            d = {**doc, "format": fmt}
            src = tmp / f"{f.stem}.{k}.json"
            src.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
            out = tmp / f"{f.stem}.{k}"
            if k == "pdf":
                rep = render.run(src, out.with_suffix(".pdf"), str(ROOT / "imagenes"))
                h = sin_base64(out.with_suffix(".html").read_text(encoding="utf-8"))
                art = contar(h)
                art_min = contar(re.sub(r"<style>.*?</style>", "", h, flags=re.S))       # cota baja: el agente reutiliza el CSS del diseño
            elif k == "pptx":
                rep = render_pptx.run(src, out.with_suffix(".pptx"), str(ROOT / "imagenes"))
                art = tokens_pptx(out.with_suffix(".pptx"))
            elif k in ("docx", "xlsx"):
                rep = render_office.run(src, out.with_suffix("." + k), str(ROOT / "imagenes"))
                art = (tokens_docx if k == "docx" else tokens_xlsx)(out.with_suffix("." + k))
            else:
                proj = tmp / f"{f.stem}_video"
                proj.mkdir(exist_ok=True)
                rep = {"estado": "ok", "formato": fmt, "errores": [], "avisos": [], "auditoria": {}}
                try:
                    dr, idx = render_video.build(d, proj, fmt, rep)
                    rep.update({"duracion_s": round(dr.t, 2)})
                    art = contar(sin_base64(idx.read_text(encoding="utf-8")))
                except Exception as e:  # noqa: BLE001
                    fila["formatos"][k] = {"error": str(e)[:120]}
                    continue
            rep.setdefault("job", "x")
            informe = contar(reporte_corto(rep))
            prompt = contar(prompt_mod.prompt_maestro(design, fmt, doc.get("palette", "default"), {}, "A", True))
            con = prompt + fila["contrato"] + informe + parche
            fila["formatos"][k] = {"con": {"prompt_maestro": prompt, "contrato": fila["contrato"], "informe": informe, "correccion": parche, "total": con},
                                   "artefacto_a_mano": art, **({"artefacto_sin_estilos": art_min} if k == "pdf" else {}), "sin": {"min": art * FACTOR["min"], "central": art * FACTOR["central"], "max": art * FACTOR["max"]},
                                   "ahorro_pct": round(100 * (1 - con / (art * FACTOR["central"])), 1), "estado": rep.get("estado")}
        docs.append(fila)
        print("·", f.stem, {k: v.get("ahorro_pct") for k, v in fila["formatos"].items()})
    return docs


def agregar(docs):
    out = {}
    for k in FORMATS:
        v = [d["formatos"][k] for d in docs if k in d["formatos"] and "con" in d["formatos"][k]]
        if not v:
            continue
        con, sin = [x["con"]["total"] for x in v], [x["sin"]["central"] for x in v]
        med = lambda a: round(sum(a) / len(a))      # noqa: E731
        out[k] = {"n": len(v), "con": {"media": med(con), "min": min(con), "max": max(con)}, "sin": {"media": med(sin), "min": min(sin), "max": max(sin),
                                                                                                        "rango_factor": [med([x["sin"]["min"] for x in v]), med([x["sin"]["max"] for x in v])]},
                  "ahorro_pct": round(100 * (1 - sum(con) / sum(sin)), 1)}
        if k == "pdf":
            lo = [x["artefacto_sin_estilos"] * FACTOR["central"] for x in v]
            out[k]["ahorro_pct_cota_baja"] = round(100 * (1 - sum(con) / sum(lo)), 1)
    return out


def agentes(docs):
    from api import openapi
    ej = next((d for d in docs if d["id"] == "informe_ventas"), docs[0])
    base = ej["formatos"].get("pdf", {}).get("con", {})
    md = ROOT / "contenido" / "prompt_master_uso.md"
    reg = ROOT / "servidor" / "data" / "director.jsonl"
    local = [json.loads(x) for x in reg.read_text(encoding="utf-8").splitlines()] if reg.exists() else []
    return {
        "mismo_contrato": f"el contrato de «{ej['id']}» pesa {ej['contrato']} tokens para cualquier agente",
        "claude_mcp": {"definiciones_herramientas_completo": contar(compacto(herramientas.mcp_tools())),
                       "definiciones_herramientas_minimo": contar(compacto([t for t in herramientas.openai_tools(core_only=True)])), "por_documento": base.get("total")},
        "chatgpt_openapi": {"definiciones_openapi": contar(compacto(openapi())), "por_documento": base.get("total")},
        "modelo_local": {"corridas_registradas": len(local), "tokens_entrada_media": round(sum(x.get("tokens_in", 0) for x in local) / len(local)) if local else None,
                         "tokens_salida_media": round(sum(x.get("tokens_out", 0) for x in local) / len(local)) if local else None, "costo": "0 (tu GPU)",
                         "nota": "las definiciones de herramientas se pagan una vez por conversación, no por documento"},
        "markdown_en_vez_de_json": ({"documento": md.name, "markdown": contar(md.read_text(encoding="utf-8")),
                                     "contrato_json": contar(compacto(json.loads((ROOT / "contenido" / "prompt_master_uso.json").read_text(encoding="utf-8"))))} if md.exists() else None),
    }


def recetas_medidas():
    """Una llamada con receta: list_recipes + recipe_get + create_from_recipe (3 huecos cambiados) + informe corto. Sin el contrato JSON ni el Markdown."""
    import biblioteca
    from engine import recetas
    filas = []
    for r in biblioteca.todos("receta"):
        vals = {k: h["defecto"] for k, h in list(r["huecos"].items())[:3]}
        pasos = {"list_recipes": compacto([{"id": r["id"], "tipo": "receta", "descripcion": r["descripcion"][:110]}]), "recipe_get": compacto(recetas.ficha(r)),
                 "create_from_recipe": compacto({"receta": r["id"], "valores": vals}), "informe": compacto({"estado": "ok", "job": "0" * 12, "formato": "pdf-a4", "pdf": "http://127.0.0.1:8765/v1/files/x.pdf"})}
        filas.append({"id": r["id"], "formato": r.get("formato"), "tokens": sum(contar(v) for v in pasos.values()), "sin_recipe_get": sum(contar(v) for k, v in pasos.items() if k != "recipe_get")})
    n = len(filas)
    return {"n": n, "media": round(sum(f["tokens"] for f in filas) / n), "media_sin_recipe_get": round(sum(f["sin_recipe_get"] for f in filas) / n), "recetas": filas,
            "nota": "list_recipes + recipe_get + create_from_recipe con 3 huecos + informe; las definiciones de herramientas se pagan una vez por conversación"}


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    with tempfile.TemporaryDirectory() as t:
        docs = medir(Path(t))
    gasto = json.loads((ROOT / "referencias" / "prompt-master" / "gasto.json").read_text(encoding="utf-8"))
    res = {"generado": time.strftime("%Y-%m-%d"), "metodo_conteo": METODO, "estimado": not KEY, "factor_iteraciones": FACTOR,
           "evidencia_factor": "referencias/prompt-master/gasto.json: 4 iteraciones visuales para un estilo; ver servidor/tools/TOKENS.md",
           "formatos": agregar(docs), "estilo_nuevo": {"tokens": gasto["total"], "pasos": gasto["pasos"], "medicion": gasto["medicion"], "modelo": gasto["modelo"], "fuente": gasto["fuente"]},
           "agentes": agentes(docs), "recetas": recetas_medidas(), "documentos": docs}
    dest = ROOT / "servidor" / "web" / "stats"
    dest.mkdir(exist_ok=True)
    (dest / "tokens.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    import shutil
    shutil.copy(Path(__file__).with_name("TOKENS.md"), dest / "TOKENS.md")
    print("→", dest / "tokens.json")
    for k, v in res["formatos"].items():
        print(f"{k:6} CON {v['con']['media']:>6}  SIN {v['sin']['media']:>7}  ahorro {v['ahorro_pct']} %  (n={v['n']})")


if __name__ == "__main__":
    main()
