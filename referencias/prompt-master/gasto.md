# Gasto de tokens al crear el estilo «prompt-master» (sesión Claude Code, modelo Sonnet 5.5)

Fuente: el contador `total_tokens` restante que muestra la sesión después de cada llamada (no hay contador por paso; los pasos se miden como diferencia entre dos lecturas).
**Medido, aproximado:** las lecturas intermedias se tomaron cada pocas llamadas, así que el desglose es de orden de magnitud; el total sí es una diferencia directa.

| Paso | Tokens aprox. | Qué incluye |
|---|---|---|
| 1 · Leer la referencia (`leer_pdf.py` + `contacto.png` + 5 KB de `resumen.md`) | ~9 000 | la imagen de contacto pesa más que el texto |
| 2 · Crear el diseño (manifiesto, paletas, 4 plantillas, capa CSS) | ~35 000 | incluye 4 iteraciones visuales (contacto de portadas/divisores) |
| 3 · Validar (`validar_diseno.py`) hasta 10/10 | ~8 000 | 3 fallos corregidos: contraste de la paleta «noche», símbolos de portada, título de portada |
| 4 · Documento nuevo (Markdown → contrato → PDF y PPTX por la API) | ~18 000 | contenido de 7 secciones + 2 renders + 1 revisión visual |
| 5 · Publicar y catalogar | ~6 000 | galería, `catalogo.py`, comprobar /estilos |
| **Total del estilo** | **≈ 76 000** | de 14 815 024 a 14 734 220 restantes en la sesión (≈ 80 800 contando ajustes de /estilos) |

## Qué se aprendió (y cuesta menos la próxima vez)
- Las iteraciones visuales dominan el gasto (≈ 45 %). Con un diseño base que ya trae la **capa de fuentes por rol** (`font_roles`, nuevo en el motor) y el script de la capa CSS, un estilo parecido baja a ~40 000.
- Fallo real del motor encontrado y corregido en el origen: las fuentes de `--font-display/--font-body/--font-mono` estaban fijas (Anton/Archivo/IBM Plex Mono). Ahora un diseño puede declarar `font_roles` en su manifiesto (`engine/assets.py`).
- La API cachea por contenido + versión del diseño: al iterar sobre el CSS hay que subir `version` en el manifiesto o renderizar con `render.py`.
- **Space Grotesk no se descargó** (la referencia lo usa en los numerales): quedó pendiente de tu aprobación; los numerales usan Archivo 900.
