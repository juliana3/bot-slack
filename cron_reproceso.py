import schedule
import time
import requests
import logging

from services.db_operations import eliminar_no_autorizados
from services.drive_utils import eliminar_archivos
from services.sheets_utils import eliminar_filas_no_autorizadas

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

REPROCESO_URL = "http://localhost:4000/reprocesar_errores"

def ejecutar_reproceso():
    #llama al endpoint de nuestra api
    try:
        logging.info("Ejecutando reproceso automatico de errores")
        response = requests.get(REPROCESO_URL)
        if response.status_code == 200:
            logging.info("Reproceso completado exitosamente %s", response.json())
        else:
            logging.warning(f"Error al reprocesar: %s", response.status_code)
    except Exception as e:
        logging.error("Error al ejecutar reproceso automatico: %s", e)

def ejecutar_limpieza_db():
    #ejecuta la limpieza de registros viejos y no autorizados en la bbdd
    logging.info("Iniciando tarea de limpieza de base de datos...")
    eliminar_no_autorizados()

def ejecutar_limpieza_sheets():
    #ejecuta la limpieza de filas viejas y no autorizadas en sheets
    logging.info("Iniciando tarea de limpieza de Google Sheets...")
    eliminar_filas_no_autorizadas()

def ejecutar_limpieza_drive():
    #ejecuta la limpieza de archivos viejos en drive
    logging.info("Iniciando tarea de limpieza de Google Drive...")
    eliminar_archivos()



#PLANIFICACION DE LAS TAREAS

"""reproceso"""
schedule.every(6).hours.do(ejecutar_reproceso)
#schedule.every(5).minutes.do(ejecutar_reproceso)

"""Limpiezas"""
schedule.every().sunday.at("02:00").do(ejecutar_limpieza_db)
schedule.every().sunday.at("02:05").do(ejecutar_limpieza_sheets)
schedule.every().sunday.at("02:10").do(ejecutar_limpieza_drive)






while True:
    try:
        schedule.run_pending()
    except Exception as e:
        logging.error(f"Error en el bucle principal de schedule: {e}", exc_info=True)

    time.sleep(1)