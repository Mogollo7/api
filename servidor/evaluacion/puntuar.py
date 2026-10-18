#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Puntúa los archivos que creó un agente (Haiku, Opus, Codex…) en las 20 entradas de casos.json, igual que evaluar.py con el modelo local.
"""python servidor/evaluacion/puntuar.py resultados_haiku.json [--etiqueta haiku]
resultados = {"c01": "<job de 12 hex>", …}. Por caso mide: formato correcto, bloques esperados en el contrato, estado del motor (ok=1, con_avisos=.5), y si usó una receta
(la ficha del job lo dice en `origen`). Imprime una tabla y escribe salida/evaluacion/agentes/<etiqueta>.json para compararlo con otro sujeto."""
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAIZ = HERE.parent.parent
FORMATO = {"pdf": "pdf-a4", "pptx": "pptx-16x9", "docx": "docx-a4", "xlsx": "xlsx", "video": ("video-16x9", "video-9x16")}


def get(path):
    with urllib.request.urlopen("http://127.0.0.1:8765" + path, timeout=60) as r:
        return json.loads(r.read())


def bloques(doc):
    return {b.get("type") for p in doc.get("document", {}).get("parts", []) for s in p.get("sections", []) for b in s.get("blocks", []) if isinstance(b, dict)}


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    etiqueta = sys.argv[sys.argv.index("--etiqueta") + 1] if "--etiqueta" in sys.argv else Path(a[0]).stem
    jobs = json.loads(Path(a[0]).read_text(encoding="utf-8"))
    casos = json.loads((HERE / "casos.json").read_text(encoding="utf-8"))["casos"]
    filas = []
    for c in casos:
        job = jobs.get(c["id"])
        if not job:
            filas.append({"id": c["id"], "hecho": False})
            continue
        try:
            doc = get(f"/v1/jobs/{job}/doc")
            inf = get(f"/v1/jobs/{job}")
        except Exception as e:  # noqa: BLE001
            filas.append({"id": c["id"], "hecho": False, "error": str(e)[:80]})
            continue
        quiere = FORMATO[c["formato"]]
        fmt_ok = doc.get("format") in (quiere if isinstance(quiere, tuple) else (quiere,))
        estado = inf.get("estado")
        filas.append({"id": c["id"], "hecho": True, "formato": fmt_ok, "bloques": set(c["bloques"]) <= bloques(doc), "estado": estado,
                      "calidad": 1.0 if estado == "ok" else .5 if estado == "con_avisos" else 0.0, "bloques_vistos": sorted(bloques(doc))})
    n = len(filas)
    res = {"sujeto": etiqueta, "casos": n, "hechos": sum(f["hecho"] for f in filas), "formato": sum(bool(f.get("formato")) for f in filas) / n,
           "bloques": sum(bool(f.get("bloques")) for f in filas) / n, "calidad": sum(f.get("calidad", 0) for f in filas) / n}
    for f in filas:
        print(f"{f['id']} " + ("sin job" if not f["hecho"] else f"formato={int(f['formato'])} bloques={int(f['bloques'])} estado={f['estado']}"))
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items()})
    dest = RAIZ / "salida" / "evaluacion" / "agentes"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / f"{etiqueta}.json").write_text(json.dumps({"resumen": res, "casos": filas}, ensure_ascii=False, indent=1, default=list), encoding="utf-8")


if __name__ == "__main__":
    main()
