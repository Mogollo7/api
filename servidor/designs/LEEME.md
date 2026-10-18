# Anatomía de un diseño (cómo crear uno nuevo)

Un diseño es una carpeta `servidor/designs/<id>/`. **Copiar un diseño existente es lo normal**:
`python servidor/crear_diseno.py <id> --base anura --nombre "Nombre"` y editar. El motor no conoce ningún diseño en particular.

| Archivo / carpeta | Qué contiene | Obligatorio |
|---|---|---|
| `manifest.json` | id, nombre, versión, formatos, **7 roles de color**, pares de texto permitidos, fuentes (con **licencia**), medidas de hoja (`page`), símbolos y posiciones de portada/divisor, tratamientos de imagen, reglas de redacción, vocabulario de bloques | sí |
| `palettes.json` | paletas con nombre (`{rol: #hex}`); el documento elige con `"palette": "nombre"` | sí |
| `variantes.json` | registro de plantillas con id (`CV-n` portada, `DV-X` divisor, `TB-n` tabla…), nivel atómico y estado (`propuesta/aprobada/rechazada`) | sí |
| `bundle.css` + `extras.css` | estilos. **Contrato de clases** que el motor necesita: `.page`, `.cover`, `.dv`, `.lp` (`.tope`, `.cont`, `.pie`), `.tab`, `.co`, `.ch` y las de los bloques (ver `extras.css` de ANURA) | sí |
| `templates/cover.<ID>.html`, `templates/divider.<ID>.html` | **plantillas declarativas** de portada y divisor con campos `{{…}}` | ≥ 2 de cada una |
| `fonts/*.woff2` | fuentes (se incrustan) | sí |
| `simbolos.json` | catálogo de símbolos vectoriales (`gNN`) | sí |
| `defs.svg.txt` | `<symbol>` extra para usar en plantillas (p. ej. goteos) | no |
| `geo/*.json` | contornos para `map` (`poligonos` en [lon, lat]) | no |
| `ranas/` (o `arte/`) | arte de dos tintas que se repinta con la paleta | no |

## Plantillas: campos disponibles (`engine/tpl.py`)
Sintaxis: `{{campo}}` (escapado) · `{{&campo}}` (HTML ya saneado) · `{{#if x}}…{{else}}…{{/if}}` · `{{#each lista}}…{{campo}} / {{.}}…{{/each}}`.
- **Portada**: `meta.*`, `cover.*` (title, vertical, text, …), `header_html`, `img` (data URI o vacío), `alt`, `syms` (símbolos sueltos del manifiesto), `foot_sym`,
  `words` (filas del titular: `text`, `mh` = tamaño máximo en cqw), `stack_rows`, `kicker`, `badge`, `quote_html`, `strip_html`, `list_items`, `note_items`, `atoms.*` (barcode, hazard, xbox, big_x, globe, cross1, cross2).
- **Divisor**: `cls`, `style_attr`, `number`, `total`, `label`, `part.*` (title, desc…), `desc_cls`, `head_sym`, `loose_sym`, `img`, `alt`.
- Atributos de ajuste que entiende el motor: `data-fit="w"` (reduce hasta caber en una línea), `data-fit="v"` / `"b"` (por alto), `data-fit="f"` + `data-maxh` (rellena el ancho exacto), `data-bleed` (puede sangrar fuera de la hoja).

## Lista de revisión
`python servidor/validar_diseno.py <id>`: manifiesto, fuentes con licencia, paletas (contraste ≥ 4,5 y claridad en grises), ≥ 2 portadas y ≥ 2 divisores,
clases CSS, símbolos de portada (3–5), plantillas sin campos sueltos, **documento de muestra corto y largo sin avisos ni desbordes**, sin redundancia, y cada portada/divisor renderizado.
Cuando todo sale ✔: `python servidor/galeria.py --design <id>` para aprobar variantes y `python servidor/prompt.py <id> --skill salida/skills` para el Prompt Maestro y la skill.

## Formatos de hoja
`manifest.formats_dims` puede declarar `{"pdf-letter": {"ph": 129.4, "pdf": "Letter"}}`. El diseño debe traer posiciones válidas para esa altura; ANURA solo declara A4.

## Protocolo de estilos nuevos (probado con `prompt-master`)
1. **Extraer** de la referencia (`leer_pdf.py` / `descomponer.py`): paleta vectorial exacta, tipografías, espaciado, bordes y sombras.
2. **Buscar parecido** antes de crear: `python servidor/biblioteca.py buscar "<descripción>" --tipo estilo`. Si hay uno cercano, ajústalo en vez de crear otro.
3. **Nombrar y versionar:** `crear_diseno.py <id> --base <parecido>`; `estilo` (familia) y `version` en el manifiesto. Al cambiar el CSS sube `version`: la API cachea por contenido + versión.
4. **Normas de base:** contraste de texto ≥ 4,5:1 (3:1 si es grande), rejilla de espaciado, márgenes mínimos, jerarquía tipográfica, sin superposición. `validar_diseno.py` las comprueba.
5. **Fuentes distintas a Anton/Archivo/Plex:** declara `font_roles: {display, body, mono}` en el manifiesto (si usas una sola fuente, el peso y el trazo se fijan en la capa CSS del diseño).
6. **Validar** hasta 10/10 ✔, **guardar con un ejemplo de uso** (`contenido/*.md|json` + catálogo) y registrar la entrada: `python servidor/tools/biblioteca_cargar.py`.
