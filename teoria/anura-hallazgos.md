# Anura: hallazgos, pruebas, errores y teoría (recopilación para la guía universal)

Recopilado el 2026-10-14 desde `D:\Anura` y `D:\server\Anura`. Es **material en bruto ordenado**: cada dato lleva su fuente entre corchetes y sus condiciones, porque una cifra sin condiciones no sirve para decidir un método. Nada se ha inventado; donde dos fuentes se contradicen, se dice.

Dominio de origen: identificar especies de ranas (Anura) de Colombia con BioCLIP, k-NN y paquetes regionales, en el móvil. Lo que aquí se aprendió sirve para cualquier otra familia de animales o plantas.

---

## 0. Qué se leyó y qué no

**Leído completo o casi:**
- Bóveda Obsidian `D:\Anura\Second Brain` (189 md; leí unos 60: experimentos, decisiones, metodología, open set, admin, notas de conversación en `notes/`).
- Raíz de `D:\Anura`: `CONTEXTO_CURSOR`, `ESTADO_PROYECTO_2026-09-13`, `PLAN_MODELO_VISION`, `PLAN_ETIQUETADO_DATOS`, `PLAN_DESARROLLO`, `VALIDATION_GATE`, `EMBEDDING_CONTRACT`, `PROTOCOLO_ENCODER_Y_OBSERVACIONES`, `CAMBIOS_ENCODER_Y_OBSERVACIONES`.
- Informes de pruebas: `validation/` (fases 16, 17, 19, 20, 21, 23A, geografía, topografía, stress test, escalabilidad), `evaluation/open_set_v1/` (kNN, prior, ensemble, rechazo), `bioclip/` (resultados fase 4, logs), `training/` (destilación), `segmentacion/` (logs), `data dirty/` (reportes).
- Comentarios en código (`grep` de BUG/NOTA/FIX en `bioclip/`, `training/`, `pipeline_dataset/`): casi todo ya estaba documentado en los md; lo nuevo está incluido abajo.

**No leído (por si hay más que sacar):**
- ~100 notas de la bóveda sobre app, diseño, Kotlin, guía CVAT (no tocan el modelo).
- `D:\server\Anura\docs`, `README`, `DEPLOY_LINUX`, `CAMBIOS_PREFERENCIAS` (infraestructura del servidor).
- Informes de fases 11, 12, 14, 15, 18 de `validation/` y `evaluation/fase13/*` salvo lo resumido en otros informes.
- Logs de scraping (`scraper_run.log`, `logs_limpieza_duplicados.txt`) y los `.py` completos.
- Las imágenes y datasets.

---

## 1. Las 15 lecciones, en una página

1. **Mide un baseline sin entrenar antes de construir nada.** Zero-shot y k-NN sobre embeddings congelados dieron 70,4 % Top-1 (28 especies, 419 muestras, 5 pliegues) y el fine-tuning no lo superó [`bioclip/resultados_fase4_esquematizado.md`].
2. **Quitar el fondo no ayudó.** Recortar al animal bajó el Top-1 incluso sin entrenar (51,5 → 42,5 %), y poner el fondo a negro lo bajó más (60,7 → 50,7 → 44,7 %). Detalle en la sección 3.
3. **El contexto geográfico es la mayor ganancia y también el mayor riesgo.** +24,9 pp con el prior en el test completo, +15,3 pp en sitios aislados; pero aplicado a la decisión oficial volteó una identificación correcta [`Arquitectura Multimodal` §5.2].
4. **Filtrar por región mejora la precisión, no solo el peso del paquete.** k-NN sobre 25 especies regionales: 66,2 % frente a 54,4 % del clasificador de 41 clases (+11,8 pp).
5. **Un clasificador de N clases desperdicia probabilidad en especies que no están en la zona.** Es la causa mecánica del punto 4.
6. **Los ViT no se cuantizan a INT8 sin reentrenar.** Cinco intentos con herramientas distintas dieron entre 0,2 % y 51 %. FP16 es el límite práctico.
7. **La destilación a un modelo pequeño falló** (57,7 → 24,3 %): el alumno tenía que aprender "qué es una rana" y "cuál rana" a la vez, con la rana en el 10 % del encuadre.
8. **Mahalanobis con covarianza compartida degradó el rechazo**: AUROC 0,69 (euclídea cruda) → 0,59 (Mahalanobis). La covarianza se estimó con 798 imágenes de 10 especies en 512 dimensiones.
9. **El rechazo de especies desconocidas no está resuelto.** FAR entre 52 % y 94 % según el método, el umbral y el conjunto. El cuello de botella son pares de especies hermanas casi idénticas en el embedding, no la falta de contexto ni de datos.
10. **Una evaluación se puede contaminar sin querer.** La Fase 13 tenía el 100 % de sus imágenes KNOWN dentro de TRAIN; la auditoría por SHA256 no vio que una misma observación estaba duplicada bajo dos nombres de especie.
11. **Un score "perfecto" suele ser una trampa.** Mahalanobis ajustado sobre el mismo conjunto que se evalúa dio AUROC 1,0; el prior de zona con la especie real (oráculo) dio 0,701 y el honesto era 0,617.
12. **Separa near-OOD de far-OOD.** "No es una rana" se separa bien (hueco limpio 46,65 / 49,99); "es una rana que no conozco" no.
13. **La exportación a ONNX falla en silencio.** `opset_version=17` produjo un archivo de 1,2 MB sin error; hay que validar tamaño y predicciones idénticas.
14. **Las especies raras se salvan por el nivel taxonómico**, no por inflar datos: 27 de 28 especies quedaron cubiertas por género o familia.
15. **La documentación se desincroniza.** Hubo "BlockClip" (no existe), "BioCLIP 2.5 no existe" (sí existe), tres cifras de especies distintas y dos "nivel 2" con significados opuestos.

---

## 2. Cronología de resultados (con condiciones)

Las cifras no son comparables entre filas si cambian las especies, el split o la entrada. Por eso la tabla las lista juntas.

| Cuándo | Qué | Condiciones | Resultado | Fuente |
|---|---|---|---|---|
| Etapa I | Segmentación binaria + BioCLIP + cabezas | 10 especies, 70 individuos/especie, `GroupSplit` por individuo | **~99 %** | `Modelo de Visión — BioCLIP` §7 |
| Fase 3 | k-NN zero-shot (k=5, coseno) | 28 especies, 419 embeddings (15 img/especie), 5 pliegues | **70,4 % ± 4,4** Top-1; 90,9 % Top-3 | `resultados_fase4_esquematizado.md` |
| Fase 4 v1 | BioCLIP + 3 cabezas, 28 especies | Imagen completa; pico val 72,7 % en época 10 | Test **69,2 %** (−1,2 pp vs baseline) | idem |
| Fase 4 v2 | + Albumentations | Misma config | **19,7 %** (−50,7 pp) | idem |
| Fase 4 v3 | "+ dropout y weight decay" | No se ejecutó la config nueva | 69,2 % (igual a v1) | idem |
| EXP-001 | Transfer learning, 41 especies | Oversampling + pesos de clase | 35,3 % (zero-shot) → 44,2 % (solo cabezas) → **57,0 %** | `Experimentos y Resultados` |
| EXP-002 | ¿Daño por escasez? | <45 individuos vs ≥45 | 53,1 % vs 56,7 %: **rechazada**; el techo es taxonómico (*Dendropsophus*) | idem |
| EXP-006 | fp16 | CPU real | −0,1 pp (56,8 → 56,7 %) | idem |
| EXP-006/010 | int8 | dinámico y 3 estáticos | −5,4 pp; 3,5 %, 8,2 % y fallo de memoria | idem |
| EXP-007 | Prior GPS, peso 0,75 | Test completo / aislado >10 km (n=72) | +24,9 pp / **+15,3 pp** | idem |
| EXP-009 | RAM y latencia | 1/2/4 hilos | ~405 MB; 403 → 154 ms | idem |
| EXP-014 | k-NN + SQLite-vec | 41 especies, 766 imágenes | 1-NN 53,9 %; k=5 **56,4 %** (−0,7 pp vs clasificador) | idem |
| EXP-015 | Igual, paquete Antioquia | 25 especies, 467 imágenes | k-NN **66,2 %** vs clasificador 54,4 % (**+11,8 pp**) | idem |
| Destilación | BioCLIP → MobileNetV3-S | 2.230 train, variante A | Teacher 57,7 % → alumno **24,3 %** | `training/resultados_diagnostico_destilacion.md` |
| Prior de zona en paquete | k-NN + prior | 167 imágenes, control de fuga | 62,9 → **72,5 %** (+9,6 pp) | `Arquitectura Multimodal` §5.1 |
| Prior de clima | Open-Meteo | 129 imágenes | +3,9 pp (señal frágil) | `Contexto del Paso a Paso` |
| Creador de paquetes | Tres capas vs teléfono actual | 547 test, 715 desconocidas | 59,4 % vs 54,3 %; FAR 75,7 % vs 82,7 %; AUROC 0,652 vs 0,597 | `Prueba Real del Creador de Paquetes` |

