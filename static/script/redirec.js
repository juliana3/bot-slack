const frases = [
    "¡BIENVENIDO A CROMBIE! 🎉🥳",
    "¡A PARTIR DE AHORA ERES UN CROMBIER! 😎"
]

const elemento = document.getElementById('maquina-escribir')
let indexFrase = 0;
let indexChar = 0;
let borrando = false;

function animarTexto(){
    const fraseActual = frases[indexFrase];

    if (!borrando && indexChar < fraseActual.length){
        elemento.textContent += fraseActual.charAt(indexChar);
        indexChar++;
        setTimeout(animarTexto, 50);
    }
    else if (!borrando && indexChar === fraseActual.length){
        borrando = true;
        setTimeout(animarTexto, 5000);
    }
    else if(borrando && indexChar > 0){
        elemento.textContent = fraseActual.substring(0, indexChar - 1);
        indexChar--;
        setTimeout(animarTexto, 50)
    }
    else if(borrando && indexChar === 0){
        borrando = false;
        indexFrase = (indexFrase + 1) % frases.length;
        setTimeout(animarTexto, 500);
    }
}

animarTexto();
