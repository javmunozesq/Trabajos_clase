// js/forValidation.js
// ----------------------------------------------------------------------------
// VERSIÓN “MINI” PARA CLASE: una función por campo
// - Campo 1: Nombre  -> validateName() + wireNameValidation()
// - (Ejemplo) Campo 2: Apellidos -> validateLastName() + wireLastNameValidation()
// Helpers reutilizables: showError() / clearError() para no repetir DOM.
// ----------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
  // ==========================
  // HELPERS DE UI (GENÉRICOS)
  // ==========================

  /**
   * Pinta el campo como inválido (rojo) y crea/actualiza el <p> del error.
   * @param {HTMLInputElement|HTMLTextAreaElement} input
   * @param {string} errorId  id único del <p> que mostrará el mensaje
   * @param {string} message  texto del error
   */
  function showError(input, errorId, message) {
    // Señales para accesibilidad y CSS
    input.setAttribute('aria-invalid', 'true'); // borde rojo
    input.removeAttribute('data-valid'); // si estaba marcado como válido, lo quitamos

    // Contenedor visual donde insertaremos el mensaje
    const control = input.closest('.control') || input.parentElement; 

    // Crear o actualizar el <p class="error-msg" role="alert">
    let p = control.querySelector('#' + errorId);
    if (!p) {
      p = document.createElement('p');
      p.id = errorId;
      p.className = 'error-msg';
      p.setAttribute('role', 'alert');
      control.appendChild(p);

      // Vincular input ↔ mensaje (accesibilidad)
      const describedby = (input.getAttribute('aria-describedby') || '')
        .split(' ')
        .filter(Boolean);
      if (!describedby.includes(errorId)) {
        describedby.push(errorId);
        input.setAttribute('aria-describedby', describedby.join(' '));
      }
    }
    p.textContent = message;
  }

  /**
   * Limpia el estado de error (quita rojo) y marca el campo como válido (azul).
   * @param {HTMLInputElement|HTMLTextAreaElement} input
   * @param {string} errorId
   */
  function clearError(input, errorId) {
    input.removeAttribute('aria-invalid');
    input.setAttribute('data-valid', 'true');

    const control = input.closest('.control') || input.parentElement;
    const p = control.querySelector('#' + errorId);
    if (p) p.remove();

    // Sanea aria-describedby si ya no quedan mensajes asociados
    const rest = (input.getAttribute('aria-describedby') || '')
      .split(' ')
      .filter(id => id && id !== errorId);
    if (rest.length) input.setAttribute('aria-describedby', rest.join(' '));
    else input.removeAttribute('aria-describedby');
  }

  // ===================================
  // CAMPO 1: NOMBRE (mínimo 3 chars)
  // ===================================

  const nameInput = document.getElementById('nombre'); // <input id="nombre" ...>
  const NAME_ERROR_ID = 'error-name';// id único para el <p> del error

  /** Regla sencilla: al menos 3 caracteres (ignora espacios alrededor). */
  function validateName() {
    const value = (nameInput?.value || '').trim(); // Evita error si no existe
    if (value.length < 3) {
      showError(nameInput, NAME_ERROR_ID, 'El nombre debe tener al menos 3 caracteres.'); // Mensaje visible
      return false;
    }
    clearError(nameInput, NAME_ERROR_ID); // Limpia el error si es válido
    return true;
  }

  /** Escuchas para el campo Nombre */
  function wireNameValidation() {
    if (!nameInput) return;

    // Validar al salir del campo
    nameInput.addEventListener('blur', validateName); // 'blur' = pierde foco

    // Mientras escribe: si ya cumple, limpiar el error para feedback inmediato
    nameInput.addEventListener('input', () => {
      if (nameInput.value.trim().length >= 3) {
        clearError(nameInput, NAME_ERROR_ID);
      }
    });

    // (Opcional) Evitar envío si el nombre está mal:
    const form = document.getElementById('form-inscripcion'); // <form id="form-inscripcion" ...>
    form?.addEventListener('submit', (e) => { if (!validateName()) e.preventDefault(); }); // ' ' del form
  }

  wireNameValidation(); // linea única para activar la validación del nombre

  // ==========================================================
  // EJEMPLO (OPCIONAL) CAMPO 2: APELLIDOS (mínimo 3 chars)
  // - Deja este bloque como plantilla para cuando quieras
  //   incorporar la validación del segundo campo.
  // ==========================================================

  // const lastNameInput = document.getElementById('apellidos');
  // const LASTNAME_ERROR_ID = 'error-lastname';
  //
  // function validateLastName() {
  //   const value = (lastNameInput?.value || '').trim();
  //   if (value.length < 3) {
  //     showError(lastNameInput, LASTNAME_ERROR_ID, 'Los apellidos deben tener al menos 3 caracteres.');
  //     return false;
  //   }
  //   clearError(lastNameInput, LASTNAME_ERROR_ID);
  //   return true;
  // }
  //
  // function wireLastNameValidation() {
  //   if (!lastNameInput) return;
  //   lastNameInput.addEventListener('blur', validateLastName);
  //   lastNameInput.addEventListener('input', () => {
  //     if ((lastNameInput.value || '').trim().length >= 3) {
  //       clearError(lastNameInput, LASTNAME_ERROR_ID);
  //     }
  //   });
  //   // const form = document.getElementById('form-inscripcion');
  //   // form?.addEventListener('submit', (e) => { if (!validateLastName()) e.preventDefault(); });
  // }
  //
  // wireLastNameValidation();

  // ----------------------------------------------------------
  // NOTAS PARA EXTENDER (MISMA RECETA PARA CADA CAMPO NUEVO):
  // 1) Captura el input por su id (getElementById).
  // 2) Define un ERROR_ID único.
  // 3) Escribe validateX(): aplica tu regla y usa showError/clearError.
  // 4) Escribe wireXValidation(): engancha blur + input.
  // 5) (Opcional) Bloquea submit si falla: en el 'submit' del form.
  // ----------------------------------------------------------
});
