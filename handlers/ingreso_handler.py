import os
import requests
from dotenv import load_dotenv
import logging
import time
from io import BytesIO

from services.db_operations import guardar_ingresante, actualizar_estado, obtener_id_carpeta_drive
from services.sheets_utils import  cargar_sheets
from services.slack_utils import notificar_rrhh
from services.payload_utils import payloadALTA
from services.drive_utils import crear_carpeta, subir_imagen_a_drive


from handlers.documento_handler import procesar_documento




load_dotenv()

API_URL = os.getenv("PEOPLEFORCE_URL") 
API_TOKEN = os.getenv("PEOPLEFORCE_TOKEN")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


def procesar_ingreso(datos, archivos=None, ingresante_id_db = None, es_reproceso = False):

    fila_sheets = None
    id_carpeta_ingresante = None

    if not ingresante_id_db:
        ingresante_id_db = datos.get("id")

    #si es reproceso o si ya se gguardo en la bbdd se busca el id DE LA CARPETA
    if ingresante_id_db:
        ingresante_con_id_carpeta = obtener_id_carpeta_drive(ingresante_id_db)
        if ingresante_con_id_carpeta:
            id_carpeta_ingresante = ingresante_con_id_carpeta.get("id_carpeta_drive")
            if id_carpeta_ingresante:
                logging.info(f"Se encontró carpeta existente en BD: {id_carpeta_ingresante}")

    #si NO se encontro carpeta, crear una nueva
    if not id_carpeta_ingresante:
        #crear una carpeta para las fotos de dni y el pdf
        nombre_carpeta = f"{datos.get('nombre')}-{datos.get('apellido')}"
        id_carpeta_ingresante = crear_carpeta(nombre_carpeta)
        logging.info(f"Carpeta creada en Drive con ID: {id_carpeta_ingresante}")

    datos["id_carpeta_drive"] = id_carpeta_ingresante
    
    #subir las imagenes si no es reproceso
    if not es_reproceso:
        #subir las imagenes a la carpeta
        id_dni_frente = None
        if "dni_frente" in archivos:
            img_f = BytesIO(archivos["dni_frente"])
            id_dni_frente = subir_imagen_a_drive(img_f, "dni_frente.jpg", id_carpeta_ingresante)
            if not id_dni_frente:
                logging.error("Falló la subida de la imagen del DNI frente a Drive.")
                return {"status": "failed", "message": "Falló la subida del DNI frente a Drive."}
        
        id_dni_dorso = None
        if "dni_dorso" in archivos:
            img_d = BytesIO(archivos["dni_dorso"])
            id_dni_dorso = subir_imagen_a_drive(img_d, "dni_dorso.jpg", id_carpeta_ingresante)
            if not id_dni_dorso:
                logging.error("Falló la subida de la imagen del DNI dorso a Drive.")
                return {"status": "failed", "message": "Falló la subida del DNI dorso a Drive."}
            
        datos["dni_frente"] = id_dni_frente
        datos["dni_dorso"] = id_dni_dorso

    #Guardar los datos iniciales en Sheets como respaldo solo si no es reproceso
    if not es_reproceso:
        logging.info("Intentando añadir datos a Google Sheets..")
        fila_sheets = cargar_sheets(datos)

        if fila_sheets is None:
            logging.error("Falló la escritura en Google Sheets. Continuando sin respaldo")

    

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
                    "dni_f": datos.get("dni_frente", ""),
                    "dni_d": datos.get("dni_dorso", ""),
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
