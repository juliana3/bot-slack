const formulario = document.getElementById('formulario-contacto');

// Escucha el evento de envío del formulario
formulario.addEventListener('submit', function(e) {
  // Evita el envío por defecto del formulario
  e.preventDefault();
  const datos = new FormData(formulario);
  
  // URL de tu endpoint de backend
  const urlBackend = 'http://localhost:4000/agregar_persona';

  fetch(urlBackend, {
    method: 'POST',
    body: datos
  })
  .then(response => response.json())
  .then(data => {
    console.log('Respuesta del backend:', data);
    // Si la respuesta es exitosa, redirige al usuario
    if (data.status === 'success') {
      window.location.href = 'agradecimiento.html';
    } else {
      // Maneja errores, muestra un mensaje, etc.
      alert('Hubo un error al enviar el formulario.');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    alert('Hubo un problema de conexión. Intenta de nuevo más tarde.');
  });
});