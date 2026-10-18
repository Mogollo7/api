# Ética de la IA y normativa de datos personales (Colombia) para una plataforma de identificación de biodiversidad en Antioquia

**Herramientas.** WebFetch falló (DNS: `getaddrinfo ENOTFOUND`) y `curl` por el proxy dio 403 CONNECT en unesdoc.unesco.org, api.crossref.org y www.secretariasenado.gov.co, así que NO se abrió ninguna página oficial. WebSearch sí funcionó. Todo lo de abajo se verificó solo por resultados de búsqueda (URL devuelta por el buscador + resumen), nunca por lectura directa del texto. Cada dato debe leerse con esa salvedad. Lo que no apareció en la búsqueda se marca «NO VERIFICADO».

## 1. Marcos éticos internacionales de IA

### Takeaway
DOI verificados por búsqueda: Floridi y Cowls (10.1162/99608f92.8cd550d1) y Jobin et al. (10.1038/s42256-019-0088-2). UNESCO, OCDE y HLEG existen y sus fechas se confirman, pero el id exacto de unesdoc, la URL española oficial y el DOI/URL de publications.europa.eu del HLEG NO se pudieron verificar.

### Cited Findings
- Floridi, L., & Cowls, J. (2019). A unified framework of five principles for AI in society. *Harvard Data Science Review, 1*(1). https://doi.org/10.1162/99608f92.8cd550d1 (CC BY 4.0). Cuatro principios de la bioética (beneficencia, no maleficencia, autonomía, justicia) más un quinto, explicabilidad (inteligibilidad y rendición de cuentas). Fecha de publicación discrepante entre fuentes (1 jul. vs 20 sep. 2019); se cita por DOI — [PhilArchive/Ethics&Technology](https://ethicsandtechnology.org/a-unified-framework-of-five-principles-for-ai-in-society/), [HDSR autor](https://hdsr.mitpress.mit.edu/user/luciano-floridi)
- Jobin, A., Ienca, M., & Vayena, E. (2019). The global landscape of AI ethics guidelines. *Nature Machine Intelligence, 1*, 389–399. https://doi.org/10.1038/s42256-019-0088-2. Convergencia en cinco principios: transparencia, justicia y equidad, no maleficencia, responsabilidad, privacidad; con divergencia en su interpretación e implementación. Preprint: arXiv 1906.11668 — [arXiv](https://arxiv.org/abs/1906.11668v1), [ETH](https://ethicsandtechnology.org/important-report-by-eth-on-the-global-landscape-of-ai-ethics-guidelines/)
- OCDE (2019). Recommendation of the Council on Artificial Intelligence, OECD/LEGAL/0449. Adoptada el 22 may. 2019; revisada el 8 nov. 2023 (definición de «sistema de IA») y el 3 may. 2024. Texto oficial en legalinstruments.oecd.org; PDF devuelto por el buscador: https://legalinstruments.oecd.org/public/doc/648/648.en.pdf — [resultado de búsqueda OCDE](https://legalinstruments.oecd.org/public/doc/648/648.en.pdf). El buscador indicó que el PDF lleva copyright 2026, por lo que podría haber cambios posteriores a 2024 (no confirmado).
- Grupo de Expertos de Alto Nivel sobre IA (2019). Directrices éticas para una IA fiable. Comisión Europea; presentadas el 8 abr. 2019; IA fiable = lícita, ética y robusta; siete requisitos clave; lista de evaluación; 52 expertos; no vinculantes. Página oficial (versión inglesa): https://digital-strategy.ec.europa.eu/en/library/ethics-guidelines-trustworthy-ai ; la CE publicó el texto también en español (página `digital-strategy.ec.europa.eu/es/node/1950` devuelta por el buscador, sin leer su contenido) — [Comisión Europea](https://digital-strategy.ec.europa.eu/en/library/ethics-guidelines-trustworthy-ai)
- UNESCO (2021). Recomendación sobre la ética de la inteligencia artificial. Adoptada por la Conferencia General, 41.ª reunión, París, 9–24 nov. 2021 (aprobada el 23 nov. 2021); incluye valores, principios, 11 áreas de acción política, evaluación del impacto ético y evaluación de preparación. Un PDF en español con código SHS/BIO/PI/2021/1 está en la Biblioteca Digital de la ONU: https://digitallibrary.un.org/record/4062376/files/1416674-ES.pdf (el título exacto de ese PDF no se leyó) — [Biblioteca Digital ONU](https://digitallibrary.un.org/record/4062376/files/1416674-ES.pdf), [CIDOB](https://gouai.cidob.org/?p=628)

