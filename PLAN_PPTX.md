# Plan: PPTX (después del PDF) con soporte de GIF y video

Escrito el 2026-10-16. Un **spike** en la nube confirmó lo esencial: `python-pptx 1.0.2` crea en un mismo `.pptx` texto, **gráfico nativo editable**, **GIF animado** (como imagen),
**video MP4 con póster** (`add_movie`) y **notas del orador**; LibreOffice (`soffice`) lo abre y lo convierte a PDF (sirve para pruebas automáticas); `ffmpeg`/`ffprobe` están disponibles.

## 1. Principio
Mismo contrato JSON, mismos roles de color, mismas variantes y mismas reglas que el PDF; cambia el **formato** (`"format": "pptx-16x9"`). El agente sigue sin escribir código.
Diferencia clave: en PDF el contenido **fluye** por hojas; en PPTX **cada diapositiva es una idea** y el servidor decide la partición.

## 2. Mapeo bloque → diapositiva
| Bloque del contrato | En PPTX |
|---|---|
| portada / parte (divisor) | diapositivas de portada y de sección (número gigante, titular, imagen en dos tintas) |
| `p`, `list`, `callout`, `compare`, `kpi`, `stats`, `big` | cuadros de texto y formas nativas editables; ≤ 6 viñetas y ≈ 45 palabras por diapositiva (si no cabe, se parte) |
| `table` | tabla nativa; ≤ 8 filas por diapositiva (se parte repitiendo cabecera) |
| `chart`: bar, hbar, line, stack, scatter | **gráfico nativo editable** con los roles de la paleta; `hist` = columnas nativas |
| `chart`: box, heat, map | imagen PNG a 200 ppp renderizada por Chromium desde el mismo SVG (no editable); se avisa |
| `flowchart`, `flow`, `ladder`, `timeline` | formas y conectores nativos (editables) |
| `image` | imagen en dos tintas con pie y crédito |
| **`media` (nuevo)** | GIF o video (ver §4) |
| `form`, `toc`, `custom` | `toc` → diapositiva de agenda; `form` y `custom` se degradan a nota (como siempre) |

Reglas heredadas: **un titular por diapositiva y no se repite** (anti-redundancia), cifras una sola vez, contraste ≥ 4,5, nada de texto sobre foto, grises revisados.
Nuevo: **notas del orador** (`notes` por sección o bloque) y **duración sugerida** (solo metadato).

## 3. Diseño (plantillas)
`designs/<id>/pptx/` define **layouts** reales de PowerPoint (portada, sección, título+contenido, dos columnas figura+cifras, tabla, gráfico, imagen completa, media, cierre) y el **tema**
(7 roles como colores del tema; Anton/Archivo/Plex como fuentes del tema). Se generan desde el manifiesto (no a mano) para que un diseño nuevo traiga su PPTX gratis.
**Riesgo conocido:** PowerPoint **no incrusta** estas fuentes en el archivo: o se instalan (carpeta `fonts/` en la entrega) o se aplica un mapa de reemplazo (Anton→Impact, Archivo→Arial, Plex Mono→Consolas) y se avisa en el informe.

## 4. Soporte de GIF y video (bloque `media` común a PDF, web y PPTX)
```json
{"type":"media","kind":"gif|video","src":"clips/demo.mp4","poster":"clips/demo.png","loop":true,"autoplay":false,
 "caption":"…","credit":"autor · licencia","alt":"descripción","start":0,"end":null,"fit":"contain"}
```
| Formato | Comportamiento |
|---|---|
| **PPTX · GIF** | imagen animada (`add_picture`; anima en modo presentación). Opción `gif_to_mp4: true` lo convierte con ffmpeg a MP4 en bucle (más ligero y fiable) |
| **PPTX · video** | `add_movie` con fotograma de póster (si no hay, se extrae con ffmpeg); `autoplay`/`loop` requieren **XML de temporización** propio (python-pptx no lo expone): código nuevo |
| **PDF** | no reproduce: se imprime el póster (o el primer fotograma del GIF) con marca «▶ video», pie, crédito y la URL/código QR si hay `url` |
| **Web** | `<video controls preload="metadata" poster>` / `<img>` con `alt`, sin autoplay con sonido, respeta `prefers-reduced-motion` |
Reglas: MP4 H.264 + AAC, ≤ 1920×1080; aviso > 50 MB y error > 200 MB; crédito y `alt` obligatorios; sin audio autoplay; rutas relativas a `--media`.
Herramienta nueva `servidor/tools/media.py`: `ffprobe` (validar), póster, transcodificar, GIF→MP4, recorte.

