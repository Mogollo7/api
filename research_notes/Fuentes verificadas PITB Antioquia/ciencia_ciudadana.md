# Ciencia ciudadana en monitoreo de biodiversidad: calidad, motivación, confianza en IA y comunicación (PITB Antioquia)

## Método y herramientas (leer primero)

- FALLÓ: `api.crossref.org`, `api.openalex.org`, `api.semanticscholar.org`, `doi.org`, `redalyc.org`, `scielo.org`, `dialnet.unirioja.es` (Bash: proxy responde 403 al CONNECT) y también WebFetch (error DNS `ENOTFOUND` en crossref, openalex, pmc.ncbi, iiasa, wiley). No se pudo abrir ningún DOI ni PDF directamente.
- FUNCIONÓ: solo WebSearch. Devuelve un resumen redactado por un modelo sobre registros de repositorios, editoriales y bases de datos. Las referencias de abajo se contrastaron contra esos registros, no contra la página del editor.
- Criterio: dato confirmado en un registro bibliográfico = "VERIFICADO (vía búsqueda)". Dato que solo conozco de memoria o que no apareció = "NO VERIFICADO". Las iniciales de nombre de pila no salieron en los registros, salvo donde se indica; hay que completarlas desde la página del editor antes de entregar. Recomendación: abrir cada DOI en el PC del usuario (doi.org) para el chequeo final.

## 1. Ciencia ciudadana para datos de biodiversidad (fuentes clave)

### Takeaway
Hay cinco fuentes sólidas y verificadas: Chandler et al. 2017 (alcance global y vacíos), Theobald et al. 2015 (potencial no aprovechado), Pocock et al. 2017 (diversidad de proyectos), Pocock et al. 2018 (visión de monitoreo global) y Bonney et al. 2009/2014 (modelo de proyecto y próximos pasos).

