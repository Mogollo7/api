# Cierre de vacíos: guía de identificación de especies con IA

> Convención: todo dato lleva fuente inline. Lo no verificado va marcado **[SIN FUENTE]**. Las tablas sólo contienen números leídos en la fuente citada.

## 1. Caracteres que separan anuros crípticos/parecidos (Pristimantis, Rhinella, Dendropsophus, Boana)

### Takeaway
Sí: en descripciones taxonómicas recientes de anuros neotropicales, el color del iris, los colores ocultos de ingle/muslo (flash colors), el patrón y la extensión de la membrana interdigital y, sobre todo, el canto de anuncio aparecen como caracteres diagnósticos explícitos. Casi siempre se usan combinados, y en complejos crípticos el desempate lo dan el canto o el ADN (16S).

### Cited Findings
- **Pristimantis, ingle y muslos ocultos:** en el grupo de *P. phoxocephalus* las superficies ocultas de los muslos son amarillas con reticulaciones oscuras. Eso lo separa de *P. atillo*, que tiene la ingle naranja, y de otras especies parecidas con ingles en tonos marrones — [ZooKeys 868, tratamiento 8](https://pmc.ncbi.nlm.nih.gov/articles/instance/6687670/bin/zookeys.868.26766-treatment8.xml)
- **Pristimantis, ingle más canto:** *P. jimenezi* se diferencia de *P. phoxocephalus* por el color de la ingle y por diferencias en el canto de anuncio. La misma descripción usa el iris (cobrizo rojizo con reticulaciones negras) — [ZooKeys 868, tratamiento 5](https://pmc.ncbi.nlm.nih.gov/articles/instance/6687670/bin/zookeys.868.26766-treatment5.xml)
- **Pristimantis, flash colors:** una especie peruana se reconoce por la ingle, la parte posterior de los muslos y las canillas de color rojo brillante — [ZooKeys (preview id 8507)](https://zookeys.pensoft.net/article_preview.php?id=8507)
- **Pristimantis, iris:** una especie de la Serranía del Baudó (Colombia) se diagnostica en parte por el iris cobrizo o bronce rojizo con finas reticulaciones negras y la esclerótica azul claro — [Zootaxa (mapress 56780)](https://mapress.com/zt/article/view/56780)
- **Pristimantis, ausencia de flash color como carácter:** la redescripción de *P. marmoratus* incluye en la diagnosis la ausencia de coloración llamativa axilar/preaxilar, un iris con patrón cruzado y un lavado amarillo o verde pálido en la ingle — [European Journal of Taxonomy 397](https://europeanjournaloftaxonomy.eu/index.php/ejt/article/download/525/1178)
- **Pristimantis, canto en un complejo críptico:** en las especies crípticas del complejo *P. ockendeni* se combinaron la morfología, el canto (número de notas, duración y frecuencia dominante) y la coloración translúcida de la ingle en vida — [AGRIS/FAO](https://agris.fao.org/search/fr/records/682f1c6ed0cf3796e6211a7e)
- **Pristimantis de Guayana:** dos tipos de canto (de una y de tres notas) se usaron junto con la ingle amarilla y el iris gris — [Zootaxa (mapress 57576)](https://mapress.com/zt/article/view/57576)
- **Dendropsophus, saco vocal y canto:** *D. bilobatus* (grupo *D. microcephalus*, alto río Madeira) se distingue sobre todo por el saco vocal verde bilobulado y por un canto de 1–4 notas monofásicas con frecuencia dominante de unos 9 kHz — [Ferrão et al. 2020, ZooKeys](https://ppbio.inpa.gov.br/sites/default/files/Ferrao_M_et_al_2020_ZooKeys.pdf)
- **Dendropsophus, membrana interdigital:** una especie bromelícola de la Mata Atlántica se diagnostica por su tamaño pequeño, el patrón dorsal "enmarcado" y la membrana corta entre los dedos IV y V del pie. Su canto tiene dos notas (unos 5 kHz) — [CONICET Digital](https://repositoriosdigitales.mincyt.gob.ar/vufind/Record/CONICETDig_467c9b70e32054c149aa08b87e1744c0)
- **Dendropsophus, canto más ADN:** en una especie nueva del grupo *D. decipiens* los cantos van en series de 3–9 notas, con 9–29 pulsos por nota y frecuencia dominante de 5578–6422 Hz. Difiere al menos un 8 % en 16S de sus congéneres — [PMC8279364](https://pmc.ncbi.nlm.nih.gov/articles/PMC8279364)
- **Por qué la morfología sola falla:** en Dendropsophus la diversidad críptica se debe a la alta similitud fenotípica entre especies sumada al polimorfismo intraespecífico, y los métodos morfológicos tradicionales a menudo no la detectan — [PMC8279364](https://pmc.ncbi.nlm.nih.gov/articles/PMC8279364)

### Inferences
- Para una app de IA basada en fotos, el iris, la ingle y los muslos sólo son visibles si la foto los muestra (ingle y muslos requieren manipular al animal o que esté en salto o extensión). Si la foto no los muestra, la app debería pedir foto adicional o grabación del canto antes de dar la especie.
- En Dendropsophus el canto y el 16S son más decisivos que el color.

### Gaps
- **Boana:** no encontré en esta búsqueda una descripción con diagnosis explícita por patrón ventral, membrana o flash colors **[SIN FUENTE]**.
- **Rhinella:** no hay ejemplos sourced de separación de especies crípticas por iris o ingle **[SIN FUENTE]**. Lo que sí está documentado es que *R. horribilis* fue revalidada en 2016 al separar poblaciones antes llamadas *R. marina* — [Wikipedia, Rhinella horribilis](https://en.wikipedia.org/wiki/Rhinella_horribilis). Es fuente secundaria; el trabajo de 2016 no se consultó.
- No encontré una revisión general que cuantifique qué fracción de diagnosis neotropicales usa cada carácter **[SIN FUENTE]**.

## 2. Dimorfismo sexual en anuros; Rhinella marina / R. horribilis

### Takeaway
Bell & Zamudio (2012, *Proc. R. Soc. B* 279:4687–4693) documentaron dicromatismo sexual en más de 120 especies de ranas, de dos tipos: dinámico (cambio temporal del macho en reproducción) y ontogenético (cambio permanente a la madurez). En *R. marina* los adultos se distinguen por varias señales: el macho es más pequeño y amarillento-pardo, la hembra tiene manchas pardas irregulares, el macho lleva callos nupciales y espículas córneas en las verrugas en época reproductiva, y la distribución de las glándulas de toxina difiere entre sexos. Para *R. horribilis* no encontré datos específicos.

### Cited Findings
- "Over 120 species" con dicromatismo sexual documentado (Tabla 1 de Bell & Zamudio 2012) — [AmphibiaWeb, Bell: Sexual dichromatism](https://amphibiaweb.org/amphibian/dichromatism.html). La lista de especies está en [AmphibiaWeb, tablas](https://amphibiaweb.org/amphibian/dichromatism_tables.html).
- Desglose 31 dinámicas + 91 ontogenéticas = 122 especies. Esta cifra viene de una fuente secundaria que cita el artículo — [Froglife 2018](https://www.froglife.org/2018/01/); también en [Inside Ecology](https://insideecology.com/?p=6260). No la verifiqué contra la Tabla 1 original.
- El dicromatismo dinámico es "especialmente prevalente" en Ranidae, Bufonidae e Hylidae. El ontogenético se reparte en más taxones, sobre todo Hyperoliidae, Bufonidae e Hylidae. En el sapo neotropical *Incilius luetkenii* el cambio dura sólo unas horas — [AmphibiaWeb](https://amphibiaweb.org/amphibian/dichromatism.html)
- Un trabajo posterior liderado por Bell clasificó 178 especies como de dicromatismo dinámico. Es distinto del de 2012 — [Smithsonian Magazine](https://www.smithsonianmag.com/smithsonian-institution/color-changing-marvel-tree-frogs-looking-love-180964976/)
- **R. marina, color:** los machos adultos son más pequeños y de color pardo amarillento, con el amarillo más marcado en flancos y garganta. Hembras y machos inmaduros tienen manchas pardas irregulares en el dorso — [AmphibiaWeb, Rhinella marina](https://amphibiaweb.org/species/229)
- **R. marina, piel y callos:** ambos sexos tienen verrugas dispersas. En los machos sexualmente activos las verrugas llevan espículas córneas, y los machos tienen callos nupciales oscuros en los tres primeros dedos de la mano (Easteal 1963) — [AmphibiaWeb](https://amphibiaweb.org/species/229)
- **R. marina, tamaño:** las hembras pueden superar 225 mm de longitud hocico-cloaca (LHC), aunque la mayoría de los adultos mide 85–150 mm, y los machos son más pequeños — [AmphibiaWeb](https://amphibiaweb.org/species/229). Animal Diversity Web lista el dimorfismo como "sexes alike", lo que contradice lo anterior — [ADW](https://animaldiversity.org/accounts/bufo_marinus)
- **R. marina, glándulas:** los machos tienen parótidas más pequeñas y alargadas que las hembras, pero más glándulas en extremidades (sobre todo posteriores) y dorso. La diferencia persiste en sapos criados en cautiverio en condiciones estandarizadas — [PMC5677481](https://pmc.ncbi.nlm.nih.gov/articles/PMC5677481/)
- **Rhinella en general:** en *R. rubescens* y *R. schneideri* los machos tienen antebrazos más robustos y las hembras alcanzan mayor tamaño asintótico — [Copeia 103(2), 2015](https://bioone.org/journals/Copeia/volume-103/issue-2/CH-14-092/Sexual-Dimorphism-Growth-and-Longevity-of-Two-Toad-Species-Anura/10.1643/CH-14-092.full). En *R. inopina* los machos suelen tener coloración uniforme y las hembras más manchas amarillentas en los flancos (resultado de búsqueda; no verifiqué el texto completo).

### Inferences
- Patrón útil para la guía: "hembra/juvenil manchado, macho adulto más uniforme y amarillento" en *R. marina*. Ojo: un macho inmaduro también es manchado, así que el color solo no sexa.
- Callos nupciales y espículas sólo existen en machos en actividad reproductiva, así que su ausencia no prueba que el ejemplar sea hembra.

### Gaps
- No hay porcentaje de especies dicromáticas sobre el total de anuros en la fuente primaria consultada **[SIN FUENTE]**. No pude abrir el texto completo de PMC3497084.
- Dimorfismo en color de *R. horribilis*: no encontré descripción específica **[SIN FUENTE]**.

## 3. Identificación de renacuajos (Colombia/Neotrópico) y tabla de Gosner (1960)

### Takeaway
Para Colombia la referencia principal es la clave ilustrada de Lynch & Suárez (2011, *Caldasia*) para tierras bajas al oriente de los Andes. El barcoding con 16S está validado para renacuajos neotropicales. La tabla de Gosner tiene 46 estadios: 1–25 embrionarios/prealimentación y 26–46 larvales. Los rangos 26–30, 31–37/40 y 42–46 se definen por el miembro posterior y la metamorfosis de la cabeza.

### Cited Findings
- **Lynch & Suárez (2011), Caldasia:** clave ilustrada de renacuajos de tierras bajas al oriente de los Andes, con énfasis en Hylidae. Ilustra 41 especies, ocho de ellas antes desconocidas — [Caldasia/UNAL](https://revistas.unal.edu.co/index.php/cal/article/view/36389); [DOAJ](https://doaj.org/article/bc388c70acb347478957e98f66edf623). El mismo trabajo cita a Lynch (2006a) para los renacuajos de valles interandinos y el Caribe (no consultado).
- **Sphaenorhynchus:** Suárez-Mayorga & Lynch (2001) describieron las larvas de tres especies cerca de Leticia — [Caldasia/UNAL](https://revistas.unal.edu.co/index.php/cal/article/download/35499/35876/139318)
- **ADN, 16S:** Dubeux et al. (2022) analizaron 100 renacuajos de 12 localidades del noreste de Brasil. El 16S identificó las especies, y alrededor del 8 % de los renacuajos identificados por morfología estaban mal identificados — [SEDICI/MINCyT](https://repositoriosdigitales.mincyt.gob.ar/vufind/Record/SEDICI_6de338146ae5cc168fcda1adc7832a7d)
- La mayoría de los renacuajos tropicales siguen sin describir, y el barcoding se propone como vía rápida y barata — [PMC6808428](https://pmc.ncbi.nlm.nih.gov/articles/PMC6808428)
- **Gosner (1960)**, *Herpetologica* 16:183–190. Las frases siguientes se leyeron en el PDF del original — [copia del artículo](https://utkaluniversity.ac.in/wp-content/uploads/2022/06/Tadpole-stages-gosner-stage-1960-1.pdf):
  - "Stages 1 through 25 contain the embryonic or prefeeding series."
  - Los estadios 21–25 son la transición a renacuajo de vida libre y son "a difficult period for species identification". La alimentación independiente empieza en el estadio 25.
  - "Stages 26-30 are easily determined by the length/diameter relationship of the developing limb bud." En el estadio 31 el pie tiene forma de paleta, y del 31 al 37 aparecen los dedos individuales.
  - Los estadios 38–40 se distinguen por la proporción de los dedos y la aparición de tubérculos metatarsales y subarticulares (manchas claras en el 39, tubérculos en el 40). Los estadios 30–40 son un periodo de relativa estabilidad de los caracteres "clave".
  - En el estadio 41 la piel sobre los miembros anteriores se vuelve transparente. Los estadios 42–46 se reconocen por la metamorfosis de la cabeza (cambios en la boca): los miembros anteriores aparecen en el 42 y la metamorfosis está "essentially complete" en el 46.
- La forma del disco oral es diagnóstica a nivel de familia y está presente hacia el estadio 26 — [Gosner 1960](https://utkaluniversity.ac.in/wp-content/uploads/2022/06/Tadpole-stages-gosner-stage-1960-1.pdf)
- Categorías de McDiarmid & Altig (1999): embrión 1–~20, eclosionado ~21–24, renacuajo 25–41, metamorfo 42–46 — [Wikipedia, Gosner stage](https://en.wikipedia.org/wiki/Gosner_stage)

**Tabla para gráfico: rangos Gosner (1960)**

| Rango | Fase | Criterio principal (Gosner 1960) |
|---|---|---|
| 1–25 | Embrionaria / prealimentación | Segmentación → opérculo; alimentación desde el 25 |
| 26–30 | Larval: esbozo del miembro posterior | Relación largo/diámetro del esbozo |
| 31–37 | Larval: pie en paleta → dedos | Aparición de dedos individuales |
| 38–40 | Larval: dedos y tubérculos | Proporción de dedos; tubérculos metatarsal y subarticulares |
| 41 | Prometamorfosis | Piel transparente sobre miembros anteriores |
| 42–46 | Metamorfosis | Miembros anteriores emergen (42) → completa (46) |

### Inferences
- La agrupación del encargo ("dedos 31–41") es aproximada. En el original, 31–37 corresponde a los dedos, 38–40 a los tubérculos y 41 al inicio del clímax metamórfico.
- Para la app conviene que una foto de renacuajo antes del estadio 26 devuelva "no identificable" (Gosner advierte que 21–25 es difícil).

### Gaps
- No encontré una guía de campo nacional única ni un modelo de IA para renacuajos de Colombia **[SIN FUENTE]**.

## 4. Estadios principales BBCH 0–9 (Meier 2001)

### Takeaway
Los nombres exactos, leídos en la monografía *Growth stages of mono- and dicotyledonous plants. BBCH Monograph*, 2.ª ed., 2001, ed. Uwe Meier, son los de la tabla — [PDF BBCH (DAERA)](https://www.daera-ni.gov.uk/sites/default/files/2026-07/BBCH-Skala_en.pdf).

### Cited Findings

| Código | Estadio principal (texto original) | Traducción |
|---|---|---|
| 0 | Germination / sprouting / bud development | Germinación / brotación / desarrollo de yemas |
| 1 | Leaf development (main shoot) | Desarrollo de hojas (tallo principal) |
| 2 | Formation of side shoots / tillering | Formación de brotes laterales / ahijamiento |
| 3 | Stem elongation or rosette growth / shoot development (main shoot) | Elongación del tallo o crecimiento en roseta |
| 4 | Development of harvestable vegetative plant parts or vegetatively propagated organs / booting (main shoot) | Desarrollo de partes vegetativas cosechables / embuchado |
| 5 | Inflorescence emergence (main shoot) / heading | Emergencia de la inflorescencia / espigado |
| 6 | Flowering (main shoot) | Floración |
| 7 | Development of fruit | Desarrollo del fruto |
| 8 | Ripening or maturity of fruit and seed | Maduración del fruto y la semilla |
| 9 | Senescence, beginning of dormancy | Senescencia, inicio del reposo |

- La escala decimal se basa en el código de cereales de Zadoks et al. El primer dígito es el estadio principal y el segundo el secundario. Si dos estadios principales ocurren en paralelo, se pueden indicar ambos — [PDF BBCH](https://www.daera-ni.gov.uk/sites/default/files/2026-07/BBCH-Skala_en.pdf)

### Inferences
- El código 3 del encabezado general termina en "shoot development" y el texto del estadio añade "(main shoot)"; uso la forma del encabezado del capítulo.

### Gaps
- Ninguno.

## 5. Cómputo de los codificadores de imagen de BioCLIP 1 / 2 / 2.5

### Takeaway
- BioCLIP usa ViT-B/16, BioCLIP 2 usa ViT-L/14 y BioCLIP 2.5 Huge usa ViT-H/14, todos a 224 px.
- Según el CSV de perfiles de OpenCLIP, las torres de imagen tienen ~86 M, ~304 M y ~632 M parámetros, y su cómputo es ~35, ~162 y ~335 "GFLOPs" respectivamente.

### Cited Findings
- **Arquitecturas:**
  - BioCLIP: ViT-B/16, inicializado desde OpenAI CLIP, 224×224, TreeOfLife-10M — [HF imageomics/bioclip](https://huggingface.co/imageomics/bioclip)
  - BioCLIP 2: ViT-L/14 preentrenado en LAION-2B, TreeOfLife-200M (~214 M imágenes, 952 K taxones) — [HF imageomics/bioclip-2](https://huggingface.co/imageomics/bioclip-2)
  - BioCLIP 2.5 Huge: ViT-H/14 (OpenCLIP, LAION-2B), 224×224, TreeOfLife-200M actualizado con ~19 M imágenes más, 32 H100 durante 25 épocas — [HF imageomics/bioclip-2.5-vith14](https://huggingface.co/imageomics/bioclip-2.5-vith14)

**Tabla para gráfico: perfil de OpenCLIP (224 px)** — [open_clip docs/model_profile.csv](https://raw.githubusercontent.com/mlfoundations/open_clip/main/docs/model_profile.csv)

| Arquitectura (modelo BioCLIP) | Params totales (M) | Params torre imagen (M) | Params torre texto (M) | GFLOPs total | GFLOPs imagen | GFLOPs texto |
|---|---|---|---|---|---|---|
| ViT-B-16 (BioCLIP) | 149.62 | 86.19 | 63.43 | 41.09 | 35.13 | 5.96 |
| ViT-L-14 (BioCLIP 2) | 427.62 | 303.97 | 123.65 | 175.33 | 162.03 | 13.3 |
| ViT-H-14 (BioCLIP 2.5) | 986.11 | 632.08 | 354.03 | 381.68 | 334.59 | 47.09 |

### Inferences
- Que los pesos de BioCLIP tengan exactamente esos conteos es inferencia: las model cards no dan el conteo de parámetros, pero declaran la misma arquitectura OpenCLIP.
- Del B/16 al H/14 el cómputo de la torre de imagen se multiplica por unas 9,5 (335/35).

### Gaps
- No verifiqué si la columna "gflops" de OpenCLIP cuenta FLOPs reales o MACs (multiply-adds), así que no se puede afirmar que sean GMACs **[SIN FUENTE]**.

## 6. Pl@ntNet (multi-órgano, cobertura, precisión) e iNaturalist (taxones, Research Grade)

### Takeaway
- **Pl@ntNet:** acepta de 1 a 5 imágenes de la misma planta por consulta y devuelve especies con una puntuación de confianza. Cubre más de 77 000 especies según fuentes secundarias. No encontré cifras publicadas de precisión de la fusión multiórgano.
- **iNaturalist:** el modelo v2.26 cubre 111 435 taxones. "Research Grade" exige que más de 2/3 de los identificadores coincidan a nivel de especie.

### Cited Findings
- **API de Pl@ntNet:** se envían simultáneamente de 1 a 5 imágenes de la misma planta (cada una con su parámetro de órgano) y se recibe la lista de especies más probables con su puntuación — [resumen de my.plantnet.org/doc vía búsqueda](https://my.plantnet.org/doc). No pude abrir la página directamente (error DNS).
- El motor de identificación se describe en Affouard, Goëau, Bonnet, Lombardo & Joly, "Pl@ntNet app in the era of deep learning", ICLR 2017 (workshop). En junio de 2015 la app pasó de descriptores artesanales a CNN — [CIRAD](https://publications.cirad.fr/une_notice.php?dk=585562)
- Antes del aprendizaje profundo ya existía una estrategia de fusión "multi-plant-organ, multi-image and multi-feature" (Pl@ntNet Mobile 2014) — [HAL hal-01088819](https://hal.archives-ouvertes.fr/hal-01088819)
- **Cobertura de Pl@ntNet:** más de 77 000 especies — [Wikipedia](https://en.wikipedia.org/wiki/Pl@ntNet). Una página de terceros da unas 77 700 especies y más de 1300 millones de identificaciones a septiembre de 2025 (fuente débil) — [stork.ai](https://www.stork.ai/en/pl-ntnet)
- **Referencia de fusión (no es Pl@ntNet):** en un estudio con 101 especies la precisión top-1 fue del 77 % con la planta entera y del 97 % fusionando todas las perspectivas — [Plant Methods 2019](https://plantmethods.biomedcentral.com/track/pdf/10.1186/s13007-019-0462-4)
- **Modelo de iNaturalist:** la v2.26 tiene 111 435 taxones (la v2.25 tenía 109 680) y se entrenó con datos exportados el 19-10-2025 — [blog de iNaturalist (serie de releases)](https://www.inaturalist.org/blog/120349). Un taxón entra al modelo con unas 100 fotos y 60 observaciones — [blog de iNaturalist](https://www.inaturalist.org/blog/115962)
- **Research Grade:** requiere consenso de la comunidad a nivel de especie o inferior ("more than 2/3 of identifiers agree on a taxon at species-level"), o un consenso entre familia y especie más un voto de que no se puede mejorar. Las observaciones verificables quedan como "Needs ID" hasta alcanzarlo. "Casual" no es verificable (fecha, ubicación, silvestre o evidencia insuficientes) — [iNaturalist Help](https://help.inaturalist.org/en/support/solutions/articles/151000169936-what-is-the-data-quality-assessment-and-how-do-observations-qualify-to-become-research-grade-)

**Tabla para gráfico: taxones del modelo de visión de iNaturalist (2025)** — [blogs de iNaturalist](https://www.inaturalist.org/blog/115962)

| Versión | Taxones |
|---|---|
| 2.19 | 99 545 |
| 2.20 | 100 350 |
| 2.21 | 101 374 |
| 2.22 | 103 765 |
| 2.23 | 106 407 |
| 2.24 | 108 124 |
| 2.25 | 109 680 |
| 2.26 | 111 435 |

(Fuente: resumen de búsqueda de varias entradas del blog. El valor de la 2.24 sale citado en la entrada de la 2.25.)

### Inferences
- A la fecha de estas notas (oct-2026) probablemente exista una versión posterior a la 2.26.

### Gaps
- **Pl@ntNet:** no encontré el método exacto con que se combinan las puntuaciones de varias imágenes/órganos ni la precisión publicada (top-1/top-5) **[SIN FUENTE]**. Tampoco hay una cifra oficial actual de especies.

## 7. Datos para gráficos

### Takeaway
Las cuatro series tienen números verificados en fuente primaria: Mohanty 2016, Kumar 2022 (Tablas 1–2), las model cards de BioCLIP y EPPO/UF-IFAS para *F. occidentalis*.

### Cited Findings

**(a) Mohanty, Hughes & Salathé 2016 (PlantVillage)** — [Frontiers in Plant Science 7:1419](https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2016.01419/full)

El conjunto tiene 54 306 imágenes, 14 cultivos y 26 enfermedades (38 clases).

| Condición | Precisión |
|---|---|
| Test retenido (PlantVillage, laboratorio) | 99.35 % |
| Imágenes externas, dataset 1 (n = 121) | 31.40 % |
| Imágenes externas, dataset 2 (n = 119) | 31.69 % |

**(b) Kumar et al. 2022 (ICLR), "Fine-Tuning can Distort Pretrained Features…"** — [arXiv 2202.10054](https://arxiv.org/abs/2202.10054). Los valores son medias de 3 ejecuciones, leídas del PDF.

Tabla 1 (ID):

| Método | CIFAR-10 | Ent-30 | Liv-17 | DomainNet | FMoW | ImageNet | **Media ID** |
|---|---|---|---|---|---|---|---|
| FT | 97.3 | 93.6 | 97.1 | 84.5 | 56.5 | 81.7 | **85.1** |
| LP | 91.8 | 90.6 | 96.5 | 89.4 | 49.1 | 79.7 | **82.9** |
| LP-FT | 97.5 | 93.7 | 97.8 | 91.6 | 51.8 | 81.7 | **85.7** |

Tabla 2 (OOD):

| Método | STL | CIFAR-10.1 | Ent-30 | Liv-17 | DomainNet | FMoW | IN-V2 | IN-R | IN-Sketch | IN-A | **Media OOD** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FT | 82.4 | 92.3 | 60.7 | 77.8 | 55.5 | 32.0 | 71.5 | 52.4 | 40.5 | 27.8 | **59.3** |
| LP | 85.1 | 82.7 | 63.2 | 82.2 | 79.7 | 36.6 | 69.7 | 70.6 | 46.4 | 45.7 | **66.2** |
| LP-FT | 90.7 | 93.5 | 62.3 | 82.6 | 80.7 | 36.8 | 71.6 | 72.9 | 48.4 | 49.1 | **68.9** |

El orden de las cuatro columnas de ImageNet (V2, R, Sketch, A) es el de la lista de datasets del artículo. El texto extraído no mostró los encabezados de esa subtabla, así que conviene verificarlo en el PDF. LP-FT es el mejor en 5/6 datasets ID (la excepción es FMoW) y en 10/10 OOD.

**(c) Zero-shot de BioCLIP 1 vs 2 vs 2.5 (top-1 %, benchmark de las cards de BioCLIP 2 y 2.5)** — [HF bioclip-2](https://huggingface.co/imageomics/bioclip-2); [HF bioclip-2.5-vith14](https://huggingface.co/imageomics/bioclip-2.5-vith14)

| Modelo | NABirds | Plankton | Insects | Insects 2 | Camera Trap | PlantNet | Fungi | PlantVillage | Med. Leaf | Rare Species | **Media** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CLIP (ViT-L/14) | 66.5 | 1.3 | 9.0 | 11.7 | 29.5 | 61.7 | 7.6 | 6.5 | 25.6 | 35.2 | 25.5 |
| SigLIP | 61.7 | 2.4 | 27.3 | 20.7 | 33.7 | 81.8 | 36.9 | 28.5 | 54.5 | 47.6 | 39.5 |
| BioCLIP | 58.8 | 6.1 | 34.9 | 20.5 | 31.7 | 88.2 | 40.9 | 19.0 | 38.5 | 37.1 | 37.6 |
| BioCLIP 2 | 74.9 | 3.9 | 55.3 | 27.7 | 53.9 | 96.8 | 83.8 | 25.1 | 57.8 | 76.8 | 55.6 |
| BioCLIP 2.5 Huge | 75.8 | 5.2 | 68.2 | 30.8 | 58.7 | 96.9 | 84.9 | 33.5 | 73.2 | 85.5 | 61.3 |

(La extracción aplanó el encabezado de la tabla y las columnas se asignaron por orden.)

La card original de BioCLIP (v1) usa otro conjunto de pruebas: Birds 525 72.1, Plankton 6.1, Insects 34.8, Insects 2 20.4, PlantNet 91.4, Fungi 40.7, PlantVillage 24.4, Med. Leaf 38.6, PlantDoc 28.4, Rare Species 38.0, media 39.4 — [HF bioclip](https://huggingface.co/imageomics/bioclip). No se debe mezclar con la tabla anterior.

**(d) *Frankliniella occidentalis***

Desarrollo por temperatura, de huevo a huevo — [EPPO datasheet FRANOC](https://gd.eppo.int/taxon/FRANOC/datasheet):

| Temperatura | Ciclo huevo→huevo (días) |
|---|---|
| 15 °C | 44.1 |
| 20 °C | 22.4 |
| 25 °C | 18.2 |
| 30 °C | 15 |

EPPO también da, a 27 °C frente a 15 °C: eclosión ~4 frente a ~13 días, primer instar 1–3 frente a 7, segundo instar 3 frente a 12, prepupa (pseudopupa temprana) 1 frente a 4. Las fases pupales duran 2–9 días según la temperatura. En invernaderos de EE. UU. hay hasta 12–15 generaciones por año.

Duración por estadio a 27 °C sobre hojas de col — [UF/IFAS EDIS ENY-883/IN1089, Cluever, Smith, Funderburk & Frantz](https://ask.ifas.ufl.edu/publication/IN1089):

| Estadio | Días |
|---|---|
| Huevo | 3.07 |
| Larva I | 1.78 |
| Larva II | 2.38 |
| Prepupa | 1.00 |
| Pupa | 2.04 |
| **Total huevo→adulto** | **10.2** |

A 27 °C la fecundidad media es de 76.6 huevos por hembra.

### Inferences
- Las cifras de EPPO (huevo a huevo) y de EDIS (huevo a adulto) miden cosas distintas, así que no se deben graficar en la misma serie.

### Gaps
- **ENY-2034:** existe como "ficha de identificación de *F. occidentalis*" — [UF/IFAS GCREC, lista de publicaciones](https://gcrec.ifas.ufl.edu/gcrec-facultystaff-directory/hugh-smith/lab/extension-publications). No pude recuperar el documento, y las duraciones de estadio citadas arriba vienen de ENY-883/IN1089, no de ENY-2034 **[SIN FUENTE para ENY-2034]**.
- EPPO no da temperatura umbral de desarrollo **[SIN FUENTE]**.
