import os
import logging
import boto3
import uuid
from botocore.exceptions import ClientError

#configuracion del logging
logging.basicConfig(
    level=logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s"
)

#incializar el cliente de S3
s3_client = boto3.client('s3')
logging.info("Cliente de S3 inicializado correctamente.")

def generar_url_pre_firmada(bucket_name, object_name, expiration=3600):
    """
    Genera una URL pre-firmada para permitit que el usuario que completa el formulario pueda subir un archivo directamente a S3.
    
    Args:
        bucket_name (str): Nombre del bucket de S3.
        object_name (str): Nombre del objeto en S3.
        expiration (int): Tiempo en segundos para que la URL sea válida. Por defecto es 3600 segundos (1 hora).
    Returns:
        tuple: (URL pre-firmada, clave del objeto) si tiene exito. (None, none) si falla.
    """
    try:
        #generar la URL pre-firmada para un PUT
        response = s3_client.generate_presigned_post(
            Bucket = bucket_name,
            Key = object_name,
            ExpiresIn = expiration
        )
        logging.info(f"URL pre-firmada generada para subir a s3://{bucket_name}/{object_name}")
        return response, object_name #devuelve un dict con url y fields
    except ClientError as e:
        logging.error(f"Eroor al generar URL pre-firmada para S3: {e}", exc_info=True)
        return None,None
    except Exception as e:
        logging.error(f"Eroor inesperado al generar URL pre-firmada: {e}", exc_info=True)
        return None, None
    

def obtener_url_objeto(bucket_name, object_key):
    """
    Genera una URL pre-firmada para descargar un objeto en S3.
    Args:
        bucket_name (str): Nombre del bucket de S3.
        object_key (str): Clave del objeto en S3.
    Returns: 
        str: la URL HTTP del objeto S3
    """

    return f"s3://{bucket_name}/{object_key}" #URI de S3 que se guarda en la base de datos

def descargar_archivo_desde_s3(bucket_name, object_key):
    """
    Descarga un archivo desde S3 y devuelve su contenido en Bytes
    
    Args:
        bucket_name (str): Nombre del bucket de S3.
        object_key (str): Clave del objeto en S3.
    Returns:
        bytes: Contenido del archivo descargado en bytes o None si falla
    """

    try: 
        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=object_key
        )
        file_content = response['Body'].read()
        logging.info(f"Archivo {object_key} descargado correctamente desde S3.")
        return file_content
    except ClientError as e:
        logging.error(f"Error al descargar el archivo {object_key} desde S3: {e}", exc_info=True)
        return None
    except Exception as e:
        logging.error(f"Error inesperado al descargar el archivo {object_key}: {e}", exc_info=True)
        return None
    
    