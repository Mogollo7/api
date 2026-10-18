# Gráfico «hbar» (componente · v1.0)

Gráfico hbar: etiquetas largas. Máximo 20 elementos.

**Cuándo usarlo:** etiquetas largas

**Parámetros:**
- `data`: items:[{l,v,hi?}], max

**Ejemplo correcto:**
```json
{
 "type": "chart",
 "chart": {
  "type": "hbar",
  "data": "…"
 }
}
```

**Error típico:** Pasar más de 20 elementos: el motor lo degrada con aviso.

Origen: engine/charts.py · Licencia: propia · Etiquetas: grafico, chart, hbar