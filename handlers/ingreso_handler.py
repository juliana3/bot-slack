import os
import requests
from dotenv import load_dotenv
import logging

import gspread, os, requests, time
from oauth2client.service_account import ServiceAccountCredentials


load_dotenv()

SCOPE  = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
CREDS  = ServiceAccountCredentials.from_json_keyfile_name("prototipoform-07973d29cfea.json", SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET  = CLIENT.open("formularioPrototipo").sheet1
COL_ESTADO = 4  # Columna donde se guarda el estado de procesamiento



API_URL = "http://localhost:3000/agregar_persona"
API_TOKEN = os.getenv("PEOPLEFORCE_TOKEN")


def procesar_ingreso(datos):

    fila = datos["fila"]

    # Armar payload
    payload = {
        "name": datos["nombre"],
        "email": datos["email"]
        #despues garegar el resto de datos
    }

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            logging.info("Alta OK – fila %s | response: %s", fila, response.json())
            SHEET.update_cell(fila, COL_ESTADO, "Procesada")
            return {"mensaje": "Alta OK", "status_code": response.status_code}
        else:
            logging.error("Alta ERROR – fila %s | %s", fila, response.text)
            SHEET.update_cell(fila, COL_ESTADO, "Error")
            return {"error": "API error", "status_code": 500}

    except Exception as e:
        logging.error("Excepción – fila %s | %s", fila, str(e))
        SHEET.update_cell(fila, COL_ESTADO, "Error")
        return {"error": "Conexión fallida", "status_code": 500}
