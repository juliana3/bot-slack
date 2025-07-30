document.addEventListener("DOMContentLoaded", () => {
  const tipoContrato = document.getElementById("tipo-contrato");
  const tipoBanco = document.getElementById("tipo-banco");

  const seccionNacional = document.getElementById("bancario-nacional");
  const seccionInternacional = document.getElementById("bancario-internacional");

  // Manejo de visibilidad según tipo de contrato
  tipoContrato.addEventListener("change", () => {
    const valor = tipoContrato.value;

    if (valor === "contractor") {
      // Contractor habilita solo transferencia extranjera y oculta nacional
      seccionInternacional.style.display = "block";
      seccionNacional.style.display = "none";

      // También, deshabilitamos selector tipo banco porque no se necesita elegir nacional/internacional
      tipoBanco.value = "";
      tipoBanco.disabled = true;
    } else if (valor === "rrdd" || valor === "monotributo") {
      // RRDD o Monotributo habilitan transferencia nacional y selector tipo banco
      seccionInternacional.style.display = "none";
      seccionNacional.style.display = "block";

      tipoBanco.disabled = false;
    } else {
      // Si no selecciona nada
      seccionInternacional.style.display = "none";
      seccionNacional.style.display = "none";
      tipoBanco.disabled = false;
    }
  });

  // Manejo de visibilidad según tipo de banco (solo si el selector está habilitado)
  tipoBanco.addEventListener("change", () => {
    if (tipoBanco.disabled) return; // Ignorar cambios si está deshabilitado

    if (tipoBanco.value === "nacional") {
      seccionNacional.style.display = "block";
      seccionInternacional.style.display = "none";
    } else if (tipoBanco.value === "internacional") {
      seccionInternacional.style.display = "block";
      seccionNacional.style.display = "none";
    } else {
      seccionInternacional.style.display = "none";
      seccionNacional.style.display = "none";
    }
  });
});
