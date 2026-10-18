# Hacer página web animada

Salida: una sola página HTML con anime.js (entrada escalonada y contadores).

## Pasos
1. Receta: `create_from_recipe {"receta":"…","valores":{…},"formato":"web"}`. Busca con `list_recipes`.
2. Sin receta: `render {"format":"web-animada","markdown":"…","design":"anura"}`.
3. Fondo 3D con three.js: solo por línea de comandos.
   `python servidor/web.py doc.json --animar --fondo3d`
   - Salida por defecto: `salida/web/index.html`. Cambia con `-o`.
   - Imágenes: `--imagenes imagenes`.
   - Sin fondo 3D: usa solo `--animar`.

## Reglas
- Secciones cortas. Una sección = una hoja.
- Contadores solo con cifras que tengan dato. Sin dato, «dato pendiente».
- Imágenes con licencia y crédito.

## Al terminar
Entrega la URL o la ruta del HTML generado.
