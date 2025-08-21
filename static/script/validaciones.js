document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById('miFormulario');
  const tipoContrato = document.getElementById("tipo-contrato");
  const tipoBancoHidden = document.getElementById("tipo_banco");
  const seccionNacional = document.getElementById("bancario-nacional");
  const seccionInternacional = document.getElementById("bancario-internacional");

  const inputCelular = document.getElementById("celular");
  const inputCBU = document.getElementById("cbu");
  const paisSelect = document.getElementById("pais");
  const inputDNI = document.getElementById("dni");
  const nombreInput = document.getElementById("nombre");
  const apellidoInput = document.getElementById("apellido");
  const domicilioInput = document.getElementById("domicilio");
  const localidadInput = document.getElementById("localidad");
  const inputFecha = document.getElementById("fecha_nacimiento");

  // Capitalizar cada palabra
  function capitalizarCadaPalabra(texto) {
    return texto
      .trim()
      .toLowerCase()
      .split(' ')
      .filter(p => p !== '')
      .map(p => p.charAt(0).toUpperCase() + p.slice(1))
      .join(' ');
  }

  // --- Lógica Celular ---
  if (inputCelular) {
    const iti = intlTelInput(inputCelular, {
      initialCountry: "auto",
      geoIpLookup: callback => {
        fetch("https://ipapi.co/json/")
          .then(res => res.json())
          .then(data => callback(data.country_code))
          .catch(() => callback("us"));
      },
      utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.19/js/utils.js",
      preferredCountries: ["ar", "us", "br", "cl", "mx"],
      separateDialCode: true,
    });

    inputCelular.addEventListener('keydown', (e) => {
      if (!((e.key >= '0' && e.key <= '9') ||
            e.key === 'Backspace' || e.key === 'Delete' ||
            e.key === 'ArrowLeft' || e.key === 'ArrowRight' ||
            e.key === 'Tab' ||
            (e.ctrlKey || e.metaKey) && (['a','c','v','x'].includes(e.key)) ||
            (e.key === '+' && !iti.options.separateDialCode && inputCelular.selectionStart === 0))) {
        e.preventDefault();
      }
    });

    inputCelular.addEventListener('input', () => {
      let val = inputCelular.value;
      const curPos = inputCelular.selectionStart;

      let newVal = iti.options.separateDialCode
        ? val.replace(/[^0-9]/g, '')
        : val.replace(/[^0-9+]/g, '');

      if (!iti.options.separateDialCode) {
        if (newVal.includes('+') && newVal.indexOf('+') !== 0)
          newVal = newVal.replace(/\+/g, '');
        if (newVal.length > 1 && newVal.charAt(0) === '+' && newVal.substring(1).includes('+'))
          newVal = '+' + newVal.substring(1).replace(/\+/g, '');
      }

      if (val !== newVal) {
        inputCelular.value = newVal;
        const newPos = curPos - (val.length - newVal.length);
        inputCelular.setSelectionRange(newPos, newPos);
      }
    });

    inputCelular.addEventListener('blur', () => {
      if (iti.isValidNumber()) {
        console.log("Número válido:", iti.getNumber());
      } else {
        console.log("Número inválido");
      }
    });
  }

  // --- Lógica CBU ---
  if (inputCBU) {
    inputCBU.addEventListener('keydown', (e) => {
      if (!((e.key >= '0' && e.key <= '9') ||
            e.key === 'Backspace' || e.key === 'Delete' ||
            e.key === 'ArrowLeft' || e.key === 'ArrowRight' ||
            e.key === 'Tab' ||
            (e.ctrlKey || e.metaKey) && ['a','c','v','x'].includes(e.key))) {
        e.preventDefault();
      }
    });

    inputCBU.addEventListener('input', () => {
      const curPos = inputCBU.selectionStart;
      const original = inputCBU.value;
      let nuevo = original.replace(/[^0-9]/g, '');

      if (nuevo.length > 22) {
        nuevo = nuevo.slice(0, 22);
      }

      if (original !== nuevo) {
        inputCBU.value = nuevo;
        const newPos = curPos - (original.length - nuevo.length);
        inputCBU.setSelectionRange(newPos, newPos);
      }
    });

    inputCBU.addEventListener('blur', () => {
      if (inputCBU.value.length > 0 && inputCBU.value.length !== 22) {
        inputCBU.setCustomValidity("El CBU debe tener exactamente 22 números.");
        inputCBU.reportValidity();
      } else {
        inputCBU.setCustomValidity("");
      }
    });
  }

  // Lógica para cambiar validación según país
  if (inputDNI && paisSelect) {
    inputDNI.addEventListener('input', () => {
      const pais = paisSelect.value;
      let val = inputDNI.value;

      switch (pais) {
        case 'de': // Alemania
          val = val.replace(/[^A-Za-z0-9]/g, '').slice(0, 9);
          break;
        case 'ar': // Argentina
          val = val.replace(/\D/g, '').slice(0, 8);
          break;
        case 'au': // Australia
          val = val.replace(/\D/g, '').slice(0, 9);
          break;
        case 'uy': // Uruguay
          val = val.replace(/\D/g, '').slice(0, 8);
          break;
        case 'pe': // Perú
          val = val.replace(/\D/g, '').slice(0, 8);
          break;
        case 'ec': // Ecuador
          val = val.replace(/\D/g, '').slice(0, 10);
          break;
        case 'co': // Colombia
          val = val.replace(/\D/g, '').slice(0, 10);
          break;
        case 'gt': // Guatemala
          val = val.replace(/\D/g, '').slice(0, 13);
          break;
        case 'do': // República Dominicana
          val = val.replace(/\D/g, '').slice(0, 11);
          break;
        case 'es': // España
          val = val.replace(/[^A-Za-z0-9]/g, '').slice(0, 9);
          break;
        case 'us': // Estados Unidos (SSN con guiones opcionales)
          val = val.replace(/[^0-9-]/g, '').slice(0, 11);
          break;
        default:
          val = val.replace(/\D/g, '').slice(0, 8);
      }
      inputDNI.value = val;
    });
  }

  // --- Lógica tipo contrato ---
  if (tipoContrato) {
    tipoContrato.addEventListener("change", () => {
      const valor = tipoContrato.value;

      if (valor === "contractor") {
        seccionInternacional.style.display = "block";
        seccionNacional.style.display = "none";
        tipoBancoHidden.value = "internacional";
      } else if (["rrdd", "monotributo"].includes(valor)) {
        seccionInternacional.style.display = "none";
        seccionNacional.style.display = "block";
        tipoBancoHidden.value = "nacional";
      } else {
        seccionInternacional.style.display = "none";
        seccionNacional.style.display = "none";
        tipoBancoHidden.value = "";
      }
    });
  }

  // --- Lógica submit: Validaciones y capitalización ---

  // DICE LAUTARO QUE LO REVISEN ACA 
  
  if (form) {
    console.log("Formulario encontrado:", form);

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      // Validar DNI
      if (inputDNI && !inputDNI.checkValidity()) {
        e.preventDefault();
        alert("Formato de documento no válido para el país seleccionado.");
        return;
      }

      // Capitalizar campos
      if (nombreInput) nombreInput.value = capitalizarCadaPalabra(nombreInput.value);
      if (apellidoInput) apellidoInput.value = capitalizarCadaPalabra(apellidoInput.value);
      if (domicilioInput) domicilioInput.value = capitalizarCadaPalabra(domicilioInput.value);
      if (localidadInput) localidadInput.value = capitalizarCadaPalabra(localidadInput.value);

      const formData = new FormData(form);
      fetch(form.action, {
        method: 'POST',
        body: formData
        })
      .then(res => {
        if (!res.ok) throw new Error("Error en el servidor");
        return res.json(); // o res.text() si el backend no devuelve JSON
      })
      .then(data => {
        console.log("Respuesta:", data);
        window.location.href = '/gracias';  // redirigir solo si fue exitoso
      })
      .catch(error => {
        console.error('Error al enviar el formulario:', error);
        alert("Hubo un error al enviar los datos");
      });


    });
  }else{
    console.error("Formulario no encontrado");
  }

});

