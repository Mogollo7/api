# Bloque «flow» (componente · v1.0)

Pasos en tarjetas (proceso lineal).

**Cuándo usarlo:** Pasos en tarjetas (proceso lineal).

**Parámetros:**
- `steps`: list (obligatorio) — [{title,text?,n?,on?}] Máx. 9.
- `cols`: num — Columnas 2–4.

**Ejemplo correcto:**
```json
{
 "type": "flow",
 "cols": 3,
 "steps": [
  {
   "title": "Uno",
   "text": "…"
  },
  {
   "title": "Dos",
   "on": true
  }
 ]
}
```

**Error típico:** Pasarse del límite de longitud (steps ≤ 9): el motor recorta o reduce con aviso.

Origen: engine/spec.py · Licencia: propia · Etiquetas: flow