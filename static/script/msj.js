async function detectarIdioma() {
    const idiomaNavegador = navigator.language || navigator.userLanguage;
    if (idiomaNavegador.startsWith("es")) return "es";
    return "en"; 
}

async function cargarTraducciones() {
    const idioma = await detectarIdioma();

    // Diccionario embebido en JS
    const traducciones = {
        es: {
            title: "¡Bienvenido a Crombie",
            frases: [
                "BIENVENIDO A CROMBIE! 🎉🥳",
                "A PARTIR DE AHORA ERES UN CROMBIER! 😎"
            ]
        },
        en: {
            title: "¡Welcome to Crombie!",
            frases: [
                "WELCOME TO CROMBIE! 🎉🥳",
                "FROM NOW ON, YOU ARE A CROMBIER! 😎"
            ]
        }
    };

    return traducciones[idioma] || traducciones["en"];
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