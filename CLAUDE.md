# CLAUDE.md · contrato de trabajo para futuras sesiones

Repositorio: guía de IA para identificar animales + servidor ligero que convierte un JSON de contenido en PDF/web con el diseño ANURA.
Lee primero `CODIGO_CREADO.md` (qué es código mío y qué es contenido), `ESTANDARES.md` y `WEB.md`.

## Reglas fijas
- **Separación de papeles.** El contenido (`contenido/*.json`) son datos: sin HTML, CSS ni scripts. El código del servidor va en `servidor/` y cada archivo
  empieza con `[CLAUDE-CONSTRUCTOR]`. Los archivos existentes de `teoria/` y `research_notes/` no se editan.
- **Nada inventado.** Cifra sin dato = «dato pendiente». Estimación solo con `[SIM]`/SIMULACIÓN. Conserva `[FUENTE]`, `[INF]`, `[SIN FUENTE]`, `[CALC]`, `[RESUMEN]`.
- **Lo no estándar no rompe.** Cualquier bloque, gráfico, variante o paleta desconocidos se degradan con aviso (ver `ESTANDARES.md` §1). Antes de dar por bueno un cambio
  del motor, corre `python -m unittest discover -s servidor/tests` (incluye `no_estandar.json`).
- **Variantes nuevas = propuestas.** Se añaden a `designs/anura/variantes.json` con `estado: propuesta` y se muestran en la galería; no se cambia el aspecto de lo aprobado.

## Cuando te pasen una referencia (hazlo en este orden, ahorra contexto)
1. **PDF** → `python servidor/tools/leer_pdf.py ref.pdf -o referencias/<nombre>`; lee `resumen.md` (medidas en cqw, tipografías, colores exactos de los vectores) y mira **solo**
   `contacto.png`. No abras las páginas una por una. Los colores del PDF son los vectoriales (p. ej. `#fe0032`), no los de la imagen renderizada (el grano los aclara).
2. **Imagen** → `python servidor/tools/descomponer.py img.jpg -o referencias/<nombre>`; verifica con `anotada.png` (una imagen) y lee `guias.md`. Es heurística: bloques de color, foto,
   texto pequeño, símbolos y códigos salen bien; titulares gigantes salen a medias. Corrige a mano lo que veas mal y anota las coordenadas medidas.
3. **Divide en átomos** (regla, chip, símbolo, franja, código, bloque de acento, titular apilado, foto en dos tintas…) y anota: posición en cqw, alineación (izquierda / centro),
   jerarquía de tamaños, qué se repite. Símbolos y reglas se vectorizan (SVG con `currentColor`); las fotos se tramean con el filtro duotono, no se vectorizan.
4. **Construye** como variante (`CV-n`, `DV-n`, `TB-n`…), mide con `render.py`, mira `salida/*.informe.json` y un contacto en grises.
5. **Galería** → `python servidor/galeria.py --imagenes teoria/imagenes`; el usuario aprueba y `aprobar.py` aplica.

## Revisión (protocolo en grises, ya automático en cada render)
Paleta (contraste + L*) → corrección de contraste (rol parecido o oscurecer/aclarar por pasos) → auditoría a 794/1300/400 px → contacto en grises.
Si algo «no se distingue», la medida es la de `contrast_fix.js`: letra gris sobre fondo claro se oscurece.

## Comandos
```bash
pip install -r servidor/requirements.txt scipy potracer opencv-python-headless   # los 3 últimos solo para tools/descomponer.py
python servidor/render.py contenido/guia.json -o salida/guia.pdf --imagenes teoria/imagenes
python servidor/web.py contenido/guia.json -o salida/web/index.html --imagenes teoria/imagenes --estilo
python servidor/galeria.py --imagenes teoria/imagenes --pdf
python servidor/aprobar.py --listar
python -m unittest discover -s servidor/tests
```

## Trampas ya pisadas (no repetir)
- Medir bloques con el **mismo ancho** que la hoja final (90 cqw): midiendo a 100 cqw todo cabía «de más» y el contenido invadía el pie.
- `fit.js` ajusta tamaños en **cqw** (no px) para valer a cualquier ancho; un contenedor `flex-wrap:wrap` encoge los hijos y rompe el modo `data-fit="f"`.
- La auditoría trata el texto SVG como línea de caja: separar líneas ≥ `fs+5`; el texto rotado (`transform`) se excluye del cruce texto/texto.
- Una palabra larga no se parte: el título se reduce (R12) y, si aun así no cabe, se recorta con «…».
- En la nube **no hay acceso a Wikimedia** (el proxy lo rechaza): `servidor/tools/commons.py` se usa en el PC del usuario; aquí se usan las fotos de `teoria/imagenes`.
- Lectura de assets de un artifact: `read` con `path` **de uno en uno**; con `paths` falla.
- Chromium: `/opt/pw-browsers/chromium` (o `CHROMIUM_PATH`); no correr `playwright install` en la nube.
