# Taxonomía, identificación y contexto para una guía universal de identificación por IA

Nota de método: ~15 búsquedas web (resúmenes de buscador, no todas las páginas se abrieron completas). Todo lo marcado [SIN FUENTE] es conocimiento general no verificado en esta sesión. Cifras de bases de datos cambian a diario; reverificar antes de citar.

## 1. Fundamentos de taxonomía

### Takeaway
La jerarquía (dominio > reino > filo > clase > orden > familia > género > especie) y el binomio son convenciones estables, pero los nombres cambian (sinónimos, divisiones de géneros/especies) y eso rompe datasets etiquetados con nombres viejos. Hay que guardar un ID de taxón estable y un mapeo a nombre aceptado, no solo el string.

### Cited Findings
- Ejemplo de sapo: Rhinella marina. Clasificación [SIN FUENTE, conocimiento general]: Eukarya > Animalia > Chordata > Amphibia > Anura > Bufonidae > Rhinella > Rhinella marina. Ojo: ASW reconoce que parte de las poblaciones de Mesoamérica y noroeste de Sudamérica son R. horribilis (ver sección 3).
- Ejemplo de planta [SIN FUENTE]: Eukarya > Plantae > Tracheophyta > Liliopsida > Poales > Poaceae > Zea > Zea mays (maíz).
- Binomio = Género + epíteto específico, en cursiva, género con mayúscula [SIN FUENTE]. Un "taxón" es cualquier grupo nombrado a cualquier rango; un "clado" es un ancestro con todos sus descendientes (monofilético); un "complejo de especies" es un grupo de especies cercanas, difíciles de separar morfológicamente [SIN FUENTE, definiciones generales].
- GBIF y NCBI eligen un nombre aceptado por taxón y marcan los demás como sinónimos; en GBIF cada nombre tiene su propio ID de taxón y estado ("accepted"/"synonym"), en NCBI los sinónimos se fusionan en el ID del aceptado. GBIF avisa que los sinónimos pueden seguir en uso, así que conviene consultar el nombre necesario — [GBIF docs sinonimia](https://docs.gbif.org/course-data-use/en/synonymy.html); [PMC10838036](https://pmc.ncbi.nlm.nih.gov/articles/PMC10838036)
- El backbone de GBIF se arma desde muchas fuentes, lo que produce variaciones considerables en taxones superiores y muchos sinónimos; nombres solo en bases nomenclaturales quedan como "doubtful accepted" — [GBIF data-blog](https://data-blog.gbif.org/post/gbif-backbone-taxonomy)
- Caso cuantificado: una lista curada de leguminosas añadió 30,456 nombres al backbone de GBIF y 61,235 registros de ocurrencia quedaron mejor etiquetados — [Legume Data Portal](https://www.legumedata.org/beanbag/69/issue-69-taxonomy-working-group)
- Los agregadores (ALA, GBIF) han sido criticados por imponer taxonomías backbone a registros de museos/herbarios: el nombre original puede cambiar de rango o dejar de ser buscable, y las descargas masivas enmascaran el cambio — [presentación TDWG](https://spnhctdwg18.sched.com/event/G4V4/look-what-theyve-done-to-our-data-how-aggregators-change-data-items-in-collection-records)
- Ejemplo de cambio de nombre/recuento: Anolis pasó de ~427 especies (Reptile Database, enero 2018) a solo 52 en Anolis sensu stricto cuando la Reptile Database adoptó el split de Nicholson et al. (2012) en ocho géneros (Norops 169, Dactyloa 83); el cambio fue controvertido — [Anole Annals 2019](https://www.anoleannals.org/2019/03/22/anoles-by-the-numbers-part-i-species-descriptions); [Anole Annals 2012](https://anoleannals.org/2012/12/26/reptile-database-recognizes-split-of-anolis-into-eight-genera). (El 52 y los géneros vienen del resumen del buscador; verificar en la página.)
- Conteos de anfibios divergen entre catálogos: AmphibiaWeb 9,081 especies (7 ago 2026; Anura 8,011) vs. ASW 8,781 (versión sept 2024, vía Guinness) — [AmphibiaWeb](https://amphibiaweb.org/lists); [Guinness](https://www.guinnessworldrecords.com/world-records/760423-largest-order-of-amphibians). Fechas distintas: no comparables directamente.

### Inferences
- Para un dataset de entrenamiento: almacenar (ID GBIF/ASW, nombre aceptado, fecha del snapshot taxonómico) y nombres alternativos; elegir un solo catálogo por grupo (ASW/AmphibiaWeb anfibios, Reptile Database reptiles).
- Si un género se divide (Anolis), las etiquetas a nivel de género se vuelven inestables; la etiqueta a nivel de familia/"complejo" es más robusta.

### Gaps
- Fuente primaria para las definiciones de taxón/clado/complejo y para las clasificaciones de ejemplo: no abierta en esta sesión.
- Grupos relevantes para foto-ID (vertebrados, insectos, arácnidos, plantas, hongos) y cómo se identifica cada uno: no investigado con fuentes (ver sección 2 para lo parcial).

## 2. Cómo identifican los expertos

### Takeaway
Los expertos combinan morfología (claves dicotómicas, caracteres diagnósticos), ADN (COI animales; rbcL+matK plantas; ITS hongos), sonido y contexto; la foto puede no mostrar los caracteres diagnósticos. iNaturalist exige consenso comunitario para "Research Grade".

### Cited Findings
- Código de barras animal: fragmento de 648 pb del gen mitocondrial COI propuesto por Hebert et al. (2003); probado en 260 especies de aves norteamericanas (2004) — [PMC519005](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC519005/)
- Plantas: CBOL (2009) propuso rbcL + matK como "core barcode" (con periodo de prueba; matK difícil de amplificar); ITS2 favorecido en algunos grupos — [PMC2799520](https://pmc.ncbi.nlm.nih.gov/articles/PMC2799520)
- Hongos: ITS como barcode primario [SIN FUENTE: la búsqueda no devolvió fuente].
- iNaturalist Research Grade: ≥2 identificaciones que concuerdan y >2/3 de identificadores apoyan el taxón; requiere foto o sonido, fecha y ubicación válidas, organismo silvestre. Fuentes discrepan si el umbral es especie o género; puede volver a "Needs ID" — [iNat post Research Grade](https://www.inaturalist.org/posts/39072-research-grade); [iNat laji.fi](https://inaturalist.laji.fi/posts/26549-what-is-a-verifiable-observation-and-how-does-it-reach-research-grade); [foro iNat](https://forum.inaturalist.org/t/observation-showing-as-research-grade-with-only-1-id-at-species-level/75048)
- Bioacústica de aves: Merlin Sound ID convierte audio en espectrogramas y los trata como imágenes, entrenado con la Macaulay Library — [Cornell/Newswise](https://www.newswise.com/articles/what-bird-is-singing-ask-the-merlin-bird-id-app-for-an-instant-answer)
- En Rhinella, el canto de anuncio (menos notas, mayor frecuencia dominante) ayudó a separar R. bella — ver sección 3.

### Inferences
- Una foto que no muestra los caracteres diagnósticos (ej. dorso/vientre, genitales, venación, dewlap cerrado) no basta; el sistema debe devolver "género/familia" en vez de forzar especie.

### Gaps
- Claves dicotómicas, cámaras trampa, y por qué la foto es insuficiente (fuente formal): no encontrado en esta sesión.

## 3. Especies crípticas, parecidos, Anolis y Rhinella

### Takeaway
Anolis es muy diverso (427 spp. en el conteo amplio de 2018) y tiene ecomorfos convergentes; en varios casos especies crípticas se separan por morfología fina, ADN, hemipenes y color del dewlap, no por el aspecto general. Rhinella marina es un complejo con al menos R. horribilis y R. bella separados.

### Cited Findings
- 427 especies de Anolis (Reptile Database, enero 2018); 171 autores han descrito especies — [Anole Annals](https://www.anoleannals.org/2019/03/22/anoles-by-the-numbers-part-i-species-descriptions). Otra fuente: ">425 especies, el género de amniotas más rico" (resumen de buscador; Wikipedia como puntero).
- Ecomorfos de las Antillas Mayores: conjuntos similares de especialistas de hábitat evolucionaron independientemente en cada isla (convergencia) — [Anole Annals](https://anoleannals.org/2012/07/17/ecomorphs-converge-on-suites-of-correlated-traits). Con 100 especies, un método sin categorías previas (SURFACE) halló que muchos, pero no todos, los casos de convergencia coinciden con los ecomorfos clásicos — [Ingram et al. vía repositorio](https://repository.urosario.edu.co/items/50e6cd90-6618-4f3e-b068-dfa252e4973e/full)
- Críptica andina: especie nueva del suroeste de Colombia/noroeste de Ecuador (1187-2353 m), hermana de A. aequatorialis, distinguida por escamación, osteología craneal, hemipenes y ADN; registros colombianos previos de A. aequatorialis podrían ser esta especie — [ZooKeys 794](https://zookeys.pensoft.net/article_preview.php?id=26936)
- A. tropidogaster vs A. gaigei: separados por hemipenes, color del dewlap macho (púrpura-rojizo uniforme vs naranja-amarillo con centro oscuro), pholidosis y 16S — [Zootaxa 3348](https://mapress.com/zt/article/view/zootaxa.3348.1.1)
- A. biporcatus vs A. parvauritus: escamas distales del dewlap blancas vs negras; subdivisiones genéticas profundas sugieren más especies crípticas — [Anole Annals 2017](https://anoleannals.org/2017/05/21/new-mainland-green-anole-recognized)
- Contra-nota: el dewlap es filogenéticamente poco informativo y muestra convergencia; sirve como carácter diagnóstico entre especies concretas, no como regla general — [Wash U profile, evolución del dewlap](https://profiles.wustl.edu/en/publications/evolution-of-anolis-lizard-dewlap-diversity/)
- Rhinella marina/horribilis: R. horribilis (Mesoamérica y noroeste de Sudamérica, incl. oeste/norte de Colombia) fue sacada de la sinonimia de R. marina por Acevedo-Rincón, Lampo & Cipriani (2016, Zootaxa 4103: 574-586); R. marina s.s. queda sobre todo en la cuenca amazónica — [ASW R. horribilis](https://amphibiansoftheworld.amnh.org/Amphibia/Anura/Bufonidae/Rhinella/Rhinella-horribilis)
- 2024: Rhinella bella (oeste de los Andes ecuatorianos), separada por genética, morfología, acústica y ecología; menor tamaño, cráneo distinto, canto con menos notas y mayor frecuencia dominante — [Menéndez-Guerrero et al. 2024, PUCE](https://puceinvestiga.puce.edu.ec/es/publications/cryptic-diversity-in-toads-of-the-rhinella-marina-species-group-a/)
- Introgresión mitocondrial "fantasma" en R. horribilis: ADN mitocondrial y nuclear pueden discrepar — [Evolution in the genus Rhinella](https://archive.org/details/evolutiongenusr00pere)

### Inferences
- Para Anolis: datos útiles = localidad, altitud, color/forma del dewlap (macho), sexo, canto no aplica (no cantan; usan displays visuales), comportamiento/microhábitat (ecomorfo), escamación. [El dato "Anolis no vocalizan" es conocimiento general, SIN FUENTE.]
- Para Rhinella en Colombia: la localidad (cuenca amazónica vs. oeste/norte) es el discriminante principal; una foto sola no resuelve marina vs horribilis.

### Gaps
- Número de especies crípticas de Anolis: no hallado. Afirmación "muchas Anolis parecen muy similares": parcialmente respaldada (convergencia de ecomorfos y casos crípticos concretos), pero sin cifra global. Acosta-Galvis no apareció en las búsquedas sobre este complejo.

## 4. Priors contextuales

### Takeaway
iNaturalist usa un geomodelo (entrenado solo con observaciones iNat y un mapa de elevación) para etiquetar "Expected Nearby"; Merlin usa eBird (fecha y lugar) y packs regionales offline. Funcionan como prior, pero tienen errores documentados.

### Cited Findings
- Geomodelo iNat: toma una ubicación y devuelve especies probables; reemplazó la regla de "9 celdas vecinas con observaciones"; entrenado con ~80 mil especies, actualización mensual. Si ningún taxón visualmente similar está esperado cerca, muestra los similares de todos modos — [iNat blog 84677](https://www.inaturalist.org/blog/84677); [Help "Expected Nearby"](https://help.inaturalist.org/en/support/solutions/articles/151000170371-what-does-expected-nearby-mean-)
- Reportes de usuarios de errores (especies fuera de rango marcadas como esperadas): [foro iNat](https://forum.inaturalist.org/t/species-not-expected-nearby-are-being-presented-as-expected-nearby-in-inaturalist-next/71504) (informes de usuarios, no diagnósticos confirmados).
- Merlin: >mil millones de observaciones eBird indican qué aves son probables por lugar y fecha; Photo ID acepta fecha/ubicación; packs regionales descargables permiten uso offline (cobertura exacta de packs: verificar en la app, fuentes de terceros discrepan) — [Cornell Lab](https://www.birds.cornell.edu/landtrust/merlin-bird-id); [PopSci](https://www.popsci.com/technology/cornell-merlin-app-bird-id/)

### Inferences
- Combinar posterior = verosimilitud visual × prior geográfico/altitudinal/estacional; limitar el peso del prior para no suprimir registros nuevos o fuera de rango (invasoras, divagantes). El prior hereda el sesgo de muestreo de iNat/eBird (zonas con pocos observadores aparecen como "no esperado").

### Gaps
- Efecto de altitud/hora/estación en la precisión de modelos: no hallado con cifras.

## 5. Casos de plantas y plagas

### Takeaway
Las plagas tienen estados egg-larva-pupa-adult (insectos holometábolos) y "germinación" solo aplica a semillas/plantas. Si la foto de la plaga es mala, evaluar síntomas de la planta; los modelos de enfermedad entrenados en laboratorio generalizan mal al campo.

### Cited Findings
- Etapas de vida de insectos: huevo-larva-pupa-adulto es completo en holometábolos; hemimetábolos tienen ninfas [SIN FUENTE, general].
- EPPO Global Database: información básica de ~98,500 especies y registros detallados de >1,900 plagas reguladas; por plaga da distribución (mapa), plantas hospedantes y categorización cuarentenaria; páginas por hospedante listan plagas (tipos Host/Wild/Experimental) — [EPPO GD](https://gd.eppo.int/)
- CABI Invasive Species Compendium: fichas con hospedantes y distribución (cifras de 2015-2016: >1,500 a >2,000 fichas; desactualizado) — [Lucid key server PDF](https://keyserver.lucidcentral.org/key-server/data/0709090f-0c03-490e-8004-030c01080e07/media/Html/Invasive_species_compendium.pdf)
- Plantwise Knowledge Bank (CABI): guías, fichas, fotos en >100 idiomas; filtros por país; herramienta diagnóstica por síntomas y parte afectada; mapas de distribución — [Plantwise](https://www.botany.one/plantwise-knowledge-bank-of-crop-pests-diseases/)
- Datasets:
  - IP102: 75,222 imágenes, 102 clases de plagas, distribución long-tail, ~19,000 con cajas — [IEEE DataPort](https://ieee-dataport.org/documents/ip102); [hyper.ai](https://hyper.ai/en/datasets/19794). Reseña: [arXiv 2507.01494](https://arxiv.org/pdf/2507.01494)
  - PlantDoc: 2,598 imágenes, 13 especies, hasta 17 enfermedades, de la web (Google/Ecosia), no de laboratorio; espejo Dataset Ninja dice 2,482 (discrepancia) — [arXiv 1911.10317](https://arxiv.org/pdf/1911.10317)
  - Pl@ntNet-300K: 306,146 imágenes, 1,081 especies; 80% de especies = 11% de las imágenes; ambigüedad alta de etiquetas — [NeurIPS 2021](https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/file/7e7757b1e12abcb736ab9a754ffb617a-Paper-round2.pdf)
  - PlantVillage: 54,306 imágenes de hojas sanas/enfermas en condiciones controladas; 99.35% en test interno, pero 31.4% en imágenes de otras fuentes web (azar 2.6%) — [Mohanty et al. 2016](https://arxiv.org/pdf/1604.03169)
- Brecha lab→campo (estudios posteriores): vid EfficientNet-B2 99.61% interno → 66.80% externo; maíz 94.1% → 55.1%; fresa macro-F1 0.418-0.824 en campo — resumidos por buscador desde [MDPI sustainability 18-06867](https://mdpi-res.com/d_attachment/sustainability/sustainability-18-06867/article_deploy/sustainability-18-06867.pdf) y [PMC9330607](https://pmc.ncbi.nlm.nih.gov/articles/PMC9330607/) (verificar cada cifra en su paper). Explicación de atajos por fondo uniforme: fuente secundaria (blog).
- Pl@ntNet, iNaturalist como bases para plantas/hospedantes: no se obtuvo documentación primaria en esta sesión.

### Inferences
- Flujo: (1) ¿se ve el insecto? clasificar etapa (huevo/larva/pupa/adulto/ninfa); (2) si no, clasificar síntoma en la planta (mina, perforación, clorosis, mancha, melaza/fumagina) y devolver lista de plagas candidatas filtradas por cultivo+región vía EPPO/CABI; (3) marcar baja confianza. Aplicar "germinación" solo a semillas/plántulas.
- Entrenar con imágenes de campo; no confiar en cifras de PlantVillage.

### Gaps
- Tamaños/rendimiento actuales de modelos sobre IP102 (SOTA): no verificados. Fotos de síntomas como señal de diagnóstico: sin fuente primaria.

## 6. Bases de datos útiles

### Takeaway
GBIF (agregador de ocurrencias), iNaturalist (observaciones con ID comunitaria), catálogos taxonómicos por grupo (ASW, AmphibiaWeb, Reptile Database), SiB Colombia (datos nacionales vía GBIF), Xeno-canto (audio).

### Cited Findings
- GBIF: pasó de 1,000 millones de ocurrencias el 4 jul 2018; en abril 2018 tenía registros de 1,049,839 nombres de especies (cuenta de nombres, incluye sinónimos no reconocidos; no equivale a especies reales) — [NBN](https://nbn.org.uk/news/big-data-for-biodiversity-gbif-org-surpasses-1-billion-species-occurrence-records/). Cifra actual no obtenida.
- AmphibiaWeb: 9,081 especies (7 ago 2026) — [AmphibiaWeb listas](https://amphibiaweb.org/lists). ASW (AMNH): taxonomía/sinonimias/distribución de anfibios, >8,700 especies a 2024 — [ASW](https://amphibiansoftheworld.amnh.org/)
- SiB Colombia: >34 millones de registros abiertos (sept 2025), 254 organizaciones, >80,300 especies registradas; coordinado por Instituto Humboldt; publica en GBIF — [MinAmbiente](https://www.minambiente.gov.co/colombia-segundo-pais-del-mundo-con-mas-datos-publicos-sobre-biodiversidad/)
- EPPO GD, CABI ISC, Plantwise: ver sección 5.

### Gaps
- Reptile Database (datos actuales, nº especies), Xeno-canto (totales globales), iNaturalist (totales): sin cifra obtenida; Xeno-canto solo mostró páginas de colaboradores.
