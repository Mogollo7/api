#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Director creativo local: un modelo pequeño (Ollama / LM Studio, API estilo OpenAI) usa las herramientas de myStyle para crear PDF, PPTX o video.
"""Uso (con la API encendida: python servidor/api.py y Ollama corriendo):

    python servidor/director.py "Informe de ventas del trimestre con 4 cifras y un gráfico de barras" --formato pdf
    python servidor/director.py --md contenido/ejemplo_markdown.md            # el contenido ya está escrito: el modelo solo elige estilo si falta
    python servidor/director.py "Portada con esta imagen" --imagen foto.png     # un modelo de visión describe la imagen primero
    python servidor/director.py --semana                                        # cuántas veces hubo que recurrir a Claude, por semana

Regla de escalado: si el motor rechaza el resultado 3 veces seguidas, el director se detiene y deja un informe para Claude en salida/director/escalado_*.md;
las correcciones se guardan (POST /v1/corrections) para que el caso no vuelva a llegar ahí. Config del modelo: servidor/config/cerebro.json.
"""
import argparse
import base64
import json
import mimetypes
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import herramientas  # noqa: E402

CONFIG = HERE / "config" / "cerebro.json"
METRICAS = HERE / "data" / "director.jsonl"
SALIDA = HERE.parent / "salida" / "director"
DEFECTO = {"endpoint": "http://127.0.0.1:11434/v1", "modelo": "qwen2.5-coder:7b", "modelo_vision": "", "perfil": "minimo", "max_pasos": 12, "temperatura": 0.2,
           "mystyle_url": "http://127.0.0.1:8765", "mystyle_key": "", "rechazos_para_escalar": 3, "espera_s": 600}

SISTEMA = """Eres el director creativo de myStyle. Creas documentos con herramientas. No inventes datos: cifra sin dato = "dato pendiente".
Pasos: 1) list_recipes (q = lo que te piden): si hay una receta parecida, llama create_from_recipe con SOLO los huecos que quieras cambiar (recipe_get te los muestra);
2) si ninguna receta sirve: escribe el contenido en MARKDOWN y llama a la herramienta del formato con el campo markdown
(PDF create_pdf · PowerPoint create_pptx · video create_video · Word y Excel render con format docx-a4 o xlsx);
3) si estado es ok o con_avisos, TERMINA (los avisos son informativos). Solo si hay errores usa patch con el job que devolvió la herramienta.
Markdown:
---
titulo: Título
objetivo: una frase
estilo: anura
---
## Una sección por hoja
- viñeta  /  1. paso
:::kpi
4 200 kWh | consumo mensual
:::
:::big
87 % | de satisfacción
:::
| Uso | kWh |
|---|---|
| A | 10 |
{grafico: bar}
> Una cita.
Llama UNA herramienta por turno, con JSON válido. Al terminar, di en 2 líneas qué hiciste y da la URL."""


def cargar_config(sobre=None):
    c = dict(DEFECTO)
    if CONFIG.exists():
        c.update(json.loads(CONFIG.read_text(encoding="utf-8")))
    c.update({k: v for k, v in (sobre or {}).items() if v not in (None, "")})
    return c


class Cerebro:
    """Cliente mínimo de /chat/completions (OpenAI, Ollama, LM Studio)."""

    def __init__(self, cfg):
        self.cfg, self.tokens_in, self.tokens_out = cfg, 0, 0

    def chat(self, mensajes, tools=None, modelo=None, json_mode=False):
        body = {"model": modelo or self.cfg["modelo"], "messages": mensajes, "temperature": self.cfg["temperatura"], "stream": False}
        if tools:
            body["tools"] = tools
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        req = urllib.request.Request(self.cfg["endpoint"].rstrip("/") + "/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json", "Authorization": "Bearer local"})
        try:
            with urllib.request.urlopen(req, timeout=self.cfg["espera_s"]) as r:
                d = json.loads(r.read())
        except urllib.error.URLError as e:
            raise SystemExit(f"No llego al modelo en {self.cfg['endpoint']} ({e.reason}). ¿Está corriendo Ollama? Prueba: ollama run {self.cfg['modelo']}")
        u = d.get("usage") or {}
        self.tokens_in += u.get("prompt_tokens", 0)
        self.tokens_out += u.get("completion_tokens", 0)
        return d["choices"][0]["message"]


