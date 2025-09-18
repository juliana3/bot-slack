import os
import requests
from dotenv import load_dotenv
import logging
import time
from io import BytesIO

from services.db_operations import  actualizar_columna, obtener_id_carpeta_drive
from services.sheets_utils import  cargar_sheets
from services.slack_utils import notificar_rrhh
from services.payload_utils import payloadALTA
from services.drive_utils import crear_carpeta, mover_archivo


from handlers.documento_handler import procesar_documento




load_dotenv()

API_URL = os.getenv("PEOPLEFORCE_URL") 
API_TOKEN = os.getenv("PEOPLEFORCE_TOKEN")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


def procesar_ingreso(datos,  es_reproceso = False):

    id_carpeta_ingresante = None
    ingresante_id_db = datos.get("id")
    #si es reproceso o si ya se gguardo en la bbdd se busca el id DE LA CARPETA
    if es_reproceso and ingresante_id_db: # si es reproceso buscar el id de la carpeta
        carpeta_ingresante_dict = obtener_id_carpeta_drive(ingresante_id_db) #esto devuelve un dict
        id_carpeta_ingresante = carpeta_ingresante_dict['id_drive_folder']

        if id_carpeta_ingresante:
            logging.info(f"Se encontró carpeta existente en BD: {id_carpeta_ingresante}")

    #si NO se encontro carpeta, crear una nueva
    if not id_carpeta_ingresante:
        #crear una carpeta para las fotos de dni y el pdf
        nombre_carpeta = f"{datos.get('first_name')}-{datos.get('last_name')}"
        id_carpeta_ingresante = crear_carpeta(nombre_carpeta)
        logging.info(f"Carpeta creada en Drive con ID: {id_carpeta_ingresante}")

    
    actualizar_columna(ingresante_id_db, "id_drive_folder", id_carpeta_ingresante)

    #cambiamos las fotos del dni de carpeta "no autorizados" a su carpeta personal
    mover_archivo(datos.get('dni_front'), id_carpeta_ingresante)
    mover_archivo(datos.get('dni_back'), id_carpeta_ingresante)


    

    # Armar payload para mandar a People Forc
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
            actualizar_columna(ingresante_id_db, "onboarding_status", "Procesada")

            #Notifica a rrhh por slack
            notificar_rrhh(payload["first_name"], payload["last_name"],payload["personal_email"], "alta")


            #capturar el ID de la persona creada
            employee_id = response.json().get("id") 
            if employee_id:
                actualizar_columna(ingresante_id_db, "id_pf", employee_id)

                #armar el dict para procesar documento
                payload_doc = {
                    "document_id_db": ingresante_id_db,
                    "employee_id": employee_id,
                    "nombre": datos.get("first_name", ""),
                    "apellido": datos.get("last_name", ""),
                    "email": datos.get("email", ""),
                    "dni_f": datos.get("dni_front", ""),
                    "dni_d": datos.get("dni_back", ""),
                    "id_carpeta_drive" : id_carpeta_ingresante,
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
            actualizar_columna(ingresante_id_db, "onboarding_status", "Error")
            return {"error": "API error", "status": "failed"}

    except requests.exceptions.RequestException as e:
        logging.error(f"Excepción en solicitud a People Force para ingresante ID DB: {ingresante_id_db} | {str(e)}")
        actualizar_columna(ingresante_id_db, "onboarding_status", "Error")
        return {"error": "Conexíon con PeopleForce fallida", "status": "failed", "status_code": 500}
    except Exception as e:
        logging.error(f"Excepción para ingresante ID BD: {ingresante_id_db} | {str(e)}" )
        actualizar_columna(ingresante_id_db, "onboarding_status", "Error")
        return {"error": "Error interno", "status": "failed", "status_code": 500}
