#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""API de myStyle (biblioteca estándar). Esquema completo en GET /v1/openapi.json.

Uso diario
    GET  /v1/designs                         diseños (id, nombre, versión, formatos, estilo, estado)
    GET  /v1/designs/{id}                    paletas, bloques, reglas, variantes
    GET  /v1/schema                          JSON Schema del contrato
    POST /v1/prompt                          Prompt Maestro (texto)
    POST /v1/render                          contrato -> archivo. pdf-a4 · pptx-16x9 · docx-a4 · xlsx responden al momento;
                                             video-16x9 · video-9x16 responden 202 {job, estado_url} (cola propia)
    POST /v1/batch                           {documents:[contrato…]} -> 202 {jobs:[{job, estado_url}]}
    GET  /v1/jobs/{id}                       202 + estado (en_cola, renderizando) o el informe con las URL firmadas
    POST /v1/jobs/{id}/patch                 {ops:[{op:set|insert|delete, section, block, value}]} -> vuelve a renderizar sin reenviar todo
    POST /v1/uploads                         {name, data (base64)} imagen o CSV -> {src} para usar en el contrato
    GET  /v1/commons?q=&n=                   busca en Wikimedia Commons (solo licencias libres)
    POST /v1/commons/import                  {title} -> descarga, guarda crédito y devuelve {src}
Diseños y galería
    GET  /v1/designs/{id}/skill | /motion | /kit | /fonts.zip | /gallery
    POST /v1/jobs/{id}/publish               publica un trabajo en la galería de su diseño (por defecto todo es privado)
Administración (Authorization: Bearer <clave de administrador>, en ADMIN_KEY o servidor/data/admin-key.txt)
    POST /v1/designs/import                  {id, zip (base64)} -> borrador validado
    POST /v1/designs/{id}/publish            borrador -> publicado
    GET  /v1/stats                           tiempos y avisos por diseño, formato y bloque