def llamadas(msg):
    """tool_calls del mensaje; si el modelo pequeño escribió la llamada como texto (<tool_call>{…}</tool_call> o JSON suelto), la recupera."""
    if msg.get("tool_calls"):
        out = []
        for t in msg["tool_calls"]:
            a = t["function"].get("arguments") or {}
            out.append((t.get("id", "call"), t["function"]["name"], json.loads(a) if isinstance(a, str) else a))
        return out
    txt = msg.get("content") or ""
    nombres = {t["name"] for t in herramientas.TOOLS}
    dec, pos = json.JSONDecoder(), 0
    while True:
        k = txt.find("{", pos)
        if k < 0:
            return []
        try:
            o, fin = dec.raw_decode(txt, k)
        except ValueError:
            pos = k + 1
            continue
        if isinstance(o, dict) and o.get("name") in nombres:       # solo la PRIMERA: las siguientes dependen de su resultado
            a = o.get("arguments") or o.get("parameters") or {}
            return [("texto", o["name"], json.loads(a) if isinstance(a, str) else a)]
        pos = fin


def recorta(o, n=6000):
    s = o if isinstance(o, str) else json.dumps(o, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + f"…[recortado {len(s) - n} caracteres]"


def fallo(r):
    return isinstance(r, dict) and (r.get("estado") in ("rechazado", "fallido") or bool(r.get("errores")) or ("error" in r and not r.get("job")))


def escalar(tarea, motivo, ultimos, cfg):
    SALIDA.mkdir(parents=True, exist_ok=True)
    f = SALIDA / f"escalado_{time.strftime('%Y%m%d_%H%M%S')}.md"
    f.write_text(f"# Para Claude: el modelo local no lo resolvió\n\n**Tarea:** {tarea}\n\n**Motivo:** {motivo}\n\n**Modelo:** {cfg['modelo']}\n\n"
                 f"## Últimos resultados del motor\n```json\n{recorta(ultimos, 5000)}\n```\n\n"
                 "## Qué se pide\nRevisa qué regla viola, explica por qué y propone la corrección (documento o parche). Guarda el cambio con save_correction (origen: claude).\n", encoding="utf-8")
    return f


def mide(**r):
    METRICAS.parent.mkdir(exist_ok=True)
    with METRICAS.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"t": int(time.time()), "semana": time.strftime("%G-W%V"), **r}, ensure_ascii=False) + "\n")


