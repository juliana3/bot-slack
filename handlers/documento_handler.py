import logging



from services.pf_utils import subir_documento
from services.toPDF_utils import armar_pdf_dni
from services.slack_utils import notificar_rrhh
from services.db_operations import actualizar_estado



def procesar_documento(datos):
    logging.info(f"procesar_documento: Iniciando procesamiento para ID BD: {datos.get('document_id_db')}")
    
    document_id_db = datos.get("document_id_db")

    if document_id_db is None:
        logging.error("procesar_documento: 'document_id_db' no recibido en los datos.")
        return {"error": "'document_id_db' es un campo requerido", "status_code": 400}

    nombre = datos.get("nombre")
    apellido = datos.get("apellido")
    email = datos.get("email")
    dni_f = datos.get("dni_f")
    dni_d = datos.get("dni_d")
    employee_id = datos.get("employee_id")
    
    try:
        logging.info(f"procesar_documento: Intentando armar PDF para {nombre} {apellido}")
        # Armar el PDF
        pdf_dni = armar_pdf_dni(nombre,"dni-ingresantes-prueba", dni_f, dni_d)

        if not pdf_dni:
            logging.error(f"No se pudo generar el pdf para {nombre} {apellido}")
            actualizar_estado(document_id_db, "estado_pdf", "Error")
            return {"error": "Falló la generación del PDF", "status_code": 500}
        logging.info(f"PDF de {nombre} {apellido} generado correctamente")

        #subir el documento a people force
        subida= subir_documento(employee_id, pdf_dni, f"{nombre}_{apellido}_DNI.pdf")
        if subida.get("status_code") in [200,201] :
            logging.info("PDF de %s subido correctamente a PeopleForce", nombre)

            # Notificar por Slack
            notificar_rrhh(nombre, apellido,email,"documento")

            #Actualizar sheets
            actualizar_estado(document_id_db,"estado_pdf", "Subido")
            return {"mensaje": "Documento subido con éxito", "status_code": 200}
        else:
            logging.error("Falló la subida del PDF de %s a PeopleForce", nombre)

            #modificar sheets
            actualizar_estado(document_id_db,"estado_pdf", "Error")
            return {"error": "Falló la subida a PeopleForce", "status_code": 502}
    except Exception as e:
        logging.error(f"procesar_documento: Excepción inesperada al procesar documento para ID BD: {document_id_db}: {str(e)}", exc_info=True)

        actualizar_estado(document_id_db,"estado_pdf", "Error")
        return {"error": f"Excepción en el procesamiento del documento: {str(e)}", "status_code": 500}




    

