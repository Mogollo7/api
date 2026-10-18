# Bloque «custom» (componente · v1.0)

ÚLTIMO RECURSO: fragmento HTML saneado (solo etiquetas y clases permitidas). Úsalo solo si ningún bloque sirve.

**Cuándo usarlo:** ÚLTIMO RECURSO: fragmento HTML saneado (solo etiquetas y clases permitidas). Úsalo solo si ningún bloque sirve.

**Parámetros:**
- `html`: str (obligatorio) — HTML.

**Ejemplo correcto:**
```json
{
 "type": "custom",
 "html": "<p class=\"k\">Texto</p>"
}
```

**Error típico:** Olvidar un campo obligatorio: el contrato rechaza el documento.

Origen: engine/spec.py · Licencia: propia · Etiquetas: custom