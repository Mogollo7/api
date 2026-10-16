#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Crea un diseño NUEVO copiando uno existente (copiar es lo normal): la carpeta queda lista para editar y pasar la lista de revisión.

    python servidor/crear_diseno.py editorial --base anura --nombre "Editorial"
    # 1) edita designs/editorial/{manifest.json, palettes.json, extras.css, templates/*.html, variantes.json}
    # 2) python servidor/validar_diseno.py editorial          ← lista de revisión; cuando todo sale ✔, el diseño está listo
Guía completa en designs/LEEME.md.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--base", default="anura")
    ap.add_argument("--nombre")
    a = ap.parse_args()
    src, dst = HERE / "designs" / a.base, HERE / "designs" / a.id
    if dst.exists():
        sys.exit(f"ya existe {dst}")
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".cache", "__pycache__"))
    m = json.loads((dst / "manifest.json").read_text())
    m.update({"id": a.id, "name": a.nombre or a.id, "version": "0.1.0", "base": a.base})
    m["_marca"] = f"[CLAUDE-CONSTRUCTOR] Diseño '{a.id}' creado desde '{a.base}'. Edita y valida con servidor/validar_diseno.py."
    (dst / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=2))
    v = json.loads((dst / "variantes.json").read_text())
    for x in v["variantes"]:
        x["estado"] = "propuesta"
    (dst / "variantes.json").write_text(json.dumps(v, ensure_ascii=False, indent=1))
    (dst / "LEEME_DISENO.md").write_text(f"# Diseño {a.id} (desde {a.base})\n\nPasos: 1) paleta en palettes.json y roles en manifest.json · 2) fuentes en fonts/ (con licencia en el manifiesto) · 3) plantillas en templates/ "
                                         f"(portada y divisor) y sus estilos en extras.css · 4) variantes.json (una fila por plantilla) · 5) `python servidor/validar_diseno.py {a.id}` hasta que todo sea ✔ · "
                                         f"6) `python servidor/galeria.py --design {a.id}` para aprobar variantes.\nContrato de clases y campos: designs/LEEME.md.\n", encoding="utf-8")
    print(f"creado {dst}")


if __name__ == "__main__":
    main()