### Inferences
- Para contrastar el texto del proyecto, los cinco principios de Floridi y Cowls más la privacidad y la responsabilidad de Jobin et al. cubren el núcleo; el HLEG añade supervisión humana, robustez, gobernanza de datos, bienestar social/ambiental y rendición de cuentas (siete requisitos; lista completa NO leída en la sesión, verificar en el documento).

### Gaps
- UNESCO: el ark `pf0000381137` sugerido NO VERIFICADO (la búsqueda solo devolvió `pf0000378931`, que es el borrador). No se encontró registro español en unesdoc; la versión española oficial en unesdoc NO VERIFICADO. Referencia APA en español queda pendiente de abrir la ficha.
- OCDE: no se obtuvo la lista de principios (valores: crecimiento inclusivo, derechos humanos y valores democráticos, transparencia y explicabilidad, solidez/seguridad, responsabilidad) leyendo la fuente; NO VERIFICADO en sesión. Título en español oficial NO VERIFICADO.
- HLEG: DOI/URL de publications.europa.eu y título exacto del PDF español NO VERIFICADO.
- Jobin et al.: la lista completa de los 11 principios NO se confirmó en la sesión (búsqueda solo devolvió los 5 más frecuentes). Recuerdo del modelo, sin fuente: transparencia, justicia y equidad, no maleficencia, responsabilidad, privacidad, beneficencia, libertad y autonomía, confianza, sostenibilidad, dignidad, solidaridad; verificar en el artículo.
- Metadatos Crossref (volumen, número, páginas) no consultados directamente (api.crossref.org bloqueado).

## 2. Política y ley colombiana

### Takeaway
Ley 1581 de 2012 y CONPES 3975 existen y sus datos básicos se confirman por copias oficiales de terceros entidades públicas; las URL de Secretaría del Senado y DNP NO se pudieron abrir. El Marco Ético 2021 aparece en prensa, pero no se halló el documento oficial.

