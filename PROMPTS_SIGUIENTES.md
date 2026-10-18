# myStyle · paso a paso siguiente (prompts listos para Claude Code)

Escrito el 2026-10-17 con /prompt-master. **No se ejecuta nada hasta que el usuario lo revise.** Orden: de Haiku a Opus, respetando dependencias.
Cada prompt se pega en una sesión nueva de Claude Code abierta en `D:\feibert\api\guia`, con el modelo indicado en el selector.

> Estos prompts son para un agente con acceso real al sistema. Revisa los límites de archivos, lo prohibido y las condiciones de parada antes de pegarlos.

## Reparto y presupuesto (estimación, no medida)
| # | Tarea | Modelo | Por qué ese modelo | Tokens aprox. | Depende de |
|---|---|---|---|---|---|
| H1 | Formatos: referencias reales que llevan a los ejemplos | **Haiku 5.5** | cambio mecánico con instrucciones exactas | 40–70 k | — |
| S1 | Logo de 3 círculos con la identidad (Paleta 7) | **Sonnet 5.5** | criterio visual acotado | 30–50 k | — |
| S2 | Cuentagotas: paleta desde una imagen | **Sonnet 5.5** | función nueva de frontend, sin arquitectura | 90–140 k | — |
| S3 | Filtro del catálogo rediseñado | **Sonnet 5.5** | UX de frontend | 70–110 k | — |
| O1 | Estilo nuevo desde *Guia-Prompt-Master-v2.pdf* + PDF de uso + publicarlo | **Opus 5.5** | lectura de referencia, diseño, motor y validación | 350–600 k | — |
| O2 | Método y medición de tokens (con vs sin la herramienta) | **Opus 5.5** | metodología que no puede ser inventada | 120–200 k | O1 (usa su gasto real) |
| S4 | Sección Estadísticas en la web | **Sonnet 5.5** | página con datos ya medidos | 80–120 k | O2 |
| S5 | /design:design-critique de toda la web y corrección de espacios y márgenes | **Sonnet 5.5** | crítica estructurada y CSS | 180–280 k | H1, S1–S4, O1 |
| H2 | Cierre: regenerar catálogo, pruebas, documentación y bitácora | **Haiku 5.5** | comandos y texto | 30–60 k | todo |

Total estimado ≈ 1,0–1,6 M tokens. Hacerlo todo con Opus costaría varias veces más; Haiku y Sonnet toman lo mecánico y el frontend.

---

## H1 · Haiku 5.5 — Formatos con referencias reales
```xml
<context>
Proyecto myStyle (API de documentos). Frontend: servidor/web/app.html y servidor/web/site.css, servido por servidor/api.py en http://localhost:8765.
La sección /formatos (data-route="/formatos") tiene 5 tarjetas .fmt: PDF, PowerPoint y Video usan fotos de ranas de Wikimedia (servidor/web/img/*.jpg); Word y Excel no tienen imagen.
Ya existen ejemplos reales: catálogo en servidor/web/cat/<id>/p01.png (PDF), salida/pptx/*_png/Diapositiva1.PNG (PPTX), salida/office/*.docx y *.xlsx, salida/video/informe_ventas.mp4.
</context>
<task>
1. Crea servidor/web/fmt/ con una miniatura PNG de 16:9 (máx. 900 px de ancho, ≤ 150 KB) por formato, sacada de un ejemplo REAL del informe de ventas:
   pdf.png (p01 del catálogo informe_ventas), pptx.png (Diapositiva1 de salida/pptx/informe_ventas_png; si no existe, ejecútala con python servidor/tools/pptx_png.py),
   docx.png (página 3 de salida/office/informe_ventas_word.pdf con pdftoppm), xlsx.png (captura de la hoja con gráfico: abre el xlsx con Excel por COM y exporta, o dibuja la tabla con Pillow si no hay Excel),
   video.png (fotograma del segundo 7 de salida/video/informe_ventas.mp4 con ffmpeg).
2. En app.html, cambia la imagen de cada tarjeta por su miniatura y convierte cada tarjeta en un enlace:
   PDF → /catalogo?formato=pdf ; PowerPoint, Word y Excel → abren /catalogo/informe_ventas con ese formato preseleccionado en «Descargar como» (usa ?descargar=pptx-16x9|docx-a4|xlsx) ; Video → /catalogo/informe_ventas?video=1 (abre la ficha y empieza «Crear video»).
3. Añade la lectura de esos parámetros en route() de app.html. Texto del enlace visible: «Ver ejemplos de PDF», «Ver ejemplo en PowerPoint», etc.
4. Quita del pie la lista «Fotos de Formatos · Wikimedia Commons» solo si ninguna foto de Commons queda en uso; si quedan, déjala.
</task>
<constraints>
Solo edita servidor/web/app.html, servidor/web/site.css y crea servidor/web/fmt/. NUNCA borres imágenes de servidor/web/img/.
Cada miniatura lleva alt descriptivo. Mantén clip-path y estilo de .fmt. Sin dependencias nuevas.
</constraints>
<done>
Las 5 tarjetas muestran una miniatura real y llevan a su ejemplo; los 5 enlaces abren lo prometido en el navegador (verifícalo con la herramienta de navegador);
python -m unittest discover -s servidor/tests sigue en OK.
</done>
<stop>Para y pregunta antes de instalar algo o si un ejemplo de salida/ no existe y no se puede regenerar con los scripts del proyecto.</stop>
Tras cada paso escribe: ✅ [qué terminaste].
```

