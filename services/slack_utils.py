import os
import requests
from dotenv import load_dotenv
import logging

load_dotenv()

#Definicion de variables
SLACK_BOT_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")  #AHORA: es el id del canal test 

def notificar_rrhh(nombre, apellido,email, tipo):
    if tipo == "alta":
        mensaje = f"Alta exitosa para *{nombre} {apellido}* (`{email}`) en PeopleForce."
    elif tipo == "documento":
        mensaje = f"Documento cargado para: *{nombre} {apellido}* (`{email}`) en PeopleForce."
    

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
