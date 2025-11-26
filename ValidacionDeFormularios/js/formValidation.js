// ========================
// Helpers DOM y accesibilidad
// ========================
function $(selector, root = document) {
  return root.querySelector(selector);
}
function $all(selector, root = document) {
  return Array.from(root.querySelectorAll(selector));
}
function getControl(input) {
  return input.closest('.control') || input.parentElement;
}
function ensureErrorNode(input) {
  const control = getControl(input);
  let msg = control.querySelector('.error-msg');
  if (!msg) {
    msg = document.createElement('p');
    msg.className = 'error-msg';
    msg.setAttribute('role', 'alert');
    msg.setAttribute('aria-live', 'polite');
    control.appendChild(msg);
  }
  const msgId = `error-${input.id || input.name}`;
  msg.id = msgId;

  const describedBy = (input.getAttribute('aria-describedby') || '').trim();
  const ids = new Set(describedBy ? describedBy.split(/\s+/) : []);
  ids.add(msgId);
  input.setAttribute('aria-describedby', Array.from(ids).join(' '));

  return msg;
}
function showError(input, message) {
  const msg = ensureErrorNode(input);
  msg.textContent = message || '';
  input.setAttribute('aria-invalid', 'true');
  const control = getControl(input);
  control?.classList.add('is-invalid');
  control?.classList.remove('is-valid');
}
function clearError(input) {
  const control = getControl(input);
  const msg = control?.querySelector('.error-msg');
  if (msg) msg.textContent = '';
  input.removeAttribute('aria-invalid');
  control?.classList.remove('is-invalid');
  control?.classList.add('is-valid');
}
function disableSubmit(btn) {
  btn.disabled = true;
  btn.setAttribute('aria-disabled', 'true');
}
function enableSubmit(btn) {
  btn.disabled = false;
  btn.setAttribute('aria-disabled', 'false');
}
function focusFirstInvalid(form) {
  const firstInvalid = form.querySelector('[aria-invalid="true"], :invalid');
  if (firstInvalid) firstInvalid.focus();
}

// ========================
// Mensajes por campo
// ========================
const messages = {
  nombre: {
    required: 'El nombre es obligatorio.',
    minlength: 'Debe tener al menos 2 caracteres.',
    custom: 'Nombre inválido.',
  },
  apellidos: {
    required: 'Los apellidos son obligatorios.',
    minlength: 'Debe tener al menos 2 caracteres.',
    custom: 'Apellidos inválidos.',
  },
  email: {
    required: 'El correo es obligatorio.',
    typeMismatch: 'Formato de correo no válido.',
    custom: 'Correo inválido.',
  },
  telefono: {
    required: 'El teléfono es obligatorio.',
    patternMismatch: '9–20 caracteres; solo dígitos, espacio, + ( ) -.',
    custom: 'Teléfono inválido.',
  },
  cp: {
    required: 'El código postal es obligatorio.',
    patternMismatch: 'Debe tener exactamente 5 dígitos.',
    custom: 'Código postal inválido.',
  },
  dni: {
    required: 'El documento es obligatorio.',
    patternMismatch: 'Entre 5 y 15 caracteres alfanuméricos.',
    custom: 'Documento inválido.',
  },
  iban_ultimos: {
    required: 'Los 4 últimos dígitos del IBAN son obligatorios.',
    patternMismatch: 'Debe tener exactamente 4 dígitos.',
    custom: 'IBAN inválido.',
  },
  fecha_nacimiento: {
    required: 'La fecha de nacimiento es obligatoria.',
    custom: 'Debes tener entre 16 y 119 años.',
  },
  altura: {
    required: 'La altura es obligatoria.',
    rangeUnderflow: 'Mínimo 120 cm.',
    rangeOverflow: 'Máximo 230 cm.',
    stepMismatch: 'Debe ser entero.',
    custom: 'Altura inválida.',
  },
  peso: {
    required: 'El peso es obligatorio.',
    rangeUnderflow: 'Mínimo 35 kg.',
    rangeOverflow: 'Máximo 250 kg.',
    custom: 'Peso inválido.',
  },
  objetivos: {
    required: 'Indica tus objetivos.',
    custom: 'Escribe al menos 3 palabras reales.',
  },
  plan: {
    required: 'Selecciona un plan.',
    custom: 'Plan inválido.',
  },
  tos: {
    required: 'Debes aceptar los términos y condiciones.',
  },
  rgpd: {
    required: 'Debes aceptar la política de privacidad.',
  },
  condiciones: {
    required: 'Selecciona al menos una condición o “Ninguna”.',
    conflict: '“Ninguna” no puede combinarse con otras opciones.',
  },
};

