# Hacer presentación (PowerPoint)

Salida: `.pptx` 16:9, editable.

## Pasos
1. `list_recipes {"q":"presentación de ventas"}`. Receta principal: `presentacion_ventas`.
2. `recipe_get {"id":"presentacion_ventas"}` y rellena solo los huecos que cambian.
3. `create_from_recipe {"receta":"presentacion_ventas","valores":{"<hueco>":"<valor>"},"formato":"pptx","estilo":"anura"}`.
4. Sin receta: Markdown y `create_pptx {"markdown":"…","design":"anura"}`.

## Reglas para diapositivas
- Cada `##` es una hoja (diapositiva). Un mensaje por hoja.
- Cifras clave: `:::kpi` (2 a 4 filas) o `:::big`.
- Tabla con `{grafico: …}` debajo si hay datos comparables.
- Cita de cliente o testigo: `> cita`.
- Sin dato, pon «dato pendiente». No inventes cifras.
- Imágenes: `![pie](ruta)` con licencia y crédito.

## Al terminar
`ok` o `con_avisos`: entrega la URL. Con `errores`: `patch` según `tareas/corregir-y-revisar.md`.
