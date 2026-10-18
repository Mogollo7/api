# Bloque «p» (componente · v1.0)

Párrafo de texto.

**Cuándo usarlo:** Párrafo de texto.

**Parámetros:**
- `text`: markup (obligatorio) — Texto del párrafo. Máx. 1400.

**Ejemplo correcto:**
```json
{
 "type": "p",
 "text": "Texto con **negrita**, *Nombre científico* y una marca [FUENTE]."
}
```

**Error típico:** Pasarse del límite de longitud (text ≤ 1400): el motor recorta o reduce con aviso.

Origen: engine/spec.py · Licencia: propia · Etiquetas: p, párrafo, texto