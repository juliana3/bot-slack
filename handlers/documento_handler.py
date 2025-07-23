import logging


from services.pf_utils import subir_documento
from services.toPDF_utils import armar_pdf_dni
from services.slack_utils import notificar_rrhh
from services.sheets_utils import SHEET, get_col, update_col




def procesar_documento(datos):
    logging.info(f"procesar_documento: Iniciando procesamiento para fila {datos.get('fila')}")
    
    fila = datos["fila"]

    print("Link frente:", datos.get("dni_f"))
    print("Link dorso:", datos.get("dni_d"))

    {"error": "Falló la generación del PDF", "status_code": 500}
    
    try:
        logging.info(f"procesar_documento: Intentando armar PDF para {datos['nombre']}")
        # Armar el PDF
        pdf_dni = armar_pdf_dni(datos["dni_f"], datos["dni_d"])

        if not pdf_dni:
            logging.error("No se pudo generar el pdf para %s", datos["nombre"])
            update_col(fila, "Estado PDF", "Error")
            return {"error": "Falló la generación del PDF", "status_code": 500}
        logging.info("PDF de %s generado correctamente", datos["nombre"])

        #subir el documento a people force
        subida= subir_documento(datos["employee_id"], pdf_dni, f"{datos['nombre']}_{datos['apellido']}_DNI.pdf")
        if subida.get("status_code") in [200,201] :
            logging.info("PDF de %s subido correctamente a PeopleForce", datos["nombre"])

            # Notificar por Slack
            notificar_rrhh(datos["nombre"], datos["apellido"],datos["email"],"documento")

            #Actualizar sheets
            update_col(fila, "Estado PDF", "Subido")
            return {"mensaje": "Documento subido con éxito", "status_code": 200}
        else:
            logging.error("Falló la subida del PDF de %s a PeopleForce", datos["nombre"])

            #modificar sheets
            update_col(fila, "Estado PDF", "Error")
            return {"error": "Falló la subida a PeopleForce", "status_code": 502}
    except Exception as e:
        logging.error(f"procesar_documento: Excepción inesperada al procesar documento para fila {fila}: {str(e)}", exc_info=True)

        update_col(fila, "Estado PDF", "Error")
        return {"error": f"Excepción en el procesamiento del documento: {str(e)}", "status_code": 500}




    

