# Fuentes verificadas para IA de identificación de especies (PITB Antioquia)

## Método y limitaciones de verificación

### Takeaway
Solo funcionó WebSearch. Todos los hosts académicos fallaron desde esta sesión, así que la verificación es por snippets de buscador (con coincidencia entre varias fuentes), NO por resolución directa del DOI. Los datos marcados NO VERIFICADO deben comprobarse a mano antes de entregar.

### Cited Findings
- WebFetch falló (getaddrinfo ENOTFOUND) en arxiv.org, api.crossref.org, api.semanticscholar.org, openaccess.thecvf.com, proceedings.mlr.press — herramienta: WebFetch (sin fuente web; fallo propio de la sesión).
- curl por el proxy falló (403 en CONNECT) en api.crossref.org, api.openalex.org, export.arxiv.org — herramienta: curl (política de egreso del proxy, no se reintentó ni se rodeó).
- WebSearch (modo standard) funcionó y devolvió páginas de arXiv, CVF, PMLR, NeurIPS, Caltech, PMC, mlanthology como resultados; los datos de abajo vienen de esos resultados.
- Ningún DOI fue resuelto con un GET. «Verificado» aquí = el buscador lo muestra en una fuente bibliográfica indexada (indicada).

### Inferences
- Para APA 7 completo, las listas de autores largas (más de 3) no se pudieron confirmar nombre por nombre; se indican como NO VERIFICADO donde corresponde.

### Gaps
- Comprobar DOIs con doi.org/Crossref desde un PC sin restricciones (Crossref: `https://api.crossref.org/works/<doi>`).

---

## Fuentes solicitadas (6)

### Takeaway
Las seis existen y se confirmaron título, año, venue y páginas por búsqueda; DOI confirmado en cuatro de seis (los dos de PMLR/ICLR usan URL estable).

### Cited Findings

