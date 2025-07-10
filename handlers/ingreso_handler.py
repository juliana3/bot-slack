import os
import requests
from dotenv import load_dotenv
import logging

import gspread, os, requests, time
from oauth2client.service_account import ServiceAccountCredentials


load_dotenv()

#Configuracion del acceso a Google Sheets
SCOPE  = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
CREDS  = ServiceAccountCredentials.from_json_keyfile_name("prototipoform-07973d29cfea.json", SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET  = CLIENT.open("formularioPrototipo").sheet1
COL_ESTADO = 5  # Columna donde se guarda el estado de procesamiento


#Definicion de variables
SLACK_BOT_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")  #AHORA: es el id del canal test 

API_URL = "http://localhost:3000/agregar_persona" #esto se cambia por os.getenv("PEOPLE_FORCE_URL")
API_TOKEN = os.getenv("PEOPLE_FORCE_TOKEN")


def notificar_rrhh(nombre,email):
    mensaje = f"Alta completada para: *{nombre}* (`{email}`) en PeopleForce."

    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-type": "application/json"
    }

    data = {
        "channel": SLACK_CHANNEL_ID,
        "text": mensaje
    }

    try:
        response = requests.post("https://slack.com/api/chat.postMessage", headers=headers, json=data)
        try:
            body = response.json()
        except Exception as e:
            logging.error(f"No se pudo parsear respuesta de Slack: {str(e)}")
            body = {}

        if response.status_code != 200 or not response.json().get("ok"):
            logging.warning(f"No se pudo enviar notificación Slack: {response.text}")

        else:
            logging.info("Notificación enviada a Slack")

    except Exception as e:
        logging.error(f"Fallo al enviar mensaje a Slack: {str(e)}")
        return False


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

            #Notifica a rrhh por slack
            notificar_rrhh(datos["nombre"], datos["email"])

            return {"mensaje": "Alta OK", "status_code": response.status_code}
        else:
            logging.error("Alta ERROR – fila %s | %s", fila, response.text)
            SHEET.update_cell(fila, COL_ESTADO, "Error")
            return {"error": "API error", "status_code": 500}

    except Exception as e:
        logging.error("Excepción – fila %s | %s", fila, str(e))
        SHEET.update_cell(fila, COL_ESTADO, "Error")
        return {"error": "Conexión fallida", "status_code": 500}
