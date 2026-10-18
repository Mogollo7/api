# Bloque «flowchart» (componente · v1.0)

Diagrama de flujo estándar (≤ 14 nodos, ≤ 3 por capa).

**Cuándo usarlo:** Diagrama de flujo estándar (≤ 14 nodos, ≤ 3 por capa).

**Parámetros:**
- `nodes`: list (obligatorio) — [{id,label,kind:'start|process|decision|io|end'}] Máx. 14.
- `edges`: list — [{from,to,label?}]
- `title`: markup — Título.
- `caption`: markup — Pie.

**Ejemplo correcto:**
```json
{
 "type": "flowchart",
 "nodes": [
  {
   "id": "a",
   "label": "Inicio",
   "kind": "start"
  },
  {
   "id": "b",
   "label": "Fin",
   "kind": "end"
  }
 ],
 "edges": [
  {
   "from": "a",
   "to": "b"
  }
 ]
}
```

**Error típico:** Pasarse del límite de longitud (nodes ≤ 14): el motor recorta o reduce con aviso.

Origen: engine/spec.py · Licencia: propia · Etiquetas: flowchart