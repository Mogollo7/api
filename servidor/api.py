#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""API local (biblioteca estándar). Rutas de la fase 1 del Prompt Maestro:

    GET  /v1/designs                     lista de diseños
    GET  /v1/designs/{id}                variantes, paletas, bloques, reglas
    GET  /v1/designs/{id}/skill          SKILL.md del diseño (texto)
    GET  /v1/schema                      JSON Schema del contrato
    POST /v1/prompt                      {design, format, palette, variants:{cover,divider}, mode:"A|B", short:bool} -> Prompt Maestro (texto)
    POST /v1/render                      contrato JSON -> informe + URL del PDF (idempotente: el mismo contenido devuelve el mismo trabajo)
    GET  /v1/jobs/{id}                   informe de un trabajo
    GET  /v1/files/{archivo}             PDF generado

Seguridad mínima: variable API_KEY (cabecera `Authorization: Bearer <clave>`), cuerpo ≤ 5 MB, ≤ 300 hojas por documento, y un render a la vez.
Es síncrona y pensada para uso local o detrás de un proxy con TLS; para producción faltan cola, cuotas por clave y retención (ver ESTADO_MOTOR_PDF.md).
"""
import argparse
import hashlib
import json
import os
import re
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import render
from engine import prompt, spec

OUT = Path(os.environ.get("API_OUT", Path(tempfile.gettempdir()) / "anura-api"))
OUT.mkdir(exist_ok=True)
IMAGES = "imagenes"
MAX_BODY = 5 * 1024 * 1024
MAX_PAGES = 300
LOCK = threading.Lock()


class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else (body.encode() if isinstance(body, str) else json.dumps(body, ensure_ascii=False).encode())
        self.send_response(code)
        self.send_header("Content-Type", ctype + ("; charset=utf-8" if ctype.startswith("text") or ctype == "application/json" else ""))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _auth(self):
        key = os.environ.get("API_KEY")
        if key and self.headers.get("Authorization") != f"Bearer {key}":
            self._send(401, {"error": "clave de API inválida o ausente"})
            return False
        return True

    def do_GET(self):
        if not self._auth():
            return
        if self.path == "/v1/designs":
            ds = []
            for d in (render.HERE / "designs").iterdir():
                if (d / "manifest.json").exists():
                    m = json.loads((d / "manifest.json").read_text())
                    ds.append({"id": m["id"], "name": m["name"], "version": m["version"], "formats": m["formats"]})
            return self._send(200, ds)
        if self.path == "/v1/schema":
            return self._send(200, spec.json_schema())
        mm = re.fullmatch(r"/v1/designs/([\w-]+)/skill", self.path)
        if mm:
            try:
                return self._send(200, prompt.skill_md(mm.group(1)), "text/markdown")
            except Exception:  # noqa: BLE001
                return self._send(404, {"error": "diseño no encontrado"})
        mm = re.fullmatch(r"/v1/designs/([\w-]+)", self.path)
        if mm:
            try:
                _, m = render.load_design(mm.group(1))
            except Exception:  # noqa: BLE001
                return self._send(404, {"error": "diseño no encontrado"})
            reg = json.loads((render.HERE / "designs" / mm.group(1) / "variantes.json").read_text())["variantes"]
            return self._send(200, {"id": m["id"], "paleta": m["palette"]["roles"], "bloques": m["blocks"], "reglas": m["reglas_medibles"],
                                    "variantes": [{k: v[k] for k in ("id", "tipo", "nombre", "estado")} for v in reg if v["tipo"] in ("portada", "divisor", "hoja")]})
        mm = re.fullmatch(r"/v1/jobs/(\w+)", self.path)
        if mm and (OUT / f"{mm.group(1)}.informe.json").exists():
            return self._send(200, (OUT / f"{mm.group(1)}.informe.json").read_bytes())
        mm = re.fullmatch(r"/v1/files/([\w.-]+)", self.path)
        if mm and (OUT / mm.group(1)).exists():
            return self._send(200, (OUT / mm.group(1)).read_bytes(), "application/pdf")
        self._send(404, {"error": "ruta no encontrada"})

    def do_POST(self):
        if not self._auth():
            return
        n = int(self.headers.get("Content-Length", 0))
        if n > MAX_BODY:
            return self._send(413, {"error": f"cuerpo de {n} bytes; máximo {MAX_BODY}"})
        try:
            body = json.loads(self.rfile.read(n))
        except Exception:  # noqa: BLE001
            return self._send(400, {"error": "JSON inválido"})
        if self.path == "/v1/prompt":
            try:
                return self._send(200, prompt.prompt_maestro(body.get("design", "anura"), body.get("format", "pdf-a4"), body.get("palette", "default"), body.get("variants") or {},
                                                             body.get("mode", "B"), bool(body.get("short"))), "text/markdown")
            except Exception as e:  # noqa: BLE001
                return self._send(400, {"error": str(e)})
        if self.path != "/v1/render":
            return self._send(404, {"error": "ruta no encontrada"})
        design = body.get("design", "anura")
        try:
            ver = json.loads((render.HERE / "designs" / design / "manifest.json").read_text())["version"]
        except Exception:  # noqa: BLE001
            ver = "?"
        job = hashlib.sha256((json.dumps(body, sort_keys=True, ensure_ascii=False) + ver + IMAGES).encode()).hexdigest()[:12]
        if (OUT / f"{job}.informe.json").exists() and (OUT / f"{job}.pdf").exists():     # idempotencia
            rep = json.loads((OUT / f"{job}.informe.json").read_text())
            rep.update({"job": job, "pdf": f"/v1/files/{job}.pdf", "repetido": True})
            return self._send(200, rep)
        src = OUT / f"{job}.json"
        src.write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
        with LOCK:
            rep = render.run(src, OUT / f"{job}.pdf", IMAGES)
        if rep.get("paginas") and rep["paginas"] > MAX_PAGES:
            rep["avisos"].append({"bloque": "documento", "causa": f"{rep['paginas']} hojas (máx {MAX_PAGES})", "ajuste": "divide el documento"})
        (OUT / f"{job}.informe.json").write_text(json.dumps(rep, ensure_ascii=False), encoding="utf-8")
        rep.update({"job": job, "pdf": f"/v1/files/{job}.pdf" if rep["estado"] != "rechazado" else None})
        self._send(200 if rep["estado"] != "rechazado" else 422, rep)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--puerto", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--imagenes", default="imagenes")
    a = ap.parse_args()
    IMAGES = a.imagenes
    print(f"API en http://{a.host}:{a.puerto}")
    ThreadingHTTPServer((a.host, a.puerto), H).serve_forever()
