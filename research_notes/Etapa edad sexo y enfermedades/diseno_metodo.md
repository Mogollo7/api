# Diseño de pipeline universal de identificación: especie, etapa, sexo, edad, salud

Nota metodológica: ~20 llamadas de búsqueda/lectura; casi todas las fuentes son resúmenes (abstracts) de arXiv o páginas web, no lecturas completas de los PDF. Lo que no se verificó va marcado [SIN FUENTE].

## 1. Diseño multitarea: cabezales compartidos vs modelos separados vs prompts zero-shot

### Takeaway
BioCLIP 2 afirma que la variación intraespecífica (etapa de vida, sexo) se conserva en el embedding en subespacios ortogonales a la distinción entre especies, lo que respalda un embedding compartido con cabezales ligeros por atributo. No hay evidencia encontrada de que ocurra igual con salud/enfermedad, ni de prompts zero-shot fiables para atributos.

### Cited Findings
- CLIP se entrena con 400 M de pares imagen-texto; el texto permite nombrar conceptos nuevos y aplicar el modelo sin entrenamiento específico, con transferencia razonable en más de 30 datasets, a menudo cercana a baselines supervisados — [CLIP, arXiv 2103.00020](https://arxiv.org/abs/2103.00020)
- BioCLIP: dataset TreeOfLife-10M (plantas, animales, hongos); supera baselines en tareas finas de biología por 16-17% absoluto; aprende una representación jerárquica que "conforma al árbol de la vida" — [BioCLIP, arXiv 2311.18803](https://arxiv.org/abs/2311.18803)
- BioCLIP 2: el abstract afirma que las variaciones intraespecíficas (p. ej. etapas de vida y sexos) "se preservan y se separan mejor" en el espacio de embedding, en subespacios ortogonales a las distinciones entre especies, y que esto se acentúa con más datos de entrenamiento. El abstract no menciona salud ni enfermedad — [BioCLIP 2, arXiv 2505.23883](https://arxiv.org/abs/2505.23883)
- Detalle del paper BioCLIP 2: TreeOfLife-200M ≈ 214 M de imágenes, 952,257 taxones; la variación de etapa se evalúa con NeWT y la de sexo con NABirds, con tareas de "alineación" (clasificador de especie entrenado en una variante reconoce la otra) y "diferenciación" (distinguir variantes). Los autores reconocen que la separación ortogonal no está probada formalmente (solo evidencia empírica) y que el dataset está desbalanceado (microorganismos con ≤ ~12 imágenes) — [BioCLIP 2, versión HTML](https://arxiv.org/html/2505.23883)
- En el mismo paper, los resultados zero-shot reportados son solo de clasificación de especie; no se encontraron resultados zero-shot de prompts de atributos. Para enfermedad de plantas (PlantDoc) BioCLIP 2 puntúa 40.4 ± 3.7 (Tabla 2) — [BioCLIP 2, versión HTML](https://arxiv.org/html/2505.23883)
- El abstract de BioCLIP 2 no reporta que se hayan probado cabezales multitarea; no se encontró un estudio que compare directamente cabezales compartidos frente a modelos separados para especie+etapa+sexo+salud. [SIN FUENTE]

### Inferences
- Diseño recomendado (inferencia, no probado en las fuentes): un backbone/embedding congelado tipo BioCLIP 2 + cabezales lineales o MLP pequeños por pregunta (etapa, sexo, salud), entrenados con pocas etiquetas, con cabezales condicionados al taxón (p. ej. un cabezal de sexo por grupo taxonómico) porque la expresión de sexo y etapa es específica de cada grupo.
- Prompts tipo "a photo of an adult male X" quedan como baseline barato para sondear, no como método de producción, mientras no haya validación propia.
- Salud/enfermedad probablemente necesita ajuste fino o cabezal supervisado con datos locales; el 40.4 de PlantDoc sugiere que el embedding general no resuelve enfermedad por sí solo.

### Gaps
- No hay evidencia encontrada sobre embeddings de especie y su codificación de salud/enfermedad en animales.
- No se leyó el apéndice completo de BioCLIP 2 (el fetch truncó los últimos ~26k caracteres).

## 2. Clasificación jerárquica, abstención y calibración

### Takeaway
Fundamentos sólidos: calibrar con temperature scaling, rechazar con clasificación selectiva (riesgo objetivo / cobertura) y, para "desconocido", usar la puntuación de un buen clasificador cerrado. El "rollup" taxonómico (devolver género/familia cuando no hay confianza para especie) ya se usa en producción en SpeciesNet.

### Cited Findings
- Las redes modernas están mal calibradas; profundidad, anchura, weight decay y batch norm influyen; temperature scaling (versión de un parámetro de Platt scaling) es "sorprendentemente eficaz" — [Guo et al. 2017](https://arxiv.org/abs/1706.04599)
- Clasificación selectiva con opción de rechazo sobre una red ya entrenada; el usuario fija un riesgo objetivo y el clasificador rechaza para cumplirlo con alta probabilidad; en ImageNet top-5 reportan 2% de error garantizado con 99.9% de probabilidad manteniendo casi 60% de cobertura — [Geifman & El-Yaniv 2017](https://arxiv.org/abs/1705.08500)
- La probabilidad softmax máxima es una baseline simple para detectar entradas mal clasificadas o fuera de distribución, aunque a veces se puede superar — [Hendrycks & Gimpel 2016](https://arxiv.org/abs/1610.02136)
- Capacidad de rechazo de clases desconocidas correlaciona fuertemente con la precisión en clases conocidas; mejorar la precisión cerrada fortalece la baseline de max-logit hasta el estado del arte; propone el Semantic Shift Benchmark — [Vaze et al. 2021, arXiv 2110.06207](https://arxiv.org/abs/2110.06207)
- SpeciesNet: ensamble de MegaDetector + clasificador con más de 2,000 etiquetas que incluyen taxones superiores (p. ej. "mammalia", "felidae") y no-animales ("blank", "vehicle"); incluye rollup taxonómico para predicciones de baja confianza y filtro geográfico opcional. Wildlife Insights (anuncio de 2020, puede estar desactualizado) mostraba "No CV Results" bajo 65% de confianza para especie y 95% para vacíos — [búsqueda sobre SpeciesNet / repo google/cameratrapai](https://github.com/google/cameratrapai) (detalles de umbrales de resumen de búsqueda, no verificados en la página del repo)
- BioCLIP aprende representación alineada con la jerarquía taxonómica — [BioCLIP](https://arxiv.org/abs/2311.18803)

### Inferences
- Diseño: salida = nodo más fino cuyo score calibrado supere un umbral por rango; si ninguno, "no sé" con petición de otra foto. Umbrales elegidos en una validación de otros sitios, no del mismo.
- Para abstención: temperature scaling + MSP/max-logit como baseline, y medir con curva riesgo-cobertura.

### Gaps
- No se leyó un paper específico de clasificación jerárquica con pérdida por rangos (p. ej. Bertinetto et al.). [SIN FUENTE]
- Los umbrales reales de SpeciesNet no se confirmaron en la documentación primaria.

## 3. Datos necesarios para etapa/sexo/salud

### Takeaway
No hay una cifra general de "mínimo viable" en las fuentes. Hay dos ejemplos concretos y un aviso fuerte: los datos de laboratorio no generalizan al campo.

### Cited Findings
- Edad y sexo en ciervo rojo (preprint 2026, un sitio, una especie): 4352 recortes etiquetados por expertos, 3392 imágenes de trampa cámara en el bosque Veldenstein (Alemania); mejores modelos 90.77% (edad) y 96.15% (sexo); los autores señalan que la literatura previa usaba imágenes de calidad más alta y consistente — [arXiv 2601.15813](https://arxiv.org/html/2601.15813v1) (cifras de resumen de búsqueda)
- Dataset de especie, sexo, clase de edad e ID individual con YOLO/EfficientNet (Mustafić et al. 2024); cifras de exactitud no verificadas — [Zenodo 13740674](https://zenodo.org/records/13740674)
- PlantVillage-like: CNN con 54,306 imágenes de hoja en condiciones controladas, 99.35% en test retenido (14 cultivos, 26 enfermedades); en imágenes de internet con otras condiciones cae a 31.4%; los autores concluyen que se necesita un conjunto más diverso — [Mohanty et al. 2016](https://arxiv.org/abs/1604.03169)
- PlantDoc: 2,598 imágenes, 13 especies, hasta 17 clases de enfermedad, ~300 horas humanas de anotación sobre imágenes de internet; mejora de clasificación hasta 31%; clases en train desde 54 hasta 137 imágenes en una versión; los conteos difieren entre versiones — [PlantDoc, ar5iv 1911.10317](https://ar5iv.labs.arxiv.org/html/1911.10317); [Dataset Ninja / resumen](https://datasetninja.com/plantdoc)
- iNaturalist tiene anotaciones de Life Stage y Sex mantenidas por administradores (evita campos inconsistentes), con Sex no aplicable a algunos grupos (hongos, plantas, varios invertebrados); se anotan con base en la evidencia de la observación — [iNaturalist anotaciones](https://www.inaturalist.org/pages/annotations)
- Los dos grupos de camera traps y generalización: ver sección 4 (Beery 2018).

### Inferences
- Fuente de etiquetas más barata: anotaciones de iNaturalist (etapa/sexo) como etiquetas ruidosas + verificación experta de una muestra.
- Dividir test por individuo y por sitio es obligatorio para no inflar resultados (ver Beery 2018); las cifras de ciervo rojo no cubren eso.
- Mínimo viable razonable (inferencia): cabezal sobre embedding congelado con cientos de ejemplos por clase y por taxón, validado en un sitio no visto. El número exacto es [SIN FUENTE].

### Gaps
- [SIN FUENTE]: acuerdo entre anotadores (kappa) para etapa/sexo/enfermedad; imágenes mínimas por clase; manejo de enfermedades raras (desbalance), más allá de la nota de BioCLIP 2 sobre desbalance taxonómico.

## 4. Pipelines de trampa cámara, ciencia ciudadana y campo

### Takeaway
Primero detector, luego clasificador. La generalización a sitios nuevos es el punto débil conocido.

### Cited Findings
- MegaDetector detecta animales, personas y vehículos, sirve para eliminar imágenes vacías, no identifica especie; entrenado con varios millones de imágenes de muchos ecosistemas; el código de clasificadores del repo está en gran parte obsoleto porque SpeciesNet los supera — [MegaDetector (GitHub)](https://github.com/agentmorris/MegaDetector)
- SpeciesNet usa detector + clasificador, con umbral de detección por defecto 0.1 y NMS IoU 0.5 en la API alojada (valores de la API, no de rollup) — [repo google/cameratrapai](https://github.com/google/cameratrapai)
- Camera Trap benchmark (20 cámaras): rendimiento muy bueno en sitios de entrenamiento, caída fuerte en sitios nuevos, especialmente en clasificación — [Beery et al. 2018](https://arxiv.org/abs/1807.04975)
- En mushroom apps, la precisión se degrada con oclusión, mala luz, ejemplares limpios o inmaduros, y faltan señales no visibles en foto (olor, textura, sustrato, época) — [reporte citado en búsqueda](https://pubmed.ncbi.nlm.nih.gov/36794335/) (el segundo punto es del resumen de búsqueda, de una nota periodística)

### Inferences
- Puerta de calidad (desenfoque, oclusión, tamaño del sujeto en el recorte) antes del clasificador y solicitud de segunda foto/órgano cuando falle; los umbrales de desenfoque son [SIN FUENTE].

### Gaps
- No se encontró fuente primaria para métricas de calidad de imagen ni para el flujo "pedir otra foto" en apps de ciencia ciudadana.

## 5. Segmentación de lesiones/síntomas (SAM)

### Takeaway
SAM es promptable y zero-shot, pero para lesiones o imágenes médicas la evidencia citada apunta a modelos adaptados, no al SAM general.

### Cited Findings
- SAM: más de mil millones de máscaras en 11 millones de imágenes; promptable; transfiere zero-shot, a menudo igualando métodos supervisados — [Kirillov et al. 2023](https://arxiv.org/abs/2304.02643)
- MedSAM, adaptado con 1,570,263 pares imagen-máscara en 10 modalidades; se evaluó contra especialistas por modalidad. El abstract dice que los métodos médicos previos "carecen de generalidad" — [arXiv 2304.12306](https://arxiv.org/abs/2304.12306)
- PlantDoc enmarca la enfermedad como detección de objetos en condiciones naturales — [PlantDoc](https://ar5iv.labs.arxiv.org/html/1911.10317)

### Inferences
- SAM puede servir para proponer máscaras de hoja/lesión con un punto o caja; la calidad en lesiones de plantas o piel animal no se verificó. [SIN FUENTE]

### Gaps
- No se encontró evaluación de SAM sobre lesiones de plantas/animales silvestres ni sus modos de falla en esos dominios.

## 6. Evaluación

### Takeaway
Reportar métricas por clase, calibración y rendimiento en sitios no vistos; el resultado en el mismo sitio engaña.

### Cited Findings
- Brecha de generalización por sitio — [Beery 2018](https://arxiv.org/abs/1807.04975); por condiciones de captura — [Mohanty 2016](https://arxiv.org/abs/1604.03169)
- Calibración — [Guo 2017](https://arxiv.org/abs/1706.04599); selectividad riesgo-cobertura — [Geifman 2017](https://arxiv.org/abs/1705.08500); rechazo/OOD — [Hendrycks 2016](https://arxiv.org/abs/1610.02136), [Vaze 2021](https://arxiv.org/abs/2110.06207)
- Accuracy por clase puede diferir entre grupos sexo-edad aunque el total parezca alto (afirmación de resumen de búsqueda sobre encuestas de venados, sin verificar en fuente primaria) — [Elliott et al., Wildlife Research 2023](https://deerlab.auburn.edu/files/2024/02/2023-Wildlife-Research-Elliott-et-al.-ISSUE-7-a8e70824f0db5d43.pdf)

### Inferences
- Reglas de reporte: top-1/top-k por rango, F1 por clase y matriz de confusión, AUROC de aceptar/rechazar, ECE antes y después de temperature scaling, cobertura a riesgo fijo, división por individuo y sitio, y intervalos de confianza (el estudio de micología muestra IC muy anchos con 78 muestras).

### Gaps
- [SIN FUENTE]: definición estándar de ECE con número de bins recomendado en esta literatura (no leído el cuerpo de Guo 2017).

## 7. Límites éticos y de seguridad

### Takeaway
Es un apoyo, no un diagnóstico. Los hongos comestibles y las enfermedades notificables son los riesgos más claros.

### Cited Findings
- Estudio toxicológico (78 especímenes de exposiciones reales): la mejor de tres apps acertó 49% (IC 0-100) y ninguna superó ese nivel; para tóxicas, 44% la mejor app; Amanita phalloides fue identificada erróneamente en tres casos; muestras pequeñas, IC muy anchos — [Clin Toxicol 2023, PubMed 36794335](https://pubmed.ncbi.nlm.nih.gov/36794335/)
- Los autores observaron aumento de intoxicaciones por identificar mal tóxicas como comestibles; la recomendación es confirmar con micólogo o centro de toxicología — [resumen de búsqueda sobre el mismo estudio](https://pubmed.ncbi.nlm.nih.gov/36794335/)
- iNaturalist oculta coordenadas por geoprivacidad o por taxón amenazado (campo coordinates_obscured) — [iNaturalist, ayuda](https://help.inaturalist.org/en/support/solutions/articles/151000191830)
- Los miembros de WOAH deben notificar enfermedades listadas vía WAHIS; las de fauna silvestre no listadas se reportan voluntariamente (WAHIS-Wild); la lista se actualiza cada año — [WOAH WAHIS](https://www.woah.org/en/what-we-do/animal-health-and-welfare/disease-data-collection/world-animal-health-information-system/)

### Inferences
- Para hongos: no emitir "comestible"; mostrar solo identificación con incertidumbre y advertencia explícita. Para especies amenazadas: no publicar coordenadas exactas. Para sospecha de enfermedad notificable en animales: derivar a autoridad veterinaria/sanitaria; la obligación concreta por país es [SIN FUENTE] (hay que revisar la normativa de Colombia/ICA u otra).

### Gaps
- No se verificó la norma nacional aplicable ni las listas de taxones amenazados a ocultar.

## 8. Tabla de decisión: organismo x pregunta

### Takeaway
Viabilidad desde foto: plantas, aves y mamíferos grandes ofrecen más; hongos e invertebrados pequeños dependen de caracteres no visibles. Casi toda la tabla es inferencia con respaldo parcial; las celdas sin respaldo van marcadas.

### Cited Findings
Leyenda: Sí / Parcial / Lab = necesita laboratorio. Método = qué usar. Respaldo entre paréntesis.

| Organismo | Especie | Etapa | Sexo | Edad | Enfermedad/salud |
|---|---|---|---|---|---|
| Mamíferos medianos/grandes (trampa cámara) | Sí: MegaDetector + SpeciesNet ([repo](https://github.com/google/cameratrapai)) | Parcial: cabezal sobre recorte [SIN FUENTE] | Parcial: solo en dimorfismo visible; ciervo rojo 96.15% en un sitio ([arXiv 2601.15813](https://arxiv.org/html/2601.15813v1)) | Parcial: ciervo rojo 90.77% en un sitio (mismo) | Parcial/Lab: lesiones visibles solamente [SIN FUENTE]; notificación a autoridad |
| Aves | Sí: BioCLIP-like; sexo evaluado en NABirds ([BioCLIP 2](https://arxiv.org/html/2505.23883)) | Parcial: etapa en NeWT (mismo) | Parcial: depende de dimorfismo; embedding separa variantes (mismo) | Parcial [SIN FUENTE] | Parcial/Lab [SIN FUENTE] |
| Reptiles/anfibios | Parcial [SIN FUENTE] | Parcial (larva/adulto vía anotaciones iNat, [iNat](https://www.inaturalist.org/pages/annotations)) | Parcial [SIN FUENTE] | Lab/Parcial [SIN FUENTE] | Lab [SIN FUENTE] |
| Insectos y arácnidos | Parcial (rasgos microscópicos a veces necesarios) [SIN FUENTE] | Sí/Parcial (larva/adulto, anotación iNat) | Parcial [SIN FUENTE] | Lab [SIN FUENTE] | Lab [SIN FUENTE] |
| Plantas | Sí/Parcial: embedding tipo BioCLIP + pedir órgano adicional [SIN FUENTE para el flujo] | Parcial: fenología [SIN FUENTE] | No aplica en general (iNat excluye plantas del sexo, [iNat](https://www.inaturalist.org/pages/annotations)) | Lab/No [SIN FUENTE] | Parcial: lab 99.35%, campo 31.4% ([Mohanty](https://arxiv.org/abs/1604.03169)); PlantDoc, 40.4 en BioCLIP 2 ([BioCLIP 2](https://arxiv.org/html/2505.23883)); Lab para confirmar patógeno |
| Hongos | Parcial/Lab: apps 49% como mejor caso en 78 especímenes ([Clin Toxicol](https://pubmed.ncbi.nlm.nih.gov/36794335/)) | Parcial [SIN FUENTE] | No aplica (iNat excluye hongos del sexo) | No | Lab; nunca declarar comestibilidad |
| Peces y vida acuática | [SIN FUENTE] | [SIN FUENTE] | [SIN FUENTE] | [SIN FUENTE] | [SIN FUENTE] |
| Microorganismos | Lab (BioCLIP 2 reconoce ≤~12 imágenes para microscópicos, [BioCLIP 2](https://arxiv.org/html/2505.23883)) | No | No | No | Lab |

Método por defecto en todas las celdas "Parcial": embedding compartido congelado + cabezal por taxón y pregunta, calibración con temperature scaling, abstención con rollup taxonómico y umbral tomado de validación en sitios no vistos, y solicitud de nueva foto cuando el control de calidad falle.

### Inferences
- "Parcial" se asigna cuando existe evidencia de que el rasgo puede ser visible en algunos taxones pero no hay validación general; es juicio del investigador, no resultado de un paper.

### Gaps
- Reptiles, anfibios, peces e invertebrados: no se encontraron fuentes en esta ronda; recomendable una segunda búsqueda dirigida por grupo.
- Falta evidencia específica de salud animal desde foto.
