# Entrada escalonada (web, anime.js) (animacion · v1)

En la salida web animada los hijos de cada sección suben y aparecen uno tras otro al entrar en pantalla. Se activa solo con format web-animada.

**Cuándo usarlo:** Ya va incluida: el director de video la aplica sola en cifras y barras.

**Parámetros:**
- `duracion`: 700 ms
- `escalon`: 90 ms
- `ease`: outExpo

**Ejemplo correcto:**
```json
{
 "automatico": true
}
```

**Error típico:** Duraciones largas (> 1.5 s) retrasan la escena: el video de la API dura ≤ 120 s.

Origen: servidor/video/vendor (anime.js 4.5 · three 0.186 · lottie-web 5.13) · Licencia: MIT · Etiquetas: web, anime, entrada, escalonado, scroll