// [CLAUDE-CONSTRUCTOR] Protocolo de revisión en grises: corrige solo lo que no se distingue.
// Para cada texto cuyo contraste con su fondo sea < 4,5 (o < 3 si es grande): 1) prueba los roles del diseño y se queda con
// el que cumple y más se parece al original; 2) si ninguno sirve, oscurece (fondo claro) o aclara (fondo oscuro) el color por pasos
// de 5 % hasta cumplir. Devuelve la lista de cambios (texto, de, a, razón). No toca texto dentro de SVG ni letras de contorno.
() => {
  const parse = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(',').map(Number); return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1}; };
  const lum = c => { const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return .2126 * f(c.r) + .7152 * f(c.g) + .0722 * f(c.b); };
  const ratio = (a, b) => { const x = lum(a) + .05, y = lum(b) + .05; return Math.max(x, y) / Math.min(x, y); };
  const bgOf = el => { let a = el; while (a) { const c = parse(getComputedStyle(a).backgroundColor); if (c && c.a > .5) return c; a = a.parentElement; } return {r: 248, g: 245, b: 238}; };
  const css = n => { const v = getComputedStyle(document.documentElement).getPropertyValue('--' + n).trim(); const m = v.match(/#([0-9a-f]{6})/i); return m ? {r: parseInt(m[1].slice(0, 2), 16), g: parseInt(m[1].slice(2, 4), 16), b: parseInt(m[1].slice(4, 6), 16)} : null; };
  const roles = ['negro', 'bosque', 'hoja', 'vivo', 'ocre', 'crema', 'arena'].map(n => ({n, c: css(n)})).filter(x => x.c);
  const hex = c => '#' + [c.r, c.g, c.b].map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
  const dist = (a, b) => Math.hypot(a.r - b.r, a.g - b.g, a.b - b.b);
  const out = [], seen = new WeakSet();
  document.querySelectorAll('.page').forEach(pg => {
    const w = document.createTreeWalker(pg, NodeFilter.SHOW_TEXT); let n;
    while (n = w.nextNode()) {
      if (!n.textContent.trim()) continue;
      const el = n.parentElement; if (seen.has(el) || el.closest('svg')) continue; seen.add(el);
      const st = getComputedStyle(el); const fg = parse(st.color); if (!fg || fg.a < .5) continue;
      if (st.webkitTextFillColor && st.webkitTextFillColor.indexOf('rgba(0, 0, 0, 0)') === 0) continue;
      const bg = bgOf(el); const px = parseFloat(st.fontSize); const big = px >= 24 || (px >= 18.66 && +st.fontWeight >= 700);
      const need = big ? 3 : 4.5; const r0 = ratio(fg, bg); if (r0 >= need) continue;
      let best = null;
      roles.forEach(x => { if (ratio(x.c, bg) >= need) { const d = dist(x.c, fg); if (!best || d < best.d) best = {c: x.c, d, via: 'rol ' + x.n}; } });
      if (!best) { const toDark = lum(bg) > .3; let c = {...fg}; for (let i = 0; i < 40 && ratio(c, bg) < need; i++) { c = toDark ? {r: c.r * .95, g: c.g * .95, b: c.b * .95} : {r: c.r + (255 - c.r) * .05, g: c.g + (255 - c.g) * .05, b: c.b + (255 - c.b) * .05}; } best = {c, via: toDark ? 'oscurecido' : 'aclarado'}; }
      el.style.color = hex(best.c);
      out.push({texto: n.textContent.trim().slice(0, 30), de: hex(fg), a: hex(best.c), via: best.via, ratio_antes: +r0.toFixed(2), ratio_despues: +ratio(best.c, bg).toFixed(2)});
    }
  });
  return out;
}
