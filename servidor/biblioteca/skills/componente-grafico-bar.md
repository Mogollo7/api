# Gráfico «bar» (componente · v1.0)

Gráfico bar: comparar pocas categorías. Máximo 14 elementos.

**Cuándo usarlo:** comparar pocas categorías

**Parámetros:**
- `data`: items:[{l,v,hi?,err?,hatch?}] o series (agrupadas/apiladas): categories:[..], series:[{name,values:[..]}], mode:'grouped'|'stacked'; max, unit

**Ejemplo correcto:**
```json
{
 "type": "chart",
 "chart": {
  "type": "bar",
  "data": "…"
 }
}
```

**Error típico:** Pasar más de 14 elementos: el motor lo degrada con aviso.

Origen: engine/charts.py · Licencia: propia · Etiquetas: grafico, chart, bar