## S1 · Sonnet 5.5 — Logo coherente con la identidad visual
```xml
<context>
El logo actual son 3 círculos que se suman como luz (rojo, verde, azul). Está en el símbolo #i-logo de servidor/web/app.html, en las variables --l1/--l2/--l3 de servidor/web/site.css,
en servidor/web/favicon.svg y en la función favicon() de app.html (icono de la pestaña que sigue al tema).
La identidad de la web es la Paleta 7: tinta #030b18, papel #f5eae4, rojo #fe0032, noche #313e60. El verde y el azul puros no pertenecen a esa identidad.
</context>
<task>
Rediseña los colores del logo para que coincidan con la identidad sin perder la idea de «3 círculos que se superponen» (indicador):
- Tema claro y oscuro con tonos derivados SOLO de la Paleta 7 (por ejemplo rojo, noche y papel, o variaciones de su luminosidad); la mezcla de los cruces debe seguir viéndose.
- Elige el modo de mezcla (screen, multiply o ninguno con opacidad) que mejor se lea sobre la barra oscura y sobre una pestaña clara del navegador.
- Aplica lo mismo en #i-logo, favicon.svg (con su @media de esquema oscuro) y favicon().
Muestra 2 propuestas en una página temporal servidor/web/_logo.html (claro y oscuro, a 16, 32 y 128 px), elige la mejor con una razón de una línea y borra _logo.html al final.
</task>
<constraints>Solo toca app.html, site.css, favicon.svg y la página temporal. No cambies la tipografía del logotipo «myStyle».</constraints>
<done>El logo a 16 px se distingue en claro y oscuro; los colores salen de la Paleta 7; el icono de la pestaña cambia con el botón de tema.</done>
<stop>Para y muestra las 2 propuestas antes de aplicar si ninguna se lee bien a 16 px.</stop>
Tras cada paso escribe: ✅ [qué terminaste].
```

## S2 · Sonnet 5.5 — Cuentagotas: armar la paleta desde una imagen
```xml
<context>
Taller (/taller) en servidor/web/app.html: tarjeta «Diseño y paleta» con 7 inputs de color (#roles, roles negro, bosque, hoja, vivo, ocre, crema, arena), que se validan en vivo con POST /v1/paleta.
</context>
<task>
Añade dentro de esa tarjeta una sección «Paleta desde una imagen»:
1. Botón «Elegir imagen» (input file, PNG/JPG/WEBP, ≤ 15 MB) que la dibuja en un <canvas> local (no se sube al servidor).
2. Extrae 8 colores dominantes en el navegador (cuantización mediana o k-means simple con semilla fija) y muéstralos como muestras.
3. Asigna los colores a los 7 roles por luminosidad y saturación: el más oscuro → negro; oscuro saturado → bosque; medio → hoja; los dos más saturados → vivo y ocre; los dos más claros → crema y arena.
4. Modo cuentagotas: al hacer clic sobre la imagen, toma el color de ese píxel y lo asigna al rol seleccionado (selector de rol activo). Si el navegador tiene window.EyeDropper, añade «Tomar de la pantalla».
5. Tras asignar, llama a sync() para validar contraste y redibujar la galería; muestra los avisos existentes.
6. Botones «Aplicar a mi paleta» y «Deshacer».
</task>
<constraints>
Solo edita servidor/web/app.html y servidor/web/site.css. Sin librerías externas. Todo en el cliente. Accesible con teclado (roles y muestras con botones de 44 px).
</constraints>
<done>Con una foto cualquiera se rellenan los 7 roles, el cuentagotas cambia un rol con un clic, /v1/paleta responde y la galería se actualiza. Verifica en el navegador con una imagen de servidor/web/img/.</done>
<stop>Para y pregunta antes de añadir dependencias o tocar el servidor.</stop>
Tras cada paso escribe: ✅ [qué terminaste].
```

