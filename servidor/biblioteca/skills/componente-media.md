# Bloque «media» (componente · v1.0)

GIF o video. PDF imprime el póster con «▶»; web reproduce; PPTX lo incrusta.

**Cuándo usarlo:** GIF o video. PDF imprime el póster con «▶»; web reproduce; PPTX lo incrusta.

**Parámetros:**
- `kind`: str (obligatorio) — gif | video.
- `src`: str (obligatorio) — Archivo.
- `poster`: str — Imagen de póster.
- `caption`: markup — Pie.
- `credit`: str — Autor y licencia.
- `alt`: str (obligatorio) — Texto alternativo.
- `url`: str — Enlace al video.

**Ejemplo correcto:**
```json
{
 "type": "media",
 "kind": "video",
 "src": "clips/demo.mp4",
 "poster": "clips/demo.png",
 "alt": "Demostración del proceso",
 "caption": "Video 1."
}
```

**Error típico:** Olvidar un campo obligatorio: el contrato rechaza el documento.

Origen: engine/spec.py · Licencia: propia · Etiquetas: media