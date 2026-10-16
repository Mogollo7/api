# Estado del motor de PDF (actualizado 2026-10-16, tras los cierres C1–C6)

**Veredicto:** el motor de PDF queda **completo para el uso previsto**: con un diseño fijo, crear un PDF es (1) pedir el Prompt Maestro del diseño, (2) que un agente escriba el JSON de contenido, (3) `render.py` y revisar el informe.
**Añadir un diseño nuevo** = copiar uno (`crear_diseno.py`), editar y pasar la lista de revisión (`validar_diseno.py`): ya no se toca el motor. Lo que queda no bloquea; está abajo con su nombre.

| # | Criterio | Estado | Evidencia |
|---|---|---|---|
| G1 | Contrato estable y versionado | **Hecho** | `engine/spec.py` (única fuente) → validador, `servidor/contrato.schema.json` y Prompt Maestro; el documento declara `"contract":"1.0"` y el servidor avisa si no coincide |
| G2 | Vocabulario cerrado + degradación segura | **Hecho** | 24 bloques; `tests/no_estandar.json` (13 casos) produce PDF con auditoría limpia |
| G3 | Maquetación, paginación, anti-solape, anti-redundancia | **Hecho** | flujo medido en Chromium, tablas/listas/refs se parten por filas, bloques gigantes se reducen con aviso |
| G4 | Diseños como datos | **Hecho** | portadas y divisores son **plantillas declarativas** (`designs/<id>/templates/*.html`, `engine/tpl.py`); `designs/LEEME.md`; **segundo diseño «editorial»** creado con `crear_diseno.py` + `validar_diseno.py` sin tocar el motor |
| G5 | Paletas, variantes, aprobación | **Hecho** | `palettes.json`, `variantes.json` (≈ 60 ids), `galeria.py`, `aprobar.py` |
| G6 | Gráficos, mapa, diagrama estándar | **Hecho** | bar (simple, agrupadas, apiladas), hbar, line (multiserie, fechas), stack, pie/dona, hist, box, scatter, heat, map, flowchart |
| G7 | Imágenes: filtro, créditos, Wikimedia | **Parcial** | filtro, créditos y `alt` obligatorio: hecho. `commons.py` con caché, pero la llamada real a Wikimedia **no se pudo probar** desde la nube |
| G8 | Revisión: auditoría, contraste, grises, redundancia, regresión | **Hecho** | `regresion.py` compara 5 documentos hoja a hoja contra golden (`tests/golden/`) |
| G9 | Elementos de documento | **Hecho** (salvo ecuaciones) | índice con enlaces y páginas, numeración, marcadores, etiquetado y metadatos (pikepdf), cita, código, referencias, notas al pie, listas anidadas, `media` (póster) |
| G10 | Operación | **Parcial** | CLI y API (idempotente, clave `API_KEY`, límites de cuerpo y hojas, un render a la vez), `Dockerfile` **sin construir** (no hay Docker en la nube). Faltan cola asíncrona, cuotas por clave y retención |
| G11 | Aceptación con temas distintos | **Hecho** | 5 documentos: guía de IA, análisis «cine» (paridad con la referencia), informe de ventas, manual de procedimiento, ficha de proyecto; 2 diseños |
| G12 | Prompt Maestro y skill desde el manifiesto | **Hecho** | `servidor/prompt.py`, `POST /v1/prompt`, `GET /v1/designs/{id}/skill`; `salida/skills/` |

## Pendiente (no bloquea el «completo»; necesita tu PC o decisiones tuyas)
1. **Probar el Prompt Maestro con un agente externo real** (ChatGPT, otro Claude): yo escribí los 5 documentos, así que la prueba independiente no está hecha. Pásale `salida/skills/documentos-<diseño>/PROMPT_MAESTRO.md` + tu contenido y corre `render.py` sobre lo que devuelva.
2. **Construir el Docker** y probar `commons.py` contra Wikimedia en tu PC.
3. **Letter** y otros formatos: el motor lo parametriza (`formats_dims`), pero ningún diseño lo declara todavía.
4. Huecos finos: ecuaciones, partir una `figure` entre hojas, control de viudas y huérfanas, tablas de cabecera múltiple.
5. Operación en producción: cola, cuotas, retención.

## Cómo se comprueba que sigue completo
`python -m unittest discover -s servidor/tests` (26 pruebas) · `python servidor/regresion.py --comprobar` · `python servidor/validar_diseno.py <diseño>` · informe de cada render (`avisos`, `auditoria`, `correcciones_contraste`).
