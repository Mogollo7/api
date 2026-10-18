#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Biblioteca de estilos, plantillas, componentes y animaciones: archivos JSON que cualquier agente (también uno local pequeño) consulta.
"""Biblioteca legible por el agente. Vive en servidor/biblioteca/<tipo>/<id>.json (+ servidor/biblioteca/skills/<tipo>-<id>.md).

    python servidor/biblioteca.py buscar "patrón de puntos" [--tipo plantilla] [-n 5]
    python servidor/biblioteca.py ver anura

Búsqueda por similitud (TF-IDF + sinónimos, sin dependencias). Versionado: guardar un estilo que ya existe exige `sobrescribir` y conserva la versión anterior.
"""
import json
import math
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

DIR = Path(__file__).resolve().parent / "biblioteca"
TIPOS = ("estilo", "plantilla", "componente", "animacion", "receta", "ingrediente", "recurso")
CARPETA = {"estilo": "estilos", "plantilla": "plantillas", "componente": "componentes", "animacion": "animaciones", "receta": "recetas", "ingrediente": "ingredientes", "recurso": "recursos"}
SIN = {"dots": "punto", "dot": "punto", "puntos": "punto", "punteado": "punto", "grid": "rejilla", "cuadricula": "rejilla", "malla": "rejilla", "patron": "punto",
       "slide": "diapositiva", "ppt": "pptx", "powerpoint": "pptx", "doc": "word", "cover": "portada", "kpi": "cifra", "cifras": "cifra", "metrica": "cifra",
       "chart": "grafico", "graficos": "grafico", "table": "tabla", "titulo": "titular", "header": "cabecera", "fade": "aparecer", "stagger": "escalonado"}


def norm(s):
    return unicodedata.normalize("NFD", str(s).lower()).encode("ascii", "ignore").decode()


PARAR = {"de", "la", "el", "con", "y", "un", "una", "para", "en", "los", "las", "del", "que", "se", "al", "por", "a", "o", "es"}


def tokens(s):
    out = []
    for w in re.findall(r"[a-z0-9]+", norm(s)):
        if w in PARAR:
            continue
        w = SIN.get(w, w)
        if len(w) > 3 and w.endswith("es"):
            w = w[:-2]
        elif len(w) > 3 and w.endswith("s"):
            w = w[:-1]
        out.append(SIN.get(w, w))
    return out


def todos(tipo=None):
    res = []
    for t in TIPOS:
        if tipo and t != tipo:
            continue
        for f in sorted((DIR / CARPETA[t]).glob("*.json")):
            try:
                res.append(json.loads(f.read_text(encoding="utf-8")))
            except ValueError:
                continue
    return res


def _texto(e):
    return " ".join([e.get("nombre", ""), e.get("nombre", ""), e.get("descripcion", ""), " ".join(e.get("tags", [])) * 2, e.get("uso", "")])


def buscar(q, tipo=None, n=5):
    """Entradas más parecidas a `q`. Devuelve [{id, tipo, nombre, descripcion, tags, version, puntaje}]."""
    docs = todos(tipo)
    if not docs:
        return []
    toks = [Counter(tokens(_texto(e))) for e in docs]
    df = Counter(t for c in toks for t in c)
    N = len(docs)
    idf = lambda t: math.log(1 + N / (1 + df.get(t, 0)))                          # noqa: E731
    qt = Counter(tokens(q))
    qn = math.sqrt(sum((v * idf(t)) ** 2 for t, v in qt.items())) or 1
    res = []
    for e, c in zip(docs, toks):
        dot = sum(qt[t] * idf(t) * c[t] * idf(t) for t in qt if t in c)
        dn = math.sqrt(sum((v * idf(t)) ** 2 for t, v in c.items())) or 1
        s = dot / (qn * dn)
        qs = set(re.findall(r"[a-z0-9_-]+", norm(q)))
        if norm(e["id"]) in qs or (len(e.get("nombre", "")) > 3 and norm(e["nombre"]) in norm(q)):
            s += .5
        if s > 0:
            res.append((s, e))
    res.sort(key=lambda x: -x[0])
    return [{"id": e["id"], "tipo": e["tipo"], "nombre": e.get("nombre", ""), "descripcion": e.get("descripcion", ""), "tags": e.get("tags", []),
             "version": e.get("version", "1"), "puntaje": round(s, 3)} for s, e in res[:max(1, min(int(n), 20))]]


