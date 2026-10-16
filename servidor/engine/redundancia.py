# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Regla anti-redundancia: el mismo texto (o casi) no se repite en titulares y etiquetas de una misma hoja.
README de ANURA: «un dato aparece una sola vez por hoja». Repetir el título en la cabecera, el titular, el pie de figura y el aviso es ruido visual.

Dos usos: `similar(a, b)` (servidor, para decidir qué se omite) y la misma lógica en audit.js (informe de lo que quedó repetido).
"""
import re
import unicodedata

STOP = {"para", "como", "esta", "este", "esos", "esas", "entre", "sobre", "desde", "hasta", "donde", "cuando", "los", "las", "una", "uno", "del", "con", "por", "que", "sus", "son"}


def stems(s: str) -> set:
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return {w[:6] for w in re.findall(r"[a-z0-9]+", s) if len(w) >= 4 and w not in STOP and not w.isdigit()}


def similar(a: str, b: str, laxo: bool = False) -> bool:
    """Misma idea: comparten ≥ 75 % de las raíces del texto más corto. Por defecto exige ≥ 2 raíces compartidas (o conjuntos iguales),
    para no tomar por repetición un subtítulo de una palabra («Fauna» dentro de «Enfermedad en fauna y flora»). `laxo=True` acepta 1 raíz."""
    sa, sb = stems(a), stems(b)
    if not sa or not sb:
        return False
    shared = len(sa & sb)
    if shared == 0 or shared / min(len(sa), len(sb)) < 0.75:
        return False
    return laxo or shared >= 2 or sa == sb
