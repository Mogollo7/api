# Qué código creé yo (Claude) y qué es contenido

Marca: **todo archivo de código que escribí como constructor empieza con `[CLAUDE-CONSTRUCTOR]`** (`#` en Python, `//` en JS, `/* */` en CSS, `_marca` en JSON).
Lo que no la lleva no es código mío.

| Papel | Qué produjo | Líneas de código |
|---|---|---|
| **Agente externo** (como lo haría ChatGPT con el prompt) | `contenido/guia.json`, `contenido/cine_ejemplo.json`, `servidor/tests/*.json`: solo datos, sin HTML/CSS/scripts | **0** |
| **Constructor del servidor** | La tabla de abajo | ~4428 |

No edité ningún archivo preexistente (`teoria/`, `research_notes/`, `PROMPT_PDF.md`) ni el artifact del sistema de diseño (solo lo leí).

## Código creado por mí

| Archivo | Líneas | Para qué sirve |
|---|---|---|
| `servidor/render.py` | 300 | Tubería PDF: contrato → bloques → medir → paginar → PDF → corrección de contraste → auditoría → informe |
| `servidor/api.py` | 80 | API local mínima (biblioteca estándar) |
| `servidor/web.py` | 164 | Salida web y guía de estilo atómica del mismo contrato |
| `servidor/galeria.py` | 211 | Galería de variantes con el motor real, con aprobación y exportación |
| `servidor/aprobar.py` | 49 | Aplica las aprobaciones al registro de variantes |
| `servidor/engine/contract.py` | 52 | Contrato: errores solo estructurales; lo demás, avisos |
| `servidor/engine/blocks.py` | 357 | Bloques → HTML, con degradación segura y bloque custom saneado |
| `servidor/engine/charts.py` | 395 | Gráficos estándar: bar, hbar, line, stack, hist, box, scatter, heat, map |
| `servidor/engine/diagram.py` | 133 | Diagrama de flujo estándar por capas |
| `servidor/engine/layout.py` | 116 | Maquetación de flujo y paginación (reduce bloques gigantes) |
| `servidor/engine/pages.py` | 159 | Plantillas: portadas CV-1…CV-4, divisores DV-A…DV-F, hoja clara |
| `servidor/engine/assets.py` | 135 | Fuentes, símbolos, duotono, repintado de arte por paleta, créditos |
| `servidor/engine/atoms_svg.py` | 34 | Átomos vectoriales del cartel: franja, código de barras, cruz, X en caja |
| `servidor/engine/variants.py` | 54 | Registro de variantes y aprobación |
| `servidor/engine/paleta.py` | 41 | Revisión de paleta: contraste y claridad en grises |
| `servidor/engine/text.py` | 61 | Texto en línea seguro |
| `servidor/engine/audit.js` | 73 | Auditoría de hojas (superposición, desborde, contraste) |
| `servidor/engine/contrast_fix.js` | 32 | Protocolo en grises: corrige texto que no se distingue |
| `servidor/engine/fit.js` | 19 | Ajuste de títulos (ancho, alto, rellenar) |
| `servidor/tools/leer_pdf.py` | 189 | Lector eficiente de PDF de referencia: resumen, paleta exacta y contacto |
| `servidor/tools/descomponer.py` | 222 | Descompone una imagen en átomos, con recortes y SVG |
| `servidor/tools/commons.py` | 72 | Búsqueda en Wikimedia Commons con licencia (para tu PC) |
| `servidor/designs/anura/manifest.json` | 354 | Reglas medibles del diseño |
| `servidor/designs/anura/extras.css` | 288 | Estilos de bloques y plantillas (solo tokens ANURA) |
| `servidor/designs/anura/palettes.json` | 21 | Paletas por roles: anura y cine |
| `servidor/designs/anura/variantes.json` | 595 | Registro de variantes con estado |
| `servidor/web/web.css` | 71 | Kit web atómico |
| `servidor/tests/test_motor.py` | 151 | 15 pruebas |

## Documentos míos (no son código)
`CLAUDE.md` (contrato para futuras sesiones), `ESTANDARES.md` (gráfico, mapa y diagrama de flujo estándar, y qué pasa con lo no estándar), `WEB.md` (reglas web y diseño atómico),
`referencias/` (lecturas de las referencias), `servidor/README.md`, este archivo.

## Copiado sin cambios del sistema de diseño ANURA (no es código mío)
`servidor/designs/anura/bundle.css`, `fonts/*.woff2`, `simbolos.json`, `ranas/*.png`, `drip.svg.txt`. Origen: artifact `23sPATA5AWXcd7YeXNuYtc`.

## Salidas generadas
`salida/guia.pdf` (70 hojas) · `salida/cine_ejemplo.pdf` (paridad con la referencia, 15 hojas) · `salida/galeria/` (variantes para aprobar) · `salida/web/` (web y guía de estilo) ·
`salida/contacto_grises_*.png` · `*.informe.json`.

## Lo que NO hice
Word, PPTX, Excel y video; cola asíncrona, claves de API, MCP, OpenAPI; edición por parches e identificadores estables; importación de diseños; modo B (HTML sin API);
la llamada real a la API de Wikimedia (solo está probado su análisis sin red); el artifact de ANURA no se modificó (las variantes viven en el repo, a la espera de tu aprobación).
El contorno de Colombia es esquemático, no oficial.
