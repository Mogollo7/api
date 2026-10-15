# Guía de trabajo: identificación de especies con IA + estilo visual

Documento vivo. Agrupa la teoría, las notas y el estilo visual del proyecto. Se organiza en tres partes.

## Índice
**Parte 1 (base)** · §1 Teoría · §2 Estilo visual · §3 Imágenes y gráficos · §4 Reparto por modelo · §5 Identidad · §6 Datos a pedir · §6b Ruta de método · §7 Dudas
**Parte 2 (investigación)** · §8 BioCLIP 1, 2, 2.5 · §9 Otros modelos · §10 Métodos (transfer learning, destilación, FP16, segmentación, caché) · §11 Taxonomía y especies casi idénticas · §12 Contexto, plagas y plantas · §13 Verificación del texto del usuario
**Parte 3 (auditoría y ampliación)** · §15 ¿Se aplica a cualquier especie? · §16 Qué preguntar a una foto · §17 Etapa, sexo y edad · §18 Enfermedad en fauna y flora · §19 Método por organismo · §20 Diseño multi-pregunta · §21 Límites · §22 Pendientes (sustituido) · §23 Tabla de contenido v1
**Parte 4 (decisiones del usuario y caso conductor)** · §24 Rango taxonómico como alcance · §26 Especie × etapa × sexo · §27 Etiquetar bien · §28 Fine-tuning frente a congelado · §29 Contexto dinámico · §30 Pocas imágenes y aumentación · §31 De animal a flora · §32 Caso *Frankliniella* · §33 Tabla de contenido definitiva · §34 Pendientes vigentes

---

## 1. Teoría: cómo un modelo identifica especies

### 1.1 La idea base
Un modelo de clasificación de imágenes aprende una función `f(imagen) → probabilidades por especie`. No "conoce" especies: aprende patrones visuales (forma de la hoja, patrón de manchas, proporción del cuerpo, textura de la piel) a partir de ejemplos etiquetados.

- **Clasificación**: una etiqueta por imagen (la especie más probable).
- **Detección**: localiza el animal o la planta dentro de la imagen (caja delimitadora) antes de clasificar.
- **Búsqueda por similitud**: útil cuando hay miles de especies o aparecen especies nuevas; compara embeddings en lugar de clases fijas.

### 1.2 Arquitecturas habituales
| Familia | Ejemplos | Cuándo usarla |
|---|---|---|
| CNN ligera | MobileNetV3 | Móvil y tiempo real (caso del proyecto Anura) |
| CNN clásica | ResNet-50 | Línea base sólida, fácil de entrenar |
| Transformer de visión | ViT, DINOv2 | Mejor precisión con mucho dato; más pesado |

Para un prototipo: **transferencia de aprendizaje** sobre un modelo preentrenado en ImageNet. Se congela el backbone y se entrena solo la última capa.

### 1.3 Datos: lo que más pesa
- **Fuentes abiertas**: iNaturalist, GBIF, Wikimedia Commons (revisar licencias).
- **Equilibrio**: intentar ≥ 100 imágenes por especie; evitar que una especie tenga 3 000 y otra 40.
- **Variedad**: distintos ángulos, luz, fondos, edades del ejemplar, estaciones.
- **Separación**: entrenamiento / validación / prueba **por fuente o por observación**, no al azar. Si la misma foto aparece en train y test, la métrica miente.
- **Aumento de datos**: volteo, recorte aleatorio, cambio de color leve, desenfoque. No invertir colores ni rotar ciegamente (una hoja de cabeza abajo sigue siendo esa hoja, pero una figura espejada puede cambiar una clave diagnóstica).

### 1.4 Entrenamiento y métricas
- Función de pérdida: entropía cruzada. Si hay mucha desigualdad, pesos por clase o *focal loss*.
- Métricas: **top-1** (la primera opción acierta), **top-5** (la verdadera está entre las cinco primeras), y **F1 por especie**. La exactitud global engaña si hay clases dominantes.
- Matriz de confusión: revela qué especies se confunden entre sí (las pareadas suelen ser parientes cercanos).
- Calibración: que "90 % de confianza" signifique que acierta alrededor del 90 %. Útil para decidir cuándo pedir una segunda foto o decir "no sé".

### 1.5 Limitaciones que hay que explicar en el trabajo
- **Sesgo geográfico**: si el dataset es de Europa, falla en Colombia.
- **Especies raras**: pocos ejemplos, peor rendimiento. Mostrar "no identificado" es mejor que adivinar.
- **Confusión de especies similares** (criptícas, mimetismo).
- **No sustituye a un especialista**: el resultado es una sugerencia con un porcentaje.

### 1.6 Pipeline de referencia
1. Definir el alcance: cuántas especies, en qué región, en móvil o web.
2. Recolectar y limpiar datos; documentar fuente y licencia de cada imagen.
3. Dividir train / val / test por observación.
4. Entrenar línea base (MobileNet o ResNet con transferencia).
5. Evaluar con top-1, top-5, F1 por especie y matriz de confusión.
6. Exportar (ONNX; si es móvil, cuantizar a fp16 o int8 y medir latencia en el dispositivo).
7. Probar con fotos nuevas tomadas en campo, no solo con el test.
8. Interfaz: mostrar las 3 mejores opciones con su porcentaje y una advertencia de límite.

---

## 2. Estilo visual del proyecto

### 2.1 Paleta (dada por el usuario)
| Rol | Color | Uso |
|---|---|---|
| Base oscura | `#0b0d12` (negro azulado de las referencias) | Fondo de portada y de páginas de impacto |
| Acento principal | `#dfff04` (verde lima neón) | Títulos destacados, bloques, bocadillos de la mascota, barras de énfasis |
| Papel | `#ffffff` | Fondo de lectura, tarjetas |
| Tinta | `#000000` | Texto sobre blanco, líneas |

Regla: el lima se usa como **acento**, no como fondo de texto largo. Sobre negro, el texto va en blanco o lima; sobre lima, el texto va en negro.

### 2.2 Tipografía
- **Títulos**: Aquire (incluida en `fonts/`). Pesos disponibles: Light, Regular (`Aquire-BW0ox.otf`), Bold.
- **Cuerpo**: usar una sans legible; la del sistema de diseño actual (Source Serif 4 / JetBrains Mono) sigue para texto corrido y código.
- Licencia de Aquire: **Freeware, uso no comercial** (ver `fonts/`). Si el proyecto se monetiza, cambiar de fuente.

### 2.3 Forma: esquinas interiores y retrofuturismo
- Bloques con **esquinas interiores redondeadas** (las esquinas cóncavas que se ven en las referencias: un panel que se "recorta" hacia dentro).
- Líneas finas tipo **trazo ondulado / resorte** como detalle decorativo (referencia de la portada cyberpunk).
- Elementos geométricos: rombos y estrellas de cuatro puntas como marcadores.
- Patrón de **puntos** (cuadrícula o esfera) como textura, siempre fuera del texto.
- Sin sombras suaves ni degradados de moda; contraste plano y bloques sólidos.

### 2.3.1 Disposición inner corner: piezas con nombre
Recreación en `inner-corner-layout.html`. Para pedir una pieza, usa su nombre.

| # | Nombre | Qué es |
|---|---|---|
| 1 | `marco` | Panel claro (papel) con radio grande; la hoja base. |
| 2 | `forma-lima` | Rectángulos fusionados en una silueta: esquinas exteriores convexas y **esquinas interiores** cóncavas del mismo radio donde se unen. Gesto principal. |
| 3 | `codigo-serie` | Identificador corto ("S-384x") en la esquina libre del marco. |
| 4 | `barras-carga` | Cuatro barras inclinadas, la última más ancha. |
| 5 | `boton-circular` | Círculo negro con icono, alojado en la pestaña superior de la forma lima. |
| 6 | `dato-destacado` | Rótulo pequeño + cifra grande, alineado a la derecha. |
| 7 | `etiqueta-icono` | Icono + categoría encima del titular. |
| 8 | `titular-display` | Palabra gigante en Aquire Bold, comprimida en ancho y estirada en alto. |
| 9 | `chips-opcion` | Píldoras (activa en negro, otra en contorno) dentro de la **muesca**: el hueco de extremo semicircular en el borde de la forma lima. |
| 10 | `icono-pixel` | Dibujo en matriz de puntos redondeados con algunos grises. |
| 11 | `sello` | Aro grueso con muescas como cierre en la esquina inferior. |
| 12 | `figura` | Ilustración recortada que rompe el marco y tapa parte del titular. **Necesita imagen** (PNG sin fondo). |

Nota: Aquire solo tiene mayúsculas; todo texto en Aquire se ve en caja alta.

### 2.4 Mascota con bocadillo
- La mascota habla siempre con un **bocadillo** (globo de diálogo) con la cola apuntando a ella.
- Bocadillo en lima con texto negro, o negro con borde lima y texto lima.
- Máximo una frase corta por bocadillo.

### 2.5 Hojas del PDF
- Puedes elegir entre fondo de lima, negro o blanco por hoja.
- Cada sección alterna fondo: portada negra, secciones blancas con acento lima, cierre lima.

---

## 3. Necesidades de imagen, mockup y gráficos

Cuando una sección necesite una imagen, un mockup o un gráfico, anotar aquí:

| Sección | Tipo | Descripción exacta | Fuente o herramienta | Estado |
|---|---|---|---|---|
| Portada | Ilustración | Figura humana o de especie con estética cyber/moda | Imagen de referencia del usuario o generada | Pendiente |
| Pipeline | Diagrama | Flujo de 8 pasos del apartado 1.6 | `/dataviz` o SVG a mano | Pendiente |
| Resultados | Gráfico | Barras top-1 por especie + matriz de confusión | `/dataviz` | Pendiente |
| App | Mockup | Pantalla de resultado: foto, 3 especies, porcentajes | `/frontend-design` | Pendiente |

Gráficos: el usuario prefiere **tablero visual / dashboard informativo** (tarjetas de métrica, mini gráficos, indicadores), no gráficos planos por defecto. Diseño con `/ui-ux-pro-max`.

---

## 4. Flujo de trabajo por modelo (de `pormt.txt`)
- **Haiku**: organiza carpetas, recopila notas, prepara el plan y la lista de diagramas.
- **Sonnet**: investiga, redacta el texto y las citas APA; entrega texto por sección con descripción exacta de cada diagrama.
- **Opus**: revisa exactitud técnica y aprueba el diseño antes de producir archivos finales.

---

## 5. Identidad visual de la Guía de IA
Resumen; la versión visual completa está en `identidad.html` y en el artefacto (componentes FondoGlifos, Hojas, ElementosHUD, InnerCorner).

- **Fondo de glifos** grises (◎ ✕ □ ⧈ + ·) en manchas que se deshacen en puntos; sustituye a la cuadrícula de puntos. Nunca bajo texto.
- **Portadas con aire**: GUÍA DE IA + "Cómo hacer que un modelo distinga animales". Cuatro variantes: Zócalo, Negra con pestaña, Panel superior, Columna.
- **Hojas interiores**: normal (papel), verde de punto clave, negra de apertura, tablero de datos.
- **Texto**: títulos en Aquire (sin tildes), texto corrido en Bricolage 10 pt / 1,55, HUD en JetBrains Mono mayúsculas.
- **Auditoría**: tabla de reglas en `identidad.html`, sección 6.

---

## 6. Datos que necesito (para pedir a la DB)
Lo que no aparezca en el stack o en los md que me pases:

