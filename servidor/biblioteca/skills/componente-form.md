# Bloque «form» (componente · v1.0)

Ficha de datos con filas para completar.

**Cuándo usarlo:** Ficha de datos con filas para completar.

**Parámetros:**
- `title`: markup — Título.
- `rows`: list (obligatorio) — Etiquetas.

**Ejemplo correcto:**
```json
{
 "type": "form",
 "title": "Datos del estudiante",
 "rows": [
  "Nombre completo",
  "Fecha"
 ]
}
```

**Error típico:** Olvidar un campo obligatorio: el contrato rechaza el documento.

Origen: engine/spec.py · Licencia: propia · Etiquetas: form