# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Átomos gráficos aprendidos del cartel de referencia (descomponer.py): franja de peligro, código de barras, marca de cruz, X en caja.
Todo vectorial y con currentColor, para que cambie con la paleta."""
import hashlib


def barcode(seed: str, bars: int = 46) -> str:
    h = hashlib.sha256(seed.encode()).digest()
    x, out = 0.0, []
    for i in range(bars):
        w = 0.8 + (h[i % 32] >> (i % 5)) % 3 * 0.9
        if i % 2 == 0:
            out.append(f'<rect x="{x:.1f}" y="0" width="{w:.1f}" height="30"/>')
        x += w + 0.7
    return f'<svg class="atm-code" viewBox="0 0 {x:.0f} 30" preserveAspectRatio="none" aria-hidden="true" style="fill:currentColor">{"".join(out)}</svg>'


def hazard() -> str:
    return ('<svg class="atm-hazard" viewBox="0 0 40 12" preserveAspectRatio="none" aria-hidden="true">'
            '<defs><pattern id="hz" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><rect width="4" height="8" style="fill:currentColor"/></pattern></defs>'
            '<rect width="40" height="12" style="fill:url(#hz)"/></svg>')


def cross() -> str:
    return '<svg class="atm-cross" viewBox="0 0 10 10" aria-hidden="true"><path d="M5 0V10M0 5H10" style="stroke:currentColor;stroke-width:1;fill:none"/></svg>'


def xbox() -> str:
    return ('<svg class="atm-xbox" viewBox="0 0 10 10" aria-hidden="true"><rect x=".6" y=".6" width="8.8" height="8.8" style="fill:none;stroke:currentColor;stroke-width:.8"/>'
            '<path d="M2.5 2.5L7.5 7.5M7.5 2.5L2.5 7.5" style="stroke:currentColor;stroke-width:1.1"/></svg>')


def big_x() -> str:
    return '<svg class="atm-bigx" viewBox="0 0 10 10" aria-hidden="true"><path d="M1 1L9 9M9 1L1 9" style="stroke:currentColor;stroke-width:1.6;fill:none"/></svg>'