**Discrepancias a tener presentes:**
- 70,4 % (Fase 3) y 57 % (EXP-001) no son la misma cosa: 28 vs 41 especies, 419 muestras vs 3.600+ y distinto split. El segundo es el honesto con individuos separados.
- El prior geográfico dio +24,9 pp en EXP-007 y +9,6 pp en el paquete real. Nunca se reconcilió cuál citar [`00_OPEN_TASKS`].
- Fase 4 v3 no probó la regularización: se ejecutó la configuración vieja.

---

## 3. Segmentación binaria y quitar el fondo (la pregunta de la que partiste)

### Qué se esperaba
Que recortar la rana (y poner el fondo a negro) quitara el atajo del sustrato y subiera el Top-1. Lo respaldaba la Etapa I (~99 %).

### Qué se probó, en orden

| # | Prueba | Resultado |
|---|---|---|
| 1 | Etapa I: segmentación binaria + BioCLIP, 10 especies | ~99 %. No es fuga (split por individuo), pero solo 10 especies (4 familias, 6 géneros) |
| 2 | Entrenar el segmentador (DeepLabV3+ResNet50, rana/fondo) | 827 pares → 820 sin duplicados; 574/123/123. IoU val 87,4 %, **test 83,3 %**; parada temprana en la época 16; brecha train-val 2,4 % |
| 3 | Aplicarlo a las 41 especies (17.180 imágenes) | La rana ocupa solo el **6–18 %** del encuadre (`fg_medio`). *Dendrobates truncatus*: 23,1 % de máscaras degeneradas, no pasó el gate |
| 4 | EXP-011: Fase 4 en variante C (recorte + máscara), 41 especies | **Peor que sin segmentar**: Top-1 especie 26,5 → 32,8 % frente a 35,3 → 41,9 % en el mismo tramo. Máscaras usables en 99,1–99,3 % del dataset: no fue falta de cobertura |
| 5 | Recorte sin entrenar (BioCLIP zero-shot, mismas 848 imágenes) | Completa **51,5 %** vs recortada **42,5 %** (−9,1 pp Top-1, −9,2 pp Top-3) |
| 6 | EXP-012: diagnóstico | El segmentador se entrenó con 9 especies y se aplicó a 41 (cambio de dominio). El bbox usaba **todos** los píxeles marcados: 34,2 % de las máscaras de *D. truncatus* tenían ≥2 islas y el recorte doblaba el área real |
| 7 | Arreglar el bbox (componente conexo mayor) | Sigue peor: 60,7 → 50,7 % (150 imágenes pareadas) |
| 8 | EXP-013: el código solo recortaba, nunca ponía el fondo a negro | Corregido, el fondo negro es **aún peor**: completa 60,7 % → zoom 50,7 % → fondo negro 44,7 % (Top-3: 83,3 / 80,7 / 75,3 %) |
| 9 | C-14: decisión | Variante C **descartada** para el prototipo del 27 sep, sin reentrenar |

### Por qué no ayudó (hipótesis, con lo que las respalda)
- **Cambio de dominio:** BioCLIP se preentrenó con millones de fotos naturales y el fine-tuning solo vio imagen completa. Un fondo negro artificial queda más lejos de lo que conoce que un simple cambio de encuadre. Cuanto más se aleja la entrada de lo visto, peor rinde (dispersión del EXP-013).
- **Recorte pequeño reescalado:** recortar ~10 % del encuadre y llevarlo a 224×224 mete borrosidad (explicación del propio script de recorte; el efecto aparece con el encoder sin entrenar).
- **Pérdida de contexto útil** que el ViT sí aprovechaba (hipótesis no probada).
- **Segmentador débil fuera de su dominio:** 9 especies de entrenamiento, 41 de uso.

### Qué NO se demostró
- Que la variante C sea mala en sí. Se evaluó solo con un modelo entrenado en imagen completa. **El único experimento que decide es reentrenar desde cero sobre el recorte con fondo negro y ambos arreglos** (pendiente; no cupo en 15 días).
- Que el 99 % de la Etapa I se deba a la segmentación y no a que eran 10 especies fáciles. Nunca se hizo la ablación en la misma muestra.

### Una decisión que costó tiempo
La decisión C-9 (11 sep) fue **esperar a la segmentación antes de entrenar identificación**. Después se vio que el recorte empeoraba. Se perdieron días bloqueados por una hipótesis no validada. Lo barato era el experimento 5, de unos 7 minutos de GPU.

### Qué quedó en pie
La segmentación **semántica** (16 regiones) pasa a ser capa de **explicación después** de identificar, nunca de decisión: "la segmentación nunca decide, solo explica" [`Automatización del Entrenamiento de Segmentación` §8]. El clasificador sigue viendo siempre la imagen completa.

---

## 4. Lo que funcionó

### 4.1 Contexto geográfico
- **Fórmula:** `P(especie|foto,lugar) ∝ P(especie|foto) · P(especie|lugar)^w`, con `P(especie|lugar)` por conteo de observaciones de train en 50 km, suavizado de Laplace/α=0,5, y w=0,75 por barrido.
- **Validación anti-fuga:** se descartaron 300 observaciones con precisión posicional de hasta 7.270 km; sin coordenadas en (0,0).
- **Decaimiento gradual con la distancia** (24 → 21 → 15 pp): firma de señal biogeográfica real, no de memorización de coordenadas.
- **Incidente real (22 sep):** el prior sin acotar volteó una *D. bogerti* bien identificada a *D. truncatus* (razón de prior ≈5×). **Regla vigente:** la especie oficial sale siempre del voto visual; el prior solo reordena las alternativas mostradas y el porcentaje.
- **Lo que no sirvió:** prior de género/familia (GEO-4: Top-1 0,634 → 0,411, "perjudicial"), altitud por punto exacto para rechazo (NO_GO: FAR 36,94 → 36,77 %), clima como pieza de decisión (+3,9 pp, n=129, y añade dependencia de red).
- **Sin coordenadas en el pool KNOWN oficial:** 0 % recuperables por diseño; la ablación completa quedó NOT_VERIFIED. Con 38 imágenes, geografía y altitud no cambiaron ni un caso.

### 4.2 Paquetes regionales + k-NN (estilo Merlin)
- Backbone congelado en la app; lo que cambia por zona son embeddings en `.sqlite` descargables.
- Antioquia: 6,39 MB, 2.073 vectores, 25 especies (≥3 observaciones de train dentro del bbox).
- El paquete del creador pesa **241 KB** frente a 11,2 MB del actual (50 veces menos).
- Añadir una especie = actualizar datos, no reentrenar (probado 41 → 42 con un fixture sintético; releases anteriores intactos por hash).

### 4.3 Cascada taxonómica y techo de resolución por especie
- Cabezas Familia/Género/Especie y enmascarado jerárquico para no predecir combinaciones imposibles.
- Niveles por cobertura: **A** ≥70 individuos (especie, umbral estándar), **B** 30–69 (umbral más exigente), **C** <30 con género/familia ≥70 (baja a género o familia), **D** <30 sin rescate (familia y candidata a open set). Umbrales de arranque A 0,50 y B 0,70, a recalibrar.
- Cobertura: 27 de 28 especies rescatadas por jerarquía; solo *Sachatamia electrops* quedó huérfana (única centrolénida).
- **Trampa al reportar:** el "acierto en el nivel afirmado" se infla bajando siempre a familia; se reporta junto con la distribución de niveles afirmados.
- Ponderación amortiguada (raíz cuadrada) en vez de frecuencia inversa: multiplicar ×6 el gradiente de una clase de 11 individuos fuerza a memorizar.

### 4.4 Datos y evaluación
- `GroupSplit` por `obs_id` real de iNaturalist, tope de 70 observaciones por especie: 3.258 imágenes, 1.706 individuos, 0 grupos partidos.
- pHash/dHash para duplicados y ráfagas (>95 % de similitud).
- Augmentación **solo en train y al vuelo**; estadísticas de normalización solo con train.
- Gates documentados: calidad, taxonomía, contaminación, embedding, centroides, open set, blind test → PASS / FAIL / PENDING; nunca un `READY_FOR_PRODUCTION` automático.