## 5. Código nuevo que hay que añadir (estimado)
| Archivo | Para qué | Líneas |
|---|---|---|
| `engine/pptx/build.py` | tubería: contrato → presentación; partición en diapositivas; informe | 250 |
| `engine/pptx/theme.py` | tema y layouts desde el manifiesto (colores, fuentes, medidas 13,333×7,5 in) | 200 |
| `engine/pptx/blocks_pptx.py` | texto, listas, avisos, cifras, tablas, imágenes, notas | 300 |
| `engine/pptx/charts_pptx.py` | gráficos nativos y PNG para box/heat/map; flowchart con conectores | 250 |
| `engine/pptx/media.py` | GIF, video, póster, XML de autoplay/bucle | 120 |
| `tools/media.py` | ffprobe/póster/transcodificado | 100 |
| `engine/blocks.py` / `web.py` | bloque `media` para PDF (póster) y web (`<video>`) | 60 |
| `engine/contract.py` | `media`, `notes`, `format: pptx-16x9` | 30 |
| `engine/audit_pptx.py` | auditoría: texto fuera de la diapositiva, contraste, redundancia, tamaño mínimo de letra (≥ 18 pt) | 150 |
| `tests/test_pptx.py` | pruebas (abrir con LibreOffice → PDF → comparar páginas) | 120 |
**Total ≈ 1.600 líneas.** Se enganchan en `render.py` (`--format pptx`) y `api.py`.

## 6. Fases y criterios de aceptación
| Fase | Alcance | Se acepta cuando |
|---|---|---|
| P0 | Spike (hecho) | python-pptx + GIF + MP4 + soffice funcionan |
| P1 | Tema, layouts, portada, secciones, texto, listas, avisos, tablas | un documento de texto sale sin desbordes; el mismo JSON da PDF y PPTX |
| P2 | Gráficos nativos y PNG; flowchart con conectores; cifras y figura+cifras | los gráficos se pueden editar en PowerPoint y respetan la paleta |
| P3 | Imágenes en dos tintas y **media** (GIF/video) | un PPTX con 1 GIF y 1 video abre, reproduce y pasa el aviso de tamaño |
| P4 | Notas del orador, agenda, variantes aprobables de diapositiva en la galería | galería de diapositivas aprobable |
| P5 | Regresión: PPTX → PDF (LibreOffice) → comparar con «golden»; auditoría PPTX | cambios del motor no rompen diapositivas |
Se empieza **cuando se cierren C1–C2 del PDF** (diseños declarativos y prompt), para no duplicar plantillas.

## 7. Riesgos
Fuentes no incrustadas (§3) · LibreOffice y PowerPoint difieren en detalles (se prueba en LibreOffice; la validación final es en PowerPoint real) · autoplay/bucle exigen XML a mano ·
videos pesan (el PPTX puede pasar de 100 MB) · gráficos `box/heat/map` no editables · animaciones de entrada/transición quedan **fuera de alcance** (solo medios).

## 8. Protocolo de referencia (imagen → estilo y componentes → contenedores)
Ver `CLAUDE.md`. Resumen: (1) leer la referencia con la herramienta (PDF o imagen); (2) sacar el **estilo** (paleta exacta, tipografías, escala, grano); (3) dividir en **contenedores** =
regiones de color continuo (bloque de acento, foto, papel); (4) **dentro** de cada contenedor van los textos y, dentro o fuera, los símbolos; (5) clasificar cada pieza como átomo;
(6) construir como variante propuesta; (7) revisar en grises y con la regla anti-redundancia.

## 9. Frontend web brutalista adaptado a páginas (biblioteca de diseños)
Se construye con `servidor/web/web.css` (ver `WEB.md`, sección «Frontend de la biblioteca»). Páginas: **Biblioteca** (tarjetas de diseño), **Detalle** (variantes, paletas, formatos),
**Generador de prompt** (selección → Prompt Maestro listo para copiar), **Galería de trabajos** y **Aprobación de variantes** (ya existe como `galeria.py`). Misma regla: 7 roles, radio 0,
sombras sólidas, grano solo en héroe, accesibilidad por teclado, sin dependencias externas.
