# Identificar insectos por contexto cuando la apariencia no basta (caso: trips Frankliniella en flores de Colombia)

Nota de método: los datos salen de páginas abiertas con WebFetch (EDIS/UF-IFAS IN1089, ficha de EPPO de FRANOC) y de resúmenes de resultados de búsqueda (los demás). Las cifras que vienen solo de resúmenes de búsqueda llevan la marca "(snippet)" y conviene revisarlas en la fuente original antes de publicarlas. Lo que no se pudo verificar lleva [SIN FUENTE].

## 1. Identificación por planta hospedera y por alimentación (host range)

### Takeaway
La planta hospedera es la primera clave de muchas guías: los minadores se identifican por hospedero + forma de la mina, los áfidos con claves organizadas por género de planta, y las orugas con bases de datos de registros hospedero-insecto. Pero en especies muy polífagas (como *F. occidentalis*) el hospedero reduce poco la lista de candidatos.

### Cited Findings
- **Minas de hojas.** El sitio *The leaf and stem mines of British flies and other insects* (Pitkin, Ellis, Plant y Edmunds) está organizado por planta hospedera. Cubre 885 minadores británicos y tiene claves para las minas de 675 de los 882 géneros de hospederos tratados. Cada clave usa la forma y la posición de la mina (p. ej. "mina corta y estrecha cerca del ápice" frente a "corredor ancho e irregular que toca el nervio central") y el patrón del excremento (granos regulares que alternan a los lados del corredor). Para los minadores de gramíneas recomienda criar al adulto, porque solo así la identificación es fiable — [ukflymines.co.uk](https://www.ukflymines.co.uk/); ejemplo de clave por hospedero: [clave Bellis](https://ukflymines.co.uk/Keys/BELLIS.php) (snippet)
- Para Europa continental existe el recurso complementario en neerlandés *Bladmineerders en plantengallen van Europa* (Ellis), que cubre minas y agallas — mencionado en [ukflymines.co.uk](https://www.ukflymines.co.uk/) (snippet); no se verificó su URL [SIN FUENTE para la URL]
- **Áfidos.** *Blackman & Eastop's Aphids on the World's Plants* (aphidsonworldsplants.info), basado en los libros *Aphids on the World's Trees* (1994) y *Aphids on the World's Herbaceous Plants and Shrubs* (2006). Tiene listas de hospederos y claves de los áfidos de cada género de planta, más una clave aparte para los áfidos polífagos. Las claves usan medidas de partes duras en preparaciones microscópicas — [aphidsonworldsplants.info](https://aphidsonworldsplants.info/); [reseña en bioinfo](https://bioinfo.org.uk/html/b158185.htm); [Wiley, vol. 1 "Host lists and keys"](https://www.wiley-vch.de/en/areas-interest/natural-sciences/aphids-on-the-world-39-s-herbaceous-plants-and-shrubs-978-0-471-48973-3) (snippet)
- **Lepidoptera.** HOSTS (Natural History Museum, Londres; Robinson, Ackery, Kitching, Beccaloni y Hernández) reúne unos 180 000 registros de plantas hospederas de orugas para unas 22 000 especies, sacados de unas 1600 fuentes. Ya no se actualiza (es un archivo). Se descarga en CSV con licencia CC0. DOI 10.5519/havt50xw — [NHM Data Portal: HOSTS](https://data.nhm.ac.uk/dataset/hosts) (snippet)
- **EPPO Global Database.** Su ficha de *F. occidentalis* registra 244 especies hospederas de 62 familias. En EE. UU. ataca, al aire libre, flores de albaricoque, durazno, nectarina, ciruela, rosa, clavel, arveja de olor, arveja, tomate, *Capsicum*, cucurbitáceas y fresa. En Europa ataca sobre todo cultivos de invernadero: crisantemo, *Gerbera*, rosa y *Saintpaulia* — [EPPO FRANOC datasheet](https://gd.eppo.int/taxon/FRANOC/datasheet)
- UF/IFAS (IN1089) indica que *F. occidentalis* tiene hospederos en 65 familias. Advierte que aparecer en la lista de hospederos no significa que la planta permita la reproducción — [EDIS IN1089](https://ask.ifas.ufl.edu/publication/IN1089)
- *Thrips palmi*: más de 200 especies hospederas de más de 36 familias, pero es plaga sobre todo de Cucurbitaceae y Solanaceae (*Capsicum annuum*, *Cucumis melo*, *Cucurbita* spp., *Solanum melongena*, *Solanum tuberosum*) — [Defra factsheet T. palmi](https://planthealthportal.defra.gov.uk/assets/factsheets/T.palmi-Plant-Pest-Factsheet-Template-Accessibility-Updated-2022.pdf); [EPPO THRIPL](https://gd.eppo.int/taxon/THRIPL/datasheet) (snippet)
- CABI Compendium: EPPO cita la ficha CABI 24426 para *F. occidentalis* — [búsqueda EPPO/CABI](https://gd.eppo.int/taxon/FRANOC/documents) (snippet); no se abrió [SIN FUENTE para el contenido]

### Inferences
- El hospedero filtra con fuerza en grupos especialistas (minadores, agalleros, muchos áfidos). En generalistas como *F. occidentalis* (244 especies, 62 familias) solo sirve para dar prioridad a ciertos candidatos.
- Lección para estudiantes: el hospedero cambia la probabilidad de cada especie, pero no la confirma. La propia UF advierte que "hospedero registrado" no implica que la planta sostenga una población.

### Gaps
- Claves de agallas (hospedero + forma de la agalla): no se encontró ninguna fuente concreta en esta ronda [SIN FUENTE]. Fuera de la mención al recurso de Ellis, no hay ejemplos citables.
- Plantwise: no se consultó [SIN FUENTE].

## 2. El daño como evidencia cuando el insecto no está

### Takeaway
Existen clasificaciones formales del daño, como el sistema de grupos funcionales de alimentación y tipos de daño (FFG–DT) de Labandeira y col. En trips, la combinación de plateado + punteado oscuro de excremento + cicatrices en flores es característica, aunque se puede confundir con daño de ácaros y de otros trips. También hay trabajos de visión artificial que clasifican el daño en lugar del insecto.

### Cited Findings
- **Daño de *F. occidentalis* (EPPO):** decoloración del haz de la hoja con hundimientos donde hubo alimentación. El patrón es "más grueso" que el de *Thrips tabaci*. En ornamentales puede haber plateado, deformaciones, crecimiento anormal y protuberancias marrones. También aparecen manchas con halo, botones deformados y "pimpling" (granitos) en flores de orquídea por los huevos puestos en los pétalos — [EPPO FRANOC](https://gd.eppo.int/taxon/FRANOC/datasheet)
- **Excremento:** los trips dejan depósitos fecales líquidos que forman un punteado verde oscuro, mientras que los ácaros tetraníquidos dejan gránulos negros. Esto sirve para separar daño de trips de daño de ácaros — [EPPO FRANOC](https://gd.eppo.int/taxon/FRANOC/datasheet)
- UF/IFAS: en la figura de daño en hoja de tomate, "las manchas oscuras son excremento". Además se ven cicatrices en pimentón y heridas de oviposición en tomate — [EDIS IN1089](https://ask.ifas.ufl.edu/publication/IN1089)
- *T. palmi*: cicatrices plateadas, hojas deformadas o cloróticas. En infestaciones fuertes las hojas se ven plateadas o bronceadas, los brotes se atrofian y los frutos quedan cicatrizados; en berenjena hay lesiones corchosas — [Defra T. palmi](https://planthealthportal.defra.gov.uk/assets/factsheets/T.palmi-Plant-Pest-Factsheet-Template-Accessibility-Updated-2022.pdf); [EPPO THRIPL](https://gd.eppo.int/taxon/THRIPL/datasheet) (snippet)
- Rosa en Colombia: larvas y adultos de *F. occidentalis* chupan y raspan folíolos, botones y pétalos, y dejan distorsiones y "necrosamientos incoloros discontinuos" — [Inventum 2008, Uniminuto](https://revistas.uniminuto.edu/index.php/Inventum/article/download/81/79/292) (snippet)
- **Clasificación publicada de tipos de daño:** *Guide to Insect (and other) Damage Types on Compressed Plant Fossils* (Labandeira, Wilf, Johnson y Marsh; Smithsonian, 2007, v3.0/3.01). Agrupa la herbivoría foliar en grupos funcionales de alimentación: alimentación en agujero, de margen, esqueletización, alimentación superficial, minado, perforación-succión y agallas. Cada tipo de daño (DT) tiene un número; en la literatura se citan DT por encima de 290 — [Annual Review of Entomology](https://annualreviews.org/doi/pdf/10.1146/annurev-ento-120120-102849); [Smithsonian repository](https://repository.si.edu/server/api/core/bitstreams/a060347b-7462-44dc-a360-f230c4f8fa96/content) (snippet). No se verificó el número total de DT [SIN FUENTE].
- **Visión artificial sobre el daño:** Meineke y col. (Duke, herbario) entrenaron un detector y un clasificador de tipos de herbivoría en *Quercus bicolor* y *Onoclea sensibilis*: seis tipos de daño + dos clases de hoja sana. Con cajas dibujadas a mano, el clasificador acertó el tipo de daño en el 81,5 % de los casos (8 categorías). La detección automática fue más débil: mAP 45 % — [DukeSpace](https://dukespace.lib.duke.edu/items/4e57405b-a1bf-4a32-8350-19a1725e2673/full) (snippet)
- Polilla minadora del peral (Ecosphere 2021): redes profundas clasificaron 52 322 fotos de 19 semanas en seis clases principales de daño. El rendimiento dependía de cuánto se parecían los tipos de daño y de cuántas imágenes de entrenamiento había — [Ecosphere, DOAJ](https://doaj.org/article/bcbf6a1e174c4f58b20746466466418a) (snippet)
- Ácaros en algodón: se estimó el nivel de daño (no el tipo) con MobileNetV1, con 91,88 % en el conjunto de prueba — [IJABE](https://ijabe.org/index.php/ijabe/article/download/4816/pdf) (snippet)

### Inferences
- Para la guía: el punteado de excremento, verde oscuro y líquido en trips frente a gránulos negros en ácaros, es un buen ejemplo de "evidencia indirecta" que separa grupos parecidos sin ver al animal.
- Masticador frente a chupador: el sistema FFG separa "perforación y succión" de la alimentación con mandíbulas (agujero, margen, esqueletización), y es la tipología citable más adecuada.

### Gaps
- No se encontró una fuente primaria sobre melaza/fumagina en esta ronda [SIN FUENTE].
- No se encontró un dataset público de visión artificial etiquetado específicamente con daño de trips (plateado) [SIN FUENTE].

## 3. Hábitat, microhábitat, estación, hora, geografía y tipo de trampa como contexto

### Takeaway
El tipo de trampa y el cebo dicen mucho del taxón capturado. Las trampas adhesivas azules favorecen a *F. occidentalis*. La feromona de agregación Thripline-AMS (neryl (S)-2-methylbutanoate) es específica de esa especie, mientras que Lurem-TR atrae a varias. El microhábitat (dentro de flores complejas o en el suelo) y la zona geográfica también reducen la lista de candidatos.

### Cited Findings
- En monitoreo, las trampas adhesivas azules capturan más *F. occidentalis* que las amarillas. Las amarillas también atrapan minadores, áfidos y moscas blancas. Las capturas en trampa rara vez reflejan el tamaño de la población o anticipan el daño — [EDIS IN1089](https://ask.ifas.ufl.edu/publication/IN1089)
- Muestreo en flor: golpear la flor sobre una tabla clara y contar los trips, o ponerla en etanol — [EDIS IN1089](https://ask.ifas.ufl.edu/publication/IN1089)
- Microhábitat: la prepupa y la pupa (estados que no se alimentan) suelen estar en el suelo, pero también pueden quedarse dentro de flores complejas como el crisantemo — [EDIS IN1089](https://ask.ifas.ufl.edu/publication/IN1089)
- **Feromona:** Hamilton, Hall y Kirk (2005) identificaron neryl (S)-2-methylbutanoate, producido por los machos, como la primera feromona de agregación descrita en Thysanoptera. Aumentó la captura de ambos sexos en trampas azules — [J. Chem. Ecol. 2005, 31:1369-1379](https://wiki.pestinfo.org/wiki/Journal_of_Chemical_Ecology_(2005)_31,_1369-1379); [AGRIS](https://agris.fao.org/search/ar/records/65e0191290674e46e6548f94) (snippet)
- Sampson, Hamilton y Kirk: la feromona multiplicó la captura por ~1,3 en trampa azul, 1,7 en amarilla, 1,9 en transparente y 3,4 en negra. Los depredadores probados no fueron atraídos — [Springer s40064-015-0864-3](https://link.springer.com/doi/10.1186/s40064-015-0864-3); [PMC4348358](https://pmc.ncbi.nlm.nih.gov/articles/PMC4348358) (snippet)
- Thripline-AMS es específico de especie (atrae machos y hembras de *F. occidentalis*); Lurem-TR es interespecífico — [PMC4348358](https://pmc.ncbi.nlm.nih.gov/articles/PMC4348358) (snippet)
- En mora (Cruz-Esteban y col. 2020), 200–400 µg de la feromona en trampas azules o amarillas multiplicaron la captura por ~2,5–3. Se capturaron más hembras en túnel y más machos a campo abierto — [J. Appl. Entomol. 2020, 144:755-763](https://wiki.pestinfo.org/wiki/Journal_of_Applied_Entomology_(2020)_144,_755-763) (snippet)
- Colombia: en crisantemo para semilla en la Sabana de Bogotá (2021), *F. occidentalis* fue la especie dominante en todas las etapas fenológicas, y se respalda el uso de trampas adhesivas amarillas bajo cubierta plástica — [Agronomía Colombiana, UNAL](https://revistas.unal.edu.co/index.php/agrocol/article/view/95978) (snippet)
- Geografía y hábitat en Colombia: en La Ceja (Antioquia), dentro de invernadero, la especie más frecuente en crisantemo (*Dendranthema grandiflora*) fue *Frankliniella panamensis*, con *Thrips australis*, *Taeniothrips* sp. y *Neohydatothrips* cf. *burungae*; *F. occidentalis* apareció en bouvardia. En plantas silvestres (guayacán rosado, margarita, uchuva, trébol, eucalipto, etc.) se registraron *F. insularis* y *Frankliniella* sp. — [Rev. Colomb. Entomol., Univalle](https://revistacolombianaentomologia.univalle.edu.co/index.php/SOCOLEN/article/download/9601/12149/29965) (snippet; los nombres aparecían con errores de OCR en el snippet y se transcribieron según la nomenclatura usual)
- En Medellín (29 ornamentales, 56 fincas), *F. occidentalis* fue la especie más frecuente y la de mayor distribución geográfica; el crisantemo/pompón y el aster tuvieron las poblaciones más altas — [Rev. Colomb. Entomol.](https://revistacolombianaentomologia.univalle.edu.co/index.php/SOCOLEN/article/download/9999/12703/31856) (snippet)
- Mac Aodha, Cole y Perona (ICCV 2019) proponen un "prior" espacio-temporal: dados un lugar y una fecha, estima la probabilidad de cada categoría a partir de datos de solo presencia (iNaturalist, eBird). Su ejemplo motivador son dos sapos muy parecidos que viven en zonas distintas de Europa — [CVF Open Access](https://openaccess.thecvf.com/content_ICCV_2019/html/Aodha_Presence-Only_Geographical_Priors_for_Fine-Grained_Image_Classification_ICCV_2019_paper.html); [project page](https://homepages.inf.ed.ac.uk/omacaod/projects/geopriors/index.html)

### Inferences
- En La Ceja, la especie dominante cambió según el cultivo y el sitio (*F. panamensis* en crisantemo, *F. occidentalis* en bouvardia). Es un buen ejemplo de que "trips en crisantemo de Antioquia" no equivale automáticamente a *F. occidentalis*.
- Una trampa cebada con Thripline-AMS sesga la captura hacia *F. occidentalis*, pero eso no prueba que cada individuo capturado lo sea.

### Gaps
- Hora del día, altitud y estacionalidad de *Frankliniella* en Colombia: no se encontraron datos citables [SIN FUENTE].
- Trampas de luz como indicador de taxón: no se buscó [SIN FUENTE].

## 4. Machine learning que combina imagen + contexto (cultivo, lugar, fecha)

### Takeaway
Hay evidencia de que los metadatos de contexto mejoran la clasificación de invertebrados (alrededor de +10 % según un estudio con especímenes de NEON). Los priors geográficos dan "grandes mejoras" en clasificación de grano fino, y IP102 organiza las plagas por cultivo en una jerarquía. Los resultados no se pueden comparar entre sí: cambian el dataset, la métrica y la tarea.

### Cited Findings
- Blair y col. (2022), *Embracing imperfection: Machine-assisted invertebrate classification in real-world datasets*: más de 72 000 invertebrados de trampas pitfall de NEON (45 sitios de EE. UU., 2016–2019). Precisión máxima en taxones conocidos: XGBoost 72,7 % frente a ResNet-50 72,8 %. Los modelos sin metadatos de contexto rinden peor. En taxones no vistos (zero-shot): ResNet-50 65,5 % frente a XGBoost 39,4 % — [WUR research](https://research.wur.nl/en/publications/embracing-imperfection-machine-assisted-invertebrate-classificati/) (snippet)
- El resumen de ese trabajo dice que los metadatos de contexto mejoran la precisión en "~10 %" — [registro hebis](https://ubmr.hds.hebis.de/EdsRecord/edo%252C161009979) (snippet; atribución al mismo artículo inferida del resultado de búsqueda, verificar)
- BioAutoML-NAS: un módulo de fusión une los embeddings de imagen con metadatos; 96,81 % de exactitud en BIOSCAN-5M y 93,25 % en Insects-1M. El resumen no aísla cuánto aportan los metadatos — [arXiv 2510.05888](https://arxiv.org/html/2510.05888v1) (snippet)
- Análogo en otro dominio (cámaras trampa, fauna): la fusión temprana de metadatos supera a la fusión tardía; el mejor modelo llega a 98,9 % — [arXiv 2409.04825](https://arxiv.org/pdf/2409.04825) (snippet)
- Priors geográficos (Mac Aodha y col. 2019): combinar el prior con el clasificador de imagen da "una gran mejora" en varios datasets. No se extrajo la cifra para iNaturalist — [CVF](https://openaccess.thecvf.com/content_ICCV_2019/papers/Aodha_Presence-Only_Geographical_Priors_for_Fine-Grained_Image_Classification_ICCV_2019_paper.pdf)
- IP102 (Wu y col., CVPR 2019): más de 75 000 imágenes, 102 clases con distribución de cola larga y ~19 000 imágenes con cajas. Tiene una taxonomía jerárquica en la que las plagas que afectan sobre todo a un mismo producto agrícola comparten categoría superior — [Papers with Code](https://cs.paperswithcode.com/paper/ip102-a-large-scale-benchmark-dataset-for); [mmcheng.net](https://mmcheng.net/ip102/) (snippet)
- Según un proveedor secundario, son 8 superclases: arroz, maíz, trigo, remolacha y alfalfa (cultivos de campo) y vid, cítricos y mango (cultivos económicos). No se confirmó en el artículo original — [V7 Labs](https://www.v7labs.com/open-datasets/ip102) (snippet)
- Pipeline de polillas (detección + clasificación): la exactitud subió de 79,62 % a 88,05 %, pero por recortar la imagen, no por usar contexto — [GI dl](https://dl.gi.de/items/92317555-906c-42d9-af32-223e7c7beb2b/full) (snippet)

### Inferences
- Para trips en flores, la forma lógica de aprovechar el contexto sería un prior por cultivo, región y fecha (como el de Mac Aodha) o una jerarquía por cultivo (como IP102). Ningún estudio encontrado lo prueba en *Frankliniella* [SIN FUENTE para gains en trips].

### Gaps
- No se encontró un estudio controlado que aísle la ganancia de "cultivo hospedero" como variable de entrada en un clasificador de plagas [SIN FUENTE].
- No se encontraron cifras de ganancia de modelos jerárquicos sobre IP102 [SIN FUENTE].

## 5. Trips: especies de Frankliniella y parecidas, hospederos, daño, tamaños, sexo, TSWV, ICA

### Takeaway
Las especies se parecen tanto que se necesita microscopio (setas ocelares, peine del tergito VIII, número de segmentos antenales). El contexto (cultivo, competencia como vector, tipo de daño) ayuda a ordenar los candidatos, pero no reemplaza la morfología. *F. occidentalis* es haplodiploide: los machos salen de huevos no fecundados y son más pequeños y pálidos.

### Cited Findings
**Separación morfológica (requiere microscopio)**
- *Frankliniella* tiene antena de 8 segmentos (*Thrips*, 7). La vena principal del ala anterior tiene cerdas regulares (14–19 en *F. occidentalis*) y el protórax tiene un par de cerdas claramente más largo. Separar especies es "tarea de expertos" — [EPPO FRANOC](https://gd.eppo.int/taxon/FRANOC/datasheet)
- Caracteres de *F. occidentalis*: pedicelo antenal liso; espinas del segundo segmento antenal no muy gruesas; setas ocelares separadas por al menos 1,5 veces el diámetro de un ocelo; cuatro setas pequeñas en el margen anterior del protórax; peine microtrichial completo en el segmento abdominal VIII — [EDIS IN1089](https://ask.ifas.ufl.edu/publication/IN1089)
- *F. schultzei*: el par III de setas ocelares está junto, entre los ocelos posteriores; tiene dos pares de setas en el margen anterior del metanoto y le falta el peine posteromarginal del tergito VIII. Es difícil de separar de *F. occidentalis* — [Lucid NZ Thysanoptera](https://keys.lucidcentral.org/keys/v3/nz_thrips/the_key/key/New_Zealand_Thysanoptera/Media/Html/frankliniella_schultzei.htm); [Lucid key server](https://keyserver.lucidcentral.org/key-server/data/07060c0e-0504-490a-8003-050004060f01/media/Html/browse_species/Frankliniella_schultzei.htm) (snippet)
- *T. palmi*: adulto casi todo amarillo, con una línea oscura donde se juntan las alas en reposo; hembra de ~1,3 mm (frente a 1,7 mm de *T. flavus*); setas interocelares fuera del triángulo ocelar. Se confunde con *T. flavus* y *T. tabaci* — [EPPO THRIPL](https://gd.eppo.int/taxon/THRIPL/datasheet); [Defra](https://planthealthportal.defra.gov.uk/assets/factsheets/T.palmi-Plant-Pest-Factsheet-Template-Accessibility-Updated-2022.pdf) (snippet)

**Hospederos y contexto que separa**
- *F. schultzei*: se reproduce en flores y también en hojas, sobre muchísimos hospederos, y además come ácaros. Transmite TSWV, TCSV y GRSV. En Nueva Zelanda la forma oscura es la vectora típica; en Bowen (Australia) la forma pálida es la principal vectora — [Lucid NZ](https://keys.lucidcentral.org/keys/v3/nz_thrips/the_key/key/New_Zealand_Thysanoptera/Media/Html/frankliniella_schultzei.htm) (snippet)
- *F. fusca* (trips del tabaco): principal vector de TSWV en maní en Georgia (EE. UU.) y responsable de casi todo el daño temprano en maní del sureste — [Entomology Today 2022](https://entomologytoday.org/2022/02/23/tobacco-thrips-tiny-insects-big-impact-georgia-peanut-production/); [Alabama Extension](https://www.aces.edu/blog/topics/crop-production/tomato-spotted-wilt-virus-on-peanuts/) (snippet)
- *F. tritici* (trips oriental de las flores), *T. palmi* y chilli thrips: "no son vectores competentes" de TSWV. *F. tritici* suele aparecer junto con *F. occidentalis* en campo y ser más abundante — [EDIS IN401](https://ask.ifas.ufl.edu/publication/IN401); [Strzyzewski 2023, J. Pest Sci.](https://nfrec.ifas.ufl.edu/media/nfrecifasufledu/images/faculty-/martini/horticultural-entomology/docs/publications/2023-strzyzewski-JPS.pdf) (snippet)
- *F. bispinosa* transmite TSWV en laboratorio, pero con menos eficiencia que *F. occidentalis* — [EDIS IN401](https://ask.ifas.ufl.edu/publication/IN401) (snippet)
- *F. insularis*: en Colombia se registró en flores silvestres de La Ceja (Antioquia) — [Rev. Colomb. Entomol.](https://revistacolombianaentomologia.univalle.edu.co/index.php/SOCOLEN/article/download/9601/12149/29965) (snippet). Sus hospederos en cultivos no se verificaron [SIN FUENTE].
- *T. tabaci*: el daño de *F. occidentalis* es "más grueso" que el de *T. tabaci* — [EPPO FRANOC](https://gd.eppo.int/taxon/FRANOC/datasheet). Hospederos de *T. tabaci* no verificados en esta ronda [SIN FUENTE].
- Colombia: *F. occidentalis* daña flores de crisantemo en la Sabana de Bogotá (Agronomía Colombiana 1989) y fue la única especie encontrada en crisantemo en Piendamó, Cauca (1994) — [Agronomía Colombiana 1989, DOAJ](https://doaj.org/article/2dcf28bc8d5446158e91661b62d4dcca); [UNAL agrocol 20999](https://revistas.unal.edu.co/index.php/agrocol/article/view/20999) (snippet). Los trips de rosa de exportación pueden viajar en la flor cortada hacia Europa y causar intercepciones — [Inventum 2008](https://revistas.uniminuto.edu/index.php/Inventum/article/download/81/79/292) (snippet)

**Tamaños por estado (mm)**
- Huevo: 550 × 250 µm según UF/IFAS — [EDIS IN1089](https://ask.ifas.ufl.edu/publication/IN1089); "unos 200 µm" según EPPO — [EPPO FRANOC](https://gd.eppo.int/taxon/FRANOC/datasheet). **Las dos fuentes no coinciden.**
- Larva I: < 1 mm, incolora o blanca; larva II: ~1 mm, amarilla — [AHDB](https://archive.ahdb.org.uk/knowledge-library/recognition-biology-main-thrips-species-protected-ornamentals) (snippet). Larva II al final del estadio: ~1 mm, amarillo pálido — [UGA C1158](https://secure.caes.uga.edu/extension/publications/files/pdf/C%201158_3.PDF) (snippet). EPPO describe la larva I como translúcida y la II como amarillo dorado, sin medidas — [EPPO](https://gd.eppo.int/taxon/FRANOC/datasheet)
- Prepupa y pupa: amarillentas, "unos 2 mm" según una sola fuente (AHDB) — [AHDB](https://archive.ahdb.org.uk/knowledge-library/recognition-biology-main-thrips-species-protected-ornamentals) (snippet; cifra no corroborada). EPPO dice que "ambos estados pupales son blancos" — [EPPO](https://gd.eppo.int/taxon/FRANOC/datasheet). **Conflicto de color.** La prepupa tiene esbozos alares cortos y antenas hacia adelante; la pupa tiene esbozos más largos y antenas dobladas hacia atrás sobre la cabeza — [EDIS IN1089](https://ask.ifas.ufl.edu/publication/IN1089)
- Adulto: "generalmente menos de 2 mm" — [EPPO](https://gd.eppo.int/taxon/FRANOC/datasheet); [EDIS IN1089](https://ask.ifas.ufl.edu/publication/IN1089). 1,2–1,4 mm — [UNH Extension](https://extension.unh.edu/resources/files/Resource002803_Rep4158.pdf) (snippet)
- El artículo de Agronomía Colombiana (1989) sobre el ciclo de vida en crisantemo no se pudo leer: el PDF es un escaneo sin texto [SIN FUENTE para sus medidas].

**Sexo y haplodiploidía**
- Los machos salen de huevos no fecundados (las hembras sin aparear pueden producirlos) y las hembras de huevos fecundados — [EPPO](https://gd.eppo.int/taxon/FRANOC/datasheet); [EDIS IN1089](https://ask.ifas.ufl.edu/publication/IN1089). Ninguna de las dos fuentes usa los términos "arrenotoquia" o "haplodiploidía".
- Macho más pequeño, de abdomen estrecho con punta redondeada y color amarillo pálido, casi blanco. Hembra de abdomen más redondeado que termina en punta, de color amarillo a marrón; solo las hembras tienen formas pálida, intermedia y oscura — [EPPO](https://gd.eppo.int/taxon/FRANOC/datasheet). Los machos son "más pequeños y más pálidos" y mucho menos comunes, y forman enjambres de apareamiento — [EDIS IN1089](https://ask.ifas.ufl.edu/publication/IN1089)
- Proporción habitual: unas 4 hembras por macho; cada hembra pone de 20 a 40 huevos — [EPPO](https://gd.eppo.int/taxon/FRANOC/datasheet)
- En Florida la forma más común es la intermedia: amarilla con una banda oscura longitudinal en tórax y abdomen — [EDIS IN1089](https://ask.ifas.ufl.edu/publication/IN1089)

**TSWV**
- *F. occidentalis* transmite TSWV y tobacco streak ilarvirus. Solo las ninfas adquieren el virus (con al menos 30 min de alimentación). El trips se vuelve infectivo a los 3–10 días y transmite con al menos 15 min de alimentación — [EPPO](https://gd.eppo.int/taxon/FRANOC/datasheet)
- Síntomas generales: crecimiento nuevo atrofiado, bronceado en hojas jóvenes, estrías marrones en tallos terminales, anillos (ring spots) de color púrpura oscuro a marrón y crecimiento de un solo lado — [Oklahoma State Extension](https://extension.okstate.edu/programs/digital-diagnostics/plant-diseases/tomato-spotted-wilt-virus.html) (snippet). El primer síntoma puede ser un tono bronceado o púrpura; las manchas con centro de aspecto normal suelen indicar virus — [SDSU Extension](https://extension.sdstate.edu/tomato-spotted-wilt-virus) (snippet)
- En crisantemo: manchas amarillas y anillos, lesiones necróticas, necrosis angular y colapso del tallo justo debajo de la flor; puede afectar a una sola rama. No se puede diagnosticar a simple vista: hace falta análisis de laboratorio — [MSU Extension](https://www.canr.msu.edu/news/know_the_symptoms_of_tomato_spotted_wilt_virus_in_chrysanthemum) (snippet)

**Regulación en Colombia (ICA)**
- La lista oficial de plagas reglamentadas está en el anexo de la Resolución ICA 3593 de 2015 (que derogó la 2895 de 2010). Se actualiza con estudios técnicos según la NIMF 19 y fue modificada, por ejemplo, por la Res. 79193 de 2020 — [Res. ICA 2895/2010, compilación ICA](https://compilacionmsf.ica.gov.co:4443/compilacion/docs/docx/RESOLUCION_ICA_2895_2010.docx); [Res. ICA 79193/2020](https://normograma.invima.gov.co/normograma/docs/pdf/resolucion_ica_79193_2020.pdf) (snippet)
- No se verificó si *F. occidentalis* aparece en ese anexo ni con qué categoría [SIN FUENTE]. Como esta especie está ampliamente establecida en cultivos colombianos (ver estudios arriba), es probable que no figure como cuarentenaria ausente, pero esto es una inferencia, no un dato.

### Inferences
- Las pistas de contexto que mejor separan candidatos en flores colombianas: el cultivo y el sitio (*F. panamensis* frente a *F. occidentalis* en Antioquia), la presencia de síntomas de TSWV (que apuntan a una especie vectora y descartan *F. tritici* y *T. palmi* como causa del virus) y el cultivo (cucurbitáceas y solanáceas para *T. palmi*; maní para *F. fusca*). Aun así, la confirmación necesita preparaciones microscópicas.
- "Macho más pequeño y pálido" es un buen ejemplo para la guía de variación dentro de una especie que confunde a un clasificador visual (pálido y pequeño no significa otra especie).

### Gaps
- Tamaños exactos de la prepupa y la pupa en fuentes primarias morfométricas: solo hay una cifra de extensión (AHDB, ~2 mm) [verificar].
- Hospederos de *F. insularis* y *T. tabaci* en Colombia; anexo de la Res. ICA 3593/2015 [SIN FUENTE].
