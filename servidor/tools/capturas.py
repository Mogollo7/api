#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Capturas de la web servida por la API, dentro de una ventana con tres puntos de colores (estilo macOS), para el README y la documentación.
"""python servidor/tools/capturas.py [--url http://127.0.0.1:8765] [--salida docs/img]
Escribe docs/img/web-<ruta>.png (la ventana enmarcada) y docs/img/crudo/<ruta>.png (la captura sola). Necesita la API corriendo."""
import argparse
import base64
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

RUTAS = {"inicio": "/", "como": "/como", "agente": "/agente", "catalogo": "/catalogo", "taller": "/taller", "formatos": "/formatos", "estilos": "/estilos", "estadisticas": "/estadisticas"}
MARCO = """<!doctype html><meta charset="utf-8"><style>
html,body{margin:0}body{width:1760px;padding:72px 80px 88px;background:linear-gradient(135deg,#150F26 0%,#5B21B6 55%,#C2410C 120%);font-family:Archivo,Segoe UI,Arial,sans-serif}
.v{border-radius:18px;overflow:hidden;background:#fff;box-shadow:0 40px 90px rgba(0,0,0,.45),0 0 0 1px rgba(255,255,255,.12)}
.b{height:52px;background:#ece9f2;display:flex;align-items:center;gap:10px;padding:0 20px;border-bottom:1px solid #d7d2e0}
.b i{width:16px;height:16px;border-radius:50%;display:block}.r{background:#ff5f57}.a{background:#febc2e}.g{background:#28c840}
.u{margin:0 auto;transform:translateX(-36px);min-width:520px;text-align:center;font:500 15px/30px Segoe UI,Arial,sans-serif;color:#5b5668;background:#fff;border-radius:8px;padding:0 24px}
img{display:block;width:1600px;height:auto}</style>
<div class="v"><div class="b"><i class="r"></i><i class="a"></i><i class="g"></i><span class="u">%URL%</span></div><img src="data:image/png;base64,%IMG%"></div>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8765")
    ap.add_argument("--salida", default="docs/img")
    a = ap.parse_args()
    out = Path(a.salida)
    (out / "crudo").mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1600, "height": 900}, device_scale_factor=1)
        fr = b.new_page(viewport={"width": 1760, "height": 1100}, device_scale_factor=2)
        for nombre, ruta in RUTAS.items():
            pg.goto(a.url + ruta, wait_until="networkidle")
            pg.wait_for_timeout(1400)
            if nombre == "estadisticas":
                pg.evaluate("document.querySelector('.stchart')?.scrollIntoView({block:'start'})")
                pg.wait_for_timeout(500)
            crudo = out / "crudo" / f"{nombre}.png"
            pg.screenshot(path=str(crudo))
            fr.set_content(MARCO.replace("%URL%", "mystyle.local" + ruta).replace("%IMG%", base64.b64encode(crudo.read_bytes()).decode()))
            fr.wait_for_timeout(200)
            fr.locator("body").screenshot(path=str(out / f"web-{nombre}.png"))
            print("·", nombre)
        b.close()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
