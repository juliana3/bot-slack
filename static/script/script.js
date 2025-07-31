document.addEventListener("DOMContentLoaded", () => {
    const tipoContrato = document.getElementById("tipo-contrato");
    const tipoBancoHidden = document.getElementById("tipo-banco");

    const seccionNacional = document.getElementById("bancario-nacional");
    const seccionInternacional = document.getElementById("bancario-internacional");

    // Lógica para el campo Celular 
    const inputCelular = document.getElementById("celular");
    if (inputCelular) {
        // Inicialización del plugin intl-tel-input
        const iti = intlTelInput(inputCelular, {
            initialCountry: "auto",
            geoIpLookup: function(callback) {
                fetch("https://ipapi.co/json/")
                    .then(res => res.json())
                    .then(data => callback(data.country_code))
                    .catch(() => callback("us"));
            },
            utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.19/js/utils.js",
            preferredCountries: ["ar", "us", "br", "cl", "mx"],
            separateDialCode: true,
        });

        // Evento keydown para Celular: Previene la entrada de letras y caracteres no deseados
        inputCelular.addEventListener('keydown', (e) => {
            if (!((e.key >= '0' && e.key <= '9') ||
                  e.key === 'Backspace' || e.key === 'Delete' ||
                  e.key === 'ArrowLeft' || e.key === 'ArrowRight' ||
                  e.key === 'Tab' ||
                  (e.ctrlKey || e.metaKey) && (e.key === 'a' || e.key === 'c' || e.key === 'v' || e.key === 'x') ||
                  (e.key === '+' && !iti.options.separateDialCode && inputCelular.selectionStart === 0)
                 )) {
                e.preventDefault();
            }
        });

        // Evento input para Celular: Limpia el campo si se pega contenido no numérico
        inputCelular.addEventListener('input', () => {
            const currentCursorPosition = inputCelular.selectionStart;
            const originalValue = inputCelular.value;
            let newValue = originalValue;

            if (iti.options.separateDialCode) {
                 newValue = originalValue.replace(/[^0-9]/g, '');
            } else {
                 newValue = originalValue.replace(/[^0-9+]/g, '');
                 if (newValue.includes('+') && newValue.indexOf('+') !== 0) {
                     newValue = newValue.replace(/\+/g, '');
                 }
                 if (newValue.length > 1 && newValue.charAt(0) === '+' && newValue.substring(1).includes('+')) {
                     newValue = '+' + newValue.substring(1).replace(/\+/g, '');
                 }
            }

            if (newValue !== originalValue) {
                inputCelular.value = newValue;
                const newCursorPosition = currentCursorPosition - (originalValue.length - newValue.length);
                inputCelular.setSelectionRange(newCursorPosition, newCursorPosition);
            }
        });

        inputCelular.addEventListener('blur', () => {
            const itiInstance = inputCelular.intlTelInput;
            if (itiInstance && itiInstance.isValidNumber()) {
                console.log("Número completo formateado (Celular):", itiInstance.getNumber());
            } else {
                console.log("Número de teléfono no válido (Celular).");
            }
        });
    } else {
        console.error("El elemento con ID 'celular' no se encontró en el DOM. Asegúrate de que el input tenga id='celular'.");
    }

    // --- Lógica mejorada para el campo CBU ---
    const inputCBU = document.getElementById("cbu");
    if (inputCBU) {
        // Evento keydown para CBU: Previene la entrada de letras
        inputCBU.addEventListener('keydown', (e) => {
            // Permitir solo números (0-9), teclas de navegación, backspace, delete, tab
            // y los atajos de copiar/pegar (Ctrl/Cmd + A/C/V/X)
            if (!((e.key >= '0' && e.key <= '9') ||
                  e.key === 'Backspace' || e.key === 'Delete' ||
                  e.key === 'ArrowLeft' || e.key === 'ArrowRight' ||
                  e.key === 'Tab' ||
                  (e.ctrlKey || e.metaKey) && (e.key === 'a' || e.key === 'c' || e.key === 'v' || e.key === 'x')
                 )) {
                e.preventDefault(); // Si no es un número o una tecla permitida, previene la entrada
            }
        });

        // Evento input para CBU: Limpia el campo si se escribe o pega contenido no numérico
        inputCBU.addEventListener('input', () => {
            const currentCursorPosition = inputCBU.selectionStart;
            const originalValue = inputCBU.value;
            // **Modificación clave:** Reemplaza inmediatamente cualquier carácter que no sea un dígito.
            // Esto es más agresivo y suele resolver problemas de caracteres "filtrados".
            const newValue = originalValue.replace(/[^0-9]/g, '');

            // Si se llega a escribir algo que no es un número, se corrige inmediatamente
            if (newValue !== originalValue) {
                inputCBU.value = newValue;
                // Ajusta la posición del cursor si el valor cambió
                const newCursorPosition = currentCursorPosition - (originalValue.length - newValue.length);
                inputCBU.setSelectionRange(newCursorPosition, newCursorPosition);
            }

            // Opcional: Limitar la longitud a 22 dígitos en tiempo real
            if (inputCBU.value.length > 22) {
                const truncatedValue = inputCBU.value.substring(0, 22);
                if (inputCBU.value !== truncatedValue) {
                    inputCBU.value = truncatedValue;
                    // Asegura que el cursor no se vaya al final si se truncó el valor
                    inputCBU.setSelectionRange(22, 22);
                }
            }
        });

        // Opcional: Validación de longitud en el evento blur para CBU
        inputCBU.addEventListener('blur', () => {
            if (inputCBU.value.length > 0 && inputCBU.value.length !== 22) {
                console.log("CBU inválido: Debe tener exactamente 22 dígitos.");
                // Puedes usar las validaciones nativas del navegador para mostrar un mensaje:
                inputCBU.setCustomValidity("El CBU debe tener exactamente 22 números.");
                inputCBU.reportValidity(); // Esto muestra el mensaje de error del navegador
            } else {
                inputCBU.setCustomValidity(""); // Si es válido, limpia el mensaje de error
            }
        });

    } else {
        console.error("El elemento con ID 'cbu' no se encontró en el DOM. Asegúrate de que el input tenga id='cbu'.");
    }

    // --- Lógica existente para mostrar/ocultar secciones bancarias ---
    tipoContrato.addEventListener("change", () => {
        const valor = tipoContrato.value;

        if (valor === "contractor") {
            seccionInternacional.style.display = "block";
            seccionNacional.style.display = "none";
            tipoBancoHidden.value = "internacional";
        } else if (valor === "rrdd" || valor === "monotributo") {
            seccionInternacional.style.display = "none";
            seccionNacional.style.display = "block";
            tipoBancoHidden.value = "nacional";
        } else {
            seccionInternacional.style.display = "none";
            seccionNacional.style.display = "none";
            tipoBancoHidden.value = "";
        }
    });
});