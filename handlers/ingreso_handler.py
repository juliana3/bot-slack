import os
import requests
from dotenv import load_dotenv
import logging

from services.sheets_utils import SHEET, get_col, update_col
from services.slack_utils import notificar_rrhh
from services.toPDF_utils import armar_pdf_dni
from services.payload_utils import payloadALTA




load_dotenv()

API_URL = os.getenv("PEOPLE_FORCE_URL") 
API_TOKEN = os.getenv("PEOPLE_FORCE_TOKEN")



def procesar_ingreso(datos):

    fila = datos["fila"]


    # Armar payload
    payload = payloadALTA(datos)

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
            notificar_rrhh(datos["nombre"], datos["email"], "alta")

            employee_id = response.json().get("id") #verificar con que clave devuelve PF el json
            if employee_id:
                update_col(fila, "ID PF", employee_id)

            return {"mensaje": "Alta OK", "status_code": response.status_code}
        else:
            logging.error("Alta ERROR – fila %s | %s", fila, response.text)
            update_col(fila, "Estado", "Error")
            return {"error": "API error", "status_code": 500}

    except Exception as e:
        logging.error("Excepción – fila %s | %s", fila, str(e))
        update_col(fila, "Estado", "Error")
        return {"error": "Conexión fallida", "status_code": 500}
