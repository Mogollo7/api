# Bloque «quote» (componente · v1.0)

Cita destacada con autor.

**Cuándo usarlo:** Cita destacada con autor.

**Parámetros:**
- `text`: markup (obligatorio) — Cita. Máx. 500.
- `by`: markup — Autor o fuente.

**Ejemplo correcto:**
```json
{
 "type": "quote",
 "text": "Feo es poderoso.",
 "by": "Manifiesto"
}
```

**Error típico:** Pasarse del límite de longitud (text ≤ 500): el motor recorta o reduce con aviso.

Origen: engine/spec.py · Licencia: propia · Etiquetas: quote, cita, frase