### 4.5 Exportación y despliegue
- ONNX con `torch.onnx.export` (dynamo), **opset 18, batch fijo = 1**, consolidar pesos externos en un archivo, FP16.
- Resultado: 165,6 MB; 100 % de predicciones idénticas a PyTorch (64 imágenes); coseno 0,999999 del encoder.
- RAM ≈405 MB constante entre 1 y 4 hilos: la mayoría son activaciones, no pesos.
- FP16 no gana velocidad en CPU (decodifica a fp32 al vuelo) pero **sí mitad de tamaño**.
- Preprocesado idéntico o las predicciones no sirven: 224×224 RGB, media/desv. de open_clip.

### 4.6 Micro-adaptadores (en el admin)
- ArcFace real sobre una matriz W de 512×64 FP16 (64 KiB), con el encoder congelado.
- Medido: *P. paisa* ↔ *P. palmeri* 79,2 → 87,5 %; clúster de 4 especies 83,3 → 85,4 %.
- **Bug del entrenamiento:** con lr 0,05 y decaimiento por época divergía y colapsaba a un prototipo (~50 %). Corregido con decaimiento por paso y lr 0,01.
- Los números de 7 *Pristimantis* (46,4 → 64,3 %) son de la **simulación**, no de datos reales.

---

## 5. Lo que falló (errores con causa y lección)

### 5.1 Modelos y entrenamiento

| Qué | Cómo falló | Causa | Lección |
|---|---|---|---|
| Destilación BioCLIP → MobileNetV3-S | 57,7 → 24,3 % (−33,4 pp; objetivo <10) | Alumno aprendía "qué es una rana" y "cuál" a la vez; rana en el 10 % del encuadre; 2.230 imágenes | La destilación necesita entrada de calidad, brecha pequeña y preentrenamiento parecido. La coherencia taxonómica sí se transfirió (79,7 vs 83,4 %) |
| INT8 de BioCLIP | ~0,2 % | Outliers de atención del ViT | Consultar la literatura **antes** de optimizar un ViT |
| INT8 dinámico | −5,4 pp sin ganancia real | — | Descartado |
| INT8 estático ×3 | per-channel 3,5 %, per-tensor+MinMax 8,2 %, Percentile con `bad allocation` | Softmax y LayerNorm tienen rangos que una escala entera no representa | Solo con entrenamiento consciente de cuantización |
| Albumentations | 19,7 % (−50,7 pp) | Normalización incompatible con el pipeline BioCLIP | Revertir a torchvision; probar la augmentación sola antes |
| Fase 4 v1 | Pico val 72,7 % → test 69,2 %; pérdida de train 0,92 → 0,01 | Memorización con 28,7 M parámetros descongelados y ~2.200 imágenes | Techo de ~70 % con imagen completa |
| EfficientNet-B0 | Descartado | Necesita muchos más datos por especie | El preentrenamiento del dominio gana con pocos datos |
| ObjectBox | Reemplazado por sqlite-vec | Almacén único mmap, no se pueden montar y borrar bases por región | Decidir primero la operación, luego el motor |
| Reutilizar el backbone visual para audio | Descartado antes de probar | Alumno estrecho, riesgo de mala transferencia | Modelo dedicado pequeño (1–3 MB) |

### 5.2 Exportación y despliegue

| Síntoma | Causa | Solución |
|---|---|---|
| `torch.jit.trace`: "Graphs differed across invocations" | Ramas condicionales internas del ViT | Usar `torch.onnx.export` |
| ONNX de 1,2 MB sin error | `opset_version=17` forzaba una conversión que corrompía el grafo | Exportar directo en opset 18 |
| `ReshapeHelper: 197,8,768 vs 197,768` | `dynamic_axes` rompe el reshape de atención multi-cabeza | `batch=1` fijo |
| Pesos en un `.onnx.data` aparte | Formato "external data" por defecto | Consolidar con `save_as_external_data=False` |
| Falta `onnxscript` | Dependencia no declarada | Instalar `onnxscript` y `onnxconverter-common` |
| `Axis 1 is out-of-range ... rank 1` (24 LayerNorm) | `per_channel=True` sobre pesos de un solo eje | `per_channel=False` (no arregla la precisión) |
| `TypeError: NoneType` en un nodo `Expand` | Bug de `symbolic_shape_infer.py` con grafos dynamo | `skip_symbolic_shape=True` |
| `no such table: zone_prior_meta` (crash real) | Paquete ya instalado quedó desactualizado: el sha256 cambió pero el registro seguía apuntando a la copia vieja | Pendiente: mecanismo de detección y reinstalación (se repetirá) |
| Cuelgues intermitentes de `urllib`/`requests` | Red del entorno | Invocar `curl` por subprocess |

### 5.3 Rechazo de desconocidos (Open Set)

| Qué | Resultado | Causa |
|---|---|---|
| Fase 13 (Mahalanobis + Ledoit-Wolf, τ=39,354 al 95 % de KAR) | AUROC 0,625; **FAR 91 %**; UDR 8,9 % | Umbral permisivo; evaluación contaminada (ver 5.4) |
| Fase 16 (blind limpio: 7.475 KNOWN, 56 UNKNOWN) | AUROC 0,593; **balanced accuracy 0,457 (peor que azar)** | Mismo método sin la fuga |
| Fase 17 | Coseno 0,689, euclídea 0,694, **Mahalanobis 0,592** | Covarianza 512×512 con 798 imágenes de 10 especies; condición ≈624 |
| Fase 19 | Hipótesis **D_MIXED** | Hasta 50 % de las imágenes de *P. erythropleura* quedan más cerca de otra especie que de la propia; el AUROC crudo (0,7245) supera al post-procesado |
| Fase 20 | La pérdida ocurre al aplicar el whitening (0,69 → 0,59); el umbral congelado da balanced accuracy 0,4566 | El `individual_id` es el `observation_id` de iNaturalist, no un animal verificado |
| Fase 21 | Euclídea cruda 0,5991 vs Mahalanobis 0,4629; **no se promueve** | Solo 2 especies UNKNOWN; VALIDATION solo con KNOWN (Youden=1,0 es artefacto) |
| Fase 23A (7 especies, 620 UNKNOWN) | **AUROC 0,5733**, FAR 51,6 %, FRR 37,3 % | Pares gemelos (ver 5.5) |
| Primer informe automático 23A | AUROC vacío (NaN) y FAR 1,0 | Resultado inservible; el valor oficial posterior es 0,5733 |
| k-NN como detector | max_similarity AUROC 0,678; **consenso 0,510**; FAR 96,4 % | "VECTORIAL_NO_MEJORA" |
| Ensemble softmax + k-NN | AUROC 0,703 pero FAR 92,9 % | Mejora de AUROC sin mejora operativa; sin calibración independiente |
| Rechazo Mahalanobis (Fase 9) | AUROC 1,0 y FAR 0 | Ajustado sobre los mismos datos que se evalúan (en muestra) |
| Prior sobre desconocidos | 56/56 UNKNOWN terminan en alguna de las 41 clases; GPS adversarial baja el Top-1 de 79 a 27 % | El prior solo reordena; no crea rechazo |
| Regresión final con 41 especies activas | AUROC 0,538; FAR 0,85; KAR 0,824 | Umbral demasiado permisivo |
| Topografía real (elevación, pendiente, relieve) | **NO_GO** (FAR −0,16 puntos, 1 caso) | El problema no es contexto |

**Dato que sí salió bien:** "no es una rana" se separa de "rana desconocida" con un hueco limpio: mínimo de no-rana 49,99 frente a máximo de rana desconocida 46,65 (30 imágenes de Wikimedia, 15 de *H. picachos*). El umbral 39,35 rechaza el 100 % de las no-rana. Se añadió `NotAnuroTau = 48,0` a mano (sin calibración formal; n pequeño; no probado en teléfono).

### 5.4 Contaminación y errores de evaluación