| # | Dato | Para qué sección |
|---|---|---|
| 1 | Lista de especies: nombre común y científico, y región | Alcance, portada interior, tablero |
| 2 | Imágenes por especie y reparto entrenamiento / validación / prueba | Datos, gráfico de equilibrio |
| 3 | Fuente y licencia de cada conjunto de imágenes | Datos, créditos |
| 4 | Modelo exacto: arquitectura, tamaño de entrada, épocas, optimizador, tasa de aprendizaje, aumentos | Entrenamiento |
| 5 | Métricas: top-1, top-5, F1 por especie, matriz de confusión | Tablero de resultados |
| 6 | Pares de especies que más se confunden, con ejemplos | Limitaciones |
| 7 | Formato exportado, tamaño en MB y latencia en el Redmi Note 13 Pro+ | Despliegue |
| 8 | Fotos de ejemplo por especie y una figura PNG sin fondo para la portada | Figuras |
| 9 | Notas de compañeros: autor y fecha | Créditos |

---

## 6b. Guía universal: ruta de método para cualquier animal o cosa

Objetivo: con el stack disponible, saber qué ruta seguir, qué método probar primero y qué resultado esperar, sin importar si lo que se identifica es un animal, una planta, un objeto o una pieza de máquina.

> Evidencia medida de un caso real (ranas de Colombia, 41 especies): ver `anura-hallazgos.md`, sobre todo la sección 10, que traduce cada hallazgo a una regla de decisión.

### Paso 0 · Define la pregunta
| Pregunta | Ejemplo |
|---|---|
| ¿Qué se distingue? | Especie, raza, pieza, estado (sano o dañado) |
| ¿Cuántas clases? | 5, 50, 5 000 o "abierto" |
| ¿Dónde corre? | Móvil, web, servidor, sin conexión |
| ¿Qué error es peor? | Confundir dos clases parecidas, o no reconocer nada |

### Paso 1 · Mira los datos antes de elegir modelo
| Situación | Ruta recomendada |
|---|---|
| Menos de 50 imágenes por clase | Embeddings preentrenados + vecino más cercano (sin entrenar). Empieza aquí. |
| 50 a 500 imágenes por clase | Transferencia: congelar el backbone y entrenar la última capa. |
| Más de 500 por clase y buen equilibrio | Ajuste fino de todo el modelo, con aumentos. |
| Clases que aparecen o cambian a menudo | Búsqueda por similitud sobre embeddings; se añaden clases sin reentrenar. |
| Sin etiquetas | Clustering de embeddings y etiquetado asistido. |
| Pregunta en lenguaje natural o sin ejemplos | Modelo multimodal (visión y lenguaje) en modo cero disparos, como línea base. |

### Paso 2 · Escalera de métodos (de más simple a más complejo)
1. **Línea base sin entrenar**: embeddings de un modelo preentrenado + distancia coseno. Mide el techo fácil.
2. **Clasificador lineal sobre embeddings**: regresión logística sobre esos embeddings.
3. **Transferencia con ajuste de la última capa**: MobileNet o ResNet, pocas épocas.
4. **Ajuste fino completo**: solo si el paso 3 se queda corto y hay datos.
5. **Detección + clasificación**: si hay varios animales o la especie ocupa poca imagen. Detector primero, clasificador después.
6. **Ensamble o modelo grande en servidor**: solo para cerrar el último punto de precisión.

Regla: pasa al siguiente paso solo si el actual no alcanza el objetivo de métrica y el coste (datos, tiempo, tamaño) lo justifica.

### Paso 3 · Evalúa siempre igual
- **Top-1 y top-5**, F1 por clase y matriz de confusión.
- Conjunto de prueba separado **por observación** (la misma foto nunca en train y test).
- Prueba en campo con fotos nuevas, no solo con el conjunto de prueba.
- Un umbral de confianza: por debajo, "no sé" y pedir otra foto.

### Paso 4 · Resultados que puedes esperar (orientativos)
| Método | Cuándo sale bien | Riesgo principal |
|---|---|---|
| Vecino más cercano | Pocas imágenes, clases bien separadas | Falla con clases parecidas |
| Transferencia (última capa) | Dataset mediano, buena calidad | Sesgo del dataset de origen |
| Ajuste fino | Mucho dato, equilibrado | Sobreajuste si hay poco dato |
| Detección + clasificación | Animal pequeño o varios en la foto | Dos modelos que mantener |
| Multimodal cero disparos | Sin datos, prototipo rápido | Menos preciso que uno entrenado en la clase |

Las cifras exactas dependen de tus datos; mídelas con el paso 3 antes de prometer un número.

### Paso 5 · Despliegue según el dispositivo
- **Móvil**: modelo ligero, exportado a ONNX y cuantizado (fp16 o int8), medido en el dispositivo real.
- **Web**: modelo en el navegador si pesa poco; si no, servidor con cola.
- Muestra siempre las tres mejores opciones con su porcentaje y el aviso de límite.

## 7. Dudas abiertas
1. ¿"Iiner corners" significa esquinas interiores cóncavas como en la referencia, o bordes redondeados normales?
2. ¿La portada de prueba debe usar el lima como fondo, como acento sobre negro, o ambos?
3. ¿El artefacto de Claude (Notas Dot Grid) debe cambiar su paleta monocroma o solo añadir el lima como variante?
4. ¿Qué especies y región cubre el modelo? (define dataset y ejemplo de resultados)
5. ¿Las notas de otros compañeros son fuentes citables o solo referencia interna?

---

# PARTE 2 · Investigación añadida el 2026-10-15

Fuentes: notas de la investigación web en `andorid/research_notes/BioCLIP taxonomía e identificación visual/` (4 archivos, con URLs) y los datos de Anura en `anura-hallazgos.md` Parte B. Etiquetas: **[FUENTE]** verificado en un paper o ficha; **[CALC]** calculado; **[INF]** inferencia mía, sin fuente; **[SIM]** simulación (ver `anura-hallazgos.md` §14).

## 8. BioCLIP: qué es y cómo funciona

### 8.1 Qué es
- **BioCLIP** es un modelo de visión y lenguaje para el árbol de la vida, de Imageomics (Ohio State). Paper: *BioCLIP: A Vision Foundation Model for the Tree of Life*, CVPR 2024, arXiv 2311.18803. Licencia MIT, `imageomics/bioclip` en Hugging Face [FUENTE].
- Es **contrastivo imagen–texto**, como CLIP: aprende a acercar el vector de una foto al vector del texto que la describe. Parte de los pesos de OpenAI CLIP y sigue entrenando con datos biológicos [FUENTE].
- **BioCLIP 1:** torre de imagen ViT-B/16, entrada 224×224, **embedding de 512** dimensiones [FUENTE]. Datos: **TreeOfLife-10M**, ~10,4 millones de imágenes y 454.103 taxones, de iNaturalist (2,7 M), BIOSCAN-1M (1,1 M) y Encyclopedia of Life (6,6 M) [FUENTE].

### 8.2 La idea clave: el texto lleva el árbol taxonómico
Cada foto se empareja con un texto que puede ser nombre común, nombre científico o la **cadena taxonómica completa** (reino → filo → clase → orden → familia → género → especie), o mezclas. En cada paso se muestrea un formato por imagen («mixed»). En una ablación en Rare Species con 1 M de muestras: mixto 30,9; taxonómico + común 30,4; solo científico 22,3 [FUENTE].

**Qué se puede decir y qué no** (corrección al texto del usuario):
- Sí: las representaciones **reflejan la jerarquía** (los vectores de especies del mismo género quedan cerca) y por eso funciona en especies raras y no vistas. La evidencia del paper de que siguen la jerarquía es un t-SNE cualitativo, sin métrica [FUENTE].
- No: BioCLIP **no devuelve por sí solo** reino, familia, género y especie como salidas. En Anura, género y familia salen de los **supercentroides** y las cabezas jerárquicas que construyó el proyecto (hallazgos §4.3 y §7.1) [FUENTE + proyecto].
- La cadena completa tiene siete rangos: reino, filo, clase, orden, familia, género, especie; el texto original omitía filo, clase y orden.

### 8.3 Cifras (zero-shot, media de 10 tareas; BioCLIP 1 [FUENTE])
| Modelo | Media zero-shot | Rare Species | Birds 525 |
|---|---|---|---|
| CLIP | 21,9 | 31,8 | 49,9 |
| OpenCLIP | 20,4 | 29,8 | — |
| **BioCLIP 1** | **39,4** | **38,0** | **72,1** |

Few-shot (centroide más cercano, media): BioCLIP 1 → 50,3 (1 foto) y 68,8 (5 fotos); OpenCLIP 36,7 y 55,9; DINO 36,2 y 55,4. **Debilidades:** Plankton 6,1; PlantDoc apenas mejora (28,4 frente a 26,1). Una línea base solo con iNat21 saca 31,6: la ventaja real de los datos de TreeOfLife es de ~7,8 puntos, no los 17–20 sobre CLIP. Las cifras de la página del proyecto (CLIP 21,4; OpenCLIP 20,6) difieren de las del paper; se usan las del paper. Con el protocolo nuevo de las fichas de BioCLIP 2 y 2.5, BioCLIP 1 marca **37,6**: no son contradictorias, cambia el protocolo.

### 8.4 BioCLIP 1 frente a 2 y 2.5

| | BioCLIP 1 | BioCLIP 2 | BioCLIP 2.5 «Huge» |
|---|---|---|---|
| Torre de imagen | ViT-B/16 | ViT-L/14 | ViT-H/14 (init. CLIP LAION-2B) |
| Embedding | **512** | 768 | **1024** |
| Datos | TreeOfLife-10M (~10,4 M imágenes, 454 mil taxones) | TreeOfLife-200M (214 M imágenes, 952.257 taxones) + 26 M de LAION-2B | dato pendiente (la ficha no lo detalla) |
| Parámetros (modelo completo, archivo/4) [CALC] | ~150 M | ~428 M | ~986 M |
| Tamaño fp32 / fp16 [CALC] | 0,60 / 0,30 GB | 1,71 / 0,86 GB | 3,94 / 1,97 GB |
| Zero-shot, 10 tareas de especies | 37,6 | 55,6 | **61,3** |
| Zero-shot, 5 tareas amplias | 49,0 | 57,5 | 61,0 |
| Publicación | CVPR 2024 | NeurIPS 2025 (spotlight), arXiv 2505.23883 | Ficha en HF, repo creado 2026-02-10, sin paper propio encontrado |
| Licencia | MIT | — (dato pendiente) | MIT |

- **BioCLIP 2.5 sí existe** (`imageomics/bioclip-2.5-vith14`). La nota antigua del proyecto «BioCLIP 2.5 no existe» era falsa [FUENTE].
- Excepción: en Plankton BioCLIP 1 (6,1) supera a 2.5 (5,2) [FUENTE].
- BioCLIP 2 reporta que la **variación dentro de una especie** y la **separación entre especies** quedan en direcciones casi ortogonales en el espacio de vectores, y ambas mejoran con la escala. El paper lo da como tendencia en figuras, sin cifras, y los autores dicen no haber probado formalmente la separación [FUENTE].
- FLOPs, VRAM, tiempos de carga y soporte de `pybioclip` para 2.5: dato pendiente (ninguna fuente los da).

### 8.5 Corrección al texto del usuario sobre «512 frente a 1024»
Las dimensiones son correctas, pero **la mejora no se debe solo a las dimensiones**: viene de un modelo ~6,6 veces más grande (parámetros) y de ~20 veces más datos entre BioCLIP 1 y BioCLIP 2 [CALC]. Mejor decirlo así: «2.5 usa vectores de 1024 dimensiones, un ViT gigante y muchos más datos; los tres factores juntos explican la mejora». Y «la última versión» debe decir «la más reciente que encontramos (octubre de 2026)».

