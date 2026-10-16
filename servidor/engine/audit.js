// [CLAUDE-CONSTRUCTOR] Auditoría de hojas. Parte del JS de auditoría de ANURA (project/auditoria.md del sistema de diseño,
// copiado y adaptado por Claude: se añade el desborde del área de contenido y el contraste de texto por pares de color).
// El agente de contenido no escribe ni ejecuta este código: el servidor lo corre y devuelve solo lo que falla.
() => {
  const out = [];
  const lum = (r, g, b) => { const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); };
  const parse = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(',').map(Number); return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1}; };
  const bgOf = el => { let a = el; while (a) { const c = parse(getComputedStyle(a).backgroundColor); if (c && c.a > .5) return c; a = a.parentElement; } return {r: 248, g: 245, b: 238}; };
  document.querySelectorAll('.page').forEach((pg, pi) => {
    const P = pg.getBoundingClientRect(); const name = pg.getAttribute('aria-label') || ('hoja ' + (pi + 1));
    const items = [];
    const walk = document.createTreeWalker(pg, NodeFilter.SHOW_TEXT);
    let n;
    while (n = walk.nextNode()) {
      if (!n.textContent.trim()) continue;
      const el = n.parentElement; const st = getComputedStyle(el);
      if (st.visibility === 'hidden' || st.display === 'none') continue;
      const rg = document.createRange(); rg.selectNodeContents(n);
      if (el.closest('[transform]')) continue;
      for (const r of rg.getClientRects()) {
        if (r.width < 1 || r.height < 1) continue;
        let y = r.top, h = r.height;
        if (st.writingMode.startsWith('horizontal') && !el.closest('svg')) {
          const c = window.__c || (window.__c = document.createElement('canvas').getContext('2d'));
          c.font = `${st.fontStyle} ${st.fontWeight} ${st.fontSize} ${st.fontFamily}`;
          const m = c.measureText(rg.toString());
          const base = r.top + m.fontBoundingBoxAscent * (r.height / (m.fontBoundingBoxAscent + m.fontBoundingBoxDescent));
          y = base - m.actualBoundingBoxAscent; h = m.actualBoundingBoxAscent + m.actualBoundingBoxDescent;
        }
        items.push({el, t: n.textContent.trim().slice(0, 28), x: r.left, y, w: r.width, h, bleed: !!el.closest('.num,.cv-b2,[data-bleed]')});
      }
    }
    const clip = (el, r) => { let a = el.parentElement; let x0 = r.left, y0 = r.top, x1 = r.right, y1 = r.bottom;
      while (a && a !== pg.parentElement) { if (getComputedStyle(a).overflow !== 'visible') { const q = a.getBoundingClientRect(); x0 = Math.max(x0, q.left); y0 = Math.max(y0, q.top); x1 = Math.min(x1, q.right); y1 = Math.min(y1, q.bottom); } a = a.parentElement; }
      return {x: x0, y: y0, w: Math.max(0, x1 - x0), h: Math.max(0, y1 - y0)}; };
    const imgs = [...pg.querySelectorAll('img')].map(i => clip(i, i.getBoundingClientRect()));
    const syms = [...pg.querySelectorAll('.sym')].map(i => clip(i, i.getBoundingClientRect())).filter(r => r.w > 0);
    const inter = (a, b) => Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x)) * Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y));
    const seen = new Set();
    for (let i = 0; i < items.length; i++) {
      const a = items[i];
      for (let j = i + 1; j < items.length; j++) {
        const b = items[j]; if (a.el === b.el) continue;
        const A = inter(a, b); if (A > 4) { const k = a.t + '|' + b.t; if (!seen.has(k)) { seen.add(k); out.push({hoja: name, tipo: 'texto/texto', a: a.t, b: b.t, area: Math.round(A)}); } }
      }
      for (const im of imgs) { const A = inter(a, im); if (A > 4) out.push({hoja: name, tipo: 'texto/foto', a: a.t, area: Math.round(A)}); }
      for (const sy of syms) { const A = inter(a, sy); if (A > 4) out.push({hoja: name, tipo: 'texto/símbolo', a: a.t, area: Math.round(A)}); }
      if (!a.bleed && (a.x < P.left - 1 || a.y < P.top - 1 || a.x + a.w > P.right + 1 || a.y + a.h > P.bottom + 1)) out.push({hoja: name, tipo: 'fuera de hoja', a: a.t});
    }
    const v = pg.querySelector('.cv-v'); if (v && v.scrollHeight > v.clientHeight + 2) out.push({hoja: name, tipo: 'título vertical no cabe', a: v.scrollHeight + '>' + v.clientHeight});
    pg.querySelectorAll('*').forEach(el => { if (el.closest('.cv-b2,.num,[data-bleed]')) return;
      if (el.textContent.trim() && el.children.length === 0 && el.scrollWidth > el.clientWidth + 2 && getComputedStyle(el).overflow !== 'visible') out.push({hoja: name, tipo: 'texto cortado', a: el.textContent.trim().slice(0, 28)}); });
    // desborde del área de contenido (hoja clara): el contenido no debe invadir el pie
    const cont = pg.querySelector('.cont'), pie = pg.querySelector('.pie');
    if (cont && pie && !pg.classList.contains('measure')) {
      const last = cont.lastElementChild;
      if (last) { const lb = last.getBoundingClientRect(), pb = pie.getBoundingClientRect(); if (lb.bottom > pb.top - 1) out.push({hoja: name, tipo: 'contenido invade el pie', sobra_cqw: +((lb.bottom - pb.top) / (P.width / 100)).toFixed(1)}); }
    }
    // redundancia: el mismo texto (o casi) en dos titulares/etiquetas de la misma hoja
    {
      const STOP = new Set(['para','como','esta','este','esos','esas','entre','sobre','desde','hasta','donde','cuando','los','las','una','uno','del','con','por','que','sus','son']);
      const stems = t => new Set((t.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').match(/[a-z0-9]+/g) || []).filter(w => w.length >= 4 && !STOP.has(w) && !/^\d+$/.test(w)).map(w => w.slice(0, 6)));
      const sel = s => [...pg.querySelectorAll(s)].filter(e => !e.closest('.pie') && e.textContent.trim().length > 3);
      const prim = sel('h3,.ttl,.tope-txt,.cv-tit h2,.cv-v,.cv3-t,.cv2-row,.cv4-row,.cv4-k b');
      const sec = sel('.lead,.ct,.sh,.fh,.bh,.co .lb');
      const seenR = new Set();
      const pares = []; prim.forEach((x, i) => { prim.slice(i + 1).forEach(y => pares.push([x, y])); sec.forEach(y => pares.push([x, y])); });
      for (const [x, y] of pares) {
        if (x.contains(y) || y.contains(x)) continue;
        const A = stems(x.textContent), B = stems(y.textContent); if (!A.size || !B.size) continue;
        let sh = 0; A.forEach(v => { if (B.has(v)) sh++; });
        const igual = sh === A.size && sh === B.size;
        if (sh >= 1 && (sh >= 2 || igual) && sh / Math.min(A.size, B.size) >= 0.75) { const k = x.textContent.trim().slice(0, 24) + '|' + y.textContent.trim().slice(0, 24); if (!seenR.has(k)) { seenR.add(k); out.push({hoja: name, tipo: 'redundancia', a: x.textContent.trim().slice(0, 40), b: y.textContent.trim().slice(0, 40)}); } }
      }
    }
    // contraste de texto (pares de color)
    if (!pg.classList.contains('cover')) {
      const bad = new Set();
      items.forEach(it => {
        const st = getComputedStyle(it.el); const fg = parse(st.color); if (!fg) return;
        if (it.el.closest('svg')) { const sv = it.el.closest('svg'); if (sv) { /* el SVG de gráficos se pinta sobre crema */ } }
        const bg = bgOf(it.el); const L1 = lum(fg.r, fg.g, fg.b) + .05, L2 = lum(bg.r, bg.g, bg.b) + .05;
        const ratio = Math.max(L1, L2) / Math.min(L1, L2);
        const px = parseFloat(st.fontSize) * 794 / P.width; const big = px >= 24 || (px >= 18.66 && +st.fontWeight >= 700);
        if (ratio < (big ? 3 : 4.5) && !it.bleed) { const k = it.t + '|' + ratio.toFixed(1); if (!bad.has(k)) { bad.add(k); out.push({hoja: name, tipo: 'contraste', a: it.t, ratio: +ratio.toFixed(2)}); } }
      });
    }
  });
  return out;
}
