# Bloque «chart» (componente · v1.0)

Gráfico estándar en marco con título y pie. Ver tipos.

**Cuándo usarlo:** Gráfico estándar en marco con título y pie. Ver tipos.

**Parámetros:**
- `title`: markup — Título del gráfico (no repitas el titular de la hoja). Máx. 70.
- `tag`: markup — Etiqueta mono: fuente o tipo de dato.
- `chart`: obj (obligatorio) — {type, data[, legend]}
- `caption`: markup — Pie: «Figura N. …».
- `sim`: bool — Datos simulados (marco punteado).
- `half`: bool — Dos bloques half seguidos van lado a lado.

**Ejemplo correcto:**
```json
{
 "type": "chart",
 "title": "Acierto",
 "chart": {
  "type": "bar",
  "data": {
   "max": 100,
   "items": [
    {
     "l": "A",
     "v": 40,
     "hi": true
    },
    {
     "l": "B",
     "v": 62
    }
   ]
  }
 },
 "caption": "Figura 1. Muestra."
}
```

**Error típico:** Pasarse del límite de longitud (title ≤ 70): el motor recorta o reduce con aviso.

Origen: engine/spec.py · Licencia: propia · Etiquetas: chart, gráfico, barras, líneas