# Bloque «big» (componente · v1.0)

Una cifra gigante con su leyenda.

**Cuándo usarlo:** Una cifra gigante con su leyenda.

**Parámetros:**
- `value`: str (obligatorio) — Cifra.
- `unit`: str — Unidad.
- `caption`: markup (obligatorio) — Leyenda.

**Ejemplo correcto:**
```json
{
 "type": "big",
 "value": "62,9",
 "unit": "%",
 "caption": "Acierto top-1"
}
```

**Error típico:** Olvidar un campo obligatorio: el contrato rechaza el documento.

Origen: engine/spec.py · Licencia: propia · Etiquetas: big