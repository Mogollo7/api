#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor. Búsqueda de imágenes en Wikimedia Commons con su licencia.
"""Busca imágenes en Wikimedia Commons por la API oficial y guarda cada una con autor, licencia y enlace (obligatorios para reutilizarlas).

    python servidor/tools/commons.py "Rhinella marina" -n 5 --destino teoria/imagenes/nuevas

Escribe los JPG y añade las filas a `<destino>/../creditos.csv` (archivo,especie_o_tema,que_muestra,url_commons,autor,licencia), el formato que lee el servidor.
Solo acepta licencias libres (CC0, dominio público, CC BY, CC BY-SA). NOTA: en la nube de Claude el proxy bloquea commons.wikimedia.org; ejecútalo en tu PC.
La función `parse()` está probada sin red; la llamada real a la API NO se ha podido probar desde la nube.
"""
import argparse
import csv
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://commons.wikimedia.org/w/api.php"
OK_LIC = re.compile(r"^(cc0|public domain|pd|cc[- ]by(-sa)?[- ]?[0-9.]*)", re.I)
UA = {"User-Agent": "guia-ia-servidor/0.2 (uso educativo)"}


def parse(resp: dict, ancho: int = 1400):
    """Respuesta de la API (generator=search + prop=imageinfo) -> lista de dicts utilizables. Sin red."""
    out = []
    for p in (resp.get("query", {}).get("pages", {}) or {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        meta = ii.get("extmetadata", {})
        lic = meta.get("LicenseShortName", {}).get("value", "")
        if not ii.get("thumburl") or not OK_LIC.match(lic.strip()):
            continue
        autor = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "")).strip()
        out.append({"titulo": p.get("title", "").replace("File:", ""), "url_commons": ii.get("descriptionurl", ""), "thumb": ii["thumburl"],
                    "autor": autor, "licencia": lic.strip(), "descripcion": re.sub(r"<[^>]+>", "", meta.get("ImageDescription", {}).get("value", ""))[:160]})
    return out


def buscar(q: str, n: int = 5, ancho: int = 1400):
    params = {"action": "query", "format": "json", "generator": "search", "gsrsearch": f"{q} filetype:bitmap", "gsrnamespace": 6, "gsrlimit": n * 3,
              "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": ancho}
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return parse(json.load(r), ancho)[:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("consulta")
    ap.add_argument("-n", type=int, default=5)
    ap.add_argument("--destino", default="teoria/imagenes/nuevas")
    a = ap.parse_args()
    dest = Path(a.destino)
    dest.mkdir(parents=True, exist_ok=True)
    csvp = dest.parent / "creditos.csv"
    nuevo = not csvp.exists()
    with csvp.open("a", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        if nuevo:
            w.writerow(["archivo", "especie_o_tema", "que_muestra", "url_commons", "autor", "licencia"])
        for it in buscar(a.consulta, a.n):
            name = re.sub(r"[^\w.-]+", "_", it["titulo"])[:80]
            if not name.lower().endswith((".jpg", ".jpeg", ".png")):
                name += ".jpg"
            if not (dest / name).exists():       # caché: no se vuelve a descargar
                req = urllib.request.Request(it["thumb"], headers=UA)
                (dest / name).write_bytes(urllib.request.urlopen(req, timeout=60).read())
            w.writerow([f"{dest.name}/{name}", a.consulta, it["descripcion"], it["url_commons"], it["autor"], it["licencia"]])
            print("ok", name, it["licencia"])


if __name__ == "__main__":
    main()
