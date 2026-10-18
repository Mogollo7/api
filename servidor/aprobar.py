#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Aplica tus aprobaciones al registro de variantes.

    python servidor/aprobar.py aprobaciones.json          # el archivo que exporta la galería (botón «Exportar»)
    python servidor/aprobar.py --aprobar DV-E CV-2        # o ids sueltos
    python servidor/aprobar.py --rechazar TB-2
    python servidor/aprobar.py --listar
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from engine.variants import Registry  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archivo", nargs="?")
    ap.add_argument("--design", default="anura")
    ap.add_argument("--aprobar", nargs="*", default=[])
    ap.add_argument("--rechazar", nargs="*", default=[])
    ap.add_argument("--listar", action="store_true")
    a = ap.parse_args()
    reg = Registry(HERE / "designs" / a.design)
    if a.archivo:
        for vid, est in json.loads(Path(a.archivo).read_text(encoding="utf-8")).items():
            if vid in reg.by_id and est in ("propuesta", "aprobada", "rechazada"):
                reg.set_state(vid, est)
    for v in a.aprobar:
        reg.set_state(v, "aprobada")
    for v in a.rechazar:
        reg.set_state(v, "rechazada")
    if a.archivo or a.aprobar or a.rechazar:
        reg.save()
    if a.listar or not (a.archivo or a.aprobar or a.rechazar):
        for v in reg.data["variantes"]:
            print(f'{v["id"]:<10}{v["estado"]:<10}{v["tipo"]:<11}{v["nombre"]}')
    c = {}
    for v in reg.data["variantes"]:
        c[v["estado"]] = c.get(v["estado"], 0) + 1
    print(c)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")      # Windows: la consola cp1252 no acepta ✔ → ·
    main()
