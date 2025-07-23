import re
import io
import os
import logging
from fpdf import FPDF
from PIL import Image
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
CREDENTIALS_FILE = "chatbot-people-466623-1ec1f3039c87.json"

creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)

def extraer_id_drive(link): #devuelve un string con el ID del archivo de Google Drive
    """Extrae el ID de archivo desde un link de Google Drive."""
    patrones = [
        r"/d/([a-zA-Z0-9_-]{25,})",   # formato /d/ID/view
        r"id=([a-zA-Z0-9_-]{25,})"    # formato id=ID
    ]
    for patron in patrones:
        match = re.search(patron, link)
        if match:
            return match.group(1)
    return None

def descargar_imagen_drive(file_id, creds): #Devuelve los bytes de una imagen de Google Drive
    """Descarga una imagen desde Drive como bytes."""
    try:
        servicio = build("drive", "v3", credentials=creds)
        request = servicio.files().get_media(fileId=file_id)
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        buffer.seek(0)
        return buffer.read()
    except Exception as e:
        logging.error(f"Error al descargar imagen de Drive ({file_id}): {str(e)}")
        return None



def armar_pdf_dni(link1, link2):
    """Función principal: recibe links, descarga imágenes y arma el PDF."""

    id1 = extraer_id_drive(link1)
    id2 = extraer_id_drive(link2)

    if not id1 or not id2:
        logging.error("No se pudieron extraer los IDs de las imágenes")
        return None

    img1 = descargar_imagen_drive(id1, creds)
    img2 = descargar_imagen_drive(id2, creds)

    if not img1 or not img2:
        logging.error("Error al descargar una o ambas imágenes")
        return None

    try:
        pdf = FPDF()
        pdf.set_auto_page_break(0)

        for index, imagen in enumerate([img1, img2]):
            pdf.add_page()
            temp_path = f"temp_dni_{index}.jpg"

            #convertimos a jpg si es necesario
            Image.open(io.BytesIO(imagen)).convert("RGB").save(temp_path, "JPEG")

            #insertar en el PDF
            pdf.image(temp_path, x=10, y=10, w= 180)

            #borramos el archivo temporal
            os.remove(temp_path)
        buffer = io.BytesIO(pdf.output(dest="S").encode("latin1"))
        return buffer.getvalue()

    except Exception as e:
        logging.error(f"Error al armar el PDF: {str(e)}")
        return None