## S3 · Sonnet 5.5 — Filtro del catálogo
```xml
<context>
/catalogo en servidor/web/app.html: buscador #cq, grupos de botones .fbtn por Estilo, Diseño y Tipo (función shelf()), tarjetas .book. Datos: GET /v1/catalog (style, design, kind, pages, blocks, title, text).
Problema: los filtros ocupan mucho, no muestran cuántos resultados da cada opción, no se ven los filtros activos ni se pueden limpiar, y no quedan en la URL.
</context>
<task>
Rediseña el filtrado como una barra compacta:
1. Una fila con el buscador y tres desplegables (Estilo, Diseño, Tipo) tipo menú con casillas (selección múltiple), cada opción con su conteo «(n)» calculado con los demás filtros aplicados.
2. Debajo, «píldoras» de filtros activos con ✕ y un botón «Limpiar filtros».
3. Orden: «Más recientes», «Más páginas», «A–Z».
4. Filtro nuevo «Formato de ejemplo» (PDF, PowerPoint, Word, Excel, Video) que se usa también desde /formatos (?formato=).
5. Guarda el estado en la URL (?q=&estilo=&diseno=&tipo=&orden=) y respétalo al cargar y con Atrás/Adelante.
6. En móvil (≤ 560 px) los desplegables se abren como hoja inferior a pantalla completa.
</task>
<constraints>Solo app.html y site.css. Mantén los tokens de color, el contraste ≥ 4,5:1 y objetivos ≥ 44 px. Escape cierra el desplegable; el foco vuelve al botón.</constraints>
<done>Combinar filtros da el resultado correcto, los conteos cuadran, la URL refleja el estado y un enlace con ?estilo=brutalismo abre ya filtrado. Verifica en 1366 px y 375 px.</done>
<stop>Para si el cambio exige tocar la API.</stop>
Tras cada paso escribe: ✅ [qué terminaste].
```

