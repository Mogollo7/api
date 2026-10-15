# BioCLIP v1: qué es y cómo funciona

## 1. Autoría, paper, venue, licencia, repo

### Takeaway
BioCLIP (v1) es un modelo tipo CLIP para biología, del Imageomics Institute (Ohio State y colaboradores), publicado en CVPR 2024 (oral) como arXiv:2311.18803. Pesos con licencia MIT en Hugging Face `imageomics/bioclip`.

### Cited Findings
- Título: "BioCLIP: A Vision Foundation Model for the Tree of Life". Autores: Samuel Stevens, Jiaman Wu, Matthew J Thompson, Elizabeth G Campolongo, Chan Hee Song, David Edward Carlyn, Li Dong, Wasila M Dahdul, Charles Stewart, Tanya Berger-Wolf, Wei-Lun Chao, Yu Su — [arXiv abs](https://arxiv.org/abs/2311.18803)
- Venue: CVPR 2024 (oral). arXiv:2311.18803 [cs.CV]; v1 30-nov-2023, v3 (camera-ready) 14-may-2024 — [arXiv abs](https://arxiv.org/abs/2311.18803)
- Licencia del modelo: MIT — [HF model card](https://huggingface.co/imageomics/bioclip)
- Repo HF: `imageomics/bioclip`; código en GitHub Imageomics/bioclip — [HF](https://huggingface.co/imageomics/bioclip), [GitHub](https://github.com/Imageomics/bioclip)
- Abstract: TreeOfLife-10M descrito como "el mayor y más diverso dataset de imágenes de biología listo para ML"; BioCLIP supera baselines en 16%-17% absoluto en benchmarks de clasificación fina; las representaciones siguen la jerarquía del árbol de la vida, lo que los autores asocian con su generalización — [arXiv abs](https://arxiv.org/abs/2311.18803)
- Existe pybioclip (paquete) y una demo en HF como formas alternativas de uso — [GitHub](https://github.com/Imageomics/bioclip)

### Inferences
- "Imageomics Institute / Ohio State": la afiliación institucional no aparece en las páginas que leí (solo autores); es conocimiento previo, no verificado aquí. Tanya Berger-Wolf, Wei-Lun Chao y Yu Su son profesores de OSU (no verificado en estas fuentes).

### Gaps
- Afiliaciones exactas de autores no extraídas de la fuente.

## 2. Arquitectura

### Takeaway
ViT-B/16 como codificador de imagen y un transformer causal de texto (77 tokens), inicializados desde CLIP de OpenAI y entrenados con el objetivo contrastivo CLIP. Embedding de 512 dimensiones (verificado en la config).

### Cited Findings
- Imagen: ViT-B/16, inicializado desde el checkpoint OpenAI CLIP ViT-B/16; texto: transformer autoregresivo (causal) de 77 tokens — [HF](https://huggingface.co/imageomics/bioclip), [paper HTML](https://arxiv.org/html/2311.18803v3)
- `open_clip_config.json`: embed_dim 512; visión: image_size 224, 12 capas, width 768, patch 16; texto: context_length 77, vocab 49,408, width 512, 8 heads, 12 capas; mean (0.48145466, 0.4578275, 0.40821073), std (0.26862954, 0.26130258, 0.27577711) — [open_clip_config.json](https://huggingface.co/imageomics/bioclip/raw/main/open_clip_config.json)
- Entrenamiento: 100 epochs, cosine, batch global 32,768, 8 A100-80GB en 2 nodos (~4 días), LR máx 1e-4, 1,000 pasos warm-up, weight decay 0.2, entrada 224x224, fp16 — [HF](https://huggingface.co/imageomics/bioclip), [paper HTML](https://arxiv.org/html/2311.18803v3)
- Huella estimada: 132.71 kg CO2 eq — [HF](https://huggingface.co/imageomics/bioclip)

### Inferences
- Es la arquitectura de CLIP ViT-B/16 sin cambios; lo que cambia son los datos y el texto.

### Gaps
- Número de parámetros: no declarado en las fuentes que leí (no verificado). CLIP ViT-B/16 original ronda ~150M, pero eso es conocimiento previo, no verificado.

## 3. Datos de entrenamiento: TreeOfLife-10M

### Takeaway
~10.4M imágenes, 454,103 clases taxonómicas únicas, combinando iNat21, BIOSCAN-1M y EOL (curado); la diversidad viene sobre todo de EOL.

### Cited Findings
- Total ~10.4M imágenes, 454,103 taxones únicos ("over 10 million" / "454K") — [paper HTML](https://arxiv.org/html/2311.18803v3)
- iNat21: 2.7M imágenes, 10,000 clases; BIOSCAN-1M: 1.1M, 7,831 clases (98.6% etiquetadas solo a nivel de familia); EOL: 6.6M, 448,910 clases — [paper HTML](https://arxiv.org/html/2311.18803v3)
- Etiquetas agregadas desde iNaturalist, EOL e ITIS; ~84% de las imágenes tienen taxonomía completa; error de "hemihomónimos" en rangos altos afecta ~0.1-0.2% (Apéndice C) — [paper HTML](https://arxiv.org/html/2311.18803v3)
- Cada imagen tiene cadena taxonómica (7 rangos Linneanos, reino a especie) y nombre común cuando existe; iNat21 y BIOSCAN-1M no son redistribuibles (hay que construirlos con `treeoflife10m.md`); la parte EOL está en HF — [GitHub](https://github.com/Imageomics/bioclip)
- EOL consultado el 29-jul-2023 — [project page](https://imageomics.github.io/bioclip/)
- Sin datos de GPS ni estado de conservación en el entrenamiento — [HF](https://huggingface.co/imageomics/bioclip), [paper HTML](https://arxiv.org/html/2311.18803v3)

### Inferences
- Solo animales, plantas y hongos (según abstract); no bacterias, etc.

### Gaps
- Detalle del proceso de limpieza de EOL no extraído.

## 4. Idea clave: texto taxonómico

### Takeaway
En vez de una etiqueta plana, el texto de cada imagen incluye la cadena taxonómica completa; con entrenamiento "mixto" de varios formatos de texto. Esto NO equivale a que el modelo prediga automáticamente todo el árbol: es un clasificador contrastivo imagen-texto y la salida depende de los textos candidatos que se le den.

### Cited Findings
- Formatos de texto (Tabla 3), ejemplo con urraca: Common "black-billed magpie"; Scientific "Pica hudsonia"; Taxonomic "Animalia Chordata Aves Passeriformes Corvidae Pica hudsonia"; Sci+Com "Pica hudsonia with common name black-billed magpie"; Tax+Com = cadena taxonómica + "with common name ...". "Mixed" muestrea un tipo por imagen por paso; la entrada final usa plantilla tipo "a photo of Pica hudsonia." — [paper HTML](https://arxiv.org/html/2311.18803v3)
- Ablación (Rare Species, 1M muestras): Tax+Com train/test 30.4; Mixto 30.9; solo Scientific 22.3. Los autores afirman que el entrenamiento mixto mantiene rendimiento consistente entre tipos de texto de prueba — [paper HTML](https://arxiv.org/html/2311.18803v3)
- Datos: Mixto en ToL-1M 30.9 vs. iNat21 (2.7M) 21.3; ToL-10M completo 38.0 — [paper HTML](https://arxiv.org/html/2311.18803v3)
- Objetivo (ToL-1M, 1-shot/5-shot): cross-entropy 16.5/26.2; hierarchical CE 19.3/30.5; CLIP 44.7/63.8 — [paper HTML](https://arxiv.org/html/2311.18803v3)
- Zero-shot generalizado (App. H, 800 etiquetas): BioCLIP 26.0%, CLIP 23.0%, OpenCLIP 18.2% — [paper HTML](https://arxiv.org/html/2311.18803v3)
- Jerarquía: t-SNE sobre imágenes no vistas de validación de iNat21; BioCLIP separa órdenes y familias más claramente que CLIP. Es cualitativo, sin métrica cuantitativa — [paper HTML](https://arxiv.org/html/2311.18803v3)
- La model card dice que el texto incluye rangos desde reino hasta especie más nombre común cuando hay — [HF](https://huggingface.co/imageomics/bioclip)
- La conclusión indica que BioCLIP está entrenado fundamentalmente para clasificación; el GitHub no aclara si da predicciones por rango o solo a especie — [paper HTML](https://arxiv.org/html/2311.18803v3), [GitHub](https://github.com/Imageomics/bioclip)

### Inferences
- Cómo se usa en la práctica: se compara la imagen contra textos candidatos (p. ej. cadenas taxonómicas); para obtener "el árbol completo" hay que dar candidatos con cadenas completas, o evaluar por nivel con candidatos de ese nivel. El modelo no genera la taxonomía por sí mismo (no es generativo). Esto es inferencia a partir del diseño CLIP, no una frase de las fuentes.
- Frase correcta para el guía: "las representaciones reflejan la jerarquía (evidencia cualitativa)", no "identifica todo el árbol taxonómico".
- Ayuda a taxones no vistos porque el texto de una especie comparte prefijo (género, familia...) con parientes vistos (explicación de los autores en espíritu; la redacción exacta no fue verificada).

### Gaps
- Sin cifras de exactitud por rango taxonómico en las fuentes leídas.

## 5. Benchmarks reportados

### Takeaway
Zero-shot media 39.4 vs. 21.9 (CLIP) y 20.4 (OpenCLIP); few-shot con centroides, mejoras ~17 puntos.

### Cited Findings
- Zero-shot top-1 (%): Birds 525: CLIP 49.9 / OpenCLIP 54.7 / BioCLIP 72.1; Plankton 3.2 / 2.2 / 6.1; Insects 9.1 / 6.5 / 34.8; Insects 2 9.8 / 9.6 / 20.4; PlantNet 58.5 / 50.2 / 91.4; Fungi 10.2 / 5.7 / 40.7; PlantVillage 5.4 / 8.0 / 24.4; Med. Leaf 15.9 / 12.4 / 38.6; PlantDoc 26.1 / 25.8 / 28.4; Rare Species 31.8 / 29.8 / 38.0; Media 21.9 / 20.4 / 39.4 — [HF](https://huggingface.co/imageomics/bioclip), [paper HTML](https://arxiv.org/html/2311.18803v3)
- Few-shot (SimpleShot, clasificador de centroide más cercano, promedio de 5 semillas): 1-shot media BioCLIP 50.3 vs. CLIP 33.6 (+16.7), Rare Species 44.9; 5-shot media 68.8 vs. 51.5 (+17.3), Rare Species 65.7 — [paper HTML](https://arxiv.org/html/2311.18803v3)
- Rare Species: 400 especies listadas por IUCN (NT a EW), 30 imágenes c/u, excluidas del entrenamiento — [paper HTML](https://arxiv.org/html/2311.18803v3)
- Project page (otra tabla zero-shot): media BioCLIP 39.4, modelo solo iNat21 31.6, CLIP 21.4, OpenCLIP 20.6; afirma +17% a 20% absoluto vs. baselines — [project page](https://imageomics.github.io/bioclip/)

### Inferences
- Conflicto menor: CLIP media 21.9 (HF/paper) vs. 21.4 (project page); y OpenCLIP 20.4 vs. 20.6. Probablemente versiones/condiciones distintas de la tabla; no verificado. Usar la tabla del paper/HF.
- La ventaja sobre el baseline iNat21-only es ~7.8 puntos (39.4 vs 31.6), mucho menor que sobre CLIP.
- PlantDoc (28.4 vs 26.1) casi no mejora; Plankton sigue en 6.1: BioCLIP no es universal.

### Gaps
- Los números por dataset del baseline iNat21-only no se extrajeron.

## 6. Limitaciones

### Takeaway
Los autores no tienen sección formal de limitaciones; reconocen herencia de CLIP, falta de GPS, y que es para asistir a biólogos. No encontré análisis de error específico sobre especies crípticas.

### Cited Findings
- Hereda preocupaciones de CLIP; sin información geográfica; "asistir, no reemplazar" biólogos y evitar sobreconfianza — [HF](https://huggingface.co/imageomics/bioclip)
- Etiquetas BIOSCAN solo a nivel de familia (98.6%); error de hemihomónimos; entrenado fundamentalmente para clasificación; futuro: escalar a 100M+ imágenes y descripciones de rasgos — [paper HTML](https://arxiv.org/html/2311.18803v3)
- Rendimiento bajo en Plankton (6.1) e Insects 2 (20.4) zero-shot — [HF](https://huggingface.co/imageomics/bioclip)
- BioCLIP 2 (trabajo posterior) indica preocupación por el colapso de variación intraespecífica (etapas de vida, sexos) con entrenamiento extenso, y datos desbalanceados con cola larga entre taxones, lo que puede perjudicar especies raras — [NVIDIA case study](https://www.nvidia.com/en-us/case-studies/ohio-state-ai-bioclip2-conservation-biodiversity), [BioCLIP 2](https://arxiv.org/pdf/2505.23883) (la afirmación sobre BioCLIP 2 viene del resumen de búsqueda, no leí el PDF)
- Un paper de 2026 afina BioCLIP y evalúa en CrypticBio; advierte que la inferencia jerárquica top-down puede inflar o ocultar errores por nivel — [arXiv 2606.21838](https://arxiv.org/pdf/2606.21838) (solo snippet de búsqueda; resultados no vistos)

### Inferences
- Para especies casi idénticas o críptica, es razonable esperar errores (los rasgos distintivos son sutiles), pero no hay cifra verificada para BioCLIP v1.

### Gaps
- Sin confusión medida en especies crípticas, sesgo de fondo ni domain shift específico de v1 en fuentes primarias.

## 7. Uso práctico

### Takeaway
Se carga con open_clip desde el hub de HF; los embeddings sirven para clasificadores de centroide/kNN.

### Cited Findings
- Código: `import open_clip; model, preprocess_train, preprocess_val = open_clip.create_model_and_transforms('hf-hub:imageomics/bioclip'); tokenizer = open_clip.get_tokenizer('hf-hub:imageomics/bioclip')` — [HF](https://huggingface.co/imageomics/bioclip)
- Preprocesado: 224x224, mean/std de CLIP indicados arriba — [open_clip_config.json](https://huggingface.co/imageomics/bioclip/raw/main/open_clip_config.json)
- Few-shot en el paper: clasificador de centroide más cercano (SimpleShot) sobre los embeddings — [paper HTML](https://arxiv.org/html/2311.18803v3)
- La única dependencia es open_clip; ejemplos en `examples/` del repo HF — [GitHub](https://github.com/Imageomics/bioclip)

### Inferences
- Embeddings de 512-d normalizados L2 aptos para kNN/centroides (la normalización es práctica estándar de CLIP, no verificada en estas fuentes).

### Gaps
- Latencia/tamaño en disco/cuantización para móvil no investigados.
