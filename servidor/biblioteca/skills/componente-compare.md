# Bloque «compare» (componente · v1.0)

Dos opciones enfrentadas con veredicto.

**Cuándo usarlo:** Dos opciones enfrentadas con veredicto.

**Parámetros:**
- `left`: obj (obligatorio) — {title,sub?,items}
- `right`: obj (obligatorio) — {title,sub?,items}
- `verdict`: markup — Veredicto.

**Ejemplo correcto:**
```json
{
 "type": "compare",
 "left": {
  "title": "A",
  "items": [
   "…"
  ]
 },
 "right": {
  "title": "B",
  "items": [
   "…"
  ]
 },
 "verdict": "A gana."
}
```

**Error típico:** Olvidar un campo obligatorio: el contrato rechaza el documento.

Origen: engine/spec.py · Licencia: propia · Etiquetas: compare