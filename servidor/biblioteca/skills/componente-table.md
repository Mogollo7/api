# Bloque «table» (componente · v1.0)

Tabla; se parte por filas entre hojas repitiendo la cabecera.

**Cuándo usarlo:** Tabla; se parte por filas entre hojas repitiendo la cabecera.

**Parámetros:**
- `head`: list — Encabezados.
- `rows`: list (obligatorio) — Filas: listas de celdas (texto, número o {t,tone:'f|p|l|n',hi}). Máx. 40.
- `widths`: list — Anchos relativos.
- `caption`: markup — Pie de tabla.
- `variant`: str — Variante.

**Ejemplo correcto:**
```json
{
 "type": "table",
 "head": [
  "Variable",
  "Tipo"
 ],
 "rows": [
  [
   "edad",
   "int8"
  ],
  [
   "año",
   "int16"
  ]
 ]
}
```

**Error típico:** Pasarse del límite de longitud (rows ≤ 40): el motor recorta o reduce con aviso.

Origen: engine/spec.py · Licencia: propia · Etiquetas: table, tabla, filas, columnas