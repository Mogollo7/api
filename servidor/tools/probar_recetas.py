#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Comprueba que cada receta/ingrediente del supermercado sale completo SIN rellenar nada (valores por defecto) y pasa el contrato.
"""python servidor/tools/probar_recetas.py [id ...] [--render]     (--render: además la dibuja en PDF, PPTX, Word y Excel con la API en :8765; sale 1 si algo falla)"""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import biblioteca  # noqa: E402
from engine import contract, markdown, recetas  # noqa: E402


def post(path, body):
    try:
        with urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8765" + path, json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=300) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ids = [a for a in sys.argv[1:] if not a.startswith("--")]
    mal = 0
    for e in biblioteca.todos("receta") + biblioteca.todos("ingrediente"):
        if ids and e["id"] not in ids:
            continue
        probs = []
        for k, h in e.get("huecos", {}).items():
            if h.get("defecto") in (None, "", []) or not h.get("desc"):
                probs.append(f"hueco '{k}' sin defecto o sin desc")
        if e["tipo"] == "receta":
            md, av, _ = recetas.receta(e["id"])
        else:
            md, av = recetas.componer([{"id": e["id"]}], {"titulo": e.get("nombre", "x")})
        doc, av2 = markdown.a_contrato(md, {"design": e.get("estilo", "anura")})
        m = json.loads((ROOT / "designs" / doc["design"] / "manifest.json").read_text(encoding="utf-8"))
        w = []
        m = {**m, "formats": list(dict.fromkeys(m["formats"] + ["video-16x9", "video-9x16", "web-animada"]))}      # como hace la API
        errs = contract.validate(doc, m, w)
        probs += [f"contrato: {x}" for x in errs] + [f"aviso: {x.get('causa')}" for x in av + av2] + ([f"{len(w)} avisos del contrato"] if w else [])
        if "--render" in sys.argv and e["tipo"] == "receta" and e.get("formato") != "video":
            for fmt in ("pdf-a4", "pptx-16x9", "docx-a4", "xlsx"):
                r = post("/v1/render", {"receta": e["id"], "format": fmt})
                if r.get("estado") != "ok" or r.get("avisos"):
                    probs.append(f"{fmt}: {r.get('estado')} {[a.get('causa') for a in r.get('avisos', [])][:2] or r.get('error')}")
        print(("✔" if not probs else "✘"), e["tipo"], e["id"], "; ".join(probs))
        mal += bool(probs)
    sys.exit(1 if mal else 0)


if __name__ == "__main__":
    main()
