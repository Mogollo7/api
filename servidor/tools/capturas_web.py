#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Captura la web servida (API en :8765) en las vistas clave y las enmarca (tres puntos de colores) en docs/media/. Para el README y los videos.
"""python servidor/tools/capturas_web.py [--url http://127.0.0.1:8765] [--salida docs/media] [--ancho 1440 --alto 900] [--fondo "#0b1020"]"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import marco  # noqa: E402

VISTAS = [  # (archivo, ruta, javascript previo, espera ms)
    ("home", "/", "", 1200),
    ("ejemplos-pptx", "/", "document.querySelector('#show-tabs button[data-k=pptx]').click();document.getElementById('ejemplos').scrollIntoView()", 900),
    ("ejemplos-web", "/", "document.querySelector('#show-tabs button[data-k=web]').click();document.getElementById('ejemplos').scrollIntoView()", 2500),
    ("estadisticas-home", "/", "document.getElementById('home-stats').scrollIntoView()", 900),
    ("video-creativo", "/", "document.getElementById('video-creativo').scrollIntoView()", 1200),
    ("catalogo", "/catalogo", "", 1500),
    ("formatos", "/formatos", "", 1200),
    ("estadisticas", "/estadisticas", "", 1500),
    ("agente", "/agente", "document.getElementById('t5').click()", 800),
    ("estilos", "/estilos", "", 1000),
]


def main():
    from playwright.sync_api import sync_playwright
    a = sys.argv[1:]
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d      # noqa: E731
    url, out = opt("--url", "http://127.0.0.1:8765"), Path(opt("--salida", "docs/media"))
    w, h = int(opt("--ancho", 1440)), int(opt("--alto", 900))
    tmp = out / "_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
        for nombre, ruta, js, espera in VISTAS:
            pg.goto(url + ruta, wait_until="load")
            pg.wait_for_timeout(600)
            if js:
                pg.evaluate(js)
            pg.wait_for_timeout(espera)
            pg.screenshot(path=str(tmp / f"{nombre}.png"))
            print(marco.enmarcar(tmp / f"{nombre}.png", out / f"{nombre}.png", url.replace("http://", "") + ruta, opt("--fondo", "#0b1020"), True))
        b.close()
    for f in tmp.glob("*.png"):
        f.unlink()
    tmp.rmdir()


if __name__ == "__main__":
    main()
