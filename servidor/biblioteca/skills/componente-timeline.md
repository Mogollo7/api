# Bloque «timeline» (componente · v1.0)

Línea de vida: etapas con duración.

**Cuándo usarlo:** Línea de vida: etapas con duración.

**Parámetros:**
- `items`: list (obligatorio) — [{code,label,days,vis:'v|h|x',photo}]
- `adult`: obj — Etapa final sin duración.
- `legend`: list — [[clase,texto]]
- `caption`: markup — Pie.

**Ejemplo correcto:**
```json
{
 "type": "timeline",
 "items": [
  {
   "code": "H",
   "label": "Huevo",
   "days": 3,
   "vis": "h",
   "photo": "casi nunca"
  }
 ]
}
```

**Error típico:** Olvidar un campo obligatorio: el contrato rechaza el documento.

Origen: engine/spec.py · Licencia: propia · Etiquetas: timeline