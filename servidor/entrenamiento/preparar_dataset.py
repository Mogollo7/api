#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Prepara el dataset JSONL para un LoRA (Fase 4): solo ejemplos YA validados. No entrena nada.
"""python servidor/entrenamiento/preparar_dataset.py [--salida servidor/entrenamiento/dataset] [--minimo 100]

Fuentes (de más a menos fiable):
  1) corridas de salida/evaluacion/*/resultados.json con calidad 1.0 y herramienta correcta → conversaciones de tool-calling (formato `messages` de OpenAI);
  2) servidor/data/correcciones.jsonl → pares preferencia {prompt, chosen, rejected}.
Escribe `tool_calling.jsonl` y `preferencias.jsonl`, y avisa si hay menos del mínimo recomendado (100–300 para la primera prueba)."""
import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "servidor"))
import correcciones  # noqa: E402
import director  # noqa: E402


def tool_calling():
    out = []
    for f in sorted((RAIZ / "salida" / "evaluacion").glob("*/resultados.json")):
        for c in json.loads(f.read_text(encoding="utf-8"))["casos"]:
            m = c["metricas"]
            if not (m["herramienta"] and m["calidad"] >= 1.0 and not c["escalado"]):
                continue
            msgs = [{"role": "system", "content": director.SISTEMA}, {"role": "user", "content": c["tarea"] + f" (formato: {c['formato']})"}]
            for t in c["traza"]:
                msgs.append({"role": "assistant", "content": None, "tool_calls": [{"type": "function", "function": {"name": t["tool"], "arguments": json.dumps(t["args"], ensure_ascii=False)}}]})
                msgs.append({"role": "tool", "name": t["tool"], "content": json.dumps(t["resultado"], ensure_ascii=False)[:1500]})
            out.append({"messages": msgs})
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", default=str(RAIZ / "servidor" / "entrenamiento" / "dataset"))
    ap.add_argument("--minimo", type=int, default=100)
    a = ap.parse_args()
    d = Path(a.salida)
    d.mkdir(parents=True, exist_ok=True)
    tc = tool_calling()
    (d / "tool_calling.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in tc) + ("\n" if tc else ""), encoding="utf-8")
    n_pref = correcciones.dataset(d / "preferencias.jsonl")
    print(f"tool_calling.jsonl: {len(tc)} ejemplos · preferencias.jsonl: {n_pref} pares → {d}")
    if len(tc) + n_pref < a.minimo:
        print(f"⚠ hay {len(tc) + n_pref} de {a.minimo} recomendados: sigue acumulando evaluaciones y correcciones antes de entrenar.")


if __name__ == "__main__":
    main()
