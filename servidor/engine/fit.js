// [CLAUDE-CONSTRUCTOR] Ajuste de títulos de una línea: el servidor reduce el tamaño antes de cortar (regla R12 de ANURA).
// Escribe el tamaño en cqw para que valga a cualquier ancho de hoja.
(function () {
  function fit() {
    document.querySelectorAll('[data-fit]').forEach(function (el) {
      el.style.fontSize = '';
      var page = el.closest('.page');
      var scale = page.clientWidth / 100;
      var vertical = el.dataset.fit === 'v';
      var fs = parseFloat(getComputedStyle(el).fontSize) / scale;
      var guard = 120;
      var over = function () { return vertical ? el.scrollHeight > el.clientHeight + 1 : el.scrollWidth > el.clientWidth + 1; };
      while (over() && guard-- > 0 && fs > 3) { fs -= 0.25; el.style.fontSize = fs + 'cqw'; }
    });
  }
  window.__fit = fit;
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit); else window.addEventListener('load', fit);
})();
