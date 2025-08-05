import requests
import json
import logging
import time

# Configuración del logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# URL del endpoint de tu aplicación Flask
FLASK_ENDPOINT = "http://localhost:4000/agregar_persona"

# Datos de prueba para simular el envío del formulario
# Es crucial que las claves (keys) de este diccionario coincidan
# con los nombres de las columnas en tu tabla de ingresantes.
payload = {
    "nombre": "Juan",
    "apellido": "Perez",
    "dni": "12345679",
    "dni_frente": "dni_frente/juan_perez_12345678_frente.png",
    "dni_dorso": "dni_dorso/juan_perez_12345678_dorso.png",
    "email": "juana.perez@example.com",
    "domicilio": "Calle Falsa 123",
    "localidad": "Ciudad Autónoma de Buenos Aires",
    "celular": "+5491155554444",
    "fecha_nacimiento": "1990-01-01",
    "tipo_contrato": "rrdd",
    "banco": "Banco Galicia",
    "numero_cuenta": "1234567890",
    "cbu": "1234567890123456789012",
    "alias": "JUAN.PEREZ.GALICIA",
    "cuil": "20123456789",
    "obra_social": "OSDE",
    "codigo_afip": "123456",
    "id_pf": None,
    "estado_alta": "Pendiente",
    "estado_pdf": "Pendiente"
}


def enviar_payload():
    """
    Simula el envío de un formulario a través de una solicitud HTTP POST.
    """
    logging.info(f"Enviando solicitud POST a {FLASK_ENDPOINT} con los siguientes datos:")
    logging.info(json.dumps(payload, indent=4))

    try:
        response = requests.post(FLASK_ENDPOINT, json=payload, timeout=10)
        
        logging.info(f"Respuesta del servidor: {response.status_code}")
        logging.info(f"Body de la respuesta: {response.text}")
        
        if response.status_code == 200:
            logging.info("El payload fue enviado y procesado correctamente.")
        else:
            logging.error("Hubo un error al enviar el payload. Revisa los logs de tu servidor Flask.")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error de conexión: {e}")
        logging.error("Asegúrate de que tu servidor Flask esté en ejecución.")
    except Exception as e:
        logging.error(f"Error inesperado: {e}")

if __name__ == "__main__":
    enviar_payload()