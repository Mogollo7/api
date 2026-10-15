# Comparación de BioCLIP con otros modelos y métodos técnicos de un pipeline de identificación de especies

Nota de método: la herramienta WebFetch devuelve resúmenes generados por un modelo pequeño, no texto literal; las cifras están tal como las devolvió, y lo marcado "NO VERIFICADO" proviene de conocimiento general sin fuente consultada en esta sesión. Dos URLs resultaron ser de otro paper (arXiv 2405.17537 es CLIBD, no BioTrove; arXiv 2502.13414 es de física); se corrigieron o descartaron.

## 1. BioCLIP frente a CLIP/OpenCLIP, SigLIP, DINOv2, BioTrove, clasificadores iNaturalist, SpeciesNet/Perch, Pl@ntNet, Merlin, MegaDetector

### Takeaway
BioCLIP (ViT-B/16, MIT, imagen+texto taxonómico) es la opción documentada para embeddings/zero-shot/few-shot sobre el árbol de la vida completo; los demás cubren nichos distintos (detección en cámaras trampa, audio, plantas con servicio propietario, aves con datos eBird). No hay en las fuentes una comparación directa de BioCLIP con SigLIP ni DINOv2 (solo DINO v1).

### Cited Findings
- BioCLIP: entrenado sobre TreeOfLife-10M; supera a baselines "by 16% to 17% absolute" en benchmarks de clasificación fina; los autores dicen que sus representaciones siguen la jerarquía del árbol de la vida — [arXiv 2311.18803](https://arxiv.org/abs/2311.18803)
- Zero-shot, media en 10 tareas: BioCLIP 39.4%, CLIP 21.9%, OpenCLIP 20.4% — [arXiv 2311.18803 (HTML)](https://arxiv.org/html/2311.18803)
- Few-shot, media: 1-shot CLIP 33.6 / OpenCLIP 36.7 / DINO 36.2 / BioCLIP 50.3; 5-shot 51.5 / 55.9 / 55.4 / 68.8 — [arXiv 2311.18803 (HTML)](https://arxiv.org/html/2311.18803)
- Rare Species (taxones no vistos), zero-shot: BioCLIP 38.0%, CLIP 31.8%, OpenCLIP 29.8%, modelo solo-iNat21 21.3%; few-shot BioCLIP 44.9% (1-shot) y 65.7% (5-shot) vs CLIP 28.5% y 46.0% — [arXiv 2311.18803 (HTML)](https://arxiv.org/html/2311.18803)
- Ablación de texto: entrenar con nombre taxonómico+común da lo mejor; nombre taxonómico supera al científico en test (26.6% vs 22.3%) — [arXiv 2311.18803 (HTML)](https://arxiv.org/html/2311.18803)
- El paper NO incluye comparación few-shot con DINOv2 ni SigLIP; sus baselines son CLIP, OpenCLIP, ImageNet-21K supervisado y DINO. Limitaciones declaradas: entrenado para clasificación; Bioscan-1M con 98.6% de etiquetas solo a nivel de familia; ~0.1-0.2% de hemihomónimos mal etiquetados — [arXiv 2311.18803 (HTML)](https://arxiv.org/html/2311.18803)
- Model card BioCLIP: ViT-B/16 inicializado desde el checkpoint OpenAI CLIP y entrenado con código OpenCLIP, entrada 224x224; licencia MIT; ~450K taxones citados; 8xA100-80GB ~4 días, batch global 32,768, fp16 mixed precision, 100 épocas; sin información geográfica en el entrenamiento; uso previsto: zero-shot y few-shot con KNN sin fine-tuning; "asistir a biólogos, no reemplazarlos"; no indica nº de parámetros ni tamaño de archivo — [HF imageomics/bioclip](https://huggingface.co/imageomics/bioclip)
- BioCLIP 2 (NeurIPS 2025): TreeOfLife-200M con 214 millones de imágenes; afirma que los embeddings se alinean con rasgos ecológicos/funcionales (tamaño de pico, hábitat) y que la variación intra-especie (etapa de vida, sexo) queda en subespacios ortogonales a la inter-especie — [arXiv 2505.23883 vía NeurIPS](https://proceedings.neurips.cc/paper_files/paper/2025/hash/94da80cbfe870c1db958c88a8a27018c-Abstract-Conference.html)
- BioTrove (NeurIPS 2024, Datasets & Benchmarks): 161.9M imágenes de iNaturalist (research-grade), ~366.6K especies; se entrenó una suite de CLIP (BT-CLIP) sobre un subconjunto de 40M (BioTrove-Train) centrado en aves, arácnidos, insectos, plantas, hongos, moluscos y reptiles; variantes BIOTROVE-O (init OpenCLIP) y BIOTROVE-B (init BioCLIP). La búsqueda no halló un modelo llamado "BioTrove-CLIP" como tal (el nombre real es BT-CLIP). La tarjeta HF habla de 33K especies para el subconjunto de 40M — [arXiv 2406.17720](https://arxiv.org/pdf/2406.17720); [NeurIPS](https://proceedings.neurips.cc/paper_files/paper/2024/hash/b92854f80ba4feefb973959b259dbc2c-Abstract.html); [HF Arboretum/BT-CLIP-O](https://huggingface.co/Arboretum/BT-CLIP-O). Hay discrepancia de cifras (366.6K vs 33K) explicada por alcance distinto (colección completa vs subconjunto); no se pudo leer el paper completo para comparar BT-CLIP vs BioCLIP.
- DINOv2: entrena ViT de 1B parámetros sobre dataset curado automáticamente y lo destila a modelos menores; afirma superar a OpenCLIP en la mayoría de benchmarks de imagen y píxel, features "all-purpose" sin fine-tuning. (Solo imagen, sin texto; licencia no confirmada por la fuente) — [arXiv 2304.07193](https://arxiv.org/abs/2304.07193)
- SigLIP: pérdida sigmoide por pares sin normalización global; mejor a batch pequeño; SigLiT 84.5% zero-shot ImageNet en 2 días con 4 TPUv4. Es mejora de la receta CLIP, no un modelo de biología — [arXiv 2303.15343](https://arxiv.org/abs/2303.15343)
- SpeciesNet (Google): >2000 etiquetas (especies, taxones superiores, "blank", "vehicle"); >65M imágenes de entrenamiento (Wildlife Insights y repositorios públicos); repo Apache-2.0 (licencia de pesos no indicada en la página); entrada: fotos fijas de cámaras trampa (también vídeo con run_md_and_speciesnet); usa MegaDetector como detector y un ensamble con geofencing opcional (país/estado) que sube a un taxón superior si la especie no es posible en la región — [GitHub google/cameratrapai](https://github.com/google/cameratrapai)
- MegaDetector: detecta animales, personas y vehículos en imágenes de cámaras trampa, NO identifica especie; útil para eliminar imágenes vacías; repo MIT; remite a SpeciesNet para especie — [GitHub agentmorris/MegaDetector](https://github.com/agentmorris/MegaDetector)
- Perch 2.0 (Google DeepMind, ago 2025): modelo fundacional de bioacústica (AUDIO, no imagen), entrenado sobre todo con aves y otros animales terrestres vocalizadores; estado del arte en BirdSet y BEANS; da clasificación y embeddings. Cifras 101.8M parámetros / 1.5M grabaciones / 14,500 especies vienen de un medio secundario, no verificadas en el paper — [arXiv 2508.04665](https://arxiv.org/pdf/2508.04665)
- Pl@ntNet: ID de plantas mediante deep learning (descrito en la doc de API); ~75k+ (2025) / 77,000+ (Wikipedia) especies; API gratuita para uso limitado/sin ánimo de lucro (límites pueden haber cambiado); las imágenes devueltas suelen ser CC BY-SA (con atribución), pero el modelo es propietario (pesos no públicos); marca registrada de CIRAD, INRAE, INRIA, IRD — [Pl@ntNet API doc](https://my.plantnet.org/doc); [Wikipedia](https://en.wikipedia.org/wiki/Pl@ntNet); [Términos](https://identify.plantnet.org/terms_of_use)
- Merlin Photo ID (Cornell Lab / Visipedia Caltech y Cornell Tech): aves; usa fecha y ubicación y datos eBird para ponderar candidatos; entrenado con fotos de Macaulay Library/eBird; funciona offline; en 2015 daba la especie correcta en top-3 el 90% de las veces (versión antigua); cobertura mundial anunciada de 10,315 especies en mayo 2023 (cifra de cobertura del app, no necesariamente de Photo ID) — [Caltech Magazine](https://magazine.caltech.edu/post/merlin-bird-photo-id); [Cornell 2023](https://www.news.cornell.edu/stories/2023/05/merlin-milestone-app-now-helps-id-birds-worldwide); [eBird](https://ebird.org/news/merlinid)

### Inferences
- Elección: especies raras/few-shot o taxonomía jerárquica -> BioCLIP (embeddings + kNN/centroides; evidencia Rare Species). Cámara trampa en servidor -> MegaDetector + SpeciesNet (con geofence). Plantas -> Pl@ntNet por API (no se puede llevar el modelo al móvil). Aves con ubicación -> Merlin (cerrado; no es un componente reutilizable). Audio -> Perch (otra modalidad). Móvil sin red -> backbone propio (BioCLIP ViT-B/16 exportado) más que servicios.
- Dado que BioCLIP es ViT-B/16 inicializado de CLIP, su coste de cómputo es el de un ViT-B estándar (inferencia; tamaño exacto no declarado en la fuente).
- SigLIP/DINOv2 son alternativas genéricas plausibles, pero no hay evidencia citada aquí de que superen a BioCLIP en especies; no afirmarlo.

### Gaps
- Comparación directa BioCLIP vs DINOv2/SigLIP en especies: no encontrada en las fuentes leídas.
- Licencias de DINOv2/SigLIP/BT-CLIP, tamaño/parámetros de BioCLIP, resultados numéricos de BT-CLIP vs BioCLIP: no verificados.
- Clasificadores entrenados en iNaturalist (p. ej. modelo iNat21, ViT/ResNet supervisados): solo aparece como baseline (21.3% en Rare Species zero-shot); no se consultó el modelo de computer vision de iNaturalist en sí. NO VERIFICADO.
- Merlin: no se consultó el paper técnico ni la cifra actual de especies en Photo ID.

## 2. Fine-tuning de modelos preentrenados para especies casi idénticas: riesgos y mitigaciones

### Takeaway
La literatura respalda que el fine-tuning completo puede distorsionar los rasgos preentrenados y perder robustez fuera de distribución; es un riesgo con mitigaciones documentadas (LP-FT, WiSE-FT), no un error categórico. Para pocas imágenes por clase, lo documentado en BioCLIP es usar el encoder congelado con KNN/few-shot.

### Cited Findings
- Kumar et al.: en 10 datasets con cambio de distribución, el fine-tuning completo dio ~2% más de accuracy in-distribution pero ~7% menos OOD que el linear probing; lo atribuyen a que el fine-tuning distorsiona los rasgos preentrenados (capas inferiores cambian mientras se aprende la cabeza). LP-FT (linear probe y luego fine-tuning) superó al fine-tuning completo en ~1% ID y ~10% OOD — [arXiv 2202.10054](https://arxiv.org/abs/2202.10054)
- WiSE-FT: promediar pesos del modelo zero-shot y el afinado (CLIP, ALIGN) mantiene accuracy en datos objetivo y mejora robustez bajo cambio de distribución; sin coste extra en entrenamiento ni inferencia; en ImageNet mejora 4-6 puntos bajo cambios de distribución y 1.6 puntos en ImageNet — [arXiv 2109.01903](https://arxiv.org/abs/2109.01903)
- Uso previsto de BioCLIP según su model card: zero-shot y few-shot con KNN "sin fine-tuning"; el encoder ViT-B/16 recomendado como base — [HF imageomics/bioclip](https://huggingface.co/imageomics/bioclip)
- Evidencia de few-shot sin afinar: BioCLIP 5-shot 68.8% medio vs 55.9% OpenCLIP — [arXiv 2311.18803](https://arxiv.org/html/2311.18803)

### Inferences
- Veredicto equilibrado: afinar es un riesgo (distorsión de features, sobreajuste con pocas imágenes por clase), mitigable con: (1) linear probe primero; (2) features congeladas + kNN/centroides por clase; (3) LP-FT; (4) tasa de aprendizaje baja; (5) WiSE-FT para interpolar con los pesos originales. Es un error solo si se hace fine-tuning completo con LR alto sobre muy pocos datos sin validación.
- Sobre "colapso" de especies similares: ninguna fuente leída lo demuestra; el mecanismo plausible (cabeza/capas que pierden la estructura jerárquica del embedding) es una inferencia, y debe validarse midiendo separación entre pares de especies parecidas antes/después.

### Gaps
- Literatura específica sobre olvido catastrófico ("catastrophic forgetting") en CLIP para taxonomía fina y sobre colapso de clases casi idénticas: no encontrada en esta sesión. NO VERIFICADO.
- Los resultados de Kumar et al. son de benchmarks de visión generales, no de especies.

## 3. Destilación de conocimiento y la analogía "DeepSeek vs ChatGPT"

### Takeaway
Destilación (Hinton et al., 2015): entrenar un modelo pequeño con el conocimiento de un modelo/ensamble grande. Lo documentado de DeepSeek: los modelos DeepSeek-R1-Distill son Qwen/Llama afinados con muestras de R1; que DeepSeek destilara de ChatGPT es una acusación de OpenAI sin evidencia publicada.

### Cited Findings
- Hinton, Vinyals, Dean: comprimir el conocimiento de un ensamble en un único modelo más fácil de desplegar (extiende a Caruana et al.); resultados en MNIST y mejora del modelo acústico de un sistema comercial; propone también modelos especialistas para clases finas que el modelo completo confunde — [arXiv 1503.02531](https://arxiv.org/abs/1503.02531). (La explicación de temperatura/soft targets no figuraba en la página del abstract; es conocimiento general del paper, no verificado aquí.)
- DeepSeek-R1-Distill: afinados desde Qwen2.5-Math-1.5B/7B, Qwen2.5-14B/32B, Llama-3.1-8B y Llama-3.3-70B-Instruct con "800k samples curated with DeepSeek-R1"; código y pesos MIT, con las licencias de las bases aplicando — [HF DeepSeek-R1-Distill-Qwen-7B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B). El paper de R1 dice que los patrones de razonamiento de modelos grandes pueden guiar a modelos pequeños — [arXiv 2501.12948](https://arxiv.org/abs/2501.12948)
- Acusación: a finales de enero 2025 OpenAI dijo al Financial Times que tenía indicios de que DeepSeek pudo haber destilado sus modelos (sospecha de uso de salidas de o1); no publicó la evidencia, no acusó de brecha de seguridad; sus términos prohíben usar salidas para desarrollar modelos competidores; David Sacks (Casa Blanca) habló de "substantial evidence"; DeepSeek no respondió — [NBC News](https://www.nbcnews.com/tech/tech-news/openai-says-deepseek-may-inapproriately-used-data-rcna189872); [BGR](https://bgr.com/tech/openai-says-it-has-evidence-deepseek-used-chatgpt-to-train-its-ai/). No se halló reporte de Reuters en la búsqueda.
- DINOv2 es otro ejemplo práctico: ViT de 1B destilado a modelos menores — [arXiv 2304.07193](https://arxiv.org/abs/2304.07193)

### Inferences
- Se puede decir con seguridad: (a) la destilación es una técnica estándar; (b) DeepSeek destiló R1 hacia Qwen/Llama; (c) OpenAI alegó (sin pruebas públicas) que DeepSeek usó salidas de ChatGPT/o1. NO se puede decir como hecho que DeepSeek destiló ChatGPT.
- Nótese que las R1-Distill son destilación por salidas (fine-tuning con muestras del profesor), no la de logits con temperatura de Hinton.
- Causas típicas de fallo (capacidad insuficiente del estudiante, pocos datos, brecha de dominio): son conocimiento general; ninguna fuente de esta sesión las cuantifica. NO VERIFICADO.

### Gaps
- Texto completo de Hinton (temperatura): no leído. Fuentes primarias sobre fallos de destilación (capacity gap): no consultadas.

## 4. Cuantización de ViT: INT8 PTQ, FP16, conversión y validación en Android

### Takeaway
INT8 PTQ ingenuo degrada ViT por distribuciones de activaciones atípicas (post-LayerNorm, post-softmax, post-GELU); FP16 es una reducción a la mitad que no necesita calibración. En Android, el soporte de FP16 en ONNX Runtime CPU es limitado según la doc, por lo que debe medirse en dispositivo.

### Cited Findings
- PTQ4ViT: métodos PTQ previos perdían >1% incluso a 8 bits en ViT; causa: activaciones post-softmax y post-GELU con distribución muy distinta de la gaussiana; propone cuantización uniforme gemela y métrica guiada por Hessiano, con <0.5% de caída a 8 bits en ImageNet — [arXiv 2111.12293](https://arxiv.org/abs/2111.12293)
- RepQ-ViT: activaciones post-LayerNorm con "severe inter-channel variation" (cuantización por canal) y post-softmax con distribución tipo ley de potencias (cuantizador log√2); logra PTQ de 4 bits "usable" — [arXiv 2212.08254](https://arxiv.org/abs/2212.08254)
- Conversión FP32->FP16 en ONNX: `onnxconverter_common.float16.convert_float_to_float16(model)`; `keep_io_types=True` mantiene entradas/salidas en float32; `min_positive_val`/`max_finite_val` (por defecto 1e-7 y 1e4) recortan constantes; `op_block_list`/`node_block_list` mantienen ops en FP32; `auto_convert_mixed_precision` requiere datos de ejemplo y, según la doc, ejecutarse en dispositivo con GPU; la doc advierte que FP16 puede reducir accuracy y no necesita datos de calibración; y que "the CPU build of ONNX Runtime doesn't support float16 ops" — [ORT float16](https://onnxruntime.ai/docs/performance/model-optimizations/float16.html)
- XNNPACK EP en Android (paquete Maven onnxruntime-android): hay que registrarlo explícitamente; la lista de ops soportadas (Conv 2D, pooling 2D, Softmax, Gemm/MatMul 2D, Resize) no menciona FP16 — [ORT XNNPACK](https://onnxruntime.ai/docs/execution-providers/Xnnpack-ExecutionProvider.html)
- NNAPI EP: requiere Android 8.1+ (9+ recomendado); `NNAPI_FLAG_USE_FP16` activa relajación fp16 que puede mejorar rendimiento y reducir accuracy; solo ops listadas, con restricciones; el fallback a CPU de NNAPI puede ser menos eficiente que los kernels de ORT — [ORT NNAPI](https://onnxruntime.ai/docs/execution-providers/NNAPI-ExecutionProvider.html)
- BioCLIP se entrenó con fp16 mixed precision — [HF imageomics/bioclip](https://huggingface.co/imageomics/bioclip)

### Inferences
- FP16 reduce pesos a 2 bytes frente a 4: tamaño de archivo ~la mitad (aritmética; lo no convertido, como ops bloqueadas, atenúa algo la reducción).
- Validación recomendada: mismo top-1 en un conjunto de validación, similitud coseno entre embeddings FP32 y FP16 (idealmente ~1.0), y comparación de top-5/ranking; mantener `keep_io_types=True` simplifica la integración en Android.
- Riesgo a vigilar: constantes que se desbordan o hacen underflow en FP16 (límite del rango FP16 ~65504; el recorte por defecto de la herramienta es 1e4 según la doc) y ops sensibles (LayerNorm/softmax) -> usar block lists o mixed precision si el coseno cae.
- La doc de ORT dice que la CPU no soporta ops FP16; en la práctica ORT inserta casts, por lo que en CPU de Android FP16 puede ahorrar tamaño pero no necesariamente latencia. NO VERIFICADO con medición; probar en el Redmi Note 13 Pro+.

### Gaps
- LLM.int8() (outliers en LLM) no consultado; el paper de outliers en LayerNorm de ViT tampoco. NO VERIFICADO.
- Hoja de ruta de PyTorch `.half()` no consultada (conocimiento general).
- Soporte actual de FP16 en CPU de ORT móvil (ARM fp16 kernels): no confirmado, la doc leída puede estar desactualizada.

## 5. Segmentación / recorte / eliminación de fondo antes de clasificar

### Takeaway
La literatura dice que los modelos usan el fondo como señal (parte útil, parte espuria), por lo que enmascarar no es claramente beneficioso; los resultados propios del proyecto (recorte 51.5->42.5%; fondo negro 60.7->44.7%) son compatibles con un desajuste de distribución respecto al preentrenamiento.

### Cited Findings
- Xiao et al. (Madry lab), "Noise or Signal": los modelos pueden lograr accuracy no trivial usando solo el fondo; con fondos adversariales fallan hasta el 87.5% de las veces aun cuando el primer plano solo se clasifica bien; los modelos más precisos dependen menos del fondo — [arXiv 2006.09994](https://arxiv.org/abs/2006.09994)
- BioCLIP/TreeOfLife se entrenó con fotos naturales completas (no segmentadas); la model card indica que no incluye información geográfica — [HF imageomics/bioclip](https://huggingface.co/imageomics/bioclip)
- SpeciesNet clasifica detecciones de MegaDetector (la pipeline de cámara trampa sí usa detección previa, para localizar animal) — [GitHub google/cameratrapai](https://github.com/google/cameratrapai)

### Inferences
- El fondo contiene señal (hábitat) y ruido; eliminarlo cambia la distribución de entrada (imágenes con fondo negro o recortes sin contexto no se parecen a las de preentrenamiento), lo que explica una caída de 60.7->44.7% sin contradecir a Xiao et al. Es una inferencia, no un resultado citado.
- Recortes que dejan al animal pequeño/ampliado a 224x224 también cambian escala y resolución; el 51.5->42.5% podría deberse a pérdida de contexto o a escala. Debe probarse recorte con margen en lugar de máscara dura.
- La experiencia de SpeciesNet/MegaDetector sugiere que detectar para localizar es útil en cámaras trampa con animales pequeños en escena; no es evidencia de que enmascarar el fondo ayude.

### Gaps
- No se hallaron estudios específicos de enmascarado de fondo en BioCLIP/CLIP para clasificación fina de especies. NO VERIFICADO.
- Los resultados propios del proyecto no se verificaron con ninguna fuente externa.
