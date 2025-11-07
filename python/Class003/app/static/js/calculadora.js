/**
 * SumaAPI - Página Principal
 * Funciones específicas para la calculadora
 */

// Funciones específicas de la página principal
const CalculadoraPage = {
  // Validar formulario en tiempo real
  setupFormValidation: function() {
    const form = document.querySelector('form');
    const inputs = document.querySelectorAll('input[type="number"]');
    const submitButton = document.querySelector('button[type="submit"]');
    
    if (!form || !inputs.length || !submitButton) return;

    inputs.forEach(input => {
      input.addEventListener('input', this.validateInput);
      input.addEventListener('blur', this.validateInput);
    });

    form.addEventListener('submit', this.handleSubmit);
  },

  // Validar un input individual
  validateInput: function(event) {
    const input = event.target;
    const value = input.value.trim();
    
    // Remover clases previas
    input.classList.remove('input-error', 'input-success');
    
    if (value === '') {
      return; // Campo vacío es válido hasta el envío
    }
    
    if (SumaAPI.validateNumber(value)) {
      input.classList.add('input-success');
    } else {
      input.classList.add('input-error');
    }
  },

  // Manejar envío del formulario
  handleSubmit: function(event) {
    const form = event.target;
    const inputs = form.querySelectorAll('input[type="number"]');
    let isValid = true;
    
    inputs.forEach(input => {
      const value = input.value.trim();
      if (value === '' || !SumaAPI.validateNumber(value)) {
        input.classList.add('input-error');
        isValid = false;
      }
    });
    
    if (!isValid) {
      event.preventDefault();
      SumaAPI.showNotification('Por favor, ingresa números válidos', 'error');
      return false;
    }
    
    // Mostrar loading en el botón
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
      submitButton.textContent = '⏳ Calculando...';
      submitButton.disabled = true;
    }
    
    return true;
  },

  // Agregar efectos visuales
  addVisualEffects: function() {
    const inputs = document.querySelectorAll('input[type="number"]');
    
    inputs.forEach(input => {
      input.addEventListener('focus', function() {
        this.parentElement.style.transform = 'translateY(-2px)';
      });
      
      input.addEventListener('blur', function() {
        this.parentElement.style.transform = 'translateY(0)';
      });
    });
  },

  // Inicializar la página
  init: function() {
    console.log('Página de calculadora iniciada');
    
    this.setupFormValidation();
    this.addVisualEffects();
    
    // Focus automático en el primer input
    const firstInput = document.querySelector('input[type="number"]');
    if (firstInput) {
      setTimeout(() => firstInput.focus(), 100);
    }
  }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
  if (document.querySelector('form[action="/calcular"]')) {
    CalculadoraPage.init();
  }
});