import datetime
import os
import logging
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from PIL import Image
import io

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s"
)

load_dotenv()

#carga de creddenciales
SERVICE_ACCOUNT_FILE = "chatbot-people-466623-1ec1f3039c87.json"
SCOPES = ['https://www.googleapis.com/auth/drive']
UNIDAD_COMPARTIDA_DRIVE = os.getenv("DRIVE_ID")
DNI_FOLDER_ID = os.getenv("DNI_DNI_FOLDER_ID") #esta es la carpeta DNIs
NO_AUTORIZADOS_DNI_FOLDER_ID = os.getenv("NO_AUTORIZADOS_DNI_FOLDER_ID")


def obtener_servicio_drive():
    #devuelve un objeto de servicio para interactuar con drive
    try:
        creds= service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes = SCOPES)
        service = build("drive", "v3", credentials=creds, cache_discovery=False)
        return service
    except Exception as e:
        logging.error(f"Error al obtener el servicio de GOOGLE DRIVE: {e}", exc_info=True)
        return None


def crear_carpeta(nombre_carpeta):
    #crea una carpeta en drive y retorna su id
    servicio_drive = obtener_servicio_drive()
    if not servicio_drive:
        return None
    
    file_metadata = {
        'name': nombre_carpeta,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [DNI_FOLDER_ID]  # DNI_FOLDER_ID es el ID de la carpeta principal 'DNIs'
    }

    try:
        archivo = servicio_drive.files().create(
            body=file_metadata, 
            fields='id',
            supportsAllDrives=True
        ).execute()
        carpeta_id = archivo.get('id')
        logging.info(f"Carpeta '{nombre_carpeta}' creada con ID: {carpeta_id}")
        return carpeta_id
    except Exception as e:
        logging.error(f"Error al crear carpeta {nombre_carpeta} en DRIVE: {e}", exc_info=True)
        return None



def subir_imagen_a_drive(archivo, nombre_archivo, carpeta_destino):
    #sube el archivo a la carpeta de drive y retorna el id
    servicio_drive = obtener_servicio_drive()
    if not servicio_drive:
        return None
    
    try:
        archivo.seek(0)
        img = Image.open(archivo)

        if img.mode in ("RGBA", "P"): #si viene una imagen con transparencia, convertir a rgb para eliminar la transparencia
            img = img.convert("RGB")

        buffer_temporal = io.BytesIO()
        img.save(buffer_temporal, format="JPEG")
        buffer_temporal.seek(0)

        #DEFINIR NOMBRE DEL ARCHIVO
        jpg_nombre_archivo = f"{os.path.splitext(nombre_archivo)[0]}.jpg"
        mime_type = "image/jpeg"

        #Guardamos las imagenes en la carpeta destino
        file_metadata = {
            'name': jpg_nombre_archivo,
            'parents': [carpeta_destino]
        }
        media = MediaIoBaseUpload(buffer_temporal, mimetype=mime_type)
        archivo = servicio_drive.files().create(
            body=file_metadata, 
            media_body=media, 
            fields = 'id',
            supportsAllDrives=True
        ).execute()

        id_archivo = archivo.get('id')
        logging.info(f"Archivo {jpg_nombre_archivo} subido correctamente a Google Drive con ID: {id_archivo}")
        return id_archivo
    except Exception as e:
        logging.error(f"Error al subir el archivo como JPG  a Drive: {e}", exc_info=True)
        return None
    





def descargar_imagen_desde_drive(id_imagen):
    #descarga las imagenes de drive usando su id

    servicio_drive = obtener_servicio_drive()
    if not servicio_drive:
        return None
    
    try:
        request = servicio_drive.files().get_media(fileId=id_imagen, supportsAllDrives=True)
        archivo = io.BytesIO()
        downloader = MediaIoBaseDownload(archivo, request)
        done = False

        while done is False:
            status,done = downloader.next_chunk()

        archivo.seek(0)
        logging.info(f"Archivo con ID {id_imagen} descargado correctamente desde Google Drive")
        return archivo.getvalue()
    except Exception as e:
        logging.error(f"Error al descargar el archivo con ID {id_imagen} desde Google Drive: {e}", exc_info=True)
        return None


   
def subir_pdf_a_drive(pdf, nombre_archivo, carpeta_destino):
    servicio_drive = obtener_servicio_drive()
    if not servicio_drive:
        return None
    
    try:
        pdf_buffer = io.BytesIO(pdf)

        file_metadata = {
            'name': nombre_archivo,
            'parents': [carpeta_destino]
        }
        media = MediaIoBaseUpload(pdf_buffer, mimetype='application/pdf')

        #subir el pdf a drive
        archivo = servicio_drive.files().create(
            body=file_metadata, 
            media_body = media, 
            fields = 'id',
            supportsAllDrives=True).execute()

        id_archivo = archivo.get('id')
        logging.info(f"Archivo PDF '{nombre_archivo}' subido correctamente a Google Drive con ID: {id_archivo}")
        return id_archivo
    except Exception as e:
        logging.error(f"Error al subir el archivo PDF a Google Drive: {e}", exc_info=True)
        return None


def mover_archivo(file_id, carpeta_destino_id):
    """
    Mueve un archivo de una carpeta a otra en una Unidad Compartida.
    """
    servicio_drive = obtener_servicio_drive()
    if not servicio_drive:
        return False

    try:
        #asumimos que la carpete de origen es No Autorizados
        carpeta_origen_id = os.getenv("NO_AUTORIZADOS_DNI_FOLDER_ID")

        servicio_drive.files().update(
            fileId=file_id,
            addParents=carpeta_destino_id,
            removeParents=carpeta_origen_id,
            supportsAllDrives=True
        ).execute()
        logging.info(f"Archivo {file_id} movido de {carpeta_origen_id} a {carpeta_destino_id}")
        return True
    except Exception as e:
        logging.error(f"Error al mover archivo {file_id}: {e}", exc_info=True)
        return False


def eliminar_archivos():
    #elimina archivos de la carpeta de no autorizados que tienen mas de 7 dias

    servicio_drive = obtener_servicio_drive()
    if not servicio_drive:
        return False
    
    try:
        carpeta_no_autorizados_id = os.getenv("NO_AUTORIZADOS_DNI_FOLDER_ID")

        #busca archivos en la carpeta
        query = f"'{carpeta_no_autorizados_id}' in parents and trashed=false"
        results = servicio_drive.files().list(
            q=query,
            fields="files(id, name, createdTime)",
            supportsAllDrives=True
        ).execute()

        archivos = results.get("files", [])
        if not archivos:
            logging.info("No se encontraron archivos para eliminar en la carpeta temporal.")
            return 
        
        #fecha limite de 7 dias
        fecha_limite = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)
        archivos_eliminados = 0 

        for archivo in archivos:
            created_time_str = archivo.get('createdTime')
            created_time = datetime.datetime.fromisoformat(created_time_str.replace("Z", "+00:00"))
            
            if created_time < fecha_limite:
                try:
                    servicio_drive.files().delete(fileId=archivo.get('id'), supportsAllDrives=True).execute()
                    logging.info(f"Archivo '{archivo.get('name')}' eliminado por antigüedad.")
                    archivos_eliminados += 1
                except Exception as e:
                    logging.error(f"Error al eliminar el archivo {archivo.get('name')}: {e}")
        
        logging.info(f"Proceso de limpieza finalizado. Se eliminaron {archivos_eliminados} archivos.")

    except Exception as e:
        logging.error(f"Error en el proceso de limpieza de archivos en Drive: {e}", exc_info=True)


