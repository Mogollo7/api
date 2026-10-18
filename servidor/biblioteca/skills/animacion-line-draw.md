# Trazo de línea (animacion · v1)

Una línea o barra se dibuja de un extremo al otro. Para gráficos de barras, reglas y subrayados.

**Cuándo usarlo:** Ya va incluida: el director de video la aplica sola en cifras y barras.

**Parámetros:**
- `duracion`: 0.9 s
- `grosor`: rol del diseño
- `sentido`: horizontal|vertical

**Ejemplo correcto:**
```json
{
 "automatico": true
}
```

**Error típico:** Duraciones largas (> 1.5 s) retrasan la escena: el video de la API dura ≤ 120 s.

Origen: GSAP 3.14.2 (servidor/video/gsap.min.js) · Licencia: GSAP «no charge» (uso propio; revisar usos prohibidos si se distribuye) · Etiquetas: grafico, barras, linea, subrayado