| Qué | Detalle | Cómo se detectó / arregló |
|---|---|---|
| Fuga en la Fase 13 | KNOWN del blind: 197/197 (Grupo A) y 569/569 (Grupo B) ya estaban en TRAIN; F3 completo era subconjunto exacto de TRAIN | Auditoría de Fase 16: se rehízo con 7.475 imágenes limpias y se congeló el resultado antes del blind |
| Centroides del Grupo B hechos con F3 (in-sample) | Violaba la separación ciega | Se rehicieron con TRAIN (3.608 verificadas) |
| Extractor de embeddings divergente | `create_model('ViT-B-16', pretrained=False)` + preproceso manual vs `hf-hub:imageomics/bioclip` | KAR del Grupo A = 0 %. De ahí el **contrato de embedding** (sha256 del encoder + dimensión + preprocesado + normalización) |
| Typo taxonómico | `acanthinus` vs `achatinus` | Alias en `taxonomia.py`; otro proceso lo borró durante la Fase 16 y bajó de 9 a 8 las especies resueltas |
| *D. labialis* = *D. molitor* | 34 de 43 observaciones (79,1 %) eran la misma observación de iNaturalist; el taxón se sinonimizó después de construir el dataset | El `leakage_audit` comparaba solo SHA256 exacto. Rebaseline: AUROC 0,5733 → 0,5713, diferencia no significativa |
| Oráculo en GEO-2/GEO-3 | Se consultaba el prior con la especie **real** de la imagen KNOWN | AUROC 0,701 inflado; honesto ≈0,617 |
| Pool KNOWN anónimo | `CLEAN_KNOWN_00001…` sin `obs_id` ni ruta | 0 % de coordenadas recuperables; la ablación geográfica completa no se pudo hacer |
| 17 de 41 especies | Consumieron el 100 % de sus datos reales en train/ref/calibración | No existe KNOWN limpio para ellas |
| Cobertura UNKNOWN | 2 especies, 35 individuos (luego 7 especies, 321 individuos) | Insuficiente (se pidió ≥10 especies y ≥200 imágenes) |
| UNKNOWN faltante | 2 de 7 especies declaradas (183 imágenes) no estaban físicamente | Informe 23A parcial |
| Fase 4 v3 | La regularización nueva no se compiló en la corrida | Resultado idéntico a v1 |

### 5.5 Pares de especies que concentran el error

- **Distancia entre centroides:** *P. paisa* ↔ *P. taeniatus* 0,1944, el par más cercano posible (percentil 0 de 820). Solapamiento cruzado ≈22 %.
- **Margen negativo por especie** (imágenes más cerca de un rival que de su propio centroide): *P. paisa* 35,4 %, *P. erythropleura* 50 %, *P. achatinus* 45 %, *D. bogerti* 41 %.
- **Generalización entre individuos:** Top-1 medio 53,5 %, tasa de margen negativo 46,5 %; rango desde *Boana boans* 83,3 % hasta *Boana platanera* 44,4 %.
- **Falsos aceptados en 23A:** 6 pares concentran el 84 % (191/228). El mayor, *Rhinella marina* → *R. horribilis* (60). Excluirla subió el AUROC de 0,5733 a 0,6156.
- **Rangos de altitud solapados:** *R. marina* 25–2.500 m (mediana 473) y *R. horribilis* 4,5–2.467 m (mediana 1.060). Ni geografía ni altitud las separan.
- **Dónde caen los desconocidos:** el 100 % de las 56 UNKNOWN tenía como vecino más cercano una familia distinta; 47 % de los falsos aceptados se concentró en *B. cinerascens* y *H. palmeri*.
- **Sachatamia electrops** (rana de cristal) es la huérfana: 23 individuos, única centrolénida. Su rasgo diagnóstico (vientre translúcido) no se puede descartar como "foto de mano".
- **Limpieza real de fotos:** EXP-003 eliminó 2 fotos (amplexo y manejo); EXP-004/005 generaron 50 candidatas de alta confianza (≈65–70 % de precisión) pendientes de revisión manual.

### 5.6 Documentación y proceso

- "BlockClip" (no existe; era un error de transcripción de BioCLIP).
- "BioCLIP 2.5 no existe" (C-8) era falso: `imageomics/bioclip-2.5-vith14` sí existe y lo usa el servidor.
- Número de especies: 15, 14, 23, 28, 30 y 50 según el documento (se fijó 28 para el prototipo; luego se trabajó con 41).
- Número de clases anatómicas: 8, 13, 16 y 18 (vigente: 16).
- "YOLO-seg es segmentación semántica": YOLO-seg es de instancias.
- Dos "nivel 2": micro-adaptador de desempate frente a fallback de género. Se renombraron `desempate_criptico` y `cascada_taxonomica`.
- El umbral τ tenía seis unidades distintas (0,32; 0,78; 0,85; 39,35; distancia, similitud, Mahalanobis).
- Tres arquitecturas de paquete en conflicto (JSON de centroides, `.sqlite` con todos los vectores, y lo que la app lee) y el paquete del creador **no lo lee el teléfono todavía**.
- Un agente borró el modo demo de la web y se cortó por límite de uso con tres agentes a medias y 74 archivos sin commitear.
- La Fase 13 ya no es evidencia: quedó marcada `COMPROMISED_BY_LEAKAGE`.

---

## 6. Datos: reglas, números y cobertura

### 6.1 Cuánto hace falta (reglas de la bóveda)
- **Identificación:** ≥70 individuos por especie. **Segmentación:** 25–30 imágenes por especie (otro modelo, otro requisito).
- **Centroide estable:** mínimo viable 10–15 fotos y 3–5 individuos; recomendado 30–50 fotos y 8–12 individuos; robusto 80–100+ fotos y 15+ individuos.
- **Lo que estabiliza el centroide es la variación entre individuos**, no el número de fotos del mismo animal.
- Más datos para: especies polimórficas (*Pristimantis*), pares crípticos y las más comunes (80 % del uso real).
- Diversidad de fotos propuesta: 60 % dorsolateral, 25 % dorsal, 15 % cabeza o vientre; flash nocturno, luz diurna, hojarasca, hoja verde, roca; seca y mojada.

### 6.2 Estado real (Sep 2026)
- Datos: 28 especies, 14.996 fotos y 893 audios al inicio; 15.229 imágenes (15.228 válidas) en el scraper; 43 especies, 12.209 fotos y 100 observaciones de la app en producción el 29 sep.
- Splits de la destilación: 2.230 / 479 / 548 imágenes (1.193 / 246 / 267 individuos).
- Splits de fase 4 con segmentación: 3.629 / 750 / 848 (41 especies, 7 familias, 13 géneros).
- 24 de 28 especies con ≥70 fotos; las 4 deficitarias, en individuos: *D. norandinus* 11, *H. picachos* 22, *S. electrops* 23, *P. vilarsi* 33. Las fuentes públicas ya estaban agotadas.
- *Boana xerophylla*: solo 3 fotos de Colombia; se completó con fotos internacionales. *P. vilarsi*: 19 individuos en iNaturalist.
- Antioquia: ~230 especies teóricas → ~130 con fotos públicas → ~85 con >50 fotos. Aun así el catálogo regional cubre ~98 % de los encuentros reales.

### 6.3 Audio
- **AnuraSet no sirve** para este catálogo: 42 especies, todas de biomas brasileños, cero traslape.
- Xeno-canto por scraping manual (API v2 retirada; v3 pide clave); IAvH Banco de Sonidos solo reenvía a Xeno-canto.
- Sin grabaciones públicas: *D. reticulatus*, *S. electrops*, *D. truncatus*, *H. picachos*, *P. vilarsi*, *P. penelopus*.
- Estándar de captura: WAV/PCM 16 bit, 44,1 kHz, mono, 3–5 s, SNR ≥15 dB (<10 dB descartar). Augmentación: SpecAugment, nunca invertir el espectrograma.

### 6.4 Augmentación
- **Permitida:** flips, rotaciones, `ShiftScaleRotate` ≤20 %, elástica suave, brillo/contraste ±30 %, sombra, CLAHE, matiz ±10.
- **Prohibida:** `HueShift > 15` (el color diagnóstico en dendrobátidos), deformaciones que alteren la proporción hocico-cloaca, MixUp/CutMix entre especies del mismo género.
- Siempre al vuelo y solo en train.

### 6.5 Etiquetas y taxonomía (errores de nomenclatura reales)
Siete correcciones en `anuro_labels.json`: `acanthinus → achatinus`, `picachus → picachos`, `sp_margaritifera → margaritifera`, `cinereascens → cinerascens`, `Pristimantis norandinus → Dendropsophus norandinus` (cambio de género), y eliminación de dos especies fantasma (*Leucostethus fraterdanieli*, *Dendrobates sp. guaviare*). Carpetas con errores de tipeo (`Boana cinereansis`, `Boana xeraphyla`, `Dendrosophus reticulatus`) se mapean con un diccionario explícito, nunca por coincidencia de texto.

Valores que faltaban en CVAT: `amplexus` (postura), `borrosa_total`, iris `negro` y `bicolor_reticulado`, dorso `reticulado` y `lineas_dorsolaterales`, `pliegue_tarsal`. Regla de equipo: ante la duda entre marcar algo y `no_determinable`, gana `no_determinable`; ante desacuerdo en una escala ordinal, el valor más conservador.

---

## 7. Teoría aplicada: lo que se decidió y por qué

