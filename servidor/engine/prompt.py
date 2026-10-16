# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Generador del PROMPT MAESTRO y de la SKILL de un diseño, a partir de su manifiesto, su registro de variantes y la especificación del contrato.
Nada se escribe a mano por diseño: si cambia el diseño o un bloque, el prompt cambia solo."""
import json
from pathlib import Path

from . import muestras, spec

HERE = Path(__file__).resolve().parent.parent

AVISOS = [
    ("tipo de bloque … fuera del vocabulario", "usa un bloque de la lista; si ninguno sirve, `callout` o, como último recurso, `custom`"),
    ("gráfico … no es estándar / N elementos y el estándar admite M", "cambia de tipo o agrupa categorías; o usa `table`"),
    ("subtítulo / título de figura repite el titular (redundancia)", "no repitas el titular: borra el subtítulo o dale otra información"),
    ("párrafo de N caracteres", "divídelo en dos bloques `p` o conviértelo en lista"),
    ("mide N cqw y la hoja admite M", "parte el bloque en dos o acorta el contenido"),
    ("imagen sin alt ni pie", "añade `caption` o `alt`"),
    ("variante … no existe / rechazada", "elige otra del catálogo de variantes de este diseño"),
    ("contraste / correcciones_contraste", "no hace falta actuar: el servidor corrige el color; si se repite, evita pedir `tone` poco legibles"),
]


def _compact(x):
    return json.dumps(x, ensure_ascii=False, separators=(",", ":"))


def prompt_maestro(design: str, fmt: str = "pdf-a4", palette: str = "default", variantes: dict = None, modo: str = "B", corto: bool = False) -> str:
    dd = HERE / "designs" / design
    m = json.loads((dd / "manifest.json").read_text(encoding="utf-8"))
    pals = json.loads((dd / "palettes.json").read_text(encoding="utf-8"))
    reg = json.loads((dd / "variantes.json").read_text(encoding="utf-8"))["variantes"]
    roles = {**m["palette"]["roles"], **(pals.get(palette, {}) if isinstance(palette, str) else palette)}
    rt = m.get("reglas_texto", {})
    var = variantes or {}
    L = []
    A = L.append
    A(f"# Prompt Maestro · diseño «{m['name']}» v{m['version']} · contrato v{spec.CONTRACT_VERSION}")
    A("")
    A("## 1. Tu papel")
    A("Eres el **agente de contenido**. Decides **qué dice** el documento y **qué bloque** lo muestra mejor. **El servidor decide cómo se ve** (tipografía, color, márgenes, paginación, gráficos, auditoría).")
    A("- **No escribas HTML, CSS, scripts ni código de ningún tipo.** Tu única salida es **UN objeto JSON válido** que cumpla el contrato; nada de texto fuera del JSON.")
    A("- Si algo no encaja en el vocabulario de bloques, usa `callout` (nota) y, solo como último recurso, `custom`. No inventes tipos de bloque ni campos.")
    A("")
    A("## 2. Este documento")
    A(f"- Diseño `{design}` · formato `{fmt}` · paleta `{palette if isinstance(palette, str) else 'propia'}`.")
    A("- Roles de color (el diseño los usa; tú nunca escribes colores): " + ", ".join(f"`{k}` {v}" for k, v in roles.items()) + ".")
    kinds = {}
    for v in reg:
        if v["tipo"] in ("portada", "divisor", "hoja"):
            kinds.setdefault(v["tipo"], []).append(v)
    A("- **Variantes** (elige por nombre; `auto` deja decidir al servidor):")
    for k, vs in kinds.items():
        A(f"  - {k}: " + "; ".join(f"`{v['id']}` {v['nombre']} ({v['estado']})" for v in vs))
    if var:
        A("- Variantes pedidas por el usuario: " + ", ".join(f"{k}={v}" for k, v in var.items()) + ". Úsalas.")
    A("")
    A("## 3. Estructura del contrato")
    A("```json")
    A('{"contract":"%s","design":"%s","format":"%s","palette":"%s","options":{"seed":7},' % (spec.CONTRACT_VERSION, design, fmt, palette if isinstance(palette, str) else "default"))
    A(' "meta":{"title":"…","author":"…","date":"Octubre 2026","version":"Vol. 01 · v0.1","header_left":["línea 1","línea 2"],"footer":"…"},')
    A(' "document":{"cover":{"variant":"auto","vertical":"PALABRA","title":"…","text":"…"},')
    A('   "parts":[{"id":"p1","title":"Parte corta","desc":"…","divider":"auto","sections":[{"id":"s1","title":"Titular de la hoja","blocks":[ … ]}]}]}}')
    A("```")
    A(f"- Portada: `title` ≤ {spec.COVER['title']['max']} caracteres, `vertical` ≤ {spec.COVER['vertical']['max']}. Parte: `title` ≤ {spec.PART['title']['max']}. Sección: `title` ≤ {rt.get('titular_max', 60)} (se muestra en mayúsculas: escríbelo en minúsculas normales).")
    A("- Una sección = **una idea** (una hoja o dos). Orden recomendado: titular → frase clave → bloque principal (gráfico/tabla/lista) → interpretación → aviso.")
    A("")
    A("## 4. Bloques disponibles" + (" (resumen)" if corto else ""))
    for name, s in spec.BLOCKS.items():
        flds = ", ".join(f"{k}{'*' if f.get('req') else ''}" for k, f in s["fields"].items())
        if corto:
            A(f"- `{name}`: {s['desc']} Campos: {flds}.")
        else:
            A(f"### `{name}` — {s['desc']}")
            for k, f in s["fields"].items():
                ex = f" valores: {f['enum']}" if f.get("enum") else ""
                mx = f" (máx {f['max']})" if f.get("max") else ""
                A(f"- `{k}`{'*' if f.get('req') else ''} ({f['type']}{mx}){ex}: {f['desc']}")
            A("```json\n" + _compact(s["example"]) + "\n```")
    A("(* obligatorio) Texto con marcas: `**negrita**`, `*cursiva*` (nombres científicos), `` `código` ``, `[^1]` (nota al pie), `[FUENTE] [CALC] [INF] [SIN FUENTE] [RESUMEN] [SIM]` (etiquetas).")
    A("")
    A("## 5. Gráficos, mapa y diagrama estándar")
    for t, c in spec.CHART_TYPES.items():
        A(f"- `{t}` (≤ {c['limit']}) — {c['uso']}. Datos: {c['data']}")
    A("- Un solo resalte (`hi:true`) por gráfico. Título corto que **no repita el titular**; pie «Figura N. …». Diagrama: nodos `start|process|decision|io|end`, ≤ 14 nodos, ≤ 3 por capa, decisiones con salidas «sí»/«no».")
    A("- Elige: **pocos números → `kpi`/`big`**; **comparar categorías → `bar`/`hbar`**; **evolución → `line`**; **partes de un todo → `pie` (≤ 7) o `stack`**; **distribución → `hist`/`box`**; **relación → `scatter`**; **correlaciones → `heat`**; **lugares → `map`**; **proceso → `flow` o `flowchart`**; **muchos datos con texto → `table`**.")
    A("")
    A("## 6. Reglas de redacción (se comprueban automáticamente)")
    A(f"1. {rt.get('idioma', 'Español neutro, frases cortas.')} Números con **coma decimal** y puntos de millar: `62,9 %`, `5.818`. Fechas: «Octubre 2026».")
    A("2. **Nunca inventes cifras.** Si falta un dato escribe **«dato pendiente»**. Una estimación va marcada `[SIM]`/SIMULACIÓN (y `sim:true` en el gráfico); nunca como resultado.")
    A("3. **Anti-redundancia:** un texto aparece **una sola vez por hoja**. No repitas el titular en el subtítulo, en el título del gráfico, en el pie ni en un aviso; no repitas la fecha, la versión ni el título del documento en otros campos. El servidor omite lo repetido y lo anota.")
    A("4. Cada afirmación con fuente lleva su etiqueta; lo que es inferencia tuya lleva `[INF]`; lo que no encontraste, `[SIN FUENTE]`.")
    A("5. **Imágenes:** usa solo rutas que te hayan dado. Si falta, escribe `need` («Foto de …») y el servidor marcará «IMAGEN NECESARIA». Toda imagen lleva `caption` o `alt` y, si es ajena, autor y licencia en el crédito.")
    A("6. Listas ≤ 14 ítems; tablas ≤ 40 filas (se parten solas); párrafos ≤ 1.400 caracteres; una hoja admite unas 350 palabras.")
    A("7. No pidas tonos, colores ni tamaños: los decide el diseño. Los elementos con tono (`callout.tone`, tablas `tone`) solo usan los valores listados.")
    A("")
    A("## 7. Cómo entregar" + (" (modo A · API)" if modo == "A" else " (modo B · archivo)"))
    if modo == "A":
        A("`POST /v1/render` con el JSON; el servidor responde con un trabajo, un informe breve y la URL del PDF. Si el informe trae `avisos` o `auditoria`, **corrige solo el contenido** y vuelve a enviar.")
    else:
        A("Entrega el JSON en un archivo `documento.json`. La persona lo convierte con `python servidor/render.py documento.json -o documento.pdf --imagenes <carpeta>` y te pasa el informe `*.informe.json`. **Corrige solo el contenido** según el informe.")
    A("")
    A("## 8. Si el informe trae avisos (qué hacer)")
    for a, b in AVISOS:
        A(f"- {a} → {b}.")
    A("")
    A("## 9. Autochequeo antes de entregar")
    A("- [ ] JSON válido y completo (`contract`, `design`, `format`, `meta`, `document.cover`, `parts`).  - [ ] ids únicos.  - [ ] titulares cortos y sin repetirse.  - [ ] ninguna cifra inventada.")
    A("- [ ] cada gráfico dentro de sus límites y con datos reales.  - [ ] cada imagen con `caption`/`alt`.  - [ ] etiquetas de fuente donde corresponde.  - [ ] nada fuera del JSON.")
    if not corto:
        A("")
        A("## 10. Ejemplo mínimo completo")
        d = muestras.doc_muestra(design, False, "auto", "auto", False, palette if isinstance(palette, str) else "default")
        d["document"]["parts"] = [{**d["document"]["parts"][0], "sections": d["document"]["parts"][0]["sections"][:2]}]
        d["document"]["parts"][0]["sections"][0]["blocks"] = d["document"]["parts"][0]["sections"][0]["blocks"][:1]
        d["document"]["parts"][0]["sections"][1]["blocks"] = d["document"]["parts"][0]["sections"][1]["blocks"][:2]
        A("```json\n" + json.dumps(d, ensure_ascii=False, indent=1)[:3500] + "\n```")
    A("")
    A("## CONTENIDO DEL USUARIO")
    A("{{CONTENIDO}}")
    return "\n".join(L) + "\n"


def skill_md(design: str) -> str:
    dd = HERE / "designs" / design
    m = json.loads((dd / "manifest.json").read_text(encoding="utf-8"))
    body = prompt_maestro(design, modo="B", corto=False).replace("{{CONTENIDO}}", "(el contenido llega en la conversación)")
    return (f"---\nname: documentos-{design}\ndescription: Genera el JSON de contenido para crear un documento (PDF) con el diseño «{m['name']}» sin escribir código: "
            f"portada, partes, secciones, tablas, gráficos estándar, mapas, diagramas de flujo e imágenes. Úsala cuando la persona pida un PDF, informe, guía o dossier con este diseño.\n---\n\n"
            "# Skill: documentos con el diseño " + m["name"] + "\n\nArchivos junto a esta skill: `contrato.schema.json` (JSON Schema del contrato), `ejemplo.json` (documento de muestra), `PROMPT_CORTO.md`.\n\n" + body)
