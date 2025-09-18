import datetime
import logging
import re
import os
import gspread
from dotenv import load_dotenv
from google.oauth2 import service_account

load_dotenv()
#configuracion del acceso a Google Sheets
SCOPE  = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
CREDS  = service_account.Credentials.from_service_account_file("chatbot-people-466623-1ec1f3039c87.json",scopes=SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET_ID = os.getenv("ID_SPREADSHEET")
SHEET  = CLIENT.open_by_key(SHEET_ID).sheet1

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
    "AUTORIZADO": "FALSE", 
    "Nombre": "first_name",
    "Apellido": "last_name",
    "DNI": "dni",
    "Email": "email",
    "Celular": "phone_number",
    "Domicilio": "address",
    "Localidad" : "locality",
    "Fecha de Nacimiento": "date_of_birth", 
    "Tipo contrato": "type_of_contract", 
    "CBU": "cbu",
    "ALIAS": "alias",
    "CUIL": "cuil",
    "Banco": "national_bank",
    "Numero de cuenta": "national_account_number", 
    "Bank name": "bank_name", 
    "Bank address": "bank_address", 
    "Swift code": "swift_code", 
    "Account holder": "account_holder", 
    "Account number": "account_number", 
    "Routing number": "routing_number", 
    "Tipo de cuenta": "account_type", 
    "Zip code": "zip_code", 
    "Obra social": "health_insurance", 
    "Codigo AFIP": "afip_code", 
    "DNI frente": "dni_front", 
    "DNI dorso": "dni_back"
}

def cargar_sheets(data_json):
    """
    Agrega una nueva fila a Sheets con los datos del formulario.
    Mapea las claves del JSON (nombres de campos del formulario(html)) a los nombres de las columnas de la hoja.

    Argumentos:data_json (dict): Diccionario con los datos del formulario.

    Retorna:int: El número de la fila añadida, o None si falla.
    """
    if SHEET is None:
        logging.error("No se pudo añadir datos a la hoja: SHEET no está inicializado.")
        return None

    columnas = get_col(SHEET)
    row_to_append = []

    for col_name in columnas.keys():
        if col_name == "Creado el":
            row_to_append.append(str(datetime.date.today()))
        else:

            # Obtener el valor del JSON del formulario usando la clave mapeada.
            form_key = FIELD_MAPPING.get(col_name, col_name)
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

    
    
def eliminar_filas_no_autorizadas():
    
    #Elimina filas de la hoja de cálculo que no han sido autorizadas después de 7 días.
    if SHEET is None:
        logging.error("No se puede eliminar filas de la hoja: la conexión falló.")
        return False
    
    try:
        # Obtener los encabezados para encontrar los índices de las columnas
        columnas = get_col(SHEET)
        col_autorizado = columnas.get("AUTORIZADO")
        col_creado_el = columnas.get("Creado el")
        
        if not col_autorizado or not col_creado_el:
            logging.error("No se encontraron las columnas 'AUTORIZADO' o 'Creado el'.")
            return False

        # Obtener todos los datos de la hoja
        all_rows = SHEET.get_all_values()
        filas_a_borrar = []
        fecha_limite = datetime.date.today() - datetime.timedelta(days=7)

        # Iterar a partir de la segunda fila (la primera es el encabezado)
        for i, fila in enumerate(all_rows[1:], 2): 
            try:
                autorizado = fila[col_autorizado - 1].strip()
                fecha_str = fila[col_creado_el - 1]
                
                # Convertir la fecha de la fila a un objeto de fecha. Esto es para fechas con ceros adelante
                fecha_creacion = datetime.datetime.strptime(fecha_str, '%d/%m/%Y').date()
            
                # Verificar si cumple las condiciones para ser eliminada
                if autorizado.upper() in ("FALSO", "FALSE") and fecha_creacion < fecha_limite:

                    filas_a_borrar.append(i)

            except (ValueError, IndexError) as e:
                # Capturar errores si los datos de la fila no son válidos
                logging.warning(f"Se omitió la fila {i} por error en los datos: {e}")
                continue

        if not filas_a_borrar:
            logging.info("No se encontraron filas no autorizadas y antiguas para eliminar.")
            return True

        # Eliminar las filas de forma masiva para ser más eficiente
        # Es necesario eliminar en orden inverso para no alterar los índices de las filas
        for fila_num in sorted(filas_a_borrar, reverse=True):
            SHEET.delete_rows(fila_num)
            logging.info(f"Fila {fila_num} eliminada de Google Sheets.")

        logging.info(f"Proceso de eliminación de filas finalizado. Se eliminaron {len(filas_a_borrar)} filas.")
        return True

    except Exception as e:
        logging.error(f"Error general al eliminar filas de Google Sheets: {str(e)}", exc_info=True)
        return False
    
if __name__ == "__main__":
    eliminar_filas_no_autorizadas()