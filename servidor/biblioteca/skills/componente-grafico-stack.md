# Gráfico «stack» (componente · v1.0)

Gráfico stack: composición 100 %. Máximo 8 elementos.

**Cuándo usarlo:** composición 100 %

**Parámetros:**
- `data`: rows:[{l,v:[a,b,c]}], total

**Ejemplo correcto:**
```json
{
 "type": "chart",
 "chart": {
  "type": "stack",
  "data": "…"
 }
}
```

**Error típico:** Pasar más de 8 elementos: el motor lo degrada con aviso.

Origen: engine/charts.py · Licencia: propia · Etiquetas: grafico, chart, stack