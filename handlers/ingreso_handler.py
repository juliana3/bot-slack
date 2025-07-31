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
        # Extraer datos de imagen si hace falta
        dni_frente_s3 = datos.get("dni-frente", "")
        dni_dorso_s3 = datos.get("dni-dorso", "")

        # Guardar en la base de datos
        logging.info("Intentando guardar datos en PostgreSQL...")
        ingresante_id_db = guardar_ingresante(datos, session)

        if not ingresante_id_db:
            logging.error("Falló la escritura en PostgreSQL.")
            return {
                "error": "Error al guardar datos en la base de datos",
                "status": "failed",
                "status_code": 500
            }

        logging.info(f"Datos guardados con éxito. ID: {ingresante_id_db}")
        return {"status": "success", "message": "Persona agregada correctamente", "id": ingresante_id_db}

    except Exception as e:
        logging.exception(f"Error general al procesar ingreso: {str(e)}")
        return {"error": "Error interno", "status": "failed", "status_code": 500}
