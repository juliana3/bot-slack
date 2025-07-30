import logging
import requests
import io
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from services.s3_utils import descargar_archivo_desde_s3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def armar_pdf_dni(nombre_persona, bucket_name, object_key_dni_frente, object_key_dni_dorso):
    """
    Descarga imágenes de DNI desde un bucket de S3 usando sus object_key,
    y las usa para crear un PDF.

    Args:
        nombre_persona (str): Nombre de la persona para fines de logging.
        bucket_name (str): Nombre del bucket de S3 donde se encuentran las imágenes.
        object_key_dni_frente (str): Clave del objeto (ruta) de la imagen del DNI frente en S3.
        object_key_dni_dorso (str): Clave del objeto (ruta) de la imagen del DNI dorso en S3.

    Returns:
        bytes: Contenido binario del PDF generado, o None si falla.
    """
    try:
        logging.info(f"armar_pdf_dni: Descargando imagen de DNI frente (object_key: {object_key_dni_frente}) desde S3.")
        # Usar la función de s3_utils para descargar la imagen
        contenido_frente = descargar_archivo_desde_s3(bucket_name, object_key_dni_frente)
        if contenido_frente is None:
            logging.error(f"armar_pdf_dni: No se pudo descargar la imagen del DNI frente para {nombre_persona}.")
            return None
        img_frente = Image.open(io.BytesIO(contenido_frente))

        logging.info(f"armar_pdf_dni: Descargando imagen de DNI dorso (object_key: {object_key_dni_dorso}) desde S3.")
        # Usar la función de s3_utils para descargar la imagen
        contenido_dorso = descargar_archivo_desde_s3(bucket_name, object_key_dni_dorso)
        if contenido_dorso is None:
            logging.error(f"armar_pdf_dni: No se pudo descargar la imagen del DNI dorso para {nombre_persona}.")
            return None
        img_dorso = Image.open(io.BytesIO(contenido_dorso))

        # Crear el PDF
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        
        # Ajustar tamaño y posición de las imágenes en el PDF
        img_width, img_height = 400, 300 
        
        # DNI Frente
        p.drawImage(ImageReader(img_frente), 50, A4[1] - 50 - img_height - 10, width=img_width, height=img_height)

        # DNI Dorso
        p.drawImage(ImageReader(img_dorso), 50, A4[1] - 50 - (2 * img_height) - 20, width=img_width, height=img_height)
        
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer.getvalue()

    except Exception as e:
        logging.error(f"armar_pdf_dni: Excepción inesperada al procesar DNI para {nombre_persona}: {e}", exc_info=True)
        return None

