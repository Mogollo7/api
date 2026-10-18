# Hacer documento (PDF, Word o Excel)

Sirve para: informe, propuesta, acta, manual, ficha de proyecto, guía, comparativo, plan trimestral, reporte de datos, hoja de cálculo.

Recetas: `informe_negocio`, `propuesta_comercial`, `manual_procedimiento`, `ficha_proyecto`, `acta_reunion`, `guia_pasos`, `comparativo`, `plan_trimestral`, `reporte_datos`, `hoja_calculo`.

## Pasos
1. `list_recipes {"q":"acta de reunión"}`
2. `recipe_get {"id":"acta_reunion"}` y lee los huecos.
3. `create_from_recipe {"receta":"acta_reunion","valores":{"<hueco>":"<valor>"},"formato":"pdf"}`
   - Word: `"formato":"docx"`. Excel: `"formato":"xlsx"`.
   - Listas dentro de `valores` como `[[valor, etiqueta, nota], …]`.
4. Sin receta exacta: `compose {"ingredientes":[{"id":"…","valores":{…}}],"titulo":"…"}`.
5. Sin nada: Markdown con `create_pdf`, o `render` con `format` `docx-a4` (Word) o `xlsx` (Excel).

## Markdown (si hace falta)
- Cabecera: `--- titulo / objetivo / formato / estilo / paleta / portada / divisor / autor / fecha ---`.
- `# Título`; cada `## sección` es una hoja; listas y tablas.
- Tabla con `{grafico: bar|hbar|pie|line}` debajo = gráfico.
- `:::kpi` con filas «valor | etiqueta | nota» (2 a 4); `:::big` con «valor | pie»; `> cita`; `> [!NOTA] aviso`; `![pie](ruta)`.
- Sintaxis exacta: `servidor/engine/markdown.py`.

## Al terminar
Estado `ok` o `con_avisos`: listo. Pasa la URL del archivo al usuario. Si hay `errores`: ver `tareas/corregir-y-revisar.md`.
