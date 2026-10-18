# [CLAUDE-CONSTRUCTOR] Markdown → contrato JSON. El contenido llega escrito; el modelo solo decide cómo presentarlo (diseño, formato, variantes).
"""a_contrato(md) -> (documento, avisos)

Cabecera opcional entre `---` (clave: valor): portada y divisor (id de variante, p. ej. CV-3 y DV-C), video: duracion (s, máx. 120) · ritmo (bpm) · entrada (slide|fade-up|wipe-reveal), titulo, objetivo, formato (pdf|pptx|docx|xlsx|video|video-vertical), estilo (id del diseño), paleta, autor, fecha, asunto, vertical.
Cuerpo:
    # Título          el primero es el título del documento (si no hay `titulo:`); los siguientes abren una PARTE
    ## Sección        una hoja (o diapositiva)
    ### Subtítulo     bloque h
    párrafos, listas (- / 1.), tablas (| a | b |), ``` código ```, > cita (última línea «— autor»), > [!NOTA] aviso, ![pie](ruta "texto")
    {grafico: bar|hbar|pie|line}   en la línea siguiente a una tabla: la convierte en gráfico (1.ª columna etiquetas, 2.ª valores)
    :::motion / palabra | texto | seg … / :::   video con escenas explícitas (ver video_motion.py)
    :::kpi / valor | etiqueta | nota? / :::      tarjetas de cifras (2 a 4)
    :::big / valor | pie / :::  o  valor | unidad | pie     una cifra gigante
    <!-- hoja -->                                 fuerza una hoja nueva con el mismo titular («(cont.)»)
"""
import re

FORMATOS = {"pdf": "pdf-a4", "pptx": "pptx-16x9", "docx": "docx-a4", "word": "docx-a4", "xlsx": "xlsx", "excel": "xlsx", "web": "web-animada", "video": "video-16x9", "video-vertical": "video-9x16"}


def _fm(txt):
    """Separa la cabecera `--- … ---` del cuerpo."""
    m = re.match(r"\s*---\s*\n(.*?)\n---\s*(?:\n|$)", txt, re.S)
    if not m:
        return {}, txt
    meta = {}
    for ln in m.group(1).splitlines():
        k, _, v = ln.partition(":")
        if k.strip() and v.strip():
            meta[k.strip().lower()] = v.strip().strip("\"'")
    return meta, txt[m.end():]


def _num(s):
    t = re.sub(r"[^\d,.\-]", "", str(s)).replace(".", "").replace(",", ".") if "," in str(s) else re.sub(r"[^\d.\-]", "", str(s))
    try:
        return float(t)
    except ValueError:
        return None


def _corta(s, n):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[:n - 1].rsplit(" ", 1)[0].rstrip(",;:") + "…"


def _celdas(ln):
    return [c.strip() for c in ln.strip().strip("|").split("|")]


