# Bloque «image» (componente · v1.0)

Foto en dos tintas con pie y crédito. Si no tienes la imagen, escribe `need` y el servidor dibuja «IMAGEN NECESARIA».

**Cuándo usarlo:** Foto en dos tintas con pie y crédito. Si no tienes la imagen, escribe `need` y el servidor dibuja «IMAGEN NECESARIA».

**Parámetros:**
- `src`: str — Ruta relativa a la carpeta de imágenes.
- `need`: markup — Qué imagen hace falta si no existe.
- `caption`: markup — Pie (sirve de texto alternativo).
- `alt`: str — Texto alternativo.
- `ratio`: str — Proporción, p. ej. 16/9.
- `treatment`: str — Tinta.
- `items`: list — Hasta 3 imágenes en fila: [{src,caption,…}] Máx. 3.

**Ejemplo correcto:**
```json
{
 "type": "image",
 "src": "fauna/rana.jpg",
 "ratio": "16/9",
 "caption": "Pie de la imagen."
}
```

**Error típico:** Pasarse del límite de longitud (items ≤ 3): el motor recorta o reduce con aviso.

Origen: engine/spec.py · Licencia: propia · Etiquetas: image