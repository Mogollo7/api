#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Registro de correcciones (JSONL): aprender sin entrenar y, más adelante, dataset para LoRA.
"""Cada corrección aceptada se guarda en servidor/data/correcciones.jsonl, una línea por registro:

    {"id","fecha","origen":"usuario|modelo|claude|motor","design","formato","job","seccion","antes","despues","motivo","regla"}

Usos, de menos a más costosos: 1) buscar parecidas y usarlas como ejemplo al decidir (`buscar`);
2) las que se repiten pasan a «errores comunes» del skill o al validador (`frecuentes`); 3) `dataset()` exporta pares bueno/malo para entrenar (Soup, preferencias).
"""
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

import biblioteca

ARCHIVO = Path(__file__).resolve().parent / "data" / "correcciones.jsonl"
ORIGENES = ("usuario", "modelo", "claude", "motor")


def _lee():
    if not ARCHIVO.exists():
        return []
    res = []
    for ln in ARCHIVO.read_text(encoding="utf-8").splitlines():
        try:
            res.append(json.loads(ln))
        except ValueError:
            continue
    return res


def guardar(r):
    """Valida y agrega un registro. `motivo` es obligatorio (sin motivo no se puede aprender nada)."""
    motivo = str(r.get("motivo", "")).strip()
    if not motivo:
        raise ValueError("falta 'motivo': di qué estaba mal y por qué")
    origen = r.get("origen", "modelo")
    if origen not in ORIGENES:
        raise ValueError(f"origen debe ser {'|'.join(ORIGENES)}")
    rec = {"id": f"c{int(time.time() * 1000):x}", "fecha": time.strftime("%Y-%m-%d"), "origen": origen, "design": r.get("design"), "formato": r.get("formato"), "job": r.get("job"),
           "seccion": str(r.get("seccion", ""))[:80], "antes": r.get("antes"), "despues": r.get("despues"), "motivo": motivo[:400], "regla": str(r.get("regla", ""))[:200]}
    if len(json.dumps(rec, ensure_ascii=False)) > 20000:
        raise ValueError("registro demasiado grande (máx 20 KB): guarda solo el bloque corregido")
    ARCHIVO.parent.mkdir(exist_ok=True)
    with ARCHIVO.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return {"id": rec["id"], "guardada": True, "total": len(_lee())}


def buscar(q, n=3):
    """Correcciones más parecidas a `q` (motivo, sección y regla)."""
    regs = _lee()
    qt = set(biblioteca.tokens(q))
    res = []
    for r in regs:
        t = Counter(biblioteca.tokens(f"{r.get('motivo', '')} {r.get('seccion', '')} {r.get('regla', '')}"))
        s = sum(1 for x in qt if x in t) / (len(qt) or 1)
        if s > 0:
            res.append((s, r))
    res.sort(key=lambda x: (-x[0], x[1]["id"]), reverse=False)
    return [{**{k: r[k] for k in ("id", "seccion", "motivo", "antes", "despues", "origen")}, "puntaje": round(s, 2)} for s, r in res[:max(1, min(int(n), 10))]]


def frecuentes(minimo=3):
    """Reglas que se repiten: candidatas a «errores comunes» del skill o a una validación del motor."""
    c = Counter(r.get("regla") or re.sub(r"\W+", " ", r["motivo"].lower())[:60] for r in _lee())
    return [{"regla": k, "veces": v} for k, v in c.most_common() if v >= minimo]


def dataset(destino):
    """Exporta pares bueno/malo (JSONL con prompt/rejected/chosen) para entrenar con preferencias."""
    n = 0
    with Path(destino).open("w", encoding="utf-8") as f:
        for r in _lee():
            if r.get("antes") is not None and r.get("despues") is not None:
                f.write(json.dumps({"prompt": f"Corrige: {r['motivo']} [{r['seccion']}]", "rejected": r["antes"], "chosen": r["despues"]}, ensure_ascii=False) + "\n")
                n += 1
    return n


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    a = sys.argv[1:]
    if a[:1] == ["buscar"]:
        print(json.dumps(buscar(a[1]), ensure_ascii=False, indent=1))
    elif a[:1] == ["frecuentes"]:
        print(json.dumps(frecuentes(int(a[1]) if a[1:] else 3), ensure_ascii=False, indent=1))
    elif a[:1] == ["dataset"]:
        print(dataset(a[1]), "pares escritos")
    else:
        print(__doc__)
