import logging


from services.pf_utils import subir_documento
from services.toPDF_utils import armar_pdf_dni
from services.slack_utils import notificar_rrhh
from services.sheets_utils import SHEET, get_col, update_col




def procesar_documento(datos):
    fila = datos["fila"]
   # Armar el PDF
    pdf_dni = armar_pdf_dni(datos["nombre"], datos["dni_f"], datos["dni_d"])

    if not pdf_dni:
        logging.error("No se pudo generar el pdf para %s", datos["nombre"])
        update_col(fila, "Estado PDF", "Error")
        return {"error": "Falló la generación del PDF", "status_code": 500}
    
    #subir el documento a people force
    subida= subir_documento(datos["employee_id"], pdf_dni, f"{datos['nombre']}_DNI.pdf")
    if subida.get("status_code") in [200,201] :
        logging.info("PDF de %s subido correctamente a PeopleForce", datos["nombre"])
        # Notificar por Slack
        notificar_rrhh(datos["nombre"],datos["email"],"documento")

        #Actualizar sheets
        update_col(fila, "Estado PDF", "Subido")
        return {"mensaje": "Documento subido con éxito", "status_code": 200}
    else:
        logging.error("Falló la subida del PDF de %s a PeopleForce", datos["nombre"])

        #modificar sheets
        update_col(fila, "Estado PDF", "Error")
        return {"error": "Falló la subida a PeopleForce", "status_code": 502}


