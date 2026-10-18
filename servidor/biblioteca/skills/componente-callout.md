# Bloque «callout» (componente · v1.0)

Aviso con etiqueta.

**Cuándo usarlo:** Aviso con etiqueta.

**Parámetros:**
- `tone`: str — Tono.
- `label`: str — Rótulo.
- `title`: markup — Título.
- `text`: markup — Texto.
- `paras`: list — Varios párrafos.

**Ejemplo correcto:**
```json
{
 "type": "callout",
 "tone": "ojo",
 "text": "Advertencia breve."
}
```

**Error típico:** Olvidar un campo obligatorio: el contrato rechaza el documento.

Origen: engine/spec.py · Licencia: propia · Etiquetas: callout, aviso, nota, destacado