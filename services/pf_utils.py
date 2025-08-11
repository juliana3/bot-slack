import logging
import os 
import requests
from dotenv import load_dotenv





load_dotenv()

API_URL = os.getenv("PEOPLEFORCE_URL") 
API_TOKEN = os.getenv("PEOPLEFORCE_TOKEN")
folder_id = os.getenv("DOCUMENT_FOLDER_ID_PF")


def subir_documento(employee_id, pdf, file_name, titulo = "DNI"):
    try:
        url = f"{API_URL}/{employee_id}/documents"
        headers = {
            "Authorization" : f"Bearer {API_TOKEN}",
        }
        files = {
            "document_folder_id": (None, folder_id),
            "name": (None, titulo),
            "document": (file_name, pdf, "application/pdf")

        }

        response = requests.post(url, headers=headers, files=files)

        if response.status_code in [200,201]:
            logging.info("Nuevo documento subido correctamente en People force")
            return {"mensaje": "Documento cargado con exito", "status_code": response.status_code}
        else:
            logging.error(f"Error al subir PDF: {response.status_code} - {response.text}")
            return {"error" : "API error", "status_code": response.status_code}
    except Exception as e:
            logging.error(f"Excepción al subir PDF: {str(e)}")
            return {"error": "Conexión fallida", "status_code": 500}
    
