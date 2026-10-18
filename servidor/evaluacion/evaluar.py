#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Evaluación del modelo local con 20 entradas fijas. El motor filtra primero; a Claude solo van los fallos y una muestra.
"""python servidor/evaluacion/evaluar.py [--solo c01,c02] [--max 5] [--modelo qwen2.5:3b] [--muestra 10] [--guardar-base]

Mide por caso: herramienta (¿llamó la correcta?), reutilización (¿buscó en la biblioteca antes de crear?), segmentación (¿los bloques esperados salieron en el contrato?),
calidad visual (estado del motor: ok / con_avisos / rechazado). Escribe salida/evaluacion/<fecha>/{resultados.json, resumen.md, lote_claude.md}.
`lote_claude.md` trae SOLO los fallos y una muestra fija (semilla) para pegarle a Claude: ahorra tokens. `--guardar-base` fija la línea base antes de entrenar."""
import argparse
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import director  # noqa: E402
import herramientas  # noqa: E402

RAIZ = HERE.parent.parent
CREA = {"pdf": "create_pdf", "pptx": "create_pptx", "video": "create_video", "docx": "render", "xlsx": "render"}
BASE = HERE / "linea_base.json"


def tipos_bloque(cliente, job):
    c, d = cliente.api("GET", f"/v1/jobs/{job}/doc")
    if c != 200 or not isinstance(d, dict):
        return set()
    return {b.get("type") for p in d.get("document", {}).get("parts", []) for s in p.get("sections", []) for b in s.get("blocks", []) if isinstance(b, dict)}


def corre(caso, cfg, cliente):
    cerebro = director.Cerebro(cfg)
    traza, t0 = [], time.time()
    tarea = f"{caso['tarea']} (formato: {caso['formato']}) (estilo: {caso['estilo']})"
    try:
        r, pasos, rech, motivo, _ = director.bucle(tarea, cfg, cerebro, cliente, "", traza)
    except SystemExit as e:
        raise SystemExit(str(e))
    except Exception as e:  # noqa: BLE001
        r, pasos, rech, motivo = None, 0, 0, f"excepción: {str(e)[:120]}"
    llamadas = [x["tool"] for x in traza]
    crea = next((i for i, n in enumerate(llamadas) if n.startswith("create_") or n == "render"), None)
    job = (r or {}).get("job") if isinstance(r, dict) else None
    tipos = tipos_bloque(cliente, job) if job else set()
    estado = (r or {}).get("estado") if isinstance(r, dict) else None
    m = {"herramienta": crea is not None and llamadas[crea] == CREA[caso["formato"]],
         "reutilizacion": crea is not None and "search_library" in llamadas[:crea],
         "segmentacion": bool(tipos) and set(caso["bloques"]) <= tipos,
         "calidad": 1.0 if estado == "ok" else (0.5 if estado == "con_avisos" else 0.0)}
    return {"id": caso["id"], "tarea": caso["tarea"], "formato": caso["formato"], "metricas": m, "estado": estado, "job": job, "bloques": sorted(t for t in tipos if t), "pasos": pasos,
            "rechazos": rech, "escalado": bool(motivo), "motivo": motivo, "tokens_in": cerebro.tokens_in, "tokens_out": cerebro.tokens_out, "segundos": round(time.time() - t0, 1), "traza": traza}


def resumen(res):
    n = len(res) or 1
    return {"casos": len(res), "herramienta": round(sum(r["metricas"]["herramienta"] for r in res) / n, 3), "reutilizacion": round(sum(r["metricas"]["reutilizacion"] for r in res) / n, 3),
            "segmentacion": round(sum(r["metricas"]["segmentacion"] for r in res) / n, 3), "calidad": round(sum(r["metricas"]["calidad"] for r in res) / n, 3),
            "sin_error_de_validacion": round(sum(1 for r in res if r["estado"] in ("ok", "con_avisos")) / n, 3), "escalados": sum(r["escalado"] for r in res),
            "tokens_in": sum(r["tokens_in"] for r in res), "tokens_out": sum(r["tokens_out"] for r in res)}


