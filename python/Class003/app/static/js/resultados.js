/**
 * SumaAPI - Página de Resultados
 * Funciones específicas para la vista de resultados
 */

// Funciones específicas de la página de resultados
const ResultadosPage = {
  // Copiar el resultado al portapapeles
  copiarResultado: function() {
    let resultado;
    
    // Intentar obtener el resultado de diferentes fuentes
    if (window.pageData && window.pageData.resultado) {
      resultado = window.pageData.resultado;
    } else {
      const resultadoElement = document.querySelector('.result-highlight .value');
      if (resultadoElement) {
        resultado = resultadoElement.textContent.trim();
      }
    }
    
    if (!resultado) {
      SumaAPI.showNotification('Error: No se pudo encontrar el resultado', 'error');
      return;
    }
    
    SumaAPI.copyToClipboard(resultado.toString(), `¡Resultado copiado: ${resultado}!`);
  },

  // Animar las tarjetas al cargar
  animateCards: function() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
      card.style.opacity = '0';
      card.style.transform = 'translateY(20px)';
      
      setTimeout(() => {
        card.style.transition = 'all 0.5s ease';
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
      }, index * 150);
    });
  },

  // Animar los stats
  animateStats: function() {
    const stats = document.querySelectorAll('.stat-card');
    stats.forEach((stat, index) => {
      setTimeout(() => {
        stat.style.transform = 'scale(1.05)';
        setTimeout(() => {
          stat.style.transform = 'scale(1)';
        }, 200);
      }, index * 100);
    });
  },

  // Inicializar la página
  init: function() {
    console.log('Página de resultados iniciada');
    
    // Animar elementos
    setTimeout(() => this.animateCards(), 100);
    setTimeout(() => this.animateStats(), 800);
    
    // Hacer el resultado destacado clicable
    const resultHighlight = document.querySelector('.result-highlight');
    if (resultHighlight) {
      resultHighlight.style.cursor = 'pointer';
      resultHighlight.title = 'Clic para copiar el resultado';
      resultHighlight.addEventListener('click', this.copiarResultado);
    }
  }
};

// Función global para copiar resultado (usada en el HTML)
function copiarResultado() {
  ResultadosPage.copiarResultado();
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
  if (document.querySelector('.result-card')) {
    ResultadosPage.init();
  }
});