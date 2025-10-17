document.addEventListener('DOMContentLoaded', () => {
  const featured = document.getElementById('featured-score');
  const statusEl = document.querySelector('.big-match .status');

  if (!featured) return;

  // Aplica animación de entrada
  animateScore(featured);

  // Función para animar marcador
  function animateScore(el) {
    el.classList.add('pop');
    setTimeout(() => el.classList.remove('pop'), 1200);
  }

  // Función pública para actualizar marcador destacado
  window.updateFeaturedScore = function (newScore, opts = {}) {
    featured.textContent = newScore;

    if (opts.home) featured.dataset.home = opts.home;
    if (opts.away) featured.dataset.away = opts.away;
    if (opts.status && statusEl) statusEl.textContent = opts.status;

    // Reinicia animación
    featured.classList.remove('pop');
    void featured.offsetWidth; // Forzar reflow
    animateScore(featured);
  };

  // Ejemplo de actualización automática (descomenta para probar)
  // setTimeout(() => {
  //   window.updateFeaturedScore('3 - 2', {
  //     home: 'Racing Club',
  //     away: 'River Plate',
  //     status: 'Finalizado'
  //   });
  // }, 3000);
});