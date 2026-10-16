# Estándares del sistema (qué es «lo estándar» y qué pasa con lo que no lo es)

Creado por Claude como constructor. Aplica a PDF y a web: son los mismos bloques, roles de color y reglas. Los números salen de
`servidor/designs/anura/manifest.json` y de los motores en `servidor/engine/`.

## 1. Principio: lo estándar se dibuja; lo no estándar se degrada, nunca rompe

| Situación | Qué hace el servidor | Dónde se ve |
|---|---|---|
| Bloque fuera del vocabulario (`video`…) | Nota «Bloque no estándar» con su texto | `avisos` |
| Tipo de gráfico desconocido, datos vacíos o demasiados | Tabla con los mismos datos (máx. 12 filas + «se muestran N de M») | `avisos` |
| Diagrama con ciclo raro, >14 nodos o >3 por capa | Lista numerada | `avisos` |
| Tono de aviso, variante o paleta que no existe | Tono `nota`, variante por defecto, paleta por defecto | `avisos` |
| Fila de tabla con celdas de más o de menos | Se completa o recorta | `avisos` |
| Imagen que falta | Recuadro «IMAGEN NECESARIA» con la descripción | `imagenes_necesarias` |
| Bloque más alto que una hoja y sin partes | Se reduce a la medida (`zoom`) | `avisos` |
| Título largo | Se reduce antes de cortar (R12); si no cabe, se recorta con «…» | `avisos` |
| Contenido que sí necesita HTML propio | Bloque `custom`: solo etiquetas y clases permitidas, sin scripts ni estilos; lo demás se elimina | `avisos` |
| Texto con contraste insuficiente | Se corrige solo (ver §6) | `correcciones_contraste` |
| Algo que el motor no pudo prever | `try/except` por bloque: nota de error, el documento sigue | `avisos` |

Solo se **rechaza** el documento (`estado: rechazado`) si falta lo estructural: diseño o formato inválido, sin portada, ids de sección repetidos.
Prueba automática: `servidor/tests/no_estandar.json` (todo lo anterior junto; debe producir PDF y auditoría limpia).

## 2. Gráfico estándar (anatomía común a todos los tipos)

- **Marco** `figure.ch`: borde duro .6cqw, fondo papel. **Título** en display mayúsculas; **etiqueta** mono con la fuente o el tipo de dato
  (`[CALC]`, `SIMULACIÓN`…); **pie** en caja mono con «Figura N. …».
- **Área de trazado** 360×H (viewBox). **Ejes**: línea negra 1,8; rejilla negra al 20 %; marcas en mono 11–12 px color `hoja`;
  título de eje en mono; los ejes llevan unidades en el título, no en cada marca. Cifras con coma decimal y signo menos «−».
- **Marcas**: relleno `hoja` (serie), `vivo` (resalte), `arena` (neutro), **siempre con borde negro**. Una sola serie resaltada por gráfico.
- **Referencias**: media = `vivo` continua; mediana = negra discontinua; tendencia = `vivo` 3,2; atípicos = círculo `vivo` con borde negro.
- **Escala de grises**: el resalte y la serie deben diferir en claridad (L*) ≥ 12; el servidor lo comprueba en la paleta.
- **Límites** (`charts.LIMITES`): pie 7 · bar 14 · hbar 20 · line 14 · stack 8 · hist 40 · box 40 · scatter 400 · heat 12 · map 60.
- **Con cifras laterales** (`figure` con `side`): figura 7/10 + columna de cifras 3/10 con regla vertical.

| Tipo | Datos que manda el agente | Cuándo |
|---|---|---|
| `bar` | `items:[{l,v,hi?,err?,hatch?}]`, `max`, `unit` | comparar pocas categorías |
| `hbar` | `items:[{l,v,hi?}]` | etiquetas largas |
| `line` | `points:[[x,y,etiqueta?]]`, `xrange`, `yrange` | tendencia con pocos puntos |
| `stack` | `rows:[{l,v:[a,b,c]}]` | composición 100 % |
| `hist` | `bars:[[x,conteo]]`, `width`, `lines:[{x,label,style}]` | distribución de una variable |
| `box` | `groups:[{l,lo,q1,med,q3,hi,out:[]}]` | dispersión y atípicos por grupo |
| `scatter` | `points`, `trend:"auto"` o `{slope,intercept,label}` | relación entre dos variables |
| `heat` | `labels`, `matrix`, `range` | correlaciones (divergente hoja ↔ crema ↔ vivo) |
| `pie` | `items:[{l,v}]`, `donut` | partes de un todo (≤ 7) |
| `bar` series | `categories`, `series:[{name,values}]`, `mode:'grouped'|'stacked'` | comparar grupos; leyenda automática |
| `line` series | `series:[{name,points}]`, x texto o fecha ISO | varias series en el tiempo |
| `map` | `outline`, `points:[{lon,lat,label,v}]` | ubicar puntos |