### 8.6 Cuándo usar cada uno
| Caso | Elegir | Razón |
|---|---|---|
| Móvil sin internet | **BioCLIP 1**, solo torre de imagen en ONNX fp16 (165,6 MB medidos en Anura) | Ligero; BioCLIP 2.5 en fp16 son ~2 GB [CALC] |
| Servidor con GPU | **BioCLIP 2.5** | Mayor precisión zero-shot; sin límite de tamaño |
| Compromiso | BioCLIP 2 | ViT-L/14 |
| Cualquier caso | Medir primero con tus fotos | Los benchmarks no son tus especies. Top-1 de Anura con 2.5: [SIM] 65,9–72,9 %; real: dato pendiente |

## 9. Otras opciones y con qué compararlo

| Modelo | Qué es | Cuándo usarlo | Límite |
|---|---|---|---|
| CLIP / OpenCLIP | Visión y lenguaje general | Base de partida o comparación | 21,9 y 20,4 de media frente a 39,4 de BioCLIP 1 [FUENTE] |
| DINO / DINOv2 | Visión autosupervisada | Vectores visuales sin texto | El paper de BioCLIP solo compara con DINO v1; DINOv2 y SigLIP: dato pendiente |
| BioTrove (BT-CLIP) | CLIP biológico con 161,9 M de imágenes y ~366,6 mil especies (arXiv 2406.17720); el modelo publicado es BT-CLIP, entrenado con un subconjunto de 40 M | Alternativa a BioCLIP | Comparación directa con BioCLIP: dato pendiente |
| SpeciesNet (Google) | >2.000 etiquetas, >65 M de imágenes, Apache-2.0, usa MegaDetector | Cámaras trampa | Cerrado a su catálogo |
| MegaDetector | Detecta animal, persona y vehículo; **no da especie** | Filtrar fotos vacías o localizar el animal | Detector, no clasificador |
| Pl@ntNet | Plantas; modelo propietario | Plantas | Imágenes devueltas por lo general CC BY-SA |
| Merlin (Photo ID/Sound ID) | Usa ubicación y fecha de eBird, funciona sin conexión | Referencia de diseño para paquetes regionales | Modelo cerrado |
| Perch 2.0 | Solo audio | Sonidos | No sirve para fotos |

## 10. Métodos que decidieron cosas

### 10.1 ¿Es un error el *transfer learning*?
Veredicto: **es un riesgo con mitigaciones, no un error**.
- Literatura [FUENTE, Kumar et al., arXiv 2202.10054]: el ajuste fino completo da ~2 % más en distribución pero ~7 % menos fuera de distribución que un clasificador lineal; **LP-FT** (primero la capa lineal, luego todo) supera al ajuste fino completo en ~1 % y ~10 % fuera de distribución. WiSE-FT suma 4–6 puntos bajo cambio de distribución (arXiv 2109.01903).
- En Anura: el ajuste fino de BioCLIP **no superó** a los vectores congelados (69,2 % frente a 70,4 %), memorizó (pérdida de train 0,92 → 0,01 con ~2.200 imágenes) y la Albumentations mal configurada lo hundió a 19,7 % (hallazgos §2, §5.1).
- «Que las especies parecidas dejen de distinguirse»: **no encontré una fuente que lo demuestre** [INF]. Lo respaldado es que, con pocas fotos por especie, el ajuste fino memoriza y pierde la estructura que BioCLIP ya traía.
- Reglas: empezar con vectores congelados + centroides o kNN; si hace falta, LP-FT con tasa de aprendizaje baja; evaluar en individuos y lugares distintos.
- Matiz del proyecto (por confirmar, hallazgos §15): una nota dice que el fine-tuning mejoraba el **rechazo** (FAR 75,7 frente a 84,2 %) sin mejorar el top-1.

### 10.2 Destilación del conocimiento (y por qué falló aquí)
- **Qué es:** un modelo pequeño («alumno») aprende a imitar las salidas de uno grande («maestro») [FUENTE, Hinton 2015].
- **Ejemplo seguro:** los modelos *DeepSeek-R1-Distill* son modelos Qwen2.5 y Llama ajustados con ~800 mil muestras generadas por R1 [FUENTE, ficha de HF].
- **No afirmar** que DeepSeek destiló a ChatGPT: es una **acusación** de OpenAI, que dijo haber visto indicios sin publicarlos [FUENTE]. Corrección al texto del usuario: usar el ejemplo de R1-Distill.
- **En Anura fracasó:** BioCLIP → MobileNetV3-S, 57,7 → **24,3 %** (−33,4 pp; objetivo <10), con 2.230 imágenes de entrenamiento y la rana en solo ~10 % del encuadre. Causas probables: el alumno aprendía «qué es una rana» y «cuál rana» a la vez; brecha de capacidad y de dominio. Sí se transfirió la coherencia taxonómica (79,7 frente a 83,4 %) (hallazgos §5.1). Las causas genéricas de fracaso (capacidad, pocos datos, dominio) son [INF].

### 10.3 De FP32 a FP16 (cómo se optimizó el encoder)
1. Extraer la **torre de imagen** de BioCLIP (se descarta la de texto).
2. Exportar con `torch.onnx.export` (dynamo), **opset 18, batch fijo = 1**, pesos en un solo archivo.
3. Convertir a **FP16** (en ONNX: `convert_float_to_float16` de `onnxconverter-common`; `keep_io_types` conserva entradas y salidas en fp32 [FUENTE, doc de ONNX Runtime]).
4. Validar: predicciones idénticas al original (64 imágenes, 100 %) y coseno 0,999999 entre embeddings.
5. Resultado: **165,6 MB** (la mitad del fp32); RAM ≈405 MB; **sin ganancia de velocidad** en CPU (el motor de CPU de ONNX Runtime no ejecuta operaciones fp16 de forma nativa y las pasa a fp32) [FUENTE + medido]. Qué hace en el Redmi: [SIM] ≈0,3–0,6 s con 4 hilos; real: dato pendiente.
- **Por qué no INT8:** los ViT tienen valores atípicos en las activaciones tras LayerNorm y tras softmax/GELU que una escala entera no representa (PTQ4ViT, arXiv 2111.12293; RepQ-ViT, arXiv 2212.08254) [FUENTE]. En Anura cinco intentos dieron 0,2–51 %.
- Preprocesado idéntico siempre: 224×224 RGB y media/desviación de `open_clip`. Contrato de embedding: `encoder_sha256` + dimensión + preprocesado + normalización.

### 10.4 Segmentación semántica y quitar el fondo: qué cifras hay
| Prueba | Resultado |
|---|---|
| BioCLIP sin entrenar, 848 imágenes: completa → recortada | 51,5 → 42,5 % (−9,1 pp Top-1; −9,2 pp Top-3) |
| 150 imágenes pareadas: completa → recorte → fondo negro | 60,7 → 50,7 → **44,7 %** (Top-3: 83,3 → 80,7 → 75,3 %) |
| Fase 4 con recorte + máscara, 41 especies | Top-1 especie 32,8 % frente a 41,9 % sin segmentar |
| Segmentador DeepLabV3+ResNet50 | IoU val 87,4 %, test 83,3 % (entrenado con 9 especies, usado en 41) |
| Tamaño de la rana en el encuadre | 6–18 % |
| Etapa I (segmentación + BioCLIP, 10 especies) | ~99 %: solo 10 especies; ablación nunca hecha |
- **Contexto de la literatura** [FUENTE, Xiao et al., arXiv 2006.09994]: los modelos extraen señal del fondo, y fondos adversariales rompen hasta el 87,5 % de los aciertos en primer plano. Que BioCLIP empeore con fondo negro encaja con un **cambio de dominio** (nunca vio fondos artificiales) [INF].
- **Lo que quedó:** la segmentación **explica después**, no decide. El clasificador ve la imagen completa. Experimento pendiente: reentrenar sobre recortes con fondo negro.

### 10.5 Caché de BioCLIP 2.5 (para no fallar en cada arranque)
Pedido del usuario: usar caché para que cada inicialización no tarde ni falle. Lo que hay:
- Recomendado [INF, sin verificar contra la documentación]: descargar una vez el modelo (≈3,9 GB en fp32) a una carpeta fija con `HF_HOME`; en producción usar `HF_HUB_OFFLINE=1` para que no consulte la red; **mantener el proceso cargado** (servidor «caliente»); precalcular y guardar los vectores de texto de las especies.
- **Dato pendiente:** el mensaje exacto del error que daba en cada inicialización y en qué máquina. Sin él no se puede decir que la caché lo resuelve.

## 11. Taxonomía y cómo se identifica lo vivo

### 11.1 Rangos
Dominio → reino → filo → clase → orden → familia → género → especie (se lee de lo general a lo particular).
| Rango | Rana | Planta |
|---|---|---|
| Reino | Animalia | Plantae |
| Filo | Chordata | Tracheophyta |
| Clase | Amphibia | Liliopsida |
| Orden | Anura | Poales |
| Familia | Bufonidae | Poaceae |
| Género | *Rhinella* | *Zea* |
| Especie | *Rhinella marina* | *Zea mays* |
(ejemplos del autor del documento, sin fuente web [INF/estándar])
- **Nombre binomial:** género + epíteto; el nombre se **cambia** (sinonimias, separaciones) y eso rompe datasets: en Anura, *D. labialis* = *D. molitor* contaminó una evaluación; *R. horribilis* se separó de *R. marina* en 2016 (Zootaxa 4103) [FUENTE]; *R. bella* se describió en 2024 [FUENTE]. En una leguminosa, un listado añadió 30.456 nombres a GBIF y 61.235 registros cambiaron de etiqueta [FUENTE].
- **Taxón:** cualquier grupo con nombre. **Clado:** grupo con un ancestro común y todos sus descendientes. **Complejo de especies:** grupo de especies casi iguales [definiciones estándar, INF].

### 11.2 Cómo identifican los expertos
- **Morfología y claves dicotómicas** (dos opciones por paso hasta el nombre), caracteres diagnósticos.
- **ADN (código de barras):** animales, gen COI de 648 pares de bases (Hebert 2003); plantas, rbcL + matK, a veces ITS2 [FUENTE].
- **Sonido:** cantos de ranas y aves (Xeno-canto, Merlin Sound ID).
- **Ciencia ciudadana:** iNaturalist «grado de investigación» exige ≥2 identificaciones y más de 2/3 de acuerdo; las fuentes discrepan sobre si el umbral es especie o género [FUENTE].
- **Cuándo la foto no basta:** especies crípticas, partes que no se ven (vientre translúcido), estadios distintos. Mostrar género o familia es mejor que adivinar.

### 11.3 Grupos taxonómicos y su ruta habitual
| Grupo | Ruta habitual | Pista de apoyo |
|---|---|---|
| Anfibios (anuros) | Foto de cuerpo entero + vientre; canto | Altitud, región, hora |
| Reptiles | Escamas, color, borde del cuello (papada) | Región, microhábitat |
| Aves | Foto + canto | Fecha y lugar (eBird) |
| Mamíferos | Cámaras trampa | Detector primero |
| Insectos | Foto + estadio (huevo, larva, pupa, adulto) | Planta hospedera |
| Plantas | Hoja, flor, fruto | Región, altitud |
| Hongos | Cuerpo fructífero; ADN | Sustrato (el uso de ITS no tiene fuente confirmada) |