## O1 · Opus 5.5 — Estilo nuevo desde *Guia-Prompt-Master-v2.pdf*, PDF de uso y publicación
```xml
<context>
Lee primero guia/CLAUDE.md (protocolo de referencias) y guia/PENDIENTES.md. Referencia: C:\Users\user\Downloads\Guia-Prompt-Master-v2.pdf (7 hojas A4, «Prompt Master · Logicvalia»):
editorial tipo SaaS, papel blanco, tinta casi negra, acento violeta, degradado morado en el cierre, pasos numerados gigantes, paneles oscuros con listas de verificación;
fuentes Archivo (SemiBold/Bold/Black) y Space Grotesk. Diseños existentes: servidor/designs/anura y editorial (etiqueta «brutalismo»).
Herramientas: servidor/tools/leer_pdf.py, crear_diseno.py, validar_diseno.py, galeria.py, api.py (POST /v1/designs/import y /publish con la clave de servidor/data/admin-key.txt).
</context>
<task>
1. Lee la referencia SOLO con python servidor/tools/leer_pdf.py <pdf> -o referencias/prompt-master y mira resumen.md + contacto.png (no abras las hojas una por una).
2. Crea el diseño «prompt-master» con crear_diseno.py --base editorial; en su manifiesto: "estilo": "editorial-saas", paleta por los 7 roles con los colores vectoriales exactos del PDF,
   fuentes Archivo y Space Grotesk (OFL) en designs/prompt-master/fonts, al menos 2 portadas y 2 divisores nuevos inspirados en la referencia (originales: sin copiar logos ni textos).
3. Valida con validar_diseno.py prompt-master hasta 10/10 ✔ y revisa la galería (galeria.py --design prompt-master).
4. Actúa como un agente externo: pide el Prompt Maestro (POST /v1/prompt, modo A, corto) y escribe un contrato JSON con contenido NUEVO y verificable sobre «Cómo usar myStyle con tu agente» (5–7 hojas, con una tabla, un gráfico y una lista de pasos). Renderízalo por la API en pdf-a4 y pptx-16x9, corrige con /v1/jobs/{id}/patch según los avisos.
5. Publica el diseño (POST /v1/designs/prompt-master/publish), publica los trabajos en la galería, guarda el JSON en contenido/prompt_master_uso.json, regenera el catálogo (servidor/tools/catalogo.py) y comprueba que aparece en /catalogo y en /estilos con su etiqueta.
6. Registra en referencias/prompt-master/gasto.md los tokens que gastaste en cada paso (lectura de la referencia, diseño, validación, documento, correcciones), usando el contador de uso de la sesión.
</task>
<constraints>
No cambies los diseños anura ni editorial ni el motor salvo un fallo real (si lo encuentras, arréglalo en el origen y añade una prueba).
Las variantes nuevas entran como «propuesta». Nada inventado: cifras sin dato = «dato pendiente».
</constraints>
<done>validar_diseno 10/10 ✔; PDF y PPTX sin desbordes en el informe; el estilo «editorial-saas» aparece en /catalogo y /estilos; gasto.md con cifras de la sesión; unittest y regresion.py en OK.</done>
<stop>Para y pregunta antes de descargar las fuentes Space Grotesk (indica origen, licencia y peso) y antes de publicar el diseño.</stop>
Tras cada paso escribe: ✅ [qué terminaste] y los tokens acumulados.
```

## O2 · Opus 5.5 — Método y medición de tokens (con vs sin la herramienta)
```xml
<context>
Queremos mostrar cuánto ahorra myStyle. Datos reales disponibles: contratos de contenido/*.json, Prompt Maestro (POST /v1/prompt, corto y largo), informes de /v1/render,
HTML final que produce el motor (render.py escribe salida/*.html), composiciones de video (salida/video/*_proyecto/index.html), registro de la API (registro.jsonl en API_OUT),
y el gasto real de la sesión O1 en referencias/prompt-master/gasto.md.
</context>
<task>
1. Escribe servidor/tools/tokens.py que, para cada documento de contenido/ y cada formato (pdf, pptx, docx, xlsx, video), calcule:
   CON myStyle = tokens del Prompt Maestro corto + tokens del contrato JSON (lo que el agente escribe) + tokens del informe devuelto + 1 corrección por parche promedio;
   SIN myStyle = tokens del artefacto que el agente tendría que escribir a mano (HTML+CSS+SVG del PDF sin base64; script python-pptx equivalente; composición HyperFrames del video) × factor de iteraciones documentado.
   Usa un contador de tokens explícito: el endpoint count_tokens de la API de Anthropic si hay ANTHROPIC_API_KEY; si no, chars/3,6 marcado «estimado».
2. Justifica el factor de iteraciones con evidencia del propio proyecto (correcciones registradas, avisos por render) y escribe la metodología en servidor/tools/TOKENS.md (supuestos, fórmula, límites).
3. Genera servidor/web/stats/tokens.json con: por formato (media, mínimo, máximo) con y sin myStyle, ahorro %, costo de crear un estilo nuevo (de gasto.md de O1) y la comparación «cualquier agente» (Claude vía MCP, ChatGPT vía OpenAPI: mismos tokens de contrato).
</task>
<constraints>Nada inventado: cada número sale de un archivo medido o de un supuesto escrito en TOKENS.md. Sin dependencias nuevas salvo que exista ANTHROPIC_API_KEY.</constraints>
<done>tokens.json se regenera con un comando; TOKENS.md explica cada cifra; una prueba en servidor/tests valida la forma de tokens.json.</done>
<stop>Para y pregunta si no hay ANTHROPIC_API_KEY y la diferencia entre conteo exacto y estimado importa para la decisión.</stop>
Tras cada paso escribe: ✅ [qué terminaste].
```