## 3. Mapa estándar

Proyección equirrectangular escalada por cos(latitud media); marco negro; **retícula** cada 2° con grados en mono; contorno en `arena`
con borde negro 2; **puntos** cuadrados `vivo` con borde negro (tamaño ∝ √valor si `size:true`); **etiqueta** solo si hay ≤ 14 puntos;
**norte** con flecha y «N». Contornos en `designs/anura/geo/*.json` (`poligonos` en [lon, lat]). `colombia.json` es **esquemático**
(≈ 50 vértices a mano): sirve para ubicar, no para medir; cámbialo por un GeoJSON de Natural Earth si necesitas precisión.
Sin contorno el mapa sale como retícula con puntos; sin puntos ni contorno se degrada a tabla.

## 4. Diagrama de flujo estándar (`flowchart`)

Capas de arriba abajo; ≤ 14 nodos; ≤ 3 columnas por capa. Nodos: `start`/`end` (caja negra de doble borde), `process` (rectángulo arena),
`decision` (rombo `vivo`, 2–3 salidas con etiqueta «sí»/«no»), `io` (paralelogramo). Flechas negras ortogonales de 2 px; las que cierran un ciclo
rodean el nodo por la derecha. Para pasos lineales sin ramas usa `flow` (tarjetas), `ladder` (escalera) o `timeline` (línea de vida).

## 5. Tabla, aviso, cifras, figura (resumen)

- **Tabla**: cabecera negra mono; primera columna en negrita; regla gruesa al final; se parte por filas repitiendo cabecera. Variantes TB-1…TB-4.
- **Aviso**: borde 6, etiqueta mono arriba; tonos `nota`, `clave`, `ojo`, `sim`, `pend`, `regla`, `slate`, `hueco`.
- **Cifras**: tarjetas (2–4), columna lateral o cifra grande con disco. Una cifra, una sola vez por hoja.
- **Imagen**: siempre en dos tintas con trama (filtro del sistema), sin texto encima, con pie y crédito (Wikimedia: autor + licencia).
- **Texto**: español neutro, coma decimal, etiquetas `[FUENTE]`, `[INF]`… como chips; «dato pendiente» resaltado.

## 6. Protocolo de revisión en grises (se ejecuta solo en cada render)

1. **Paleta antes de dibujar** (`engine/paleta.py`): contraste de los pares de texto permitidos (≥ 4,5) y diferencia de claridad L* entre `negro`, `hoja`, `vivo`
   (≥ 12). Avisa si dos colores se confunden en grises.
2. **Texto contra su fondo** (`engine/contrast_fix.js`): si el contraste es < 4,5 (< 3 en letra grande) se prueba primero un rol del diseño (el más
   parecido que cumpla); si ninguno sirve, se **oscurece** el texto sobre fondo claro o se **aclara** sobre fondo oscuro, de 5 % en 5 %. Cada cambio queda en
   `correcciones_contraste` (de, a, razón, contraste antes y después).
3. **Auditoría** (`engine/audit.js`) en 794 px impresión, 1300 y 400: superposiciones, texto fuera de hoja, cortado, contenido sobre el pie.
4. **Contacto en grises** (`pdftoppm -gray`): mirar una sola imagen de todas las hojas.

## 6b. Anti-redundancia
Un texto aparece **una sola vez por hoja** (README de ANURA). `engine/redundancia.py` compara raíces de palabras de los titulares y etiquetas: la cabecera nunca repite el titular, un subtítulo
que repite el titular se omite, un título de figura que repite el titular se omite, y la auditoría informa lo que quede (`redundancia`). Un subtítulo de una palabra dentro de un titular largo
(«Fauna» en «Enfermedad en fauna y flora») es legítimo y no se toca.

## 7. Variantes y aprobación

`servidor/designs/anura/variantes.json` registra cada plantilla con id, nivel atómico y estado (`propuesta` | `aprobada` | `rechazada`).
`python servidor/galeria.py --imagenes teoria/imagenes` genera `salida/galeria/galeria_<paleta>.html`: una tarjeta por variante dibujada con el motor real,
con selector de estado y «Exportar aprobaciones». `python servidor/aprobar.py aprobaciones.json` aplica el resultado. El informe de cada render lista
`variantes_usadas` y `variantes_no_aprobadas`. Una variante rechazada se sustituye por la de por defecto.

## 8. Diseño atómico (PDF y web)

| Nivel | PDF | Web |
|---|---|---|
| Átomos | color por roles, tipografía, símbolo, regla, chip, franja, código de barras, cruz, X en caja, titular apilado | `.a-*` |
| Moléculas | tabla, aviso, cifras, gráfico, formulario | `.m-*` |
| Organismos | portada, divisor, figura + cifras, diagramas | `.o-*` |
| Plantillas | hoja normal / punto clave / tablero | `.t-*` |
| Páginas | el documento | `index.html` |
Reglas web en `WEB.md`.
