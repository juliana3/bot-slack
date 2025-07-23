import gspread, os, requests, time, logging

from handlers.ingreso_handler import procesar_ingreso
from handlers.documento_handler import procesar_documento
from services.sheets_utils import SHEET, get_col, update_col
from services.toPDF_utils import armar_pdf_dni
from services.payload_utils import payloadALTA, payloadPDF







def reprocesar_filas():
    logging.info("Iniciando reproceso de fila_datas")

    #obtener todos los valores de la hoja de una sola vez
    filas = SHEET.get_all_values()
    columnas = get_col(SHEET) # obtener los encabezados de las columnas

    f_procesadas = 0
    f_errores = 0

    for index, fila_data in enumerate(filas[1:], start=2):
        #index es el numero de fila y fila_data es la lista de valores de esa fila

        logging.info(f"Procesando fila_data {index}: {fila_data}")

        #se obtiene Estado y Estado PDF de las filas ya cargadas
        estado = fila_data[columnas["Estado"] - 1].strip().lower() if fila_data[columnas["Estado"] - 1] else ""
        estado_pdf = fila_data[columnas["Estado PDF"] - 1].strip().lower() if fila_data[columnas["Estado PDF"] - 1] else ""
        

        datos_alta = payloadALTA(index, columnas, fila_data)
        datos_doc = payloadPDF(index, columnas, fila_data)

        #si la fila ya fue procesada solo se verifica que este el pdf subido

        if estado == "procesada":

            if estado_pdf == "subido":
                logging.info(f"fila {index} ya procesada y PDF subido")
                f_procesadas += 1
            elif estado_pdf in ["error", ""]:
                logging.info(f"fila {index} ya procesada pero PDF no subido, se intenta subir")
                resultado_doc = procesar_documento(datos_doc)
                
                if resultado_doc.get("status_code") in [200,201]:
                    logging.info(f"PDF de fila {index} subido correctamente")
                    f_procesadas += 1
                else:
                    logging.error(f"Error al subir PDF de fila {index}: {resultado_doc.get('mensaje', 'Error desconocido')}")
                    f_errores += 1      
        elif estado in ["error", ""]: # si Estado esta en error o vacia, se reintenta el alta en PF
            logging.info(f"Se reintenta alta de fila {index} en PeopleForce")

            resultado = procesar_ingreso(datos_alta, index)
            if resultado.get("status") == "success":
                logging.info(f"Fila {index} reprocesada correctamente")
                f_procesadas += 1

                #intentar subir PDF
                logging.info(f"Intentando subir PDF de fila {index}")
                resultado_doc = procesar_documento(datos_doc)

                if resultado_doc.get("status_code") in [200,201]:
                    logging.info(f"PDF de fila {index} subido correctamente")
                    f_procesadas += 1
                else:
                    logging.error(f"Error al subir PDF de fila {index}: {resultado_doc.get('mensaje', 'Error desconocido')}")
            else:
                logging.error(f"Error al reprocesar fila {index}: {resultado.get('mensaje', 'Error desconocido')}")
                f_errores += 1

        time.sleep(5)  # pausa mínima para no saturar PeopleForce

    logging.info(f"Reproceso finalizado. Filas reprocesadas OK: {f_procesadas}, Filas con errores: {f_errores}")
    return {
        "mensaje"      : "Reproceso finalizado",
        "procesadas_ok": f_procesadas,
        "errores"      : f_errores
    }