### 11.4 Especies casi idénticas: los anuros (corrección del usuario: eran anuros, no *Anolis*)
- **Nota del usuario (corregida):** muchas especies de **anuros** se ven casi iguales aunque sean distintas, y por eso ciertos datos y factores favorecen mucho. **Respaldado.** Funk et al. 2012 («High levels of cryptic species diversity uncovered in Amazonian frogs», *Proc. R. Soc. B* 279:1806–1814): *Engystomops* pasa de 2 especies a 5–7 y *Hypsiboas* (hoy *Boana*) de 2 a 6–9. Fouquet et al. 2007 estima que la diversidad de anuros de Amazonia–Guayanas podría ser el doble de la reconocida [FUENTE]. *R. horribilis* se separó de *R. marina* en 2016 y *R. bella* se describió en 2024 con genética, morfología, canto y ecología [FUENTE]. En *Pristimantis* hay especies separadas por canto y por el gen 16S [FUENTE].
- **Conteo:** AmphibiaWeb lista 9.081 anfibios y 8.011 anuros, en 57 familias y 504 géneros (7 ago 2026) [FUENTE].
- **Qué datos desempatan** (cualquier grupo): localidad, altitud, canto, color de una estructura diagnóstica, comportamiento, hora, microhábitat. Los siguientes caracteres como separadores de anuros no tienen fuente confirmada: color oculto, iris, membranas [SIN FUENTE]. En Anura: *R. marina* y *R. horribilis* se solapan en altitud (25–2.500 m frente a 4,5–2.467 m), así que ni geografía ni altitud bastan (hallazgos §5.5).
- **Ejemplo en otro grupo (opcional):** los lagartos *Anolis* tienen casos crípticos documentados (*A. tropidogaster* frente a *A. gaigei*, separadas en parte por el color del abanico; *A. biporcatus* frente a *A. parvauritus*) y el abanico es diagnóstico solo para pares concretos [FUENTE]. El Reptile Database contaba 427 especies en 2018. Úsese solo si se quiere mostrar que el problema no es exclusivo de ranas.
- **No hay un recuento global de especies crípticas**: no citar un porcentaje.

## 12. Guía universal: contexto, plagas y plantas

### 12.1 El contexto como segunda vía
Cuando la imagen ya no alcanza (especies casi idénticas, foto mala), se suman variables para **reordenar** candidatas: lugar, altitud, fecha, hora, hábitat, canto, talla, planta hospedera. Reglas medidas en Anura:
- Fusión tardía sobre puntuaciones calibradas, nunca sumar porcentajes crudos.
- Prior **acotado**; la especie oficial sale del voto visual. Un prior sin acotar volteó una *D. bogerti* bien identificada.
- «No observable» ≠ «ausente» (tres estados).
- Cada prior nuevo se prueba también para ver si voltea una identificación visual de alta confianza.
- Base externa: iNaturalist «Expected Nearby» (modelo geográfico con ~80 mil taxones, se actualiza cada mes; hay informes de errores de baja autoridad) y los paquetes regionales de Merlin [FUENTE].

### 12.2 Casos de la guía
| Caso | Ruta |
|---|---|
| Estado de una **plaga** desde una foto | La plaga no «germina»: tiene **estadios** (huevo, larva, pupa, adulto) [estándar, INF]. «Germinación» aplica a semillas y a esporas de hongos, y su estado no se ve en una foto de campo. Pedir foto del estadio y de la hoja afectada |
| Foto de mala calidad | Cambiar de objetivo: analizar el **estado de la rama o la mata** (síntomas: manchas, mordeduras, marchitez). PlantVillage llega a 99,35 % en su test interno pero baja a **31,4 %** con imágenes web; otros cultivos bajan de 99,61 a 66,80 % (vid) y de 94,1 a 55,1 % (maíz) [FUENTE; cada cifra no revisada en su paper]. Pedir foto del síntoma sobre fondo real |
| ¿Qué planta ataca esta plaga en esta zona? | Usar bases de hospederos y distribución como **prior**: EPPO Global Database (~98.500 especies, >1.900 plagas reguladas, con hospederos y distribución), CABI Invasive Species Compendium, Plantwise (gratuita, con herramienta de diagnóstico por síntomas) [FUENTE]. No encontré fuente para usar Pl@ntNet o iNaturalist como herramienta de hospederos |
| Conjuntos de referencia | IP102 (75.222 imágenes, 102 clases de plagas); PlantDoc (2.598 imágenes); Pl@ntNet-300K (306.146 imágenes, 1.081 especies); PlantVillage (54.306) [FUENTE] |

### 12.3 Equilibrio: ni todo universal ni todo a mano (principio de diseño)
Afirmación del usuario: no se debe organizar todo de forma completamente universal porque puede arrastrar el resultado. **Respaldada** por Anura: los pesos cambian según el perfil de la especie (generalista 80/10/10, microendémica 30/60/10, par críptico 35/35/30, de quebrada 50/20/30) y no se aplica un único peso a todo (hallazgos §7.4). Diseño propuesto para la guía:
1. **Perfiles** de pesos editables (imagen / lugar / otros datos) en vez de un valor único.
2. Cada peso en tres valores visibles: **calculado, manual y efectivo**; el sistema nunca pisa el manual.
3. Los pesos son datos (tabla editable), no código; el prior es acotado.
4. Cada perfil se prueba con un conjunto propio y se reporta con sus condiciones.

### 12.4 Bases útiles para cualquier región
| Base | Qué aporta | Cifra [FUENTE] |
|---|---|---|
| GBIF | Registros de presencia | Totales actuales: dato pendiente |
| iNaturalist | Fotos y observaciones verificadas | Totales: dato pendiente |
| AmphibiaWeb | Anfibios | 9.081 especies (7 ago 2026) |
| Amphibian Species of the World | Taxonomía de anfibios | ~8.781 (versión de sep 2024) |
| Reptile Database | Reptiles | 427 *Anolis* (2018); total actual: dato pendiente |
| SiB Colombia | Biodiversidad de Colombia | >34 millones de registros |
| Xeno-canto | Sonidos | Totales: dato pendiente |

## 13. Verificación del texto que dictó el usuario

| Afirmación | Veredicto | Cómo queda |
|---|---|---|
| Anura nació para identificar anuros en Colombia; el modelo corría en móvil sin internet | Coherente con los documentos (requisito de modo sin conexión) | Se mantiene |
| «Extraer el visual encoder de BioCLIP y seguir todas las normativas» | Correcto en lo técnico (se exporta la torre de imagen). «Normativas» es vago | Se mantiene diciendo qué normas: contrato de embedding, preprocesado idéntico, validación de predicciones |
| BioCLIP identifica reino, familia, género y especie | **Parcial** | Se reformula (§8.2); faltan filo, clase y orden |
| BioCLIP 1 ligero pero deficiente; 512 frente a 1024 dims | Dimensiones correctas; la causa de la mejora **no son solo las dimensiones** | §8.5 |
| 2.5 es la última versión | Es la más reciente encontrada (repo de febrero de 2026) | Con fecha de consulta |
| Para servidor, usar 2.5 | Respaldado (~2 GB en fp16), sin medición propia en Anura | Con [SIM] y «dato pendiente» |
| El *transfer learning* puede ser un error | **Parcial** | Riesgo con mitigaciones (§10.1) |
| Destilación «como DeepSeek con ChatGPT» | **No respaldado como hecho** | Usar R1-Distill; la acusación a ChatGPT es una acusación (§10.2) |
| Destilación fracasó | Respaldado (57,7 → 24,3 %) | §10.2 |
| FP32 → FP16 | Respaldado | §10.3 |
| Caché para evitar el error en cada inicialización | Sin evidencia del error en los archivos | §10.5, dato pendiente |
| Los anuros (el usuario corrigió: no *Anolis*) tienen especies muy parecidas | **Respaldado** | §11.4 |
| Estado de **germinación de una plaga** | **Impreciso**: una plaga tiene estadios; «germinación» es de semillas y esporas | §12.2 |
| Foto mala → analizar la rama o la mata | Respaldado y es buena práctica | §12.2 |
| Qué planta ataca cada bicho según la zona | Respaldado por bases de hospederos (EPPO, CABI, Plantwise) | §12.2 |
| No hacerlo totalmente universal; que sea editable | Respaldado por Anura | §12.3 |

## 14. Qué falta para pasar al PDF (a la espera del usuario)
Ver §22 (lista actualizada).

---

# PARTE 3 · Auditoría y ampliación: especie, etapa, edad, sexo y enfermedad (2026-10-15)

Fuentes: `research_notes/Etapa edad sexo y enfermedades/` (anuros, vertebrados, plantas-insectos-hongos, diseño-método). Casi todas las cifras de esas notas salen de resúmenes de búsqueda y no de los PDF completos; se marcan **[RESUMEN]** cuando importa. **[SIN FUENTE]** = no encontré respaldo.

## 15. Auditoría: ¿alguien puede aplicar esta guía a cualquier especie?

**Veredicto honesto: hoy, solo en parte.**

| Pregunta que el lector quiere resolver | ¿La guía lo cubre? | Qué evidencia hay |
|---|---|---|
| ¿Qué especie es? (animal con foto) | **Sí**, es lo más sólido | Medido en 56 especies de anuros (top-1 62,85 %, top-3 86,1 %) y 28–41 en fases anteriores |
| ¿Qué género o familia, si la especie no se puede? | **Sí** | Supercentroides y cascada taxonómica medidos |
| ¿Qué especie es? (planta) | **Parcial** | Solo literatura (Pl@ntNet, PlantNet-300K); sin prueba propia |
| ¿En qué **etapa** está? | **Parcial** | Teoría y tablas por grupo (§17); sin dato propio de Anura |
| ¿Qué **edad** tiene? | **No desde una foto** (§17.3) | La guía lo dice con honestidad; la edad exige métodos de laboratorio o clases de edad |
| ¿Cuál es su **sexo**? | **Parcial** | Posible en algunos grupos y especies; imposible en otros (§17.2) |
| ¿Está **enferma**? | **Parcial y con límite fuerte** (§18) | La foto da pistas, no diagnóstico; casi no hay ML validado en campo |
| ¿Qué método uso para **mi** organismo? | **Se añade en §19** | Tabla organismo × pregunta |

Huecos que bajaban la aplicabilidad (se corrigen en esta Parte 3):
1. La Parte 1 hablaba casi solo de **especie**; faltaban etapa, edad, sexo y salud.
2. Los números medidos son todos de **anuros de Colombia**. Para otros grupos solo hay literatura; el lector debe saber qué es medido y qué no.
3. No había una **tabla de decisión** «mi organismo → mi pregunta → método».
4. Faltaba decir **qué hacer cuando la foto no basta** para cada pregunta.
5. Faltaba separar «puede inferirse de una foto» de «requiere laboratorio».
6. «Género» puede significar rango taxonómico o sexo; la guía tiene que distinguirlos (pregunta abierta §22).

## 16. Qué cambia con cada pregunta: el principio

Una foto responde cuatro familias de preguntas con **fiabilidad distinta**:
| Pregunta | Qué evidencia visual usa | Fiabilidad típica |
|---|---|---|
| Especie / género / familia | Forma, color, patrón | Alta si hay datos; baja en especies gemelas |
| Etapa de vida | Cambios de forma (larva → adulto), fenología | Media; depende del grupo |
| Sexo | Dimorfismo (tamaño, color, estructuras) | Solo si la especie lo tiene y es visible |
| Edad | Casi nada fiable en foto | Baja; se usan **clases de edad** (cría / joven / adulto) |
| Salud | Lesiones visibles | Pistas inespecíficas; **no es diagnóstico** |

