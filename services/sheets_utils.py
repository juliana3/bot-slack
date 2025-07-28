import gspread
from google.oauth2 import service_account

#configuracion del acceso a Google Sheets
SCOPE  = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
CREDS  = service_account.Credentials.from_service_account_file("chatbot-people-466623-1ec1f3039c87.json",scopes=SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET  = CLIENT.open("Formulario_PF").sheet1

#funcion que devuelve un diccionario con los nombres de las columnas y sus indices
def get_col(sheet = SHEET):
    headers = sheet.row_values(1)
    return {h.strip(): i + 1 for i, h in enumerate(headers)}

#funcion que actualiza el contenido de una columna seleccionada por su nombre
def update_col(fila, nombre_columna, valor, sheet = SHEET):
    columnas = get_col(sheet)
    col = columnas[nombre_columna]
    if col:
        sheet.update_cell(fila, col, valor)
    else:
        raise ValueError(f"Columna '{nombre_columna}' no encontrada en la hoja.")