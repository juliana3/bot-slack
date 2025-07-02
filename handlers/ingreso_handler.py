import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("PEOPLEFORCE_URL")
API_TOKEN = os.getenv("PEOPLEFORCE_TOKEN")

def procesar_ingreso(datos):
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
            return {
                "mensaje": "Alta exitosa en PeopleForce",
                "status_code": response.status_code
            }
        else:
            return {
                "error": "Error en la API de PeopleForce",
                "detalle": response.text,
                "status_code": 500
            }

    except Exception as e:
        return {
            "error": "Error de conexión con PeopleForce",
            "detalle": str(e),
            "status_code": 500
        }