### Cited Findings
- Ley Estatutaria 1581 de 2012, expedida el 17 oct. 2012, Diario Oficial 48.587; desarrolla el derecho a conocer, actualizar y rectificar datos en bases de datos; se aplica al tratamiento en territorio colombiano; excluye bases de uso exclusivamente personal o doméstico; reglamentada parcialmente por el Decreto 1377 de 2013 — [Colombia Compra Eficiente](https://relatoria.colombiacompra.gov.co/normativa/ley-1581-de-2012/?print=pdf), [Salud Capital PDF](https://www.saludcapital.gov.co/Normo/gsp/ley_1581_de_2012.pdf), [DIAN normograma](https://normograma.dian.gov.co/dian/compilacion/docs/ley_1581_2012.htm). La URL esperada de Senado (`https://www.secretariasenado.gov.co/senado/basedoc/ley_1581_2012.html`) NO se pudo abrir ni apareció en resultados: NO VERIFICADO.
- Existen proyectos de reforma de la Ley 1581 en trámite (2025–2026) — [Gaceta, búsqueda](https://www.redjurista.com/Compilaciones2018/gacetasCongreso/2026/gc_1217_2026.pdf); estado actual NO VERIFICADO.
- CONPES 3975 (2019), Política Nacional para la Transformación Digital e Inteligencia Artificial, fechado 8 nov. 2019, DNP/MinTIC/Presidencia — copias: [Registraduría PDF](https://registraduria.gov.co/IMG/pdf/documento-conpes-3975.pdf), [ICFES PDF](https://normograma.icfes.gov.co/docs/pdf/conpes_dnp_3975_2019.pdf), [MinTIC normograma](https://normograma.mintic.gov.co/mintic/compilacion/docs/conpes_dnp_3975_2019.htm). La URL de DNP NO se verificó. El resumen busca generar valor social y económico con tecnologías digitales.
- CONPES 4144 de 2025 (Política Nacional de IA), aprobado el 14 feb. 2025, hoja de ruta a 2030, ejes que incluyen ética y gobernanza; sustituye en la práctica como marco vigente de IA — [DNP](https://dnp.gov.co/publicaciones/Planeacion/Paginas/conpes-4144-hoja-de-ruta-colombia-inteligencia-artificial-retos-actuales-transformacion-futura.aspx), [Colpensiones copia](https://normativa.colpensiones.gov.co/colpensiones/compilacion/docs/CONPES_DNP_4144_2025.htm)
- Marco Ético para la IA en Colombia (2021): presentado por el gobierno Duque (consejero presidencial Víctor Muñoz) con 10 principios (transparencia, privacidad, control humano de decisiones, prevalencia de derechos de niños, niñas y adolescentes), con apoyo de BID y CAF; consulta pública hasta el 2 dic. — [DPL News](https://dplnews.com/?p=77669). Documento base: Guío Español (2020), por encargo de CAF, que aclara no representar opiniones oficiales — [Univ. Sergio Arboleda copia](https://www.usergioarboleda.edu.co/wp-content/uploads/2021/11/Marco-etico-para-la-inteligencia-artificial-en-Colombia-Maestria-en-Inteligencia-artificial.pdf) (contenido no leído).

### Inferences
- Para el proyecto convendría citar CONPES 4144 (2025) además del 3975, porque es la política de IA más reciente (fuera del encargo original, añadido por el hallazgo).
- Si la plataforma recoge fotos con geolocalización de usuarios o datos de cuenta, Ley 1581 aplica a esos datos personales; los registros de especies en sí no son datos personales (inferencia, no verificada jurídicamente).

### Gaps
- Decreto 1377 de 2013: solo confirmado como reglamentario parcial; también está compilado hoy en el Decreto 1074 de 2015 (recuerdo, NO VERIFICADO).
- Documento oficial del Marco Ético 2021 en Presidencia/MinTIC: no encontrado; solo prensa. La guía ética de la CRC/MinTIC citada por el buscador no se verificó.
- Artículos concretos (principios art. 4, datos sensibles art. 5) no leídos: NO VERIFICADO.

## 3. Ética de compartir datos de biodiversidad y ocultar ubicaciones de especies amenazadas

### Takeaway
Chapman (2020) es la guía de referencia de GBIF; iNaturalist ofusca por defecto las ubicaciones de taxones amenazados (cuadro de 0,2 × 0,2 grados).

### Cited Findings
- Chapman, A. D. (2020). *Current best practices for generalizing sensitive species occurrence data* (v1.0). GBIF Secretariat, Copenhague. https://doi.org/10.15468/doc-5jp4-5g10 (DOI dado por el buscador; no resuelto en sesión). Actualiza Chapman y Grafton (2008); CC BY-SA 4.0; versión en español: «Buenas prácticas para generalizar datos de especies sensibles en registros biológicos» — [GBIF docs](https://docs.gbif.org/sensitive-species-best-practices/master/en/), [PDF español](https://docs.gbif.org/sensitive-species-best-practices/master/es/buenas-practicas-para-generalizar-datos-de-especies-sensibles-en-registros-biologicos.es.pdf), [noticia GBIF](https://www.gbif.org/news/18GVsWZ6Heas1RBAEmHHSv)
- Objetivo: publicar la mayor cantidad posible de datos de taxones sensibles sin exponer a las especies a daño — [GBIF docs](https://docs.gbif.org/sensitive-species-best-practices/master/en/)
- iNaturalist: el público ve un punto aleatorio dentro de un cuadro de 0,2° × 0,2° (~500 km² en el ecuador); el observador ve la ubicación real; taxones amenazados se marcan «obscured» y pocos «private»; no hay política oficial única, los curadores deciden y la actualización desde la Lista Roja de la UICN está desfasada — [iNaturalist Help](https://help.inaturalist.org/en/support/solutions/articles/151000233080-how-does-inaturalist-protect-the-locations-of-sensitive-species-), [foro iNaturalist](https://forum.inaturalist.org/t/why-do-some-of-my-endangered-species-observations-continue-to-get-obfuscated/30388)

### Inferences
- Una política razonable para la plataforma: generalizar o ocultar coordenadas de especies amenazadas (lista UICN/Resolución 1912 de 2017 colombiana, esta última no verificada) y conservar la precisión solo para el titular del registro.

### Gaps
- Contenido de recomendaciones concretas de Chapman (2020) no leído.
- Normativa colombiana de especies amenazadas y datos de biodiversidad (Resolución 1912/2017, SiB Colombia): no investigada.