### Cited Findings
- Chandler et al. (2017) construyeron una base de datos de programas de ciencia ciudadana (CS) y monitoreo comunitario (CBM) y los cruzaron con las Variables Esenciales de Biodiversidad. Los datos CS aportan sobre todo distribución y abundancia de especies, fenología y función ecosistémica. Solo aves, mariposas y plantas se monitorean a escala. Hay más esquemas en Europa, Norteamérica, Sudáfrica, India y Australia, y menos en el trópico. Abierto (CC BY). — [IIASA/Arizona/resumen](https://pure.iiasa.ac.at/13923); [Arizona](https://experts.arizona.edu/en/publications/contribution-of-citizen-science-towards-international-biodiversit/)
  - Referencia: Chandler, M., See, L., Copas, K., Bonde, A. M. Z., López, B. C., Danielsen, F., Legind, J. K., Masinde, S., Miller-Rushing, A. J., Newman, G., Rosemartin, A., & Turak, E. (2017). Contribution of citizen science towards international biodiversity monitoring. *Biological Conservation, 213*(Part B), 280–294. https://doi.org/10.1016/j.biocon.2016.09.004 — apellidos, revista, volumen, páginas y DOI VERIFICADOS; iniciales NO VERIFICADAS.
  - Cifra "más de 3600 proyectos" y ">50 % de los datos de GBIF vienen de ciencia ciudadana": aparecen en resúmenes secundarios (GBIF, nota de prensa CREAF), no en el artículo; no citar como cifra del artículo sin comprobarla. — [GBIF](https://tools.gbif.org/data-use/83208), [CREAF](https://www.creaf.cat/es/node/69915)
- Theobald et al. (2015) revisaron 388 proyectos de biodiversidad con ciencia ciudadana. Estiman unos 1,3 millones de voluntarios. Solo ~12 % alimentó con claridad artículos revisados por pares. La publicación fue más probable con escala espacial amplia, larga duración, datos públicos y capacitación en identificación taxonómica. — [Univ. de Washington](https://www.biology.washington.edu/pubs/global-change-and-local-solutions-tapping-unrealized-potential-citizen-science-biodiversity-res); [ICIMOD](https://lib.icimod.org/record/30232)
  - Referencia: Theobald, E. J., Ettinger, A. K., Burgess, H. K., DeBey, L. B., Schmidt, N. R., Froehlich, H. E., Wagner, C., HilleRisLambers, J., Tewksbury, J., Harsch, M. A., & Parrish, J. K. (2015). Global change and local solutions: Tapping the unrealized potential of citizen science for biodiversity research. *Biological Conservation, 181*, 236–244. https://doi.org/10.1016/j.biocon.2014.10.021 — título, revista, volumen, páginas y DOI VERIFICADOS. La lista de autores se comprobó solo parcialmente (una búsqueda dijo que "coincide", otra que un listado la ordena distinto): ORDEN E INICIALES NO VERIFICADOS.
- Pocock, Tweddle, Savage, Robinson y Roy (2017) identificaron 509 proyectos ambientales y ecológicos, los puntuaron en 32 atributos y encontraron variación continua entre "participación masiva" y "monitoreo sistemático". Cluster aparte de proyectos totalmente informáticos. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC5378328); [RePEc](https://ideas.repec.org/a/plo/pone00/0172579.html)
  - Referencia: Pocock, M. J. O., Tweddle, J. C., Savage, J., Robinson, L. D., & Roy, H. E. (2017). The diversity and evolution of ecological and environmental citizen science. *PLOS ONE, 12*(4), e0172579. https://doi.org/10.1371/journal.pone.0172579 — VERIFICADA (iniciales: M. J. O., J. C., J., L. D., H. E. confirmadas por el nombre completo en el resumen).
- Pocock et al. (2018) proponen una visión de monitoreo global de biodiversidad con ciencia ciudadana: actividades factibles para participantes y útiles para usuarios de datos de lo local a lo global. — [NORA](https://nora.nerc.ac.uk/id/eprint/521398/); [repositorio UC](https://repositorio.uc.cl/dspace/items/a4636984-3c74-4607-8fd5-667179302c52/full)
  - Referencia (parcial): Pocock, M. J. O., Chandler, M., [coautores intermedios NO VERIFICADOS], Danielsen, F. (2018). A vision for global biodiversity monitoring with citizen science. En D. A. Bohan, A. J. Dumbrell, G. Woodward, & M. Jackson (Eds.), *Next generation biomonitoring: Part 2* (Advances in Ecological Research, Vol. 59, pp. 169–223). Academic Press. https://doi.org/10.1016/bs.aecr.2018.06.003 — DOI, volumen y páginas VERIFICADOS; lista completa de autores y título del volumen NO VERIFICADOS. Nota: NO es un artículo sobre calidad de datos, aunque el encargo lo mencionaba así.
- Bonney et al. (2009) presentan el modelo de proyecto desarrollado en el Cornell Lab of Ornithology, útil para monitoreo de biodiversidad, investigación y educación. Acceso de pago. — [BioOne](https://bioone.org/journals/bioscience/volume-59/issue-11/bio.2009.59.11.9/Citizen-Science--A-Developing-Tool-for-Expanding-Science-Knowledge/10.1525/bio.2009.59.11.9.full); [EU-Citizen.Science](https://eu-citizen.science/resource/25)
  - Referencia: Bonney, R., Cooper, C. B., Dickinson, J., Kelling, S., Phillips, T., Rosenberg, K. V., & Shirk, J. (2009). Citizen science: A developing tool for expanding science knowledge and scientific literacy. *BioScience, 59*(11), 977–984. https://doi.org/10.1525/bio.2009.59.11.9 — VERIFICADA (siete autores, volumen, número, páginas, DOI); iniciales NO VERIFICADAS.
- Bonney et al. (2014), Policy Forum en *Science*: la ciencia ciudadana no es aceptada universalmente y los datos de voluntarios a veces tienen dificultad para ser revisados. Piden diseño sólido de monitoreo, tecnología abierta de gestión y análisis de datos, y formación profesional. — [Washington COASST (PDF)](https://depts.washington.edu/coasst/news/publications/Science%20Policy%20Forum.pdf); [Idaho Ecosystems](https://www.idahoecosystems.org/node/107)
  - Referencia: Bonney, R., Shirk, J. L., Phillips, T. B., Wiggins, A., Ballard, H. L., Miller-Rushing, A. J., & Parrish, J. K. (2014). Next steps for citizen science. *Science, 343*(6178), 1436–1437. https://doi.org/10.1126/science.1251554 — VERIFICADA (autores, volumen, número, páginas, DOI).

### Inferences
- Chandler (vacíos geográficos y taxonómicos) y Theobald (poco uso en publicaciones) sirven para justificar que una plataforma antioqueña con fauna y flora aporte a una zona poco cubierta. Es una inferencia mía, no una afirmación de los autores sobre Antioquia.
- Pocock 2017 sirve para ubicar el proyecto en el continuo "participación masiva vs. monitoreo sistemático" (el PITB se acerca a lo primero: fotos oportunistas).

### Gaps
- No se leyó ningún texto completo; todo viene de resúmenes y registros.
- Iniciales de nombres de pila y listas completas de autores pendientes (marcado arriba).
- El encargo mencionaba "Pocock et al. 2018/2017 sobre calidad de datos": no se encontró un artículo con ese perfil. Para calidad de datos se verificó Kosmala et al. 2016 (sección 2).

## 2. Calidad, validación y sesgo en registros ciudadanos

### Takeaway
La evidencia converge en que los datos ciudadanos pueden ser comparables a los de profesionales si hay capacitación, validación por expertos y réplica, pero los registros oportunistas tienen sesgo espacial y de esfuerzo que exige modelado o protocolos semiestructurados.

### Cited Findings
- Kosmala, Wiggins, Swanson y Simmons (2016): la calidad se debe evaluar caso por caso; hay proyectos que igualan o superan la exactitud profesional; estrategias: capacitar y probar voluntarios, validación experta, replicación entre voluntarios, corrección estadística del error sistemático. — [bioRxiv](https://www.biorxiv.org/content/10.1101/074104v1); [Ocean Best Practices](https://repository.oceanbestpractices.org/handle/11329/2155)
  - Referencia: Kosmala, M., Wiggins, A., Swanson, A., & Simmons, B. (2016). Assessing data quality in citizen science. *Frontiers in Ecology and the Environment, 14*(10), 551–560. https://doi.org/10.1002/fee.1436 — revista, volumen, número, páginas y DOI VERIFICADOS; los cuatro apellidos son los de mi consulta y los registros los respaldan en conjunto, iniciales NO VERIFICADAS.
- Isaac et al. (2014): las fuentes de datos tienen compromisos; los esquemas de largo plazo dan datos de calidad pero cubren pocos taxones y regiones, y los registros oportunistas son abundantes pero poco estructurados. Carecen de ausencias y de esfuerzo de muestreo. — [NORA](https://nora.nerc.ac.uk/id/eprint/508444/); [Methods.blog](https://methodsblog.com/?p=9031)
  - Referencia: Isaac, N. J. B., van Strien, A. J., August, T. A., de Zeeuw, M. P., & Roy, D. B. (2014). Statistics for citizen science: Extracting signals of change from noisy ecological data. *Methods in Ecology and Evolution, 5*(10), 1052–1060. https://doi.org/10.1111/2041-210X.12254 — VERIFICADA (nombres completos de los autores aparecen en el registro).
- Kelling et al. (2019): la mayoría de datos de monitoreo viene de voluntarios y falta información para corregir sesgos del observador; proponen registrar también el proceso de observación (eBird), con un continuo de estructurado a oportunista. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6422830); [St Andrews](https://research-portal.st-andrews.ac.uk/en/publications/using-semistructured-surveys-to-improve-citizen-science-data-for-/)
  - Referencia (parcial): Kelling, S., Johnston, A., Bonn, A., Fink, D., Ruiz-Gutierrez, V., Bonney, R., Fernandez, M., Hochachka, W. M., Julliard, R., Kraemer, R., & Guralnick, R. (2019). Using semistructured surveys to improve citizen science data for monitoring biodiversity. *BioScience, 69*(3), 170–179. https://doi.org/10.1093/biosci/biz010 — título, revista, volumen, número, páginas y DOI VERIFICADOS; un registro da los primeros diez autores y "et al.", el último autor "Guralnick" proviene de mi memoria: NO VERIFICADO.
- Kelling et al. (2015) estiman habilidad de observadores de eBird con curvas de acumulación de especies; la habilidad mejora con la participación continua. — [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4599805/); [eBird](https://ebird.org/news/plos2015)
  - Referencia (parcial): Kelling, S., [coautores NO VERIFICADOS] (2015). Can observation skills of citizen scientists be estimated using species accumulation curves? *PLOS ONE, 10*(10), e0139600. https://doi.org/10.1371/journal.pone.0139600 — título, volumen, artículo y DOI VERIFICADOS; autores completos NO VERIFICADOS.
- Aceves-Bueno et al. (2017), revisión cuantitativa: según resúmenes secundarios, 62 % de los artículos que comparan valores P no halló diferencia significativa, y 55 % de los que reportan % de acuerdo mostró ≥80 %. Recomiendan una muestra de referencia profesional y capacitación. Otra fuente secundaria da "73 %" y "casi 50 % de divergencia"; las cifras difieren, no citar ninguna sin leer el artículo. — [JSTOR Daily](https://daily.jstor.org/a-scientific-look-at-citizen-science); [McMaster](https://synopsis.mcmaster.ca/science-for-the-people/)
  - Referencia (parcial): Aceves-Bueno, E., [coautores NO VERIFICADOS]. (2017). The accuracy of citizen science data: A quantitative review. *Bulletin of the Ecological Society of America, 98*(4), 278–290. DOI: NO VERIFICADO (el que probé, 10.1002/bes2.1336, no se pudo confirmar). Volumen, número y páginas solo vienen de JSTOR Daily (secundaria).

### Inferences
- Para el PITB, la validación con IA más revisión de expertos y el registro de metadatos (fecha, lugar, observador, esfuerzo) se apoya en Kosmala 2016 y Kelling 2019.
- Como la plataforma recoge registros oportunistas, Isaac 2014 sirve para advertir que no hay datos de ausencia y que el esfuerzo no es uniforme antes de usarlos en ordenamiento territorial.

### Gaps
- Aceves-Bueno 2017: autores y DOI sin verificar; no usar hasta confirmar en la página de ESA/Wiley.
- Kelling 2015: autores no obtenidos.

## 3. Motivación y participación

### Takeaway
Dos fuentes verificadas: West y Pateman (2016) sobre reclutamiento y retención y Rotman et al. (2012) sobre cómo cambia la motivación durante el proyecto.

### Cited Findings
- West y Pateman (2016) vinculan teorías del voluntariado con ejemplos de voluntariado ambiental y ciencia ciudadana; sostienen que la organización del proyecto es central y debe considerar motivaciones, atributos personales y cómo se entera la gente. Acceso abierto CC BY 4.0. — [DOAJ](https://doaj.org/article/efdc5391e4334d6cba43aa673d079082); [White Rose](https://eprints.whiterose.ac.uk/id/eprint/114091/)
  - Referencia: West, S., & Pateman, R. (2016). Recruiting and retaining participants in citizen science: What can be learned from the volunteering literature? *Citizen Science: Theory and Practice, 1*(2), Artículo 15. https://doi.org/10.5334/cstp.8 — VERIFICADA (nota: SEI lista 2017, la revista dice diciembre de 2016).
- Rotman et al. (2012): la motivación de voluntarios en ciencia ciudadana ecológica cambia a lo largo del proyecto; intereses personales y factores externos (atribución, reconocimiento) la moldean. — [Unpaywall/ACM](https://unpaywall.org/10.1145%2F2145204.2145238); [UMD](https://lccd.umiacs.umd.edu/node/14906)
  - Referencia: Rotman, D., Preece, J., Hammock, J., Procita, K., Hansen, D., Parr, C., Lewis, D., & Jacobs, D. (2012). Dynamic changes in motivation in collaborative citizen-science projects. En *Proceedings of the ACM 2012 Conference on Computer Supported Cooperative Work (CSCW '12)* (pp. 217–226). ACM. https://doi.org/10.1145/2145204.2145238 — VERIFICADA (autores, páginas, DOI).

### Inferences
- Rotman respalda dar reconocimiento (atribución del autor de cada foto) en la plataforma; West y Pateman respaldan pensar el reclutamiento más allá de la motivación individual. Inferencia mía.

### Gaps
- No se buscaron estudios de motivación en Colombia ni en América Latina.

## 4. Confianza humana en la identificación por IA y explicabilidad

### Takeaway
Existe un estudio cualitativo directo en una app de identificación de aves (Merlin); no encontré estudios revisados por pares sobre explicabilidad en iNaturalist u otras apps de especies.

### Cited Findings
- Kim et al. (2023) entrevistaron a 20 usuarios de una app de identificación de aves basada en IA: la ven confiable pero aceptan sus resultados de forma selectiva tras conductas de verificación, y algunos renuncian a usarla en situaciones de alto riesgo. El conocimiento del dominio y el contexto influyen en la confianza. — [arXiv](https://arxiv.org/pdf/2305.08598); [Princeton](https://collaborate.princeton.edu/en/publications/humans-ai-and-context-understanding-end-users-trust-in-a-real-wor/)
  - Referencia: Kim, S. S. Y., Watkins, E. A., Russakovsky, O., Fong, R., & Monroy-Hernández, A. (2023). Humans, AI, and context: Understanding end-users' trust in a real-world computer vision application. En *Proceedings of the 2023 ACM Conference on Fairness, Accountability, and Transparency (FAccT '23)* (13 pp.). ACM. https://doi.org/10.1145/3593013.3593978 — autores y DOI VERIFICADOS en búsqueda; páginas exactas NO VERIFICADAS. La app es Merlin Bird ID según el resumen de la búsqueda; el nombre no se comprobó en el artículo.
- Fiabilidad de iNaturalist (no confianza/explicabilidad): estudios de caso con liquenes (2023) y hormigas (preprint bioRxiv 2025) comparan identificaciones con las de expertos. — [Munzi et al. 2023 (PDF)](https://iris.unipa.it/retrieve/31375fc4-485f-4dc8-8716-d78e4ca80e4c/Munzi%20et%20al%202023.pdf); [bioRxiv 2025](https://www.biorxiv.org/content/10.1101/2025.02.08.637263.full.pdf). Referencias completas NO VERIFICADAS; solo se vio el enlace.

### Inferences
- Kim 2023 respalda mostrar el nivel de certeza de la IA y exigir verificación humana (o experta) de registros dudosos. Es inferencia mía; el estudio no evalúa plataformas de planificación territorial.

### Gaps
- Sin estudio verificado de explicabilidad en apps de especies. Un comentario crítico sobre iNaturalist (skeptic.org.uk) no es académico y no se usa.

## 5. Fuentes en español ya citadas por el proyecto

### Takeaway
Ambas existen. Gumucio-Dagron: el año del volumen es 2011 según una fuente y 2012 según el sitio de la revista; Servaes: coincide con lo citado.

### Cited Findings
- Gumucio-Dagron, *Signo y Pensamiento* 30(58), pp. 26–39, DOI 10.11144/Javeriana.syp30-58.cpcs. El número es enero–junio de 2011, pero la página de la revista indica publicado el 2012-05-30. El resumen distingue dos corrientes: modernización, y luchas anticoloniales y antidictatoriales; el artículo cuestiona un desarrollo sin participación de los afectados. Aparece también en Pereira y Cadavid (2011), *Comunicación, desarrollo y cambio social* (Pontificia Universidad Javeriana). — [Revista Javeriana](https://revistas.javeriana.edu.co/index.php/signoypensamiento/article/view/2454); [Dialnet](https://dialnet.unirioja.es/servlet/articulo?codigo=8062838); [SciELO Colombia](http://www.scielo.org.co/scielo.php?script=sci_arttext&pid=S0120-48232011000100002)
  - Referencia: Gumucio-Dagron, A. (2011). Comunicación para el cambio social: Clave del desarrollo participativo. *Signo y Pensamiento, 30*(58), 26–39. https://doi.org/10.11144/Javeriana.syp30-58.cpcs — título, volumen, número y páginas VERIFICADOS (vía búsqueda); DOI proviene de un resumen de búsqueda. **El año correcto en la cita APA es 2011** (el SciELO URL lleva S0120-4823**2011**; la edición del número es 2011). El proyecto cita 2012: corregir a 2011 o conservar 2012 solo si el usuario prefiere la fecha de publicación en línea. El apellido real es "Gumucio-Dagron" (una fuente lo escribe "Gumucio-Dragon", error de ese sitio).
- Servaes (2012), *CIC Cuadernos de Información y Comunicación* 17, pp. 17–40, monográfico "Comunicación, cambio social y desarrollo", publicado 2012-09-26. Recibido 7-mar-2012, aceptado 4-abr-2012. Acceso abierto CC BY 4.0. — [UCM](https://revistas.ucm.es/index.php/CIYC/article/view/39256); [número](https://revistas.ucm.es/index.php/CIYC/issue/view/2257); [Redalyc](https://www.redalyc.org/pdf/935/93524422007.pdf)
  - Referencia: Servaes, J. (2012). Comunicación para el desarrollo sostenible y el cambio social. Una visión general. *CIC Cuadernos de Información y Comunicación, 17*, 17–40. DOI: NO VERIFICADO. El DOI que probé (10.5209/rev_CIYC.2012.v17.39256) sigue el patrón del número, pero no se confirmó; no incluirlo hasta comprobarlo en doi.org. Si no se confirma, usar la URL de UCM arriba.

### Inferences
- Ambos textos sostienen un enfoque participativo de la comunicación, adecuado al marco de la plataforma. Esto es de los resúmenes; no se leyó el texto completo de ninguno.

### Gaps
- Pendiente confirmar en el PC del usuario el DOI de Servaes y la decisión 2011 o 2012 para Gumucio-Dagron.
- Sin lectura de texto completo: cualquier cita textual o número de página interna exige abrir los PDF.
