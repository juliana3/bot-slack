import os
import requests
from dotenv import load_dotenv
import logging
from services.sheets_utils import SHEET, update_col
from services.slack_utils import notificar_rrhh
from services.correo_utils import verificar_y_enviar_dni



load_dotenv()

API_URL = "http://localhost:3000/agregar_persona" #esto se cambia por os.getenv("PEOPLE_FORCE_URL")
API_TOKEN = os.getenv("PEOPLE_FORCE_TOKEN")



def procesar_ingreso(datos):

    fila = datos["fila"]

    # Armar payload
    payload = {
        "name": datos["nombre"],
        "email": datos["email"]
        #despues garegar el resto de datos
    }

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            logging.info("Alta OK – fila %s | response: %s", fila, response.json())
            update_col(fila, "Estado","Procesada")

            #Notifica a rrhh por slack
            notificar_rrhh(datos["nombre"], datos["email"])

            # Verifica y envía el DNI si corresponde
            try:
                verificar_y_enviar_dni(fila)
            except Exception as e:
                logging.warning(f"Fallo al enviar DNI para fila {fila}: {e}")

            return {"mensaje": "Alta OK", "status_code": response.status_code}
        else:
            logging.error("Alta ERROR – fila %s | %s", fila, response.text)
            update_col(fila, "Estado", "Error")
            return {"error": "API error", "status_code": 500}

    except Exception as e:
        logging.error("Excepción – fila %s | %s", fila, str(e))
        update_col(fila, "Estado", "Error")
        return {"error": "Conexión fallida", "status_code": 500}