def falla(r):
    m = r["metricas"]
    return r["escalado"] or not (m["herramienta"] and m["segmentacion"]) or m["calidad"] < 1


def lote(res, muestra, semilla=7):
    fallos = [r for r in res if falla(r)]
    ok = [r for r in res if not falla(r)]
    random.Random(semilla).shuffle(ok)
    sel = fallos + ok[:max(0, muestra - len(fallos))] if muestra else fallos
    L = ["# Lote para revisar con Claude (solo fallos + muestra)\n", "Por cada caso: qué está mal, dónde, qué regla viola y la corrección. Guarda cada una con `save_correction` (origen: claude).\n"]
    for r in sel:
        L.append(f"## {r['id']} · {r['formato']} · {'FALLO' if falla(r) else 'muestra'}\n**Tarea:** {r['tarea']}\n\n**Métricas:** {json.dumps(r['metricas'])} · estado: {r['estado']} · pasos: {r['pasos']} · bloques: {', '.join(r['bloques'])}\n")
        if r.get("motivo"):
            L.append(f"**Motivo de escalado:** {r['motivo']}\n")
        L.append("```json\n" + json.dumps(r["traza"], ensure_ascii=False, indent=1)[:2500] + "\n```\n")
    return "\n".join(L)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--solo")
    ap.add_argument("--max", type=int)
    ap.add_argument("--modelo")
    ap.add_argument("--muestra", type=int, default=10)
    ap.add_argument("--guardar-base", action="store_true")
    a = ap.parse_args()
    casos = json.loads((HERE / "casos.json").read_text(encoding="utf-8"))["casos"]
    if a.solo:
        casos = [c for c in casos if c["id"] in a.solo.split(",")]
    if a.max:
        casos = casos[:a.max]
    cfg = director.cargar_config({"modelo": a.modelo})
    cliente = herramientas.Cliente(cfg["mystyle_url"], cfg["mystyle_key"])
    res = []
    for c in casos:
        r = corre(c, cfg, cliente)
        res.append(r)
        print(f"{c['id']} {c['formato']:5} herr={int(r['metricas']['herramienta'])} reuso={int(r['metricas']['reutilizacion'])} seg={int(r['metricas']['segmentacion'])} calidad={r['metricas']['calidad']} pasos={r['pasos']} {r['segundos']}s")
    s = resumen(res)
    dest = RAIZ / "salida" / "evaluacion" / time.strftime("%Y%m%d_%H%M%S")
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "resultados.json").write_text(json.dumps({"modelo": cfg["modelo"], "resumen": s, "casos": res}, ensure_ascii=False, indent=1), encoding="utf-8")
    base = json.loads(BASE.read_text(encoding="utf-8")) if BASE.exists() else None
    md = [f"# Evaluación · {cfg['modelo']} · {time.strftime('%Y-%m-%d %H:%M')}\n", "| Métrica | Ahora | Línea base |", "|---|---|---|"]
    for k in ("herramienta", "reutilizacion", "segmentacion", "calidad", "sin_error_de_validacion"):
        md.append(f"| {k} | {s[k]:.0%} | {(str(round(base['resumen'][k] * 100)) + ' %') if base else '—'} |")
    md.append(f"\nEscalados a Claude: {s['escalados']} de {s['casos']} · tokens locales {s['tokens_in']}/{s['tokens_out']}\n")
    (dest / "resumen.md").write_text("\n".join(md), encoding="utf-8")
    (dest / "lote_claude.md").write_text(lote(res, a.muestra), encoding="utf-8")
    if a.guardar_base:
        BASE.write_text(json.dumps({"modelo": cfg["modelo"], "fecha": time.strftime("%Y-%m-%d"), "resumen": s}, ensure_ascii=False, indent=1), encoding="utf-8")
        print("línea base guardada en", BASE)
    print("\n" + "\n".join(md))
    print("→", dest)


if __name__ == "__main__":
    main()
