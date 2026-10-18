# Fondo 3D de portada (three.js) (animacion · v1)

Icosaedro de alambre girando detrás de la portada web, con el color de acento del diseño. Solo desde la línea de comandos: python servidor/web.py doc.json --animar --fondo3d.

**Cuándo usarlo:** Ya va incluida: el director de video la aplica sola en cifras y barras.

**Parámetros:**
- `rotacion`: 0.003/0.005 rad por cuadro
- `opacidad`: 0.35

**Ejemplo correcto:**
```json
{
 "automatico": true
}
```

**Error típico:** Duraciones largas (> 1.5 s) retrasan la escena: el video de la API dura ≤ 120 s.

Origen: servidor/video/vendor (anime.js 4.5 · three 0.186 · lottie-web 5.13) · Licencia: MIT · Etiquetas: web, three, 3d, portada, fondo