Seguridad: claves en API_KEY o API_KEYS (separadas por comas); URL de archivos firmadas con caducidad (RETENTION_DAYS, 7; video 2);
cuerpo ≤ 5 MB (subidas ≤ 20 MB); ≤ 300 hojas; video ≤ 120 s. Pensada para uso local o detrás de un proxy con TLS.
"""
import argparse
import base64
import hashlib
import hmac
import io
import json
import os
import queue
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import auditar
import biblioteca
import calidad
import correcciones
import galeria
import herramientas
import captura
import recursos
import referencia
import render
import render_office
import render_pptx
import render_video
import web
from engine import recetas
from engine import ids, markdown, paleta, prompt, spec

sys.path.insert(0, str(render.HERE / "tools"))
import commons  # noqa: E402

OUT = Path(os.environ.get("API_OUT", Path(tempfile.gettempdir()) / "anura-api"))
OUT.mkdir(exist_ok=True)
DATA = render.HERE / "data"
DATA.mkdir(exist_ok=True)
IMAGES = "imagenes"
MAX_BODY, MAX_UPLOAD = 5 * 1024 * 1024, 20 * 1024 * 1024
MAX_PAGES = 300
RETENTION = {"default": float(os.environ.get("RETENTION_DAYS", 7)), "video": float(os.environ.get("VIDEO_RETENTION_DAYS", 2))}
LOCK = threading.Lock()                 # Chromium del PDF: un render a la vez
STATIC = {".css": "text/css", ".js": "text/javascript", ".json": "application/json", ".md": "text/markdown", ".html": "text/html", ".png": "image/png", ".jpg": "image/jpeg", ".woff2": "font/woff2", ".pdf": "application/pdf",
          ".svg": "image/svg+xml", ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation", ".zip": "application/zip", ".mp4": "video/mp4",
          ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
DOC_FORMATS = {"pdf-a4": "pdf", "pptx-16x9": "pptx", "docx-a4": "docx", "xlsx": "xlsx", "web-animada": "html"}


def secret_file(name, env):
    if os.environ.get(env):
        return os.environ[env]
    f = DATA / name
    if not f.exists():
        f.write_text(secrets.token_hex(24))
    return f.read_text(encoding="utf-8").strip()


ADMIN_KEY = secret_file("admin-key.txt", "ADMIN_KEY")
SIGN_KEY = secret_file("sign-key.txt", "SIGN_KEY").encode()
API_KEYS = {k.strip() for k in (os.environ.get("API_KEYS", "") + "," + os.environ.get("API_KEY", "")).split(",") if k.strip()}


# ---------- URL firmadas ----------
def sign(path, days=None):
    exp = int(time.time() + 86400 * (days or RETENTION["default"]))
    sig = hmac.new(SIGN_KEY, f"{path}|{exp}".encode(), hashlib.sha256).hexdigest()[:24]
    return f"{path}?exp={exp}&sig={sig}"


def signed_ok(path, qs):
    try:
        exp, sig = int(qs["exp"][0]), qs["sig"][0]
    except (KeyError, ValueError, IndexError):
        return False
    good = hmac.new(SIGN_KEY, f"{path}|{exp}".encode(), hashlib.sha256).hexdigest()[:24]
    return exp >= time.time() and hmac.compare_digest(good, sig)


def with_urls(rep):
    """Toda ruta /v1/files/… del informe sale firmada (caduca con la retención)."""
    out = dict(rep)
    for k, v in rep.items():
        if isinstance(v, str) and v.startswith("/v1/files/") and "?" not in v:
            out[k] = sign(v, RETENTION["video"] if v.endswith((".mp4", "_proyecto.zip")) else None)
    return out


# ---------- registro (observabilidad) ----------
def log(job, body, rep, secs):
    bloques = sorted({str(a.get("bloque", "")).split(".")[0] for a in rep.get("avisos", []) if a.get("bloque")})[:20]
    with (OUT / "registro.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"t": int(time.time()), "job": job, "design": body.get("design"), "format": body.get("format", "pdf-a4"), "estado": rep.get("estado"),
                            "segundos": round(secs, 2), "avisos": len(rep.get("avisos", [])), "bloques": bloques}, ensure_ascii=False) + "\n")


# ---------- renders ----------
def job_id(body):
    try:
        ver = json.loads((render.HERE / "designs" / body.get("design", "anura") / "manifest.json").read_text(encoding="utf-8"))["version"]
    except Exception:  # noqa: BLE001
        ver = "?"
    return hashlib.sha256((json.dumps(body, sort_keys=True, ensure_ascii=False) + ver + IMAGES).encode()).hexdigest()[:12]


def render_doc(body, job=None):
    """PDF, PPTX, Word o Excel. Devuelve (código HTTP, informe con rutas sin firmar). Idempotente por contenido."""
    body = ids.asegurar(body)
    job = job or job_id(body)
    fmt = body.get("format", "pdf-a4")
    ext = DOC_FORMATS.get(fmt)
    if not ext:
        return 400, {"error": f"formato '{fmt}' no soportado; usa {sorted(DOC_FORMATS) + sorted(render_video.FORMATS)}"}
    if (OUT / f"{job}.informe.json").exists() and (OUT / f"{job}.{ext}").exists():
        rep = json.loads((OUT / f"{job}.informe.json").read_text(encoding="utf-8"))
        rep.update({"job": job, ext: f"/v1/files/{job}.{ext}", "repetido": True})
        return 200, rep
    src = OUT / f"{job}.json"
    src.write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
    t0 = time.time()
    with LOCK:
        if ext == "pdf":
            rep = render.run(src, OUT / f"{job}.pdf", IMAGES)
        elif ext == "pptx":
            rep = render_pptx.run(src, OUT / f"{job}.pptx", IMAGES)
        elif ext == "html":
            rep = web.run(src, OUT / f"{job}.html", IMAGES)
        else:
            rep = render_office.run(src, OUT / f"{job}.{ext}", IMAGES)
    if rep.get("paginas") and rep["paginas"] > MAX_PAGES:
        rep["avisos"].append({"bloque": "documento", "causa": f"{rep['paginas']} hojas (máx {MAX_PAGES})", "ajuste": "divide el documento"})
    if isinstance(rep.get("fuentes"), dict):
        rep["fuentes"]["descarga"] = f"/v1/designs/{body.get('design', 'anura')}/fonts.zip"
    rep.update({"job": job, "formato": fmt})
    (OUT / f"{job}.informe.json").write_text(json.dumps(rep, ensure_ascii=False), encoding="utf-8")
    log(job, body, rep, time.time() - t0)
    rep[ext] = f"/v1/files/{job}.{ext}" if rep["estado"] != "rechazado" else None
    return (200 if rep["estado"] != "rechazado" else 422), rep


VIDEO_Q, DOC_Q = queue.Queue(), queue.Queue()      # colas separadas: un video largo no bloquea los documentos


def enqueue(body):
    """Encola un trabajo (video o documento de un lote). Devuelve el estado sin firmar."""
    body = ids.asegurar(body)
    job = job_id(body)
    video = body.get("format") in render_video.FORMATS
    done = OUT / f"{job}.{'mp4' if video else DOC_FORMATS.get(body.get('format', 'pdf-a4'), 'pdf')}"
    if (OUT / f"{job}.informe.json").exists() and done.exists():
        return {"job": job, "estado": "ok", "estado_url": f"/v1/jobs/{job}"}
    st = OUT / f"{job}.estado.json"
    if not st.exists() or json.loads(st.read_text(encoding="utf-8"))["estado"] in ("fallido", "rechazado", "ok"):
        (OUT / f"{job}.json").write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
        st.write_text(json.dumps({"job": job, "estado": "en_cola"}), encoding="utf-8")
        (OUT / f"{job}.informe.json").unlink(missing_ok=True)
        (VIDEO_Q if video else DOC_Q).put((job, body))
    return {"job": job, "estado": json.loads(st.read_text(encoding="utf-8"))["estado"], "estado_url": f"/v1/jobs/{job}", "en_cola": (VIDEO_Q if video else DOC_Q).qsize()}


def video_worker():
    while True:
        job, body = VIDEO_Q.get()
        st = OUT / f"{job}.estado.json"
        st.write_text(json.dumps({"job": job, "estado": "renderizando"}), encoding="utf-8")
        t0 = time.time()
        try:
            q = ((body.get("options") or {}).get("video") or {}).get("quality", "draft")
            rep = render_video.run(OUT / f"{job}.json", OUT / f"{job}.mp4", body["format"], q if q in ("draft", "looks", "delivery") else "draft")
            proj = OUT / f"{job}_proyecto"
            if proj.exists():
                shutil.make_archive(str(proj), "zip", proj)
                rep["proyecto"] = f"/v1/files/{job}_proyecto.zip"
            if rep["estado"] not in ("rechazado", "fallido"):
                rep["video"] = f"/v1/files/{job}.mp4"
        except Exception as e:  # noqa: BLE001
            rep = {"estado": "fallido", "errores": [{"bloque": "video", "causa": str(e)[:400], "ajuste": "revisa `npx hyperframes doctor`"}], "avisos": []}
        rep["job"] = job
        (OUT / f"{job}.informe.json").write_text(json.dumps(rep, ensure_ascii=False), encoding="utf-8")
        st.write_text(json.dumps({"job": job, "estado": rep["estado"]}), encoding="utf-8")
        log(job, body, rep, time.time() - t0)
        VIDEO_Q.task_done()


def doc_worker():
    while True:
        job, body = DOC_Q.get()
        st = OUT / f"{job}.estado.json"
        st.write_text(json.dumps({"job": job, "estado": "renderizando"}), encoding="utf-8")
        try:
            _, rep = render_doc(body, job)
        except Exception as e:  # noqa: BLE001
            rep = {"estado": "fallido", "errores": [{"bloque": "render", "causa": str(e)[:400], "ajuste": "revisa el contrato con GET /v1/schema"}]}
            (OUT / f"{job}.informe.json").write_text(json.dumps(rep, ensure_ascii=False), encoding="utf-8")
        st.write_text(json.dumps({"job": job, "estado": rep["estado"]}), encoding="utf-8")
        DOC_Q.task_done()


def janitor():
    """Retención: borra trabajos vencidos (el video antes) salvo los publicados en una galería."""
    while True:
        keep = {g["job"] for f in DATA.glob("galeria-*.json") for g in json.loads(f.read_text(encoding="utf-8"))}
        now = time.time()
        for f in OUT.iterdir():
            job = f.name.split(".")[0].split("_")[0]
            if job in keep or f.name in ("registro.jsonl", "galeria", "kits"):
                continue
            days = RETENTION["video"] if f.suffix == ".mp4" or "_proyecto" in f.name else RETENTION["default"]
            try:
                if now - f.stat().st_mtime > days * 86400:
                    shutil.rmtree(f) if f.is_dir() else f.unlink()
            except OSError:
                pass
        time.sleep(3600)


for fn in (video_worker, doc_worker, janitor):
    threading.Thread(target=fn, daemon=True).start()


# ---------- parches ----------
def apply_patch(doc, ops):
    """Edición por parches: el agente cambia un bloque sin reenviar el documento. Errores con formato fijo."""
    secs = {s["id"]: s for p in doc["document"]["parts"] for s in p["sections"]}
    for i, op in enumerate(ops):
        where = f"ops[{i}]"
        if op.get("op") == "meta":
            doc.setdefault("meta", {}).update(op.get("value") or {})
            continue
        s = secs.get(op.get("section"))
        if s is None:
            raise ValueError(f"{where}: sección '{op.get('section')}' no existe; ids: {', '.join(list(secs)[:12])}")
        bl, k = s.setdefault("blocks", []), op.get("block")
        if op.get("op") == "set" and k is None:
            s.update(op.get("value") or {})                   # campos de la sección (title, lead…)
        elif op.get("op") == "set":
            j = ids.indice(doc, s, k)
            val = dict(op["value"])
            if isinstance(bl[j], dict) and bl[j].get("id") and not val.get("id"):
                val["id"] = bl[j]["id"]                     # el bloque conserva su identidad al cambiar de contenido
            bl[j] = val
        elif op.get("op") == "insert":
            bl.insert(len(bl) if k is None else ids.indice(doc, s, k), op["value"])
        elif op.get("op") == "delete":
            del bl[ids.indice(doc, s, k)]
        else:
            raise ValueError(f"{where}: op debe ser set, insert, delete o meta")
    return doc


def registrar_patch(antes, despues, ops, motivo, job, origen):
    """Cada parche con `motivo` queda como corrección (antes/después del bloque) para aprender de ella."""
    def blk(d, sid, k):
        for p in d["document"]["parts"]:
            for sec in p["sections"]:
                if sec["id"] == sid:
                    try:
                        return sec["blocks"][ids.indice(d, sec, k)]
                    except (ValueError, IndexError):
                        return None
        return None
    for op in ops:
        if op.get("op") == "meta" or op.get("section") is None:
            continue
        k = op.get("block")
        a = blk(antes, op["section"], k) if k is not None and op.get("op") in ("set", "delete") else None
        b = op.get("value") if op.get("op") in ("set", "insert") else None
        sec = f"{op['section']}.{(a or b or {}).get('id', k)}" if k is not None or b else op["section"]
        try:
            correcciones.guardar({"seccion": sec, "antes": a, "despues": b, "motivo": motivo, "job": job, "origen": origen if origen in correcciones.ORIGENES else "modelo",
                                  "design": antes.get("design"), "formato": antes.get("format")})
        except ValueError:
            pass


# ---------- diseños ----------
def manifest(did):
    return json.loads((render.HERE / "designs" / did / "manifest.json").read_text(encoding="utf-8"))


def kit_zip(did):
    """Kit del diseño (modo B, sin API): manifiesto, CSS, fuentes, símbolos, plantillas, SKILL, Prompt Maestro, esquema y ejemplo."""
    d = render.HERE / "designs" / did
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in d.rglob("*"):
            if f.is_file() and "ranas" not in f.parts and f.suffix != ".zip":
                z.write(f, f"{did}/{f.relative_to(d).as_posix()}")
        z.writestr(f"{did}/SKILL.md", prompt.skill_md(did))
        z.writestr(f"{did}/PROMPT_MAESTRO.md", prompt.prompt_maestro(did, "pdf-a4", "default", {}, "B", False))
        z.writestr(f"{did}/contrato.schema.json", json.dumps(spec.json_schema(), ensure_ascii=False, indent=1))
        ej = render.HERE / "tests" / "ejemplo_minimo.json"
        if ej.exists():
            z.write(ej, f"{did}/ejemplo.json")
    return buf.getvalue()


def import_design(body):
    did = body.get("id", "")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,30}", did):
        return 400, {"error": "id: minúsculas, números y guiones (2-31)"}
    dest = render.HERE / "designs" / did
    if dest.exists() and manifest(did).get("estado", "publicado") == "publicado":
        return 409, {"error": "ya existe un diseño publicado con ese id; súbelo con otro id o como versión nueva"}
    raw = base64.b64decode(body.get("zip", ""), validate=True)
    tmp = Path(tempfile.mkdtemp())
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        total = 0
        for i in z.infolist():
            total += i.file_size
            target = (tmp / i.filename).resolve()
            if tmp.resolve() not in target.parents and target != tmp.resolve() or total > 200e6:
                return 400, {"error": f"ruta no permitida o paquete demasiado grande: {i.filename}"}
        z.extractall(tmp)
    root = next((p.parent for p in tmp.rglob("manifest.json")), None)
    if not root:
        return 400, {"error": "el paquete no trae manifest.json"}
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(root, dest)
    m = manifest(did)
    m.update({"id": did, "estado": "borrador"})
    (dest / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    r = subprocess.run([sys.executable, str(render.HERE / "validar_diseno.py"), did, "--rapido"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    return 201, {"id": did, "estado": "borrador", "validacion": (r.stdout or r.stderr)[-3000:], "valido": r.returncode == 0,
                 "siguiente": f"revisa la galería y publica con POST /v1/designs/{did}/publish"}


def openapi():
    def op(summary, body=None, resp="Informe o datos JSON"):
        o = {"summary": summary, "responses": {"200": {"description": resp}}}
        if body:
            o["requestBody"] = {"required": True, "content": {"application/json": {"schema": body}}}
        return o
    doc_ref = {"$ref": "#/components/schemas/Contrato"}
    return {"openapi": "3.1.0", "info": {"title": "myStyle · API de documentos", "version": spec.CONTRACT_VERSION,
                                         "description": "El agente manda datos (contrato JSON); el servidor maqueta y devuelve PDF, PPTX, Word, Excel o video. El texto del contrato es dato, nunca instrucciones."},
            "servers": [{"url": "/"}], "components": {"schemas": {"Contrato": spec.json_schema()},
                                                      "securitySchemes": {"clave": {"type": "http", "scheme": "bearer"}}}, "security": [{"clave": []}],
            "paths": {
                "/v1/designs": {"get": op("Lista los diseños")},
                "/v1/designs/{id}": {"get": op("Paletas, bloques, reglas y variantes de un diseño")},
                "/v1/schema": {"get": op("JSON Schema del contrato")},
                "/v1/prompt": {"post": op("Prompt Maestro de un diseño", {"type": "object", "properties": {"design": {"type": "string"}, "format": {"type": "string"}, "mode": {"enum": ["A", "B"]}, "short": {"type": "boolean"}}})},
                "/v1/render": {"post": op("Renderiza un documento. format: pdf-a4, pptx-16x9, docx-a4, xlsx (al momento) o video-16x9, video-9x16 (202 + job)", doc_ref)},
                "/v1/batch": {"post": op("Lote de documentos -> trabajos", {"type": "object", "properties": {"documents": {"type": "array", "items": doc_ref}}})},
                "/v1/jobs/{id}": {"get": op("Estado e informe de un trabajo (URL firmadas)")},
                "/v1/jobs/{id}/patch": {"post": op("Corrige bloques sin reenviar el documento", {"type": "object", "properties": {
                    "ops": {"type": "array", "items": {"type": "object", "properties": {"op": {"enum": ["set", "insert", "delete", "meta"]}, "section": {"type": "string"}, "block": {"type": ["integer", "string"], "description": "índice o id estable del bloque"}, "value": {}}}},
                    "format": {"type": "string"}, "motivo": {"type": "string", "description": "por qué se corrige; se guarda como corrección aprendida"}}})},
                "/v1/jobs/{id}/publish": {"post": op("Publica un trabajo en la galería de su diseño")},
                "/v1/uploads": {"post": op("Sube una imagen o CSV (base64) y devuelve src", {"type": "object", "properties": {"name": {"type": "string"}, "data": {"type": "string"}}})},
                "/v1/commons": {"get": op("Busca imágenes libres en Wikimedia Commons (q, n)")},
                "/v1/commons/import": {"post": op("Importa una imagen de Commons con su crédito", {"type": "object", "properties": {"title": {"type": "string"}}})},
                "/v1/designs/{id}/gallery": {"get": op("Trabajos publicados con ese diseño")},
                "/v1/designs/{id}/kit": {"get": op("Kit del diseño (zip) para el modo B", resp="application/zip")},
                "/v1/designs/{id}/skill": {"get": op("SKILL.md del diseño", resp="text/markdown")},
                "/v1/designs/{id}/motion": {"get": op("Kit de motion para /estudio-motion y /brag", resp="text/markdown")},
                "/v1/recipes": {"get": op("Recetas e ingredientes (q para buscar); POST expande receta+valores a Markdown"), "post": op("Expande una receta ({receta, valores}) o ingredientes ({ingredientes, meta}) a Markdown")},
                "/v1/recipes/{id}": {"get": op("Huecos de una receta o ingrediente")},
                "/v1/library": {"get": op("Busca en la biblioteca de estilos, plantillas, componentes y animaciones (q, tipo, n)"),
                                "post": op("Guarda un estilo o plantilla nueva (409 si existe: pide sobrescribir)", {"type": "object", "properties": {"entry": {"type": "object"}, "sobrescribir": {"type": "boolean"}}})},
                "/v1/library/{id}": {"get": op("Ficha de una entrada: parámetros, ejemplo y error típico")},
                "/v1/audit": {"post": op("Audita un PDF (márgenes, solapes, contraste, fuentes)", {"type": "object", "properties": {"job": {"type": "string"}, "pdf_base64": {"type": "string"}, "margen_mm": {"type": "number"}}})},
                "/v1/corrections": {"get": op("Busca correcciones parecidas (q) o lista las que se repiten"),
                                    "post": op("Registra una corrección aceptada", {"type": "object", "properties": {"seccion": {"type": "string"}, "antes": {}, "despues": {}, "motivo": {"type": "string"}}, "required": ["motivo"]})},
                "/v1/jobs/{id}/doc": {"get": op("Documento del trabajo con los ids estables de sus bloques")},
                "/v1/markdown": {"post": op("Convierte Markdown (cabecera con titulo, formato y estilo) al contrato JSON", {"type": "object", "properties": {"markdown": {"type": "string"}, "design": {"type": "string"}, "format": {"type": "string"}}})},
                "/v1/tools": {"get": op("Herramientas del agente como function calling estilo OpenAI (perfil=minimo para modelos pequeños)")},
            }}


class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json", extra=None):
        data = body if isinstance(body, bytes) else (body.encode() if isinstance(body, str) else json.dumps(body, ensure_ascii=False).encode())
        self.send_response(code)
        self.send_header("Content-Type", ctype + ("; charset=utf-8" if ctype.startswith("text") or ctype == "application/json" else ""))
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def _admin(self):
        return hmac.compare_digest(self.headers.get("Authorization", ""), f"Bearer {ADMIN_KEY}")

    def _auth(self, path):
        if not API_KEYS or path.startswith(("/web/", "/v1/files/")) or path in ("/", "/index.html", "/v1/openapi.json") or self._admin():
            return True                                         # los archivos se protegen con su firma
        if self.headers.get("Authorization", "").removeprefix("Bearer ") in API_KEYS:
            return True
        self._send(401, {"error": "clave de API inválida o ausente", "ajuste": "envía Authorization: Bearer <clave>"})
        return False

    def do_GET(self):
        u = urllib.parse.urlsplit(self.path)
        path, qs = u.path, urllib.parse.parse_qs(u.query)
        if not self._auth(path):
            return
        if path in ("/", "/index.html") or re.fullmatch(r"/(como|agente|catalogo(/\w+)?|taller|formatos|estilos|estadisticas)/?", path):   # rutas del frontend
            return self._send(200, (render.HERE / "web" / "app.html").read_bytes(), "text/html")
        if path.startswith("/web/"):                                   # estáticos del frontend (fuentes, imágenes, catálogo, css)
            f = (render.HERE / path.lstrip("/")).resolve()
            if (render.HERE / "web") in f.parents and f.is_file():
                return self._send(200, f.read_bytes(), STATIC.get(f.suffix, "application/octet-stream"))
            return self._send(404, {"error": "no existe"})
        if path == "/v1/openapi.json":
            return self._send(200, openapi())
        if path == "/v1/tools":                                         # las mismas herramientas del MCP, como function calling estilo OpenAI (Ollama, LM Studio…)
            return self._send(200, herramientas.openai_tools(core_only=qs.get("perfil", [""])[0] == "minimo"))
        mm = re.fullmatch(r"/v1/styles/([\w-]+)/validate", path)         # lista de revisión de un diseño
        if mm and (render.HERE / "designs" / mm.group(1)).is_dir():
            r = subprocess.run([sys.executable, str(render.HERE / "validar_diseno.py"), mm.group(1), "--rapido"], capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=render.HERE.parent, timeout=600)
            return self._send(200, {"ok": "TODO ✔" in r.stdout, "salida": r.stdout[-1600:]})
        if path == "/v1/recipes":                                       # el supermercado: recetas e ingredientes
            return self._send(200, biblioteca.buscar(qs["q"][0], qs.get("tipo", [None])[0], qs.get("n", ["5"])[0]) if qs.get("q") else
                              [{k: e.get(k) for k in ("id", "tipo", "nombre", "descripcion", "formato")} for t in ("receta", "ingrediente") for e in biblioteca.todos(t)])
        mm = re.fullmatch(r"/v1/recipes/([\w-]+)", path)
        if mm:
            e = biblioteca.obtener(mm.group(1))
            return self._send(200, recetas.ficha(e)) if e and "markdown" in e else self._send(404, {"error": f"no hay receta '{mm.group(1)}'", "ajuste": "busca con GET /v1/recipes?q=…"})
        if path == "/v1/library":
            return self._send(200, biblioteca.buscar(qs.get("q", [""])[0], qs.get("tipo", [None])[0], qs.get("n", ["5"])[0]) if qs.get("q") else
                              [{k: e.get(k) for k in ("id", "tipo", "nombre", "version", "tags")} for e in biblioteca.todos(qs.get("tipo", [None])[0])])
        mm = re.fullmatch(r"/v1/library/([\w-]+)", path)
        if mm:
            e = biblioteca.obtener(mm.group(1), qs.get("tipo", [None])[0])
            return self._send(200, e) if e else self._send(404, {"error": f"no hay '{mm.group(1)}' en la biblioteca", "ajuste": "busca con GET /v1/library?q=…"})
        if path == "/v1/corrections":
            return self._send(200, correcciones.buscar(qs.get("q", [""])[0], qs.get("n", ["3"])[0]) if qs.get("q") else correcciones.frecuentes(int(qs.get("minimo", ["3"])[0])))
        mm = re.fullmatch(r"/v1/jobs/(\w+)/doc", path)                    # el documento del trabajo con los ids estables de sus bloques
        if mm and (OUT / f"{mm.group(1)}.json").exists():
            return self._send(200, (OUT / f"{mm.group(1)}.json").read_bytes())
        if path == "/v1/catalog":
            return self._send(200, (render.HERE / "web" / "cat" / "catalog.json").read_bytes())
        mm = re.fullmatch(r"/v1/examples/(\w+)", path)                  # JSON de contenido de una plantilla del catálogo
        if mm and (render.HERE.parent / "contenido" / f"{mm.group(1)}.json").exists():
            return self._send(200, (render.HERE.parent / "contenido" / f"{mm.group(1)}.json").read_bytes())
        if path == "/v1/designs":
            ds = []
            for d in sorted((render.HERE / "designs").iterdir()):
                if (d / "manifest.json").exists():
                    m = manifest(d.name)
                    if m.get("estado", "publicado") == "publicado" or self._admin():
                        ds.append({"id": m["id"], "name": m["name"], "version": m["version"], "formats": m["formats"] + sorted(set(DOC_FORMATS) - set(m["formats"])) + sorted(render_video.FORMATS),
                                   "estilo": m.get("estilo", "brutalismo"), "estado": m.get("estado", "publicado")})
            return self._send(200, ds)
        if path == "/v1/schema":
            return self._send(200, spec.json_schema())
        if path == "/v1/stats":
            if not self._admin():
                return self._send(401, {"error": "solo administración"})
            rows = [json.loads(x) for x in (OUT / "registro.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()] if (OUT / "registro.jsonl").exists() else []
            agg = {}
            for r in rows:
                a = agg.setdefault(f"{r['design']}·{r['format']}", {"trabajos": 0, "fallidos": 0, "segundos": 0.0, "avisos": 0})
                a["trabajos"] += 1
                a["fallidos"] += r["estado"] in ("fallido", "rechazado")
                a["segundos"] += r["segundos"]
                a["avisos"] += r["avisos"]
            top = {}
            for r in rows:
                for b in r["bloques"]:
                    top[b] = top.get(b, 0) + 1
            return self._send(200, {"por_diseno_formato": {k: {**v, "segundos_medio": round(v["segundos"] / v["trabajos"], 2)} for k, v in agg.items()},
                                    "bloques_con_mas_avisos": sorted(top.items(), key=lambda x: -x[1])[:15], "total": len(rows)})
        if path == "/v1/commons":
            q = (qs.get("q") or [""])[0].strip()
            if not q:
                return self._send(400, {"error": "falta q", "ajuste": "/v1/commons?q=Dendrobates&n=6"})
            try:
                return self._send(200, {"resultados": commons.buscar(q, min(12, int((qs.get("n") or ["6"])[0])), 900)})
            except Exception as e:  # noqa: BLE001
                return self._send(502, {"error": f"Wikimedia Commons no respondió: {str(e)[:120]}", "ajuste": "reintenta en unos segundos o sube la imagen con POST /v1/uploads"})
        mm = re.fullmatch(r"/v1/designs/([\w-]+)/(skill|motion|kit|gallery|fonts\.zip)", path)
        if mm and (render.HERE / "designs" / mm.group(1) / "manifest.json").exists():
            did, what = mm.groups()
            if what == "skill":
                return self._send(200, prompt.skill_md(did), "text/markdown")
            if what == "motion":
                return self._send(200, render_video.motion_kit(did, f"http://{self.headers.get('Host', 'localhost:8765')}"), "text/markdown")
            if what == "kit":
                return self._send(200, kit_zip(did), "application/zip", {"Content-Disposition": f'attachment; filename="kit-{did}.zip"'})
            if what == "gallery":
                g = DATA / f"galeria-{did}.json"
                items = json.loads(g.read_text(encoding="utf-8")) if g.exists() else []
                fmt = (qs.get("format") or [None])[0]
                return self._send(200, {"trabajos": [with_urls(x) for x in items if not fmt or x["formato"] == fmt]})
            z = render.HERE / "designs" / did / "fonts" / f"fuentes-{did}.zip"
            return self._send(200, z.read_bytes(), "application/zip") if z.exists() else self._send(404, {"error": "sin fuentes empaquetadas", "ajuste": f"python servidor/tools/fuentes_ttf.py {did}"})
        mm = re.fullmatch(r"/v1/designs/([\w-]+)", path)
        if mm:
            try:
                _, m = render.load_design(mm.group(1))
            except Exception:  # noqa: BLE001
                return self._send(404, {"error": "diseño no encontrado"})
            reg = json.loads((render.HERE / "designs" / mm.group(1) / "variantes.json").read_text(encoding="utf-8"))["variantes"]
            return self._send(200, {"id": m["id"], "paleta": m["palette"]["roles"], "paletas": {k: v for k, v in json.loads((render.HERE / "designs" / mm.group(1) / "palettes.json").read_text(encoding="utf-8")).items() if not k.startswith("_")},
                                    "bloques": m["blocks"], "reglas": m["reglas_medibles"], "estilo": m.get("estilo", "brutalismo"),
                                    "variantes": [{k: v[k] for k in ("id", "tipo", "nombre", "estado", "uso")} for v in reg if v["tipo"] in ("portada", "divisor", "hoja")]})
        mm = re.fullmatch(r"/v1/jobs/(\w+)", path)
        if mm and (OUT / f"{mm.group(1)}.informe.json").exists():
            rep = json.loads((OUT / f"{mm.group(1)}.informe.json").read_text(encoding="utf-8"))
            for ext in ("pdf", "pptx", "docx", "xlsx"):
                if (OUT / f"{mm.group(1)}.{ext}").exists() and rep.get("estado") != "rechazado":
                    rep[ext] = f"/v1/files/{mm.group(1)}.{ext}"
            return self._send(200, with_urls(rep))
        if mm and (OUT / f"{mm.group(1)}.estado.json").exists():           # en cola o renderizando
            return self._send(202, (OUT / f"{mm.group(1)}.estado.json").read_bytes())
        mm = re.fullmatch(r"/v1/files/([\w.-]+)", path)
        if mm and (OUT / mm.group(1)).is_file():
            if not signed_ok(path, qs):
                return self._send(403, {"error": "enlace vencido o sin firma", "ajuste": "pide de nuevo GET /v1/jobs/{id} para obtener un enlace nuevo"})
            return self._send(200, (OUT / mm.group(1)).read_bytes(), STATIC.get(Path(mm.group(1)).suffix, "application/octet-stream"))
        self._send(404, {"error": "ruta no encontrada", "ajuste": "mira GET /v1/openapi.json"})

    def do_POST(self):
        path = urllib.parse.urlsplit(self.path).path
        if not self._auth(path):
            return
        n = int(self.headers.get("Content-Length", 0))
        limit = MAX_UPLOAD if path in ("/v1/uploads", "/v1/designs/import") else MAX_BODY
        if n > limit:
            return self._send(413, {"error": f"cuerpo de {n} bytes; máximo {limit}"})
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except Exception:  # noqa: BLE001
            return self._send(400, {"error": "JSON inválido"})
        md_av = []
        if path in ("/v1/render", "/v1/recipes"):                       # entrada en Markdown o receta/ingredientes: el contenido llega escrito, el motor lo asigna a bloques
            try:
                if path == "/v1/recipes":                               # solo expande a Markdown (para revisarlo antes de renderizar)
                    exp, md_av = recetas.a_markdown(body)
                    return self._send(200, {"markdown": exp.get("markdown", ""), "avisos": md_av})
                body, md_av = markdown.expandir(body)
            except ValueError as ex:
                return self._send(400, {"error": str(ex), "ajuste": "busca con list_recipes y mira los huecos con recipe_get"})
        elif path == "/v1/batch" and isinstance(body.get("documents"), list):
            body["documents"] = [markdown.expandir(d)[0] for d in body["documents"]]
        if path == "/v1/markdown":                                      # solo convierte (para revisar el contrato antes de renderizar)
            doc, av = markdown.a_contrato(str(body.get("markdown", "")), {k: body[k] for k in ("design", "format", "palette", "options") if body.get(k)})
            return self._send(200, {"document": doc, "avisos": av})
        if path == "/v1/audit":                                         # PDF propio o de un trabajo: márgenes, solapes, contraste, fuentes
            try:
                if body.get("job"):
                    f = OUT / f"{re.sub(r'[^0-9a-f]', '', str(body['job']))}.pdf"
                    if not f.exists():
                        return self._send(404, {"error": "ese trabajo no tiene PDF (¿vencido?)", "ajuste": "crea el PDF con create_pdf y audita su job"})
                    return self._send(200, auditar.auditar(str(f), margen_mm=float(body.get("margen_mm", 10))))
                raw = base64.b64decode(body.get("pdf_base64", ""), validate=True)
                if not raw.startswith(b"%PDF"):
                    return self._send(415, {"error": "no es un PDF", "ajuste": "envía pdf_base64 de un PDF o un job"})
                return self._send(200, auditar.auditar(datos=raw, margen_mm=float(body.get("margen_mm", 10))))
            except Exception as e:  # noqa: BLE001
                return self._send(400, {"error": str(e)[:300], "ajuste": "envía {job} o {pdf_base64}"})
        if path == "/v1/reference":                                     # imagen de referencia → paleta, modo, comando de la fábrica
            try:
                ruta = body.get("ruta")
                if body.get("base64"):
                    raw = base64.b64decode(body["base64"], validate=True)
                    ruta = str(OUT / f"ref_{hashlib.sha256(raw).hexdigest()[:12]}.img")
                    Path(ruta).write_bytes(raw)
                if not ruta or not Path(ruta).is_file():
                    return self._send(400, {"error": "envía {ruta} de un archivo local o {base64}", "ajuste": "imagen PNG/JPG/WEBP o PDF"})
                return self._send(200, referencia.analizar(ruta, str(body.get("id", "estilo-nuevo"))))
            except Exception as e:  # noqa: BLE001
                return self._send(400, {"error": str(e)[:300]})
        if path == "/v1/screenshot":                                    # para MIRAR lo creado: página de un PDF o una web local
            try:
                job = re.sub(r"[^0-9a-f]", "", str(body.get("job", "")))
                origen = next((str(OUT / f"{job}.{e}") for e in ("pdf", "html") if job and (OUT / f"{job}.{e}").exists()), body.get("url") or body.get("ruta"))
                if not origen:
                    return self._send(400, {"error": "envía {job} o {url} (http://127.0.0.1…)", "ajuste": "para un PDF: {job, pagina}"})
                dest = OUT / f"cap_{hashlib.sha256((str(origen) + str(body.get('pagina', 1))).encode()).hexdigest()[:10]}.png"
                with LOCK:
                    rep = captura.capturar(origen, dest, body.get("pagina", 1), body.get("ancho", 1280), body.get("alto", 800), bool(body.get("completa")))
                rep["png"] = f"/v1/files/{dest.name}"
                return self._send(200, with_urls(rep))
            except Exception as e:  # noqa: BLE001
                return self._send(400, {"error": str(e)[:300]})
        mm = re.fullmatch(r"/v1/styles(?:/([\w-]+)/(variants))?", path)   # fábrica de estilos (solo administración: escribe diseños)
        if mm:
            if not self._admin():
                return self._send(401, {"error": "crear estilos es de administración", "ajuste": "usa la clave de servidor/data/admin-key.txt (el cliente local la lee solo)"})
            try:
                if mm.group(2):
                    cmd = ["variante", mm.group(1), "--tipo", str(body["tipo"]), "--fondo", str(body["fondo"]), "--nuevo", str(body["nuevo"])]
                else:
                    i = str(body.get("id", ""))
                    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,30}", i):
                        return self._send(400, {"error": "id en minúsculas (a-z, 0-9, -)"})
                    cmd = ["estilo", i, "--acento", str(body["acento"]), "--piel", str(body.get("piel", "suave")), "--modo", str(body.get("modo", "claro"))] + (["--nombre", str(body["nombre"])] if body.get("nombre") else [])
                with LOCK:
                    r = subprocess.run([sys.executable, str(render.HERE / "fabrica_estilo.py")] + cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=render.HERE.parent, timeout=600)
                ok = "VALIDACIÓN: todo" in r.stdout
                return self._send(201 if ok else 422, {"ok": ok, "salida": r.stdout[-1400:] or r.stderr[-500:], "ajuste": None if ok else "corrige lo que marca ✘ o usa otro acento/piel; luego vuelve a llamar"})
            except (KeyError, subprocess.TimeoutExpired) as e:
                return self._send(400, {"error": f"falta o tardó: {e}", "ajuste": "estilo: {id, acento, piel?, modo?, nombre?}; variantes: {tipo, fondo, nuevo}"})
        if path == "/v1/resources":                                     # patrones, fondos e iconos generados por código → imagenes/recursos/
            try:
                return self._send(201, recursos.crear(str(body.get("tipo", "")), str(body.get("id", "")), body.get("color", "#7C3AED"), body.get("color2", "#FFFFFF"),
                                                      body.get("tam", 40), body.get("ancho", 1600), body.get("alto", 900), str(body.get("icono", "leaf"))))
            except ValueError as ex:
                return self._send(400, {"error": str(ex), "ajuste": "tipos: " + ", ".join(recursos.TIPOS)})
        if path == "/v1/quality":                                       # ortografía (LanguageTool) + accesibilidad del PDF de un trabajo, o ortografía de un texto
            try:
                rep = {}
                job = re.sub(r"[^0-9a-f]", "", str(body.get("job", "")))
                texto = str(body.get("texto", ""))
                if job:
                    if (OUT / f"{job}.pdf").exists():
                        rep["accesibilidad"] = calidad.pdf_accesible(str(OUT / f"{job}.pdf"))
                    if (OUT / f"{job}.json").exists():
                        texto = "\n".join(calidad.textos(json.loads((OUT / f"{job}.json").read_text(encoding="utf-8"))))
                if not job and not texto:
                    return self._send(400, {"error": "envía {job} o {texto}"})
                rep["ortografia"] = calidad.ortografia(texto[:20000])
                return self._send(200, rep)
            except Exception as e:  # noqa: BLE001
                return self._send(400, {"error": str(e)[:300]})
        if path == "/v1/library":                                       # save_style: JSON de datos, nunca código; si existe, exige sobrescribir
            try:
                e = body.get("entry") or {}
                if len(json.dumps(e)) > 20000:
                    return self._send(413, {"error": "entrada de más de 20 KB"})
                e.pop("skill", None)
                return self._send(201, biblioteca.guardar(e, bool(body.get("sobrescribir"))))
            except ValueError as ex:
                return self._send(409 if "ya existe" in str(ex) else 400, {"error": str(ex)})
        if path == "/v1/corrections":
            try:
                return self._send(201, correcciones.guardar(body))
            except ValueError as ex:
                return self._send(400, {"error": str(ex)})
        if path == "/v1/prompt":
            try:
                return self._send(200, prompt.prompt_maestro(body.get("design", "anura"), body.get("format", "pdf-a4"), body.get("palette", "default"), body.get("variants") or {},
                                                             body.get("mode", "B"), bool(body.get("short"))), "text/markdown")
            except Exception as e:  # noqa: BLE001
                return self._send(400, {"error": str(e)})
        if path == "/v1/paleta":      # revisa una paleta propia {rol: #hex}: contraste y grises
            try:
                m = manifest(body.get("design", "anura"))
                roles = {**m["palette"]["roles"], **body["palette"]}
                if not all(re.fullmatch(r"#[0-9a-fA-F]{6}", v) for v in roles.values()):
                    raise ValueError("cada rol debe ser #rrggbb")
                return self._send(200, {"avisos": paleta.check(roles, m)})
            except Exception as e:  # noqa: BLE001
                return self._send(400, {"error": str(e)})
        if path == "/v1/galeria":     # variantes dibujadas con el motor real y la paleta pedida (nombre o propia)
            try:
                with LOCK:
                    f, _ = galeria.build(OUT / "galeria", Path(IMAGES), body.get("palette", "default"), body.get("design", "anura"), nav=False)
                return self._send(200, f.read_bytes(), "text/html")
            except Exception as e:  # noqa: BLE001
                return self._send(400, {"error": str(e)})
        if path == "/v1/uploads":
            name = re.sub(r"[^\w.-]+", "_", str(body.get("name", "archivo")))[:60]
            try:
                raw = base64.b64decode(body.get("data", ""), validate=True)
            except Exception:  # noqa: BLE001
                return self._send(400, {"error": "data debe ir en base64"})
            kind = {b"\x89PNG": ".png", b"\xff\xd8\xff": ".jpg", b"GIF8": ".gif", b"RIFF": ".webp"}
            ext = next((e for sig_, e in kind.items() if raw.startswith(sig_)), ".csv" if name.lower().endswith(".csv") and b"\x00" not in raw[:4096] else None)
            if not ext:
                return self._send(415, {"error": "solo PNG, JPG, GIF, WEBP o CSV", "ajuste": "convierte el archivo y vuelve a subirlo"})
            dest = Path(IMAGES) / "uploads"
            dest.mkdir(parents=True, exist_ok=True)
            fn = f"{hashlib.sha256(raw).hexdigest()[:16]}_{Path(name).stem[:40]}{ext}"
            (dest / fn).write_bytes(raw)
            return self._send(201, {"src": f"uploads/{fn}", "bytes": len(raw), "nota": "usa src en un bloque image; añade autor y licencia si la imagen no es tuya"})
        if path == "/v1/commons/import":
            title = str(body.get("title", "")).removeprefix("File:").strip()
            if not title:
                return self._send(400, {"error": "falta title (nombre del archivo en Commons)"})
            try:                                                   # se vuelve a consultar Commons: no se confía en URLs del cliente
                params = {"action": "query", "format": "json", "titles": f"File:{title}", "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 1400}
                with urllib.request.urlopen(urllib.request.Request(commons.API + "?" + urllib.parse.urlencode(params), headers=commons.UA), timeout=30) as r:
                    found = commons.parse(json.load(r))
                if not found:
                    return self._send(404, {"error": "no está en Commons o su licencia no es libre (CC0, dominio público, CC BY, CC BY-SA)"})
                it = found[0]
                if urllib.parse.urlsplit(it["thumb"]).hostname != "upload.wikimedia.org":
                    return self._send(400, {"error": "origen de imagen no permitido"})
                dest = Path(IMAGES) / "commons"
                dest.mkdir(parents=True, exist_ok=True)
                fn = re.sub(r"[^\w.-]+", "_", it["titulo"])[:80]
                fn += "" if fn.lower().endswith((".jpg", ".jpeg", ".png")) else ".jpg"
                if not (dest / fn).exists():
                    with urllib.request.urlopen(urllib.request.Request(it["thumb"], headers=commons.UA), timeout=60) as r:
                        (dest / fn).write_bytes(r.read())
                    import csv
                    cp = Path(IMAGES) / "creditos.csv"
                    new = not cp.exists()
                    with cp.open("a", encoding="utf-8", newline="") as fh:
                        w = csv.writer(fh)
                        if new:
                            w.writerow(["archivo", "especie_o_tema", "que_muestra", "url_commons", "autor", "licencia"])
                        w.writerow([f"commons/{fn}", body.get("tema") or title, it["descripcion"], it["url_commons"], it["autor"], it["licencia"]])
                return self._send(201, {"src": f"commons/{fn}", "autor": it["autor"], "licencia": it["licencia"], "url_commons": it["url_commons"]})
            except Exception as e:  # noqa: BLE001
                return self._send(502, {"error": f"Wikimedia Commons no respondió: {str(e)[:120]}"})
        if path == "/v1/batch":
            docs = body.get("documents") or []
            if not isinstance(docs, list) or not 1 <= len(docs) <= 50:
                return self._send(400, {"error": "documents: lista de 1 a 50 contratos"})
            return self._send(202, {"jobs": [enqueue(d) for d in docs]})
        if path == "/v1/designs/import":
            if not self._admin():
                return self._send(401, {"error": "solo administración", "ajuste": "usa la clave de servidor/data/admin-key.txt"})
            try:
                code, rep = import_design(body)
            except Exception as e:  # noqa: BLE001
                code, rep = 400, {"error": str(e)[:300]}
            return self._send(code, rep)
        mm = re.fullmatch(r"/v1/designs/([\w-]+)/publish", path)
        if mm:
            if not self._admin():
                return self._send(401, {"error": "solo administración"})
            did = mm.group(1)
            m = manifest(did)
            m["estado"] = "publicado"
            if body.get("version"):
                m["version"] = str(body["version"])
            (render.HERE / "designs" / did / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
            return self._send(200, {"id": did, "estado": "publicado", "version": m["version"]})
        mm = re.fullmatch(r"/v1/jobs/(\w+)/(publish|patch)", path)
        if mm:
            job, what = mm.groups()
            src = OUT / f"{job}.json"
            if not src.exists():
                return self._send(404, {"error": "trabajo no encontrado o vencido"})
            doc = json.loads(src.read_text(encoding="utf-8"))
            if what == "patch":
                antes = json.loads(json.dumps(doc))
                try:
                    doc = apply_patch(doc, body.get("ops") or [])
                    if body.get("motivo"):
                        registrar_patch(antes, doc, body.get("ops") or [], str(body["motivo"]), job, body.get("origen", "modelo"))
                except (ValueError, IndexError, KeyError, TypeError) as e:
                    if isinstance(e, KeyError) and str(e).strip("'") == "document":
                        return self._send(409, {"error": "ese trabajo no tiene un documento válido que parchear", "ajuste": "vuelve a llamar create_pdf/create_pptx con markdown"})
                    return self._send(400, {"error": str(e), "ajuste": "ops: [{op:'set', section:'s1', block:0, value:{type:'p', text:'…'}}]"})
                if body.get("format"):
                    doc["format"] = body["format"]
                if doc.get("format") in render_video.FORMATS:
                    return self._send(202, with_urls(enqueue(doc)))
                code, rep = render_doc(doc)
                return self._send(code, with_urls(rep))
            rep = json.loads((OUT / f"{job}.informe.json").read_text(encoding="utf-8")) if (OUT / f"{job}.informe.json").exists() else {}
            if rep.get("estado") in (None, "rechazado", "fallido"):
                return self._send(409, {"error": "solo se publican trabajos terminados"})
            fmt = doc.get("format", "pdf-a4")
            ext = "mp4" if fmt in render_video.FORMATS else DOC_FORMATS.get(fmt, "pdf")
            g = DATA / f"galeria-{doc.get('design', 'anura')}.json"
            items = [x for x in (json.loads(g.read_text(encoding="utf-8")) if g.exists() else []) if x["job"] != job]
            items.insert(0, {"job": job, "titulo": str(body.get("title") or doc.get("meta", {}).get("title", ""))[:120], "formato": fmt, "paleta": doc.get("palette", "default"),
                             "variantes": (doc.get("options") or {}).get("variants") or "auto", "fecha": time.strftime("%Y-%m-%d"), "archivo": f"/v1/files/{job}.{ext}"})
            g.write_text(json.dumps(items[:200], ensure_ascii=False, indent=1), encoding="utf-8")
            return self._send(200, {"publicado": True, "galeria": f"/v1/designs/{doc.get('design', 'anura')}/gallery"})
        if path != "/v1/render":
            return self._send(404, {"error": "ruta no encontrada", "ajuste": "mira GET /v1/openapi.json"})
        if body.get("format") in render_video.FORMATS:                      # video: asíncrono, cola propia
            st = enqueue(body)
            if st["estado"] == "ok":
                return self._send(200, with_urls(json.loads((OUT / f"{st['job']}.informe.json").read_text(encoding="utf-8"))))
            return self._send(202, st)
        code, rep = render_doc(body)
        if md_av:
            rep["avisos"] = list(rep.get("avisos", [])) + md_av
        self._send(code, with_urls(rep))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")      # Windows: la consola cp1252 no acepta ✔ → ·
    ap = argparse.ArgumentParser()
    ap.add_argument("--puerto", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--imagenes", default="imagenes")
    a = ap.parse_args()
    IMAGES = a.imagenes
    print(f"API en http://{a.host}:{a.puerto}  ·  clave de administración en {DATA / 'admin-key.txt'}")
    ThreadingHTTPServer((a.host, a.puerto), H).serve_forever()