Regla: **la guía debe devolver el nivel que la evidencia sostiene**, igual que con la taxonomía: «adulto, sexo no determinable», «signos compatibles con una enfermedad de la piel; requiere confirmación».

## 17. Etapa, sexo y edad por grupo

### 17.1 Etapa de vida
| Grupo | Etapas | Cómo se ve en foto |
|---|---|---|
| **Anuros** | Puesta → renacuajo (46 estadios de Gosner, 1960) → metamorfosis → juvenil → adulto | Renacuajos: difícil identificar la especie solo por morfología en el Neotrópico; se apoya en ADN (16S) comparando con adultos de la misma localidad. Más útil para etapa: estadios 26–38 [RESUMEN] |
| **Insectos** | Huevo, larva o ninfa, pupa, adulto (metamorfosis completa o incompleta) | La especie en larva suele ser difícil; el daño (agallas, minas, excrementos) a veces es la pista [SIN FUENTE] |
| **Plantas** | Escala **BBCH** (germinación → crecimiento → floración → fruto → senescencia) | Por órganos visibles; la lista 0–9 no se leyó en la monografía: verificarla en el PDF antes de citar |
| **Aves** | Pollo, juvenil, inmaduro, adulto; muda y plumaje | Plumaje por edad y sexo (muda; guía de Pyle) |
| **Mamíferos** | Cría, joven, adulto | Tamaño, astas, melena (en ML solo hay casos aislados) |
| **Peces** | Alevín, juvenil, adulto | Estadios de vida en foto: [SIN FUENTE] |

### 17.2 Sexo
- **Anuros:** las hembras son más grandes en la mayoría de especies (una fuente da ~10 % con machos más grandes y otra ~5 %: **discrepan**). Rasgos útiles en foto: saco vocal o garganta oscura, almohadillas nupciales, tímpano (solo algunas especies), amplexo. Todos dependen de la especie y de la época reproductiva. La lista de especies sin dimorfismo externo: [SIN FUENTE].
- **Aves:** ~60 % son monomórficas y solo se sexan por PCR del gen CHD [RESUMEN].
- **Mamíferos:** cérvidos desde cámara trampa: edad 90,77 % y sexo 96,15 % (ciervo rojo, un sitio, 4.352 recortes etiquetados por expertos) [RESUMEN]. **No generalizar** a otras especies ni otros sitios.
- **Reptiles:** en serpientes el sexo se determina por sondeo o eversión de hemipenes, **no** por foto.
- **Plantas:** algunas son dioicas (flores de un solo sexo); las fuentes encontradas son de baja calidad: citar solo el principio.

### 17.3 Edad
- **Anuros:** la edad **no se lee en una foto**. Lo estándar es contar líneas de crecimiento (LAGs) en falanges: funciona bien hasta ~8 años y subestima a los más viejos. La talla no es un proxy fiable [RESUMEN].
- **Plantas:** los anillos del tronco exigen una muestra.
- **Aves:** edad por muda y plumaje; en mano, osificación del cráneo.
- Lo que sí puede ofrecer una guía: **clase de edad** (cría, joven, adulto), con el aviso de que no es edad en años.

## 18. Enfermedad: fauna y flora

### 18.1 Principio
Una foto muestra **síntomas**, no **causa**. Un buen resultado dice: «lesión compatible con X, otras causas posibles Y, confirmar con Z».

### 18.2 Fauna
| Grupo | Signos visibles | Confirmación | ML publicado |
|---|---|---|---|
| **Anuros** | Letargo, muda anormal, enrojecimiento, hemorragia, edema. Son **inespecíficos**: se confunden entre quitridiomicosis (*Batrachochytrium dendrobatidis*, *B. salamandrivorans*), ranavirus y «pata roja» (*Aeromonas*). Malformaciones por el trematodo *Ribeiroia ondatrae* (no es la única causa) | qPCR, histología o cultivo | **Ninguno encontrado** para fotos de enfermedad o condición corporal de anfibios |
| **Aves** | Viruela aviar, conjuntivitis micoplásmica del pinzón doméstico, salmonelosis | Laboratorio | No evaluado aquí |
| **Mamíferos** | Sarna, síndrome de la nariz blanca en murciélagos | Enfermedad de desgaste crónico: solo post mortem | CNN para sarna en cámaras trampa: [SIN FUENTE] |
| **Peces** | Puntos blancos de ich | Microscopio | ~82–90 % en acuicultura [RESUMEN], conjuntos pequeños |
| **Ganado** | Dermatosis nodular contagiosa, fiebre aftosa (lesiones) | Veterinario / laboratorio | 89–99 % [RESUMEN], tesis y conjuntos pequeños, sin validación de campo |
| **Abejas** | Varroa, cría con loque, cría de tiza | Laboratorio | Varroa: F1 0,874 (abejas infestadas) y 0,714 (el ácaro) |

Obligación: algunas enfermedades de animales son de **notificación obligatoria** (lista de WOAH); la norma nacional no se encontró [SIN FUENTE].

### 18.3 Flora
- **Síntomas visibles:** manchas, clorosis, marchitez, roya, mildiu, deficiencia de nutrientes, daño de plagas.
- **El problema de la foto de laboratorio:** Mohanty 2016: **99,35 %** en el test del laboratorio y **31,4 %** con imágenes tomadas en otras condiciones (54.306 imágenes, 14 cultivos, 26 enfermedades).
- **Qué ayuda:** clasificar **lesiones individuales** subió la exactitud media un 12 % (Barbedo 2019; segmentación aún manual); varias fotos y varios órganos; contexto de lugar y cultivo.
- **PlantDoc:** BioCLIP 2 saca 40,4 ± 3,7 y BioCLIP 1 apenas mejora a CLIP (28,4 frente a 26,1): **los modelos de biodiversidad no sustituyen a uno de enfermedades de plantas**.
- **Plagas (insectos):** IP102 (75.222 imágenes, 102 clases): ResNet-50 con ajuste fino 49,4 % [RESUMEN]; trampas de luz F1 0,93 en validación y 0,71 de extremo a extremo.
- **Hongos:** la foto es **insegura para decidir si algo es comestible**: la mejor de tres apps acertó 49 % en 78 ejemplares y confundió *Amanita phalloides*; un centro de intoxicaciones belga reporta 44,4 % de tóxicos clasificados como no tóxicos o comestibles [RESUMEN]. Código de barras de ADN: región ITS (Schoch 2012). La germinación de esporas es una observación de laboratorio.
- **Confirmación:** PCR o cultivo; diagnóstico por extensionistas (Plantwise tiene una herramienta por síntomas; su base de conocimiento no se verificó).

### 18.4 Cuando la foto es mala (cascada propuesta [INF])
1. Pedir otra foto (otro ángulo, más cerca, con escala).
2. Pedir **otro órgano** (hoja, flor, fruto; vientre de la rana).
3. Cambiar de pregunta: de «qué plaga» a «**estado de la rama o de la planta**» (síntomas).
4. Añadir contexto (lugar, altitud, fecha, cultivo, planta hospedera).
5. Bajar de rango (especie → género → familia) o decir «no determinable».

## 19. Método por organismo y por pregunta

Leyenda: **F** = factible desde una foto; **P** = parcial (depende de especie o foto); **L** = requiere laboratorio; **—** = sin evidencia encontrada. Las celdas con juicio propio son [INF]; las demás tienen respaldo en las secciones anteriores.

| Organismo | Especie | Etapa | Sexo | Edad | Enfermedad | Método principal | Apoyo de contexto |
|---|---|---|---|---|---|---|---|
| Anuros | **F** (62,9 % top-1; 86,1 % top-3) | P (renacuajo: ADN) | P | **L** | P (pistas) / **L** | Embeddings + centroides, paquete regional | Lugar, altitud, canto |
| Aves | F | F | P (60 % monomórficas: **L**) | P (muda) | P | Foto + canto (Merlin) | Fecha y lugar (eBird) |
| Mamíferos | F (cámaras trampa) | P | P (ciervo: sí) | P | P (sarna) / **L** | MegaDetector → clasificador | Sitio |
| Reptiles | P | P | P / **L** (serpientes: sondeo) | **L** | — | Foto + ficha de caracteres | Localidad |
| Peces | P | — | — | — | P (ich) | Foto en acuario o cultivo | Hábitat |
| Insectos | P (adulto F; larva P) | F (huevo/larva/pupa/adulto) | P | — | — | Foto + planta hospedera | EPPO / CABI |
| Plantas | F (Pl@ntNet: varios órganos) | F (BBCH) | P | **L** | P (síntomas) / **L** | Foto de órganos | Región |
| Hongos | P | P | — | — | — | Foto + ADN (ITS) | Sustrato; **no usar para comestibilidad** |

**Cómo elegir el método (árbol):**
1. ¿Qué quieres saber? (especie, etapa, sexo, edad, salud).
2. ¿La respuesta es **visible**? Si no (edad, ADN, diagnóstico) → laboratorio o clase de edad.
3. ¿Cuántas clases y cuántas fotos? → ruta de §6b.
4. ¿La foto alcanza? Si no → cascada de §18.4.
5. ¿Hay especies gemelas? → documentar pares, usar contexto acotado y rebajar de rango.

## 20. Diseño recomendado para varias preguntas a la vez

- **Una sola base de vectores** (BioCLIP) y **cabezas ligeras** por pregunta: especie, etapa, sexo, salud. Respaldo: el resumen de BioCLIP 2 (arXiv 2505.23883) afirma que etapa y sexo se conservan en subespacios ortogonales a la especie; **no menciona salud** y no hay resultados zero-shot con prompts de atributos [RESUMEN]. Es una hipótesis razonable, no un resultado probado para Anura.
- **Zero-shot con texto** («foto de una rana macho adulta de X»): sin evidencia encontrada.
- **Abstención y calibración:** escalado de temperatura (Guo 2017), clasificación selectiva (Geifman y El-Yaniv 2017), línea base con la máxima probabilidad softmax (Hendrycks y Gimpel 2016), reconocimiento de conjunto abierto (Vaze 2021). SpeciesNet ya sube a taxón superior.
- **Cámaras trampa:** primero detector (MegaDetector detecta animal, persona y vehículo; la especie no) y después clasificador; el rendimiento cae en sitios nuevos (Beery 2018).
- **Segmentación de lesiones:** SAM y MedSAM existen, pero ningún estudio encontrado los evalúa en lesiones de plantas o animales.
- **Datos para etapa, sexo y salud:** solo dos ejemplos concretos publicados (ciervo rojo; PlantVillage). **Mínimo de imágenes por clase, acuerdo entre anotadores y manejo de enfermedades raras: [SIN FUENTE].** Hay que medirlos, igual que se hizo con la identificación de especie.
- **Evaluación:** separar por individuo y por sitio; reportar con condiciones; AUROC para rechazo; calibración (ECE).

## 21. Límites y responsabilidad
- **No es un diagnóstico.** Enfermedad, edad y sexo dudosos se devuelven como «compatible con…».
- **Hongos comestibles:** no usar una foto para decidir qué se come.
- **Especies amenazadas:** ocultar coordenadas (iNaturalist lo hace con taxones amenazados).
- **Enfermedades de notificación obligatoria:** avisar a la autoridad (lista de WOAH; norma nacional: dato pendiente).
- **Datos sensibles:** observaciones privadas solo en el servidor del usuario.

