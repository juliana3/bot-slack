import  time, logging, os
from dotenv import load_dotenv
import requests


from handlers.documento_handler import procesar_documento
from handlers.ingreso_handler import procesar_ingreso
from services.db_operations import obtener_ingresante_por_estado



API_TOKEN = os.getenv("PEOPLEFORCE_TOKEN")
API_URL= os.getenv("PEOPLEFORCE_URL")

def reprocesar_filas():
    logging.info("Iniciando reproceso de registros en PostgreSQL")

    f_procesadas = 0
    f_errores = 0

    try:
        # Consultar registros con errores o PDF pendiente en PostgreSQL
        ingresantes_a_reprocesar = obtener_ingresante_por_estado()
        logging.info(f"Se encontraron {len(ingresantes_a_reprocesar)} registros para reprocesar")


        for ingresante in ingresantes_a_reprocesar:
            ingresante_id_db = ingresante.get('id')
            dni = ingresante.get('dni')
            
            logging.info(f"Procesando registro DB ID: {ingresante_id_db} (DNI: {dni})....")

            estado_alta_db = ingresante.get('estado_alta', '').strip().lower()
            estado_pdf_db = ingresante.get('estado_pdf', '').strip().lower()
            #reproceso del alta
            if estado_alta_db in ["error", "pendiente", ""]:
                logging.info(f"Reintentando alta de registro DB ID: {ingresante_id_db} en PeopleForce.")

                try:
                    resultado_alta = procesar_ingreso(ingresante, archivos ={}, es_reproceso=True)

                    if resultado_alta.get("status") == "success":
                        f_procesadas +=1
                    else:
                        f_errores +=1
                        logging.error(f"Reproceso de alta falló para ID: {ingresante_id_db} - {resultado_alta}")
                except Exception as e:
                    f_errores +=1
                    logging.error(f"Excepción reprocesando alta para ID {ingresante_id_db}: {str(e)}", exc_info=True)


        
            #si estado_alta esta ok pero estado_pdf no
            if estado_alta_db == "procesada" and estado_pdf_db in ["error","pendiente",""]:
                logging.info(f"Intentando subir PDF de BD ID: {ingresante_id_db}.")
                datos_doc = {
                    "document_id_db": ingresante_id_db,
                    "employee_id": ingresante.get('id_pf'),
                    "nombre": ingresante.get('nombre'),
                    "apellido": ingresante.get('apellido'),
                    "email": ingresante.get('email'),
                    "dni_f": ingresante.get('dni_frente'),
                    "dni_d": ingresante.get('dni_dorso'),
                    "id_carpeta_drive" : ingresante.get('id_carpeta_drive')
                }

                #procesar documento
                resultado_doc = procesar_documento(datos_doc)
                if resultado_doc.get("status_code") in [200, 201]:
                    logging.info(f"PDF de DB ID: {ingresante_id_db} subido correctamente a PeopleForce")
                else:
                    logging.error(f"Error al subir PDF de DB ID: {ingresante_id_db}: {resultado_doc.get('error', 'Error desconocido')}")
                    f_errores +=1
                

            time.sleep(5)

    except Exception as e:
        logging.error(f"Excepción general en reprocesar_filas: {str(e)}", exc_info=True)
        return {"error": "Error interno en reproceso", "status": "failed", "status_code": 500}
    finally:
        time.sleep(5)  # pausa mínima para no saturar PeopleForce

    logging.info(f"Reproceso finalizado. Filas reprocesadas OK: {f_procesadas}, Filas con errores: {f_errores}")
    return {
        "mensaje"      : "Reproceso finalizado",
        "procesadas_ok": f_procesadas,
        "errores"      : f_errores
    }