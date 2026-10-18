# Bloque «refs» (componente · v1.0)

Referencias o bibliografía numerada.

**Cuándo usarlo:** Referencias o bibliografía numerada.

**Parámetros:**
- `items`: list (obligatorio) — Cada referencia como texto. Máx. 40.
- `title`: markup — Título.

**Ejemplo correcto:**
```json
{
 "type": "refs",
 "items": [
  "Autor (2024). Título. Revista."
 ]
}
```

**Error típico:** Pasarse del límite de longitud (items ≤ 40): el motor recorta o reduce con aviso.

Origen: engine/spec.py · Licencia: propia · Etiquetas: refs