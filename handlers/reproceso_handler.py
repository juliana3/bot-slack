import gspread, os, requests, time
from oauth2client.service_account import ServiceAccountCredentials
from handlers.ingreso_handler import procesar_ingreso

# Configuración de Google Sheets
SCOPE  = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
CREDS  = ServiceAccountCredentials.from_json_keyfile_name("prototipoform-07973d29cfea.json", SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET  = CLIENT.open("formularioPrototipo").sheet1



def reprocesar_filas():
    filas = SHEET.get_all_values()
    f_procesadas = 0
    f_errores = 0

    for index, fila in enumerate(filas[1:], start=2):
        estado = fila[-1].strip().lower()

        if estado in ("error",""):
            datos = {
                "fila" : index,
                "nombre" : fila[1],
                "email" : fila[2],
            }

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