# Cuadrícula escalonada (animacion · v1)

Los elementos de una cuadrícula o lista entran uno tras otro (retraso corto entre ellos). Para tarjetas, cifras y logos.

**Cuándo usarlo:** Se activa con options.video: {"options": {"video": {"escalon": 0.12}}}

**Parámetros:**
- `duracion`: 0.5 s
- `escalon`: 0.08 s
- `desde`: start|center|end

**Ejemplo correcto:**
```json
{
 "options": {
  "video": {
   "escalon": 0.12
  }
 }
}
```

**Error típico:** Duraciones largas (> 1.5 s) retrasan la escena: el video de la API dura ≤ 120 s.

Origen: GSAP 3.14.2 (servidor/video/gsap.min.js) · Licencia: GSAP «no charge» (uso propio; revisar usos prohibidos si se distribuye) · Etiquetas: escalonado, tarjetas, rejilla, cifras