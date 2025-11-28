# Formulario de Inscripción Gimnasio — Validación JS + DOM

## 📘 Descripción
Proyecto académico de validación de formularios accesibles.  
Se parte de un formulario HTML + CSS y se implementa validación en **JavaScript vanilla** usando el DOM.  
El envío se bloquea hasta que todos los campos obligatorios cumplen sus reglas y se aceptan los consentimientos.

---

## 🧩 Reglas de validación por campo

| Campo              | Regla aplicada                                                                 |
|--------------------|--------------------------------------------------------------------------------|
| **nombre**         | Mínimo 2 caracteres reales                                                     |
| **apellidos**      | Mínimo 2 caracteres reales                                                     |
| **email**          | Patrón estándar de correo (`usuario@dominio.tld`)                              |
| **telefono**       | 9–20 caracteres; solo dígitos, espacio, + ( ) -                               |
| **cp**             | Exactamente 5 dígitos                                                          |
| **dni**            | 5–15 caracteres alfanuméricos                                                  |
| **iban_ultimos**   | Exactamente 4 dígitos                                                          |
| **fecha_nacimiento** | Edad calculada ≥16 y <120 años                                               |
| **altura**         | Entero entre 120 y 230 cm                                                      |
| **peso**           | Número entre 35 y 250 kg (decimales permitidos)                                |
| **objetivos**      | Al menos 3 palabras reales                                                     |
| **plan**           | Selección obligatoria (no vacío)                                               |
| **condiciones médicas** | Al menos una marcada; exclusión entre “Ninguna” y otras                   |
| **tos** (Términos) | Obligatorio: debe estar marcado                                                |
| **rgpd** (Privacidad) | Obligatorio: debe estar marcado                                             |

---

## ⚙️ Cómo arrancar en local

1. Clonar o descargar el proyecto.
2. Abrir el archivo `index.html` en cualquier navegador moderno.
3. El formulario cargará con estilos (`css/styles.css`) y validación (`js/formValidation.js`).

---

## 🧪 Pruebas realizadas

- **Campos obligatorios vacíos** → muestran mensaje “required”.
- **Email inválido** → mensaje “Formato de correo no válido”.
- **Teléfono con letras** → mensaje “patternMismatch”.
- **Código postal con menos de 5 dígitos** → mensaje “Debe tener exactamente 5 dígitos”.
- **Fecha de nacimiento <16 años o ≥120** → mensaje “Debes tener entre 16 y 119 años”.
- **Objetivos con menos de 3 palabras** → mensaje “Escribe al menos 3 palabras reales”.
- **Condiciones médicas**:
  - Ninguna marcada → error.
  - “Ninguna” + otra → error de conflicto.
  - Solo “Ninguna” o solo otras → válido.
- **Consentimientos**:
  - Si falta Términos o RGPD → botón Enviar deshabilitado.
  - Ambos marcados → botón habilitado.
- **Submit con errores** → se bloquea y enfoca el primer campo inválido.
- **Submit válido** → alerta de envío simulado y reset del formulario.

---