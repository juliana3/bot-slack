import datetime
import logging
import re
import gspread
from google.oauth2 import service_account

#configuracion del acceso a Google Sheets
SCOPE  = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
CREDS  = service_account.Credentials.from_service_account_file("chatbot-people-466623-1ec1f3039c87.json",scopes=SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET  = CLIENT.open("Respaldo-ingresos").sheet1

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

FIELD_MAPPING = { #las claves son los nombres de las columnas en sheets y los valores los nombres de las variables que vienen del formulario
    "Nombre": "nombre",
    "Apellido": "apellido",
    "DNI": "dni",
    "Email": "email",
    "Celular": "celular",
    "Domicilio": "domicilio",
    "Localidad" : "localidad",
    "Fecha de Nacimiento": "fecha_nacimiento", 
    "Nivel educativo terciario": "nivel_terciario", 
    "Nivel educativo universitario": "nivel_universitario", 
    "Tipo contrato": "tipo_contrato", 
    "CBU": "cbu",
    "ALIAS": "alias",
    "CUIL": "cuil",
    "Banco": "banco",
    "Numero de cuenta": "cuenta", 
    "Bank name": "bank_name", 
    "Bank address": "bank_address", 
    "Swift code": "swift_code", 
    "Account holder": "account_holder", 
    "Account number": "account_number", 
    "Routing number": "routing_number", 
    "Tipo de cuenta": "tipo_cuenta", 
    "Zip code": "zip_code", 
    "Obra social": "obra_social", 
    "Codigo AFIP": "codigo_afip", 
    "DNI frente": "dni_frente", 
    "DNI dorso": "dni_dorso" 
}

def cargar_sheets(data_json):
    """
    Añade una nueva fila a Google Sheets con los datos del formulario.
    Mapea las claves del JSON (nombres de campos del formulario) a los nombres de las columnas de la hoja.

    Args:
        data_json (dict): Diccionario con los datos del formulario.

    Returns:
        int: El número de la fila añadida, o None si falla.
    """
    if SHEET is None:
        logging.error("No se pudo añadir datos a la hoja: SHEET no está inicializado.")
        return None

    columnas = get_col(SHEET)
    row_to_append = []

    for col_name in columnas.keys():
        # Obtener la clave del formulario que corresponde a esta columna de la hoja.
        # Si no está en FIELD_MAPPING, asumimos que el nombre de la columna es el mismo que la clave del formulario.
        form_key = FIELD_MAPPING.get(col_name, col_name)
        
        # Obtener el valor del JSON del formulario usando la clave mapeada.
        value = data_json.get(form_key, "")
        
        row_to_append.append(value)

    try:
        result = SHEET.append_row(row_to_append, value_input_option='USER_ENTERED', insert_data_option='INSERT_ROWS')
        range_str = result['updates']['updatedRange'].split('!')[1]
        fila = int(re.findall(r'\d+', range_str)[0])
        logging.info(f"Datos del formulario añadidos a la fila {fila} en Google Sheets.")
        return fila
    except Exception as e:
        logging.error(f"Error al añadir nueva fila a Google Sheets: {str(e)}", exc_info=True)
        return None

    
    
