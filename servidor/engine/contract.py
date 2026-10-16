# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Validación del contrato de entrada. Devuelve errores con formato fijo: bloque, causa, ajuste sugerido."""

LIM = {"p": 1400, "items": 14, "rows": 40, "points": 14}


def _e(where, cause, fix):
    return {"bloque": where, "causa": cause, "ajuste": fix}


def validate(doc: dict, manifest: dict, warns: list = None) -> list:
    """Errores = el documento no se puede construir (se rechaza). Todo lo demás que no sea estándar se degrada y va a `warns`."""
    errs = []
    warns = warns if warns is not None else []
    vocab = set(manifest["blocks"]["vocabulario"])
    charts = set(manifest["blocks"]["chart_types"])
    if doc.get("design") != manifest["id"]:
        errs.append(_e("design", f"diseño '{doc.get('design')}' no coincide con '{manifest['id']}'", "usa design: anura"))
    if doc.get("format") not in manifest["formats"]:
        errs.append(_e("format", f"formato '{doc.get('format')}' no soportado", f"usa uno de {manifest['formats']}"))
    d = doc.get("document") or {}
    if not d.get("cover"):
        errs.append(_e("document.cover", "falta la portada", "añade cover con title y vertical"))
    seen = set()
    for pi, part in enumerate(d.get("parts", [])):
        for si, sec in enumerate(part.get("sections", [])):
            sid = sec.get("id", f"p{pi}s{si}")
            if sid in seen:
                errs.append(_e(sid, "id repetido", "cada sección lleva un id único"))
            seen.add(sid)
            for bi, b in enumerate(sec.get("blocks", [])):
                w = f"{sid}.b{bi}"
                t = b.get("type")
                if t not in vocab:
                    warns.append(_e(w, f"tipo de bloque '{t}' fuera del vocabulario", "se mostrará como nota; usa un bloque del vocabulario"))
                    continue
                if t == "p" and len(b.get("text", "")) > LIM["p"]:
                    warns.append(_e(w, f"párrafo de {len(b['text'])} caracteres (máx {LIM['p']})", "divídelo en dos bloques p"))
                if t == "list" and len(b.get("items", [])) > LIM["items"]:
                    warns.append(_e(w, f"lista de {len(b['items'])} ítems (máx {LIM['items']})", "divide la lista"))
                if t == "table" and len(b.get("rows", [])) > LIM["rows"]:
                    warns.append(_e(w, f"tabla de {len(b['rows'])} filas (máx {LIM['rows']})", "divide la tabla"))
                if t == "table":
                    n = len(b.get("head", []))
                    for ri, r in enumerate(b.get("rows", [])):
                        if len(r) != n:
                            warns.append(_e(f"{w}.r{ri}", f"fila con {len(r)} celdas y cabecera con {n}", "se completó o recortó la fila"))
                            del r[n:]
                            r.extend([""] * (n - len(r)))
                if t in ("chart", "figure") and b.get("chart") and b["chart"].get("type") not in charts:
                    warns.append(_e(w, f"gráfico '{b['chart'].get('type')}' no es estándar", "se mostrará una tabla con los datos"))
    return errs
