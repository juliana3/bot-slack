from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from services.sheets_utils import update_col
import io
import logging

# Configuración
SCOPES = ["https://www.googleapis.com/auth/drive"]
CREDENTIALS_FILE = "prototipoform-07973d29cfea.json"
FOLDER_ID = "1ml8dvJ_BH1xHrhmv2ZkikgzJH6uw4FmL" # ID de la carpeta en Google Drive donde se guardarán los PDFs

def subir_pdf_a_drive(nombre, pdf_bytes):
    try:
        creds = Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=SCOPES
        )
        servicio = build("drive", "v3", credentials=creds)

        # Preparar archivo
        archivo = {
            "name": f"DNI - {nombre}.pdf",
            "parents": [FOLDER_ID],
            "mimeType": "application/pdf"
        }

        media = MediaIoBaseUpload(io.BytesIO(pdf_bytes), mimetype="application/pdf")

        # Subir
        archivo_creado = servicio.files().create(
            body=archivo,
            media_body=media,
            fields="id, webViewLink"
        ).execute()

        logging.info(f"PDF subido a Drive: {archivo_creado['webViewLink']}")
        return archivo_creado["webViewLink"]

    except Exception as e:
        logging.error(f"Error al subir PDF a Drive: {str(e)}")
        return None


