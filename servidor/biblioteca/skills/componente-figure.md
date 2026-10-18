# Bloque «figure» (componente · v1.0)

Figura (gráfico o imagen) con columna de cifras laterales (7/10 + 3/10).

**Cuándo usarlo:** Figura (gráfico o imagen) con columna de cifras laterales (7/10 + 3/10).

**Parámetros:**
- `chart`: obj — Como en chart.
- `image`: obj — Como en image.
- `title`: markup — Título.
- `caption`: markup — Pie.
- `side`: list — Cifras: [{v,l}].
- `side_note`: markup — Nota bajo las cifras.
- `side_title`: markup — Rótulo de la columna.

**Ejemplo correcto:**
```json
{
 "type": "figure",
 "chart": {
  "type": "bar",
  "data": {
   "items": [
    {
     "l": "A",
     "v": 3
    }
   ]
  }
 },
 "caption": "Figura 2.",
 "side": [
  {
   "v": "0,34",
   "l": "r de Pearson"
  }
 ]
}
```

**Error típico:** Olvidar un campo obligatorio: el contrato rechaza el documento.

Origen: engine/spec.py · Licencia: propia · Etiquetas: figure, figura, imagen, foto