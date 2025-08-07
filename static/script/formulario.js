document.addEventListener("DOMContentLoaded", function () {
    const formulario = document.getElementById("miFormulario");
    const mensaje = document.getElementById("mensajeAgradecimiento");

    formulario.addEventListener("submit", function (event) {
        event.preventDefault(); // Evita el envío por defecto del navegador

        const formData = new FormData(formulario);

        fetch(formulario.action, {
        method: "POST",
        body: formData,
        })
        .then(response => {
            if (response.ok) {
            // Éxito en el envío
            formulario.style.display = "none";
            mensaje.style.display = "block";
            } else {
            alert("Hubo un error al enviar el formulario.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Hubo un error al enviar el formulario.");
        });
    });
});

mensaje.classList.add("mostrar");