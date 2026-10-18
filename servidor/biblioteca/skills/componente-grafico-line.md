# Gráfico «line» (componente · v1.0)

Gráfico line: tendencia con pocos puntos o series. Máximo 14 elementos.

**Cuándo usarlo:** tendencia con pocos puntos o series

**Parámetros:**
- `data`: points:[[x,y,etiqueta?]] o series:[{name,points:[[x,y]..]}]; x puede ser texto/fecha ISO; xrange,yrange,xlabel,ylabel

**Ejemplo correcto:**
```json
{
 "type": "chart",
 "chart": {
  "type": "line",
  "data": "…"
 }
}
```

**Error típico:** Pasar más de 14 elementos: el motor lo degrada con aviso.

Origen: engine/charts.py · Licencia: propia · Etiquetas: grafico, chart, line