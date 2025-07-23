import os
from flask import jsonify
import requests
from dotenv import load_dotenv
import logging
import time

from services.sheets_utils import SHEET, get_col, update_col
from services.slack_utils import notificar_rrhh
from services.payload_utils import payloadALTA, payloadPDF
from handlers.documento_handler import procesar_documento




load_dotenv()

API_URL = os.getenv("PEOPLE_FORCE_URL") 
API_TOKEN = os.getenv("PEOPLE_FORCE_TOKEN")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


def procesar_ingreso(datos, fila):

    columnas = get_col(SHEET)  

    try:
        fila_data = SHEET.row_values(fila)
    except Exception as e:
        logging.error(f"Excepción al leer fila {fila} de la hoja: {str(e)}")

        return {"error": "Error al leer datos de la hoja", "status": "failed", "status_code": 500}
    

    # Armar payload para mandar a People Force
    payload = payloadALTA(fila, columnas, fila_data)

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
            notificar_rrhh(payload["first_name"], payload["last_name"],payload["personal_email"], "alta")


            #capturar el ID de la persona creada
            employee_id = response.json().get("id") #verificar con que clave devuelve PF el json
            if employee_id:
                update_col(fila, "ID PF", employee_id)

                #armar el dict para procesar documento
                payload_doc = {
                    "fila" : fila,
                    "employee_id": employee_id,
                    "nombre": datos.get("nombre"),
                    "apellido": datos.get("apellido"),
                    "email": datos.get("email"),
                    "dni_f": datos.get("dni_f"),
                    "dni_d": datos.get("dni_d"),
                }

                try:
                    time.sleep(5) # Pausa de 5 segundos, ajustar si es necesario.
                    
                    logging.info(f"Flask: Llamando a procesar_documento para fila {fila}")
                    resultado_doc = procesar_documento(payload_doc)

                    if resultado_doc.get("status_code") in [200,201]:
                        logging.info(f"Flask: Documento procesado y subido correctamente para fila {fila}")

                        return {"status": "success", "message": "Persona agregada y documento subido."}
                    else:
                        logging.error(f"Flask: Error al procesar documento para fila {fila}: {resultado_doc}")
                        return {"status": "failed", "message": "Persona agregada pero documento falló.","error": resultado_doc.get('error')}
                except requests.exceptions.RequestException as e:
                    logging.error(f"Excepcion al llamr procesar_documento para fila {fila}: {str(e)}")

                    return {"status": "failed", "message": "    p   ersona agregada pero documento falló.", "error": str(e)}

            #si no obtuvo el ID
            return {"mensaje": "Alta OK pero ID no obtenido", "status": "partial_success"}
        else:
            logging.error("Alta ERROR – fila %s | %s", fila, response.text)
            update_col(fila, "Estado", "Error")
            return {"error": "API error", "status": "failed"}

    except requests.exceptions.RequestException as e:
        logging.error("Excepción en solicitud a People Force – fila %s | %s", fila, str(e))
        update_col(fila, "Estado", "Error")
        return {"error": "Conexíon con PeopleForce fallida", "status": "failed", "status_code": 500}
    except Exception as e:
        logging.error("Excepción – fila %s | %s", fila, str(e))
        update_col(fila, "Estado", "Error")
        return {"error": "Error interno", "status": "failed", "status_code": 500}
