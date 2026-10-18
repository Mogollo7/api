# [CLAUDE-CONSTRUCTOR] Supermercado: recetas (documento completo con huecos) e ingredientes (fragmento con huecos) → Markdown listo para el motor.
"""rellenar(receta, valores) -> (markdown, avisos, ficha)   componer(items, meta) -> (markdown, avisos)

Una receta/ingrediente es un JSON de la biblioteca (tipo «receta» o «ingrediente») con:
  huecos:    {nombre: {desc, defecto, ejemplo?, lista?: [campos]}}   lista = repite una línea por elemento
  markdown:  texto con {{hueco}} y bloques {{#lista}}…{{campo}}…{{/lista}} (para una lista de textos: {{.}})
Todo hueco lleva `defecto`: con 0 valores el documento sale completo (el agente solo cambia lo que quiere cambiar).
"""
import re

NL = chr(10)

import biblioteca


def _item(it, campos):
    """Un elemento de lista puede llegar como dict, lista o texto «a | b | c»."""
    if isinstance(it, dict):
        return it
    vals = it if isinstance(it, (list, tuple)) else [p.strip() for p in str(it).split("|")]
    return dict(zip(campos or ["."], vals)) | ({".": vals[0]} if vals else {})


def _vacio(v):
    return v in (None, "", [], {})


def rellenar(r, valores=None):
    valores, av = dict(valores or {}), []
    huecos = r.get("huecos", {})
    for k in valores:
        if k not in huecos:
            av.append({"bloque": "receta", "causa": f"el hueco '{k}' no existe en '{r['id']}'", "ajuste": "huecos válidos: " + ", ".join(huecos)})
    datos = {k: (valores[k] if not _vacio(valores.get(k)) else h.get("defecto")) for k, h in huecos.items()}
    md = r["markdown"]

    def lista(m):
        k, cuerpo = m.group(1), m.group(2)
        campos = huecos.get(k, {}).get("lista")
        items = datos.get(k) or []
        if not isinstance(items, list):
            items = [items]
        mx = huecos.get(k, {}).get("max")
        if mx and len(items) > mx:
            av.append({"bloque": "receta", "causa": f"'{k}' admite {mx} elementos y llegaron {len(items)}", "ajuste": f"se usan los primeros {mx}"})
            items = items[:mx]
        out = []
        for it in items:
            d = _item(it, campos)
            out.append(re.sub(r"\{\{([\w.]+)\}\}", lambda x: str(d.get(x.group(1), "")), cuerpo))
        return "".join(out)

    md = re.sub(r"\{\{#(\w+)\}\}\n?(.*?)\{\{/\1\}\}\n?", lista, md, flags=re.S)
    md = re.sub(r"\{\{(\w+)\}\}", lambda m: str(datos.get(m.group(1)) if datos.get(m.group(1)) is not None else ""), md)
    return md, av


def ficha(r):
    """Lo mínimo que el agente necesita para rellenar: solo los huecos, con su descripción y un ejemplo."""
    return {"id": r["id"], "tipo": r["tipo"], "nombre": r.get("nombre"), "descripcion": r.get("descripcion"), "formato": r.get("formato"), "estilo": r.get("estilo"),
            "huecos": {k: {"desc": h.get("desc", ""), **({"campos": h["lista"]} if h.get("lista") else {}), **({"max": h["max"]} if h.get("max") else {}),
                           "defecto": h.get("defecto")} for k, h in r.get("huecos", {}).items()},
            "uso": "create_from_recipe(receta='" + r["id"] + "', valores={…solo los huecos que quieras cambiar…})"}


def _get(id_, tipo):
    r = biblioteca.obtener(id_, tipo)
    if not r or "markdown" not in r:
        raise ValueError(f"no hay {tipo} '{id_}'")
    return r


def receta(id_, valores=None, over=None):
    """Markdown completo de una receta. `over` = {formato, estilo, paleta} que ganan sobre los de la receta."""
    r = _get(id_, "receta")
    md, av = rellenar(r, valores)
    return md, av, r


def componer(items, meta=None):
    """Varios ingredientes en orden → un documento. meta = {titulo, formato, estilo, objetivo, autor, fecha, paleta}."""
    meta, av, partes = dict(meta or {}), [], []
    if not isinstance(items, list) or not items:
        raise ValueError("ingredientes: lista [{id, valores}] con al menos uno")
    for it in items:
        it = {"id": it} if isinstance(it, str) else it
        md, a = rellenar(_get(it.get("id", ""), "ingrediente"), it.get("valores"))
        partes.append(md.strip())
        av += a
    cab = "\n".join(f"{k}: {v}" for k, v in (("titulo", meta.get("titulo", "Documento")), ("objetivo", meta.get("objetivo")), ("formato", meta.get("formato", "pdf")),
                                              ("estilo", meta.get("estilo")), ("paleta", meta.get("paleta")), ("autor", meta.get("autor")), ("fecha", meta.get("fecha"))) if v)
    return f"---\n{cab}\n---\n\n" + "\n\n".join(partes) + "\n", av


def a_markdown(body):
    """Si el cuerpo trae `receta` o `ingredientes`, devuelve el cuerpo con `markdown` (y avisos). Los demás campos (format, design…) ganan."""
    if body.get("receta"):
        md, av, r = receta(body["receta"], body.get("valores"))
        por_defecto = {"format": r.get("formato"), "design": r.get("estilo")}       # el formato y el estilo de la receta, salvo que el cuerpo diga otro
    elif body.get("ingredientes"):
        md, av = componer(body["ingredientes"], body.get("meta") or {k: body[k] for k in ("titulo", "objetivo", "autor", "fecha") if body.get(k)})
    else:
        return body, []
    por_defecto = locals().get("por_defecto", {})
    for k in ("portada", "divisor"):                     # variantes de plantilla elegidas: van a la cabecera del Markdown
        if body.get(k):
            md = md.replace("---" + NL, "---" + NL + f"{k}: {body[k]}" + NL, 1) if md.startswith("---" + NL) else "---" + NL + f"{k}: {body[k]}" + NL + "---" + NL + md
    nuevo = {k: v for k, v in body.items() if k not in ("receta", "valores", "ingredientes", "meta", "titulo", "objetivo", "autor", "fecha", "portada", "divisor")}
    from engine.markdown import FORMATOS
    for k, v in por_defecto.items():
        if v and not nuevo.get(k):
            nuevo[k] = FORMATOS.get(v, v) if k == "format" else v
    return {**nuevo, "markdown": md}, av
