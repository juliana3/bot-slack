#punto de entrada
from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
import os
import logging 


from services.db_operations import Session
from services import sheets_utils

from handlers.ingreso_handler import procesar_ingreso
from handlers.documento_handler import procesar_documento

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

app = Flask(__name__)

#verificacion de inicializacion de sheets
if sheets_utils.SHEET is None:
    logging.error("La conexion a Google Sheets falló. El respaldo en Sheets no va a funcionar")

#verifiacion de inicializacion de PostgreSQL
if not os.getenv("DATABASE_URL"):
    logging.error("DATABASE_URL no está congigurada. La conexión a PostgreSQL fallará")

print("Flask arrancó", flush=True)

@app.route('/formulario_ingresante')
def mostar_formulario():
    return render_template('index.html')


@app.route('/agregar_persona', methods=['POST'])

def agregar_persona():
    # Obtener datos del formulario como diccionario
    datos = request.form.to_dict()

    # Obtener archivos
    dni_frente_file = request.files.get("dni-frente")
    dni_dorso_file = request.files.get("dni-dorso")

    # Agregar a datos
    datos["dni-frente"] = dni_frente_file
    datos["dni-dorso"] = dni_dorso_file

    session = Session()
    try:
        # Pasar también los archivos a procesar_ingreso
        resultado = procesar_ingreso(datos, session)

        http_status_code = 200
        if resultado.get("status") == "failed":
            http_status_code = 500
        # Devolvemos solo los campos de texto (sin archivos) para evitar el error MODIFICAR PARA PODER ENVIAR IMAGENES
        datos_sin_archivos = {k: v for k, v in datos.items() if not hasattr(v, "read")}

        return jsonify({"mensaje": "Recibido correctamente", "datos": datos_sin_archivos, "status": resultado}), http_status_code
    finally:
        session.close()




@app.route('/reprocesar_errores', methods=['POST', 'GET'])
def reprocesar_errores():
    session = Session()
    try:
        resultado = reprocesar_filas(session)
        return jsonify(resultado), 200
    finally:
        session.close()


@app.route('/subir_pdf', methods=['POST'])
def subir_pdf():
    logging.info("Flask: Solicitud POST recibida en /subir_pdf.")
    session = Session()
    try:
        datos_pdf = request.get_json()
        logging.info(f"Flask: Datos recibidos en /subir_pdf: {datos_pdf}")
        

        resultado = procesar_documento(datos_pdf, session)

        if resultado.get("status_code") in [200,201]:
            return jsonify({"mensaje": "Documento procesado correctamente"}), 200
        else:
            logging.error(f"Flask: procesar_documento falló. Resultado: {resultado}")
            return jsonify({"error": resultado.get("mensaje", "Error al procesar documento")}), 500
        
    except Exception as e:
        logging.error("Excepción al procesar PDF: %s", str(e))
        return jsonify({"error": f"Excepción: {str(e)}"}), 500
    finally:
        session.close()


# Iniciar el servidor
if __name__ == '__main__':
    app.run(debug=True, port=4000, host='0.0.0.0')
