import  time, logging

from handlers.ingreso_handler import procesar_ingreso
from handlers.documento_handler import procesar_documento
from services.db_operations import obtener_ingresante_por_estado, obtener_ingresante_por_id



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
            datos_ingreso = ingresante

            if estado_alta_db in ["error","pendiente",""]:
                logging.info(f"Reintentando alta de registro DB ID: {ingresante_id_db} en PeopleForce.")

                #reprocesar ingreso
                resultado_alta = procesar_ingreso(datos_ingreso)
                if resultado_alta.get("status") == "succes" or resultado_alta.get("status") == "partial_success":
                    logging.info(f"Alta del registro DB ID: {ingresante_id_db} reprocesada correctamente")
                    f_procesadas +=1

                    ingresante_actualizado = obtener_ingresante_por_id(ingresante_id_db)
                    employee_id_actualizado= ingresante_actualizado.get('id_pf') if ingresante_actualizado else None

                    #si estado_alta esta ok pero estado_pdf no
                    if estado_pdf_db in ["error","pendiente",""] and employee_id_actualizado:
                        logging.info(f"Intentando subir PDF de BD ID: {ingresante_id_db}.")
                        datos_doc = {
                            "document_id_db": ingresante_id_db,
                            "employee_id": employee_id_actualizado,
                            "nombre": ingresante.get('nombre'),
                            "apellido": ingresante.get('apellido'),
                            "email": ingresante.get('email'),
                            "dni_f": ingresante.get('dni_frente'),
                            "dni_d": ingresante.get('dni_dorso'),
                        }

                        #procesar documento
                        resultado_doc = procesar_documento(datos_doc)
                        if resultado_doc.get("status_code") in [200, 201]:
                            logging.info(f"PDF de DB ID: {ingresante_id_db} subido correctamente a PeopleForce")
                        else:
                            logging.error(f"Error al subir PDF de DB ID: {ingresante_id_db}: {resultado_doc.get('error', 'Error desconocido')}")
                            f_errores +=1
                    elif not employee_id_actualizado:
                        logging.warning(f"No se pudo reintentar PDF para DB ID: {ingresante_id_db} porque no se obtuvo employee_id")
                else:
                    logging.error(f"Error al reprocesar alta en PeopleForce para el registro DB ID: {ingresante_id_db}: {resultado_alta.get('error', 'Error desconocido')}")
                    f_errores +=1
            elif estado_alta_db == "procesada" and estado_pdf_db in ["pendiente","error",""]:
                logging.info(f"Reintentando subir PDF para DB ID: {ingresante_id_db}")

                datos_doc = {
                    "document_id_db": ingresante_id_db,
                    "employee_id": ingresante.get('id_pf'),
                    "nombre": ingresante.get('nombre'),
                    "apellido": ingresante.get('apellido'),
                    "email": ingresante.get('email'),
                    "dni_f": ingresante.get('dni_frente'),
                    "dni_d": ingresante.get('dni_dorso'),
                }
                resultado_doc = procesar_documento(datos_doc)

                if resultado_doc.get("status_code") in [200,201]:
                    logging.info(f"PDF de DB ID: {ingresante_id_db} subido correctamente aa PeopleForce")
                    f_procesadas += 1
                else:
                    logging.error(f"Error al subir PDF de DB ID: {ingresante_id_db} a PeopleForce")
                    f_errores += 1

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