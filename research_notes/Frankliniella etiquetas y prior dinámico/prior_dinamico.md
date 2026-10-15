# Prior geográfico y contextual dinámico para identificación de especies

Nota de método: solo se leyeron en texto completo los artículos de Mac Aodha 2019 y Cole 2023 (PDF de arXiv). Las páginas oficiales de iNaturalist (blog 84677, blog 134410, ayuda de ALA/NZ) devolvieron 403 al recuperarlas; de ellas solo hay lo que muestran los resultados de búsqueda y la página de ayuda "Expected Nearby". La documentación de Merlin se conoce solo por resúmenes de búsqueda (la página de eBird fue bloqueada). Todo lo que no tiene fuente va marcado [SIN FUENTE].

## 1. Métodos publicados: qué hace cada uno con especies endémicas vs. amplias, datos que necesita, ganancias reportadas

### Takeaway
Los métodos van de conteos por celda (Berg 2014, "Seen Nearby" antiguo) a redes neuronales de ubicación con pérdida solo-presencia (Mac Aodha 2019, SINR). Ninguno trata "endémica vs. amplia" con un parámetro explícito: la escala espacial por especie emerge de los datos (kernel adaptativo o embedding aprendido), y la ganancia depende de cuántas observaciones hay por especie.

### Cited Findings
**Mac Aodha et al. 2019 (ICCV)**
- Prior espacio-temporal P(y|x) con x = (lon, lat, día del año), entrenado solo con presencias; se combina con cualquier clasificador con P(y|I,x) ∝ P(y|I)·P(y|x), asumiendo P(y) uniforme e independencia condicional de imagen y ubicación dado y — [Mac Aodha 2019, arXiv](https://arxiv.org/abs/1906.05272)
- Modelo: red totalmente conectada f(x) que da un embedding de 256 dimensiones; P(y|x) ≈ sigmoide(f(x)·O), con O la matriz de embeddings de especies. Entrada con codificación periódica sin/cos para que 31-dic y 1-ene queden cerca — [Mac Aodha 2019](https://arxiv.org/abs/1906.05272)
- Modela el sesgo del fotógrafo con un embedding por fotógrafo, usado solo en entrenamiento; no se necesita en inferencia — [Mac Aodha 2019](https://arxiv.org/abs/1906.05272)
- Pérdida "conservadora": asume ausente donde no se observó (positivos con peso λ = número de categorías, pseudo-negativos en ubicaciones aleatorias). Los autores dicen que es una suposición muy fuerte, pero permite que el prior baje agresivamente predicciones visuales incorrectas — [Mac Aodha 2019](https://arxiv.org/abs/1906.05272)
- Para contrarrestar el desbalance limitan a 100 puntos por categoría y época (excepto en YFCC, donde limitar empeoró) — [Mac Aodha 2019](https://arxiv.org/abs/1906.05272)
- Resultados top-1 (InceptionV3, sin prior → prior completo): iNat2017 val 63.27 → 69.60; iNat2018 val 60.20 → 72.68; iNat2018 con 520×520: 66.18 → 77.49; en top-3 iNat2018 77.90 → 87.26 — [Mac Aodha 2019, Tabla 2](https://arxiv.org/abs/1906.05272)
- BirdSnap (ubicaciones simuladas desde eBird) 70.07 → 79.58; NABirds 76.08 → 81.50 — [Mac Aodha 2019, Tabla 1](https://arxiv.org/abs/1906.05272)
- Con YFCC (objetos cotidianos sin estructura geográfica) todos los métodos rinden como "sin prior" (~50 %): el prior solo ayuda si las categorías tienen estructura espacio-temporal — [Mac Aodha 2019](https://arxiv.org/abs/1906.05272)
- Baselines comparados: vecino más cercano, grilla discretizada, kernel adaptativo de Berg et al. Añadir un prior uniforme a los métodos de vecinos aumentó su rendimiento, porque da robustez donde no hay observaciones cercanas — [Mac Aodha 2019](https://arxiv.org/abs/1906.05272)
- Berg et al. 2014 (Birdsnap) discretizaron espacio y tiempo en cubos y usaron un estimador de densidad por kernel adaptativo por especie, de forma independiente; el costo es memoria y la elección de discretización afecta el resultado — descrito en [Mac Aodha 2019](https://arxiv.org/abs/1906.05272); abstract de Berg: priors estimados a partir de observaciones en ubicaciones irregulares y sesgadas, que mejoran el rendimiento — [Birdsnap, CVPR 2014](https://openaccess.thecvf.com/content_cvpr_2014/html/Berg_Birdsnap_Large-scale_Fine-grained_2014_CVPR_paper.html)
- Limitaciones declaradas: calidad de la ubicación (puede ser inexacta u ofuscada a propósito), sesgos espaciales conocidos de ciencia ciudadana (arguyen que el sesgo de prueba es similar al de entrenamiento), y no usa variables ambientales — [Mac Aodha 2019, sec. 4.5](https://arxiv.org/abs/1906.05272)

**Cole et al. 2023 (SINR, ICML)**
- Entrena sobre 35.5 millones de observaciones de iNaturalist de 47,375 especies (antes de 2022), solo presencias; predice presencia en cualquier ubicación — [Cole 2023, arXiv](https://arxiv.org/abs/2306.02564)
- Pérdidas "assume negative" (AN): SSDL (misma especie, otro lugar aleatorio), SLDS (misma ubicación, otras especies) y LAN-full (combina ambas, usa todas las entradas de ŷ). LAN-full supera a LAN-SSDL y LAN-SLDS en la mayoría de casos y supera a la pérdida de Mac Aodha 2019 (LGP) en las cuatro tareas — [Cole 2023](https://arxiv.org/abs/2306.02564)
- Pseudo-negativos que siguen la distribución de los datos suelen ser mejores, salvo en IUCN: algunas especies viven lejos de zonas bien muestreadas, y LAN-SSDL se comporta mal donde hay pocos datos de entrenamiento — [Cole 2023](https://arxiv.org/abs/2306.02564)
- Tarea "Geo Prior": 282,974 imágenes de 39,444 especies (máx. 10 por especie, research grade, ene–may 2022); métrica = cambio en top-1 del clasificador al aplicar el prior en prueba. Ganancias: grilla discretizada con todos los datos +4.1; LGP de 2019 +5.2; LAN-full coords con 10 ejemplos por especie +4.6, 100 → +6.1, 1000 → +6.2 puntos — [Cole 2023, Tabla 1](https://arxiv.org/abs/2306.02564)
- 2,721 especies (9,808 imágenes) del conjunto de prueba no estaban en el entrenamiento del modelo de rango — [Cole 2023, apéndice](https://arxiv.org/abs/2306.02564)
- Con solo 10 ejemplos por especie (1 % de los datos) SINR supera en todas las tareas a la mejor grilla discretizada con todos los datos; "se necesitan más datos para detalle fino" (los mapas con pocos datos son suaves, sin información de alta frecuencia espacial) — [Cole 2023](https://arxiv.org/abs/2306.02564)
- Ejemplo cualitativo con Wood Thrush: LAN-full con pocos datos cubre casi todo el rango (pocos falsos negativos) y ajusta bordes al añadir datos; LAN-SSDL sobreestima y pierde la extensión sur — [Cole 2023, Fig. 7](https://arxiv.org/abs/2306.02564)
- Solo coordenadas rinden casi como coordenadas + variables ambientales (97 % en S&T, 93 % en IUCN, 95 % en Geo Prior); combinarlas es algo mejor — [Cole 2023](https://arxiv.org/abs/2306.02564)
- Limitar a 1000 ejemplos por especie en lugar de usar todos cambia poco: −0.79 MAP (S&T), −0.25 (IUCN), −1.1 puntos de top-1 (Geo Prior) — es decir, el desbalance perjudica poco y reducirlo compensa — [Cole 2023](https://arxiv.org/abs/2306.02564)
- Limitaciones: datos muy desbalanceados por especie y por región; regiones muy biodiversas poco representadas; benchmarks con puntos ciegos (limitados a especies bien descritas); modelos "no calibrados ni validados más allá de los experimentos"; precaución para conservación — [Cole 2023, sec. 4.5 y apéndice](https://arxiv.org/abs/2306.02564)

**iNaturalist "Expected Nearby" / geomodel**
- Antes: conteo relativo de observaciones en grilla de 1° y etiqueta "Seen Nearby" si había observaciones del taxón en las 9 celdas vecinas; luego se sustituyó por el geomodel (etiqueta "Expected Nearby") — [resumen de búsqueda sobre el blog](https://www.inaturalist.org/posts/84677) [contenido directo no verificable: 403]
- El geomodel recibe una ubicación y devuelve las especies más probables; se entrena con las mismas taxa y calendario mensual que el modelo de visión, solo con observaciones de iNaturalist y un mapa de elevación — [resumen de búsqueda sobre el blog](https://www.inaturalist.org/posts/84677)
- Por defecto, solo se muestran sugerencias visualmente similares y esperadas cerca; si ninguna visualmente similar está esperada cerca, se muestran las visualmente similares sin importar dónde se esperan — [Ayuda iNaturalist](https://help.inaturalist.org/en/support/solutions/articles/151000170371-what-does-expected-nearby-mean-)
- La ayuda NO especifica el criterio/umbral de "cerca" ni la exactitud del geomodel — [Ayuda iNaturalist](https://help.inaturalist.org/en/support/solutions/articles/151000170371-what-does-expected-nearby-mean-)
- Un comentario (no oficial verificado) en el blog dice que bastó la elevación como covariable, que añadir precipitación no mejoró lo suficiente y que elegir bien los umbrales "no lo hemos perfeccionado"; un umbral algo alto puede hacer desaparecer una especie de celdas donde sí ocurre — [resultado de búsqueda, comentarios del blog](https://www.inaturalist.org/blog/84677-introducing-the-inaturalist-geomodel) [de segunda mano]
- Actualizaciones posteriores: el geomodel pasó a entrenarse con SINR (antes celdas de grilla); según un post comunitario las versiones nuevas excluyen variables ambientales [afirmación de un autor del foro, verificar en notas oficiales] — [búsqueda: blog iNat](https://www.inaturalist.org/blog/134410)
- Críticas de usuarios: hexágonos de ~60 km complican a endémicos locales; la etiqueta se muestra solo si el hexágono donde cae la observación está en el modelo (no cuentan los vecinos); una especie sin suficientes observaciones no entra al modelo de visión y no tiene mapa — [foro iNat, CV suggesting out of range](https://forum.inaturalist.org/t/cv-suggesting-out-of-range-species/79857); [búsqueda sobre el foro](https://forum.inaturalist.org/t/list-of-suggested-species-expected-nearby-in-drop-down-menu-shows-species-ocurring-hundreds-of-kilometers-away/80485) [comentarios de usuarios, no personal oficial]
- Crítica de usuario: falta de clima; elevación como proxy débil (insectos de tierras bajas húmedas "esperados" en el desierto de Taklamakan) — [foro iNat, anuncio](https://forum.inaturalist.org/t/introducing-the-inaturalist-geomodel/45407)

**Merlin / eBird**
- Merlin pide ubicación y fecha de la foto y usa la frecuencia de reportes de eBird en la zona; Cornell dice que usa más de 415 millones de observaciones de eBird y que puede ser menos preciso en regiones remotas con pocos datos de eBird — [búsqueda: Cornell/eBird](https://ebird.org/nw/news/automatic-photo-id-thanks-to-your-ebirding) [página bloqueada; datos tomados del resumen de búsqueda]
- El modelo de visión se entrenó con millones de fotos de eBird — misma fuente [resumen]
- La implementación exacta (fórmula de combinación, escala espacial) no se encontró publicada en las fuentes accesibles

**Mapas de rango (IUCN, GBIF) y sus problemas**
- Los mapas de rango se critican por errores de comisión (especie "presente" donde no está) y de omisión; la protección se sobreestima al usarlos, más a resolución alta — [estudio en mamíferos, WCS/Uniroma1](https://library.wcs.org/en-us/doi/ctl/view/mid/33065/pubid/PUB22291.aspx)
- Los mapas IUCN no están refinados por altitud ni cobertura (Area of Habitat), por lo que incluyen hábitat inadecuado (comisión) y su resolución es gruesa — [resumen de búsqueda sobre productos IUCN](https://par.nsf.gov/biblio/10535289-combining-camera-trap-surveys-iucn-range-maps-improve-knowledge-species-distributions)
- Estudio de cámaras trampa (510 mamíferos medianos y grandes): las cámaras detectaron solo 39 % de las especies esperadas según rangos IUCN y AOH; 85 % de los desacuerdos "solo-IUCN" ocurrieron a menos de 200 km del borde del rango; solo 4 % de las ocurrencias detectadas cayeron fuera del rango IUCN — mismo enlace, [estudio único no verificado en texto completo]
- Crítica 2024 (J. Mammalogy): los mapas son estáticos, no reproducibles, con precisión variable; recomiendan uso a escalas gruesas (>200 km) más que para decisiones locales — [resumen de búsqueda](https://library.wcs.org/en-us/doi/ctl/view/mid/33065/pubid/PUB22291.aspx) [fuente agregada, verificar]
- En SINR el mapa IUCN se usa como referencia; los autores advierten que los benchmarks tienen inexactitudes — [Cole 2023](https://arxiv.org/abs/2306.02564)

### Inferences
- Ningún método publicado usa una "dimensión de endemismo" explícita. El kernel adaptativo (Berg) y el embedding aprendido (Mac Aodha/SINR) ajustan la escala espacial por especie de forma implícita: especie con pocos puntos o agrupados da un prior localizado o suave; especie con muchos puntos dispersos da uno amplio. Para endémicos con pocos puntos, el modelo suave (SINR con 10 ejemplos produce mapas sin detalle) tiende a "emborronar" el rango, lo que coincide con la queja de usuarios sobre hexágonos de 60 km y endémicos locales.
- Que Mac Aodha 2019 y SINR reporten ganancias de +6 a +12 puntos de top-1 es en conjuntos con miles de especies a escala global; no se puede extrapolar sin evaluar a una región pequeña.
- Para una guía estudiantil sirve contrastar tres familias: conteo en celdas (simple, fácil de explicar), kernel/vecinos (escala adaptativa por especie), red neuronal (mejor, pero necesita muchos datos y no es explicable fácilmente).

### Gaps
- No se pudo leer el texto oficial del blog de iNaturalist (403): umbral exacto de "Expected Nearby", cómo maneja estacionalidad, tamaño exacto de las celdas, número de observaciones mínimo. [SIN FUENTE] verificada.
- No se encontró documentación técnica de Merlin sobre cómo se combina la frecuencia con la salida visual.
- No se encontró un estudio que compare directamente priors para endémicas vs. amplias dentro del mismo modelo (ganancia por rareza de especie).
- No se extrajo el texto de Berg 2014 (403): detalle de ancho de banda adaptativo y ganancia exacta.

## 2. Diseño dinámico del prior (ancho de banda por especie, suavizado, límites, sesgos, recálculo, fenología)

### Takeaway
Las fuentes respaldan: prior desacoplado del clasificador, mezcla con prior uniforme para robustez, codificación periódica del día del año, y conciencia del sesgo del observador. Los mecanismos concretos de ancho de banda por especie, encogimiento empírico-Bayes y multiplicador acotado son diseño propio, no extraídos de las fuentes consultadas.

### Cited Findings
- Añadir un prior uniforme a los métodos basados en vecinos mejora su rendimiento porque aporta robustez cuando no hay observaciones del conjunto de entrenamiento cerca del punto de prueba — [Mac Aodha 2019](https://arxiv.org/abs/1906.05272)
- Berg et al. usan un estimador de densidad por kernel adaptativo por especie sobre cubos espacio-temporales — descrito en [Mac Aodha 2019](https://arxiv.org/abs/1906.05272)
- Codificación del día del año con sin/cos (envolvente) para continuidad entre fin y comienzo de año; en la ablación, quitar la envolvente baja top-1 de iNat2018 de 72.68 a 72.12 (y quitar la fecha a 72.41, el fotógrafo a 72.84 — este último es mayor que el completo, así que el término de fotógrafo no ayuda siempre) — [Mac Aodha 2019, Tabla 2](https://arxiv.org/abs/1906.05272)
- Sesgo del observador: la pérdida del fotógrafo usa el hecho de que un "no reporte" de un fotógrafo que nunca fotografió algo similar aporta poca información sobre ausencia — [Mac Aodha 2019](https://arxiv.org/abs/1906.05272)
- Sesgo geográfico de fotógrafos: los embeddings muestran gran sesgo hacia Norteamérica, Europa y Nueva Zelanda — [Mac Aodha 2019, Fig. 3](https://arxiv.org/abs/1906.05272)
- Limitar ejemplos por especie (tope) reduce el desbalance; para SINR el beneficio de reducir desbalance compensa la pérdida de datos — [Cole 2023](https://arxiv.org/abs/2306.02564)
- Más datos por especie mejora de forma confiable el rendimiento de SINR (Fig. 5) y aporta detalle espacial fino — [Cole 2023](https://arxiv.org/abs/2306.02564)
- Los embeddings de ubicación aprendidos capturan zonas climáticas sin datos climáticos — [Mac Aodha 2019, Fig. 3](https://arxiv.org/abs/1906.05272); coordenadas ≈ 93–97 % de lo que logran variables ambientales — [Cole 2023](https://arxiv.org/abs/2306.02564)
- Un nuevo conjunto de datos no obliga a reentrenar el clasificador: el prior se entrena independiente de él — [Mac Aodha 2019](https://arxiv.org/abs/1906.05272). iNaturalist reentrena modelo de visión y geomodel con la misma programación mensual — [resumen búsqueda blog 84677](https://www.inaturalist.org/posts/84677)
- Altitud: el geomodel de iNaturalist usó elevación como única covariable ambiental; críticas de que es proxy débil — ver sección 1 (fuentes de foro/comentarios, no oficiales verificadas)

### Inferences
Propuesta de diseño [diseño propio, SIN FUENTE para los parámetros; las fuentes respaldan solo la idea general]:
- Ancho de banda por especie: calcular la dispersión observada (por ejemplo mediana de distancias al centroide o distancia al k-ésimo vecino) y usar kernel cuyo radio crece con esa dispersión; para especies con pocos puntos, usar piso mínimo de radio (para evitar prior de un solo punto) y dejar que el kernel se ensanche. Es la idea del kernel adaptativo de Berg, pero con parámetros a calibrar [SIN FUENTE sobre valores].
- Encogimiento: P_suav(y|x) = (n_cerca + α·u)/(n_total + α), con u uniforme y α pequeño; con pocas observaciones la prior se acerca a uniforme (Laplace/aditivo; empirical Bayes elegiría α a partir de la dispersión entre especies) [SIN FUENTE: parámetros].
- Multiplicador acotado: prior_final = clip(prior_suav / prior_uniforme, m_min, m_max) con m_min > 0, de modo que ninguna especie sea eliminada (apoya el hallazgo de que la mezcla uniforme da robustez).
- Si la especie es amplia o la observación vieja o imprecisa: ensanchar kernel o reducir peso w; las fuentes dicen que la ubicación puede ser inexacta u ofuscada (Mac Aodha) pero no dan fórmula [SIN FUENTE].
- Sesgo de observación (carreteras, ciudades): la literatura aquí consultada lo modela con embeddings de fotógrafo; alternativas (pesos por esfuerzo, thinning espacial) no se verificaron con fuente en esta ronda [SIN FUENTE].
- Recalcular al llegar datos nuevos: el prior es barato de reentrenar o recalcular sin tocar el clasificador (se apoya en Mac Aodha); la frecuencia concreta es decisión propia.
- Fenología: usar día del año con codificación periódica; la ganancia de la fecha en las ablaciones es pequeña frente a la ubicación (iNat2018: 72.41 sin fecha vs. 72.68 con fecha), así que no se debe esperar mucho de fecha en datos globales — para un sitio con estación marcada puede ser distinto [SIN FUENTE].

### Gaps
- No se encontraron fuentes sobre empirical Bayes aplicado a priors geográficos de especies, ni sobre ponderación por antigüedad/precisión de coordenadas.
- No se encontraron en esta ronda métodos verificados de corrección de sesgo de carreteras/ciudades (solo el modelo de fotógrafo de Mac Aodha y la mención a Johnston et al. 2020 en la bibliografía de Cole, que no se leyó).
- Altitud y clima: sin fuente oficial sobre cuánto aportan más allá de coordenadas, salvo el resultado de SINR (coordenadas ~93–97 % de coordenadas+ambiente).

## 3. Riesgos: sobreescritura, cambios de rango, ausencia ≠ no observado, privacidad

### Takeaway
La pérdida "asumir ausente" hace al prior intencionalmente agresivo (útil para filtrar, peligroso para registros nuevos o fuera de rango). Los autores mismos lo señalan como suposición muy fuerte. Los riesgos de invasoras y privacidad no están respaldados con fuentes en esta ronda.

### Cited Findings
- Mac Aodha 2019: la pérdida es "conservadora" y asume ausencia donde no se observó, "una suposición muy fuerte" que permite bajar agresivamente predicciones incorrectas del clasificador — [Mac Aodha 2019](https://arxiv.org/abs/1906.05272)
- Presencia-ausencia requiere esfuerzo intenso de muestreo para confirmar ausencia con certeza; los datos solo-presencia no la ofrecen — [Mac Aodha 2019](https://arxiv.org/abs/1906.05272)
- Cole 2023: los pseudo-negativos pueden ser incorrectos; los modelos no están calibrados ni validados para conservación; fallan en zonas poco muestreadas (LAN-SSDL) — [Cole 2023](https://arxiv.org/abs/2306.02564)
- Mapas de rango: omisión y comisión; el 85 % de los desacuerdos solo-IUCN cerca de bordes (<200 km) — ver sección 1
- iNaturalist: si ningún taxón visualmente similar está esperado cerca, se muestran igual los visualmente similares: es una salida de seguridad para que el prior no deje sin respuesta al usuario — [Ayuda iNaturalist](https://help.inaturalist.org/en/support/solutions/articles/151000170371-what-does-expected-nearby-mean-)
- Usuarios critican que la etiqueta solo comunica "esperado" y no "no esperado" — [resumen de búsqueda de foro](https://forum.inaturalist.org/t/cv-suggesting-out-of-range-species/79857) [opinión de usuarios]
- Un comentario del blog advierte que un umbral algo alto puede hacer que una especie desaparezca de celdas donde ocurre — [comentario citado en búsqueda](https://www.inaturalist.org/blog/84677-introducing-the-inaturalist-geomodel)
- Ubicaciones inexactas u ofuscadas degradan el prior — [Mac Aodha 2019, sec. 4.5](https://arxiv.org/abs/1906.05272)

### Inferences
- Para el proyecto: el prior debe ser un multiplicador acotado y nunca un filtro duro; ante la duda, mostrar la lista visual sin prior (mismo principio que iNaturalist).
- "No observado" no es "ausente": las fuentes lo dicen explícitamente al describir la naturaleza solo-presencia de los datos; las especies sub-muestreadas (regiones poco visitadas) quedarán subestimadas.
- Invasoras y cambio climático (Rhinella marina, Frankliniella): ninguna fuente de esta ronda cubre rangos cambiantes ni invasoras; sí se sigue que un prior estático entrenado con datos pasados penalizará a una especie que expande su rango. [SIN FUENTE] para magnitudes o ejemplos concretos.
- Privacidad en especies amenazadas: Mac Aodha cita ubicaciones "intencionalmente ofuscadas" como limitación; reglas de ofuscación (celdas, GBIF/iNat) no se verificaron aquí. [SIN FUENTE]

### Gaps
- Sin fuente sobre efecto del cambio climático ni invasoras en priors geográficos, ni sobre Rhinella marina o Frankliniella.
- Sin fuente sobre políticas de obfuscación de coordenadas de iNaturalist/GBIF (no se consultaron).
- Sin cifras de cuántas veces el prior "mata" una identificación correcta.

## 4. Contexto más allá de la geografía y fusión

### Takeaway
La fusión estándar documentada es la bayesiana de Mac Aodha: P(y|I,x) ∝ P(y|I)·P(y|x), con independencia condicional. La versión con exponente w, el peso por perfil de especie y la calibración son extensiones razonables pero sin fuente aquí.

### Cited Findings
- Fórmula de fusión y supuestos (independencia condicional de I y x dado y, P(y) uniforme) — [Mac Aodha 2019, ecs. 1–3](https://arxiv.org/abs/1906.05272)
- Mac Aodha menciona que variables ambientales adicionales pueden ser una señal valiosa para algunas categorías, aunque su modelo no las usa — [Mac Aodha 2019, sec. 4.5](https://arxiv.org/abs/1906.05272)
- Trabajo previo (Tang et al.) integra rasgos de ubicación dentro del clasificador (coordenadas, censo, hashtags, mapas de uso de suelo), pero necesita esa información en prueba y reentrenar el modelo si hay datos nuevos — [Mac Aodha 2019, trabajos relacionados](https://arxiv.org/abs/1906.05272)
- En SINR las coordenadas y las variables ambientales son complementarias — [Cole 2023](https://arxiv.org/abs/2306.02564)
- Merlin usa ubicación y fecha como contexto — ver sección 1
- Una limitación notable de la independencia condicional: "en realidad una imagen puede contener información de ubicación no relacionada con la clase (p. ej. el fondo)" — [Mac Aodha 2019](https://arxiv.org/abs/1906.05272)

### Inferences
- Generalización directa: para planta hospedera, cultivo, hora del día o vector de plaga se puede añadir P(y|contexto) como factor extra, con exponentes w_k por contexto: P ∝ P(y|I)·∏ P(y|c_k)^w_k. Aquí w=1 reproduce Bayes ingenuo; w<1 amortigua cuando los factores están correlacionados. [SIN FUENTE: propuesta propia; hay que calibrar w en validación].
- Como las señales de contexto suelen correlacionarse (cultivo y región, hospedera y estación), la hipótesis de independencia condicional se rompe y conviene w<1 o aprender los pesos — consecuencia lógica de la limitación citada por Mac Aodha, sin cifras.
- Calibración previa de las probabilidades del clasificador antes de multiplicar [SIN FUENTE: práctica común, no verificada aquí].
- Peso aprendido por perfil de especie (p. ej. mayor w para endémicas bien muestreadas, menor para amplias): [SIN FUENTE], hipótesis a probar.

### Gaps
- Ninguna fuente consultada trata hospedera, cultivo, hora del día o vectores de enfermedad como prior.
- Sin fuente sobre fusión con exponente w ni sobre aprendizaje de pesos por especie.

## 5. Evaluación de un prior

### Takeaway
Las fuentes dan un protocolo de evaluación claro: medir el cambio en top-1/top-3/top-5 con y sin prior, con conjuntos de prueba separados temporalmente. Las pruebas de aislamiento por distancia y trampas de contaminación del oráculo son propuestas propias.

### Cited Findings
- Métrica "Geo Prior": cambio en top-1 del clasificador al aplicar el prior en prueba; el clasificador no se entrena con información geográfica — [Cole 2023](https://arxiv.org/abs/2306.02564)
- Separación temporal para evitar solapamiento: conjunto de prueba con observaciones research grade de ene–may 2022, entrenamiento anterior; Mac Aodha usó eBird 2015 para entrenar y 2016 para probar — [Cole 2023](https://arxiv.org/abs/2306.02564); [Mac Aodha 2019](https://arxiv.org/abs/1906.05272)
- Ablaciones: sin fecha, sin envolvente, sin fotógrafo, reportando top-1/top-3/top-5 — [Mac Aodha 2019, Tabla 2](https://arxiv.org/abs/1906.05272)
- La mejora del prior se mantiene con un clasificador más potente (iNat2018 520×520: de 66.18 a 77.49 top-1), es decir, es en parte ortogonal a mejoras visuales — [Mac Aodha 2019](https://arxiv.org/abs/1906.05272)
- Cole 2023 recomienda varias evaluaciones complementarias (S&T, IUCN, Geo Prior, Geo Feature) porque cada una tiene puntos ciegos; la correlación entre tareas es alta pero no perfecta (por ejemplo IUCN vs. S&T 0.62 en una matriz de correlación citada) — [Cole 2023, Fig. 6](https://arxiv.org/abs/2306.02564)
- La evaluación de SDM solo-presencia es notoriamente difícil (Beery et al. 2021, citado) — [Cole 2023, apéndice](https://arxiv.org/abs/2306.02564)
- Variación entre corridas: típicamente <0.5 MAP, siempre <1.0 MAP en cinco corridas — [Cole 2023, Fig. A1](https://arxiv.org/abs/2306.02564)

### Inferences
- Ablación por distancia (sitios aislados): repartir la prueba por distancia al punto de entrenamiento más cercano y reportar top-1/top-3 por tramo. SINR admite que los modelos espacialmente explícitos pueden no generalizar a lugares lejanos de los datos de entrenamiento [mencionado en el apéndice de Cole; verificar redacción exacta]; por eso este análisis revela dónde el prior daña.
- Trampa de contaminación del oráculo: no usar observaciones de prueba (ni sus vecinas casi duplicadas) para construir el prior; basta separar por fecha como hacen Cole y Mac Aodha, y por observador o sitio cuando se pueda. Es una práctica inferida, sin fuente específica de "trampas".
- Reportar siempre por clase (endémicas vs. amplias) además de la media global, porque la media oculta el efecto en especies raras.

### Gaps
- No se encontraron protocolos publicados específicos de "trampa de contaminación del oráculo" ni de evaluación por distancia a sitios aislados, más allá de las divisiones temporales descritas.
- No se localizaron cifras por clase (endémicas vs. amplias) en los artículos.
