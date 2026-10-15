# BioCLIP 2 y BioCLIP 2.5 (sucesores de BioCLIP 1)

Fecha de consulta: 2026-10-14. Fuentes primarias: tarjetas de modelo y API de Hugging Face, arXiv 2505.23883. Todo lo marcado "calculado" o "no verificado" no proviene de una fuente.

## BioCLIP 2: paper, arquitectura, datos, afirmaciones

### Takeaway
BioCLIP 2 (Gu et al., arXiv 2505.23883, NeurIPS 2025 Spotlight) es un CLIP ViT-L/14 entrenado sobre TreeOfLife-200M (~214M imágenes, 952K taxones); sube la media zero-shot en especies de 37.6 (BioCLIP 1) a 55.6 y la media en tareas no-especie de 49.0 a 57.5.

### Cited Findings
- Título "BioCLIP 2: Emergent Properties from Scaling Hierarchical Contrastive Learning"; 16 autores (Gu, Stevens, Campolongo, ..., Chao, Su); v1 29-may-2025, v2 23-oct-2025; comentarios arXiv: NeurIPS 2025 Spotlight — [arXiv](https://arxiv.org/abs/2505.23883)
- Arquitectura: image encoder ViT-L/14 + text encoder transformer, ajustado desde CLIP ViT-L/14 preentrenado en LAION-2B; licencia MIT; entrenamiento en 32 H100, 30 épocas (~10 días), Adam lr 1e-4, wd 0.2, entrada 224x224 — [HF bioclip-2](https://huggingface.co/imageomics/bioclip-2)
- Dimensión de embedding 768; visión 24 capas, ancho 1024, patch 14; texto 12 capas, ancho 768, 12 heads, contexto 77, vocab 49408 — [open_clip_config.json de bioclip-2](https://huggingface.co/imageomics/bioclip-2/raw/main/open_clip_config.json)
- Datos: TreeOfLife-200M, 214M imágenes, 952,257 taxones (~868K a nivel especie), más 26M muestras LAION-2B como experience replay. Fuentes GBIF: 51.8M especímenes de museo, 617.8K cámaras trampa, 151M ciencia ciudadana. 2.6x más taxones que BioTrove (162M imágenes, 366K especies) — [arXiv HTML](https://arxiv.org/html/2505.23883)
- Zero-shot especies (media 10 tareas): BioCLIP 37.6 -> BioCLIP 2 55.6 (+18.0); CLIP ViT-L/14 25.5. Fungi 40.9 -> 83.8; Rare Species 37.1 -> 76.8; Camera Trap 31.7 -> 53.9. One-shot media 50.0 -> 64.1; five-shot 68.5 -> 78.3 — [arXiv HTML](https://arxiv.org/html/2505.23883)
- Tareas no-especie (FishNet/NeWT/AwA2/Herbarium19/PlantDoc), media: BioCLIP 49.0 -> BioCLIP 2 57.5 (CLIP 42.7; DINOv3 48.6). Por tarea BioCLIP 1 vs 2: FishNet 30.1/39.8, NeWT 82.7/89.1, AwA2 65.9/69.5, Herb19 26.8/48.6, PlantDoc 39.5/40.4 — [arXiv HTML](https://arxiv.org/html/2505.23883)
- Propiedades emergentes: el embedding se alinea con rasgos ecológicos/funcionales entre especies; la variación intra-especie (etapas de vida, sexo) se conserva en subespacios ortogonales a la separación entre especies; ambas tendencias se acentúan al escalar datos (probado con 1M, 10M, 50M, 214M). Medidas: razón de varianza explicada rho (decrece con la escala) y Fisher Discriminant Ratio (crece). El paper da resultados de tendencia (figuras), no cifras exactas para esto; el Teorema 5.1 respalda la ortogonalidad bajo prototipos casi ortogonales, y los autores dicen no haber probado formalmente la tendencia de separación — [arXiv](https://arxiv.org/abs/2505.23883), [HTML](https://arxiv.org/html/2505.23883)
- Ablaciones: solo nombres científicos sin jerarquía, FishNet 35.1 -> 33.8; entropía cruzada en vez de contrastiva, FishNet 33.0 — [arXiv HTML](https://arxiv.org/html/2505.23883)
- Advertencia de sesgo hacia especies bien representadas (datos de cola larga) — [HF bioclip-2](https://huggingface.co/imageomics/bioclip-2)

### Inferences
- BioCLIP 1 usa ViT-B/16 y TreeOfLife-10M; la ganancia de BioCLIP 2 mezcla modelo mayor y datos ~20x mayores.

### Gaps
- El paper discrepa internamente: el texto dice brecha 22.8% en Camera Trap, la tabla da 22.2 puntos. Usar la tabla.
- Los últimos ~26K caracteres del HTML del paper no se leyeron (apéndices).
- No se obtuvieron cifras numéricas de rho ni de Fisher ratio.

## BioCLIP 2.5: existencia y datos

### Takeaway
BioCLIP 2.5 existe: `imageomics/bioclip-2.5-vith14` ("BioCLIP 2.5 Huge"), ViT-H/14, embedding 1024, MIT. La afirmación "BioCLIP 2.5 no existe" es falsa.

### Cited Findings
- Repo creado 2026-02-10 (createdAt), última modificación 2026-08-27; licencia MIT; 11,391 descargas al consultar — [HF API](https://huggingface.co/api/models/imageomics/bioclip-2.5-vith14?blobs=true)
- La tarjeta no da fecha de lanzamiento propia; es versión 1.0.0, citada como 2026, DOI 10.57967/hf/10131 — [HF README](https://huggingface.co/imageomics/bioclip-2.5-vith14/raw/main/README.md). La tarjeta de BioCLIP 2 indica que existe una versión más nueva, bioclip-2.5-vith14 — [HF bioclip-2](https://huggingface.co/imageomics/bioclip-2)
- embed_dim 1024; visión: 32 capas, ancho 1280, head_width 80, patch 14, imagen 224; texto: 24 capas, ancho 1024, 16 heads, contexto 77, vocab 49408 — [open_clip_config.json](https://huggingface.co/imageomics/bioclip-2.5-vith14/raw/main/open_clip_config.json)
- Base: CLIP ViT-H/14 preentrenado en LAION-2B; datos: TreeOfLife-200M actualizado (+19M imágenes y filtrado adicional por contenido) + réplica de 26M muestras LAION-2B; 25 épocas, 32 H100-80GB (4 nodos, Bridges-2 PSC), ~11 días; Adam lr 1e-4, 20,000 warmup, coseno, wd 0.2; lote 1,152 imágenes bio + 128 replay por GPU; bf16 puro, torch.compile; 224x224 — [HF README](https://huggingface.co/imageomics/bioclip-2.5-vith14/raw/main/README.md)
- Zero-shot especies, top-1, media 10 tareas: BioCLIP 37.6; BioCLIP 2 55.6; 2.5 Huge 61.3. Por tarea (BioCLIP 2 -> 2.5): NABirds 74.9->75.8, Plankton 3.9->5.2 (BioCLIP 1: 6.1, el mejor), Insects 55.3->68.2, Insects 2 27.7->30.8, Camera Trap 53.9->58.7, PlantNet 96.8->96.9, Fungi 83.8->84.9, PlantVillage 25.1->33.5, Med. Leaf 57.8->73.2, Rare Species 76.8->85.5 — [HF README](https://huggingface.co/imageomics/bioclip-2.5-vith14/raw/main/README.md)
- Tareas amplias, media 5 tareas: BioCLIP 49.0; BioCLIP 2 57.5; 2.5 Huge 61.0 (FishNet 39.8->48.5, NeWT 89.1->90.0, AwA2 69.5->72.9, Herb19 48.6->51.9, PlantDoc 40.4->41.9). Métricas: FishNet all-9-labels, NeWT micro-acc, AwA2 macro-F1, Herb19 clustering acc, PlantDoc 1-shot — mismo README
- La tarjeta indica: requiere bastante más cómputo de inferencia que BioCLIP 2; metadatos/embeddings de especies del dataset aún por actualizar — mismo README
- Carga: `open_clip.create_model_and_transforms('hf-hub:imageomics/bioclip-2.5-vith14')` — mismo README
- El README de pybioclip consultado menciona solo BioCLIP 2 (default) y BioCLIP original; no menciona 2.5 — [GitHub pybioclip](https://github.com/Imageomics/pybioclip)

### Inferences
- Ganancia 2.5 vs 2: +5.7 puntos en especies y +3.5 en amplias (61.3-55.6 y 61.0-57.5); la tarjeta las llama "%".
- Ganancias grandes en Insects, Med. Leaf, Rare Species y FishNet; casi nulas en PlantNet/NABirds (saturadas).

### Gaps
- No se localizó paper de BioCLIP 2.5; el único respaldo es la tarjeta. Fecha de lanzamiento: solo createdAt del repo.
- FLOPs: ninguna fuente consultada los da.

## Tabla comparativa BioCLIP 1 vs 2 vs 2.5

### Takeaway
Tres escalas: ~150M, ~428M, ~986M parámetros (calculados desde tamaño de archivo).

### Cited Findings
| | BioCLIP 1 | BioCLIP 2 | BioCLIP 2.5 Huge |
|---|---|---|---|
| Arquitectura imagen | ViT-B/16 (init CLIP OpenAI) | ViT-L/14 (init CLIP LAION-2B) | ViT-H/14 (init CLIP LAION-2B) |
| Embedding dim | no verificado (config no leído) | 768 | 1024 |
| Params (calculado: bytes/4) | ~149.7M (598,599,013 B) | ~427.6M (1,710,517,724 B) | ~986.1M (3,944,517,804 B) |
| Archivo | .bin 598.6 MB | safetensors 1.71 GB (+ .bin 1.71 GB) | safetensors 3.94 GB (+ .bin 3.94 GB) |
| fp16 (calculado, mitad) | ~0.30 GB | ~0.86 GB | ~1.97 GB |
| FLOPs aprox. | no verificado | no verificado | no verificado |
| Datos | TreeOfLife-10M (~450K+ taxones) | TreeOfLife-200M (~214M img, 952K taxones) + 26M LAION | TreeOfLife-200M actualizado (+19M) + 26M LAION |
| Licencia | MIT | MIT | MIT |
| Lanzamiento | HF creado 2023-06-26; CVPR 2024 | HF creado 2025-05-27; paper 2025-05-29 | HF creado 2026-02-10 |
| Zero-shot esp. media | 37.6 | 55.6 | 61.3 |
| Amplias media | 49.0 | 57.5 | 61.0 |

Fuentes: [HF bioclip](https://huggingface.co/imageomics/bioclip), [API bioclip](https://huggingface.co/api/models/imageomics/bioclip?blobs=true), [API bioclip-2](https://huggingface.co/api/models/imageomics/bioclip-2?blobs=true), [API 2.5](https://huggingface.co/api/models/imageomics/bioclip-2.5-vith14?blobs=true) y las tarjetas citadas. La tarjeta de BioCLIP 1 da 39.4 de media zero-shot y 38.0 en Rare Species con su propia tabla; las tarjetas nuevas dan 37.6 y 37.1 (protocolo de 10 tareas distinto). No mezclar.

### Inferences
- Parámetros: el cálculo asume pesos fp32; el 2.5 sale 986.1M, coherente con el CLIP ViT-H/14 estándar (de memoria del autor, no de fuente). fp16 es la mitad exacta del archivo fp32.
- El embedding de BioCLIP 1 sería 512 por convención de CLIP B/16; no verificado.

### Gaps
- FLOPs sin fuente. De memoria (no verificado): ViT-H/14 de imagen ~160+ GFLOPs frente a ~80 de L/14 y ~40 de B/16; confirmar con la tabla de perfiles de open_clip antes de citar.

## Notas prácticas: memoria, carga y caché

### Takeaway
2.5 Huge pesa 3.94 GB en fp32 (~1.97 GB en fp16); cabe en cualquier GPU de servidor moderna, pero conviene mantenerlo cargado en un proceso persistente y con caché local/offline.

### Cited Findings
- El repo trae dos formatos (safetensors y .bin, ~3.94 GB cada uno) — [HF API](https://huggingface.co/api/models/imageomics/bioclip-2.5-vith14?blobs=true)
- La tarjeta de 2.5 avisa de mayor cómputo de inferencia que BioCLIP 2 — [HF README](https://huggingface.co/imageomics/bioclip-2.5-vith14/raw/main/README.md)

### Inferences (no verificadas contra documentación; práctica estándar de Hugging Face/open_clip)
- VRAM: pesos fp32 ~3.9 GB, fp16/bf16 ~2 GB, más activaciones; con lote pequeño a 224x224 una GPU de 8 GB debería bastar. Medir en el hardware real.
- Caché: fijar `HF_HOME` (o `HF_HUB_CACHE`) a disco persistente; precalentar con `huggingface-cli download imageomics/bioclip-2.5-vith14` o `snapshot_download`; luego `HF_HUB_OFFLINE=1` evita llamadas de red y errores de re-descarga. Alternativa: instantánea local y cargar desde ruta (soporte de ruta local en open_clip depende de la versión; verificar).
- Cargar el modelo una sola vez al arranque (proceso caliente), `model.eval()`, `torch.inference_mode()`, fp16/bf16 en GPU; precomputar y guardar en disco los embeddings de texto del catálogo de especies, de modo que cada petición solo codifique la imagen.

### Gaps
- No se midieron tiempos de carga ni VRAM reales; el README de pybioclip no documenta caché/offline ni lista 2.5 (puede estar soportado en otra versión, no verificado).

## Base de recomendación

### Takeaway
Servidor con GPU: BioCLIP 2.5 Huge (mejor precisión). Móvil/on-device: BioCLIP 1 por tamaño (~150M, ~0.3 GB fp16) o BioCLIP 2 (~0.86 GB fp16) como compromiso si el dispositivo lo soporta.

### Cited Findings
- 2.5 mejora +5.7 puntos (especies) y +3.5 (amplias) sobre BioCLIP 2, con más cómputo — [HF README](https://huggingface.co/imageomics/bioclip-2.5-vith14/raw/main/README.md)
- BioCLIP 2 supera a BioCLIP 1 en +18.0 puntos zero-shot — [arXiv HTML](https://arxiv.org/html/2505.23883)

### Inferences
- BioCLIP 1 es el único con tamaño realista para móvil, pero pierde ~18 a ~24 puntos de media zero-shot frente a 2/2.5 (55.6-37.6; 61.3-37.6). BioCLIP 2 da casi toda la ganancia con 0.43x del tamaño del 2.5 (computado). Exportar el encoder de imagen a ONNX y cuantizar; precomputar embeddings de texto en servidor.
- No hay mejora universal: en Plankton BioCLIP 1 (6.1) supera a 2.5 (5.2).

### Gaps
- Latencia y consumo en móvil, y calidad tras cuantización, no verificados.
