import re
import logging
import phonenumbers
import datetime

#congifuracion del logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


#FUNCIONES PARA HACER LA CONVERSION DE TIPOS PARA MANDAR EL PAYLOAD A PF+
def convertir_a_int(dato):
    dato_limpio = "".join(filter(str.isdigit, dato))
    dato_int = None
    if dato_limpio:
        try:
            dato_int = int(dato_limpio)
            return dato_int
        except ValueError:
                # En caso de que el string no sea un número válido
                logging.error(f"El valor '{dato}' no se puede convertir a número.")


def formatear_fecha_PF(fecha):
    if fecha is None:
        return None
    
    try:
        fecha_objeto = datetime.datetime.strptime(fecha, '%Y-%m-%d')
        return fecha_objeto.strftime('%Y-%m-%d')
    except ValueError:
        try:
            fecha_objeto = datetime.datetime.strptime(fecha, '%d/%m/%Y')
            return fecha_objeto.strftime('%Y-%m-%d')
        except ValueError:
            try:
                fecha_objeto = datetime.datetime.strptime(fecha, '%d-%m-%Y')
                return fecha_objeto.strftime('%Y-%m-%d')
            except (ValueError, TypeError) as e:
                # Si todos los intentos fallan, registra el error y retorna None
                logging.error(f"Error al convertir la fecha: {fecha}. Error: {e}")
                return None

