# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Maquetación de flujo con paginación automática.

Estrategia (decisión de la auditoría #1 del Prompt Maestro: ANURA usa posiciones fijas, un PDF de tema libre necesita flujo):
1. Cada bloque se convierte en una "unidad" (HTML). Tablas y listas se parten por filas/ítems.
2. Chromium mide la altura real de cada unidad al ancho exacto de la hoja (en cqw).
3. Un empaquetador voraz llena hojas de altura fija, respetando 'mantener con el siguiente' en subtítulos.
El agente nunca calcula posiciones; si un bloque no cabe solo en una hoja, el informe lo dice (bloque, cuánto sobra).
"""
import json

MEASURE_JS = r"""
() => {
  const pg = document.querySelector('.page.measure');
  const scale = pg.clientWidth / 100;           // 1cqw en px
  const out = [];
  document.querySelectorAll('.cont > .u').forEach(u => {
    const r = {i: +u.dataset.u, h: u.getBoundingClientRect().height / scale, parts: null};
    const tb = u.querySelector('table.tab');
    if (tb && u.dataset.split === 'table') {
      const th = tb.querySelector('thead');
      r.head = th ? th.getBoundingClientRect().height / scale : 0;
      r.rows = [...tb.querySelectorAll('tbody tr')].map(t => t.getBoundingClientRect().height / scale);
      r.total = u.getBoundingClientRect().height / scale;
    }
    const ul = u.querySelector('ul.bl');
    if (ul && u.dataset.split === 'list') {
      r.rows = [...ul.querySelectorAll('li')].map(t => t.getBoundingClientRect().height / scale);
      r.total = u.getBoundingClientRect().height / scale;
    }
    out.push(r);
  });
  return out;
}
"""


def measure_html(shell: str, units: list) -> str:
    body = "".join(
        f'<div class="u" data-u="{i}" data-split="{u.get("split","")}">{u["html"]}</div>' for i, u in enumerate(units)
    )
    return shell.replace("%%MEASURE%%", f'<article class="page lp measure"><div class="cont" style="position:static">{body}</div></article>')


def measure(page, shell: str, units: list) -> list:
    page.set_content(measure_html(shell, units), wait_until="load")
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(150)
    return page.evaluate(MEASURE_JS)


def pack(units: list, meas: list, capacity: float, gap: float, render_part, warn: list) -> list:
    """Devuelve páginas: lista de listas de HTML. render_part(unit, r0, r1) -> html de un fragmento de tabla/lista."""
    pages, cur, used = [], [], 0.0

    def flush():
        nonlocal cur, used
        if cur:
            pages.append(cur)
        cur, used = [], 0.0

    def add(html, h, keep=False):
        nonlocal used
        need = h + (gap if cur else 0)
        cur.append((html, h, keep))
        used += need

    def fits(h):
        return used + h + (gap if cur else 0) <= capacity + 0.01

    n = len(units)
    for i, (u, m) in enumerate(zip(units, meas)):
        h = m["h"]
        keep = u.get("keep_next", False)
        if u.get("split") and m.get("rows") and h > capacity - (used + (gap if cur else 0)):
            # parte la tabla o lista por filas
            rows, head = m["rows"], m.get("head", 0.0)
            chrome = m["total"] - head - sum(rows)       # bordes, caption
            r0 = 0
            while r0 < len(rows):
                room = capacity - used - (gap if cur else 0)
                acc, r1 = head + max(chrome, 0) * 0, r0
                while r1 < len(rows) and acc + rows[r1] + (chrome if r1 + 1 == len(rows) else 0) <= room + 0.01:
                    acc += rows[r1]
                    r1 += 1
                if r1 == r0:
                    if cur:
                        flush()
                        continue
                    r1 = r0 + 1
                    warn.append({"bloque": u.get("label", "?"), "causa": f"una fila mide {rows[r0]:.1f}cqw y no cabe en una hoja", "ajuste": "acorta el texto de la fila"})
                frag_h = head + sum(rows[r0:r1]) + (chrome if r1 == len(rows) else 0)
                add(render_part(u, r0, r1), frag_h)
                r0 = r1
                if r0 < len(rows):
                    flush()
            continue
        if h > capacity + 0.01 and not u.get("split"):
            # bloque más alto que una hoja y sin partes: se reduce a la medida (nunca se desborda) y se avisa
            z = (capacity - 0.5) / h
            warn.append({"bloque": u.get("label", "?"), "causa": f"mide {h:.1f}cqw y la hoja admite {capacity:.1f}", "ajuste": f"se redujo al {z*100:.0f} %; parte el bloque o acorta el contenido"})
            u = {**u, "html": f'<div style="zoom:{z:.3f}">{u["html"]}</div>'}
            h = capacity - 0.5
        need = h
        if keep and i + 1 < n:
            nm = meas[i + 1]
            nxt = (nm.get("head", 0) + nm["rows"][0]) if units[i + 1].get("split") and nm.get("rows") else nm["h"]
            need = h + gap + min(nxt, capacity - h - gap)
        if not fits(need):
            if h > capacity + 0.01 and not cur:
                warn.append({"bloque": u.get("label", "?"), "causa": f"mide {h:.1f}cqw y la hoja admite {capacity:.1f}", "ajuste": f"sobran {h-capacity:.1f}cqw: parte el bloque o acorta el texto"})
            else:
                flush()
        add(u["html"], h, keep)
    flush()
    return [[c[0] for c in pg] for pg in pages]
