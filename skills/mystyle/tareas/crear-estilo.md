# Crear un estilo nuevo (desde una imagen, un PDF o una descripción)

Todo se hace con herramientas: no escribes CSS. Antes, `search_library {"q":"…","tipo":"estilo"}`: si ya hay uno parecido, úsalo y para.

## Si el usuario da una imagen o PDF
1. `analyze_reference {"ruta":"<ruta local>","id":"mi-estilo"}` → modo (claro/oscuro), acento, paleta y el comando exacto.
2. Si pide una fuente, esa manda; si no, Archivo (la de los estilos de la fábrica). Las fuentes disponibles están en `servidor/designs/*/fonts`.
3. `create_style {"id":"mi-estilo","acento":"#C22ADD","piel":"recta","modo":"oscuro","nombre":"Mi estilo"}` → crea el diseño con 4 variantes y corre los 10 chequeos. Si hay ✘ (casi siempre contraste), cambia el acento o la piel y repite.
   Pieles: `suave` (esquinas redondeadas, trazo fino), `recta` (rectas, trazo grueso, títulos en mayúsculas), `redonda` (muy redondeada, sombra), `editorial` (casi recta, trazo fino).
4. Variantes extra: `create_variant {"estilo":"mi-estilo","tipo":"portada","fondo":"acento","nuevo":"CV-3"}` (también `divisor`, y fondo `claro` u `oscuro`).
5. Mira el resultado: `create_from_recipe {"receta":"informe_negocio","estilo":"mi-estilo","portada":"CV-3"}` y `screenshot {"job":"…","pagina":1}`; compáralo con la referencia.
6. Símbolos de la referencia (si importan): `python servidor/tools/descomponer.py <imagen> -o referencias/<id>` y `designs/LEEME.md`.

## Si falta una herramienta
Haz lo que puedas con las que hay y apunta lo que faltó. Si creas una pieza que servirá otra vez (receta, ingrediente, recurso, plantilla), guárdala con `save_style` (`tipo`: receta, ingrediente, recurso, plantilla o estilo; si el id existe, pregunta al usuario antes de `sobrescribir`).

## Reglas fijas
- Cada estilo: paleta de 7 roles con contraste ≥ 4,5, una portada y un divisor mínimo, validación en «todo ✔».
- Nada de logos ni textos de la referencia: se toma el estilo, no la marca.
