# Animación Lottie (lottie-web) (animacion · v1)

lottie-web está en servidor/video/vendor/lottie.min.js (MIT). Aún no hay bloque del contrato que lo use: se incrusta a mano en una página web con lottie.loadAnimation({container, path, loop:true}).

**Cuándo usarlo:** Ya va incluida: el director de video la aplica sola en cifras y barras.

**Parámetros:**
- `path`: archivo .json de Lottie
- `loop`: true|false

**Ejemplo correcto:**
```json
{
 "automatico": true
}
```

**Error típico:** Duraciones largas (> 1.5 s) retrasan la escena: el video de la API dura ≤ 120 s.

Origen: servidor/video/vendor (anime.js 4.5 · three 0.186 · lottie-web 5.13) · Licencia: MIT · Etiquetas: lottie, animacion, web, vector