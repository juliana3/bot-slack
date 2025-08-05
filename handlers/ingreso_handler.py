import os
import requests
from dotenv import load_dotenv
import logging
import time

from services.database_config import Session, Ingresante
from services.sheets_utils import SHEET, get_col, cargar_sheets
from services.slack_utils import notificar_rrhh
from services.payload_utils import payloadALTA
from services.db_operations import guardar_ingresante, actualizar_estado

from handlers.documento_handler import procesar_documento




load_dotenv()

API_URL = os.getenv("PEOPLE_FORCE_URL") 
API_TOKEN = os.getenv("PEOPLE_FORCE_TOKEN")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


def procesar_ingreso(datos: dict, session):
    try:
        # Obtener datos de archivos desde el formulario
        dni_frente_s3 = datos.get("dni-frente", "")
        dni_dorso_s3 = datos.get("dni-dorso", "")

        # 1. Guardar respaldo en Google Sheets
        fila_sheets = cargar_sheets(datos)
        logging.info(f"[DEBUG] Resultado de cargar_sheets: {fila_sheets}")

        if fila_sheets is None:
            logging.warning("Falló la escritura en Google Sheets. Continuando sin respaldo...")

        # 2. Guardar en la base de datos
        logging.info("Intentando guardar datos en PostgreSQL...")
        ingresante_id_db = guardar_ingresante(datos, session)

        if not ingresante_id_db:
            logging.error("Falló la escritura inicial en PostgreSQL.")
            return {
                "error": "Error al guardar datos en la base de datos principal",
                "status": "failed",
                "status_code": 500
            }

        # 3. Preparar alta en PeopleForce
        payload = payloadALTA(datos)
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }

        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code not in [200, 201]:
            logging.error(f"Alta ERROR para ingresante ID BD: {ingresante_id_db} | {response.text}")
            actualizar_estado(ingresante_id_db, "estado_alta", "Error", session)
            return {"error": "API error", "status": "failed"}

        # 4. Si PeopleForce respondió bien
        logging.info(f"Alta OK para ingresante ID DB: {ingresante_id_db} | response: {response.json()}")
        actualizar_estado(ingresante_id_db, "estado_alta", "Procesada", session)

        notificar_rrhh(
            payload.get("first_name", ""),
            payload.get("last_name", ""),
            payload.get("personal_email", ""),
            "alta"
        )

        # 5. Obtener employee_id de la respuesta
        employee_id = response.json().get("id")
        if employee_id:
            actualizar_estado(ingresante_id_db, "id_pf", employee_id, session)

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
                time.sleep(5)  # Esperar 5 segundos antes de procesar documentos

                logging.info(f"Llamando a procesar_documento para ingresante ID BD: {ingresante_id_db}")
                resultado_doc = procesar_documento(payload_doc, session)

                if resultado_doc.get("status_code") in [200, 201]:
                    logging.info(f"Documento procesado correctamente para ingresante ID BD: {ingresante_id_db}")
                    return {"status": "success", "message": "Persona agregada y documento subido."}
                else:
                    logging.error(f"Error al procesar documento para ID DB: {ingresante_id_db}: {resultado_doc}")
                    return {
                        "status": "failed",
                        "message": "Persona agregada pero documento falló.",
                        "error": resultado_doc.get("error")
                    }

            except requests.exceptions.RequestException as e:
                logging.error(f"Excepción al procesar documento para ID BD: {ingresante_id_db}: {str(e)}")
                return {
                    "status": "failed",
                    "message": "Persona agregada pero documento falló.",
                    "error": str(e)
                }

        else:
            return {"message": "Alta OK pero no se recibió ID de empleado", "status": "partial_success"}

    except requests.exceptions.RequestException as e:
        logging.error(f"Excepción al conectar con PeopleForce para ID DB: {ingresante_id_db} | {str(e)}")
        actualizar_estado(ingresante_id_db, "estado_alta", "Error", session)
        return {"error": "Conexión con PeopleForce fallida", "status": "failed", "status_code": 500}

    except Exception as e:
        logging.exception(f"Excepción general para ingresante ID BD: {ingresante_id_db}")
        actualizar_estado(ingresante_id_db, "estado_alta", "Error", session)
        return {"error": "Error interno", "status": "failed", "status_code": 500}
