# Bloque «list» (componente · v1.0)

Lista con viñetas o numerada; un ítem puede llevar sublista {t, items}.

**Cuándo usarlo:** Lista con viñetas o numerada; un ítem puede llevar sublista {t, items}.

**Parámetros:**
- `items`: list (obligatorio) — Ítems (texto o {t, items:[…]}). Máx. 14.
- `ordered`: bool — Numerada.

**Ejemplo correcto:**
```json
{
 "type": "list",
 "ordered": true,
 "items": [
  "Primero",
  {
   "t": "Segundo",
   "items": [
    "detalle a",
    "detalle b"
   ]
  },
  "Tercero"
 ]
}
```

**Error típico:** Pasarse del límite de longitud (items ≤ 14): el motor recorta o reduce con aviso.

Origen: engine/spec.py · Licencia: propia · Etiquetas: list, lista, viñetas