async function detectarIdioma() {
    const idiomaNavegador = navigator.language || navigator.userLanguage;
    if (idiomaNavegador.startsWith("es")) return "es";
    if (idiomaNavegador.startsWith("pt")) return "pt";
    return "en";
}

async function cargarTraducciones() {
    const idioma = await detectarIdioma();
    const resp = await fetch(`/static/locales/${idioma}.json`);
    return await resp.json();
}

async function traducirPagina() {
    const traducciones = await cargarTraducciones();

    // Traducir title
    if (traducciones.title) {
        document.title = traducciones.title;
    }

    // Traducir headings
    document.querySelectorAll("h1, h2, h3, h4, h5, h6").forEach(h => {
        const key = h.textContent.trim();
        if (traducciones[key]) {
            h.textContent = traducciones[key];
        }
    });

    // Traducir párrafos
    document.querySelectorAll("p").forEach(p => {
        const key = p.textContent.trim().replace(/\s+/g, " ");
        if (traducciones[key]) {
            p.textContent = traducciones[key];
        }
    });

    // Traducir botones
    document.querySelectorAll("button").forEach(btn => {
        const key = btn.textContent.trim();
        if (traducciones[key]) {
            btn.textContent = traducciones[key];
        }
    });

    // Traducir labels y options
    document.querySelectorAll("label, option").forEach(el => {
        const key = el.textContent.trim();
        if (traducciones[key]) {
            el.textContent = traducciones[key];
        }
    });
}

traducirPagina();