def descarga(r, carpeta):
    """Baja los archivos del resultado (URL firmadas) a una carpeta."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    out = []
    for k in ("pdf", "pptx", "docx", "xlsx", "video"):
        u = r.get(k)
        if isinstance(u, str) and u.startswith("http"):
            dst = carpeta / f"{r.get('job', 'doc')}.{ {'video': 'mp4'}.get(k, k)}"
            urllib.request.urlretrieve(u, dst)
            out.append(str(dst))
    return out


def subir_imagenes(md, base, cliente):
    """Sube las imágenes locales que cita el Markdown y reescribe su src con el que devuelve la API."""
    def f(m):
        alt, src, cap = m.group(1), m.group(2), m.group(3)
        p = (base / src).resolve()
        if re.match(r"\w+://", src) or not p.is_file():
            return m.group(0)
        c, r = cliente.api("POST", "/v1/uploads", {"name": p.name, "data": base64.b64encode(p.read_bytes()).decode()})
        return f"![{alt}]({r['src']}" + (f' "{cap}"' if cap else "") + ")" if c == 201 else m.group(0)
    return re.sub(r'!\[(.*?)\]\((\S+?)(?:\s+"(.*?)")?\)', f, md)


def describe_imagen(ruta, cerebro):
    cfg = cerebro.cfg
    if not cfg.get("modelo_vision"):
        return "(no hay modelo de visión configurado en cerebro.json: modelo_vision)"
    mime = mimetypes.guess_type(str(ruta))[0] or "image/png"
    url = f"data:{mime};base64," + base64.b64encode(Path(ruta).read_bytes()).decode()
    m = cerebro.chat([{"role": "user", "content": [{"type": "text", "text": "Describe en 2 frases el diseño de esta imagen: tipo de pieza, disposición (qué va dónde), colores dominantes y tipografía."},
                                                    {"type": "image_url", "image_url": {"url": url}}]}], modelo=cfg["modelo_vision"])
    return (m.get("content") or "").strip()


def decidir_md(md, cerebro, cliente):
    """El contenido ya está escrito: si falta el estilo o el formato, el modelo elige UNA vez (JSON corto). Si no falta nada, no se gasta ni un token."""
    meta = {}
    m = re.match(r"\s*---\s*\n(.*?)\n---", md, re.S)
    if m:
        for ln in m.group(1).splitlines():
            k, _, v = ln.partition(":")
            meta[k.strip().lower()] = v.strip()
    if meta.get("estilo") and meta.get("formato"):
        return {}
    titulos = re.findall(r"^#{1,2}\s+(.*)", md, re.M)[:12]
    obj = meta.get("objetivo") or " ".join(titulos[:3])
    cand = cliente.llamar("search_library", {"q": obj, "tipo": "estilo", "n": 4})
    ops = ", ".join(f"{x['id']} ({x['descripcion'][:50]})" for x in cand) if isinstance(cand, list) else "anura"
    r = cerebro.chat([{"role": "user", "content": f"Contenido: «{obj}». Secciones: {', '.join(titulos)}.\nEstilos disponibles: {ops}.\nFormatos: pdf, pptx, docx, xlsx, video.\n"
                       'Elige. Responde SOLO JSON: {"estilo":"<id>","formato":"<formato>"}'}], json_mode=True)
    try:
        o = json.loads(re.search(r"\{.*\}", r.get("content") or "{}", re.S).group(0))
    except (ValueError, AttributeError):
        return {}
    fmt = {"pdf": "pdf-a4", "pptx": "pptx-16x9", "docx": "docx-a4", "xlsx": "xlsx", "video": "video-16x9"}.get(str(o.get("formato", "")).lower())
    return {k: v for k, v in {"design": o.get("estilo") if o.get("estilo") in {x["id"] for x in cand} else None, "format": fmt}.items() if v}


def ejecuta_md(ruta, cfg, cerebro, cliente, formato=None, estilo=None):
    p = Path(ruta)
    md = subir_imagenes(p.read_text(encoding="utf-8"), p.parent, cliente)
    dec = decidir_md(md, cerebro, cliente) if not (formato and estilo) else {}
    body = {"markdown": md, **dec, **({"format": formato} if formato else {}), **({"design": estilo} if estilo else {})}
    fmt = body.get("format")
    if not fmt:
        m = re.search(r"^formato:\s*(\S+)", md, re.M)
        fmt = herramientas.FORMATS_MD.get(m.group(1).lower()) if m else None
    c, r = cliente.api("POST", "/v1/render", body)
    r = cliente._espera(c, r) if c == 202 else cliente.absolute(cliente.short(r))
    return r, dec


def bucle(tarea, cfg, cerebro, cliente, extra="", trace=None):
    """Bucle de herramientas con escalado. Devuelve (resultado final, pasos, rechazos, motivo_escalado)."""
    perfil_min = cfg["perfil"] == "minimo"
    tools = herramientas.openai_tools(core_only=perfil_min)
    msgs = [{"role": "system", "content": SISTEMA}, {"role": "user", "content": tarea + (f"\n\nImagen de referencia: {extra}" if extra else "")}]
    rech, ultimo, ult_resultados = 0, None, []
    for paso in range(1, cfg["max_pasos"] + 1):
        m = cerebro.chat(msgs, tools)
        msgs.append({k: v for k, v in m.items() if k in ("role", "content", "tool_calls")} | {"role": "assistant"})
        calls = llamadas(m)
        if not calls:
            return ultimo, paso, rech, None, (m.get("content") or "").strip()
        for cid, name, args in calls:
            try:
                r = cliente.llamar(name, args)
            except Exception as e:  # noqa: BLE001
                r = {"error": str(e)[:300]}
            print(f"  · {name} → {str(r)[:110]}")
            (SALIDA / "ultimo_resultado.json").parent.mkdir(parents=True, exist_ok=True)
            (SALIDA / "ultimo_resultado.json").write_text(json.dumps({"tool": name, "args": args, "resultado": r}, ensure_ascii=False, indent=1)[:60000], encoding="utf-8")
            ult_resultados = (ult_resultados + [r])[-3:]
            if trace is not None:
                trace.append({"tool": name, "args": {k: (v if len(str(v)) < 200 else str(v)[:200] + "…") for k, v in args.items()} if isinstance(args, dict) else str(args)[:200], "resultado": r if not isinstance(r, (dict, list)) else (herramientas.Cliente.short(r) if isinstance(r, dict) else r[:3])})
            if name.startswith(("create_", "render", "patch")):
                ultimo = r if isinstance(r, dict) else ultimo
                rech = rech + 1 if fallo(r) else 0
            msgs.append({"role": "tool", "tool_call_id": cid, "name": name, "content": recorta(r)} if cid != "texto" else {"role": "user", "content": f"Resultado de {name}: {recorta(r)}"})
        if rech >= cfg["rechazos_para_escalar"]:
            return ultimo, paso, rech, f"el motor rechazó el resultado {rech} veces seguidas", None
    return ultimo, cfg["max_pasos"], rech, "se agotaron los pasos sin un resultado válido", None


def semana():
    if not METRICAS.exists():
        return print("Aún no hay corridas registradas.")
    por = {}
    for ln in METRICAS.read_text(encoding="utf-8").splitlines():
        r = json.loads(ln)
        s = por.setdefault(r["semana"], {"corridas": 0, "escaladas": 0, "tokens_in": 0, "tokens_out": 0})
        s["corridas"] += 1
        s["escaladas"] += 1 if r.get("escalado") else 0
        s["tokens_in"] += r.get("tokens_in", 0)
        s["tokens_out"] += r.get("tokens_out", 0)
    print("semana     corridas  a Claude  tokens locales (entrada/salida)")
    for k in sorted(por):
        v = por[k]
        print(f"{k}   {v['corridas']:>7}  {v['escaladas']:>8}  {v['tokens_in']}/{v['tokens_out']}")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tarea", nargs="?", help="qué crear, en palabras")
    ap.add_argument("--md", help="archivo Markdown con el contenido ya escrito")
    ap.add_argument("--imagen", help="imagen de referencia (necesita modelo_vision)")
    ap.add_argument("--formato", help="pdf | pptx | docx | xlsx | video")
    ap.add_argument("--estilo", help="id del diseño (anura, editorial…)")
    ap.add_argument("--modelo")
    ap.add_argument("--perfil", choices=["minimo", "completo"])
    ap.add_argument("--descargar", help="carpeta donde guardar los archivos (por defecto salida/director)")
    ap.add_argument("--revisar", action="store_true", help="al final pregunta si quedó bien; si no, intenta corregir 2 veces y luego escala")
    ap.add_argument("--semana", action="store_true")
    a = ap.parse_args()
    if a.semana:
        return semana()
    if not (a.tarea or a.md):
        ap.error("pasa una tarea o --md")
    cfg = cargar_config({"modelo": a.modelo, "perfil": a.perfil})
    cliente = herramientas.Cliente(cfg["mystyle_url"], cfg["mystyle_key"])
    cerebro = Cerebro(cfg)
    fmt_pedido = herramientas.FORMATS_MD.get((a.formato or "").lower()) if a.formato else None
    t0, escalado, motivo, pasos, rech = time.time(), None, None, 0, 0
    try:
        if a.md:
            r, dec = ejecuta_md(a.md, cfg, cerebro, cliente, fmt_pedido, a.estilo)
            texto, tarea = f"Markdown {a.md} " + (f"· el modelo eligió {dec}" if dec else "· sin gastar tokens del modelo"), f"md:{a.md}"
        else:
            extra = describe_imagen(a.imagen, cerebro) if a.imagen else ""
            tarea = a.tarea + (f" (formato: {a.formato})" if a.formato else "") + (f" (estilo: {a.estilo})" if a.estilo else "")
            r, pasos, rech, motivo, texto = bucle(tarea, cfg, cerebro, cliente, extra)
    except urllib.error.URLError as e:
        raise SystemExit(f"No llego a la API de myStyle en {cfg['mystyle_url']} ({e.reason}). Enciéndela: python servidor/api.py")
    if motivo:
        f = escalar(a.tarea or a.md, motivo, r, cfg)
        escalado = str(f)
        print(f"\n⚠ Escalado a Claude: {motivo}.\n  Informe listo para pegarle: {f}")
    elif isinstance(r, dict) and r.get("job"):
        print("\n✔", texto or "Listo.")
        for k in ("pdf", "pptx", "docx", "xlsx", "video"):
            if r.get(k):
                print(f"  {k}: {r[k]}")
        if r.get("avisos"):
            print(f"  avisos: {len(r['avisos'])} (revisa con --revisar o con patch)")
        print("  guardado en:", *descarga(r, a.descargar or SALIDA))
        if a.revisar:
            print("\n¿Quedó bien? Enter = sí, o escribe qué no te gusta:")
            c = sys.stdin.readline().strip()
            for intento in range(2) if c else []:
                r, _, _, mot2, _ = bucle(f"El usuario dice: «{c}». Corrige el trabajo {r['job']} con patch (no lo rehagas).", cfg, cerebro, cliente)
                print("  ↻ intento", intento + 1, "→", (r or {}).get("estado"))
                if not mot2 and not fallo(r):
                    break
            else:
                if c:
                    f = escalar(c, "el usuario marcó que no quedó bien y el modelo local no lo corrigió en 2 intentos", r, cfg)
                    escalado = str(f)
                    print("⚠ Escalado a Claude:", f)
    else:
        print("\nSin resultado:", texto or r)
    mide(tarea=str(a.tarea or a.md)[:80], modelo=cfg["modelo"], pasos=pasos, rechazos=rech, escalado=bool(escalado), tokens_in=cerebro.tokens_in, tokens_out=cerebro.tokens_out,
         segundos=round(time.time() - t0, 1), ok=bool(isinstance(r, dict) and r.get("job") and not motivo))


if __name__ == "__main__":
    main()
