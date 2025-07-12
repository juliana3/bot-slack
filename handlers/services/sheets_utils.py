import gspread
from oauth2client.service_account import ServiceAccountCredentials

#configuraciondel acceso a Google Sheets
SCOPE  = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
CREDS  = ServiceAccountCredentials.from_json_keyfile_name("prototipoform-07973d29cfea.json", SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET  = CLIENT.open("formularioPrototipo").sheet1

#funcion que devuelve un diccionario con los nombres de las columnas y sus indices
def get_col(sheet = SHEET):
    headers = sheet.row_values(1)
    return {h.strip(): i + 1 for i, h in enumerate(headers)}

#funcion que actualiza el contenido de una columna seleccionada por su nombre
def update_col(fila, nombre_columna, valor, sheet = SHEET):
    columnas = get_col(sheet)
    col = columnas.get(nombre_columna)
    if col:
        sheet.update_cell(fila, col, valor)
    else:
        raise ValueError(f"Columna '{nombre_columna}' no encontrada en la hoja.")