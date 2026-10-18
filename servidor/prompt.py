#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Genera el Prompt Maestro y la skill de un diseño.

    python servidor/prompt.py anura                                  # Prompt Maestro largo por la salida estándar
    python servidor/prompt.py anura --corto --modo A --variantes cover=CV-2,divider=DV-E --paleta cine
    python servidor/prompt.py anura --skill salida/skills            # carpeta de skill: SKILL.md + schema + ejemplo + prompts
    python servidor/prompt.py --schema contrato.schema.json          # solo el JSON Schema
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from engine import muestras, prompt, spec  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("design", nargs="?", default="anura")
    ap.add_argument("--format", default="pdf-a4")
    ap.add_argument("--paleta", default="default")
    ap.add_argument("--variantes", default="")
    ap.add_argument("--modo", default="B", choices=["A", "B"])
    ap.add_argument("--corto", action="store_true")
    ap.add_argument("--skill")
    ap.add_argument("--schema")
    a = ap.parse_args()
    if a.schema:
        Path(a.schema).write_text(json.dumps(spec.json_schema(), ensure_ascii=False, indent=1), encoding="utf-8")
        print("escrito", a.schema)
        return
    var = dict(x.split("=", 1) for x in a.variantes.split(",") if "=" in x)
    if a.skill:
        out = Path(a.skill) / f"documentos-{a.design}"
        out.mkdir(parents=True, exist_ok=True)
        (out / "SKILL.md").write_text(prompt.skill_md(a.design), encoding="utf-8")
        (out / "contrato.schema.json").write_text(json.dumps(spec.json_schema(), ensure_ascii=False, indent=1), encoding="utf-8")
        (out / "ejemplo.json").write_text(json.dumps(muestras.doc_muestra(a.design, False, "auto", "auto", False), ensure_ascii=False, indent=1), encoding="utf-8")
        (out / "PROMPT_MAESTRO.md").write_text(prompt.prompt_maestro(a.design, a.format, a.paleta, var, a.modo, False), encoding="utf-8")
        (out / "PROMPT_CORTO.md").write_text(prompt.prompt_maestro(a.design, a.format, a.paleta, var, a.modo, True), encoding="utf-8")
        print("skill en", out)
        return
    sys.stdout.write(prompt.prompt_maestro(a.design, a.format, a.paleta, var, a.modo, a.corto))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")      # Windows: la consola cp1252 no acepta ✔ → ·
    main()
