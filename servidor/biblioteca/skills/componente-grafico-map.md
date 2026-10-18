# Gráfico «map» (componente · v1.0)

Gráfico map: ubicar puntos. Máximo 60 elementos.

**Cuándo usarlo:** ubicar puntos

**Parámetros:**
- `data`: outline:'colombia'|[[lon,lat]..], points:[{lon,lat,label,v}], size:bool, graticule:2

**Ejemplo correcto:**
```json
{
 "type": "chart",
 "chart": {
  "type": "map",
  "data": "…"
 }
}
```

**Error típico:** Pasar más de 60 elementos: el motor lo degrada con aviso.

Origen: engine/charts.py · Licencia: propia · Etiquetas: grafico, chart, map