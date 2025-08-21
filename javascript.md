 const inputFecha = document.getElementById("fecha_nacimiento");

 if (form) {
    form.addEventListener("submit", (e) => {
      // Formatear fecha antes de enviar
      if (inputFecha && inputFecha.value) {
        let [year, month, day] = inputFecha.value.split("-");
        let fechaTexto = `${day}-${month}-${year}`;
        inputFecha.value = fechaTexto;  // Cambio para enviar como texto
      }

      // Validar DNI
      if (inputDNI) {
        const dniValor = inputDNI.value;
        if (!/^\d{8}$/.test(dniValor)) {
          e.preventDefault();
          alert("El DNI debe tener exactamente 8 números.");
          return;
        }
      }

      // Capitalizar campos
      if (nombreInput) nombreInput.value = capitalizarCadaPalabra(nombreInput.value);
      if (apellidoInput) apellidoInput.value = capitalizarCadaPalabra(apellidoInput.value);
      if (domicilioInput) domicilioInput.value = capitalizarCadaPalabra(domicilioInput.value);
      if (localidadInput) localidadInput.value = capitalizarCadaPalabra(localidadInput.value);
    });
  }