def a_contrato(txt, defecto=None):
    avisos = []
    meta, body = _fm(txt)
    defecto = defecto or {}
    lines = body.splitlines()
    titulo = meta.get("titulo") or ""
    parts, sec, blocks = [], None, None
    n_sec = 0

    def abre_parte(t):
        parts.append({"id": f"p{len(parts) + 1}", "title": _corta(t, 34), "desc": _corta(meta.get("objetivo") or t, 200), "sections": []})

    def abre_sec(t, cont=False):
        nonlocal sec, blocks, n_sec
        if not parts:
            abre_parte(meta.get("parte") or titulo or "Contenido")
        n_sec += 1
        sec = {"id": f"s{n_sec}", "title": _corta(t + (" (cont.)" if cont else ""), 90), "blocks": []}
        blocks = sec["blocks"]
        parts[-1]["sections"].append(sec)

    def add(b):
        if sec is None:
            abre_sec("Introducción")
        blocks.append(b)

    i, para = 0, []
    motion = []                                                         # escenas explícitas de video (:::motion), ver video_motion.py

    def flush():
        nonlocal para
        if para:
            add({"type": "p", "text": " ".join(x.strip() for x in para)})
            para = []

    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            flush(); i += 1; continue
        m = re.match(r"(#{1,6})\s+(.*)", s)
        if m:
            flush()
            n, t = len(m.group(1)), m.group(2).strip()
            if n == 1:
                if not titulo:
                    titulo = t
                else:
                    abre_parte(t); sec = None
            elif n == 2:
                abre_sec(t)
            else:
                add({"type": "h", "text": _corta(t, 80)})
            i += 1; continue
        if s == "<!-- hoja -->":
            flush()
            if sec is not None:
                abre_sec(re.sub(r" \(cont\.\)$", "", sec["title"]), cont=True)
            i += 1; continue
        if s.startswith("```"):                                         # código
            flush()
            lang, j = s[3:].strip(), i + 1
            code = []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                code.append(lines[j]); j += 1
            add({"type": "code", "code": "\n".join(code), **({"lang": lang} if lang else {})})
            i = j + 1; continue
        if re.match(r":::\s*motion\s*$", s):
            flush()
            j = i + 1
            while j < len(lines) and lines[j].strip() != ":::":
                if lines[j].strip():
                    motion.append(lines[j].strip())
                j += 1
            i = j + 1
            continue
        m = re.match(r":::\s*(kpi|big)\s*$", s)
        if m:
            flush()
            j, rows = i + 1, []
            while j < len(lines) and lines[j].strip() != ":::":
                if lines[j].strip():
                    row = re.sub(r"^\s*[-*]\s+", "", lines[j])
                    if "|" not in row:                                  # «80 % de los residuos» → valor | etiqueta
                        mv = re.match(r"\s*([$€]?\s?[-+]?[\d.,]+\s?(?:%|[A-Za-zµ]{1,4})?)\s+(.*)", row)
                        row = f"{mv.group(1)} | {mv.group(2)}" if mv else row
                    rows.append([c.strip() for c in row.split("|")])
                j += 1
            if m.group(1) == "kpi":
                add({"type": "kpi", "items": [{"v": r[0], "l": r[1] if len(r) > 1 else "", **({"note": r[2]} if len(r) > 2 and r[2] else {})} for r in rows[:4]]})
                if len(rows) > 4:
                    avisos.append({"bloque": "kpi", "causa": f"{len(rows)} cifras; el bloque admite 4", "ajuste": "divide en dos bloques kpi"})
            elif rows:
                r0 = rows[0]
                add({"type": "big", "value": r0[0], **({"unit": r0[1]} if len(r0) > 2 and r0[1] else {}), "caption": r0[2] if len(r0) > 2 else (r0[1] if len(r0) > 1 else "")})
            i = j + 1; continue
        if s.startswith(">"):                                           # cita o aviso
            flush()
            q = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                q.append(lines[i].strip().lstrip(">").strip()); i += 1
            mm = re.match(r"\[!(\w+)\]\s*(.*)", q[0]) if q else None
            if mm:
                add({"type": "callout", "label": mm.group(1).upper(), "text": " ".join([mm.group(2)] + q[1:]).strip()})
            else:
                by = ""
                if len(q) > 1 and re.match(r"[—–-]\s*\S", q[-1]):
                    by = re.sub(r"^[—–-]\s*", "", q.pop())
                add({"type": "quote", "text": " ".join(q), **({"by": by} if by else {})})
            continue
        if re.match(r"\|.*\|", s) and i + 1 < len(lines) and re.match(r"\s*\|?[\s:\-|]+\|?\s*$", lines[i + 1]) and "-" in lines[i + 1]:   # tabla
            flush()
            head, rows = _celdas(s), []
            i += 2
            while i < len(lines) and re.match(r"\s*\|.*\|", lines[i]):
                rows.append(_celdas(lines[i])); i += 1
            g = re.match(r"\{grafico:\s*(bar|hbar|pie|line)\s*\}", lines[i].strip()) if i < len(lines) else None
            if g:
                i += 1
                items = [(r[0], _num(r[1])) for r in rows if len(r) > 1 and _num(r[1]) is not None]
                if len(items) >= 2:
                    kind = g.group(1)
                    if kind == "bar" and max(len(k) for k, _ in items) > 9:
                        kind = "hbar"                                   # etiquetas largas: barras horizontales
                    if kind == "line":
                        ch = {"type": "line", "data": {"points": [[k, v] for k, v in items]}}
                    else:
                        ch = {"type": kind, "data": {"items": [{"l": k, "v": v} for k, v in items]}}
                    add({"type": "chart", "title": _corta(" / ".join(head[:2]), 70), "chart": ch})
                    continue
                avisos.append({"bloque": "tabla", "causa": "no hay números en la 2.ª columna para el gráfico", "ajuste": "deja la tabla o corrige los valores"})
            add({"type": "table", "head": head, "rows": rows})
            continue
        m = re.match(r"!\[(.*?)\]\((\S+?)(?:\s+\"(.*?)\")?\)\s*$", s)
        if m:                                                           # imagen: el texto alternativo sirve de pie y de guía de colocación
            flush()
            alt, src, cap = m.groups()
            add({"type": "image", "src": src, "alt": alt or cap or "imagen", "caption": cap or alt or ""})
            i += 1; continue
        if re.match(r"([-*+]|\d+[.)])\s+", s):                          # lista (con sublistas por sangría de 2+ espacios)
            flush()
            ordered = bool(re.match(r"\d+[.)]\s", s))
            items = []
            while i < len(lines) and re.match(r"\s*([-*+]|\d+[.)])\s+", lines[i]):
                raw = lines[i]
                txt_ = re.sub(r"^\s*([-*+]|\d+[.)])\s+", "", raw).strip()
                if len(raw) - len(raw.lstrip()) >= 2 and items:
                    prev = items[-1]
                    if isinstance(prev, str):
                        prev = items[-1] = {"t": prev, "items": []}
                    prev["items"].append(txt_)
                else:
                    items.append(txt_)
                i += 1
            if len(items) > 14:
                avisos.append({"bloque": "list", "causa": f"{len(items)} ítems; el bloque admite 14", "ajuste": "divide la lista"})
                items = items[:14]
            add({"type": "list", "items": items, **({"ordered": True} if ordered else {})})
            continue
        para.append(s); i += 1
    flush()
    if not titulo:
        titulo = "Documento"
        avisos.append({"bloque": "cabecera", "causa": "no hay `titulo:` ni un `# Título`", "ajuste": "añade un título"})
    if not parts and not motion:
        abre_sec("Contenido")
        avisos.append({"bloque": "documento", "causa": "no hay secciones (`## …`)", "ajuste": "usa `## Título` para cada hoja"})
    fmt = FORMATOS.get(meta.get("formato", "").lower(), None) if meta.get("formato") else None
    if meta.get("formato") and not fmt:
        avisos.append({"bloque": "cabecera", "causa": f"formato '{meta['formato']}' desconocido", "ajuste": "usa pdf, pptx, docx, xlsx, video o video-vertical"})
    doc = {"contract": "1.0", "design": meta.get("estilo") or defecto.get("design") or "anura", "format": fmt or defecto.get("format") or "pdf-a4",
           **({"palette": meta["paleta"]} if meta.get("paleta") else ({"palette": defecto["palette"]} if defecto.get("palette") else {})),
           "meta": {"title": _corta(titulo, 120), **({"author": meta["autor"]} if meta.get("autor") else {}), **({"date": meta["fecha"]} if meta.get("fecha") else {}),
                    **({"subject": meta.get("asunto") or meta["objetivo"]} if (meta.get("asunto") or meta.get("objetivo")) else {}),
                    "header_left": [meta.get("autor") or _corta(titulo, 28), meta.get("fecha") or "Documento"], "footer": _corta(titulo, 80)},
           "document": {"cover": {"vertical": _corta((meta.get("vertical") or titulo.split()[0]).upper(), 20), "title": _corta(titulo, 70), **({"text": _corta(meta["objetivo"], 200)} if meta.get("objetivo") else {})},
                        "parts": [({**p, "divider": meta["divisor"]} if meta.get("divisor") else p) for p in parts if p["sections"]]}}
    if motion:
        import video_motion
        ev = video_motion.parse(motion)
        if not ev:
            avisos.append({"bloque": "motion", "causa": "ninguna línea válida en :::motion", "ajuste": "tipo | texto | segundos; tipos: " + ", ".join(video_motion.KINDS)})
    vid = {k: (int(meta[h]) if k in ("duration", "bpm") and re.fullmatch(r"\d+", meta[h]) else meta[h]) for h, k in (("duracion", "duration"), ("ritmo", "bpm"), ("entrada", "entrada"), ("escalon", "escalon"), ("musica", "musica")) if meta.get(h)}
    if motion and ev:
        vid["motion"] = ev
    if vid:                                                             # video: duracion (s, máx. 120), ritmo (bpm), entrada (slide|fade-up|wipe-reveal), escalon (s)
        doc.setdefault("options", {})["video"] = vid
    if meta.get("portada"):
        doc["document"]["cover"]["variant"] = meta["portada"]
    for k in ("options",):
        if defecto.get(k):
            doc[k] = defecto[k]
    return doc, avisos


def expandir(body):
    """Si el cuerpo trae `markdown`, lo convierte y deja que design/format/palette/options del cuerpo ganen sobre la cabecera. Devuelve (cuerpo, avisos)."""
    if not isinstance(body, dict):
        return body, []
    from engine import recetas              # supermercado: receta/ingredientes → Markdown
    body, av0 = recetas.a_markdown(body)
    if "markdown" not in body:
        return body, []
    over = {k: body[k] for k in ("design", "format", "palette", "options") if body.get(k)}
    doc, av = a_contrato(str(body["markdown"]), over)
    doc.update(over)
    return doc, av0 + av