### 7.1 Representación y clasificación
- BioCLIP ViT-B/16 (TreeOfLife-10M, 512-d) como extractor. Zero-shot ya sirve como suelo.
- Normalización L2 para quitar la magnitud (luz, escala, fondo) y quedarse con el ángulo.
- **Prototipos (centroides L2)** en vez de una capa `Dense(N)`: añadir especie = calcular un vector; no sufren el sesgo de clase del softmax.
- Tres centroides: **global**, **regional por paquete** y **de morfo**. No se promedian morfos opuestos (*Oophaga histrionica*). Con <3 individuos en el paquete se presta el global con `borrowed: true`.
- **Super-centroides:** género = suma L2 de especies; familia = suma L2 de géneros (un voto por género). Rangos de partida de τ: especie 0,72–0,85; género 0,60–0,70; familia 0,50–0,58 (hipótesis; el cálculo real de familia salió por encima en la simulación).
- Cabezas jerárquicas con pérdida multi-cabeza (CE en paralelo) + enmascarado.
- **Triplet/ArcFace:** triplet es de 2015, exige minería (batch-hard, lotes de P clases × K imágenes con K≥4); ArcFace/SupCon son más estables. Hard-negative mining es peligroso con etiquetas sucias (elige una y otra vez el error). Regla: medir primero con embeddings congelados; añadir solo si Recall@5 no alcanza.
- **Decisión de arquitectura:** no descongelar el ViT (obligaría a redistribuir el ONNX de >100 MB). El metric learning va **solo en el micro-adaptador**.
- Una nota de conversación recomendaba ArcFace con margen 0,35–0,5 sobre las últimas capas del ViT con lr 1e-5; se descartó por el motivo anterior.

### 7.2 Micro-adaptadores y clústeres crípticos
- Matriz W (512×64, FP16, 64 KiB) por clúster de N especies; según las notas de diseño, reentrenar un clúster tarda ~30 s–1 min (no medido) y no toca los demás ni el ONNX.
- Árbol de adaptación si el grupo pasa de ~12 especies (`MAX_CLUSTER_SPECIES=12`, configurable, avisa y no divide solo).
- El **herpetólogo** define los miembros; el sistema alerta pero no decide.
- La capa 2 usa el error de reconstrucción ε del subespacio. **En simulación** rechazó 100 % de intrusos de otra familia y ~48 % de congéneres, por eso existe la capa 3 de contexto.

### 7.3 Open Set (diseño vigente)
- **Tres capas:** (1) distancia con radio por especie ajustado con Weibull/EVT sobre distancias intra-clase y convertido a corte de coseno (`tau_kind: cosine_similarity`); (2) residuo de reconstrucción en clústeres; (3) compuerta ecológica (altitud gaussiana × hábitat), valor inicial P<0,05.
- **Estados:** `MATCH_SPECIES`, `MATCH_GENUS`, `MATCH_FAMILY`, `OSR_GLOBAL`, `OSR_CLUSTER`, `OSR_GEO`.
- Mahalanobis queda como **comparación offline**, no se empaqueta. GAN, MC Dropout, ensambles y OpenMax no van al móvil.
- **Procedimiento correcto:** objetivo operativo → umbral elegido en validación → reporte en test sin tocarlo. Separar near-OOD y far-OOD y reportar ambos. Métricas: AUROC, FPR@95TPR, AUPR, accuracy en conocidos y coherencia jerárquica del rechazo.
- **Coste de los errores:** un falso conocido contamina la base científica; un falso desconocido solo molesta. Umbral conservador.
- Rechazo jerárquico: "Familia Hylidae, género probable *Boana*, especie no determinable" vale más que "desconocido".
- **Medido con vectores reales** (el simulador daba AUROC 0,91, FAR 20 %; la realidad: AUROC 0,65, FAR 93 % en capa 1, 75,7 % con las tres capas). Las tablas simuladas se marcaron "optimistas".
- **Capa 3 con datos reales:** `umbral_geo` 0,05 ataja 31 desconocidas pero rechaza 25 fotos buenas de 167. Pendiente decidir rechazo o penalización.

### 7.4 Contexto, pesos y fusión
- **Late fusion** ponderada sobre puntuaciones calibradas (temperature scaling), nunca sumar porcentajes crudos; renormalizar los pesos entre las modalidades presentes.
- Variables de contexto por importancia: GPS (10/10), altitud (10/10), canto (10/10 para crípticas), fecha/hora (8), microhábitat (8), talla (6).
- **Pesos por perfil de especie:** generalista 80/10/10 (σ altitud 1000 m); microendémica 30/60/10 (σ 120 m); par críptico 35/35/30; especialista de quebrada 50/20/30. Se implementan como gaussianas por especie, no como `if/else`.
- Cada peso en tres valores visibles: calculado, manual y efectivo; el sistema nunca pisa el manual.
- **Regla de oro:** el prior acotado (p. ej. multiplicador 0,5–1,5) o solo para alternativas; **nunca elimina una especie** (los registros más valiosos son los que aparecen donde no se esperaba).
- **"No observable" ≠ "ausente":** tipo de tres estados, nunca booleano.
- Cada prior nuevo se evalúa también por si puede voltear una identificación visual de alta confianza.
- Pendientes de prior sin datos: ecosistema (barato: punto en polígono IDEAM), microhábitat (texto libre de iNaturalist), talla/SVL (AmphibiaWeb, 291 consultas), hora (solo fecha disponible en el CSV).

### 7.5 Contratos, versiones y gates
- **Contrato del embedding:** `encoder_sha256` + dimensión + preprocesado + normalización; solo son comparables vectores con contrato idéntico.
- **Encoder:** `bioclip_anura_mejor.pt` (fine-tuning de BioCLIP 1) → `encoder_anura_fp16.onnx`, sha `219e860e…`. "Congelado" significa "no se reentrena desde el 12 sep", no "BioCLIP 1 puro".
- **BioCLIP puro frente a fine-tuned:** mismo Top-1 (59,0 vs 59,2 %), pero el fine-tuned rechaza mejor (FAR 75,7 vs 84,2 %; AUROC 0,652 vs 0,599). El valor del fine-tuning está en el rechazo, no en el Top-1.
- **Releases:** inmutables por hash; un paquete regional elige su release visual; releases viejo y nuevo coexisten. Aprobación científica y técnica por **personas distintas**; publicar pide confirmación.
- **Escalabilidad real:** el pipeline de ingeniería escala a cientos de especies; el Open Set científico no (la covarianza compartida con 9 especies es un BLOCKER pasadas ~50).
- **Privacidad:** observaciones públicas solo en servidor; privadas en servidor y móvil; fotos privadas con URL firmada de 60 s; coordenadas de especies amenazadas ofuscadas.

---

## 8. Cómo salió el ciclo de datos y el despliegue

- Flujo vigente: especie → ficha publicada → fotos y vectores → centroides → calibración OSR → compilación de paquete por subregión (borrador → aprobado → publicado) → descarga en el teléfono.
- Entorno de pruebas desechable (`_pruebas`): Postgres de prueba, MinIO de prueba, 14 suites pasaron con bases nuevas.
- Auditoría de seguridad: 6 vulnerabilidades corregidas, entre ellas la toma de la cuenta *super* por mayúsculas y la lectura de archivos con `..` en miniaturas.
- Desplegado el 29 sep (copias previas: `pg_dump` y 8,7 GB de MinIO). El vaciado de datos **no se hizo** (el usuario lo rechazó).
- Paquete legado de Antioquia (30 especies, 4.034 vectores) importado y restaurable con un botón.
- **Aún sin verificar:** prueba de punta a punta en un teléfono real; `OnDeviceInferenceTest`; la app no lee todavía el umbral del paquete ni los clústeres.

---

## 9. Preguntas abiertas con evidencia

| Pregunta | Qué se sabe | Qué falta |
|---|---|---|
| ¿Mejora la variante C si se **reentrena** desde cero con ambos arreglos? | Solo se probó en inferencia: empeora | El experimento en sí |
| ¿Qué umbral open set de producción? | 39,35 (FAR 91 %) vs 35,36 (piloto) vs 48,0 (solo no-rana) | Validación de campo con calibración mixta |
| ¿Rejector aprendido sobre los 512-d? | Propuesto como siguiente paso barato | Probarlo |
| ¿Hard negatives o fine-tuning dirigido a pares gemelos? | Causa raíz identificada (*Rhinella marina/horribilis*) | Protocolo nuevo; toca el encoder |
| ¿Euclídea cruda reemplaza a Mahalanobis? | Mejor en todo lo medido, no es release | ≥10 especies UNKNOWN (≥200 imágenes), calibración mixta, blind independiente |
| ¿Altitud como rechazo o como penalización? | Rechazo cuesta 25 fotos buenas de 167 | Decisión del autor |
| ¿Cuál cifra citar del prior geográfico? | +24,9 pp (EXP-007) vs +9,6 pp (paquete real) | Reconciliar condiciones |
| ¿Funciona el audio? | Sin métricas ni arquitectura | Datos y experimento |
| ¿QAT para bajar tamaño? | Solo FP16 funciona | Reentrenar con cuantización simulada |
| ¿Piloto de campo (≥150 observaciones, ≥2 localidades)? | Plantillas listas; ningún reporte con datos | Hacerlo |
| ¿Catálogo de 28 o 41 especies? | La app y las pruebas usan 41 | Confirmar con el autor |
| ¿Rechazo por tipo de foto? | Casos adversariales 13/16 pasaron; 0 bytes, bytes aleatorios y JPEG truncado lanzan excepción sin capturar | Añadir `ERROR_DE_ENTRADA` al contrato |