// ========================
// Reglas por campo (JS)
// ========================
function normalizeText(v) {
  return (v || '').trim();
}
function countRealWords(text) {
  const cleaned = normalizeText(text).replace(/\s+/g, ' ');
  const tokens = cleaned.split(' ').filter(w => /\p{L}{2,}/u.test(w));
  return tokens.length;
}
function calcAge(dateStr) {
  if (!dateStr) return NaN;
  const dob = new Date(dateStr);
  const today = new Date();
  let age = today.getFullYear() - dob.getFullYear();
  const m = today.getMonth() - dob.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) age--;
  return age;
}
const rules = {
  nombre: (input) => normalizeText(input.value).length >= 2,
  apellidos: (input) => normalizeText(input.value).length >= 2,
  email: (input) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(normalizeText(input.value)),
  telefono: (input) => /^[0-9\s+()-]{9,20}$/.test(normalizeText(input.value)),
  cp: (input) => /^[0-9]{5}$/.test(normalizeText(input.value)),
  dni: (input) => /^[A-Za-z0-9]{5,15}$/.test(normalizeText(input.value)),
  iban_ultimos: (input) => /^[0-9]{4}$/.test(normalizeText(input.value)),
  fecha_nacimiento: (input) => {
    const age = calcAge(input.value);
    return Number.isFinite(age) && age >= 16 && age < 120;
  },
  altura: (input) => {
    const num = Number(input.value);
    return Number.isInteger(num) && num >= 120 && num <= 230;
  },
  peso: (input) => {
    const num = Number(input.value);
    return Number.isFinite(num) && num >= 35 && num <= 250;
  },
  objetivos: (input) => countRealWords(input.value) >= 3,
  plan: (input) => normalizeText(input.value) !== '',
};
// Grupo condiciones médicas
function validateCondiciones(groupRoot) {
  const checks = Array.from(groupRoot.querySelectorAll('input[type="checkbox"][name="condiciones[]"]'));
  const selected = checks.filter(c => c.checked).map(c => c.value);
  if (selected.length === 0) return { ok: false, reason: 'required' };
  const hasNinguna = selected.includes('ninguna');
  const hasOther = selected.some(v => v !== 'ninguna');
  if (hasNinguna && hasOther) return { ok: false, reason: 'conflict' };
  return { ok: true };
}

// ========================
// Wiring del formulario
// ========================
const form = $('#form-inscripcion');
const submitBtn = $('.actions .btn-primary');

const fields = [
  'nombre', 'apellidos', 'email', 'telefono', 'cp', 'dni',
  'iban_ultimos', 'fecha_nacimiento', 'altura', 'peso', 'objetivos', 'plan',
];

const inputs = Object.fromEntries(
  fields.map((name) => {
    const node = form.querySelector(`[name="${name}"]`);
    return [name, node];
  })
);

// Root del grupo de condiciones médicas
const condicionesRoot =
  form.querySelector('[aria-label="Condiciones médicas"]')?.closest('.control') ||
  form;

