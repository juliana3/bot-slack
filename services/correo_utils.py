import requests
import logging 
from services.sheets_utils import SHEET, get_col

def verificar_y_enviar_dni(fila):
    columnas = get_col(SHEET)
    estado = SHEET.cell(fila, columnas["Estado"]).value  or ""
    correo_enviado = SHEET.cell(fila, columnas["Correo enviado"]).value or ""

    estado = estado.strip().lower()
    correo_enviado = correo_enviado.strip().lower()

    if estado == "procesada" and correo_enviado != "si":
        logging.info(f"Enviando solicitud de correo con foto para fila {fila}")
        try:
            response = requests.post(
                "https://script.google.com/macros/s/AKfycbxcDYaMZzQbEXh37fQe12qQgoJaxtwEbpNx5dm6vzge8Nua3HvWR0PQYGSEgwaSBofjfg/exec",
                json={"fila": fila}
            )
            if response.status_code == 200:
                if "Correo enviado" in response.text:
                    logging.info(f"Confirmacion desde APPS SCRIPT: Correo enviado correctamente para fila {fila}")
                else:
                    logging.warning(f"Respuesta inesperada desde Apps Script: {response.text}")
            else:
                logging.warning(f"Fallo al solicitar envío desde APPS SCRIPT. Status: {response.status_code}")
        except Exception as e:
            logging.error(f"Error al contactar Apps Script: {e}")