---

## 10. De los hallazgos a la guía universal

Reglas de decisión que se pueden aplicar a cualquier animal (para el apartado 6b de `guia.md`):

| Si… | Entonces… | Evidencia aquí |
|---|---|---|
| Vas a empezar | Mide zero-shot y k-NN con embeddings congelados antes de entrenar | Fase 3 70,4 % vs fine-tuning 69,2 % |
| Quieres pre-procesar la imagen (recorte, fondo, segmentación) | Haz un A/B **con el modelo que vas a usar**, sin entrenar, antes de construir el pipeline | −9,1 pp; −10 pp; −16 pp |
| El animal ocupa ~10 % del encuadre | Mide el efecto de resolución; no asumas que recortar ayuda | `fg_medio` 6–18 % |
| Tienes muchas especies y el usuario sabe dónde está | Filtra por región y usa k-NN sobre el paquete regional | +11,8 pp |
| Tienes coordenadas | Úsalas como prior **acotado y solo para reordenar** | +24,9 / +15,3 pp; incidente D. bogerti |
| Tienes clases raras | Resuelve a nivel de género o familia y comunícalo | 27/28 cubiertas |
| Necesitas meter el modelo en el móvil | FP16, ONNX con batch fijo y opset 18; verifica predicciones idénticas; no INT8 en ViT | 5 intentos fallidos |
| Quieres modelo pequeño on-device | No destiles con la entrada original; mide el hueco antes | −33,4 pp |
| Quieres rechazar desconocidos | Distancia simple (coseno o euclídea) antes que Mahalanobis; calibra con un set mixto; separa near y far; no ajustes el detector con el set de evaluación | AUROC 0,69 vs 0,59; Youden=1,0 artefacto |
| Tus especies tienen gemelas | Documenta pares conflictivos y advierte al usuario; micro-adaptador solo para clústeres confirmados | *R. marina/horribilis*, *P. paisa/taeniatus* |
| Vas a evaluar | Split por individuo y localidad; congela antes del blind; audita por hash **y** por observación | Fase 13 y Fase 16; *D. labialis* |
| Añades una especie | Embeddings → centroide → release nuevo; no reentrenar; recalibrar si pasan ~50 | Escalabilidad 41 → 42 |
| Reportas resultados | Siempre con condiciones: especies, split, n, versión | Tabla de la sección 2 |
| Dependes de documentos | Una sola fuente de verdad y registro de decisiones con fecha | Sección 5.6 |

---

## 11. Archivos fuente principales

- `D:\Anura\Second Brain\Brain\07 Notas de Trabajo\Experimentos Fallidos y Decisiones Descartadas.md`
- `…\05 Evaluación y Métricas\Experimentos y Resultados.md`
- `…\07 Notas de Trabajo\Inconsistencias y Decisiones Pendientes.md`
- `…\04 Desarrollo Técnico\Optimización para Inferencia en Móvil.md`, `Modelo de Visión — BioCLIP.md`, `Automatización del Entrenamiento de Segmentación.md`
- `…\02 Metodología\Open-Set Recognition.md`, `Arquitectura Multimodal.md`, `Estrategia para Especies con Cobertura Insuficiente.md`, `Contexto del Paso a Paso — Datos Faltantes.md`
- `…\19_ADMIN\Contradicciones del Modo Administrativo.md`, `Prueba Real del Creador de Paquetes.md`, `Auditoria de Implementacion del Admin.md`
- `…\Second Brain\notes\*.md` (conversaciones sobre centroides, micro-adaptadores, OSR, pesos)
- `D:\Anura\validation\fase16…fase23a\*`, `OPEN_SET_GEOGRAPHIC_INVESTIGATION_FINAL_REPORT.md`, `merlin_identification_flow\stress_test_v1\*`
- `D:\Anura\bioclip\resultados_fase4_esquematizado.md`, `bioclip\checkpoints\log_fase4_variante_c.txt`, `bioclip\evaluation\log_experimento_recorte.txt`
- `D:\Anura\segmentacion\log_entrenamiento.txt`, `log_aplicar.txt`
- `D:\Anura\training\resultados_diagnostico_destilacion.md`

---

# PARTE B · Datos de la base de producción (recopilados 2026-10-15)

Fuente: base `anura` (contenedor `anura_postgres`, solo lectura) y `services/dataset-service`, aportados por el usuario el 2026-10-15. Encoder: BioCLIP v1, 512 dim, sha `219e860e…`.

**Etiquetas de origen:** **[BD]** guardada por el panel · **[CALC]** calculada con SQL de solo lectura (mismo método que `evaluacion.js`; la tabla `dataset.evaluacion` está vacía) · **[DOC]** escrita en docs del repo · **[HIST]** método que ya no se usa · **[SIM]** simulación o dato de prueba, ver §14 (nunca se mezcla con las demás) · **[STAT]** cálculo estadístico mío sobre cifras reales.

> **Cambio de escala frente a la Parte A:** la Parte A trabaja con 28 y 41 especies (fases de septiembre). La Parte B es el dataset vigente: **56 especies**. Las cifras no son comparables entre partes (otras especies, otro split, otra versión).

## 12. El dataset medido (v5)

| Dato | Valor |
|---|---|
| Especies / fotos / observaciones (individuos) | 56 / 5.818 / 3.240 [BD] |
| Fotos por especie (mín / mediana / máx) | 85 / 100 / 191 [CALC] |
| Versión vigente v5 | train 4.087 · val 861 · test 864 fotos; 3.221 individuos; 70/15/15; partición **por individuo** (semilla `anura`) [BD] |
| Piso para entrar a un paquete | ≥ 80 fotos activas y ≥ 10 individuos (antes 10 fotos y 3 individuos) [código `reglas.js`] |
| Mínimo para centroide regional / morfo | 3 individuos [código] |
| Fotos «no rana» con vector | 1.229: reptil 184, salamandra 186, otro animal 178, insecto 27, persona 179, objeto 193, fondo 55, otro 227 [BD] |
| Evolución | v3: 28 especies · v4: 31 · v5: 56 [BD] |

## 13. Rendimiento medido

### 13.1 Identificación (centroide: coseno contra la media L2 de train, sin entrenar)

| Test v5, 56 especies, centroides globales, 864 fotos [CALC] | Valor |
|---|---|
| Top-1 | **62,85 %** (IC 95 % ≈ ±3,2 pp [STAT]) |
| Top-3 | **86,11 %** |
| Top-5 | 91,09 % |
| 1-NN contra train (referencia) | 61,34 % |
| kNN k=5 ponderado (el del Simulador) | 63,66 % |

Lectura: centroide ≈ kNN (~1 punto de diferencia) con un archivo mucho más pequeño (1 vector por especie). El salto top-1 → top-3 (+23 pp) justifica mostrar tres candidatas.

**Por qué baja con más especies** (validación, «acierto entre aceptadas») [BD]:

| Lote | Especies | Fotos val | Acierto entre aceptadas | KAR |
|---|---|---|---|---|
| 1 | 5 | 81 | 87,3 % | 97,5 % |
| 2 | 18 | 298 | 78,2 % | 98,7 % |
| 3 | 26 | 396 | 76,0 % | 97,7 % |
| 5–8 | 28 | 440 | 74,3 % | 98,0 % |
| 9 | 31 | 484 | 68,6 % | 98,1 % |
| 10–13 | 56 | 861 | **64,4 %** | 97,8 % |

Cascada lote 13 (val): 842 llegan a especie, 7 a género, 10 a familia, 2 rechazadas. **Advertencia:** la validación cambia entre lotes; no es un experimento controlado. La tendencia (más especies → menos acierto) es real, pero no se puede atribuir un número exacto a cada especie añadida.

**Paquete real de Sinú (33 especies, 493 fotos test)** [CALC]:

| Centroides | Top-1 | Top-3 |
|---|---|---|
| Globales | **73,83 %** (±3,9 pp [STAT]) | **90,67 %** |
| Regionales (63 de 256 filas con vector propio) | 70,99 % (±4,0 pp [STAT]) | 88,84 % |

