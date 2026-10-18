#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Carga la biblioteca (servidor/biblioteca/) desde lo que ya existe: diseños, variantes, bloques del contrato y presets de animación.
"""python servidor/tools/biblioteca_cargar.py     (vuelve a escribir las entradas generadas; no toca las que creó un agente con save_style)

Estilos y plantillas salen de servidor/designs/*, los componentes de engine/spec.py y las animaciones de ANIMACIONES (abajo).
El texto de cada entrada es el que busca `search_library`; cada una lleva además su SKILL.md de una pantalla."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import biblioteca  # noqa: E402
from engine import spec  # noqa: E402

SINONIMOS = {"p": "párrafo texto", "h": "subtítulo etiqueta", "list": "lista viñetas", "table": "tabla filas columnas", "chart": "gráfico barras líneas",
             "kpi": "cifras indicadores métricas", "quote": "cita frase", "figure": "figura imagen foto", "code": "código", "callout": "aviso nota destacado"}

ANIMACIONES = [
    ("fade-up", "Aparecer subiendo", "Entrada suave: el elemento sube unos píxeles mientras aparece. La de uso general para títulos y párrafos.",
     {"duracion": "0.6 s", "distancia": "40 px", "retraso": "0 s"}, ["aparecer", "entrada", "titulo", "suave"]),
    ("stagger-grid", "Cuadrícula escalonada", "Los elementos de una cuadrícula o lista entran uno tras otro (retraso corto entre ellos). Para tarjetas, cifras y logos.",
     {"duracion": "0.5 s", "escalon": "0.08 s", "desde": "start|center|end"}, ["escalonado", "tarjetas", "rejilla", "cifras"]),
    ("count-up", "Contador", "Un número sube desde 0 hasta su valor. Para cifras clave en video.",
     {"duracion": "1.2 s", "decimales": "0", "formato": "texto con prefijo/sufijo"}, ["cifra", "numero", "kpi", "contador"]),
    ("wipe-reveal", "Revelado con cortina", "Una cortina de color descubre el titular de izquierda a derecha. Estilo brutalista, para portadas y divisores.",
     {"duracion": "0.7 s", "color": "rol del diseño", "direccion": "izquierda|derecha"}, ["titular", "cortina", "portada", "brutalista"]),
    ("line-draw", "Trazo de línea", "Una línea o barra se dibuja de un extremo al otro. Para gráficos de barras, reglas y subrayados.",
     {"duracion": "0.9 s", "grosor": "rol del diseño", "sentido": "horizontal|vertical"}, ["grafico", "barras", "linea", "subrayado"]),
    ("anime-entrada-escalonada", "Entrada escalonada (web, anime.js)", "En la salida web animada los hijos de cada sección suben y aparecen uno tras otro al entrar en pantalla. Se activa solo con format web-animada.",
     {"duracion": "700 ms", "escalon": "90 ms", "ease": "outExpo"}, ["web", "anime", "entrada", "escalonado", "scroll"]),
    ("anime-contador", "Contador de cifras (web, anime.js)", "Las cifras clave de la web animada cuentan desde 0 hasta su valor al aparecer; respeta prefijo, sufijo y decimales.",
     {"duracion": "1100 ms", "ease": "outCubic"}, ["web", "anime", "cifra", "contador", "kpi"]),
    ("three-fondo-3d", "Fondo 3D de portada (three.js)", "Icosaedro de alambre girando detrás de la portada web, con el color de acento del diseño. Solo desde la línea de comandos: python servidor/web.py doc.json --animar --fondo3d.",
     {"rotacion": "0.003/0.005 rad por cuadro", "opacidad": "0.35"}, ["web", "three", "3d", "portada", "fondo"]),
    ("lottie-reproducir", "Animación Lottie (lottie-web)", "lottie-web está en servidor/video/vendor/lottie.min.js (MIT). Aún no hay bloque del contrato que lo use: se incrusta a mano en una página web con lottie.loadAnimation({container, path, loop:true}).",
     {"path": "archivo .json de Lottie", "loop": "true|false"}, ["lottie", "animacion", "web", "vector"]),
]



USO_VIDEO = {"fade-up": {"options": {"video": {"entrada": "fade-up"}}}, "wipe-reveal": {"options": {"video": {"entrada": "wipe-reveal"}}},
             "stagger-grid": {"options": {"video": {"escalon": 0.12}}}}      # parámetros que lee render_video.Director


def escribe(e, skill=True):
    d = biblioteca.DIR / biblioteca.CARPETA[e["tipo"]]
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{e['id']}.json").write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
    if skill:
        (biblioteca.DIR / "skills").mkdir(exist_ok=True)
        (biblioteca.DIR / "skills" / f"{e['tipo']}-{e['id']}.md").write_text(biblioteca.skill_md(e), encoding="utf-8")


def main():
    n = {"estilo": 0, "plantilla": 0, "componente": 0, "animacion": 0}
    for dd in sorted((ROOT / "designs").iterdir()):
        mf = dd / "manifest.json"
        if not mf.exists():
            continue
        m = json.loads(mf.read_text(encoding="utf-8"))
        pal = json.loads((dd / "palettes.json").read_text(encoding="utf-8")) if (dd / "palettes.json").exists() else {}
        roles = m.get("palette", {}).get("roles", {})
        fams = sorted({f["family"] for f in m.get("fonts", [])})
        estilo = m.get("estilo", "brutalismo")
        escribe({"id": dd.name, "tipo": "estilo", "nombre": m.get("name", dd.name), "version": m.get("version", "1"),
                 "descripcion": f"Familia visual «{estilo}»: {len(roles)} colores por rol, fuentes {', '.join(fams)}, contraste mínimo {m.get('palette', {}).get('min_contraste_texto', 4.5)}:1.",
                 "tags": [estilo, "paleta", "tipografia", *[f.lower() for f in fams], *list(pal)[:6]], "uso": "Elige el estilo cuando el usuario no trae uno; si trae una imagen, busca el parecido.",
                 "parametros": {"roles": "color por rol (negro, bosque, hoja, vivo, ocre, crema, arena)", "formatos": ", ".join(m.get("formats", []))},
                 "ejemplo": {"design": dd.name, "palette": "default"}, "paleta": roles, "fuentes": fams, "design": dd.name, "origen": "repositorio",
                 "licencia": ", ".join(sorted({f.get("licencia", "") for f in m.get("fonts", []) if f.get("licencia")})) or "propia"})
        n["estilo"] += 1
        vf = dd / "variantes.json"
        for v in (json.loads(vf.read_text(encoding="utf-8")).get("variantes", []) if vf.exists() else []):
            escribe({"id": f"{dd.name}-{v['id'].lower()}", "tipo": "plantilla", "nombre": f"{v['nombre']} ({v['tipo']})", "version": "1",
                     "descripcion": v.get("uso", ""), "tags": [v["tipo"], v.get("nivel", ""), v.get("origen", "").lower(), v.get("estado", "")], "design": dd.name,
                     "uso": f"Variante {v['id']} del diseño {dd.name}; se elige en options.variants.{v['tipo']}.", "ejemplo": {"options": {"variants": {v["tipo"]: v["id"]}}},
                     "origen": "repositorio", "licencia": "propia"})
            n["plantilla"] += 1
    for k, b in spec.BLOCKS.items():
        campos = {f: f"{x['type']}{' (obligatorio)' if x.get('req') else ''} — {x.get('desc', '')}" + (f" Máx. {x['max']}." if x.get("max") else "") for f, x in b["fields"].items()}
        lim = [f"{f} ≤ {x['max']}" for f, x in b["fields"].items() if x.get("max")]
        escribe({"id": k, "tipo": "componente", "nombre": f"Bloque «{k}»", "version": spec.CONTRACT_VERSION, "descripcion": b["desc"], "tags": [k, *SINONIMOS.get(k, "").split()],
                 "uso": b["desc"], "parametros": campos, "ejemplo": b.get("example"), "origen": "engine/spec.py", "licencia": "propia",
                 "error_tipico": ("Pasarse del límite de longitud (" + "; ".join(lim) + "): el motor recorta o reduce con aviso." if lim else "Olvidar un campo obligatorio: el contrato rechaza el documento.")})
        n["componente"] += 1
    for k, c in spec.CHART_TYPES.items():
        escribe({"id": f"grafico-{k}", "tipo": "componente", "nombre": f"Gráfico «{k}»", "version": spec.CONTRACT_VERSION, "descripcion": f"Gráfico {k}: {c['uso']}. Máximo {c['limit']} elementos.",
                 "tags": ["grafico", "chart", k], "uso": c["uso"], "parametros": {"data": c["data"]},
                 "ejemplo": {"type": "chart", "chart": {"type": k, "data": "…"}}, "origen": "engine/charts.py", "licencia": "propia",
                 "error_tipico": f"Pasar más de {c['limit']} elementos: el motor lo degrada con aviso."})
        n["componente"] += 1
    for i, nombre, desc, par, tags in ANIMACIONES:
        escribe({"id": i, "tipo": "animacion", "nombre": nombre, "version": "1", "descripcion": desc, "tags": tags, "parametros": par, "origen": "servidor/video/vendor (anime.js 4.5 · three 0.186 · lottie-web 5.13)" if i.startswith(("anime", "three", "lottie")) else "GSAP 3.14.2 (servidor/video/gsap.min.js)",
                 "licencia": "MIT" if i.startswith(("anime", "three", "lottie")) else "GSAP «no charge» (uso propio; revisar usos prohibidos si se distribuye)", "ejemplo": USO_VIDEO.get(i, {"automatico": True}),
                 "uso": ("Se activa con options.video: " + json.dumps(USO_VIDEO[i], ensure_ascii=False)) if i in USO_VIDEO else "Ya va incluida: el director de video la aplica sola en cifras y barras.", "error_tipico": "Duraciones largas (> 1.5 s) retrasan la escena: el video de la API dura ≤ 120 s."})
        n["animacion"] += 1
    print("biblioteca:", n)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
