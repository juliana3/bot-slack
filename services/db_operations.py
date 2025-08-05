import psycopg2
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
                INSERT INTO ingresantes (
                    nombre, apellido, dni, email, celular, domicilio, localidad, fecha_nacimiento,
                    nivel_terciario, nivel_universitario, obra_social, codigo_afip, cbu, alias,
                    cuil, banco, numero_cuenta, bank_name, bank_address, swift_code, account_holder,
                    holder_address, account_number, routing_number, tipo_cuenta, zip_code,
                    tipo_contrato, dni_frente, dni_dorso, estado_alta, id_pf, estado_pdf
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id;
            """
            valores = (
                data_json.get("nombre", ""),
                data_json.get("apellido", ""),
                data_json.get("dni", ""),
                data_json.get("email", ""),
                data_json.get("celular", ""),
                data_json.get("domicilio", ""),
                data_json.get("localidad", ""),
                data_json.get("fecha-nacimiento", ""), 
                data_json.get("nivel-terciario", ""),  
                data_json.get("nivel-universitario", ""),
                data_json.get("obra-social", ""),      
                data_json.get("codigo-afip", ""),      
                data_json.get("cbu", ""),
                data_json.get("alias", ""),
                data_json.get("cuil", ""),
                data_json.get("banco", ""),
                data_json.get("numero-cuenta", ""),  
                data_json.get("bank-name", ""),     
                data_json.get("bank-address", ""),  
                data_json.get("swift-code", ""),     
                data_json.get("account-holder", ""),  
                data_json.get("holder-address", ""),  
                data_json.get("account-number", ""),   
                data_json.get("routing-number", ""),  
                data_json.get("tipo-cuenta", ""),      
                data_json.get("zip-code", ""),         
                data_json.get("tipo-contrato", ""),    
                data_json.get("dni-frente", ""),      
                data_json.get("dni-dorso", ""),      
                data_json.get("estado_alta", "Pendiente"),
                data_json.get("id_pf", ""),
                data_json.get("estado_pdf", "Pendiente")
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


def actualizar_estado(id_ingresante, columna, valor):
    #actualiza un campo de un ingresante

    conn = get_db_connection()

    if conn is None:
        return None
    
    try:
        cur = conn.cursor()
        
        # Lista blanca de columnas para evitar inyección SQL
        allowed_columns = ['estado_alta', 'id_pf', 'estado_pdf']
        if columna not in allowed_columns:
            logging.error(f"Intento de actualizar una columna no permitida: {columna}")
            return False

        # La columna se inserta directamente en el query, pero el valor se usa como parámetro
        sql = f"UPDATE ingresantes SET {columna} = %s WHERE id = %s"
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
            sql = "SELECT * FROM ingresantes ORDER BY id DESC LIMIT 1;"

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
            sql = "SELECT FROM ingresantes WHERE estado_alta IN %s OR estado_pdf IN %s;"

            tupla_estados = tuple(estados)

            cursor.execute(sql(tupla_estados, tupla_estados))
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
            sql = "SELECT FROM ingresantes WHERE id = %s;"


            cursor.execute(sql(id_ingresante,))
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
