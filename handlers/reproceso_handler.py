import gspread, os, requests, time
from handlers.ingreso_handler import procesar_ingreso
from services.sheets_utils import SHEET, get_col
from services.correo_utils import verificar_y_enviar_dni





def reprocesar_filas():
    filas = SHEET.get_all_values()
    f_procesadas = 0
    f_errores = 0

    columnas = get_col(SHEET)

    for index, fila in enumerate(filas[1:], start=2):
        estado = fila[columnas["Estado"] - 1].strip().lower() if fila[columnas["Estado"] - 1] else ""
        correo_enviado = fila[columnas["Correo enviado"] - 1].strip().lower() if fila[columnas["Correo enviado"] - 1] else ""

        datos = {
            "fila" : index,
            "nombre" : fila[1],
            "email" : fila[2],
        }

        if estado == "procesada" and correo_enviado != "si":
            verificar_y_enviar_dni(index)
            f_procesadas += 1
        elif estado in ["error", ""]:

            resultado = procesar_ingreso(datos)
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