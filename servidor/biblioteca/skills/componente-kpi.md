# Bloque «kpi» (componente · v1.0)

2 a 4 tarjetas con cifra grande.

**Cuándo usarlo:** 2 a 4 tarjetas con cifra grande.

**Parámetros:**
- `items`: list (obligatorio) — [{v, l, note?}] Máx. 4.

**Ejemplo correcto:**
```json
{
 "type": "kpi",
 "items": [
  {
   "v": "62,9 %",
   "l": "top-1",
   "note": "[CALC]"
  },
  {
   "v": "86,1 %",
   "l": "top-3"
  }
 ]
}
```

**Error típico:** Pasarse del límite de longitud (items ≤ 4): el motor recorta o reduce con aviso.

Origen: engine/spec.py · Licencia: propia · Etiquetas: kpi, cifras, indicadores, métricas