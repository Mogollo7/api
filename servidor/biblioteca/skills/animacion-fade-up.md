# Aparecer subiendo (animacion · v1)

Entrada suave: el elemento sube unos píxeles mientras aparece. La de uso general para títulos y párrafos.

**Cuándo usarlo:** Se activa con options.video: {"options": {"video": {"entrada": "fade-up"}}}

**Parámetros:**
- `duracion`: 0.6 s
- `distancia`: 40 px
- `retraso`: 0 s

**Ejemplo correcto:**
```json
{
 "options": {
  "video": {
   "entrada": "fade-up"
  }
 }
}
```

**Error típico:** Duraciones largas (> 1.5 s) retrasan la escena: el video de la API dura ≤ 120 s.

Origen: GSAP 3.14.2 (servidor/video/gsap.min.js) · Licencia: GSAP «no charge» (uso propio; revisar usos prohibidos si se distribuye) · Etiquetas: aparecer, entrada, titulo, suave