## 22. Qué falta para pasar al PDF
Sustituido por §34 (lista vigente tras las respuestas del usuario del 2026-10-15).

## 23. Tabla de contenido propuesta del PDF (borrador v1; la definitiva está en §33)

> Pendiente de la autorización del usuario. Cada sección enlaza a su apartado de este md.

| # | Sección | Fuente en el md | Hoja |
|---|---|---|---|
| 0 | Portada · «Guía de IA: cómo hacer que un modelo distinga animales» | §5 | Negra · apertura |
| 1 | Cómo leer esta guía y qué puedes aplicar | §15 | Normal |
| 2 | Qué se puede preguntar a una foto (especie, etapa, sexo, edad, salud) | §16 | Verde |
| 3 | Taxonomía: rangos y cómo se identifica lo vivo | §11 | Normal |
| 4 | BioCLIP 1, 2 y 2.5: qué son y cuándo usar cada uno | §8, §9 | Negra · apertura |
| 5 | Ruta de método (paso 0 a 5) | §6b | Normal |
| 6 | Datos: cuántos, de dónde, cómo separarlos | §1.3, Parte A §6 de los hallazgos | Tablero |
| 7 | Resultados de un caso real: anuros de Colombia | hallazgos Parte B | Tablero |
| 8 | Errores y lecciones | hallazgos §1, §5 | Normal |
| 9 | Quitar el fondo, destilar y cuantizar: qué falló | §10 | Verde |
| 10 | El contexto: lugar, altitud, fecha, hospedero | §12 | Normal |
| 11 | Especies casi idénticas y qué datos las separan | §11.4 | Verde |
| 12 | Etapa, sexo y edad por grupo | §17 | Normal |
| 13 | Enfermedad en fauna y flora | §18 | Normal |
| 14 | Método por organismo y pregunta (tabla de decisión) | §19 | Tablero |
| 15 | Diseño multi-pregunta, abstención y calibración | §20 | Normal |
| 16 | Despliegue en móvil y en servidor (FP16, caché, ONNX) | §10.3, §10.5 | Normal |
| 17 | Límites, ética y notificación | §21 | Verde |
| 18 | Glosario, fuentes y créditos | todo | Normal |

---

# PARTE 4 · Decisiones del usuario y caso conductor (2026-10-15)

Lectores: **estudiantes que quieren construir otro modelo, para insectos del género *Frankliniella*** (el usuario escribió «franquinela»: se interpreta como *Frankliniella*, los trips; confirmar), con el fin de **reconocer en qué etapa de vida está el insecto en una foto y recomendar el remedio adecuado**. La guía no diseña su modelo: les da todos los conceptos y todas las opciones. Fuentes: `research_notes/Frankliniella etiquetas y prior dinámico/` (3 archivos), el código de Anura y el md `Estrategia de Construcción del Dataset`. Etiquetas igual que en la Parte 2.

## 24. El rango taxonómico es una decisión de alcance

**Idea del usuario:** el grupo que se quiere evaluar debe poder separarse **fácilmente** de los vecinos. Ejemplo: los anuros son fáciles de diferenciar del resto de anfibios porque **no tienen cola** (el nombre *Anura* significa «sin cola»).
- **Regla:** al empezar, elige un rango (orden, familia, género) cuyo límite con los vecinos sea visible y estable. Lo fácil (rana frente a no-rana) se resuelve con un umbral; lo difícil (especie frente a especie del mismo género) se resuelve con datos y contexto.
- **Evidencia medida en Anura:** «no es una rana» frente a «rana» se separa casi perfecto (AUROC 0,987–0,992), mientras que una rana frente a otra rana no (AUROC 0,665 en Sinú). Los falsos positivos de «no-rana» fueron los vecinos más parecidos: reptiles 23 % y salamandras 15 % (hallazgos §13.2).
- **Cuidado: el rasgo diagnóstico depende de la etapa.** Los renacuajos **sí** tienen cola. «Sin cola» vale solo para el adulto. Por eso etapa y rango taxonómico no se resuelven por separado (§26).
- **Para un grupo nuevo:** escribir la lista de rasgos que lo separan de sus vecinos más parecidos y comprobar que se ven en foto. En trips: el orden Thysanoptera se reconoce por alas con flecos y tamaño menor de 2 mm [INF, estándar]; la especie *no* se reconoce en foto (§32).

## 26. Una especie no es una sola apariencia: especie × etapa × sexo

**Idea del usuario:** un individuo tiene un rango taxonómico, pero también **una etapa de crecimiento y un sexo**, y ambos **cambian su apariencia**. Hay que tenerlo en cuenta.

- **Efecto en el modelo:** una sola etiqueta «especie» mezcla apariencias muy distintas (renacuajo y adulto; macho y hembra; larva y adulto). Un solo prototipo («centroide») por especie queda en el medio y no representa a ninguna. Anura ya aplica esta idea con los **morfos**: no se promedian morfos opuestos (*Oophaga histrionica*) y cada morfo con ≥3 individuos tiene centroide propio (hallazgos §7.1 y §13.4); sin medición todavía.
- **Respaldo:** BioCLIP 2 reporta que la variación dentro de una especie (etapas, sexos) se conserva en el espacio de vectores y queda separada de la variación entre especies. Usaron NeWT para etapa y NABirds para sexo; los valores exactos están en figuras que no se revisaron, y los autores dicen que la ortogonalidad no está probada de forma formal [FUENTE, resumen].
- **Esquema de etiqueta recomendado** (cada foto lleva todos los campos):

| Campo | Valores | Si no se puede saber |
|---|---|---|
| Taxón | familia / género / especie (el más fino que se confirme) | `no_determinable` + rango alcanzado |
| Etapa | las del grupo (huevo, larva I, larva II, prepupa, pupa, adulto; renacuajo, juvenil, adulto; BBCH en plantas) | `no_determinable` |
| Sexo | macho / hembra / indiferenciado | `no_determinable` (la regla de Anura) |
| Morfo | variante declarada por un experto | vacío |
| Salud | sano / síntoma observado (texto) / `no_determinable` | `no_determinable` |
| Calidad | nítida / borrosa / parcial / escala visible (sí/no) | — |
| Individuo, sitio, fecha, observador | identificadores | — |

- **Cómo modelarlo (opciones, de simple a complejo):** (1) una etiqueta compuesta «especie-etapa» como clase; (2) un vector común y **cabezas separadas** por pregunta (taxón, etapa, sexo); (3) prototipos por subclase (especie × etapa × sexo) con préstamo del global si hay <3 individuos, como hace Anura. Elegir según cuántas fotos haya por celda.
- **División de datos:** por individuo y por sitio, y comprobar que cada etapa aparece en train, val y test.

## 27. Etiquetar bien es lo más importante

- **Cifras de la literatura:** al menos 3,3 % de errores de etiqueta de media en 10 conjuntos de prueba y al menos 6 % en el conjunto de validación de ImageNet (Northcutt et al. 2021); *confident learning* (cleanlab, código abierto) estima las etiquetas sospechosas [FUENTE]. En iNaturalist, un post informal de su personal (2019) estimaba ~85 % de «grado de investigación» correcto, 91 % en aves y 65 % en insectos, con problemas metodológicos que el propio autor señala [FUENTE débil, resumen de búsqueda]: **en insectos las etiquetas públicas son las menos fiables**.
- **Errores reales de Anura** (hallazgos §5.4 y §6.5): siete correcciones de nomenclatura; carpetas con errores de tipeo; *D. labialis* = *D. molitor* (79,1 % de la misma observación) que contaminó una evaluación; el `individual_id` era el `observation_id` de iNaturalist y no un animal verificado; la búsqueda de «negativos difíciles» elige una y otra vez el error cuando hay etiquetas sucias.
- **Protocolo mínimo:**
  1. Guía de anotación escrita, con ejemplos de cada valor y cada `no_determinable`.
  2. Regla: ante la duda entre marcar algo y `no_determinable`, gana `no_determinable`; ante desacuerdo en escala ordinal, el valor más conservador (regla de Anura).
  3. Dos anotadores sobre una muestra y medir el acuerdo (kappa de Cohen: procedimiento estándar, sin fuente verificada aquí).
  4. Experto para la etiqueta de especie (en trips, identificación en microscopio, §32).
  5. Versionar la taxonomía y guardar sinónimos (los cambios de nombre rompen datasets).
  6. Detectar duplicados por hash (pHash/dHash) **y** por observación.
  7. Revisar con cleanlab o similar los casos con mayor pérdida antes de reentrenar.
  8. Congelar test antes de mirar resultados.
- **Qué pasa si no se hace:** métricas infladas (Fase 13: 100 % de los KNOWN dentro de TRAIN) o modelos que aprenden el error.

## 28. Fine-tuning frente a encoder congelado: análisis y conclusión

### 28.1 Cómo funciona y qué efectos tiene
| Opción | Qué se entrena | Efecto típico |
|---|---|---|
| Sin entrenar (zero-shot) | Nada | Línea base; BioCLIP 1: media 39,4 en 10 tareas |
| **Vectores congelados + centroides o kNN** (SimpleShot) | Solo se calculan medias | Es el protocolo few-shot de BioCLIP: Rare Species 1-shot 44,9 (CLIP 28,5), 5-shot 65,7 (CLIP 46,0) [FUENTE] |
| Linear probe (capa lineal) | Una capa | En 101 especies de polillas, el linear probe sobre BioCLIP 2 congelado fue lo mejor con pocos datos: 88,3 % sin datos del objetivo y 91,6 % con 50 % (arXiv 2508.20089) [FUENTE]; no probaron fine-tuning completo |
| Ajuste fino completo | Todos los pesos | ~2 % más dentro de distribución, ~7 % menos fuera, frente al linear probe (Kumar et al. 2022, 10 conjuntos). Mecanismo: las capas bajas se mueven mientras se aprende una cabeza inicializada al azar y eso distorsiona las características [FUENTE] |
| LP-FT (primero lineal, luego todo) | Todo, con mejor inicio | ~1 % más dentro y ~10 % más fuera que el fine-tuning completo [FUENTE] |
| WiSE-FT (promediar pesos original y ajustado) | Sin costo extra | +4–6 pp bajo cambio de distribución (resumen; otras fuentes dan cifras distintas) [FUENTE] |
| LoRA/adaptadores | Pocas matrices | «Aprende menos y olvida menos»: resultado de modelos de lenguaje, no de CLIP [FUENTE, otro dominio] |

Otros efectos: el olvido de lo preentrenado en modelos tipo CLIP depende del modelo (degradación fuera de distribución solo en los entrenados con LAION-2B y OpenAI, arXiv 2410.21582) [FUENTE]; con pocas fotos por clase el ajuste fino memoriza; en especies casi idénticas el riesgo es que el modelo aprenda el fondo o la sesión de fotos en lugar del rasgo [INF].

### 28.2 Qué pasó en Anura
- Ajuste fino de BioCLIP 1 con 28 especies: test 69,2 % frente a 70,4 % de la línea base **sin entrenar**; pérdida de train 0,92 → 0,01 con 28,7 M parámetros descongelados y ~2.200 imágenes: memorizó. Con la configuración de Albumentations mal normalizada cayó a 19,7 % (hallazgos §5.1).
- Una nota de septiembre indicaba que el modelo con fine-tuning **rechazaba mejor** (FAR 75,7 frente a 84,2 %). El usuario ha decidido **congelado**; esa nota queda como dato histórico por actualizar.
- Cambiar el encoder obliga a **recalcular todos los vectores**, redistribuir el ONNX (>100 MB) y rehacer los paquetes: los vectores viejos dejan de ser comparables (contrato de embedding: hash del encoder, dimensión, preprocesado, normalización) [proyecto + INF].

