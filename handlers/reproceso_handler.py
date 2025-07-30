import  time, logging

from handlers.ingreso_handler import procesar_ingreso
from handlers.documento_handler import procesar_documento


from services.database_config import Ingresante, Session



def reprocesar_filas():
    logging.info("Iniciando reproceso de registros en PostgreSQL")

    #obtener todos los valores de la hoja de una sola vez
    session = Session()

    f_procesadas = 0
    f_errores = 0

    try:
        # Consultar registros con errores o PDF pendiente en PostgreSQL
        query_errors_alta = session.query(Ingresante).filter(
            Ingresante.estado_alta.in_(['Error', 'Pendiente', ''])
        )

        query_errors_pdf = session.query(Ingresante).filter(
            Ingresante.estado_alta == 'Procesada',
            Ingresante.estado_pdf.in_(['Error', 'Pendiente', ''])
        )

        reprocess_ingresantes = {}
        for ingresante in query_errors_alta.all():
            reprocess_ingresantes[ingresante.id] = ingresante
        for ingresante in query_errors_pdf.all():
            reprocess_ingresantes[ingresante.id] = ingresante

        logging.info(f"Se encontraron {len(reprocess_ingresantes)} registros en PostgreSQL para reprocesar.")

        for ingresante_id_db, ingresante_obj in reprocess_ingresantes.items():
            logging.info(f"Procesando registro DB ID: {ingresante_id_db} (DNI: {ingresante_obj.dni})...")

            estado_db = ingresante_obj.estado_alta.strip().lower()
            estado_pdf_db = ingresante_obj.estado_pdf.strip().lower()

            # Construir datos_para_procesar_ingreso dinámicamente
            # Se excluyen los campos de estado y el 'id' de la DB, ya que procesar_ingreso
            # espera los datos del formulario original y las URLs de S3.
            datos_ingreso = {
                column.name: getattr(ingresante_obj, column.name)
                for column in Ingresante.__table__.columns
                if column.name not in ['id', 'estado_alta', 'id_pf', 'estado_pdf']
            } 


            # Si el alta en PeopleForce tiene error, reintentar alta
            if estado_db in ["error", "pendiente", ""]:
                logging.info(f"Reintentando alta de registro DB ID: {ingresante_id_db} en PeopleForce.")
                # procesar_ingreso espera el JSON original del formulario y la sesión
                resultado_alta = procesar_ingreso(datos_ingreso, session)
                
                if resultado_alta.get("status") == "success" or resultado_alta.get("status") == "partial_success":
                    logging.info(f"Registro DB ID: {ingresante_id_db} reprocesado (alta) correctamente.")
                    f_procesadas += 1
                    
                    session.refresh(ingresante_obj) # Refrescar el objeto para obtener los últimos datos de la DB
                    employee_id_actualizado = ingresante_obj.id_pf

                    # Si el PDF tiene error o está pendiente Y tenemos un employee_id
                    if estado_pdf_db in ["error", "pendiente", ""] and employee_id_actualizado:
                        logging.info(f"Intentando subir PDF de registro DB ID: {ingresante_id_db}.")
                        datos_doc = {
                            "document_id_db": ingresante_id_db,
                            "employee_id": employee_id_actualizado,
                            "nombre": ingresante_obj.nombre,
                            "apellido": ingresante_obj.apellido,
                            "email": ingresante_obj.email,
                            "dni_f": ingresante_obj.dni_frente, # URLs de S3
                            "dni_d": ingresante_obj.dni_dorso,  # URLs de S3
                        }
                        resultado_doc = procesar_documento(datos_doc, session) # Pasar la sesión
                        if resultado_doc.get("status_code") in [200, 201]:
                            logging.info(f"PDF de registro DB ID: {ingresante_id_db} subido correctamente.")
                        else:
                            logging.error(f"Error al subir PDF de registro DB ID: {ingresante_id_db}: {resultado_doc.get('error', 'Error desconocido')}")
                            f_errores += 1
                    elif not employee_id_actualizado:
                        logging.warning(f"No se pudo reintentar PDF para DB ID: {ingresante_id_db} porque no se obtuvo employee_id.")
                    
                else:
                    logging.error(f"Error al reprocesar alta de registro DB ID: {ingresante_id_db}: {resultado_alta.get('error', 'Error desconocido')}")
                    f_errores += 1
            
            # Si el alta ya está procesada pero el PDF tiene error, reintentar solo PDF
            elif estado_db == "procesada" and estado_pdf_db in ["error", "pendiente", ""]:
                logging.info(f"Reintentando subir PDF de registro DB ID: {ingresante_id_db} (alta ya procesada).")
                datos_doc = {
                    "document_id_db": ingresante_id_db,
                    "employee_id": ingresante_obj.id_pf,
                    "nombre": ingresante_obj.nombre,
                    "apellido": ingresante_obj.apellido,
                    "email": ingresante_obj.email,
                    "dni_f": ingresante_obj.dni_frente,
                    "dni_d": ingresante_obj.dni_dorso,
                }
                resultado_doc = procesar_documento(datos_doc, session) # Pasar la sesión
                if resultado_doc.get("status_code") in [200, 201]:
                    logging.info(f"PDF de registro DB ID: {ingresante_id_db} subido correctamente.")
                    f_procesadas += 1
                else:
                    logging.error(f"Error al subir PDF de registro DB ID: {ingresante_id_db}: {resultado_doc.get('error', 'Error desconocido')}")
                    f_errores += 1
            
            time.sleep(5)

    except Exception as e:
        logging.error(f"Excepción general en reprocesar_filas: {str(e)}", exc_info=True)
        return {"error": "Error interno en reproceso", "status": "failed", "status_code": 500}
    finally:
        session.close()

        time.sleep(5)  # pausa mínima para no saturar PeopleForce

    logging.info(f"Reproceso finalizado. Filas reprocesadas OK: {f_procesadas}, Filas con errores: {f_errores}")
    return {
        "mensaje"      : "Reproceso finalizado",
        "procesadas_ok": f_procesadas,
        "errores"      : f_errores
    }