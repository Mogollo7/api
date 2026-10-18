# Gráfico «pie» (componente · v1.0)

Gráfico pie: partes de un todo (≤ 7). Máximo 7 elementos.

**Cuándo usarlo:** partes de un todo (≤ 7)

**Parámetros:**
- `data`: items:[{l,v}] (suman el total); donut:true para dona

**Ejemplo correcto:**
```json
{
 "type": "chart",
 "chart": {
  "type": "pie",
  "data": "…"
 }
}
```

**Error típico:** Pasar más de 7 elementos: el motor lo degrada con aviso.

Origen: engine/charts.py · Licencia: propia · Etiquetas: grafico, chart, pie