**1. BioCLIP (CVPR 2024)** — Confirmado: título, Stevens como primer autor, CVPR 2024, pp. 19412–19424, Best Student Paper, arXiv 2311.18803, dataset TreeOfLife-10M, mejora de 16–17 % (o 17–20 % según versión del texto) frente a baselines — [CVF Open Access](https://openaccess.thecvf.com/content/CVPR2024/html/Stevens_BioCLIP_A_Vision_Foundation_Model_for_the_Tree_of_Life_CVPR_2024_paper.html); [arXiv](https://arxiv.org/abs/2311.18803); [Imageomics](https://imageomics.osu.edu/news/2024/06/bioclip-team-earns-best-student-paper-award-cvpr-2024)
  - Referencia (autores incompletos, NO VERIFICADO el listado completo): Stevens, S., Wu, J., Thompson, M. J., Campolongo, E. G., Song, C. H., Carlyn, D. E., Dong, L., Dahdul, W. M., Stewart, C., Berger-Wolf, T., Chao, W.-L., & Su, Y. (2024). BioCLIP: A vision foundation model for the Tree of Life. *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 19412–19424. https://openaccess.thecvf.com/content/CVPR2024/html/Stevens_BioCLIP_A_Vision_Foundation_Model_for_the_Tree_of_Life_CVPR_2024_paper.html
  - La lista de 12 autores viene de memoria del modelo, NO de una fuente consultada (una búsqueda dice «Stevens y diez coautores», lo que concuerda con 11-12 según cómo se cuente). DOI IEEE 10.1109/CVPR52733.2024.01834: NO VERIFICADO (la búsqueda no lo mostró en ninguna página); usar la URL CVF.
  - Soporta: modelo de visión-lenguaje base del proyecto; clasificación taxonómica jerárquica.

**2. CLIP (ICML 2021)** — Confirmado: PMLR 139, pp. 8748–8763, 400 M pares imagen-texto, 12 autores (Radford y once coautores), arXiv 2103.00020 — [PMLR](https://proceedings.mlr.press/v139/radford21a.html)
  - Referencia: Radford, A., Kim, J. W., Hallacy, C., Ramesh, A., Goh, G., Agarwal, S., Sastry, G., Askell, A., Mishkin, P., Clark, J., Krueger, G., & Sutskever, I. (2021). Learning transferable visual models from natural language supervision. En M. Meila & T. Zhang (Eds.), *Proceedings of the 38th International Conference on Machine Learning* (PMLR 139, pp. 8748–8763). https://proceedings.mlr.press/v139/radford21a.html
  - Nombres de autores y editores: NO VERIFICADO en esta sesión (solo se confirmó el conteo de 12); contrastar con la página PMLR.
  - Soporta: clasificación zero-shot por texto, base de BioCLIP.

**3. Kumar et al. (ICLR 2022)** — Confirmado: autores Ananya Kumar, Aditi Raghunathan, Robbie Jones, Tengyu Ma, Percy Liang; ICLR 2022 (oral); arXiv 2202.10054; el fine-tuning rinde ~2 % más ID pero ~7 % menos OOD que linear probing; LP-FT lo corrige — [ICLR](https://iclr.cc/virtual/2022/poster/5945); [arXiv](https://arxiv.org/abs/2202.10054v1)
  - Referencia: Kumar, A., Raghunathan, A., Jones, R., Ma, T., & Liang, P. (2022). Fine-tuning can distort pretrained features and underperform out-of-distribution. *International Conference on Learning Representations (ICLR 2022)*. https://arxiv.org/abs/2202.10054
  - Soporta: no afinar a ciegas el modelo; usar linear probing/LP-FT con fotos de usuarios locales. Sin DOI (ICLR no asigna).

**4. Guo et al. (ICML 2017)** — Confirmado: Chuan Guo, Geoff Pleiss, Yu Sun, Kilian Q. Weinberger; PMLR 70:1321–1330; el temperature scaling calibra bien — [PMLR](https://proceedings.mlr.press/v70/guo17a); [arXiv](https://arxiv.org/abs/1706.04599)
  - Referencia: Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. En D. Precup & Y. W. Teh (Eds.), *Proceedings of the 34th International Conference on Machine Learning* (PMLR 70, pp. 1321–1330). https://proceedings.mlr.press/v70/guo17a.html
  - Nombres de editores: NO VERIFICADO (omitirlos si no se comprueban).
  - Soporta: la confianza del modelo debe calibrarse antes de mostrarse como «% de certeza».

**5. Beery, Van Horn y Perona (ECCV 2018)** — Confirmado: pp. 472–489, DOI 10.1007/978-3-030-01270-0_28 (según listado de Caltech Library), LNCS 11133, arXiv 1807.04975 — [arXiv](https://arxiv.org/pdf/1807.04975); [Caltech feed](https://feeds.library.caltech.edu/people/Perona-P/book_section.html)
  - Referencia: Beery, S., Van Horn, G., & Perona, P. (2018). Recognition in terra incognita. En V. Ferrari, M. Hebert, C. Sminchisescu & Y. Weiss (Eds.), *Computer Vision – ECCV 2018* (LNCS vol. 11133, pp. 472–489). Springer. https://doi.org/10.1007/978-3-030-01270-0_28
  - Editores: NO VERIFICADO (de memoria); el DOI proviene de un solo listado (Caltech), no resuelto.
  - Soporta: los modelos fallan en cámaras/lugares nuevos (generalización a otros sitios, p. ej. Antioquia).

**6. Mac Aodha, Cole y Perona (ICCV 2019)** — Confirmado: pp. 9596–9606, DOI 10.1109/ICCV.2019.00969, arXiv 1906.05272 — [CVF](https://openaccess.thecvf.com/content_ICCV_2019/html/Aodha_Presence-Only_Geographical_Priors_for_Fine-Grained_Image_Classification_ICCV_2019_paper.html); [página del proyecto](https://homepages.inf.ed.ac.uk/omacaod/projects/geopriors/index.html)
  - Referencia: Mac Aodha, O., Cole, E., & Perona, P. (2019). Presence-only geographical priors for fine-grained image classification. *Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)*, 9596–9606. https://doi.org/10.1109/ICCV.2019.00969
  - Soporta: usar ubicación y fecha del registro como prior para mejorar la sugerencia de especie.

### Inferences
- Las seis son citables. Los puntos 5 y 6 respaldan el diseño georreferenciado; 3 y 4 respaldan evaluación y confianza.

### Gaps
- DOI de BioCLIP (IEEE) sin confirmar; autores/editores de varias entradas sin confirmar nombre a nombre.

---

## Fuentes adicionales

### Takeaway
Se confirmaron 7 fuentes adicionales (2014–2025). BioCLIP 2 existe y es NeurIPS 2025. SpeciesNet no tiene un artículo con el título supuesto; la referencia correcta es Gadot et al. 2024.

### Cited Findings

**7. BioCLIP 2** — Existe. «BioCLIP 2: Emergent Properties from Scaling Hierarchical Contrastive Learning», arXiv 2505.23883 (enviado 29-may-2025, revisado 23-oct-2025), NeurIPS 2025 (spotlight según Stevens); TreeOfLife-200M (~214 M imágenes); 16 autores — [arXiv](https://arxiv.org/abs/2505.23883); [NeurIPS](https://papers.neurips.cc/paper_files/paper/2025/hash/94da80cbfe870c1db958c88a8a27018c-Abstract-Conference.html); [GitHub](https://github.com/Imageomics/bioclip-2)
  - Referencia: Gu, J., Stevens, S., Campolongo, E. G., Thompson, M. J., Zhang, N., Wu, J., Kopanev, A., Mai, Z., White, A., Balhoff, J., Dahdul, W., Rubenstein, D., Lapp, H., Berger-Wolf, T., Chao, W.-L., & Su, Y. (2025). BioCLIP 2: Emergent properties from scaling hierarchical contrastive learning. *Advances in Neural Information Processing Systems (NeurIPS 2025)*. https://arxiv.org/abs/2505.23883
  - Autores tomados de la entrada BibTeX del repositorio oficial. Volumen (38) y páginas: NO VERIFICADO. Soporta: sucesor de BioCLIP, mejor rendimiento.

**8. iNaturalist 2018 dataset** — Van Horn et al., CVPR 2018, pp. 8769–8778, DOI 10.1109/CVPR.2018.00914 (de mlanthology), arXiv 1707.06642 — [CVF](https://openaccess.thecvf.com/content_cvpr_2018/html/Van_Horn_The_INaturalist_Species_CVPR_2018_paper.html); [mlanthology](https://mlanthology.org/cvpr/2018/horn2018cvpr-inaturalist/)
  - Referencia: Van Horn, G., Mac Aodha, O., Song, Y., Cui, Y., Sun, C., Shepard, A., Adam, H., Perona, P., & Belongie, S. (2018). The iNaturalist species classification and detection dataset. *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 8769–8778. https://doi.org/10.1109/CVPR.2018.00914
  - Lista de autores: NO VERIFICADO (de memoria). Soporta: ciencia ciudadana con datos de calidad variable, cola larga de especies.

**9. Norouzzadeh et al. 2018 (PNAS)** — DOI 10.1073/pnas.1719367115, PNAS 115(25): E5716–E5725, 5-jun-2018; 48 especies de Snapshot Serengeti, 93,8 % de exactitud; 99,3 % de automatización con 96,6 % de exactitud — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6016780); [arXiv](https://arxiv.org/pdf/1703.05830)
  - Referencia: Norouzzadeh, M. S., Nguyen, A., Kosmala, M., Swanson, A., Palmer, M. S., Packer, C., & Clune, J. (2018). Automatically identifying, counting, and describing wild animals in camera-trap images with deep learning. *Proceedings of the National Academy of Sciences, 115*(25), E5716–E5725. https://doi.org/10.1073/pnas.1719367115
  - Soporta: IA reduce trabajo de etiquetado manual si se filtra por confianza.

**10. Tabak et al. 2019 (MLWIC)** — Confirmado título, primer autor, preprint bioRxiv DOI 10.1101/346809; 3.367.383 imágenes, 98 % de exactitud en EE. UU., 82 % en Canadá, 94 % de detección de animales en Tanzania — [bioRxiv](https://www.biorxiv.org/content/10.1101/346809v3.full.pdf)
  - Referencia (versión publicada, DOI NO VERIFICADO): Tabak, M. A., et al. (2019). Machine learning to classify animal species in camera trap images: Applications in ecology. *Methods in Ecology and Evolution, 10*(4), 585–590. DOI 10.1111/2041-210X.13120 (DOI, volumen y páginas provienen de la memoria del modelo; dos búsquedas no lo confirmaron). Alternativa verificada: preprint https://doi.org/10.1101/346809.
  - Soporta: caída de exactitud en datos externos (82 % Canadá), argumento para validar localmente.

**11. SpeciesNet (Google)** — Repositorio oficial: ensamble MegaDetector + clasificador EfficientNetV2-M, >2000 etiquetas, 65 M de imágenes de entrenamiento; usado en Wildlife Insights. Artículo de referencia del README: Gadot et al. 2024, *IET Computer Vision* 18(8), 1193–1208, DOI 10.1049/cvi2.12318 — [GitHub](https://github.com/google/cameratrapai); [Google blog](https://blog.google/company-news/outreach-and-initiatives/sustainability/speciesnet-open-source-ai-wildlife/)
  - Referencia: Gadot, T., Istrate, Ș., Kim, H., Morris, D., Beery, S., Birch, T., & Ahumada, J. (2024). To crop or not to crop: Comparing whole-image and cropped classification on a large dataset of camera trap images. *IET Computer Vision, 18*(8), 1193–1208. https://doi.org/10.1049/cvi2.12318
  - El título «Towards a global camera trap species classifier» (Ecological Informatics) NO se encontró; no usarlo. Soporta: cámaras trampa a escala con IA abierta.

**12. Pl@ntNet (Lefort et al. 2025)** — «Cooperative learning of Pl@ntNet's Artificial Intelligence algorithm: How does it work and how can we improve it?», *Methods in Ecology and Evolution* 2025, DOI 10.1111/2041-210X.14486 (listado Pensoft/CIRAD), arXiv 2406.03356; autores: Lefort, Affouard, Charlier, Lombardo, Chouet, Goëau, Salmon, Bonnet, Joly — [arXiv](https://arxiv.org/pdf/2406.03356); [CIRAD](https://agritrop.cirad.fr/580680)
  - Referencia: Lefort, T., Affouard, A., Charlier, B., Lombardo, J.-C., Chouet, M., Goëau, H., Salmon, J., Bonnet, P., & Joly, A. (2025). Cooperative learning of Pl@ntNet's artificial intelligence algorithm: How does it work and how can we improve it? *Methods in Ecology and Evolution*. https://doi.org/10.1111/2041-210X.14486 (volumen/páginas: NO VERIFICADO).
  - Soporta: validación por la comunidad como mejora del identificador.

**13. Pl@ntNet (Joly et al. 2014)** — *Ecological Informatics* 23, 22–34, «Interactive plant identification based on social image data»; autores Joly, Goëau, Bonnet, Bakic, Barbe, Selmi, Yahiaoui, Carré, Mouysset, Molino, Boujemaa, Barthélémy; fotos georreferenciadas de ciencia ciudadana — [CIRAD](https://agritrop.cirad.fr/574241); [IRD](https://www.documentation.ird.fr/hor/fdi:010062489)
  - Referencia: Joly, A., Goëau, H., Bonnet, P., Bakić, V., Barbe, J., Selmi, S., Yahiaoui, I., Carré, J., Mouysset, E., Molino, J.-F., Boujemaa, N., & Barthélémy, D. (2014). Interactive plant identification based on social image data. *Ecological Informatics, 23*, 22–34. DOI 10.1016/j.ecoinf.2013.07.006: NO VERIFICADO (la búsqueda no lo mostró).
  - Soporta: precedente de plataforma web/móvil con fotos georreferenciadas.

### Inferences
- Para cámaras trampa (9, 10, 11) hay literatura sólida; para BioCLIP aplicado a fotos de ciudadanos en Colombia no se encontró estudio específico.

### Gaps
- No se encontró artículo evaluado por pares sobre rendimiento de BioCLIP en fauna/flora de Colombia o Antioquia.
- DOIs sin confirmar: BioCLIP IEEE, Tabak 2019 (journal), Joly 2014. Volúmenes/páginas de BioCLIP 2 y Lefort 2025 sin confirmar.
- Joly et al. «Pl@ntNet app in the era of deep learning» (ICLR 2017 workshop) apareció solo mencionado, sin verificar.
