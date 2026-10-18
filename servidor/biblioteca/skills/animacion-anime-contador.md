# Contador de cifras (web, anime.js) (animacion · v1)

Las cifras clave de la web animada cuentan desde 0 hasta su valor al aparecer; respeta prefijo, sufijo y decimales.

**Cuándo usarlo:** Ya va incluida: el director de video la aplica sola en cifras y barras.

**Parámetros:**
- `duracion`: 1100 ms
- `ease`: outCubic

**Ejemplo correcto:**
```json
{
 "automatico": true
}
```

**Error típico:** Duraciones largas (> 1.5 s) retrasan la escena: el video de la API dura ≤ 120 s.

Origen: servidor/video/vendor (anime.js 4.5 · three 0.186 · lottie-web 5.13) · Licencia: MIT · Etiquetas: web, anime, cifra, contador, kpi