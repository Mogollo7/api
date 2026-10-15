# Fine-tuning vs encoder congelado, calidad de etiquetas y escasez de imágenes (notas para guía estudiantil)

Nota de método: ~17 llamadas; se leyeron abstracts de arXiv y los textos HTML de BioCLIP y BioCLIP 2 (vía resumen de WebFetch, que cortó ~1 k y ~26 k caracteres finales). Todo lo no cubierto por una fuente va en Gaps como [SIN FUENTE].

## 1. Fine-tuning vs linear probing vs LP-FT vs WiSE-FT vs adapters; ID/OOD; olvido; BioCLIP

### Takeaway
El fine-tuning completo sube la precisión en distribución (ID) pero puede bajarla fuera de distribución (OOD) porque distorsiona las features preentrenadas; con pocas imágenes por clase, un encoder congelado más clasificador simple (centroides/linear probe) fue la opción más fuerte en los trabajos con BioCLIP encontrados. Los autores de BioCLIP evalúan zero-shot y few-shot con embeddings congelados, sin fine-tuning.

### Cited Findings
- Kumar et al. 2022: en 10 datasets con cambio de distribución, el fine-tuning rindió ~2% más ID pero ~7% menos OOD que el linear probing; ocurre cuando las features preentrenadas son buenas y el cambio es grande. — [arXiv 2202.10054](https://arxiv.org/abs/2202.10054)
- Mecanismo (análisis teórico en redes lineales de dos capas): con cabeza inicializada al azar o fija, el error OOD es alto porque, mientras se aprende la cabeza, las capas inferiores cambian y distorsionan las features preentrenadas. — [arXiv 2202.10054](https://arxiv.org/abs/2202.10054)
- LP-FT (primero linear probe, luego fine-tuning completo): ~1% mejor ID y ~10% mejor OOD que el fine-tuning completo, y supera también al linear probe simple en esos datasets. — [arXiv 2202.10054](https://arxiv.org/abs/2202.10054)
- WiSE-FT (Wortsman et al.): promedia en espacio de pesos el modelo zero-shot y el fine-tuned; en ImageNet y 5 shifts derivados sube OOD 4-6 pp sobre trabajo previo y ImageNet +1.6 pp; en 7 datasets de transferencia gana 0.8-3.3 pp sobre fine-tuning estándar; sin costo extra en entrenamiento ni inferencia. — [arXiv 2109.01903](https://arxiv.org/abs/2109.01903)
- Otro resumen del mismo método: fine-tuning estándar sube la precisión en la distribución objetivo pero suele reducir la robustez a shifts (CLIP); el ensamble mejora OOD 2-10 pp y ID casi 1 pp frente al fine-tuning estándar (cifras de resumen de búsqueda; difieren del abstract, usar las del abstract). — [búsqueda sobre Wortsman et al.](https://api.deepai.org/publication/robust-fine-tuning-of-zero-shot-models)
- Olvido en CLIP: un estudio reporta que solo los modelos LAION-2B y OpenAI sufren degradación OOD significativa tras fine-tuning y concluye que el sobreajuste no es la causa principal del olvido catastrófico. — [arXiv 2410.21582](https://arxiv.org/pdf/2410.21582)
- LoRA "aprende menos y olvida menos" (en LLMs, no CLIP): en configuraciones de rango bajo típicas rinde bastante menos que fine-tuning completo, pero conserva mejor el desempeño fuera del dominio; el fine-tuning completo aprende perturbaciones de rango 10-100 veces mayor. — [arXiv 2405.09673](https://arxiv.org/html/2405.09673v2)
- Existen métodos de LoRA selectivo aplicados a CLIP para limitar el olvido. — [arXiv 2501.15377](https://arxiv.org/pdf/2501.15377)
- BioCLIP inicializa desde CLIP de OpenAI y se preentrena continuamente en TreeOfLife-10M; supera baselines en clasificación fina de biología en 16-17% absoluto. — [arXiv 2311.18803](https://arxiv.org/abs/2311.18803)
- Protocolo few-shot de BioCLIP: sigue SimpleShot; k ejemplos por clase, embeddings del encoder preentrenado, promedio por clase (centroide), resta de media y normalización L2, asignación al centroide más cercano; 5 repeticiones con distintas semillas. No es linear probe ni fine-tuning. — [BioCLIP HTML](https://arxiv.org/html/2311.18803v3)
- Zero-shot de BioCLIP: mismo procedimiento que CLIP; BioCLIP usa nombres taxonómicos+comunes. — [BioCLIP HTML](https://arxiv.org/html/2311.18803v3)
- Rare Species: zero-shot BioCLIP 38.0 vs CLIP 31.8; 1-shot 44.9 vs 28.5; 5-shot 65.7 vs 46.0. Promedio entre tareas: zero-shot 39.4, 1-shot 50.3, 5-shot 68.8. — [BioCLIP HTML](https://arxiv.org/html/2311.18803v3) (el texto dice "9.1% mejor 1-shot que zero-shot", que no coincide con la tabla 50.3 vs 39.4; discrepancia interna).
- BioCLIP 2, few-shot medio entre tareas: 1-shot 64.1, 5-shot 78.3 (BioCLIP 50.0/68.5; DINOv3 44.8/61.8; SigLIP 43.9/61.9). Insects 1-shot 74.6, 5-shot 89.3. — [arXiv 2505.23883 HTML](https://arxiv.org/html/2505.23883)
- BioCLIP 2 en tareas no-especie: modelos congelados, se extraen embeddings y se entrena un clasificador downstream (p. ej. SVC). — [arXiv 2505.23883 HTML](https://arxiv.org/html/2505.23883)
- Polillas (101 especies, 110 imágenes objetivo/especie): linear probe sobre BioCLIP 2 congelado fue la opción más efectiva con pocos datos etiquetados (88.3% con 0% de datos objetivo; 89.4% con 5%; 91.6% con 50%); BioCLIP congelado 71.2/76.6/85.8; ConvNeXt-tiny parcialmente descongelado 59.4/72.8/85.4; los autores sugieren guardar los pocos datos etiquetados para evaluación. No probaron fine-tuning completo de BioCLIP 2. — [arXiv 2508.20089](https://arxiv.org/html/2508.20089v1)
- Fine-tuning de BioCLIP sí aportó, modestamente, en zero-shot con descripciones de rasgos: Insects 34.8% a 39.9% (con fine-tuning a nivel especie 39.6%). — [arXiv 2604.01619](https://arxiv.org/pdf/2604.01619) (visto solo vía snippet de búsqueda)
- Fine-tuning de la última proyección visual de CLIP es una variante parcial reportada como mejor que otros baselines few-shot generales (no biología). — [arXiv 2410.05270](https://arxiv.org/html/2410.05270v2)
- En un estudio con BiomedCLIP (ultrasonido) el fine-tuning completo a menudo quedó por debajo de linear probe/few-shot, y el ranking cambió entre datasets. — [arXiv 2605.02126](https://arxiv.org/pdf/2605.02126) (solo snippet)
- Few-shot clásico: un baseline simple con fine-tuning ordinario rinde competitivamente, también cross-domain. — [Chen et al., arXiv 1904.04232](https://arxiv.org/abs/1904.04232)

### Inferences
- "Contrato de embeddings": al congelar el encoder, los vectores de referencia ya calculados siguen siendo válidos y se pueden añadir clases/prototipos nuevos sin reentrenar; es una consecuencia lógica del protocolo de centroides de BioCLIP (clasificador = promedios de embeddings fijos), no una afirmación de ninguna fuente. Tras fine-tuning cambian los pesos y por tanto el espacio, así que los vectores guardados dejarían de ser comparables (consecuencia lógica; ver Gaps).
- Con muy pocas imágenes por clase y clases casi idénticas, la evidencia de polillas sugiere congelar y dedicar las imágenes a prototipos y evaluación.

### Gaps
- Ilharco et al. (p. ej. task vectors / patching) no consultado: [SIN FUENTE].
- Artículo "Fine-tuning can distort pretrained features" = Kumar et al. (arriba); no se leyó el texto completo, solo abstract.
- Recomendación explícita de los autores de BioCLIP de "no hacer fine-tuning": no encontrada textualmente; solo el protocolo sin fine-tuning y la model card (según búsqueda) que menciona kNN few-shot sin fine-tuning. [SIN FUENTE] como recomendación literal.
- Medición directa de que el cambio de pesos invalida embeddings viejos: [SIN FUENTE].
- Efecto de fine-tuning en clases casi idénticas (fine-grained, p. ej. Thysanoptera): [SIN FUENTE].
- BioCLIP 2: apéndice H (protocolo few-shot detallado) no leído.

## 2. Calidad de etiquetas

### Takeaway
Los test sets de referencia tienen en promedio al menos 3.3% de errores y ImageNet val al menos 6%; confident learning (cleanlab) los detecta con probabilidades fuera de muestra. En biología, la precisión de "research grade" de iNaturalist varía mucho por taxón (insectos peor).

### Cited Findings
- Northcutt et al. 2021 (Pervasive Label Errors): promedio de al menos 3.3% de errores en 10 test sets; en ImageNet validation, al menos 6%. — [arXiv 2103.14749](https://arxiv.org/abs/2103.14749)
- Confident learning: caracteriza errores de etiqueta, poda, estima ruido con umbrales probabilísticos y rankea ejemplos; asume ruido dependiente de clase; consistente bajo condiciones; supera 7 métodos en CIFAR; estima 645 imágenes "missile" etiquetadas como "projectile" en ImageNet; limpiar antes de entrenar mejora moderadamente la precisión; implementado en cleanlab de código abierto. — [arXiv 1911.00068](https://arxiv.org/abs/1911.00068)
- iNaturalist (post informal de staff, 2019): ~85% de observaciones Research Grade correctamente identificadas en un experimento ad hoc; 91% en aves y 65% en insectos; el autor señala problemas metodológicos. — [foro iNaturalist](https://forum.inaturalist.org/t/identification-quality-on-inaturalist/7507) (vía snippet de búsqueda)
- Para liquenes/hongos/insectos pequeños y difíciles taxonómicamente la identificación por foto suele ser errónea o insuficiente (McMullin & Allen). — [BISS abstract](https://biss.pensoft.net/article_preview.php?id=95689)
- BioCLIP 2 recomienda etiquetas taxonómicas jerárquicas con objetivo contrastivo en vez de one-hot cross-entropy (ablación). — [arXiv 2505.23883 HTML](https://arxiv.org/html/2505.23883)

### Inferences
- Para insectos pequeños, el ruido de etiquetas fuente (iNat/GBIF) probablemente sea mayor que el promedio; conviene revisión experta del set de referencia y de evaluación.

### Gaps
- Cohen's kappa / acuerdo entre anotadores, guías de anotación, experto vs crowd, versionado taxonómico/sinónimos, opción "no determinable", etiquetas jerárquicas especie/estadio/sexo como práctica: [SIN FUENTE] (no buscados).
- Docs de cleanlab: la URL probada dio 404; requisito de probabilidades out-of-sample por validación cruzada solo [SIN FUENTE] salvo el abstract del paper.
- Efecto cuantitativo del ruido de etiquetas en entrenamiento: [SIN FUENTE] más allá de lo anterior.
- Cifras v0.2 del experimento de exactitud de iNaturalist: no recuperadas.

## 3. Variación intra-clase por estadio y sexo

### Takeaway
BioCLIP 2 reporta que la variación intra-especie (estadios, sexos) se preserva y se separa en subespacios ortogonales a las diferencias entre especies, lo que respalda tratar estadio/sexo como atributos y usar prototipos por subgrupo.

### Cited Findings
- Abstract: "las variaciones intra-especie (p. ej. estadios y sexos) se preservan" y "se separan mejor en subespacios ortogonales" a las distinciones inter-especie; propiedad emergente con más datos; con análisis formal para supervisión jerárquica y objetivo contrastivo. — [arXiv 2505.23883](https://arxiv.org/abs/2505.23883)
- Evaluación: estadio vía NeWT, sexo vía NABirds; tareas de alineación (clasificador entrenado en una variante reconoce la otra) y diferenciación (distinguir variantes); ambas mejoran con la escala de datos. — [arXiv 2505.23883 HTML](https://arxiv.org/html/2505.23883)
- Limitación declarada: la separación por ortogonalidad no está probada formalmente; TreeOfLife-200M es de cola larga. — [arXiv 2505.23883 HTML](https://arxiv.org/html/2505.23883)

### Inferences
- Un solo prototipo por especie promedia variantes muy distintas (larva vs adulto, macho vs hembra) y queda lejos de cada una; k prototipos por estadio/sexo evitan esto (inferencia, no probada en una fuente).

### Gaps
- Evidencia directa de fallo de prototipo único en especies polimórficas/dimórficas, y práctica de etiquetado/split por atributo: [SIN FUENTE].

## 4. Opciones ante pocas imágenes

### Takeaway
Lo mejor documentado aquí es few-shot con embeddings congelados (SimpleShot/centroides/kNN) y mezclas/copy-paste como regularizadores; las imágenes sintéticas por difusión son poco fiables para especies finas.

### Cited Findings
- SimpleShot: vecino más cercano con resta de media + normalización L2 sobre features, sin meta-learning, supera resultados previos en 3 de 5 configuraciones de miniImageNet. — [arXiv 1911.04623](https://arxiv.org/abs/1911.04623)
- CutMix: pega parches entre imágenes con mezcla de etiquetas proporcional al área; supera consistentemente otras augmentaciones en CIFAR/ImageNet, mejora robustez y transferencia. — [arXiv 1905.04899](https://arxiv.org/abs/1905.04899)
- Copy-Paste: pegar objetos en posiciones aleatorias es suficiente; +10 AP con 10% de datos y +5 AP con todos los datos (COCO); aditivo con pseudo-etiquetado/self-training; el desglose por tamaño no se encontró. — [Ghiasi et al., arXiv 2012.07177](https://ar5iv.labs.arxiv.org/html/2012.07177)
- Class-Balanced Loss: peso por "número efectivo" (1-β^n)/(1-β); mejoras en CIFAR, ImageNet e iNaturalist de cola larga (magnitud no verificada). — [arXiv 1901.05555](https://arxiv.org/abs/1901.05555)
- Sintético: imágenes de Stable Diffusion sobre 50 clases de iNaturalist se clasificaron bien solo ~14% (26% con su método). — [arXiv 2303.17155](https://arxiv.org/pdf/2303.17155)
- Modelos de difusión organizan representaciones por etiquetas gruesas ("ave", "pez") más que por nombre taxonómico; mitigaciones (TaxaDiffusion, TaxaAdapter) mejoran fidelidad de generación, sin evidencia hallada de mejora en clasificadores. — [arXiv 2603.26128](https://arxiv.org/html/2603.26128v1), [arXiv 2506.01923](https://arxiv.org/abs/2506.01923v2)
- Datos sintéticos de modelos text-to-image: ayudan en zero/few-shot pero con limitaciones; requieren estrategias específicas. — [arXiv 2210.07574](https://arxiv.org/abs/2210.07574)
- Distilación de BioCLIP 2 hacia un modelo pequeño mejoró ~3.6% en promedio con datos objetivo escasos. — [arXiv 2508.20089](https://arxiv.org/html/2508.20089v1)

### Inferences
- La augmentación (geométrica/fotométrica/mezcla) regulariza pero no crea morfología nueva; el aporte de datos reales nuevos (iNat/GBIF) no sustituible por transformaciones (sin fuente directa).

### Gaps
- Augmentation clásica, Mixup, RandomErasing/CoarseDropout, TTA, sqrt-dampening, focal loss, pseudo-etiquetado semi-supervisado, active learning, fuentes públicas (iNaturalist, GBIF, Bugwood, EOL), transferencia desde taxones afines, rollup jerárquico: [SIN FUENTE] (no buscados).
- Evidencia a favor de sintéticos en especies finas con clasificador entrenado: no hallada.
