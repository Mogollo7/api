# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""ESPECIFICACIÓN ÚNICA del contrato: de aquí salen el validador, el JSON Schema (`contrato.schema.json`) y el Prompt Maestro.
Cambiar un bloque = cambiar SOLO este archivo (y su renderizador). Campos: tipo, req (obligatorio), max (longitud), enum, desc.

Tipos: str, markup (texto con **negrita**, *cursiva*, `código`, [FUENTE]…), num, bool, obj, list, cell (str | num | {t,tone,hi}).
"""
CONTRACT_VERSION = "1.0"

F = lambda t, desc="", req=False, **kw: {"type": t, "desc": desc, "req": req, **kw}

CHART_TYPES = {
    "bar": {"data": "items:[{l,v,hi?,err?,hatch?}] o series (agrupadas/apiladas): categories:[..], series:[{name,values:[..]}], mode:'grouped'|'stacked'; max, unit", "limit": 14, "uso": "comparar pocas categorías"},
    "hbar": {"data": "items:[{l,v,hi?}], max", "limit": 20, "uso": "etiquetas largas"},
    "line": {"data": "points:[[x,y,etiqueta?]] o series:[{name,points:[[x,y]..]}]; x puede ser texto/fecha ISO; xrange,yrange,xlabel,ylabel", "limit": 14, "uso": "tendencia con pocos puntos o series"},
    "stack": {"data": "rows:[{l,v:[a,b,c]}], total", "limit": 8, "uso": "composición 100 %"},
    "pie": {"data": "items:[{l,v}] (suman el total); donut:true para dona", "limit": 7, "uso": "partes de un todo (≤ 7)"},
    "hist": {"data": "bars:[[x,conteo]], width, xrange, xticks, lines:[{x,label,style:'mean'|'median'}], xlabel, ylabel", "limit": 40, "uso": "distribución de una variable"},
    "box": {"data": "groups:[{l,lo,q1,med,q3,hi,out:[..]}], xrange, xticks, xlabel", "limit": 40, "uso": "dispersión y atípicos por grupo"},
    "scatter": {"data": "points:[[x,y]], trend:'auto'|{slope,intercept,label}, xrange,yrange,xticks,yticks,xlabel,ylabel", "limit": 400, "uso": "relación entre dos variables"},
    "heat": {"data": "labels:[..], matrix:[[..]], range:[min,max]", "limit": 12, "uso": "correlaciones"},
    "map": {"data": "outline:'colombia'|[[lon,lat]..], points:[{lon,lat,label,v}], size:bool, graticule:2", "limit": 60, "uso": "ubicar puntos"},
}

BLOCKS = {
    "p": {"desc": "Párrafo de texto.", "fields": {"text": F("markup", "Texto del párrafo.", True, max=1400)},
          "example": {"type": "p", "text": "Texto con **negrita**, *Nombre científico* y una marca [FUENTE]."}},
    "h": {"desc": "Subtítulo de sección (etiqueta con regla). No repitas el titular de la sección.", "fields": {"text": F("markup", "Subtítulo corto.", True, max=80)},
          "example": {"type": "h", "text": "Interpretación"}},
    "list": {"desc": "Lista con viñetas o numerada; un ítem puede llevar sublista {t, items}.", "fields": {
        "items": F("list", "Ítems (texto o {t, items:[…]}).", True, max=14), "ordered": F("bool", "Numerada.")},
        "example": {"type": "list", "ordered": True, "items": ["Primero", {"t": "Segundo", "items": ["detalle a", "detalle b"]}, "Tercero"]}},
    "table": {"desc": "Tabla; se parte por filas entre hojas repitiendo la cabecera.", "fields": {
        "head": F("list", "Encabezados."), "rows": F("list", "Filas: listas de celdas (texto, número o {t,tone:'f|p|l|n',hi}).", True, max=40),
        "widths": F("list", "Anchos relativos."), "caption": F("markup", "Pie de tabla."), "variant": F("str", "Variante.", enum=["compact", "ficha"])},
        "example": {"type": "table", "head": ["Variable", "Tipo"], "rows": [["edad", "int8"], ["año", "int16"]]}},
    "chart": {"desc": "Gráfico estándar en marco con título y pie. Ver tipos.", "fields": {
        "title": F("markup", "Título del gráfico (no repitas el titular de la hoja).", False, max=70), "tag": F("markup", "Etiqueta mono: fuente o tipo de dato."),
        "chart": F("obj", "{type, data[, legend]}", True), "caption": F("markup", "Pie: «Figura N. …»."), "sim": F("bool", "Datos simulados (marco punteado)."),
        "half": F("bool", "Dos bloques half seguidos van lado a lado.")},
        "example": {"type": "chart", "title": "Acierto", "chart": {"type": "bar", "data": {"max": 100, "items": [{"l": "A", "v": 40, "hi": True}, {"l": "B", "v": 62}]}}, "caption": "Figura 1. Muestra."}},
    "figure": {"desc": "Figura (gráfico o imagen) con columna de cifras laterales (7/10 + 3/10).", "fields": {
        "chart": F("obj", "Como en chart."), "image": F("obj", "Como en image."), "title": F("markup", "Título."), "caption": F("markup", "Pie."),
        "side": F("list", "Cifras: [{v,l}]."), "side_note": F("markup", "Nota bajo las cifras."), "side_title": F("markup", "Rótulo de la columna.")},
        "example": {"type": "figure", "chart": {"type": "bar", "data": {"items": [{"l": "A", "v": 3}]}}, "caption": "Figura 2.", "side": [{"v": "0,34", "l": "r de Pearson"}]}},
    "kpi": {"desc": "2 a 4 tarjetas con cifra grande.", "fields": {"items": F("list", "[{v, l, note?}]", True, max=4)},
            "example": {"type": "kpi", "items": [{"v": "62,9 %", "l": "top-1", "note": "[CALC]"}, {"v": "86,1 %", "l": "top-3"}]}},
    "stats": {"desc": "Cifras en columna con regla vertical.", "fields": {"items": F("list", "[{v,l}]", True), "title": F("markup", "Rótulo."), "note": F("markup", "Nota.")},
              "example": {"type": "stats", "items": [{"v": "9,0", "l": "moda"}, {"v": "8,0", "l": "mediana"}]}},
    "big": {"desc": "Una cifra gigante con su leyenda.", "fields": {"value": F("str", "Cifra.", True), "unit": F("str", "Unidad."), "caption": F("markup", "Leyenda.", True)},
            "example": {"type": "big", "value": "62,9", "unit": "%", "caption": "Acierto top-1"}},
    "callout": {"desc": "Aviso con etiqueta.", "fields": {
        "tone": F("str", "Tono.", False, enum=["nota", "clave", "ojo", "sim", "pend", "regla", "slate", "hueco"]), "label": F("str", "Rótulo."), "title": F("markup", "Título."),
        "text": F("markup", "Texto."), "paras": F("list", "Varios párrafos.")},
        "example": {"type": "callout", "tone": "ojo", "text": "Advertencia breve."}},
    "image": {"desc": "Foto en dos tintas con pie y crédito. Si no tienes la imagen, escribe `need` y el servidor dibuja «IMAGEN NECESARIA».", "fields": {
        "src": F("str", "Ruta relativa a la carpeta de imágenes."), "need": F("markup", "Qué imagen hace falta si no existe."), "caption": F("markup", "Pie (sirve de texto alternativo)."),
        "alt": F("str", "Texto alternativo."), "ratio": F("str", "Proporción, p. ej. 16/9."), "treatment": F("str", "Tinta. `original` = sin filtro (capturas de pantalla).", enum=["ocre", "crema", "verde", "negroverde", "acento", "claro", "calido", "rojo", "original"]),
        "items": F("list", "Hasta 3 imágenes en fila: [{src,caption,…}]", False, max=3)},
        "example": {"type": "image", "src": "fauna/rana.jpg", "ratio": "16/9", "caption": "Pie de la imagen."}},
    "media": {"desc": "GIF o video. PDF imprime el póster con «▶»; web reproduce; PPTX lo incrusta.", "fields": {
        "kind": F("str", "gif | video.", True, enum=["gif", "video"]), "src": F("str", "Archivo.", True), "poster": F("str", "Imagen de póster."), "caption": F("markup", "Pie."),
        "credit": F("str", "Autor y licencia."), "alt": F("str", "Texto alternativo.", True), "url": F("str", "Enlace al video.")},
        "example": {"type": "media", "kind": "video", "src": "clips/demo.mp4", "poster": "clips/demo.png", "alt": "Demostración del proceso", "caption": "Video 1."}},
    "flow": {"desc": "Pasos en tarjetas (proceso lineal).", "fields": {"steps": F("list", "[{title,text?,n?,on?}]", True, max=9), "cols": F("num", "Columnas 2–4.")},
             "example": {"type": "flow", "cols": 3, "steps": [{"title": "Uno", "text": "…"}, {"title": "Dos", "on": True}]}},
    "ladder": {"desc": "Escalera de opciones de simple a complejo.", "fields": {"items": F("list", "[{title,text,cost?}]", True, max=9)},
               "example": {"type": "ladder", "items": [{"title": "Simple", "text": "…", "cost": "costo: bajo"}]}},
    "ranks": {"desc": "Embudo de rangos con dos columnas de ejemplo.", "fields": {"head": F("list", "Rótulos de columnas."), "rows": F("list", "[{rank, v:[a,b]}]", True)},
              "example": {"type": "ranks", "head": ["Rana", "Planta"], "rows": [{"rank": "Reino", "v": ["Animalia", "Plantae"]}]}},
    "timeline": {"desc": "Línea de vida: etapas con duración.", "fields": {"items": F("list", "[{code,label,days,vis:'v|h|x',photo}]", True), "adult": F("obj", "Etapa final sin duración."),
                 "legend": F("list", "[[clase,texto]]"), "caption": F("markup", "Pie.")},
                 "example": {"type": "timeline", "items": [{"code": "H", "label": "Huevo", "days": 3, "vis": "h", "photo": "casi nunca"}]}},
    "compare": {"desc": "Dos opciones enfrentadas con veredicto.", "fields": {"left": F("obj", "{title,sub?,items}", True), "right": F("obj", "{title,sub?,items}", True), "verdict": F("markup", "Veredicto.")},
                "example": {"type": "compare", "left": {"title": "A", "items": ["…"]}, "right": {"title": "B", "items": ["…"]}, "verdict": "A gana."}},
    "toc": {"desc": "Índice automático con páginas y enlaces (solo uno por documento).", "fields": {}, "example": {"type": "toc"}},
    "form": {"desc": "Ficha de datos con filas para completar.", "fields": {"title": F("markup", "Título."), "rows": F("list", "Etiquetas.", True)},
             "example": {"type": "form", "title": "Datos del estudiante", "rows": ["Nombre completo", "Fecha"]}},
    "flowchart": {"desc": "Diagrama de flujo estándar (≤ 14 nodos, ≤ 3 por capa).", "fields": {
        "nodes": F("list", "[{id,label,kind:'start|process|decision|io|end'}]", True, max=14), "edges": F("list", "[{from,to,label?}]"), "title": F("markup", "Título."), "caption": F("markup", "Pie.")},
        "example": {"type": "flowchart", "nodes": [{"id": "a", "label": "Inicio", "kind": "start"}, {"id": "b", "label": "Fin", "kind": "end"}], "edges": [{"from": "a", "to": "b"}]}},
    "quote": {"desc": "Cita destacada con autor.", "fields": {"text": F("markup", "Cita.", True, max=500), "by": F("markup", "Autor o fuente.")},
              "example": {"type": "quote", "text": "Feo es poderoso.", "by": "Manifiesto"}},
    "code": {"desc": "Bloque de código o texto monoespaciado (no se interpreta).", "fields": {"code": F("str", "Código.", True, max=1500), "lang": F("str", "Lenguaje."), "caption": F("markup", "Pie.")},
             "example": {"type": "code", "lang": "python", "code": "df.info()"}},
    "refs": {"desc": "Referencias o bibliografía numerada.", "fields": {"items": F("list", "Cada referencia como texto.", True, max=40), "title": F("markup", "Título.")},
             "example": {"type": "refs", "items": ["Autor (2024). Título. Revista."]}},
    "custom": {"desc": "ÚLTIMO RECURSO: fragmento HTML saneado (solo etiquetas y clases permitidas). Úsalo solo si ningún bloque sirve.", "fields": {"html": F("str", "HTML.", True)},
               "example": {"type": "custom", "html": "<p class=\"k\">Texto</p>"}},
}

SECTION = {"id": F("str", "Identificador único.", True), "title": F("markup", "Titular de la hoja (≤ 60 caracteres).", True, max=90),
           "tema": F("str", "Tema de la cabecera: solo si aporta palabras que el titular no tiene."), "kind": F("str", "normal | clave.", False, enum=["normal", "clave"]),
           "lead": F("markup", "Idea principal (en `clave` va en la tarjeta)."), "blocks": F("list", "Bloques de la sección.", True),
           "notes": F("list", "Notas al pie: [{n, text}] que se citan en el texto con [^n]."), "toc": F("bool", "False = no aparece en el índice.")}
PART = {"id": F("str", "Identificador.", True), "title": F("str", "Título corto (≤ 34).", True, max=34), "desc": F("str", "Descripción de 1–2 líneas.", True, max=200),
        "divider": F("str", "Variante de divisor o 'auto'."), "bg": F("str", "Rol de fondo."), "num_color": F("str", "Rol del número."), "title_color": F("str", "Rol del título."),
        "image": F("str", "Foto del divisor."), "tint": F("list", "[rol oscuro, rol claro]."), "sections": F("list", "Secciones.", True)}
COVER = {"title": F("str", "Título del documento (una sola vez; no lo repitas en otros campos).", True, max=70), "vertical": F("str", "Palabra gigante de la portada.", True, max=20),
         "text": F("str", "Descripción de 1–3 líneas.", True, max=220), "variant": F("str", "CV-1…"), "image": F("str", "Foto."), "treatment": F("str", "Tinta."), "tint": F("list", "[rol oscuro, rol claro]."),
         "alt": F("str", "Texto alternativo de la foto."), "stack": F("list", "Filas del titular apilado (CV-4)."), "badge": F("obj", "{lines, tag} (CV-4)."), "quote": F("list", "Líneas (CV-4)."),
         "strip": F("list", "Palabras (CV-4)."), "number": F("str", "Número (CV-4)."), "list": F("list", "Líneas (CV-4)."), "notes": F("list", "Notas (CV-4).")}
META = {"title": F("str", "Título para metadatos.", True), "author": F("str", "Autor."), "subject": F("str", "Asunto."), "keywords": F("list", "Palabras clave."), "date": F("str", "Fecha: «Mes AAAA»."),
        "version": F("str", "Versión o etiqueta de la caja de la portada."), "header_left": F("list", "Dos líneas de la cabecera de portada."), "footer": F("str", "Pie de las hojas.")}
ROOT = {"contract": F("str", f"Versión del contrato (hoy «{CONTRACT_VERSION}»).", True), "design": F("str", "Id del diseño.", True), "format": F("str", "pdf-a4 | pptx-16x9 | web-1col.", True),
        "palette": F("str", "Nombre de paleta, 'default' o {rol:#hex}."), "options": F("obj", "{seed}"), "meta": F("obj", "Metadatos.", True), "document": F("obj", "{cover, parts[]}", True)}


def validate_block(b: dict, w: str, warns: list):
    """Comprueba campos obligatorios, enum y longitudes de UN bloque. No lanza: añade avisos."""
    t = b.get("type")
    spec = BLOCKS.get(t)
    if not spec:
        return
    for k, f in spec["fields"].items():
        v = b.get(k)
        if f.get("req") and v in (None, "", []):
            if t in ("callout",) and k in ("text",) and b.get("paras"):
                continue
            if t == "figure" and k in ("chart", "image"):
                continue
            warns.append({"bloque": w, "causa": f"`{t}.{k}` es obligatorio y falta", "ajuste": "complétalo; si no, el bloque se degrada a nota"})
        if v is not None and f.get("enum") and isinstance(v, str) and v not in f["enum"]:
            warns.append({"bloque": w, "causa": f"`{t}.{k}`='{v}' no está en {f['enum']}", "ajuste": "usa uno de la lista"})
        if v is not None and f.get("max") and isinstance(v, str) and len(v) > f["max"]:
            warns.append({"bloque": w, "causa": f"`{t}.{k}` de {len(v)} caracteres (máx {f['max']})", "ajuste": "acorta"})
        if v is not None and f.get("max") and isinstance(v, list) and len(v) > f["max"]:
            warns.append({"bloque": w, "causa": f"`{t}.{k}` con {len(v)} elementos (máx {f['max']})", "ajuste": "divide el bloque"})


def json_schema() -> dict:
    """JSON Schema (draft-07) del contrato, generado de BLOCKS."""
    ty = {"str": {"type": "string"}, "markup": {"type": "string"}, "num": {"type": "number"}, "bool": {"type": "boolean"}, "obj": {"type": "object"}, "list": {"type": "array"}, "cell": {}}

    def prop(f):
        d = dict(ty.get(f["type"], {}))
        if f.get("enum"):
            d["enum"] = f["enum"]
        if f.get("max") and f["type"] in ("str", "markup"):
            d["maxLength"] = f["max"]
        if f.get("max") and f["type"] == "list":
            d["maxItems"] = f["max"]
        if f.get("desc"):
            d["description"] = f["desc"]
        return d

    blocks = []
    for name, s in BLOCKS.items():
        blocks.append({"type": "object", "title": name, "description": s["desc"], "required": ["type"] + [k for k, f in s["fields"].items() if f.get("req") and name not in ("callout", "figure")],
                       "properties": {"type": {"const": name}, **{k: prop(f) for k, f in s["fields"].items()}, "half": {"type": "boolean"}, "label": {"type": "string"}}})
    obj = lambda spec, extra=None: {"type": "object", "required": [k for k, f in spec.items() if f.get("req")], "properties": {k: prop(f) for k, f in spec.items()} | (extra or {})}
    section = obj(SECTION, {"blocks": {"type": "array", "items": {"oneOf": blocks}}})
    part = obj(PART, {"sections": {"type": "array", "items": section}})
    return {"$schema": "http://json-schema.org/draft-07/schema#", "title": f"Contrato de documentos v{CONTRACT_VERSION}", "type": "object",
            "required": [k for k, f in ROOT.items() if f.get("req")],
            "properties": {**{k: prop(f) for k, f in ROOT.items()}, "contract": {"const": CONTRACT_VERSION},
                           "meta": obj(META), "document": {"type": "object", "required": ["cover", "parts"], "properties": {"cover": obj(COVER), "parts": {"type": "array", "items": part}}}}}
