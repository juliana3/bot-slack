import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-2.5-pro")

def responder_con_gemini(mensaje_usuario):
    try:
        respuesta = model.generate_content(mensaje_usuario)
        return respuesta.text
    except Exception as e:
        return f"Error al generar respuesta: {e}"
