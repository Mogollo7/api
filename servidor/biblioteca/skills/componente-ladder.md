# Bloque «ladder» (componente · v1.0)

Escalera de opciones de simple a complejo.

**Cuándo usarlo:** Escalera de opciones de simple a complejo.

**Parámetros:**
- `items`: list (obligatorio) — [{title,text,cost?}] Máx. 9.

**Ejemplo correcto:**
```json
{
 "type": "ladder",
 "items": [
  {
   "title": "Simple",
   "text": "…",
   "cost": "costo: bajo"
  }
 ]
}
```

**Error típico:** Pasarse del límite de longitud (items ≤ 9): el motor recorta o reduce con aviso.

Origen: engine/spec.py · Licencia: propia · Etiquetas: ladder