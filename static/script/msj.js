
async function detectarIdioma() {
    const idiomaNavegador = navigator.language || navigator.userLanguage;
    if (idiomaNavegador.startsWith("es")) return "es";
    if (idiomaNavegador.startsWith("pt")) return "pt";
    return "en"; // por defecto
}

async function cargarTraducciones() {
    const idioma = await detectarIdioma();
    const resp = await fetch(`/static/locales/${idioma}.json`);
    return await resp.json(); // devuelve todo el JSON
}

async function iniciarAnimacion() {
    const traducciones = await cargarTraducciones();

    // Cambiar el título de la página
    if (traducciones.title) {
        document.title = traducciones.title;
    }

    // Animar el texto
    const frases = traducciones.frases || [];
    const elemento = document.getElementById('maquina-escribir');
    let indexFrase = 0;
    let indexChar = 0;
    let borrando = false;

    function animarTexto() {
        const fraseActual = frases[indexFrase] || "";

        if (!borrando && indexChar < fraseActual.length) {
            elemento.textContent += fraseActual.charAt(indexChar);
            indexChar++;
            setTimeout(animarTexto, 50);
        } else if (!borrando && indexChar === fraseActual.length) {
            borrando = true;
            setTimeout(animarTexto, 5000);
        } else if (borrando && indexChar > 0) {
            elemento.textContent = fraseActual.substring(0, indexChar - 1);
            indexChar--;
            setTimeout(animarTexto, 50);
        } else if (borrando && indexChar === 0) {
            borrando = false;
            indexFrase = (indexFrase + 1) % frases.length;
            setTimeout(animarTexto, 500);
        }
    }

    animarTexto();
}

iniciarAnimacion();
