import logging
import io
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from services.drive_utils import descargar_imagen_desde_drive

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def armar_pdf_dni(nombre_persona,id_dni_frente, id_dni_dorso):
    """
    Descarga imágenes de DNI desde google drive y las usa para crear un PDF."""

    try:
        logging.info("armar_pdf_dni: Descargando imagen de DNI frente desde Google Drive.")
        # Usar la función de drive_utils para descargar la imagen
        img_frente = descargar_imagen_desde_drive(id_dni_frente)
        if img_frente is None:
            logging.error(f"armar_pdf_dni: No se pudo descargar la imagen del DNI frente para {nombre_persona}.")
            return None
        img_frente = Image.open(io.BytesIO(img_frente))

        logging.info(f"armar_pdf_dni: Descargando imagen de DNI dorso desde Google Drive.")
        # Usar la función de drive_utils para descargar la imagen
        img_dorso = descargar_imagen_desde_drive(id_dni_dorso)
        if img_dorso is None:
            logging.error(f"armar_pdf_dni: No se pudo descargar la imagen del DNI dorso para {nombre_persona}.")
            return None
        img_dorso = Image.open(io.BytesIO(img_dorso))

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
        logging.info(f"PDF generado correctamente para {nombre_persona}.")
        return buffer.getvalue()

    except Exception as e:
        logging.error(f"armar_pdf_dni: Excepción inesperada al procesar DNI para {nombre_persona}: {e}", exc_info=True)
        return None

