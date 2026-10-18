# Bloque «ranks» (componente · v1.0)

Embudo de rangos con dos columnas de ejemplo.

**Cuándo usarlo:** Embudo de rangos con dos columnas de ejemplo.

**Parámetros:**
- `head`: list — Rótulos de columnas.
- `rows`: list (obligatorio) — [{rank, v:[a,b]}]

**Ejemplo correcto:**
```json
{
 "type": "ranks",
 "head": [
  "Rana",
  "Planta"
 ],
 "rows": [
  {
   "rank": "Reino",
   "v": [
    "Animalia",
    "Plantae"
   ]
  }
 ]
}
```

**Error típico:** Olvidar un campo obligatorio: el contrato rechaza el documento.

Origen: engine/spec.py · Licencia: propia · Etiquetas: ranks