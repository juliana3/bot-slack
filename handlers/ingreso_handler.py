import os
import requests
from dotenv import load_dotenv
import logging
import time

from services.db_operations import guardar_ingresante, actualizar_estado
from services.sheets_utils import SHEET, get_col, cargar_sheets
from services.slack_utils import notificar_rrhh
from services.payload_utils import payloadALTA
from services.db_operations import guardar_ingresante, actualizar_estado

from handlers.documento_handler import procesar_documento




load_dotenv()

API_URL = os.getenv("PEOPLEFORCE_URL") 
API_TOKEN = os.getenv("PEOPLEFORCE_TOKEN")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


def procesar_ingreso(datos, es_reproceso = False):

    dni_frente_s3 = datos.get("dni-frente","")
    dni_dorso_s3 = datos.get("dni-dorso","")
    fila_sheets = None

    #Guardar los datos iniciales en Sheets como respaldo solo si no es reproceso
    if not es_reproceso:
        logging.info("Intentando añadir datos a Google Sheets..")
        fila_sheets = cargar_sheets(datos)
    

        if fila_sheets is None:
            logging.error("Falló la escritura en Google Sheets. Continuando sin respaldo")
        
    #Guardar los datos iniciales en la Base de Datos
    logging.info("Intentando guardar datos iniciales en PostgreSQL...")
    ingresante_id_db = guardar_ingresante(datos)
    if ingresante_id_db is None:
        logging.error("Falló la escritura inicial en PostgreSQL")
        return {"error": "Error al guardar datos en la base de datos princcipal", "status": "failed", "status_code": 500}

    # Armar payload para mandar a People Force
    payload = payloadALTA(datos)

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            logging.info(f"Alta OK para ingresante ID DB: {ingresante_id_db} | response: {response.json()}")
            #actualizar estado_alta en la BD
            actualizar_estado(ingresante_id_db, "estado_alta", "Procesada")

            #Notifica a rrhh por slack
            notificar_rrhh(payload["first_name"], payload["last_name"],payload["personal_email"], "alta")


            #capturar el ID de la persona creada
            employee_id = response.json().get("id") #verificar con que clave devuelve PF el json
            if employee_id:
                actualizar_estado(ingresante_id_db, "id_pf", employee_id)

                #armar el dict para procesar documento
                payload_doc = {
                    "document_id_db": ingresante_id_db,
                    "employee_id": employee_id,
                    "nombre": datos.get("nombre", ""),
                    "apellido": datos.get("apellido", ""),
                    "email": datos.get("email", ""),
                    "dni_f": dni_frente_s3,
                    "dni_d": dni_dorso_s3,
                }

                try:
                    time.sleep(5) # Pausa de 5 segundos, ajustar si es necesario.
                    
                    logging.info(f"Flask: Llamando a procesar_documento para fila ingresante ID BD: {ingresante_id_db}")
                    resultado_doc = procesar_documento(payload_doc)

                    if resultado_doc.get("status_code") in [200,201]:
                        logging.info(f"Flask: Documento procesado y subido correctamente para ingresante ID BD: {ingresante_id_db}")

                        return {"status": "success", "message": "Persona agregada y documento subido."}
                    else:
                        logging.error(f"Flask: Error al procesar documento para ingreante ID DB:{ingresante_id_db}: {resultado_doc}")
                        return {"status": "failed", "message": "Persona agregada pero documento falló.","error": resultado_doc.get('error')}
                except requests.exceptions.RequestException as e:
                    logging.error(f"Excepcion al llamr procesar_documento para ingresante ID BD: {ingresante_id_db}: {str(e)}")

                    return {"status": "failed", "message": "persona agregada pero documento falló.", "error": str(e)}

            #si no obtuvo el ID de PF
            return {"mensaje": "Alta OK pero ID no obtenido", "status": "partial_success"}
        else:
            logging.error(f"Alta ERROR para ingresante ID BD: {ingresante_id_db} | {response.text}")
            actualizar_estado(ingresante_id_db, "estado_alta", "Error")
            return {"error": "API error", "status": "failed"}

    except requests.exceptions.RequestException as e:
        logging.error(f"Excepción en solicitud a People Force para ingresante ID DB: {ingresante_id_db} | {str(e)}")
        actualizar_estado(ingresante_id_db, "estado_alta", "Error")
        return {"error": "Conexíon con PeopleForce fallida", "status": "failed", "status_code": 500}
    except Exception as e:
        logging.error(f"Excepción para ingresante ID BD: {ingresante_id_db} | {str(e)}" )
        actualizar_estado(ingresante_id_db, "estado_alta", "Error")
        return {"error": "Error interno", "status": "failed", "status_code": 500}
