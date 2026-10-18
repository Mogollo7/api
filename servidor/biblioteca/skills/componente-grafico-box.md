# Gráfico «box» (componente · v1.0)

Gráfico box: dispersión y atípicos por grupo. Máximo 40 elementos.

**Cuándo usarlo:** dispersión y atípicos por grupo

**Parámetros:**
- `data`: groups:[{l,lo,q1,med,q3,hi,out:[..]}], xrange, xticks, xlabel

**Ejemplo correcto:**
```json
{
 "type": "chart",
 "chart": {
  "type": "box",
  "data": "…"
 }
}
```

**Error típico:** Pasar más de 40 elementos: el motor lo degrada con aviso.

Origen: engine/charts.py · Licencia: propia · Etiquetas: grafico, chart, box