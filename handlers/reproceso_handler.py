import gspread, os, requests, time, logging

from handlers.ingreso_handler import procesar_ingreso
from handlers.documento_handler import procesar_documento
from services.sheets_utils import SHEET, get_col, update_col
from services.toPDF_utils import armar_pdf_dni







def reprocesar_filas():
    filas = SHEET.get_all_values()
    columnas = get_col(SHEET)

    f_procesadas = 0
    f_errores = 0

    for index, fila in enumerate(filas[1:], start=2):
        estado = fila[columnas["Estado"] - 1].strip().lower() if fila[columnas["Estado"] - 1] else ""
        estado_pdf = fila[columnas["Estado PDF"] - 1].strip().lower() if fila[columnas["Estado PDF"] - 1] else ""
        

        datos_alta = { #estos son los datos para el ALTA
            "fila" : index,
            "nombre" : fila[1],
            "email" : fila[2],
        }

        datos_doc ={
            "fila" : index,
            "nombre": fila[1],
            "email": fila[2],
            "dni_f":fila[3],
            "dni_d": fila[4],
            "employee_id" : fila[6]
        }

        #si la fila ya fue procesada solo se verifica que este el pdf subido

        if estado == "procesada":

            if estado_pdf == "subido":
                logging.info(f"Fila {index} ya procesada y PDF subido")
                f_procesadas += 1
            elif estado_pdf in ["error", ""]:
                logging.info(f"Fila {index} ya procesada pero PDF no subido, se intenta subir")
                resultado_doc = procesar_documento(datos_doc)
                
                if resultado_doc.get("status_code") in [200,201]:
                    f_procesadas += 1
                else:
                    f_errores += 1      
        elif estado in ["error", ""]: # si la fila este en error o vacia, se reintenta el alta en PF

            resultado = procesar_ingreso(datos_alta)
            if resultado.get("status_code") in [200,201]:
                f_procesadas += 1
            else:
                f_errores += 1

        time.sleep(1)  # pausa mínima para no saturar PeopleForce

    return {
        "mensaje"      : "Reproceso finalizado",
        "procesadas_ok": f_procesadas,
        "errores"      : f_errores
    }