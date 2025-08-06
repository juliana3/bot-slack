import re
import logging
import phonenumbers
import datetime

#congifuracion del logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def validar_string(value, min_length=1, max_length=255, field_name = "Campo"):
    """
    Valida que un string no este vacio y tenga una longitud dentro de los limites
    """

    if not isinstance(value, str):
        return False, f"{field_name} debe ser un string."
    trimmed_value = value.strip()
    if not trimmed_value:
        return False, f"{field_name} no puede estar vacio."
    if len(trimmed_value) < min_length:
        return False, f"{field_name} debe tener al menos {min_length} caracteres."
    if len(trimmed_value) > max_length:
        return False, f"{field_name} no puede tener mas de {max_length} caracteres."
    return True, ""

def validar_dni(dni):
    #valida que el dni tenga 7 u 8 digitos numericos

    if not isinstance(dni, str):
        return False, "DNI debe se un string."
    dni_cleaned = re.sub(r'\D', '', dni)  # Elimina cualquier caracter no numerico
    if not re.fullmatch(r'^\d{7,8}$', dni_cleaned):
        return False, "DNI debe tener 7 u 8 digitos numericos, sin puntos ni letras."
    return True, ""

def validar_email(email):
    if not isinstance(email, str):
        return False, "Email debe ser un string."
    if not re.fullmatch(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return False, "Formato de email invalido"
    return True, ""

def validar_celular(celular, default_region="AR"):
    if not isinstance(celular, str):
        return False, "Celular debe ser un string."
    try:
        parsed_number = phonenumbers.parse(celular, default_region)

        if not phonenumbers.is_valid_number(parsed_number):
            return False, "Numero de celular invalido."
        if not phonenumbers.is_possible_number(parsed_number):
            return False, "Numero de celular no es posible."
        
        return True, ""
    except phonenumbers.NumberParseException as e:
        return False, f"Formato de número de celular inválido: {e.args[0].replace('_', ' ').lower()}."
    except Exception as e:
        logging.error(f"Error inesperado al validar celular: {e}", exc_info=True)
        return False, "Error inesperado al validar el número de celular."
    
def validar_s3_key(s3_key, field_name="Clave S3"):
    # Valida que una clave de S3 sea un string no vacio y cumpla con las reglas de formato.
    if not isinstance(s3_key, str) or not s3_key.strip():
        return False, f"{field_name} no puede estar vacío y debe ser un string."
    return True, ""

def validar_cbu(cbu):
    #valida que el cbu tenga 22 digitos numericos
    if not isinstance(cbu, str):
        return False, "CBU debe ser un string."
    cbu_cleaned = re.sub(r'\D', '', cbu)  # Elimina cualquier caracter no numerico
    if not re.fullmatch(r'^\d{22}$', cbu_cleaned):
        return False, "CBU debe tener 22 digitos numericos, sin puntos ni espacios."
    return True, ""

def validar_cuil(cuil):
    #valida que el cuil tenga 1 digitos numricos
    if not isinstance(cuil, str):
        return False, "CUIL debe ser un string."
    cuil_cleaned = re.sub(r'\D', '', cuil)  # Elimina cualquier caracter no numerico
    if not re.fullmatch(r'^\d{11}$', cuil_cleaned):
        return False, "CUIL debe tener 11 digitos numericos, sin puntos ni espacios."
    return True, ""

def validar_account_number(account_number, min_length=4, max_length=20):
    #valida que el account number sea solo digitos numericos y de un largo especifico
    if not isinstance(account_number, str):
        return False, "Account number debe ser un string."
    account_number_cleaned = re.sub(r'\D', '', account_number)  # Elimina cualquier caracter no numerico
    if not re.fullmatch(r'^\d{'+str(min_length)+','+str(max_length)+'}$', account_number_cleaned):
        return False, f"El número de cuenta debe contener solo dígitos y tener entre {min_length} y {max_length} caracteres."
    return True, ""


#FUNCIONES PARA HACER LA CONVERSION DE TIPOS PARA MANDAR EL PAYLOAD A PF+
def convertir_a_int(dato):
    dato_limpio = "".join(filter(str.isdigit, dato))
    dato_int = None
    if dato_limpio:
        try:
            dato_int = int(dato_limpio)
        except ValueError:
                # En caso de que el string no sea un número válido
                logging.error(f"El valor '{dato}' no se puede convertir a número.")


def formatear_fecha(fecha):
    try:
        fecha_objeto = datetime.datetime.strptime(fecha, '%d-%m-%Y')
        return fecha_objeto.strftime('%Y-%m-%d')
    except (ValueError, TypeError) as e:
        logging.error(f"Error al convertir la fecha: {fecha}. Error: {e}")
        return None
