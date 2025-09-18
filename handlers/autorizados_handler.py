#aca esta la logica para procesar solo a los autorizados
import logging
from services.db_operations import obtener_id_por_dni, actualizar_columna, obtener_ingresante_por_id
from handlers.ingreso_handler import procesar_ingreso
"""
    crea carpeta en drive
    sube imagens
    manda a people force
    genera pdf y lo sube
    
"""

# se reciben los datos del post con autorizaion + dni
#se busca a la perdona ór dni
#se cambia el status por AUTORIZZADA
#se llama a ingreso_handler ccon los datos

def procesar_autorizados(autorizacion, dni_ingresante):
    if not dni_ingresante:
        logging.error("Se intentó procesar un ingresante sin DNI.")
        return {"error": "El DNI del ingresante no puede estar vacío."}, 400
    
    try:

        id_autorizado = obtener_id_por_dni(dni_ingresante)

        if not id_autorizado:
            logging.warning(f"Ingresante con DNI {dni_ingresante} no encontrado en la base de datos.")
            return {"error": f"Ingresante con DNI {dni_ingresante} no encontrado"}, 404

        #cambiamos las columnas
        if str(autorizacion).upper() in ["TRUE", "VERDADERO"]:
            actualizar_columna(id_autorizado,"onboarding_status", "Autorizada")
            actualizar_columna(id_autorizado, "pdf_status", "Autorizada")

        datos_autorizado = obtener_ingresante_por_id(id_autorizado)

        if not datos_autorizado:
            logging.error(f"No se pudieron obtener los datos para el ID {id_autorizado}.")
            return {"error": f"Ingresante con DNI {dni_ingresante} no encontrado"}, 404

        if datos_autorizado['onboarding_status'] == "Autorizada":
            logging.info(f"Llamando a procesar_ingreso para el ID {id_autorizado}")
            resultado_autorizados = procesar_ingreso(datos_autorizado)

            status = resultado_autorizados.get("status")
            if status == "success":
                return resultado_autorizados, 200
            elif status == "partial_success":
                return resultado_autorizados, 200 
            elif status == "failed":
                return resultado_autorizados, 500 
            else:
                # Caso de un status inesperado
                logging.error(f"Estado de resultado inesperado de procesar_ingreso: {status}")
                return {"error": "Error interno del servidor"}, 500

        # Si el status no es 'Autorizada'
        return {"message": "El ingresante no ha sido autorizado para el procesamiento."}, 200
    
    except Exception as e:
        # Captura cualquier otra excepción no prevista
        logging.error(f"Excepción inesperada en procesar_autorizados: {e}", exc_info=True)
        return {"error": "Error interno del servidor. Por favor, intente de nuevo más tarde."}, 500

    