### 28.3 Conclusión
**Usar BioCLIP 1 congelado por defecto, y solo ajustar si se demuestra la necesidad.** Razones:
1. La medición propia dice que el ajuste no mejora el top-1 y memoriza.
2. La literatura lo respalda (peor fuera de distribución con ajuste completo) y los autores de BioCLIP evalúan sin ajuste.
3. **Añadir una especie o una etapa nueva = calcular un vector**, sin reentrenar; los paquetes regionales y las versiones inmutables dependen de que el encoder no cambie.
4. Es más barato, determinista y reproducible (no necesita GPU para mantenerlo).

Si aun así hace falta ajustar (muchas fotos por clase, línea base insuficiente): primero **linear probe**, luego **LP-FT** con tasa de aprendizaje baja, o **WiSE-FT**; validar fuera de distribución (sitios y localidades nuevos); **recalcular todos los vectores y versionar**; mantener el encoder anterior hasta comprobar. Regla del §6b: ajuste fino completo solo con >500 imágenes por clase y buen equilibrio.

## 29. Contexto dinámico: el prior geográfico y los demás datos

**Decisión del usuario:** el prior geográfico y todos los datos de contexto deben ser **dinámicos**, para no generalizar una ubicación específica: hay especies **endémicas** y otras presentes en muchos lugares con características distintas.

### 29.1 Qué dice la literatura
- **Prior geográfico presencia-solo** (Mac Aodha et al. 2019, texto completo leído): la fusión es P(clase | imagen, lugar) ∝ P(clase | imagen) · P(clase | lugar) (supone independencia condicional). Top-1 sin prior → con prior: iNat2018 60,20 → **72,68**; iNat2017 63,27 → 69,60; BirdSnap 70,07 → 79,58. Con un conjunto sin estructura geográfica (YFCC) **no ayuda** [FUENTE].
- **SINR** (Cole et al. 2023): una red aprende un mapa por especie con coordenadas; con 10 ejemplos por especie ya supera a la cuadrícula con todos los datos; las coordenadas solas dan el 93–97 % de lo que dan coordenadas + variables ambientales. Limitaciones declaradas: ubicaciones ofuscadas, datos desbalanceados, no calibrado ni validado para conservación [FUENTE].
- **iNaturalist «Expected Nearby»:** muestra las especies visualmente parecidas y esperadas cerca; si ninguna lo está, muestra todas [FUENTE]. **Merlin** usa observaciones de eBird (resumen) [FUENTE débil].
- **Ningún método publicado trata endémicas y amplias con un parámetro explícito**: la escala por especie sale implícita del modelo [FUENTE, nota del investigador]. El diseño de abajo es propuesta propia.
- Los mapas de rango tienen errores de comisión y omisión; un estudio con cámaras trampa (510 especies) detectó solo el 39 % de las especies esperadas por rangos IUCN (resumen) [FUENTE débil].

### 29.2 Diseño dinámico recomendado [propuesta propia, apoyada en Anura]
1. **Escala por especie, calculada de los datos** (nunca fija): la dispersión de sus observaciones (rango de distancias y de altitud) define cuánto se «ensancha» el prior. Endémica = poca dispersión: prior estrecho y fuerte. Amplia = mucha dispersión: prior ancho y débil.
2. **Perfiles de peso editables** por especie (Anura: generalista 80/10/10, σ altitud 1000 m; microendémica 30/60/10, σ 120 m; par críptico 35/35/30; de quebrada 50/20/30) (hallazgos §7.4). Los cortes entre perfiles se toman como **terciles de los propios datos**, no como umbrales fijos.
3. **Suavizado hacia lo uniforme** cuando hay pocas observaciones (Laplace/α, como en Anura: P(s|z) = (N+α)/(N(z)+α·K)).
4. **Prior acotado:** multiplicador entre 0,5 y 1,5 (o solo reordena alternativas); **nunca elimina** una especie; la oficial sale del voto visual (incidente *D. bogerti*).
5. **«No observado» ≠ «ausente»**; tipo de tres estados.
6. **Recalcular en cada versión** del dataset; guardar los pesos como tabla editable con tres valores (calculado, manual, efectivo).
7. **Sesgos a vigilar:** donde hay más observadores hay más registros (ciudades, carreteras); coordenadas imprecisas (en Anura se descartaron observaciones con hasta 7.270 km de imprecisión); especies invasoras o que cambian de rango (*R. marina*, *Frankliniella*); coordenadas de especies amenazadas ofuscadas.
8. **Evaluar** el prior por distancia (sitios aislados: +15,3 pp frente a +24,9 pp en el test completo en Anura), sin usar la especie real como entrada (oráculo) y comprobando que no voltea identificaciones visuales correctas.
- **Otros datos de contexto** que siguen la misma regla: fecha y época (fenología), altitud, clima, hora, hábitat, **planta hospedera o cultivo**, y la presencia de otras especies.

### 29.3 Contexto como cadena causal (la teoría del usuario sobre plagas y enfermedades)
Los insectos pueden **traer enfermedades a la planta**. Se usa como pista contextual: «insecto vector + síntomas de la planta ⇒ más probable la enfermedad que transmite». Ejemplo respaldado: los trips *Frankliniella occidentalis* transmiten el virus del bronceado del tomate (TSWV) y el virus de la mancha necrótica de la impatiens; **solo las larvas adquieren el virus y los adultos lo transmiten**; el adulto que lo adquiere ya de adulto no lo transmite; *F. occidentalis* es el vector más eficaz, *F. fusca* menos y *F. tritici* no es vector; el trips es infectante 3–10 días después de adquirirlo [FUENTE, EPPO y Univ. de Maryland]. **La etapa importa para el riesgo**, no solo para el remedio. El peso de esta pista debe ser acotado y editable, como los demás.

## 30. Pocas imágenes: aumentación y alternativas (lo que ya se hizo y lo que se puede hacer)

### 30.1 Lo registrado en código, md y landing page de Anura
| Dónde | Qué dice | Nota |
|---|---|---|
| `bioclip/scripts/fase_4_transfer_learning.py` (clasificación, torchvision) | **Moderada** (individuos reales): RandomResizedCrop 224 escala 0,6–1,0; volteo horizontal p=0,5 y vertical p=0,3; rotación ±20°; ColorJitter brillo y contraste 0,25, saturación 0,15, **matiz 0,05**; RandomAffine ±15°, traslación 0,1, escala 0,85–1,15; desenfoque gaussiano suave; RandomErasing p=0,2 (2–10 % del área). **Agresiva** (solo repeticiones de especies con <70 individuos, marcadas `aumentada: true`): escala 0,4–1,0, vertical p=0,4, rotación ±30°, brillo/contraste 0,35, saturación 0,25, matiz 0,05 (igual), traslación 0,15, escala 0,75–1,25, RandomErasing p=0,35 (2–20 %) | Val y test sin aumentación. Mismas reglas en `entrenador-gpu/…/datos.py` |
| `Estrategia de Construcción del Dataset.md` | Permitidas: HorizontalFlip, VerticalFlip, RandomRotate90, ShiftScaleRotate (límite 20 %), ElasticTransform, GridDistortion, RandomBrightnessContrast ±30 %, RandomShadow, HueSaturationValue (**matiz ±10**, saturación y valor ±20), CLAHE (clip 4,0). **Prohibidas:** HueShift >15 (el color es el carácter diagnóstico en dendrobátidos), deformaciones que alteren proporciones del cuerpo, inversión de espectrogramas y cambios extremos de tono en audio | Audio: TimeShift, ruido suave (SNR ≥15 dB), SpecAugment |
| Mismo md y landing page (`D:\server\Anura\LANDING PAGE`) | Tabla de Albumentations: geometría (flips, Rotate90, ShiftScaleRotate 0,2, ElasticTransform, GridDistortion p=0,2, Perspective p=0,3); color y calidad (BrightnessContrast 0,3, RandomShadow, HueSaturationValue 10/20/20, RGBShift 15, CLAHE, GaussianBlur, GaussNoise, ImageCompression 60–100, CoarseDropout 8 huecos de 32 px); **CutMix y CoarseDropout** para ejemplos difíciles y oclusiones | **Documentadas para el modelo de segmentación** (imagen y máscara sincronizadas). Planificado: 550 originales de train → 5.100–6.000 con aumentación; 120 en val y 120 en test sin aumentar [DOC] |
| Reglas de proceso (md) | Aumentación **solo en train y al vuelo**, nunca antes de dividir; todas las tomas de un mismo individuo o sitio en el mismo grupo; estadísticas de normalización solo con train; oversampling de especies raras con aumentación controlada; incluir fondos variados para evitar que la red asocie especie con fondo (*shortcut learning*) | Conclusión de la prueba: Albumentations mal normalizado hundió el modelo de identificación a 19,7 %; se volvió a torchvision (69,2 %) |
| Pérdida (código) | Ponderación **amortiguada (raíz cuadrada)** en vez de frecuencia inversa, porque multiplicar ×6 el gradiente de una clase de 11 individuos fuerza a memorizar | hallazgos §4.3 |

**Discrepancia a recordar:** el md y la landing hablan de Albumentations; el código de **identificación** usa torchvision. Para el estudiante: la herramienta importa menos que **comprobar la normalización** y **probar la aumentación sola** antes de entrenar.

### 30.2 Escalera si no hay suficientes imágenes (de lo más barato a lo más costoso)
| Si tienes… | Usa… | Evidencia / precaución |
|---|---|---|
| Muy pocas fotos por clase (1–10) | Vectores congelados + centroide o kNN (SimpleShot); zero-shot como línea base | BioCLIP 1: media 1-shot 50,3 y 5-shot 68,8 (10 tareas) |
| Algunas fotos (10–70) | Lo anterior + **aumentación moderada** del §30.1 | Solo train, al vuelo |
| Clases desbalanceadas | **Oversampling** con aumentación agresiva solo en las repeticiones; pesos de clase amortiguados (raíz cuadrada) | Anura: umbral de 70 individuos |
| Se necesitan más variantes difíciles | CutMix, CoarseDropout/RandomErasing, copy-paste | CutMix y Copy-Paste tienen fuente; en objetos pequeños no se halló desglose; Anura prohíbe mezclar con CutMix entre especies del mismo género |
| Se necesitan más fotos de verdad | Fuentes públicas: iNaturalist, GBIF, EOL; luego fotos propias con protocolo | En insectos las etiquetas públicas son las menos fiables (§27); las **etapas** casi nunca están etiquetadas: hay que etiquetarlas |
| Faltan etapas difíciles de fotografiar (huevos en tejido, pupas en suelo) | Fotos propias dirigidas (macro, escala visible) o **fusionar clases** (larva I y II; prepupa y pupa) y reportar a ese nivel | Rollup jerárquico: mejor «pupa o prepupa» que adivinar |
| Hay fotos sin etiqueta | Etiquetado asistido: el modelo propone, un experto confirma (aprendizaje activo); pseudo-etiquetas solo con umbral alto | [INF, práctica estándar; no verificada en las notas] |
| Nada de lo anterior alcanza | **Imágenes sintéticas** (difusión) como último recurso | Stable Diffusion se clasificó bien solo ~14 % sobre 50 clases de iNaturalist (26 % con su método): evidencia débil; nunca en val ni test |
| Al predecir | Aumentación en prueba (promediar varias versiones) y **varias fotos del mismo individuo** | [INF] |
| Siempre | Reportar con condiciones (n por clase, split, versión) | Tabla de §2 de los hallazgos |

