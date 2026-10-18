# Bloque «code» (componente · v1.0)

Bloque de código o texto monoespaciado (no se interpreta).

**Cuándo usarlo:** Bloque de código o texto monoespaciado (no se interpreta).

**Parámetros:**
- `code`: str (obligatorio) — Código. Máx. 1500.
- `lang`: str — Lenguaje.
- `caption`: markup — Pie.

**Ejemplo correcto:**
```json
{
 "type": "code",
 "lang": "python",
 "code": "df.info()"
}
```

**Error típico:** Pasarse del límite de longitud (code ≤ 1500): el motor recorta o reduce con aviso.

Origen: engine/spec.py · Licencia: propia · Etiquetas: code, código