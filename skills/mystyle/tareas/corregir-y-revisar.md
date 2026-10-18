# Corregir y revisar

## 1. Lee el resultado
- `ok` o `con_avisos`: el trabajo está terminado. Los avisos informan; no es obligatorio corregirlos.
- `errores`: corrige (paso 2).

## 2. Corrige con patch (no rehagas el documento)
patch {"job":"<12 hex>","ops":[{"op":"set","section":"s1","block":"<id del bloque>","value":{…}}],"motivo":"por qué cambias"}

- Ids de bloque: `GET /v1/jobs/<job>/doc`.
- `op` puede ser `set`, `insert` o `delete`.
- `motivo` queda como corrección aprendida.
- Antes de corregir, mira ejemplos: `find_corrections {"q":"…"}`.

## 3. Revisa
- `audit {"job":"<job>"}` (o `pdf_base64`): márgenes, solapes, contraste, fuentes.
- `check_quality {"job":"<job>"}` o `{"texto":"…"}`: ortografía en español (LanguageTool) y accesibilidad del PDF.

## 4. Registra una corrección
Si arreglaste algo fuera de `patch`: `save_correction {"motivo":"…","seccion":"…","antes":{…},"despues":{…}}`.
