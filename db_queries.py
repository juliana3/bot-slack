import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime 
import gspread
from oauth2client.service_account import ServiceAccountCredentials


load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

model = genai.GenerativeModel("models/gemini-2.5-pro")

def responder_con_gemini(mensaje_usuario):
    try:
        datos = obtener_datos_sheets()
        contexto = armar_contexto_texto(datos)

        prompt = f"""
Respondé únicamente en base a la siguiente base de datos:

{contexto}

Pregunta del usuario: {mensaje_usuario}

Si la información no está presente en los datos, respondé: "No tengo esa información".
No inventes ni supongas datos.
"""

        respuesta = model.generate_content(prompt)
        return respuesta.text

    except Exception as e:
        return f"Error al generar respuesta: {e}"
  


def obtener_datos_sheets():
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = ServiceAccountCredentials.from_json_keyfile_name("prototipoform-07973d29cfea.json", scope) #JSON descargado desde google cloud
        client = gspread.authorize(creds)

        sheet = client.open("Form Responses 1").sheet1  #Nombre de la hoja de Sheets
        datos = sheet.get_all_records()
        return datos

    except Exception as e:
        return [{"Error": f"No se pudieron obtener datos del sheet: {e}"}]


def armar_contexto_texto(datos):
    contexto = "Base de datos disponible:\n"
    for fila in datos:
        fila_texto = ", ".join(f"{clave}: {valor}" for clave, valor in fila.items())
        contexto += f"- {fila_texto}\n"
    return contexto

