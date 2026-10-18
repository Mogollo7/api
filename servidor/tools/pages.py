#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Construye la versión ESTÁTICA de la web para GitHub Pages (sin API): catálogo, formatos, ejemplos, estadísticas y documentación.
"""python servidor/tools/pages.py [--salida _site] [--base /guia] [--origen http://127.0.0.1:8765]

Copia servidor/web/ a <salida>/web/, escribe index.html y 404.html (para que /catalogo, /formatos… funcionen al recargar) con las rutas bajo --base y sin llamadas a /v1,
y la lista de diseños publicados (servidor/designs/*/manifest.json). La parte que necesita la API (Taller, renderizar, descargar) avisa que corre en local.
Pages publica con .github/workflows/pages.yml."""
import json
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
WEB = RAIZ / "servidor" / "web"
RUTAS = "como|agente|catalogo|taller|formatos|estilos|estadisticas"


def disenos():
    out = []
    for d in sorted((RAIZ / "servidor" / "designs").iterdir()):
        mf = d / "manifest.json"
        if not mf.exists():
            continue
        m = json.loads(mf.read_text(encoding="utf-8"))
        if m.get("estado", "publicado") == "publicado":
            out.append({"id": m["id"], "name": m["name"], "version": m["version"], "formats": m["formats"], "estilo": m.get("estilo", "brutalismo"), "estado": "publicado"})
    return out


def main():
    a = sys.argv[1:]
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d      # noqa: E731
    sal, base, origen = Path(opt("--salida", "_site")), "/" + opt("--base", "/guia").strip("/"), opt("--origen", "http://127.0.0.1:8765")
    if sal.exists():
        shutil.rmtree(sal)
    shutil.copytree(WEB, sal / "web", ignore=shutil.ignore_patterns("app.legacy.html", "_*"))
    (sal / "web" / "static").mkdir(exist_ok=True)
    (sal / "web" / "static" / "designs.json").write_text(json.dumps(disenos(), ensure_ascii=False), encoding="utf-8")
    h = (WEB / "app.html").read_text(encoding="utf-8")
    h = h.replace('<html lang="es"', f'<html lang="es" data-base="{base}" data-static="1" data-origin="{origen}"', 1)
    for q in ('"', "'", "`"):
        h = h.replace(f"{q}/web/", f"{q}{base}/web/")                              # rutas de archivos estáticos (HTML y plantillas de JS)
    h = re.sub(r'href="/(' + RUTAS + r')', lambda m: f'href="{base}/{m.group(1)}', h)  # enlaces internos con data-link
    h = h.replace('href="/"', f'href="{base}/"')
    (sal / "index.html").write_text(h, encoding="utf-8")
    (sal / "404.html").write_text(h, encoding="utf-8")
    (sal / ".nojekyll").write_text("", encoding="utf-8")
    media = RAIZ / "docs" / "media"
    if media.exists():
        shutil.copytree(media, sal / "media")
    print(f"sitio estático en {sal} ({sum(1 for _ in sal.rglob('*') if _.is_file())} archivos), base {base}")


if __name__ == "__main__":
    main()
