#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Capturas para MIRAR lo que se creó: página de un PDF, una web (localhost) o un HTML. Devuelve un PNG pequeño que el agente puede leer.
"""python servidor/captura.py <archivo.pdf|archivo.html|http://127.0.0.1:…> [-o salida.png] [--pagina 1] [--ancho 1280] [--alto 800] [--completa]
Un PDF se dibuja con pymupdf (rápido); una web o un HTML con Chromium (el mismo del motor)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def pdf(ruta, pagina=1, dpi=70):
    import pymupdf
    d = pymupdf.open(str(ruta))
    n = max(1, min(int(pagina), len(d)))
    return d[n - 1].get_pixmap(dpi=dpi).tobytes("png"), len(d)


def web(url, ancho=1280, alto=800, completa=False, espera=1.5):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": int(ancho), "height": int(alto)})
        pg.goto(url, wait_until="load")
        pg.wait_for_timeout(int(espera * 1000))
        png = pg.screenshot(full_page=bool(completa))
        b.close()
    return png


def capturar(origen, salida, pagina=1, ancho=1280, alto=800, completa=False):
    o = str(origen)
    if o.lower().endswith(".pdf"):
        png, n = pdf(o, pagina)
        info = {"paginas": n, "pagina": pagina}
    else:
        url = o if o.startswith(("http://127.0.0.1", "http://localhost")) else Path(o).resolve().as_uri()
        png, info = web(url, ancho, alto, completa), {}
    Path(salida).parent.mkdir(parents=True, exist_ok=True)
    Path(salida).write_bytes(png)
    return {"png": str(salida), "bytes": len(png), **info}


if __name__ == "__main__":
    a = [x for x in sys.argv[1:]]
    if not a:
        print(__doc__)
    else:
        opt = lambda k, d: a[a.index(k) + 1] if k in a else d      # noqa: E731
        print(capturar(a[0], opt("-o", "salida/captura.png"), opt("--pagina", 1), opt("--ancho", 1280), opt("--alto", 800), "--completa" in a))
