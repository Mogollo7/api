# Reglas para generar web con este estilo (brutalista, diseño atómico)

Kit: `servidor/web/web.css` (capas `.a-` átomos → `.m-` moléculas → `.o-` organismos → `.t-` plantillas). Generador: `servidor/web.py`
(mismo JSON que el PDF). Guía de estilo viva: `salida/web/estilo.html`.

## Reglas de estilo (no negociables)
1. **Color**: solo los 7 roles (`--negro --bosque --hoja --vivo --ocre --crema --arena`). Paleta nueva = nuevo valor de rol, nunca un color suelto.
   `vivo` y `ocre` nunca como texto sobre `crema`/`arena`. Contraste de texto ≥ 4,5:1 (3:1 desde 24 px).
2. **Tipografía**: Anton para títulos (mayúsculas, interlineado .92), Archivo para texto, IBM Plex Mono para datos y etiquetas. Ninguna otra.
   Tamaños fluidos con `clamp()`; cuerpo ≥ 16 px.
3. **Forma**: radio 0; bordes duros de 2–6 px; sombras sólidas desplazadas (`.35rem .35rem 0`), nunca difuminadas; sin degradados.
4. **Textura**: grano (`.grain`) solo en héroe y bandas oscuras; nunca bajo texto largo.
5. **Imágenes**: dos tintas con trama (mismo filtro que en PDF); crédito y `alt` obligatorios; sin texto encima.
6. **Jerarquía**: un titular gigante por pantalla; cifras en Anton; etiquetas mono en mayúsculas con interletraje.

## Reglas de estructura (diseño atómico)
- **Átomo**: no contiene otro átomo (botón, chip, regla, campo, símbolo, etiqueta). **Molécula**: 2+ átomos con una función (cifra, aviso, figura, fila de tabla).
- **Organismo**: sección autónoma (cabecera fija, héroe, banda de sección, sección de contenido, formulario, pie). **Plantilla**: disposición sin contenido
  (artículo 1 columna, rejilla, 7/3). **Página**: plantilla + contenido real.
- Un componente nuevo se crea **solo** si no se puede componer con los existentes; entra primero como `propuesta` en `variantes.json`.

## Accesibilidad y comportamiento
- Enlace «Saltar al contenido»; `:focus-visible` de 3 px en `vivo`; navegación por teclado completa; `lang="es"`.
- `prefers-reduced-motion`: sin animaciones. Una sola transición permitida: el desplazamiento del botón al pulsar.
- Móvil primero: una columna; tablas con desplazamiento horizontal propio (no de la página); rejillas con `auto-fit/minmax`.
- Sin dependencias externas: fuentes e imágenes incrustadas, sin CDN.

## Qué hacer con lo no estándar
Igual que en PDF (ver `ESTANDARES.md` §1): un bloque sin equivalente web se muestra como nota con su texto y se anota en `avisos`.