## S4 · Sonnet 5.5 — Sección «Estadísticas» en la web
```xml
<context>Datos en servidor/web/stats/tokens.json (de O2) y GET /v1/stats (registro de la API, solo admin). Frontend: rutas por sección en servidor/web/app.html (route(), NAMES, data-route).</context>
<task>
Crea la ruta /estadisticas (añádela también a la expresión de rutas de servidor/api.py y al menú de 3 líneas):
1. Titular y texto corto: cuánto gasta un agente CON myStyle vs SIN, por formato (PDF, PowerPoint, Word, Excel, Video).
2. Gráfico de barras agrupadas accesible (SVG propio, sin librerías) + tabla con los mismos datos; etiquetas «medido» o «estimado» según tokens.json.
3. Tarjeta «Crear un estilo nuevo desde un PDF» con el gasto real de O1, y tarjeta «Cualquier agente» (MCP y OpenAPI).
4. Enlace a servidor/tools/TOKENS.md explicado en una línea (metodología).
</task>
<constraints>Solo app.html, site.css y la línea de rutas de api.py. Colores desde los tokens del sitio; contraste ≥ 4,5:1; no repitas cifras en texto y gráfico sin necesidad.</constraints>
<done>/estadisticas carga en claro y oscuro, en 1366 y 375 px, sin desbordes y con los números de tokens.json.</done>
<stop>Para si tokens.json no existe: esta tarea depende de O2.</stop>
Tras cada paso escribe: ✅ [qué terminaste].
```

## S5 · Sonnet 5.5 — Crítica de diseño y corrección de espacios y márgenes
```xml
<context>Web myStyle en http://localhost:8765 con rutas /, /como, /agente, /catalogo, /catalogo/<id>, /taller, /formatos, /estilos, /estadisticas. Estilos en servidor/web/site.css.</context>
<task>
1. Toma capturas de cada ruta en 1366 px y 375 px, tema claro y oscuro, con la herramienta de navegador.
2. Ejecuta /design:design-critique sobre esas capturas y entrega una lista priorizada (alta/media/baja) centrada en: espacios apeñuscados, márgenes y rellenos irregulares, ritmo vertical, alineación,
   jerarquía tipográfica, densidad de botones, tarjetas desiguales y saltos de línea feos.
3. Define una escala de espaciado única (por ejemplo 4/8/12/16/24/32/48/72/96) como variables en :root y aplícala en site.css en lugar de valores sueltos.
4. Corrige todos los puntos de prioridad alta y media. Vuelve a capturar y muestra antes/después de las 3 peores vistas.
5. Repite la auditoría automática de contraste, desbordes y objetivos táctiles que ya existe en el proyecto (ver bitácora) y deja todo en 0 fallos.
</task>
<constraints>Solo site.css y, si hace falta, clases en app.html. No cambies textos ni la paleta. Mantén el estilo de la referencia (barra oscura, titulares condensados, esquinas cortadas).</constraints>
<done>Lista de crítica con cada punto marcado «corregido» o «pendiente con motivo»; auditoría en 0 fallos en las 4 combinaciones.</done>
<stop>Para y pregunta si una corrección exige cambiar la estructura de una sección.</stop>
Tras cada paso escribe: ✅ [qué terminaste].
```

## H2 · Haiku 5.5 — Cierre
```xml
<task>
En D:\feibert\api\guia: 1) python servidor/tools/catalogo.py; 2) python -m unittest discover -s servidor/tests; 3) python servidor/regresion.py --comprobar;
4) actualiza guia/PENDIENTES.md: marca en la bitácora las tareas H1–S5 hechas, mueve lo resuelto de las secciones 3 y 4 y anota lo que quedó pendiente con su motivo;
5) actualiza la lista de rutas de api.md con /estadisticas y los formatos nuevos.
</task>
<constraints>No edites código salvo api.md y PENDIENTES.md. Si una prueba falla, NO la arregles: anótala en PENDIENTES.md y para.</constraints>
<done>Las tres comprobaciones informadas con su resultado y PENDIENTES.md al día.</done>
Tras cada paso escribe: ✅ [qué terminaste].
```
