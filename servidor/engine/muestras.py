# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Contenido de MUESTRA (valores como 12, 34, 56 y una dispersión simulada: ninguna cifra es un resultado) para la galería de variantes
y para la lista de revisión de un diseño nuevo (validar_diseno.py)."""
import random

from . import blocks, spec


def samples(imgs_ok):
    rnd = random.Random(7)
    pts = [[x, round(5 + 0.6 * x + rnd.gauss(0, 2.2), 2)] for x in [rnd.uniform(1, 10) for _ in range(60)]]
    tab = {"head": ["Variable", "Rango", "Tipo"], "rows": [["variable_a", "0 a 100", "int8"], ["variable_b", "1972 a 2024", "int16"], ["variable_c", "texto", "category"]]}
    tones = {"head": ["Organismo", "Especie", "Etapa", "Edad"], "rows": [["Grupo A", {"t": "F", "tone": "f"}, {"t": "P", "tone": "p"}, {"t": "L", "tone": "l"}], ["Grupo B", {"t": "P", "tone": "p"}, {"t": "—", "tone": "n"}, {"t": "F", "tone": "f"}]]}
    bar = {"type": "bar", "data": {"max": 100, "items": [{"l": "A", "v": 40, "hi": True}, {"l": "B", "v": 62}, {"l": "C", "v": 85}]}}
    S = {}
    S["TB-1"] = {"type": "table", **tab}
    S["TB-2"] = {"type": "table", "variant": "compact", **tab}
    S["TB-3"] = {"type": "table", "variant": "ficha", "head": ["Revisión", "Resultado"], "rows": [["Registros", "Texto de muestra del resultado."], ["Faltantes", "Texto de muestra del resultado."]]}
    S["TB-4"] = {"type": "table", **tones}
    for t in blocks.CALLOUT_TONES:
        S[f"AV-{t}"] = {"type": "callout", "tone": t, "title": "Título de muestra", "text": "Texto de muestra del aviso, con una frase corta."}
    S["CF-1"] = {"type": "kpi", "items": [{"v": "12", "l": "etiqueta A", "note": "nota"}, {"v": "34 %", "l": "etiqueta B"}, {"v": "56", "l": "etiqueta C"}]}
    S["CF-2"] = {"type": "stats", "title": "Cifras", "items": [{"v": "0,00", "l": "primera medida"}, {"v": "00,0", "l": "segunda medida"}], "note": "Nota breve de lectura."}
    S["CF-3"] = {"type": "big", "value": "00,0", "unit": "%", "caption": "Texto de la cifra grande"}
    S["FG-1"] = {"type": "chart", "title": "Título del gráfico", "tag": "etiqueta · muestra", "chart": bar, "caption": "Figura 1. Pie de muestra."}
    S["FG-2"] = {"type": "figure", "title": "Título de la figura", "chart": bar, "caption": "Figura 2. Pie de muestra.", "side": [{"v": "0,00", "l": "medida A"}, {"v": "0,00", "l": "medida B"}]}
    S["FG-3"] = {"type": "image", "src": "dimorfismo/rana_arvalis_macho_azul.jpg" if imgs_ok else None, "ratio": "16/9", "caption": "Pie de imagen de muestra."}
    S["GR-bar"] = {"type": "chart", "title": "Barras", "tag": "estándar", "chart": bar}
    S["GR-hbar"] = {"type": "chart", "title": "Barras horizontales", "tag": "estándar", "chart": {"type": "hbar", "data": {"max": 10, "items": [{"l": "Categoría uno", "v": 8, "hi": True}, {"l": "Categoría dos", "v": 5}, {"l": "Categoría tres", "v": 3}]}}}
    S["GR-line"] = {"type": "chart", "title": "Líneas", "tag": "estándar", "chart": {"type": "line", "data": {"points": [[1, 20], [2, 45], [3, 40], [4, 70]], "xrange": [0, 5], "yrange": [0, 100], "xlabel": "eje x", "ylabel": "eje y"}}}
    S["GR-stack"] = {"type": "chart", "title": "Apiladas", "tag": "estándar", "chart": {"type": "stack", "data": {"rows": [{"l": "Perfil A", "v": [60, 30, 10]}, {"l": "Perfil B", "v": [30, 50, 20]}]}, "legend": [["Serie 1", "k"], ["Serie 2", "hi"], ["Serie 3", "w"]]}}
    S["GR-hist"] = {"type": "chart", "title": "Histograma", "tag": "estándar · datos de muestra", "chart": {"type": "hist", "data": {"bars": [[1, 3], [2, 8], [3, 14], [4, 22], [5, 17], [6, 9], [7, 4]], "width": 1, "xlabel": "valor", "ylabel": "frecuencia", "lines": [{"x": 4.1, "label": "Media", "style": "mean"}, {"x": 4, "label": "Mediana", "style": "median"}]}}}
    S["GR-box"] = {"type": "chart", "title": "Cajas", "tag": "estándar · datos de muestra", "chart": {"type": "box", "data": {"xrange": [0, 10], "xlabel": "valor", "groups": [{"l": "Grupo A", "lo": 2, "q1": 4, "med": 5, "q3": 7, "hi": 9, "out": [0.5]}, {"l": "Grupo B", "lo": 3, "q1": 5, "med": 6, "q3": 7.5, "hi": 9.5, "out": []}]}}}
    S["GR-scatter"] = {"type": "chart", "title": "Dispersión + tendencia", "tag": "SIMULACIÓN · puntos aleatorios", "chart": {"type": "scatter", "data": {"points": pts, "trend": "auto", "xlabel": "variable x", "ylabel": "variable y", "xrange": [0, 11], "yrange": [0, 16]}}, "sim": True}
    S["GR-heat"] = {"type": "chart", "title": "Mapa de calor", "tag": "estándar · datos de muestra", "chart": {"type": "heat", "data": {"labels": ["A", "B", "C", "D"], "matrix": [[1, .5, -.3, 0], [.5, 1, .1, -.6], [-.3, .1, 1, .8], [0, -.6, .8, 1]]}}}
    S["GR-map"] = {"type": "chart", "title": "Mapa de puntos", "tag": "contorno esquemático · coordenadas reales de ciudades", "chart": {"type": "map", "data": {"outline": "colombia", "size": True, "points": [{"lon": -74.07, "lat": 4.71, "label": "Bogotá", "v": 3}, {"lon": -75.57, "lat": 6.24, "label": "Medellín", "v": 2}, {"lon": -76.53, "lat": 3.45, "label": "Cali", "v": 2}, {"lon": -74.8, "lat": 10.96, "label": "Barranquilla", "v": 1}]}}}
    S["FL-1"] = {"type": "flow", "cols": 3, "steps": [{"title": "Paso uno", "text": "Descripción corta."}, {"title": "Paso dos", "text": "Descripción corta."}, {"title": "Paso tres", "text": "Descripción corta.", "on": True}]}
    S["FL-2"] = {"type": "flowchart", "title": "Diagrama de flujo", "nodes": [{"id": "a", "label": "Inicio", "kind": "start"}, {"id": "b", "label": "Leer datos", "kind": "io"}, {"id": "c", "label": "¿Datos válidos?", "kind": "decision"}, {"id": "d", "label": "Procesar"}, {"id": "e", "label": "Corregir"}, {"id": "f", "label": "Fin", "kind": "end"}], "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}, {"from": "c", "to": "d", "label": "sí"}, {"from": "c", "to": "e", "label": "no"}, {"from": "d", "to": "f"}, {"from": "e", "to": "b"}]}
    S["FL-3"] = {"type": "ladder", "items": [{"title": "Opción simple", "text": "Descripción.", "cost": "costo: bajo"}, {"title": "Opción media", "text": "Descripción.", "cost": "costo: medio"}, {"title": "Opción compleja", "text": "Descripción.", "cost": "costo: alto"}]}
    S["FL-4"] = {"type": "timeline", "items": [{"code": "E1", "label": "Etapa uno", "days": 3, "vis": "h", "photo": "texto"}, {"code": "E2", "label": "Etapa dos", "days": 2, "vis": "v", "photo": "texto"}, {"code": "E3", "label": "Etapa tres", "days": 1, "vis": "x", "photo": "texto"}], "adult": {"code": "A", "label": "Final", "days": "—", "photo": "texto"}, "legend": [["v", "visible"], ["h", "oculta"], ["x", "difícil"]], "caption": "Pie de muestra."}
    S["FL-5"] = {"type": "ranks", "head": ["Columna A", "Columna B"], "rows": [{"rank": "Nivel 1", "v": ["Valor", "Valor"]}, {"rank": "Nivel 2", "v": ["Valor", "Valor"]}, {"rank": "Nivel 3", "v": ["Valor", "Valor"]}]}
    S["FL-6"] = {"type": "compare", "left": {"title": "Opción A", "sub": "subtítulo", "items": ["Ventaja uno", "Ventaja dos"]}, "right": {"title": "Opción B", "sub": "subtítulo", "items": ["Ventaja uno", "Ventaja dos"]}, "verdict": "Veredicto de muestra."}
    S["FM-1"] = {"type": "form", "title": "Datos del estudiante", "rows": ["Nombre completo", "Ficha / grupo", "Fecha de entrega"]}
    return S


def doc_muestra(design: str, largo: bool = False, cover_variant: str = "CV-1", divider: str = "auto", imgs_ok: bool = True, palette: str = "default") -> dict:
    """Documento con UN ejemplo de cada bloque. `largo=True` usa titulares y textos largos para probar desbordes."""
    S = samples(imgs_ok)
    t_s = "Sección de muestra" if not largo else "Una sección con un titular bastante largo que ocupa varias líneas de la hoja y obliga a reducir el tamaño"
    filler = ("Texto de muestra para comprobar el flujo, la paginación y los saltos de línea. " * (14 if largo else 1)).strip()
    secciones = []
    for k, (name, b) in enumerate(S.items()):
        if name.startswith(("AV-", "GR-", "TB-", "CF-", "FG-", "FL-", "FM-")) and name not in ("TB-1", "AV-nota", "CF-1", "FG-1", "GR-bar", "FL-1", "FL-2", "FM-1"):
            continue
        secciones.append({"id": f"m{k}", "title": f"{t_s} {k+1}" if largo else f"Muestra {name}", "tema": "Muestra", "blocks": [{"type": "p", "text": filler}, b]})
    for t, s in spec.BLOCKS.items():
        if t in ("p", "h", "list", "table", "quote", "code", "refs", "media", "big", "stats", "compare", "ladder", "ranks", "timeline", "callout", "image") and s.get("example"):
            ex = dict(s["example"])
            if t == "image":
                ex["src"] = None
                ex["need"] = "Imagen de muestra"
            if t == "media":
                continue
            secciones.append({"id": f"e_{t}", "title": f"{t_s} · {t}" if largo else f"Bloque {t}", "tema": "Ejemplo", "blocks": [ex]})
    return {"contract": spec.CONTRACT_VERSION, "design": design, "format": "pdf-a4", "palette": palette, "options": {"seed": 5},
            "meta": {"title": "Documento de muestra", "date": "Mes 2026", "version": "Vol. 01 · v0.1", "header_left": ["Título de muestra", "Subtítulo"], "footer": "MUESTRA · lista de revisión"},
            "document": {"cover": {"variant": cover_variant, "vertical": "MUESTRA" if not largo else "UNA PALABRA LARGA", "title": "Título del documento de muestra" if not largo else "Un título del documento extremadamente largo que casi no cabe",
                                    "text": "Contexto del documento de muestra, en pocas líneas." if not largo else "Contexto largo " * 14},
                         "parts": [{"id": "p1", "title": "Parte uno", "desc": "Descripción de muestra.", "divider": divider, "sections": secciones[: len(secciones) // 2]},
                                   {"id": "p2", "title": "Parte dos" if not largo else "Una parte con título largo", "desc": "Descripción de muestra.", "divider": divider, "sections": secciones[len(secciones) // 2:]}]}}
