# Gráfico «hist» (componente · v1.0)

Gráfico hist: distribución de una variable. Máximo 40 elementos.

**Cuándo usarlo:** distribución de una variable

**Parámetros:**
- `data`: bars:[[x,conteo]], width, xrange, xticks, lines:[{x,label,style:'mean'|'median'}], xlabel, ylabel

**Ejemplo correcto:**
```json
{
 "type": "chart",
 "chart": {
  "type": "hist",
  "data": "…"
 }
}
```

**Error típico:** Pasar más de 40 elementos: el motor lo degrada con aviso.

Origen: engine/charts.py · Licencia: propia · Etiquetas: grafico, chart, hist