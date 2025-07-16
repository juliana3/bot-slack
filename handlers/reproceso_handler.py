import gspread, os, requests, time, logging

from handlers.ingreso_handler import procesar_ingreso
from services.sheets_utils import SHEET, get_col, update_col
from services.toPDF_utils import armar_pdf_dni
from services.subir_pdf_a_drive import subir_pdf_a_drive






def reprocesar_filas():
    filas = SHEET.get_all_values()
    columnas = get_col(SHEET)

    f_procesadas = 0
    f_errores = 0
    f_pdf_subidos = 0

    for index, fila in enumerate(filas[1:], start=2):
        estado = fila[columnas["Estado"] - 1].strip().lower() if fila[columnas["Estado"] - 1] else ""
        link_pdf = fila[columnas["PDF DNI"] - 1].strip().lower() if fila[columnas["PDF DNI"] - 1] else ""
        

        datos = {
            "fila" : index,
            "nombre" : fila[1],
            "email" : fila[2],
            "dni_f": fila[columnas["foto dni frente"] - 1],
            "dni_d":  fila[columnas["foto dni dorso"]  - 1]
        }

        #si la fila ya fue procesada solo se verifica que este el pdf subido

        if estado == "procesada":
            if not link_pdf:
                logging.info(f"Fila {index} procesada pero sin PDF. Intentando generar y subir...")
                pdf = armar_pdf_dni(datos["nombre"], datos["dni_f"], datos["dni_d"])

                if pdf:
                    link = subir_pdf_a_drive(datos["nombre"], pdf)

                    if link:
                        update_col(index, "PDF DNI", link)
                        f_pdf_subidos += 1
                        logging.info(f"PDF subido exitosamente en fila {index}")
                    else:
                        logging.warning(f"PDF generado pero no se pudo subir (fila {index})")
                else:
                    logging.warning(f"No se pudo generar el PDF (fila {index})")

            f_procesadas += 1
            continue

        elif estado in ["error", ""]: # si la fila este en error o vacia, se reintenta el alta en PF

            resultado = procesar_ingreso(datos)
            if resultado.get("status_code") in [200,201]:
                f_procesadas += 1
            else:
                f_errores += 1

        time.sleep(1)  # pausa mínima para no saturar PeopleForce

    return {
        "mensaje"      : "Reproceso finalizado",
        "procesadas_ok": f_procesadas,
        "errores"      : f_errores,
        "pdf_subidos"  : f_pdf_subidos
    }