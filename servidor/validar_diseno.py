#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""LISTA DE REVISIÓN de un diseño (la del Prompt Maestro). Un diseño está listo cuando todo sale ✔.

    python servidor/validar_diseno.py anura [--imagenes teoria/imagenes] [--rapido]

1 manifiesto completo · 2 fuentes con licencia · 3 paleta (7 roles, contraste ≥ 4,5, claridad en grises) · 4 al menos 2 portadas y 2 divisores con plantilla
· 5 clases CSS que el motor necesita · 6 símbolos de portada (3–5) · 7 cada plantilla de portada/divisor se dibuja sin campos sueltos
· 8 documento de muestra CORTO: sin avisos de degradación y auditoría limpia · 9 documento LARGO: auditoría limpia (sin desbordes) · 10 sin redundancia.
"""
import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import render  # noqa: E402
from engine import assets, muestras, pages, paleta, variants  # noqa: E402

ROLES = ["negro", "bosque", "hoja", "vivo", "ocre", "crema", "arena"]
CSS_NEEDS = [".page", ".cover", ".dv", ".lp", ".tope", ".cont", ".pie", ".tab", ".co", ".ch"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("design")
    ap.add_argument("--imagenes", default=str(HERE.parent / "teoria/imagenes"))
    ap.add_argument("--rapido", action="store_true", help="no renderiza una portada/divisor por variante")
    a = ap.parse_args()
    dd = HERE / "designs" / a.design
    res = []

    def chk(name, ok, detail=""):
        res.append((name, bool(ok), detail))

    try:
        m = json.loads((dd / "manifest.json").read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        sys.exit(f"✘ manifest.json ilegible: {e}")
    need = ["id", "name", "version", "formats", "palette", "fonts", "page", "templates", "blocks", "image_treatments"]
    chk("1 manifiesto completo", all(k in m for k in need) and m["id"] == a.design, f"faltan: {[k for k in need if k not in m]}")
    miss = [f["file"] for f in m.get("fonts", []) if not (dd / f["file"]).exists()]
    nolic = [f["family"] for f in m.get("fonts", []) if not f.get("licencia")]
    chk("2 fuentes existen y declaran licencia", not miss and not nolic, f"faltan archivos {miss}; sin licencia {nolic}")
    pals = json.loads((dd / "palettes.json").read_text(encoding="utf-8"))
    bad = []
    for k, p in pals.items():
        if k == "_marca":
            continue
        roles = {**m["palette"]["roles"], **p}
        if any(r not in roles for r in ROLES):
            bad.append(f"{k}: faltan roles")
        bad += [f"{k}: {x['bloque']} {x['causa']}" for x in paleta.check(roles, m) if "contraste" in x["causa"] or "grises" in x["causa"]]
    chk("3 paletas: 7 roles, contraste ≥ 4,5, claridad en grises", not bad, "; ".join(bad[:4]))
    reg = variants.Registry(dd)
    cv = [v["id"] for v in reg.data["variantes"] if v["tipo"] == "portada"]
    dv = [v["id"] for v in reg.data["variantes"] if v["tipo"] == "divisor"]
    have = lambda k, ids: [i for i in ids if (dd / "templates" / f"{k}.{i}.html").exists()]
    chk("4 ≥ 2 portadas y ≥ 2 divisores con plantilla", len(have("cover", cv)) >= 2 and len(have("divider", dv)) >= 2, f"portadas {have('cover', cv)}, divisores {have('divider', dv)}")
    css = (dd / "bundle.css").read_text(encoding="utf-8") + (dd / "extras.css").read_text(encoding="utf-8")
    chk("5 clases CSS del contrato", all(c in css for c in CSS_NEEDS), f"faltan {[c for c in CSS_NEEDS if c not in css]}")
    n = len(m["templates"]["cover"].get("symbols", []))
    chk("6 símbolos de portada entre 3 y 5", 3 <= n <= 5, f"hay {n}")
    sym = assets.Symbols(dd)
    warn = []
    roles = {**m["palette"]["roles"]}
    pc = pages.PageCtx(dd, m, roles, sym, Path(a.imagenes), HERE / ".cache", warn)
    meta = {"title": "M", "date": "Mes 2026", "version": "v1", "header_left": ["Uno", "Dos"]}
    cov = {"vertical": "MUESTRA", "title": "Título", "text": "Texto."}
    sobra = []
    for i in have("cover", cv):
        h = pages.cover(pc, meta, cov, i)
        if "{{" in h:
            sobra.append(i)
    for i in have("divider", dv):
        h = pages.divider(pc, i, "01", 2, {"title": "Sección", "desc": "Descripción."})
        if "{{" in h:
            sobra.append(i)
    chk("7 plantillas se dibujan sin campos sueltos", not sobra, f"con {{{{ sobrante: {sobra}")
    imgs = Path(a.imagenes)

    def run_doc(largo, cvv="auto", dvv="auto"):
        d = muestras.doc_muestra(a.design, largo, cvv, dvv, imgs.exists())
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "d.json"
            p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
            return render.run(p, Path(t) / "x.pdf", imgs)

    rc = run_doc(False)
    degr = [x for x in rc["avisos"] if "paleta" not in x["bloque"] and "variante" not in x["bloque"] and "metadatos" not in x["bloque"] and "sin fila" not in x["causa"] and "alt" not in x["causa"]]
    chk("8 muestra CORTA: sin degradaciones y auditoría limpia", rc["estado"] != "rechazado" and not degr and not rc["auditoria"], f"{len(degr)} avisos, auditoría {({k: len(v) for k, v in rc['auditoria'].items()})} {[x['causa'][:50] for x in degr[:2]]}")
    rl = run_doc(True)
    chk("9 muestra LARGA: sin desbordes", rl["estado"] != "rechazado" and not rl["auditoria"], f"auditoría {({k: len(v) for k, v in rl['auditoria'].items()})} " + str([x for x in rl['auditoria'].get('794-print', [])[:2]]))
    chk("10 sin redundancia en las muestras", not any(x.get("tipo") == "redundancia" for r in (rc, rl) for v in r["auditoria"].values() for x in v))
    if not a.rapido:
        bad = []
        for kind, ids in (("cover", have("cover", cv)), ("divider", have("divider", dv))):
            for i in ids:
                r = run_doc(False, i if kind == "cover" else "auto", i if kind == "divider" else "auto")
                if r["auditoria"] or r["estado"] == "rechazado":
                    bad.append(i)
        chk("11 cada portada y cada divisor, renderizados, sin problemas", not bad, f"con problemas: {bad}")
    ok = all(r[1] for r in res)
    print(f"\nLista de revisión · diseño «{a.design}» v{m['version']}\n")
    for name, good, d in res:
        print(("✔" if good else "✘"), name, ("" if good else f"\n    → {d}"))
    print("\n" + ("TODO ✔: el diseño está listo." if ok else "Faltan cosas (✘)."))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")      # Windows: la consola cp1252 no acepta ✔ → ·
    main()