- El centroide regional **no mejoró** (−2,8 pp). Con n=493 la diferencia cae **dentro del ruido** [STAT, aproximación normal sin parear]: no se puede afirmar que sea peor, solo que no mejora.
- Paquete chico frente al global de 56: 62,85 → 73,83 % (+11 pp), pero **no es la misma muestra** (493 fotos de 33 especies frente a 864 de 56). Indicativo. Esta cifra confirma en otra escala la de la Parte A (+11,8 pp, EXP-015).

**Especies fáciles y difíciles** (top-1, test, lote 13) [CALC]:
- 100 %: *Andinobates opisthomelas*, *Phyllomedusa venusta*, *Pseudis paradoxa*, *Leptodactylus savagei*. 90–95 %: *Ceratophrys calcarata*, *A. fulguritus*, *Lithodytes lineatus*, *Hyloscirtus larinopygion*.
- Peores: *Boana pugnax* 25 %, *Pristimantis permixtus* 26 %, *Rhinella humboldti* 27 %, *Leptodactylus fragilis* 32 %, *L. poecilochilus* 36 %, *P. paisa* 37,5 %, *Dendropsophus columbianus* 40 % (top-3 100 %), *Rhinella marina* 41 % (top-3 94 %), *P. achatinus* 47 % (top-3 100 %).
- Correlaciones (n=56): top-1 frente a **coseno al centroide vecino −0,62** (cuanto más cerca la vecina, peor); frente a dispersión interna −0,26; frente a nº de individuos −0,05 (con ≥38 individuos, más fotos no ayudó).

**Pares que más se confunden** (top-1 equivocado, test) [CALC]: *D. bogerti → D. microcephalus* 8 · *R. marina → R. horribilis* 7 (al revés 4) · *Hyalinobatrachium tatayoi → Espadarana prosoblepon* 5 · *D. columbianus → D. bogerti* 5 · *Craugastor metriosistus → C. raniformis* 5 · *Osteocephalus taurinus → Trachycephalus macrotis* 4 · *P. taeniatus ↔ P. penelopus* 4 y 3 · *Nymphargus grandisonae → E. prosoblepon* 4 · *R. humboldti → R. beebei* 4. Patrón: casi siempre el **mismo género**.

**Geometría de los centroides (lote 13)** [BD]: dispersión media 0,275 (0,100–0,408); Weibull medio β 2,17 / η 0,311 / radio 0,522 / τ 0,478 (cobertura 95 %); coseno medio al vecino 0,833, máximo 0,980 (*R. horribilis–R. marina*); pares con coseno ≥0,90: 15, ≥0,85: 30; supercentroides: 30 géneros (τ 0,455) y 12 familias (τ 0,366). Más dispersas: *Pseudopaludicola pusilla* 0,408, *P. penelopus* 0,387, *Scinax rostratus* 0,380, *P. paisa* 0,375, *Elachistocleis panamensis* 0,373, *Engystomops pustulosus* 0,360.

**Referencia histórica, no citar como rendimiento actual** [HIST]: 97,19 % de accuracy en validación con 11 clases (10 especies + `no_frog`, 961 fotos) y fine-tuning. El entrenador fue eliminado. Metas de diseño (`CONTEX.TXT`): ≥90 % distinguibles, ≥80 % crípticas, ≥85 % en las 10 más comunes del Valle de Aburrá. Con 56 especies el top-1 (62,9 %) no las alcanza; el top-3 (86,1 %) sí supera 85 %.

### 13.2 Rechazo de lo desconocido (Open Set)

τ se calibra para KAR 95 % con val y se mide en test. FAR = desconocidas que se cuelan.

| Subregión | Método | KAR | FAR | AUROC |
|---|---|---|---|---|
| Sabanas, 20 esp. [BD] | Mahalanobis | 96,2 % | 94,2 % | 0,576 |
| | **Coseno + Weibull** | 93,0 % | **61,2 %** | **0,826** |
| Sinú, 33 esp. [BD] | Mahalanobis | 95,3 % | 96,7 % | 0,578 |
| | **Coseno + Weibull** | 95,3 % | **91,6 %** | **0,665** |

Mejora de AUROC: +0,25 (Sabanas) y +0,09 (Sinú). Mahalanobis en 512 dimensiones con pocas fotos por especie casi no separa (0,55–0,68 en las 9 subregiones de Antioquia, FAR 87–94 %). Tamaño: ANOS v1 de 10 especies 2,14 MB; ANOS v2 de 33 especies 136 KB (la covarianza 512² es lo que pesa). **El FAR de Sinú sigue en 91,6 %: el rechazo de ranas ajenas sigue siendo débil.** Sabanas se midió con 20 especies y 188 desconocidas; Sinú con 33 y 752.

**«No es una rana»** [BD]:

| Calibración | FAR no-rana | AUROC no-rana |
|---|---|---|
| Sinú, coseno+Weibull | 6,67 % | 0,987 |
| Sinú, Mahalanobis | 5,29 % | 0,992 |
| Global 56, coseno+Weibull | 4,64 % | 0,989 |
| Global 56, Mahalanobis | 4,56 % | 0,992 |

Aquí Mahalanobis es ligeramente mejor: rana frente a no-rana es fácil (AUROC >0,98); rana frente a otra rana no. Qué se cuela (Sinú, 82 de 1.229): reptil 43/184 (23 %), salamandra 28/186 (15 %), persona 5/179, otro 4/227, otro animal 2/178, insecto 0/27, objeto 0/193, fondo 0/55.

**Curva de operación** (Sinú, coseno+Weibull, 493 conocidas, 752 desconocidas) [BD]:

| KAR objetivo | τ | KAR medido | FAR ranas ajenas | FAR no-rana |
|---|---|---|---|---|
| 80 % | 0,656 | 78,5 % | 61,3 % | 0,65 % |
| 85 % | 0,704 | 81,5 % | 68,2 % | 1,06 % |
| 90 % | 0,756 | 86,4 % | 75,1 % | 1,95 % |
| **95 %** | **0,916 (validado)** | 95,3 % | 91,6 % | 6,67 % |
| 97,5 % | 1,091 | 98,8 % | 97,6 % | 26,4 % |
| 99 % | 1,130 | 99,2 % | 98,4 % | 33,1 % |

Cada +5 pp de KAR cuestan ~+16 pp de FAR entre 90 y 95 %. El punto 95 % es una decisión de producto, no un óptimo. Las cifras se movieron con cada lote (Mahalanobis: Sabanas 0,575 → 0,576 → 0,559; Valle de Aburrá 0,591; Oriente 0,555; Suroeste 0,634; Occidente 0,684; Urabá 0,604): el problema es la métrica, no el tamaño del paquete.

### 13.3 Clústeres (grupos de 2 a 12 especies que no se separan)

- Los decide **una persona** (herpetólogo); el sistema solo sugiere. Se guardan en `dataset.cluster` y los aceptados viajan en el paquete (`clusters` en `package.sqlite`).
- **Cómo se sugieren:** pares con coseno ≥0,90 o confundidos en ≥8 % de sus fotos de val (máx. 5 pares por lote). A cada par se le entrena un adaptador de dos prototipos con ArcFace (margen 0,35, escala 30, 20 épocas, lr 0,01, semilla fija) sobre train y se mide en val contra el centroide simple.
- **Para qué sirven:** (a) en vez de un top-1 dudoso, la app dice «grupo X, requiere un detalle» y muestra la clave dicotómica (`clave.js`); (b) separan confusión real de error; (c) documentan la decisión científica.
- **Estado real:** 0 clústeres decididos; 60 filas de `cluster_sugerido` (5 pares × 12 lotes). No hay clústeres en producción ni medición en teléfono.

| Par (lote 13, val) | Coseno | n val | Antes → después de ArcFace |
|---|---|---|---|
| *R. horribilis – R. marina* | 0,980 | 29 | 86,2 → **65,5 %** (−20,7) |
| *R. humboldti – R. beebei* | 0,966 | 31 | 22,6 → **38,7 %** (+16,1) |
| *D. bogerti – D. columbianus* | 0,963 | 50 | 72,0 → 76,0 % (+4,0) |
| *B. pugnax – B. rosenbergi* | 0,963 | 28 | 85,7 → 82,1 % (−3,6) |
| *H. tatayoi – N. grandisonae* | 0,961 | 29 | 79,3 → 82,8 % (+3,5) |

