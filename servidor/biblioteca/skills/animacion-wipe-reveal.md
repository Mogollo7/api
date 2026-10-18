# Revelado con cortina (animacion · v1)

Una cortina de color descubre el titular de izquierda a derecha. Estilo brutalista, para portadas y divisores.

**Cuándo usarlo:** Se activa con options.video: {"options": {"video": {"entrada": "wipe-reveal"}}}

**Parámetros:**
- `duracion`: 0.7 s
- `color`: rol del diseño
- `direccion`: izquierda|derecha

**Ejemplo correcto:**
```json
{
 "options": {
  "video": {
   "entrada": "wipe-reveal"
  }
 }
}
```

**Error típico:** Duraciones largas (> 1.5 s) retrasan la escena: el video de la API dura ≤ 120 s.

Origen: GSAP 3.14.2 (servidor/video/gsap.min.js) · Licencia: GSAP «no charge» (uso propio; revisar usos prohibidos si se distribuye) · Etiquetas: titular, cortina, portada, brutalista