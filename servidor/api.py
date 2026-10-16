#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""API mínima (solo biblioteca estándar) con las rutas de la fase 1 del Prompt Maestro. Pensada para probar en tu PC:

    python servidor/api.py --puerto 8765 --imagenes teoria/imagenes
    curl localhost:8765/v1/designs
    curl -X POST localhost:8765/v1/render --data @contenido/guia.json     # devuelve informe + ruta del PDF
    curl -O localhost:8765/v1/files/guia.pdf

Síncrona y sin autenticación: es para pruebas locales, no para exponerla a internet (faltan claves de API, cola y límites).
"""
import argparse
import json
import re
import tempfile
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import render

OUT = Path(tempfile.gettempdir()) / "anura-api"
OUT.mkdir(exist_ok=True)
IMAGES = "imagenes"


class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/v1/designs":
            ds = []
            for d in (render.HERE / "designs").iterdir():
                if (d / "manifest.json").exists():
                    m = json.loads((d / "manifest.json").read_text())
                    ds.append({"id": m["id"], "name": m["name"], "version": m["version"], "formats": m["formats"]})
            return self._send(200, ds)
        mm = re.fullmatch(r"/v1/designs/([\w-]+)", self.path)
        if mm:
            try:
                _, m = render.load_design(mm.group(1))
            except Exception:
                return self._send(404, {"error": "diseño no encontrado"})
            return self._send(200, {"id": m["id"], "paleta": m["palette"]["roles"], "bloques": m["blocks"], "divisores": list(m["templates"]["divider"]), "reglas": m["reglas_medibles"]})
        mm = re.fullmatch(r"/v1/files/([\w.-]+)", self.path)
        if mm and (OUT / mm.group(1)).exists():
            return self._send(200, (OUT / mm.group(1)).read_bytes(), "application/pdf")
        self._send(404, {"error": "ruta no encontrada"})

    def do_POST(self):
        if self.path != "/v1/render":
            return self._send(404, {"error": "ruta no encontrada"})
        n = int(self.headers.get("Content-Length", 0))
        try:
            doc = json.loads(self.rfile.read(n))
        except Exception:
            return self._send(400, {"error": "JSON inválido"})
        job = uuid.uuid4().hex[:10]
        src = OUT / f"{job}.json"
        src.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        rep = render.run(src, OUT / f"{job}.pdf", IMAGES)
        rep["job"] = job
        rep["pdf"] = f"/v1/files/{job}.pdf" if rep["estado"] != "rechazado" else None
        self._send(200 if rep["estado"] != "rechazado" else 422, rep)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--puerto", type=int, default=8765)
    ap.add_argument("--imagenes", default="imagenes")
    a = ap.parse_args()
    IMAGES = a.imagenes
    print(f"API en http://localhost:{a.puerto}")
    HTTPServer(("127.0.0.1", a.puerto), H).serve_forever()