Promedio: **69,2 → 69,0 %** (≈0). Entre lotes: de −4,1 a +2,7 pp. Con n=28–50 por par el error de muestreo es de ±12 a ±16 pp [STAT]: los cambios de ±4 pp son ruido y los de ±16 a ±21 apenas lo superan. Conclusión: el adaptador sirve para **marcar** el par, no para corregirlo; el clúster es agrupación por decisión humana. *R. humboldti–R. beebei* tiene 22,6 % «antes» con dos clases (peor que el azar): hipótesis a verificar, etiquetas cruzadas o poblaciones de fotos distintas en train y val.

### 13.4 Morfos, contexto y paquetes

- **Morfos** (sub-centroides por variante de patrón o color; ≥3 individuos para vector propio; nunca se mezclan morfos distintos): **0 declarados, 0 etiquetas, sin ninguna medición**. Experimento propuesto: declarar morfos en 3–5 especies dispersas y comparar top-1 antes/después con la misma versión del dataset. La dispersión explica poco el error (−0,26); la cercanía a la vecina explica más (−0,62): los morfos ayudan donde una especie ocupa varios grupos de fotos; donde el problema es el parecido entre especies corresponde un clúster.
- **Contexto (altitud, zona, clima):** los priors solo reordenan candidatas, nunca deciden (`AnuraIdentifier.kt`). Prior de zona P(s|z) = (N(s,z)+α)/(N(z)+α·K); peso de zona 0,75 y de clima 0,2 en el paquete de ejemplo. Especies nuevas quedan con `p_unobserved ≈ 6×10⁻⁴` y bajan en la lista. **No hay cifra de la mejora que aportan** (solo pruebas funcionales: 90 filas copiadas idénticas).
- **Paquetes:** Valle de Aburrá (id 19, 10 especies, ANOS v1, τ 32,68, publicado) · Sinú (id 28 v4, 33 especies, ANOS v2, τ 0,9158, publicado) · subregiones 2–9 de Antioquia (ANOS v1, aprobados sin publicar). Tiempos [DOC]: GBIF ≈7 s/especie; iNaturalist 5–10 min/especie (40 individuos nuevos, 3 fotos/individuo); embeddings ≈280 ms/foto (GPU); centroides segundos; OSR coseno <1 s, Mahalanobis ≈2 s. Publicar exige 2 aprobaciones (científica y técnica) y un τ validado por una persona.

### 13.5 Qué mejora el proceso (con el dato que lo respalda)

| Palanca | Evidencia | Efecto medido |
|---|---|---|
| Paquete regional (menos especies) | Sinú 33 frente a global 56 | top-1 73,8 frente a 62,9 % (+11) [indicativo] |
| Mostrar top-3 | top-1 62,9 → top-3 86,1 | +23 pp |
| OSR coseno+Weibull en vez de Mahalanobis | AUROC 0,58 → 0,83 (Sabanas), 0,58 → 0,67 (Sinú) | fuerte para ranas ajenas; neutro/peor para no-rana (FAR +1,4 pp) |
| Subir KAR | 90 → 95 % | FAR +16 pp: decisión de producto |
| Piso de 80 fotos / 10 individuos | las 56 tienen ≥85 fotos | acierto no correlaciona con nº de individuos (−0,05) |
| Centroide regional | Sinú 70,99 frente a 73,83 | no mejoró (dentro del ruido) |
| Adaptador ArcFace en clústeres | 5 pares, 69,2 → 69,0 | ≈0, inestable |
| Morfos / clústeres aceptados / priors | 0 declarados / sin medición | sin medición |

Hipótesis de mejora detectadas en el código y datos: (1) los clústeres sugeridos ignoran el par más confundido: hay 15 pares con coseno ≥0,90 pero se sugieren 5 (`MAX_PARES`) por coseno; *D. bogerti–D. microcephalus* (8 errores, coseno 0,89) queda fuera; (2) la evaluación formal nunca se corrió: ejecutar «Evaluar ahora» por paquete publicado y guardar la línea base; (3) τ se fija en val y el KAR de test sale distinto (80 → 78,5 %; 95 → 95,3 %): reportarlo; (4) revisar la partición de *R. humboldti/beebei*; (5) las 56 mezcladas bajan el acierto: el paquete por subregión lo resuelve; (6) 13 lotes con la misma versión dan resultados idénticos: el cálculo es determinista, recalcular menos; (7) para bajar el FAR de ranas ajenas (61–92 %) hace falta más desconocidas reales y/o un criterio por especie o género en vez de un τ global.

### 13.6 Lo que NO existe todavía (para no citar de más)
- Evaluación oficial (`dataset.evaluacion`): vacía.
- Morfos y clústeres aceptados: 0.
- Medición en teléfono (latencia, consumo, precisión en campo): sin datos; los RNF dicen <15 % de RAM, sin medición.
- Efecto aislado de altitud, zona, clima y pesos sobre top-1.
- Las pruebas de `_pruebas/` usan datos **sintéticos** (base `anura_osr`): sus «top-1 = 100 %» y «AUROC >0,99» son pruebas de código, no rendimiento.
- Comparaciones entre lotes no controladas.

## 14. Simulaciones y datos de prueba (NO son mediciones)

> Estas cifras rellenan vacíos para esbozar gráficos y planear. Cada una lleva su supuesto. **No se citan como resultado** ni se mezclan con las tablas de arriba. Si el usuario las quiere en el PDF, irán con la marca «SIMULACIÓN».

| # | Qué se estima | Valor [SIM] | Supuesto y cómo se calculó |
|---|---|---|---|
| S1 | Latencia del encoder en el Redmi Note 13 Pro+ (4 hilos) | **≈0,3–0,6 s** | Medido en CPU de escritorio: 154 ms (4 hilos). Supuesto del móvil: 2–4 veces más lento. Factor **no medido** |
| S2 | Latencia con 1 hilo en el móvil | ≈0,8–1,6 s | Medido 403 ms en escritorio, mismo factor 2–4 |
| S3 | Cómputo de BioCLIP 2.5 frente a BioCLIP 1 | ≈9–10 veces más operaciones | Referencia de memoria (no verificada en las fuentes): ViT-B/16 ≈17,6 GMACs; ViT-H/14 ≈167 GMACs. FLOPs reales de BioCLIP: dato pendiente |
| S4 | Top-1 con BioCLIP 2.5 sobre las 56 especies de Anura | conservador 65,9 % · medio 68,9 % · optimista 72,9 % | Partiendo de 62,85 % y sumando +3, +6 y +10 pp **supuestos**. En benchmarks zero-shot de 10 tareas la media sube 37,6 → 61,3 (+23,7), pero con centroides sobre ranas parecidas se espera menos. Debe medirse |
| S5 | Tamaño de un paquete regional con embeddings de 1024-d | ≈2 veces el actual | El paquete de Antioquia (2.073 vectores) a 512 fp32 ≈4,25 MB de vectores; a 1024 ≈8,5 MB. Cálculo simple, sin sobrecarga de SQLite |
| S6 | Tamaño del encoder visual de 2.5 en fp16 | ≈1,0–1,3 GB (solo torre de imagen) | Modelo completo fp16 ≈1,97 GB [CALC en las notas de investigación]; la torre visual es una parte; proporción no medida |

**Cálculos estadísticos reales [STAT]** (no son simulación): intervalo del 95 % con aproximación normal, p ± 1,96·√(p(1−p)/n): top-1 56 especies ±3,2 pp (n=864); Sinú global ±3,9 pp y regional ±4,0 pp (n=493); un par de clúster con n=29 y p=0,86 ±12,6 pp.

## 15. Contradicciones nuevas entre la Parte A y la Parte B (por resolver)

1. **¿El encoder tiene fine-tuning?** La Parte A (§7.5, Fase 4) dice que `219e860e…` es el encoder **fine-tuned** (`bioclip_anura_mejor.pt`) y que por eso rechazaba mejor (FAR 75,7 frente a 84,2 %). La Parte B dice «BioCLIP v1 congelado, sin fine-tuning». **Decisión del usuario (2026-10-15): el encoder se usa congelado** (análisis en `guia.md` §28). La nota de la Parte A queda como dato histórico; si `219e860e…` corresponde o no al checkpoint ajustado, sigue sin verificarse.
2. **28, 41, 43 o 56 especies:** 28 (prototipo), 41 (fases), 43 (producción 29 sep), 56 (v5 de la BD). Para la guía se cita 56 con su versión.
3. **Prior geográfico:** sigue sin reconciliar +24,9 pp (EXP-007) frente a +9,6 pp (paquete real); la Parte B no lo mide.
4. **Rechazo:** Parte A, FAR 52–94 %; Parte B, FAR de ranas ajenas 61–92 %. Coinciden en el diagnóstico: el rechazo de ranas ajenas no está resuelto.
5. **Cifra «97 %»:** solo en el contexto histórico de 11 clases (§13.1).
