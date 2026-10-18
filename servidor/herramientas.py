#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Herramientas del agente: UNA definición que sirve al servidor MCP, a GET /v1/tools (function calling estilo OpenAI) y al bucle local (director.py).
"""Cualquier cerebro (Qwen en Ollama, Codex, Claude) usa las mismas herramientas. Cada una es una llamada HTTP a la API; el motor valida y el agente corrige con `avisos`.

    python servidor/herramientas.py            # lista las herramientas
    python servidor/herramientas.py openai     # esquemas para Ollama / LM Studio
    python servidor/herramientas.py call list_recipes '{"q":"informe de ventas"}'     # ejecuta una herramienta desde la terminal
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

FORMATS_MD = {"pdf": "pdf-a4", "pptx": "pptx-16x9", "docx": "docx-a4", "word": "docx-a4", "xlsx": "xlsx", "excel": "xlsx", "web": "web-animada", "video": "video-16x9", "video-vertical": "video-9x16"}
FORMATS = ["pdf-a4", "pptx-16x9", "docx-a4", "xlsx", "web-animada", "video-16x9", "video-9x16"]
DOC = {"type": "object", "description": "Documento en el contrato JSON de myStyle (usa library_get o get_prompt para ver los campos)."}
MD = {"type": "string", "description": "Alternativa a document: el contenido ya escrito en Markdown (cabecera --- titulo/formato/estilo ---, # ## listas tablas). Gasta menos tokens."}


def T(name, desc, props, req=(), core=True):
    return {"name": name, "description": desc, "parameters": {"type": "object", "properties": props, "required": list(req)}, "core": core}


TOOLS = [
    T("list_recipes", "EMPIEZA AQUÍ. Busca recetas (documentos completos con huecos) o ingredientes (piezas sueltas) para lo que te piden. Con una receta solo rellenas huecos y sale un documento completo.",
      {"q": {"type": "string", "description": "qué documento quieres, en palabras"}, "tipo": {"enum": ["receta", "ingrediente"]}, "n": {"type": "integer"}}, ["q"]),
    T("recipe_get", "Los huecos de una receta o ingrediente (qué escribir, máximos y valor por defecto). Es corto: no devuelve la plantilla.", {"id": {"type": "string"}}, ["id"]),
    T("create_from_recipe", "Crea el archivo desde una receta: pasas SOLO los huecos que quieras cambiar (el resto queda con su valor por defecto). Gasta ~100–300 tokens.",
      {"receta": {"type": "string"}, "valores": {"type": "object", "description": "{hueco: valor}; las listas van como [[valor, etiqueta, nota], …]"},
       "formato": {"enum": ["pdf", "pptx", "docx", "xlsx", "web", "video"], "description": "si no lo dices, el de la receta"}, "estilo": {"type": "string", "description": "id del diseño; si no, el de la receta"}, "paleta": {"type": "string"}, "portada": {"type": "string", "description": "id de variante de portada, p. ej. CV-3 (mira list_recipes/search_library tipo plantilla)"}, "divisor": {"type": "string"}}, ["receta"]),
    T("compose", "Arma un documento juntando ingredientes en orden (cada uno con sus huecos). Para lo que ninguna receta cubre.",
      {"ingredientes": {"type": "array", "items": {"type": "object"}, "description": "[{id, valores}]"}, "titulo": {"type": "string"}, "objetivo": {"type": "string"},
       "formato": {"enum": ["pdf", "pptx", "docx", "xlsx", "web", "video"]}, "estilo": {"type": "string"}, "paleta": {"type": "string"}}, ["ingredientes", "titulo"], core=False),
    T("search_library", "Busca estilos, plantillas, componentes y animaciones parecidos a lo que describes. Úsala ANTES de crear algo nuevo.",
      {"q": {"type": "string", "description": "qué buscas, en palabras"}, "tipo": {"enum": ["receta", "ingrediente", "recurso", "estilo", "plantilla", "componente", "animacion"]}, "n": {"type": "integer"}}, ["q"]),
    T("library_get", "Ficha completa de una entrada de la biblioteca (parámetros, ejemplo correcto y error típico). Para un bloque: id = p, h, list, table, chart, kpi…",
      {"id": {"type": "string"}}, ["id"], core=False),
    T("get_prompt", "Reglas cortas de un diseño para escribir el documento (longitudes, bloques, paleta).",
      {"design": {"type": "string", "description": "anura | editorial"}, "format": {"enum": FORMATS}}, ["design"], core=False),
    T("create_pdf", "Crea un PDF A4 desde un documento. Devuelve la URL y `avisos`: corrígelos con patch.", {"document": DOC, "markdown": MD, "design": {"type": "string"}}),
    T("create_pptx", "Crea una presentación PowerPoint 16:9 editable desde un documento.", {"document": DOC, "markdown": MD, "design": {"type": "string"}}),
    T("create_video", "Crea un video MP4 desde un documento (puede tardar minutos).", {"document": DOC, "markdown": MD, "design": {"type": "string"}, "vertical": {"type": "boolean", "description": "9:16 en vez de 16:9"}}),
    T("render", "Crea un archivo Word (docx-a4), Excel (xlsx) o una página web animada con anime.js (web-animada) desde el contenido. Para PDF, PowerPoint y video usa create_pdf, create_pptx o create_video.", {"document": DOC, "markdown": MD, "design": {"type": "string"}, "format": {"enum": ["docx-a4", "xlsx", "web-animada"]}}, ["format"]),
    T("audit", "Audita un PDF: márgenes, superposición, contraste y fuentes. Pasa `job` (de un create_*) o `pdf_base64`.",
      {"job": {"type": "string"}, "pdf_base64": {"type": "string"}}, core=False),
    T("check_quality", "Revisa un trabajo ya creado: ortografía en español y accesibilidad del PDF (título, idioma, etiquetas, fuentes). Pasa `job` o un `texto`.",
      {"job": {"type": "string"}, "texto": {"type": "string"}}, core=False),
    T("create_resource", "Genera un recurso gráfico por código: patrón de puntos, rejilla, líneas, ondas, degradado, ruido, marco o un icono (Lucide). Devuelve `src` para un bloque image.",
      {"tipo": {"enum": ["puntos", "rejilla", "lineas", "ondas", "degradado", "ruido", "marco", "icono"]}, "id": {"type": "string", "description": "nombre en minúsculas"}, "color": {"type": "string", "description": "#rrggbb"},
       "color2": {"type": "string", "description": "fondo #rrggbb"}, "tam": {"type": "integer"}, "icono": {"type": "string", "description": "nombre Lucide, p. ej. leaf, chart-bar"}}, ["tipo", "id"], core=False),
    T("analyze_reference", "Lee una imagen o PDF de referencia que dio el usuario y propone el estilo: modo claro/oscuro, acento, paleta y el comando exacto de la fábrica. Empieza aquí para crear un estilo desde una imagen.",
      {"ruta": {"type": "string", "description": "ruta local de la imagen/PDF"}, "base64": {"type": "string"}, "id": {"type": "string", "description": "id del estilo nuevo"}}, core=False),
    T("create_style", "Crea un estilo completo (paleta, piel, 4 variantes) con la fábrica y lo valida (10 chequeos). Si dice ✘, ajusta y repite. Es de administración: el cliente local usa la clave solo.",
      {"id": {"type": "string"}, "acento": {"type": "string", "description": "#rrggbb"}, "piel": {"enum": ["suave", "recta", "redonda", "editorial"]}, "modo": {"enum": ["claro", "oscuro"]}, "nombre": {"type": "string"}}, ["id", "acento"], core=False),
    T("create_variant", "Añade una portada o divisor nuevo a un estilo (fondo acento, claro u oscuro).",
      {"estilo": {"type": "string"}, "tipo": {"enum": ["portada", "divisor"]}, "fondo": {"enum": ["acento", "claro", "oscuro"]}, "nuevo": {"type": "string", "description": "id, p. ej. CV-3 o DV-C"}}, ["estilo", "tipo", "fondo", "nuevo"], core=False),
    T("validate_style", "Lista de revisión de un estilo (10 chequeos: paleta, contraste, plantillas, muestra corta y larga).", {"estilo": {"type": "string"}}, ["estilo"], core=False),
    T("screenshot", "Captura para MIRAR lo creado: una página de un PDF (job + pagina) o una web local (url). Devuelve la URL de un PNG que puedes abrir.",
      {"job": {"type": "string"}, "pagina": {"type": "integer"}, "url": {"type": "string", "description": "http://127.0.0.1…"}, "completa": {"type": "boolean"}}, core=False),
    T("patch", "Corrige bloques de un trabajo sin reenviarlo. ops: [{op:'set'|'insert'|'delete', section:'s1', block:'<id del bloque o índice>', value:{…}}]. `motivo` queda como corrección aprendida.",
      {"job": {"type": "string"}, "ops": {"type": "array", "items": {"type": "object"}}, "format": {"enum": FORMATS}, "motivo": {"type": "string"}}, ["job", "ops"]),
    T("save_style", "Guarda un estilo o plantilla nueva en la biblioteca. Si ya existe, pregunta al usuario antes de pasar sobrescribir:true.",
      {"entry": {"type": "object", "description": "{tipo:'estilo'|'plantilla', id, nombre, descripcion, tags:[], paleta?, fuentes?}"}, "sobrescribir": {"type": "boolean"}}, ["entry"], core=False),
    T("save_correction", "Registra una corrección aceptada (qué estaba mal y cómo quedó) para que no se repita.",
      {"seccion": {"type": "string", "description": "p. ej. s1.kpi-ab12c o portada.titulo"}, "antes": {}, "despues": {}, "motivo": {"type": "string"}, "design": {"type": "string"}}, ["motivo"], core=False),
    T("find_corrections", "Busca correcciones parecidas ya aprendidas, para usarlas como ejemplo.", {"q": {"type": "string"}, "n": {"type": "integer"}}, ["q"], core=False),
    T("job_status", "Estado e informe de un trabajo (video en cola o en curso).", {"job": {"type": "string"}}, ["job"], core=False),
]


def _params(t, core_only):
    """Perfil mínimo: los create_* solo ofrecen `markdown` (un modelo pequeño escribe mejor Markdown que el contrato JSON completo)."""
    pr = t["parameters"]
    if core_only and "markdown" in pr["properties"] and "document" in pr["properties"]:
        pr = {**pr, "properties": {k: v for k, v in pr["properties"].items() if k != "document"}, "required": list(dict.fromkeys(pr["required"] + ["markdown"]))}
    return pr


def openai_tools(core_only=False):
    return [{"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": _params(t, core_only)}} for t in TOOLS if t["core"] or not core_only]


def mcp_tools():
    return [{"name": t["name"], "description": t["description"], "inputSchema": t["parameters"]} for t in TOOLS]


class Cliente:
    """Llama a la API de myStyle. BASE y KEY salen del entorno (MYSTYLE_URL, MYSTYLE_KEY) o de los argumentos."""

    def __init__(self, base=None, key=None):
        self.base = (base or os.environ.get("MYSTYLE_URL", "http://127.0.0.1:8765")).rstrip("/")
        self.key = key if key is not None else os.environ.get("MYSTYLE_KEY", "")
        if not self.key and ("127.0.0.1" in self.base or "localhost" in self.base):       # en local, la clave de administración (data/admin-key.txt) se lee sola
            f = Path(__file__).resolve().parent / "data" / "admin-key.txt"
            self.key = f.read_text(encoding="utf-8").strip() if f.exists() else ""

    def api(self, method, path, body=None):
        h = {"Content-Type": "application/json"}
        if self.key:
            h["Authorization"] = f"Bearer {self.key}"
        req = urllib.request.Request(self.base + path, json.dumps(body).encode() if body is not None else None, h, method=method)
        try:
            with urllib.request.urlopen(req, timeout=900) as r:
                data, code, ctype = r.read(), r.status, r.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            data, code, ctype = e.read(), e.code, e.headers.get("Content-Type", "")
        except urllib.error.URLError:
            return 503, {"error": f"la API no responde en {self.base}", "ajuste": "arráncala: python servidor/api.py --puerto 8765 --imagenes imagenes (y revisa con python servidor/conectar.py comprobar)"}
        return code, (json.loads(data) if "json" in ctype else data.decode("utf-8", "replace"))

    def absolute(self, o):
        """Las rutas /v1/files/… firmadas pasan a URL completas para que el usuario pueda abrirlas."""
        if isinstance(o, dict):
            return {k: self.absolute(v) for k, v in o.items()}
        if isinstance(o, list):
            return [self.absolute(v) for v in o]
        return self.base + o if isinstance(o, str) and o.startswith("/v1/") else o

    @staticmethod
    def short(rep):
        keep = ("estado", "job", "formato", "pdf", "pptx", "docx", "xlsx", "video", "proyecto", "paginas", "diapositivas", "duracion_s", "errores", "avisos", "auditoria",
                "imagenes_necesarias", "estado_url", "error", "ajuste", "ids")
        return {k: rep[k] for k in keep if k in rep and rep[k] not in (None, [], {})} if isinstance(rep, dict) else rep

    def _espera(self, code, rep):
        t0 = time.time()
        while code == 202 and time.time() - t0 < 600:      # video: espera hasta 10 min; si no, devuelve el job
            time.sleep(4)
            code, rep = self.api("GET", f"/v1/jobs/{rep['job']}")
        return self.absolute(self.short(rep))

    ALIAS = {"web": "web-animada", "pdf": "pdf-a4", "pptx": "pptx-16x9", "docx": "docx-a4", "word": "docx-a4", "excel": "xlsx", "video": "video-16x9"}

    def llamar(self, name, a):
        a = dict(a or {})
        for k in ("format", "formato"):                         # los modelos pequeños dicen «pdf» en vez de «pdf-a4»
            if isinstance(a.get(k), str):
                a[k] = self.ALIAS.get(a[k].lower(), a[k])
        if name in ("patch", "audit", "job_status", "check_quality") and a.get("job") and not re.fullmatch(r"[0-9a-f]{12}", str(a["job"])):
            return {"error": f"job '{str(a['job'])[:40]}' no es un id de trabajo", "ajuste": "usa el campo `job` (12 caracteres hexadecimales) que devolvió create_pdf, create_pptx, create_video o render"}
        if name == "list_recipes":
            r = self.api("GET", "/v1/recipes?" + urllib.parse.urlencode({k: v for k, v in {"q": a.get("q", ""), "tipo": a.get("tipo"), "n": a.get("n", 4)}.items() if v}))[1]
            return [{"id": x["id"], "tipo": x["tipo"], "descripcion": str(x.get("descripcion", ""))[:110]} for x in r] if isinstance(r, list) else r      # corto: ahorra tokens
        if name == "recipe_get":
            return self.api("GET", "/v1/recipes/" + urllib.parse.quote(str(a.get("id", ""))))[1]
        if name in ("create_from_recipe", "compose"):
            body = {k: a[k] for k in ("receta", "valores", "ingredientes", "paleta", "portada", "divisor") if a.get(k)}
            if a.get("estilo"):
                body["design"] = a["estilo"]
            if a.get("formato"):
                body["format"] = self.ALIAS.get(str(a["formato"]).lower(), a["formato"])
            if name == "compose":
                body["meta"] = {k: a[k] for k in ("titulo", "objetivo") if a.get(k)}
            return self._espera(*self.api("POST", "/v1/render", body))
        if name == "search_library":
            return self.api("GET", "/v1/library?" + urllib.parse.urlencode({k: v for k, v in {"q": a.get("q", ""), "tipo": a.get("tipo"), "n": a.get("n", 5)}.items() if v}))[1]
        if name == "library_get":
            return self.api("GET", "/v1/library/" + urllib.parse.quote(str(a["id"])))[1]
        if name == "get_prompt":
            return self.api("POST", "/v1/prompt", {"design": a["design"], "format": a.get("format", "pdf-a4"), "mode": "A", "short": True})[1]
        if name in ("create_pdf", "create_pptx", "create_video", "render"):
            fmt = {"create_pdf": "pdf-a4", "create_pptx": "pptx-16x9", "create_video": "video-9x16" if a.get("vertical") else "video-16x9"}.get(name) or a.get("format", "pdf-a4")
            if a.get("markdown"):
                doc = {"markdown": a["markdown"], **({"design": a["design"]} if a.get("design") else {})}
            else:
                doc = dict(a["document"]) if isinstance(a.get("document"), dict) else json.loads(a["document"])
            doc["format"] = fmt
            return self._espera(*self.api("POST", "/v1/render", doc))
        if name == "audit":
            return self.api("POST", "/v1/audit", {k: a[k] for k in ("job", "pdf_base64") if a.get(k)})[1]
        if name == "check_quality":
            return self.api("POST", "/v1/quality", {k: a[k] for k in ("job", "texto") if a.get(k)})[1]
        if name == "create_resource":
            return self.api("POST", "/v1/resources", a)[1]
        if name == "analyze_reference":
            return self.api("POST", "/v1/reference", a)[1]
        if name == "create_style":
            return self.api("POST", "/v1/styles", a)[1]
        if name == "create_variant":
            return self.api("POST", f"/v1/styles/{a.get('estilo', '')}/variants", {k: a[k] for k in ("tipo", "fondo", "nuevo") if k in a})[1]
        if name == "validate_style":
            return self.api("GET", f"/v1/styles/{a.get('estilo', '')}/validate")[1]
        if name == "screenshot":
            return self.absolute(self.api("POST", "/v1/screenshot", a)[1])
        if name == "patch":
            body = {"ops": a["ops"], **({"format": a["format"]} if a.get("format") else {}), **({"motivo": a["motivo"]} if a.get("motivo") else {})}
            return self._espera(*self.api("POST", f"/v1/jobs/{a['job']}/patch", body))
        if name == "save_style":
            return self.api("POST", "/v1/library", {"entry": a["entry"], "sobrescribir": bool(a.get("sobrescribir"))})[1]
        if name == "save_correction":
            return self.api("POST", "/v1/corrections", a)[1]
        if name == "find_corrections":
            return self.api("GET", "/v1/corrections?" + urllib.parse.urlencode({"q": a.get("q", ""), "n": a.get("n", 3)}))[1]
        if name == "job_status":
            return self.absolute(self.short(self.api("GET", f"/v1/jobs/{a['job']}")[1]))
        raise ValueError(f"herramienta desconocida: {name}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.argv[1:2] == ["call"]:           # para agentes con solo una terminal: python servidor/herramientas.py call <herramienta> '<json de argumentos>'
        print(json.dumps(Cliente().llamar(sys.argv[2], json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}), ensure_ascii=False, indent=1))
    elif sys.argv[1:] == ["openai"]:
        print(json.dumps(openai_tools(), ensure_ascii=False, indent=1))
    else:
        for t in TOOLS:
            print(f"{'●' if t['core'] else '○'} {t['name']:<17} {t['description'][:90]}")
        print("● = perfil mínimo (modelos pequeños)   ○ = solo en el perfil completo")
