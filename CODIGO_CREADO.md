# Qué código creé yo (Claude) y qué es contenido

Marca de este repositorio: **todo archivo de código que escribí como constructor del servidor empieza con la línea
`[CLAUDE-CONSTRUCTOR] … El agente de contenido no lo escribe ni lo edita`** (`#` en Python, `//` en JS, `/* */` en CSS,
campo `_marca` en JSON). Lo que no lleva esa marca no es código mío.

Trabajé en dos papeles, como pedía el Prompt Maestro («el agente decide qué decir, el servidor decide cómo se ve»):

| Papel | Qué produjo | Líneas de código |
|---|---|---|
| **Agente externo** (como lo haría ChatGPT con el prompt) | `contenido/guia.json`: solo datos (texto, tablas, gráficos, referencias de imagen). Sin HTML, sin CSS, sin scripts | **0** |
| **Constructor del servidor** (lo que habría que construir una sola vez) | Todo lo de la tabla de abajo | ~1.600 |

No edité ningún archivo existente del repositorio (`teoria/`, `research_notes/`, `PROMPT_PDF.md` siguen intactos) ni
el sistema de diseño de ANURA (solo lo leí).

## Código creado por mí (marcado `[CLAUDE-CONSTRUCTOR]`)

| Archivo | Líneas | Para qué sirve |
|---|---|---|
| `servidor/render.py` | 281 | Tubería: valida el contrato → bloques a HTML → Chromium mide → pagina → PDF → auditoría → informe breve. CLI |
| `servidor/api.py` | 80 | API mínima con la biblioteca estándar: `GET /v1/designs`, `GET /v1/designs/{id}`, `POST /v1/render`, `GET /v1/files/{f}` |
| `servidor/engine/contract.py` | 48 | Valida el contrato (vocabulario cerrado de bloques, límites, filas de tabla) con errores `bloque/causa/ajuste` |
| `servidor/engine/blocks.py` | 230 | Convierte cada bloque declarativo en HTML (párrafo, lista, tabla, gráfico, kpi, cifra, aviso, imagen, flujo, escalera, rangos, línea de vida, comparación, índice) |
| `servidor/engine/charts.py` | 164 | Gráficos declarativos a SVG: barras (con error), barras horizontales, líneas, apiladas; rayado para SIMULACIÓN |
| `servidor/engine/layout.py` | 110 | Maquetación de flujo: Chromium mide cada unidad en cqw y un empaquetador llena hojas; parte tablas y listas por filas |
| `servidor/engine/pages.py` | 62 | Plantillas ANURA: portada, divisores A–D, hoja clara (coordenadas del sistema, sin moverlas) |
| `servidor/engine/assets.py` | 108 | Fuentes y símbolos incrustados, filtro de imagen duotono con trama (de `imagenes.md`), créditos |
| `servidor/engine/text.py` | 61 | Texto en línea seguro: `**negrita**`, `*cursiva*`, `` `código` ``, marcas `[FUENTE]`, `[INF]`… (escapa cualquier HTML) |
| `servidor/engine/audit.js` | 72 | Auditoría de hojas: JS de `auditoria.md` de ANURA adaptado, más desborde del pie y contraste |
| `servidor/engine/fit.js` | 18 | Reduce el tamaño de un título de una línea antes de cortarlo (regla R12) |
| `servidor/designs/anura/manifest.json` | 80 | Reglas medibles del diseño ANURA para el motor |
| `servidor/designs/anura/extras.css` | 191 | Estilos de los bloques (solo tokens ANURA, radio 0, sin degradados) |
| `servidor/tests/test_motor.py`, `ejemplo_minimo.json` | 85 | Pruebas del texto, el contrato y un render completo sin problemas de auditoría |

## Copiado sin cambios del sistema de diseño de ANURA (no es código mío)

`servidor/designs/anura/bundle.css`, `fonts/*.woff2`, `simbolos.json`, `ranas/*.png`, `drip.svg.txt`. Origen:
artifact `23sPATA5AWXcd7YeXNuYtc` (Design System).

## Contenido del agente

`contenido/guia.json` (25 secciones, 5 partes) y `contenido/LEEME.md`. Salida generada: `salida/guia.pdf`,
`salida/guia.informe.json`, `salida/contacto_grises.png`.

## Lo que NO hice (siguen pendientes del Prompt Maestro)

Word, PPTX, Excel y video; cola de trabajos asíncrona, claves de API y límites; búsqueda en Wikimedia; esquema OpenAPI y
MCP; edición por parches e identificadores estables; importación de diseños (`POST /v1/designs/import`); modo B (HTML
sin API). La API de `servidor/api.py` es síncrona y local: no la expongas a internet.