function validateNative(input) {
  const v = input.validity;
  if (v.valid) return { ok: true };
  const key =
    v.valueMissing ? 'required' :
    v.typeMismatch ? 'typeMismatch' :
    v.patternMismatch ? 'patternMismatch' :
    v.rangeUnderflow ? 'rangeUnderflow' :
    v.rangeOverflow ? 'rangeOverflow' :
    v.stepMismatch ? 'stepMismatch' :
    'customError';
  return { ok: false, reason: key };
}
function validateCustom(name, input) {
  const rule = rules[name];
  if (!rule) return { ok: true };
  const ok = rule(input);
  return { ok, reason: ok ? null : 'custom' };
}
function showMessage(name, input, reason) {
  const msgSet = messages[name] || {};
  const msg = msgSet[reason] || msgSet.custom || 'Campo inválido.';
  showError(input, msg);
}
function validateField(name) {
  const input = inputs[name];
  if (!input) return true;

  const native = validateNative(input);
  if (!native.ok) {
    showMessage(name, input, native.reason);
    return false;
  }

  const custom = validateCustom(name, input);
  if (!custom.ok) {
    showMessage(name, input, custom.reason);
    return false;
  }

  clearError(input);
  return true;
}
function validateCondicionesGroup() {
  const result = validateCondiciones(condicionesRoot);
  const anchor = form.querySelector('input[type="checkbox"][name="condiciones[]"]');
  if (!anchor) return true;

  if (!result.ok) {
    const msg = messages.condiciones[result.reason] || messages.condiciones.required;
    showError(anchor, msg);
    return false;
  }
  clearError(anchor);
  return true;
}
function gateSubmit() {
  const allValid = fields.every(validateField) && validateCondicionesGroup();

  const tos = form.querySelector('input[name="tos"]');
  const tosOk = tos?.checked === true;

  const globalOk = allValid && tosOk;

  if (globalOk) enableSubmit(submitBtn);
  else disableSubmit(submitBtn);

  return globalOk;
}
function handleChange(e) {
  const target = e.target;
  if (!target || !form.contains(target)) return;

  const name = target.name;
  if (fields.includes(name)) {
    validateField(name);
  }

  if (target.name === 'condiciones[]') {
    const checks = $all('input[name="condiciones[]"]', form);
    const ninguna = checks.find(c => c.value === 'ninguna');
    const others = checks.filter(c => c.value !== 'ninguna');

    if (target.value === 'ninguna' && target.checked) {
      others.forEach(c => (c.checked = false));
    } else if (target.checked) {
      if (ninguna?.checked) ninguna.checked = false;
    }
    validateCondicionesGroup();
  }

  gateSubmit();
}
function handleInput(e) {
  const target = e.target;
  if (!target || !form.contains(target)) return;
  const name = target.name;
  if (fields.includes(name)) {
    const native = validateNative(target);
    if (!native.ok) {
      showMessage(name, target, native.reason);
    } else {
      const custom = validateCustom(name, target);
      if (!custom.ok) showMessage(name, target, custom.reason);
      else clearError(target);
    }
  }
}
function handleSubmit(e) {
  e.preventDefault();
  const ok = gateSubmit();
  if (!ok) {
    focusFirstInvalid(form);
    return;
  }
  alert('Formulario válido. Envío simulado ✅');
  form.reset();
  postResetCleanup();
}
function postResetCleanup() {
  $all('.error-msg', form).forEach(n => (n.textContent = ''));
  $all('[aria-invalid="true"]', form).forEach(el => el.removeAttribute('aria-invalid'));
  $all('.control', form).forEach(c => c.classList.remove('is-invalid', 'is-valid'));
  disableSubmit(submitBtn);
}

// ========================
// Listeners e inicialización
// ========================
form.addEventListener('input', handleInput);
form.addEventListener('change', handleChange);
form.addEventListener('submit', handleSubmit);
form.addEventListener('reset', () => setTimeout(postResetCleanup, 0));

disableSubmit(submitBtn);