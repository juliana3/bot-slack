import psycopg2
from psycopg2 import extras
import logging
import os
from dotenv import load_dotenv

load_dotenv
logging.basicConfig(
    level=logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s"
)

def get_db_connection():
    #establece y retorna una conexion a la base de datos
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        return conn
    except Exception as e:
        logging.error(f"Error al conectar a la base de datos: {str(e)}")
        return None
    


def guardar_ingresante(data_json):
    #guarda el nueo ingresante en la base de datos
    conn = get_db_connection()

    if conn is None:
        return None
    
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO new_entrants (
                    first_name, last_name, dni, email, phone_number, address, locality, date_of_birth,
                    health_insurance, afip_code, cbu, alias,
                    cuil, national_bank, national_account_number, bank_name, bank_address, swift_code, account_holder, 
                    account_number, routing_number, account_type, zip_code,
                    type_of_contract, dni_front, dni_back, onboarding_status, id_pf, pdf_status, id_drive_folder
                ) VALUES (
                    %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id;
            """
            valores = (
                data_json.get("first_name", ""),
                data_json.get("last_name", ""),
                data_json.get("dni", ""),
                data_json.get("email", ""),
                data_json.get("phone_number", ""),
                data_json.get("address", ""),
                data_json.get("locality", ""),
                data_json.get("date_of_birth", ""), 
                data_json.get("tertiary_level", ""),  
                data_json.get("university_level", ""),
                data_json.get("health_insurance", ""),      
                data_json.get("afip_code", ""),      
                data_json.get("cbu", ""),
                data_json.get("alias", ""),
                data_json.get("cuil", ""),
                data_json.get("national_bank", ""),
                data_json.get("national_account_number", ""),  
                data_json.get("bank_name", ""),     
                data_json.get("bank_address", ""),
                data_json.get("swift_code", ""),
                data_json.get("account_holder", ""),
                data_json.get("account_number", ""),
                data_json.get("routing_number", ""),
                data_json.get("account_type", ""),
                data_json.get("zip", ""),
                data_json.get("type_of_contract", ""),
                data_json.get("dni_front", ""),
                data_json.get("dni_back", ""),
                data_json.get("onboarding_status", "Pendiente"),
                data_json.get("id_pf", ""),
                data_json.get("pdf_status", "Pendiente"),
                data_json.get("id_drive_folder", "")
            )

            #ejecutar la consulta sql con los valores
            cursor.execute(sql,valores)

            #Guardar el id del registro recien insertado
            ingresante_id = cursor.fetchone()[0]

            conn.commit()

            logging.info(f"Datos guardados correctamente con ID: {ingresante_id}")
            return ingresante_id
    except Exception as e:
        conn.rollback()
        logging.error(f"Error al guardar datos: {str(e)}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()


def actualizar_columna(id_ingresante, columna, valor):
    #actualiza un campo de un ingresante

    conn = get_db_connection()

    if conn is None:
        return None
    
    try:
        cur = conn.cursor()
        
        # Lista de columnas que se pueden editar para evitar inyección SQL
        allowed_columns = ['onboarding_status', 'id_pf', 'pdf_status', 'id_drive_folder', 'dni_front', 'dni_back']
        if columna not in allowed_columns:
            logging.error(f"Intento de actualizar una columna no permitida: {columna}")
            return False

        # La columna se inserta directamente en el query, pero el valor se usa como parámetro
        sql = f"UPDATE new_entrants SET {columna} = %s WHERE id = %s"
        cur.execute(sql, (valor, id_ingresante))
        conn.commit()
        logging.info(f"Campo '{columna}' actualizado a '{valor}' para ingresante ID: {id_ingresante}")
        return True
    except (Exception, psycopg2.DatabaseError) as e:
        logging.error(f"Error al actualizar el campo '{columna}' para el ingresante {id_ingresante}: {e}", exc_info=True)
        conn.rollback()
        return False
    finally:
        if conn is not None:
            conn.close()


def obtener_ultimo_ingresante():
    #obtiene el ultimo registro guardado

    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            sql = "SELECT * FROM new_entrants ORDER BY id DESC LIMIT 1;"

            cursor.execute(sql)
            ultimo_ingresante = cursor.fetchone()

            if ultimo_ingresante:
                logging.info("Ultimo ingresante obtenido correctamente")
                return dict(ultimo_ingresante)
            else:
                logging.warning("No se encontraron ingresantes en la bse de datos")
                return None
    except Exception as e:
        logging.error(f"Error al obtener el ultimo ingresnate: {str(e)}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()

def obtener_ingresante_por_estado():
    #Obtieen los ingresantes cuyos estado_alta o estado_pdf estan "Pendientes", "Error" o ""

    estados = ["Pendiente", "Error", ""]

    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            sql = "SELECT * FROM new_entrants WHERE onboarding_status IN %s OR pdf_status IN %s;"

            tupla_estados = tuple(estados)

            cursor.execute(sql,(tupla_estados, tupla_estados))
            ingresantes = cursor.fetchall()

            if ingresantes:
                logging.info(f"Se encontraron {len(ingresantes)} con los estados {estados}")
                return [dict(ingresante) for ingresante in ingresantes] 
            else:
                logging.warning(f"No se encontraron ingresantes con los estados {estados}") 
    except Exception as e:
        logging.error(f"Error al obtener ingresantes por estado: {str(e)}", exc_info=True)
        return []
    finally:
        if conn:
            conn.close()


def obtener_ingresante_por_id(id_ingresante):
    #Obtieen los ingresantes segun el id de su registro en BD

    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            sql = "SELECT * FROM new_entrants WHERE id = %s;"


            cursor.execute(sql,(id_ingresante,))
            ingresante = cursor.fetchone()

            if ingresante:
                logging.info(f"Ingresante con ID {id_ingresante} encontrado")
                return dict(ingresante)
            else:
                logging.warning(f"Ingresante ID {id_ingresante} no encontrado")
    except Exception as e:
        logging.error(f"Error al obtener el ingresante con ID {id_ingresante}: {str(e)}", exc_info=True)
        return []
    finally:
        if conn:
            conn.close()

def obtener_id_carpeta_drive(id_ingresante):
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            sql = "SELECT id_drive_folder FROM new_entrants WHERE id = %s;"


            cursor.execute(sql,(id_ingresante,))
            id_carpeta = cursor.fetchone()

            if id_carpeta:
                logging.info(f"ID de carpeta drive para ingresante con ID {id_ingresante} encontrado")
                return dict(id_carpeta)
            else:
                logging.warning(f"ID de carpeta drive para ingresante con ID {id_ingresante} no encontrado")
                return None
    except Exception as e:
        logging.error(f"Error al obtener el ID de la carpeta drive para el ingresante con ID {id_ingresante}: {str(e)}", exc_info=True)
    finally:
        if conn:
            conn.close()