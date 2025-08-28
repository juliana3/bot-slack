// DETECTAR EL IDIOMA DEL NAVEGADOR

async function detectarIdioma() {
    const idiomaNavegador = navigator.language || navigator.userLanguage;
    return idiomaNavegador.startsWith("en") ? "en" : "es";
}


async function cargarTraducciones() {
    const idioma = await detectarIdioma();
    const resp = await fetch(`/static/locales/${idioma}.json`);

    if (!resp.ok) {
        console.error("No se pudo cargar el archivo de traducciones:", resp.statusText);
        return {};
    }
    return await resp.json();
}

async function traducirPagina() {
    const traducciones = await cargarTraducciones();

    if (traducciones.title) {
        document.title = traducciones.title;
    }

    document.querySelectorAll("h1, h2, h3, h4, h5, h6, p, label, option, button").forEach(el => {
        const key = el.textContent.trim().replace(/\s+/g, " "); // normaliza espacios
        if (traducciones[key]) {
            el.textContent = traducciones[key];
        }
    });
}

window.addEventListener("load", traducirPagina);
