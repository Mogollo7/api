# Contador (animacion · v1)

Un número sube desde 0 hasta su valor. Para cifras clave en video.

**Cuándo usarlo:** Ya va incluida: el director de video la aplica sola en cifras y barras.

**Parámetros:**
- `duracion`: 1.2 s
- `decimales`: 0
- `formato`: texto con prefijo/sufijo

**Ejemplo correcto:**
```json
{
 "automatico": true
}
```

**Error típico:** Duraciones largas (> 1.5 s) retrasan la escena: el video de la API dura ≤ 120 s.

Origen: GSAP 3.14.2 (servidor/video/gsap.min.js) · Licencia: GSAP «no charge» (uso propio; revisar usos prohibidos si se distribuye) · Etiquetas: cifra, numero, kpi, contador