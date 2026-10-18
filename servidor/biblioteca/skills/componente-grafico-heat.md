# Gráfico «heat» (componente · v1.0)

Gráfico heat: correlaciones. Máximo 12 elementos.

**Cuándo usarlo:** correlaciones

**Parámetros:**
- `data`: labels:[..], matrix:[[..]], range:[min,max]

**Ejemplo correcto:**
```json
{
 "type": "chart",
 "chart": {
  "type": "heat",
  "data": "…"
 }
}
```

**Error típico:** Pasar más de 12 elementos: el motor lo degrada con aviso.

Origen: engine/charts.py · Licencia: propia · Etiquetas: grafico, chart, heat