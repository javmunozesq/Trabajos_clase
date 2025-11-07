/**
 * SumaAPI - Funciones JavaScript Comunes
 * Funciones globales utilizadas en toda la aplicación
 */

// Utilidades generales
const SumaAPI = {
  // Mostrar notificaciones
  showNotification: function(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Animación de entrada
    setTimeout(() => {
      notification.style.opacity = '1';
      notification.style.transform = 'translateY(0)';
    }, 10);
    
    // Remover después de 3 segundos
    setTimeout(() => {
      notification.style.opacity = '0';
      notification.style.transform = 'translateY(-10px)';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  },

  // Validar números
  validateNumber: function(value) {
    return !isNaN(value) && isFinite(value);
  },

  // Formatear números
  formatNumber: function(number, decimals = 2) {
    return parseFloat(number).toFixed(decimals);
  },

  // Copiar texto al portapapeles
  copyToClipboard: function(text, successMessage = 'Texto copiado') {
    return navigator.clipboard.writeText(text).then(() => {
      this.showNotification(successMessage, 'success');
      return true;
    }).catch(() => {
      // Fallback para navegadores sin soporte de clipboard
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      this.showNotification(successMessage, 'success');
      return true;
    });
  }
};

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
  console.log('SumaAPI JavaScript iniciado');
  
  // Agregar efectos hover mejorados
  const buttons = document.querySelectorAll('.btn');
  buttons.forEach(button => {
    button.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-2px)';
    });
    
    button.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0)';
    });
  });
});