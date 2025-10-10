document.addEventListener('DOMContentLoaded', () => {
  const featured = document.getElementById('featured-score');
  if (!featured) return;

  // Animación inicial
  featured.classList.add('pop');
  setTimeout(() => featured.classList.remove('pop'), 1200);

  // Función pública para actualizar el marcador y reactivar la animación
  window.updateFeaturedScore = function(newScore, opts = {}) {
    featured.textContent = newScore;
    if (opts.home) featured.dataset.home = opts.home;
    if (opts.away) featured.dataset.away = opts.away;
    if (opts.status) {
      const statusEl = document.querySelector('.big-match .status');
      if (statusEl) statusEl.textContent = opts.status;
    }
    // Reaplicar animación
    featured.classList.remove('pop');
    // Forzar reflow para reiniciar la animación
    void featured.offsetWidth;
    featured.classList.add('pop');
    setTimeout(() => featured.classList.remove('pop'), 1200);
  };

  // Ejemplo: actualizar automáticamente tras unos segundos (opcional)
  // setTimeout(() => window.updateFeaturedScore('3 - 2', { home: 'Racing Club', away: 'River Plate', status: 'Finalizado' }), 3000);
});