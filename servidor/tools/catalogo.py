#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Genera el catálogo de plantillas del frontend: portada y páginas interiores (PNG) de cada documento de ejemplo.
"""python servidor/tools/catalogo.py   (necesita pdftoppm de poppler en el PATH)

Lee contenido/*.json y salida/<id>.pdf; escribe servidor/web/cat/<id>/{doc.pdf,p01.png…} y servidor/web/cat/catalog.json.
"""
import datetime
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAT = ROOT / "servidor" / "web" / "cat"
INTERIOR = 8      # páginas que se muestran "por dentro"
# ponytail: la clasificación es una tabla a mano; si el catálogo crece, súbela al JSON de contenido (meta.catalogo)
KIND = {"guia": "Guía larga", "documento": "Documento académico", "cine_ejemplo": "Análisis de datos", "manual_procedimiento": "Manual de procedimiento",
        "pitb_enfermeria": "Documento temático", "informe_ventas": "Informe de negocio", "ficha_proyecto": "Ficha de proyecto", "prompt_master_uso": "Guía de uso"}


def pages(pdf):
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, encoding="utf-8", errors="replace", check=True).stdout
    return int(next(l for l in out.splitlines() if l.startswith("Pages:")).split()[1])


def main():
    items = []
    for f in sorted((ROOT / "contenido").glob("*.json")):
        pdf = ROOT / "salida" / f"{f.stem}.pdf"
        if not pdf.exists():
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        meta, cover = d.get("meta", {}), (d.get("document", {}).get("cover") or {})
        out = CAT / f.stem
        out.mkdir(parents=True, exist_ok=True)
        shutil.copy(pdf, out / "doc.pdf")
        n = pages(pdf)
        last = min(n, INTERIOR)
        subprocess.run(["pdftoppm", "-png", "-r", "60", "-f", "1", "-l", str(last), str(pdf), str(out / "p")], check=True)
        for p in out.glob("p-*.png"):                       # pdftoppm numera con ceros según el total de páginas
            p.replace(out / f"p{int(p.stem.split('-')[1]):02d}.png")
        man = json.loads((ROOT / "servidor" / "designs" / d.get("design", "anura") / "manifest.json").read_text(encoding="utf-8"))
        items.append({"id": f.stem, "title": meta.get("title", f.stem), "text": cover.get("text", ""), "design": d.get("design", "anura"),
                      "style": man.get("estilo", "brutalismo"),          # familia de estilo; un diseño nuevo declara la suya en su manifiesto
                      "palette": d.get("palette", "default"), "kind": KIND.get(f.stem, "Documento"), "pages": n, "shown": last, "updated": datetime.date.fromtimestamp(f.stat().st_mtime).isoformat(),
                      "blocks": sorted({b.get("type") for p in d.get("document", {}).get("parts", []) for s in p.get("sections", []) for b in s.get("blocks", []) if b.get("type")})})
    (CAT / "catalog.json").write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(items)} plantillas en {CAT}")


if __name__ == "__main__":
    main()
