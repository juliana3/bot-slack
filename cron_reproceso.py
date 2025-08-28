import schedule
import time
import requests
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

FLASK_URL = "http://localhost:4000/reprocesar_errores"

def ejecutar_reproceso():
    try:
        logging.info("Ejecutando reproceso automatico de errores")
        response = requests.get(FLASK_URL)
        if response.status_code == 200:
            logging.info("Reproceso completado exitosamente %s", response.json())
        else:
            logging.warning(f"Error al reprosesar: %s", response.status_code)
    except Exception as e:
        logging.error("Error al ejecutar reproceso automatico: %s", e)


#ejecutar el reproceso cada 6 horas
#schedule.every(6).hours.do(ejecutar_reproceso)

#para prueba cada 2 minutos
schedule.every(2).minutes.do(ejecutar_reproceso)

while True:
    schedule.run_pending()
    time.sleep(1)