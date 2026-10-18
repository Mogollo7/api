# Bloque «stats» (componente · v1.0)

Cifras en columna con regla vertical.

**Cuándo usarlo:** Cifras en columna con regla vertical.

**Parámetros:**
- `items`: list (obligatorio) — [{v,l}]
- `title`: markup — Rótulo.
- `note`: markup — Nota.

**Ejemplo correcto:**
```json
{
 "type": "stats",
 "items": [
  {
   "v": "9,0",
   "l": "moda"
  },
  {
   "v": "8,0",
   "l": "mediana"
  }
 ]
}
```

**Error típico:** Olvidar un campo obligatorio: el contrato rechaza el documento.

Origen: engine/spec.py · Licencia: propia · Etiquetas: stats