### 30.3 Qué NO romper al aumentar (según el tipo de pista)
- **Color diagnóstico:** matiz ≤ ±10 a 15° (regla de Anura). En trips el color de la larva y el adulto (amarillento, marrón) puede ser parte de la pista de etapa [INF].
- **Tamaño y proporciones:** si la etapa se distingue por tamaño o proporción del cuerpo, evitar zoom y deformaciones fuertes, o mantener una escala visible en la foto [INF].
- **Rotación y volteo:** válidos para insectos vistos desde arriba; no cambian la etapa [INF].
- **Fondo:** incluir fondos variados (hoja, trampa pegajosa, mano) para que no aprenda el fondo.

## 31. Del animal a la flora: qué se traslada y qué cambia

La guía es de animales; si hace falta, la **teoría** se aplica a plantas con esta tabla (y la ruta §6b es la misma):
| Concepto en animales | En flora | Particularidad |
|---|---|---|
| Rango taxonómico fácil de separar | Familia o género con rasgo visible (hoja, flor) | Las claves botánicas usan flor y fruto; **varios órganos** ayudan |
| Etapa (renacuajo, larva, adulto) | **BBCH**: germinación, crecimiento, floración, fruto, senescencia | Verificar la lista 0–9 en la monografía antes de citarla |
| Sexo | Flores masculinas, femeninas o hermafroditas; plantas dioicas | Fuentes de baja calidad: solo el principio |
| Edad | Anillos (requiere muestra) | No sale de una foto |
| Salud | Síntomas en hoja, rama o planta (manchas, clorosis, marchitez, roya, mildiu, deficiencias) | Modelo de laboratorio 99,35 % → 31,4 % en campo |
| Foto mala → pedir otra | Pedir **otro órgano** o cambiar a «estado de la rama o la mata» | Cascada §18.4 |
| Prior de lugar | Región, altitud y **cultivo / hospedero** | EPPO, CABI, Plantwise |
| Plaga como contexto | Insecto vector → enfermedad (§29.3) | Un insecto en la planta eleva la sospecha de lo que transmite |
| Pocas imágenes | Mismos métodos (§30.2) | PlantNet-300K y PlantVillage como fuente de datos |
Para plantas, los modelos de biodiversidad ayudan menos que uno de enfermedades: BioCLIP 2 saca 40,4 ± 3,7 en PlantDoc.

## 32. Caso conductor: *Frankliniella* (trips) y su etapa de vida

> Contexto para los estudiantes, no un diseño. Todo con fuente salvo lo marcado.

### 32.1 Ciclo y qué se ve
| Etapa | Duración a 27 °C (UF/IFAS, repollo) | Dónde está | ¿Se ve en foto? |
|---|---|---|---|
| Huevo | ~3,1 días | **Dentro del tejido vegetal**; ~200 µm (EPPO) | Casi nunca; solo por el daño local |
| Larva I | ~1,8 días | En la planta (hojas, flores) | Sí, con macro |
| Larva II | ~2,4 días | En la planta | Sí, con macro |
| Prepupa | ~1,0 día | Suelo u hojarasca; no se alimenta | Difícil |
| Pupa | ~2,0 días | Suelo u hojarasca; no se alimenta | Difícil |
| Adulto | — | Flores y hojas; **<2 mm** | Sí, con macro |
Huevo a adulto: **10,2 días** a 27 °C; huevo a huevo: 44,1; 22,4; 18,2 y 15 días a 15, 20, 25 y 30 °C (EPPO). Los tamaños de larva, prepupa y pupa en mm: **dato pendiente** [SIN FUENTE]. EPPO llama «estadios larvales» también a prepupa y pupa: es solo terminología.
- **Datos esperables [INF a partir de lo anterior]:** habrá muchas fotos de adultos y pocas de huevo, prepupa y pupa (ocultos). Es un caso claro de clases escasas y desbalanceadas (§30.2).

### 32.2 Identificación
- **Especie:** requiere **adultos montados en lámina al microscopio** (setas del pronoto y ocelar III, sensilas del metanoto, peine del tergito VIII); los caracteres de las setas varían dentro de una especie. **No se encontró ninguna fuente que identifique la especie por foto**. UF dice que larvas, prepupas y pupas «normalmente no se identifican».
- **Consecuencia para la guía:** el rango alcanzable por foto es **género o grupo («trips»)**; la especie debe etiquetarse con confirmación de laboratorio, y el modelo de etapa debe ser **independiente de la especie** (primero etapa, luego género).
- **Sexo:** hembras más grandes que machos; haplodiploidía y proporciones: [SIN FUENTE].
- **Visión por computador existente:** solo trampas pegajosas amarillas para especie (Laekeman et al. 2025: 5.105 parches y 4.000 etiquetas; mAP@50 ≥90 % en el test interno y 79–89 % en el externo). **No hay trabajos ni conjunto público de etapas** encontrados: los estudiantes tendrán que crearlo.
- **Cómo fotografiar [INF]:** lente macro, escala visible (regla milimétrica), fondo neutro, luz uniforme; trampa azul o amarilla para adultos.

### 32.3 Etapa → remedio (principios, no dosis)
- La etapa decide **qué control llega**: los huevos están dentro del tejido y la prepupa y la pupa en el suelo, así que un tratamiento foliar no los alcanza [INF a partir de la biología, parcialmente en EPPO y UF]; larvas y adultos están expuestos.
- Opciones habituales (resúmenes, fuentes secundarias): control cultural, biológico (ácaros depredadores *Amblyseius*, chinche *Orius*, hongos entomopatógenos *Beauveria* y *Metarhizium*, nematodos contra pupas del suelo) y químico, **con resistencia a insecticidas documentada en *F. occidentalis*** (lista de 2001, resumen).
- En cultivos de exportación colombianos el umbral de trips es **0** por reglas de cuarentena; no se halló estudio que relacione capturas en trampa con infestación de la planta (Silva-Castaño y Brochero 2021).
- **Siempre:** consultar al agrónomo y la norma local (ICA, Colombia; norma específica de *F. occidentalis*: dato pendiente). Esta guía no receta.

### 32.4 Dónde es plaga en Colombia
*F. occidentalis* domina en la Sabana de Bogotá (crisantemo), Medellín (crisantemo, aster), Piendamó (crisantemo) y La Ceja (bouvardia); la rosa es hospedero documentado. *F. fusca*, *F. tritici*, *F. schultzei* y el tomate en Colombia: [SIN FUENTE].

### 32.5 Resumen operativo (qué le sirve a un estudiante)
1. Fijar el alcance (género *Frankliniella*, o trips en general) con un rasgo visible (§24).
2. Esquema de etiquetas con etapa, sexo, sitio e individuo (§26) y protocolo de etiquetado (§27).
3. Línea base sin entrenar con BioCLIP congelado (§28), y comprobar si separa las etapas.
4. Si hay pocas fotos de una etapa, escalera del §30.2 y rollup (larva / prepupa-pupa / adulto).
5. Contexto dinámico: cultivo, región, época, síntomas en la planta, vector de virus (§29).
6. Devolver al usuario **etapa + nivel de confianza + remedio general según etapa**, y decir cuándo pedir otra foto o un experto.

## 33. Tabla de contenido definitiva del PDF (borrador, a la espera de autorización)

| # | Sección | Fuente | Hoja |
|---|---|---|---|
| 0 | Portada · «Guía de IA: cómo hacer que un modelo distinga animales» | §5 | Negra · apertura |
| 1 | Índice y cómo leer esta guía (para estudiantes) | §15, §24 | Normal |
| 2 | Qué se puede preguntar a una foto: taxón, etapa, sexo, edad, salud | §16 | Verde |
| 3 | Elegir el rango taxonómico: el grupo fácil de separar | §24, §11 | Normal |
| 4 | Una especie no es una sola apariencia: especie × etapa × sexo | §26 | Verde |
| 5 | Taxonomía y cómo identifican los expertos | §11 | Normal |
| 6 | BioCLIP 1, 2 y 2.5: qué son y cuándo usar cada uno | §8, §9 | Negra · apertura |
| 7 | Ruta de método, paso 0 a 5 | §6b | Normal |
| 8 | Etiquetar bien: protocolo | §27 | Normal |
| 9 | Fine-tuning o congelado: análisis y conclusión | §28, §10.1 | Verde |
| 10 | Pocas imágenes: aumentación y alternativas | §30 | Tablero |
| 11 | Datos: cuántos, de dónde, cómo dividirlos | §1.3, hallazgos Parte A §6 | Normal |
| 12 | Resultados de un caso real: anuros de Colombia | hallazgos Parte B | Tablero |
| 13 | Errores y lecciones; qué falló | hallazgos §1, §5; §10.2–10.4 | Normal |
| 14 | El contexto dinámico: lugar, altitud, fecha, hospedero | §12, §29 | Normal |
| 15 | Especies casi idénticas y qué las separa | §11.4 | Verde |
| 16 | Etapa, sexo y edad por grupo | §17 | Normal |
| 17 | Enfermedad en fauna y flora | §18 | Normal |
| 18 | Del animal a la flora | §31 | Normal |
| 19 | Método por organismo y pregunta (tabla de decisión) | §19 | Tablero |
| 20 | Caso conductor: *Frankliniella* y sus etapas | §32 | Negra · apertura |
| 21 | Diseño multi-pregunta, abstención y calibración | §20 | Normal |
| 22 | Despliegue: FP16, ONNX, caché | §10.3, §10.5 | Normal |
| 23 | Límites, ética y notificación | §21 | Verde |
| 24 | Glosario, fuentes y créditos (cuando se tienen) | todo | Normal |

## 34. Pendientes vigentes (tras las respuestas del 2026-10-15)

**Descartado por el usuario (no volver a pedir):** el mensaje de error de arranque de BioCLIP 2.5; la latencia en el Redmi; fuentes y licencias (solo se citan si se tienen); la norma colombiana de notificación se trata como teoría de contexto (§29.3).
**Decidido por el usuario:** el encoder se usa congelado (§28); el prior geográfico es dinámico (§29); alcance = animales con puente a flora (§31); lectores = estudiantes con el caso *Frankliniella* (§32); «género» = rango taxonómico elegido por la facilidad de separarlo de los vecinos (§24).

**Siguen faltando (concretos):**
1. ~~Confirmar que «franquinela» es *Frankliniella* (trips).~~ **Confirmado por el usuario el 2026-10-15.**
2. El cultivo y la región objetivo de los estudiantes (define hospedero, época y prior). Hoy solo hay datos de crisantemo, aster, bouvardia y rosa.
3. Cuántas fotos por etapa creen tener los estudiantes. Sin eso la escalera del §30.2 queda genérica.
4. Si los estudiantes tendrán acceso a microscopio para confirmar el género o la especie (condiciona las etiquetas).
5. Hasta dónde llega el «remedio»: la guía da principios por etapa y manda al agrónomo; ¿se quiere más (lista de productos)? No se incluirían dosis.
6. Si se incluyen o no los gráficos del tablero actual (graficos-datos.html) y cuáles se añaden (ver el mensaje del chat).
7. Imágenes y mockups listados en el chat.
8. Si se leen las ~100 notas de app y diseño y las fases 11, 12, 14, 15 y 18 antes del PDF.
9. Datos sin fuente que quedaron pendientes: tamaños de larva, prepupa y pupa de trips; haplodiploidía; caracteres que separan anuros crípticos (iris, membranas); FLOPs de BioCLIP.
