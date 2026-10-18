# Cómo se miden los tokens (CON vs SIN myStyle)

Comando: `python servidor/tools/tokens.py` → `servidor/web/stats/tokens.json` (lo muestra la ruta /estadisticas). Sin dependencias nuevas.

## Contador
- Con `ANTHROPIC_API_KEY`: endpoint `count_tokens` de Anthropic (**exacto**).
- Sin clave: **estimado** = caracteres / 3,6 (marcado `estimado: true`). Español con símbolos de código ≈ 3,4–3,9 caracteres por token; el error es pequeño frente a las diferencias que se miden (×10 entre CON y SIN), pero las cifras absolutas son aproximadas.

## Fórmula
```
CON  = tokens(Prompt Maestro corto) + tokens(contrato JSON compacto) + tokens(informe breve de la API) + 1 corrección
SIN  = tokens(artefacto escrito a mano) × factor de iteraciones
ahorro % = 1 − CON / SIN
```
- **Contrato JSON:** el de cada `contenido/*.json`, en JSON compacto (lo que el agente escribe).
- **Informe:** lo que devuelve la API a un agente (`estado`, `job`, URL, `avisos`…), tal como lo recorta `herramientas.Cliente.short`.
- **1 corrección:** un parche con un bloque promedio (tokens del contrato ÷ nº de bloques) + 40 de estructura.
- **Artefacto a mano, por formato:**
  - PDF: el HTML+CSS+SVG que produce el motor (`salida/*.html`) **sin los data: URI** (imágenes y fuentes). Incluye el CSS del diseño (cota alta). `ahorro_pct_cota_baja` repite la cuenta **sin los bloques `<style>`** (el agente reutilizaría el CSS): es el ahorro mínimo defendible.
  - PowerPoint: script python-pptx equivalente, **por fórmula** sobre el .pptx generado: 650 base + por diapositiva 90 + por forma 60 + tokens de su texto + 10 por celda + 80 y 12 por punto en gráficos.
  - Word: python-docx equivalente: 500 base + 25 por párrafo + tokens del texto + 10 por celda + 60 por imagen.
  - Excel: openpyxl equivalente: 400 base + 15 por fila + 9 por celda con valor + 120 por gráfico.
  - Video: la composición HyperFrames (`index.html`) que genera el director, **medida** sin renderizar el MP4.
- **Factor de iteraciones:** central **3**, rango 2–4. Evidencia del proyecto: crear un estilo costó 4 iteraciones visuales (`referencias/prompt-master/gasto.json`) y los renders de los documentos de muestra necesitaron de 1 a 2 rondas de corrección con avisos del motor; sin motor, esas rondas son reescrituras del artefacto. **Es un supuesto**, no una medida: el JSON deja ver los resultados con 2 y con 4 (`sin.rango_factor`).

## Límites (leer antes de citar cifras)
- Las cifras de PPTX, Word y Excel «a mano» son **fórmulas**, no scripts reales escritos por un agente. El PDF y el video son medidas directas del artefacto del motor.
- En Excel y en video de documentos con pocas tablas/cifras el ahorro es bajo o negativo: ahí escribir a mano es barato y el prompt maestro pesa más. Se muestran tal cual.
- No se midió calidad: CON incluye validación (márgenes, contraste, redundancia); SIN no la tiene y el agente no sabría que falla.
- Las definiciones de herramientas (MCP u OpenAPI) se pagan **una vez por conversación**, no por documento: van aparte en `agentes`.
- El coste de «crear un estilo» sale de `referencias/prompt-master/gasto.json`, medido con el contador de la sesión (aproximado).

## Con receta (supermercado)
`recetas` en `tokens.json`: por cada receta, lo que gasta un agente en `list_recipes` (descripción corta) + `recipe_get` (solo los huecos) + `create_from_recipe` (3 huecos cambiados) + el informe corto. No incluye el contrato JSON ni el Markdown: el contenido por defecto ya está en la receta.
Las definiciones de herramientas se pagan una vez por conversación, no por documento (ver `agentes` en el mismo archivo). Mismo contador (estimado: caracteres / 3,6).
