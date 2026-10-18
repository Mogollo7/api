# Plan en dos etapas: frontend, PDF, PPTX y video

Escrito el 2026-10-17. Fuente: el documento «API de documentos: especificación teórica y Prompt Maestro» (artifact) + el estado real del repositorio.
Frontend servido en `http://localhost:8765/` por `servidor/api.py` (no por `server.js`, que es otra API en el puerto 3000).

## Etapa 1 · Sonnet (HECHA salvo lo marcado)
| # | Entrega | Estado |
|---|---|---|
| 1.1 | Frontend reescrito: hero, cómo funciona, uso con agente externo (Claude+skill, otro LLM+Prompt Maestro, curl), catálogo tipo librería con modal «por dentro» y botón **Usar**, taller, formatos | Hecho (`servidor/web/app.html`, `site.css`) |
| 1.2 | API: `GET /v1/catalog`, `GET /v1/examples/{id}`, estáticos `/web/…` | Hecho (`api.py`) |
| 1.3 | Catálogo: miniaturas desde los PDF de ejemplo (`servidor/tools/catalogo.py`) | Hecho: 7 plantillas |
| 1.4 | Imágenes de Wikimedia Commons con autor y licencia (`web/img/credits.json`, pie del hero y del footer) | Hecho |
| 1.5 | Skills instaladas (globales, copiadas, revisadas antes): `brag` (commit 069432c), `remotion-*` ×12 (commit 1441a11) | Hecho |
| 1.6 | Ya presentes en el equipo: `hyperframes*`, `estudio-motion`, `prompt-master`, `ui-ux-pro-max`, `pdf`, `pptx`, `skill-creator`, `design:design-critique`, `dataviz` | Verificado |
| 1.7 | **Pendiente de la etapa:** prueba real del Prompt Maestro con un agente externo (ChatGPT u otro Claude) y revisión móvil del frontend | Pendiente |

**Pendiente por herramientas:** `soffice` (LibreOffice) no está instalado → hace falta para probar PPTX→PDF. Instalarlo antes de la Etapa 2.

## Etapa 2 · Opus (arquitectura y motor)
Cambia el modelo y pide «sigue con la Etapa 2». Orden recomendado:

1. **PPTX editable — HECHO (P1–P3 y la mayor parte de P4–P5)**, 2026-10-17:
   - `servidor/render_pptx.py` (un módulo; el plan preveía 5): el mismo JSON del PDF → 16:9 editable. Portada, agenda, divisores, secciones con partición automática (≤ 6 viñetas, ≤ 8 filas, párrafos por frases), los 24 bloques del vocabulario, gráficos nativos editables (bar, hbar, line, stack, pie/dona, hist, scatter con tendencia); box/heat/map → tabla nativa con aviso; flowchart con conectores; GIF y video incrustados; notas al pie → notas del orador.
   - Tema de PowerPoint con la paleta y las fuentes del diseño; color de texto elegido solo entre `pares_texto_permitidos`; títulos que se reducen para caber (R12).
   - Informe: `avisos`, `auditoria` (desbordes estimados, formas fuera, letra < 9,5 pt), `imagenes_necesarias`, `fuentes`.
   - API: `POST /v1/render` con `"format":"pptx-16x9"`; `GET /v1/designs/{id}/fonts.zip` (TTF de `tools/fuentes_ttf.py`). Frontend: selector de formato en el Taller y «Descargar PPTX» en el catálogo.
   - Revisión visual: `tools/pptx_png.py` (PowerPoint por COM o LibreOffice) → PNG + `contacto.png`. Pruebas: `Pptx` en `tests/test_motor.py` (28/28 con `PYTHONUTF8=1`).
   - **Falta:** variantes de diapositiva aprobables en la galería (P4), regresión contra «golden» de PPTX (P5), autoplay/bucle de video (XML de temporización), y que el servidor tenga las fuentes instaladas. Las pruebas previas fallan en Windows sin `PYTHONUTF8=1` (lecturas sin `encoding`).

   Plan original (referencia), fases P1–P5 de `PLAN_PPTX.md`: `engine/pptx/{build,theme,blocks_pptx,charts_pptx}.py` con `python-pptx` o `pptxgenjs` (ya en `node_modules`). Mismo contrato JSON, `"format":"pptx-16x9"`; partición en diapositivas; gráficos nativos; notas del orador; auditoría PPTX; regresión PPTX→PDF con LibreOffice. Criterio: el mismo JSON de `contenido/` da PDF y PPTX sin desbordes.
2. **PDF listo para producción** (G7, G10 de `ESTADO_MOTOR_PDF.md`): probar `commons.py` integrado al render (ya funciona desde este PC), cola asíncrona, `Dockerfile` construido, cuotas y retención. `POST /v1/render` pasa a devolver `job` + estado `queued|running|done|failed` y webhook opcional.
3. **Video — HECHO (motor determinista)**, 2026-10-17: `servidor/render_video.py` convierte el mismo JSON en un proyecto HyperFrames
   (portada, aperturas de parte, cifras con contador, barras, dispersión, citas, listas, ideas y cierre, en la grilla del tempo) y lo renderiza a MP4
   16:9 o 9:16. Pasa `npx hyperframes check` (lint, ejecución, maquetación, contraste). API: `POST /v1/render` con `format: video-*` → 202 + cola
   propia; `GET /v1/jobs/{id}` → `video` (MP4) y `proyecto` (zip para pulir con skills). `GET /v1/designs/{id}/motion` = estilo para
   `/estudio-motion` + brief para `/brag`. Skills instaladas: brag, remotion-* (12), hyperframes*, estudio-motion. **Falta:** música/efectos
   (hoy sin audio; se añaden con /estudio-motion o media-use) y licencia de Remotion si se usa en lo comercial.

   Plan original (referencia), video: worker aparte con su cola. Dirección con `/brag` (video de lanzamiento) o `/estudio-motion` (explicativos y motion graphics); construcción con Hyperframes (HTML/CSS, encaja con las plantillas del diseño) y Remotion como alternativa; bloque `media` común a PDF/web/PPTX; `format: video-16x9|video-9x16`; tope de duración y peso. Revisar licencia de Remotion antes de uso comercial.
4. **Skill de gráficos propia** (`/skill-creator` sobre `dataviz`) y **skill por diseño** generada desde el manifiesto (ya existe `GET /v1/designs/{id}/skill`).
5. **Frontend, segunda pasada:** activar las tarjetas PPTX y Video del catálogo con vista previa real (diapositivas y reproductor), galería de trabajos publicados, ranuras de imagen con búsqueda en Commons.

## Cómo cambiar de modelo
En la app: selector de modelo de la sesión → Opus. Luego escribe: «Etapa 2 del plan, empieza por el punto 1».