def obtener(id_, tipo=None):
    for e in todos(tipo):
        if e["id"] == id_:
            sk = DIR / "skills" / f"{e['tipo']}-{e['id']}.md"
            return {**e, **({"skill": sk.read_text(encoding="utf-8")} if sk.exists() else {})}
    return None


def skill_md(e):
    """SKILL.md de una pantalla: qué es, parámetros, un ejemplo correcto y un error típico."""
    L = [f"# {e['nombre']} ({e['tipo']} · v{e.get('version', '1')})", "", e.get("descripcion", ""), ""]
    if e.get("uso"):
        L += [f"**Cuándo usarlo:** {e['uso']}", ""]
    if e.get("parametros"):
        L += ["**Parámetros:**"] + [f"- `{k}`: {v}" for k, v in e["parametros"].items()] + [""]
    if e.get("ejemplo") is not None:
        L += ["**Ejemplo correcto:**", "```json", json.dumps(e["ejemplo"], ensure_ascii=False, indent=1)[:900], "```", ""]
    if e.get("error_tipico"):
        L += [f"**Error típico:** {e['error_tipico']}", ""]
    L += [f"Origen: {e.get('origen', '—')} · Licencia: {e.get('licencia', '—')} · Etiquetas: {', '.join(e.get('tags', []))}"]
    return "\n".join(L)[:2400]


def guardar(e, sobrescribir=False):
    """Guarda una entrada nueva. Si existe: sin `sobrescribir` se rechaza; con él se archiva la versión anterior y sube la versión."""
    t, i = e.get("tipo"), e.get("id", "")
    if t not in TIPOS or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,40}", i):
        raise ValueError("tipo debe ser estilo|plantilla|componente|animacion e id en minúsculas (a-z, 0-9, - _)")
    for k in ("nombre", "descripcion"):
        if not str(e.get(k, "")).strip():
            raise ValueError(f"falta '{k}'")
    d = DIR / CARPETA[t]
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{i}.json"
    e = {"version": "1", "tags": [], "origen": "agente", "licencia": "propia", **e}
    if f.exists():
        if not sobrescribir:
            raise ValueError(f"ya existe '{i}' (v{json.loads(f.read_text(encoding='utf-8')).get('version')}). Pregunta al usuario y repite con sobrescribir:true, o usa otro id")
        old = json.loads(f.read_text(encoding="utf-8"))
        (d / "_versiones").mkdir(exist_ok=True)
        (d / "_versiones" / f"{i}@{old.get('version', '1')}.json").write_text(json.dumps(old, ensure_ascii=False, indent=1), encoding="utf-8")
        try:
            e["version"] = str(int(old.get("version", "1")) + 1)
        except ValueError:
            e["version"] = old.get("version", "1") + ".1"
    f.write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
    (DIR / "skills").mkdir(exist_ok=True)
    (DIR / "skills" / f"{t}-{i}.md").write_text(skill_md(e), encoding="utf-8")
    return {"id": i, "tipo": t, "version": e["version"], "archivo": f"biblioteca/{CARPETA[t]}/{i}.json"}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    a = sys.argv[1:]
    if a[:1] == ["buscar"]:
        tipo = a[a.index("--tipo") + 1] if "--tipo" in a else None
        n = int(a[a.index("-n") + 1]) if "-n" in a else 5
        for r in buscar(a[1], tipo, n):
            print(f"{r['puntaje']:.2f}  {r['tipo']:<10} {r['id']:<22} {r['nombre']} — {r['descripcion'][:70]}")
    elif a[:1] == ["ver"]:
        print(json.dumps(obtener(a[1]), ensure_ascii=False, indent=1))
    else:
        print(__doc__)
