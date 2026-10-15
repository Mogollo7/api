# Plantas, hongos e invertebrados (insectos/plagas): identificación, etapa, edad, sexo y enfermedad/daño desde fotografías

Nota: prosa en español, nombres científicos exactos. Todo lo no verificado en fuente se marca [SIN FUENTE]. Se buscaron ~16 llamadas; varias páginas primarias (Pl@ntNet docs, PMC, CVPR PDF) no fueron accesibles, así que algunas cifras vienen de resúmenes secundarios y se indica.

## 1. Plantas: especie, fenología (BBCH), edad, sexo; qué hacen Pl@ntNet e iNaturalist

### Takeaway
La especie se identifica mejor combinando varios órganos (hoja, flor, fruto, corteza); la fenología se codifica con la escala BBCH (0–9); la edad por anillos exige un tarugo (increment borer) y no sale de una foto; el sexo en especies dioicas se lee en las flores.

### Cited Findings
- Pl@ntNet acepta de 1 a 4 fotos de la misma planta, con al menos una de hoja, flor, fruto o corteza; cada foto se etiqueta con el órgano; flores, frutos y hojas son los órganos más característicos; una foto de planta entera da contexto pero a menudo no basta; detalles como espinas, yemas o pelos del tallo ayudan a separar especies de un mismo género. — [Resumen de páginas identify de Pl@ntNet (vía búsqueda)](https://identify.plantnet.org/he/salad/identify)
- Pl@ntNet compara contra una base de imágenes validadas por la comunidad (se incorporan al alcanzar un promedio de tres estrellas/votos) y se describe como capaz de reconocer unas 20 000 especies; el método interno de fusión de órganos no aparece en las fuentes encontradas. — [Techlicious](https://www.techlicious.com/blog/plantnet-app-plant-identification-recognition/); [Gizmodo](https://gizmodo.com/download/plantnet-plant-identification)
- iNaturalist entrena su modelo de visión con fotos propias de la comunidad; desde 2023 incorpora la ubicación (geomodelo y mapas de rango); entrena un modelo completo aprox. una vez al año con actualizaciones intermedias por transfer learning; la insignia "en el modelo" aplica solo a especies; no pretende ser un clasificador taxonómico autoritativo (se sugiere tratar sus sugerencias como las de un aficionado entusiasta). — [iNaturalist, New computer vision model](https://www.inaturalist.org/posts/69193-new-computer-vision-model); [iNaturalist grant](https://www.inaturalist.org/blog/113184-inaturalist-receives-grant-to-improve-species-suggestions)
- Un comentario de foro (no oficial) indica que el umbral de inclusión pasó a 100 fotos en lugar de 100 observaciones. — [Foro iNaturalist](https://forum.inaturalist.org/t/did-computer-vision-get-worse-lately/21501?page=2)
- BBCH: monografía "Growth stages of mono- and dicotyledonous plants" (ed. Uwe Meier, 1997; 2.ª ed. 2001), código decimal de 2 dígitos con 10 estadios principales (0–9) y secundarios (0–8), basado en el código de cereales de Zadoks; reeditado digitalmente por el JKI (CC BY 4.0). — [Catálogo HathiTrust](https://catalog.hathitrust.org/Record/009138910); [Kulturpflanzenjournal/JKI, historia BBCH](https://ojs.openagrar.de/index.php/Kulturpflanzenjournal/article/view/12142/11080); [OpenAgrar PDF](https://www.openagrar.de/servlets/MCRFileNodeServlet/openagrar_derivate_00016780/BBCH%20ENGLISCH_%20.pdf)
- Los estadios principales BBCH (0 germinación/brotación, 1 desarrollo de hojas, 2 brotes laterales/macollamiento, 3 elongación del tallo, 4 partes vegetativas cosechables, 5 emergencia de inflorescencia, 6 floración, 7 desarrollo del fruto, 8 maduración, 9 senescencia) fueron dados por la fuente de búsqueda como conocimiento general, no leídos del PDF; verificar en el PDF antes de publicar. — [BBCH PDF OpenAgrar](https://www.openagrar.de/servlets/MCRFileNodeServlet/openagrar_derivate_00016780/BBCH%20ENGLISCH_%20.pdf) [verificación pendiente]
- Edad: el tarugo con barrena de incremento permite contar anillos sin talar; un núcleo puede engañar (anillos múltiples en años seco-húmedos, anillos ausentes en años muy secos), se corrige con datación cruzada, y la barrena a veces no alcanza la médula, hay que estimar anillos faltantes. — [NHPR](https://www.nhpr.org/something-wild/2017-08-04/something-wild-what-we-learn-from-a-tree-core); [NIST](https://www.nist.gov/node/1875776); [Britannica](https://www.britannica.com/print/article/157598)
- Sexo en dioicas: pistilo (ovario, estilo, estigma) = planta femenina; anteras con polen = masculina; se requiere ver prefloración o floración; algunas especies tienen flores hermafroditas. Fuente de baja calidad (sitios de contenido), usar solo como principio general. — [Resultados de búsqueda sobre sexado de plantas](https://sparc.arl.org/?p=23968) [fuente débil]; [Genomics of sex determination in dioecious trees (FAO AGRIS)](https://agris.fao.org/search/zh/records/65de39fb7c7033e84bea1a3c)

### Inferences
- Método práctico: pedir 2–4 fotos con órganos distintos y etiquetarlas; la fecha y la ubicación sirven de prior (iNaturalist usa geomodelo).
- Desde una foto se puede estimar la clase de edad relativa (plántula/juvenil/adulto por tamaño y presencia de estructuras reproductivas), no la edad en años; para leñosas reportar "no determinable desde foto".
- El sexo solo es inferible si hay flores/estructuras reproductivas visibles y la especie es dioica; si no, devolver "indeterminado".

### Gaps
- Documentación técnica de Pl@ntNet (arquitectura, fusión de órganos, exactitud) no accesible; no se obtuvo cifra de exactitud.
- Reglas oficiales de "grado de investigación" de iNaturalist y manejo de estadios juveniles: no encontradas.
- Texto exacto de cada estadio BBCH no leído directamente.

## 2. Enfermedad y estrés vegetal desde fotos; fallo en campo; confirmación de laboratorio

### Takeaway
Los modelos entrenados con imágenes de laboratorio colapsan en campo: Mohanty et al. (2016) reportan 99,35 % en test de PlantVillage frente a 31,4 % en imágenes de otras condiciones. Mejoras documentadas: más imágenes de campo y segmentar lesiones individuales (Barbedo 2019: +12 % de exactitud media).

### Cited Findings
- Mohanty, Hughes y Salathé: 54 306 imágenes de hojas sanas y enfermas bajo condiciones controladas, 14 especies de cultivo y 26 enfermedades; exactitud de 99,35 % en conjunto de prueba retenido; 31,4 % en imágenes de fuentes en línea tomadas en condiciones distintas a las de entrenamiento; línea base aleatoria 2,6 %. — [arXiv 1604.03169](https://arxiv.org/abs/1604.03169)
- Hughes y Salathé (2015): repositorio abierto PlantVillage con más de 50 000 imágenes curadas de hojas sanas e infectadas; una fuente secundaria da 54 309 imágenes (no verificado en texto completo); motivación: pérdidas por enfermedad promedio de 40 % del rendimiento potencial. — [arXiv 1511.08060](https://arxiv.org/abs/1511.08060v2); [TFDS plant_village](https://www.tensorflow.org/datasets/catalog/plant_village)
- Barbedo (2016), Biosystems Engineering 144:52–60: revisión de retos; las técnicas tienden a ser de alcance estrecho y necesitan condiciones de captura ideales; el abstract no detalla la lista completa de retos (texto completo no leído). — [Embrapa registro](https://www.bdpa.cnptia.embrapa.br/consulta/marc?id=1040545); [PDF Embrapa](https://www.alice.cnptia.embrapa.br/alice/bitstream/doc/1083285/1/AutomaticSBIAgro.pdf)
- Barbedo (2017): distingue detección de reconocimiento; reconocer es más difícil, sobre todo si debe identificar todos los trastornos posibles de una planta. — [resumen vía búsqueda](https://www.alice.cnptia.embrapa.br/handle/doc/1083285?locale=en)
- Barbedo (2019), Biosystems Engineering 180:96–107: clasificar lesiones/manchas individuales en lugar de la hoja entera aumentó la exactitud en promedio 12 % frente a las imágenes originales; ningún cultivo bajó de 75 % incluso con hasta 10 enfermedades; permite detectar varias enfermedades en una hoja; limitación: la segmentación de síntomas aún era manual. — [Embrapa registro](https://www.bdpa.cnptia.embrapa.br/consulta/marc?id=1106065)

### Inferences
- Clases de síntomas visibles a manejar (mancha, clorosis, marchitez, roya, oídio, deficiencia nutricional, daño de plaga): [SIN FUENTE] en este lote de búsquedas; usar como taxonomía de diseño, no como afirmación citada.
- Niveles de análisis recomendados: lesión (segmentada) > hoja > rama > planta entera, combinando órganos y contexto (cultivo, huésped, clima, ubicación).
- Una predicción de enfermedad desde foto debe devolverse como "sospecha" con confianza baja si la imagen es de campo, dado el 31,4 % de Mohanty.
- Confirmación en laboratorio (PCR, cultivo, serología): [SIN FUENTE] en estas búsquedas; indicar como "no confirmable con foto" sin cifras.

### Gaps
- Sin fuente sobre síntomas confundibles (virus vs deficiencia nutricional) ni sobre PCR/cultivo.
- No se verificó que Mohanty 2016 use la etiqueta "PlantVillage" en el abstract (la página no lo nombra; Hughes & Salathé sí describen PlantVillage como repositorio de ~54 k imágenes).

## 3. Insectos y plagas: estadios, dificultad larval, dimorfismo, daño, IP102, trampas, bases huésped-plaga

### Takeaway
Metamorfosis completa (huevo-larva-pupa-adulto) vs incompleta (huevo-ninfa-adulto); IP102 (75 222 imágenes, 102 clases) es difícil: ResNet-50 afinado llega a ~49,4 % de exactitud. Las trampas de luz y pegajosas funcionan para conteo y clasificación en escenarios acotados; EPPO y CABI aportan relaciones huésped-plaga.

### Cited Findings
- Metamorfosis completa: 4 estadios (huevo, larva, pupa, adulto); la larva suele ser muy distinta del adulto y comer otro alimento; la pupa no se alimenta. Incompleta: 3 estadios (huevo, ninfa, adulto), sin pupa; ninfas parecidas al adulto, sin alas desarrolladas, cada muda se acerca al adulto; ejemplos: saltamontes, chinches, libélulas. Holometabolos son más del 80 % de las especies de insectos (cita de una tesis). — [Texas A&M AgriLife/Travis TX](https://travis-tx.tamu.edu/?p=16290); [New World Encyclopedia, Holometabolous](https://www.newworldencyclopedia.org/entry/Holometabolous); [Senckenberg, Hemimetabola](https://senckenberg.de/en/institutes/senckenberg-german-entomological-institute-muencheberg/systematics-and-biogeography/hemimetabola)
- IP102 (Wu et al., CVPR 2019): 75 222 imágenes en 102 clases, distribución de cola larga, ~19 000 imágenes con cajas delimitadoras, taxonomía jerárquica por cultivo afectado; promedio de 737 imágenes por clase; dificultades: varianza inter e intra-clase y desbalance. — [Cardiff ORCA](https://orca.cardiff.ac.uk/121533); [mmcheng.net/ip102](https://mmcheng.net/ip102/); [Review Crop Pest Classification, arXiv 2507.01494](https://arxiv.org/pdf/2507.01494)
- Exactitud de línea base en IP102 (según reseña secundaria, tabla original no leída): ResNet-50 afinado desde ImageNet 49,4 % (F1 40,1; GM 31,5); ResNet desde cero 35,7 %; AlexNet 41,8 % afinado vs 35,3 % desde cero. — [Liner review de IP102](https://liner.com/review/ip102-largescale-benchmark-dataset-for-insect-pest-recognition)
- Trampa de luz automática para polillas (Bjerge et al.): >250 000 imágenes en 48 noches; F1 de validación 0,93 (CNN, 2000 imágenes, 8 clases) en versión publicada; F1 de seguimiento+clasificación 0,71 y tasa de detección de seguimiento 0,79; el preprint reportó otras cifras (864 imágenes, F1 0,96). — [PMC7825571](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7825571/); [bioRxiv](https://www.biorxiv.org/content/10.1101/2020.03.18.996447v2)
- CSIRO desarrolla trampa de luz UV con fondo blanco y cámara Raspberry Pi para detectar polillas de Spodoptera frugiperda (gusano cogollero). — [CSIRO](https://research.csiro.au/agroecology/fall-armyworm-identification-light-trap-cameras)
- Trampas pegajosas: conteo de moscas blancas con error medio ~9 % frente a humanos (Ciampi et al.); estudio con CNN de 1 739 imágenes y 95,8 % de exactitud en polillas vs otros insectos; el color de la trampa y el dispositivo de captura afectan mucho el rendimiento. — [Frontiers Plant Sci. 2024](https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2024.1484587/pdf); [PMC8396445](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8396445/)
- EPPO Global Database: información básica de >98 500 especies y datos regulatorios de >1 900 plagas; por plaga da distribución, plantas huésped y categorización cuarentenaria; incluye fichas (datasheets), informes PRA y estándares. — [EPPO Global Database](https://gd.eppo.int/); [EPPO resources](https://eppo.int/RESOURCES/eppo_databases/global_database)
- CABI Crop Protection Compendium: fichas con identidad, distribución, huéspedes, síntomas, biología, enemigos naturales, impacto y control; la atribución del listado al Compendium es probable, no confirmada. — [CABI en Hugging Face](https://huggingface.co/datasets/CABInternational/Palm-Weevil-Content)

### Inferences
- La identificación de larvas a especie desde foto es más difícil que de adultos porque la larva difiere del adulto; dado el 49,4 % en IP102, devolver género/familia o "grupo de plaga + huésped" cuando la confianza sea baja.
- Con la plaga ausente, usar firmas de daño (agallas, minas, perforaciones, frass) cruzadas con huésped en EPPO/CABI como filtro de candidatos; la lista de firmas en sí es [SIN FUENTE] en esta ronda.
- Dimorfismo sexual en insectos: [SIN FUENTE]; no afirmar sexo salvo en especies con dimorfismo documentado.

### Gaps
- Plantwise Knowledge Bank: sin resultados.
- No se obtuvo el PDF original de IP102 (HTTP 403); cifras vienen de reseñas.
- Sin fuente sobre dimorfismo sexual ni sobre daños específicos (agallas, minas).

## 4. Hongos: cuerpo fructífero, seguridad de edibilidad, ITS, esporas

### Takeaway
La identificación fotográfica no es segura para decidir edibilidad: las apps fallan con frecuencia en especies tóxicas. El código de barras de ADN oficial para hongos es la región ITS (Schoch et al. 2012), una técnica de laboratorio.

### Cited Findings
- Estudio australiano (Victorian Poisons Information Centre): 78 hongos de exposiciones reales con micólogo experto; Picture Mushroom acertó 49 %, Mushroom Identificator 35 %, iNaturalist 35 %; en tóxicos Picture Mushroom 44 %; Amanita phalloides fue identificada erróneamente por dos apps; se señaló aumento de intoxicaciones tras identificar mal especies tóxicas como comestibles. — [PubMed 36794335](https://pubmed.ncbi.nlm.nih.gov/36794335/)
- Centro de Toxicología belga: de 162 hongos (38,9 % tóxicos), sin editar la foto 8,0 % dio identificación fiable (correcta en 76,9 %); tras redimensionar 31,5 % dio identificación fiable (correcta en 52,9 %); 44,4 % de los tóxicos se clasificó mal como no tóxico o comestible. — [EAPCCT 2022 abstract](https://www.antigifcentrum.be/app/uploads/2025/11/EAPCCT-2022-identification-of-mushrooms.pdf)
- Las autoridades de Victoria indican que no existe prueba casera que distinga comestibles de venenosos. — [SGST / aviso](https://www.sgst.com.au/mushroom-foragers-warned-against-using-ai-apps-for-identification/)
- ITS como código de barras universal de hongos: consorcio multilaboratorio evaluó seis regiones; COI se descartó (difícil de amplificar, intrones, variabilidad insuficiente); los genes codificantes de proteína tuvieron a menudo mayor identificación correcta pero bajo éxito de PCR/secuenciación; ITS tuvo la mayor probabilidad de identificación exitosa y el "barcode gap" más claro; LSU mejor en algunos grupos (levaduras ascomicetos, linajes basales); SSU de baja resolución. Crítica de Kiss (2012): ITS no discrimina bien muchas especies cercanas. — [Schoch et al. 2012, PNAS](https://www.fabinet.up.ac.za/publication/pdfs/1755-schoch_et_al_2012_pnas.pdf); [ADS](https://ui.adsabs.harvard.edu/abs/2012PNAS..109.6241S/abstract)

### Inferences
- Política para una guía: nunca devolver "comestible" desde foto; devolver género/grupo probable, órganos a fotografiar adicionales (himenio, píldeo, estípite, volva, anillo) y aviso de consulta a micólogo/centro toxicológico. La lista de estructuras diagnósticas es [SIN FUENTE] aquí.
- La germinación de esporas es observación de laboratorio: [SIN FUENTE] en búsquedas; no inferible de fotos de campo.

### Gaps
- Estudio npj Science of Food (12 herramientas) solo visto en prensa, no incluido.
- No hay fuente específica sobre germinación de esporas.

## 5. Abejas melíferas y otros insectos: enfermedad y ML publicado

### Takeaway
Hay literatura de ML para varroa (Varroa destructor) en abejas y tableros pegajosos; no se encontró literatura de imágenes para loque americana/europea ni cría yesificada (ascosferosis).

### Cited Findings
- Estudio de 2021 con 600 imágenes anotadas de abejas sanas e infestadas: YOLO y SSD (y Deep SVDD) lograron F1 hasta 0,874 en abeja infestada y 0,714 en detección del ácaro mismo. — [Macquarie Univ.](https://researchers.mq.edu.au/en/publications/bee-disease-varroa-prediction-utilizing-convolutional-neural-netw/); [Uniroma1](https://www.diag.uniroma1.it/publication/29532)
- Detección en tableros pegajosos fotografiados con smartphone: problema de objetos pequeños; software VarroDetector (YOLO v11 Nano) probado en campo. — [Univ. La Rioja HAIS 2023](https://www.unirioja.es/cu/jodivaso/publications/2023/HAIS_23_varroa.pdf); [PMC12390549](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12390549/)
- Vit4V clasifica clips de video de pecoreadoras para mitigar desenfoque y oclusión; con pocos datos el aprendizaje profundo suele rendir peor (Ghezal y König, 2025, imágenes hiperespectrales). — [PMC12390549](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12390549/); [Unizar](https://zaguan.unizar.es/record/136072/files/texto_completo.pdf)

### Inferences
- Signos visibles de loque americana, loque europea y cría yesificada: [SIN FUENTE] en este lote; no incluir sin consulta a fuente (p. ej. OIE/WOAH, FAO).

### Gaps
- Sin fuentes sobre loque americana/europea, cría yesificada, ni ML para ellas.

## 6. Foto de mala calidad: alternativas

### Takeaway
No hay fuente directa; la estrategia se deriva de lo citado.

### Cited Findings
- Pl@ntNet recomienda varias fotos de órganos distintos y la planta entera solo da contexto. — [Resumen Pl@ntNet](https://identify.plantnet.org/he/salad/identify)
- La segmentación de lesiones mejora la exactitud en 12 % (Barbedo 2019) y los modelos fallan fuera de condiciones de entrenamiento (31,4 %, Mohanty 2016). — [Embrapa](https://www.bdpa.cnptia.embrapa.br/consulta/marc?id=1106065); [arXiv](https://arxiv.org/abs/1604.03169)
- iNaturalist usa ubicación como prior (geomodelo). — [iNaturalist blog](https://www.inaturalist.org/blog/113184-inaturalist-receives-grant-to-improve-species-suggestions)
- Foto en trampa pegajosa: color de trampa y dispositivo afectan resultados. — [Frontiers 2024](https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2024.1484587/pdf)

### Inferences
- Cascada propuesta: (1) evaluar calidad; (2) si no basta, analizar estado de rama/planta o el daño; (3) pedir segunda foto o otro órgano (flor/fruto/envés de hoja/planta entera); (4) usar priors de contexto (ubicación, fecha/fenología, huésped, EPPO/CABI); (5) responder en nivel taxonómico superior con confianza declarada; (6) para hongos, negar edibilidad. Es diseño propuesto, no hallazgo de fuente.

### Gaps
- Sin estudio que valide esta cascada.
