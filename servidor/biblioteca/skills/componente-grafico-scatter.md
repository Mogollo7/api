# Gráfico «scatter» (componente · v1.0)

Gráfico scatter: relación entre dos variables. Máximo 400 elementos.

**Cuándo usarlo:** relación entre dos variables

**Parámetros:**
- `data`: points:[[x,y]], trend:'auto'|{slope,intercept,label}, xrange,yrange,xticks,yticks,xlabel,ylabel

**Ejemplo correcto:**
```json
{
 "type": "chart",
 "chart": {
  "type": "scatter",
  "data": "…"
 }
}
```

**Error típico:** Pasar más de 400 elementos: el motor lo degrada con aviso.

Origen: engine/charts.py · Licencia: propia · Etiquetas: grafico, chart, scatter