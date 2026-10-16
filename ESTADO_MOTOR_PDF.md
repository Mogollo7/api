# ¿Cuándo está «completo» el motor de PDF? Criterios, estado real y lo que falta

**Definición de «completo»** (la tuya, traducida a pruebas): a partir de ese día, **añadir un sitio o un diseño nuevo es solo hablar con Claude**: Claude crea una carpeta
`designs/<id>/` (manifiesto, estilos, plantillas, recursos), pasa la lista de revisión y el motor lo renderiza **sin tocar código del motor**. Y un agente externo (ChatGPT, Claude…)
genera documentos con un prompt sin escribir HTML/CSS.

## Veredicto honesto (2026-10-16): NO está completo; el núcleo sí, faltan 6 cierres

El motor ya hace bien lo difícil (maquetación de flujo, paginación, gráficos estándar, auditoría, grises, variantes, no romperse ante lo no estándar). Pero **hoy un diseño nuevo
exige escribir código** (las portadas y divisores están en `pages.py` + CSS propio de ANURA), y falta el generador del Prompt Maestro. Eso es lo que impide el «solo hablar con Claude».

| # | Criterio de cierre | Estado | Evidencia / qué falta |
|---|---|---|---|
| G1 | Contrato estable y versionado | **Parcial** | Validación en código; falta publicar un JSON Schema `v1` congelado y el campo `contract` verificado |
| G2 | Vocabulario cerrado de bloques + degradación segura | **Hecho** | 20 bloques; `no_estandar.json` produce PDF con auditoría limpia |
| G3 | Maquetación: flujo, paginación, partir tablas/listas, sin solapes, sin redundancia | **Hecho** (con huecos) | Falta partir bloques compuestos (`figure`), control fino de viudas/huérfanas |
| G4 | **Diseños como datos** (nuevo diseño sin tocar el motor) | **NO hecho** | Plantillas de portada/divisor son código de ANURA. Falta: plantillas declarativas (`designs/<id>/templates/*.html` con campos `{{…}}` y ranuras), importación (`POST /v1/designs/import`) y checklist automática |
| G5 | Paletas, variantes y aprobación | **Hecho** | `palettes.json`, `variantes.json`, galería, `aprobar.py` |
| G6 | Gráficos, mapa y diagrama estándar | **Hecho** (9 tipos + flowchart) | Faltan barras agrupadas/apiladas verticales, líneas multiserie, pastel/dona, ejes de fecha, más contornos de mapa |
| G7 | Imágenes: filtro, créditos, Wikimedia | **Parcial** | `commons.py` solo probado sin red; falta caché de descargas y exigir `alt` |
| G8 | Revisión: auditoría, contraste, grises, redundancia | **Hecho** (falta regresión visual) | Falta comparar contra «golden» (píxeles) en cada cambio |
| G9 | Elementos propios del PDF | **Parcial** | Hay índice, numeración, marcadores y etiquetado. Faltan: cita, bloque de código, notas al pie, referencias, lista anidada, tamaño Carta, metadatos completos, enlaces internos en el índice |
| G10 | Operación | **Parcial** | CLI y API local. Faltan cola asíncrona, idempotencia, límites, claves, Docker |
| G11 | Aceptación con 5–6 temas distintos sin que el agente escriba código | **Parcial** | 3 documentos reales (guía, cine, no estándar) + mínimo. Faltan 2–3 de otros temas (informe, manual, currículum) |
| G12 | **Prompt Maestro y skill generados del manifiesto** | **NO hecho** | Falta `POST /v1/prompt` y `GET /v1/designs/{id}/skill` (el agente externo hoy no tiene su prompt) |

## Los 6 cierres, en orden (cuando estén, el motor está completo)
1. **C1 · Diseños declarativos (G4).** Plantillas HTML con campos, ranuras de imagen y símbolos; el motor deja de conocer «ANURA». Entregable: crear un segundo diseño (p. ej. «Cine» como diseño propio) **sin cambiar el motor**.
2. **C2 · Prompt Maestro + skill (G12).** Se generan del manifiesto: reglas, plantillas, variantes, paleta, contrato y ejemplos. Prueba: otro agente produce un PDF correcto con solo ese prompt.
3. **C3 · Elementos de documento (G9)**: `quote`, `code`, `footnote`, listas anidadas, Carta, metadatos, enlaces del índice.
4. **C4 · Gráficos que faltan (G6)**: agrupadas, multiserie, pastel/dona, fechas.
5. **C5 · Regresión visual + 3 documentos de aceptación (G8, G11).**
6. **C6 · Contrato v1 congelado (G1)**: JSON Schema, versión en el documento y en el diseño.
Operación (G10) y Wikimedia en vivo (G7) se cierran al desplegar, no bloquean «completo».

## Qué significa «completo» el día que pase
- Un diseño nuevo = carpeta + `lista de revisión` en verde (contraste ≥ 4,5; 2 variantes de portada; sin desbordes con texto corto y largo; sin redundancia; símbolos con reglas).
- Un sitio nuevo (web) = mismo diseño + `WEB.md`: ver `PLAN_PPTX.md` §9 para el frontend.
- Cambios futuros del motor pasan 17+ pruebas y la regresión visual.
