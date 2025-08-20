    #punto de entrada
from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
import os
import logging 


from services import sheets_utils

from handlers.ingreso_handler import procesar_ingreso
from handlers.reproceso_handler import reprocesar_filas
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

@app.route('/gracias')
def pagina_agradecimiento():
    return render_template('agradecimiento.html') 


@app.route('/agregar_persona', methods=['POST'])
def agregar_persona():

    datos = request.form.to_dict()
    archivos = request.files

    if not datos or not archivos:
        return jsonify({"error": "No se recibieron datos JSON"}), 400
    
    try:

        resultado = procesar_ingreso(datos, archivos)

        return jsonify({
            "mensaje": "Formulario recibido. Procesando...",
            "datos": datos,
            "status": resultado
        }), 200
    except Exception as e:
        logging.error(f"Excepción en /agregar_persona: {str(e)}")
        return jsonify({
            "mensaje": "Ocurrió un error interno, pero el formulario fue recibido.",
            "error": str(e),
            "status": {"status": "failed", "error": str(e)}
        }), 200
    finally:
        pass




@app.route('/reprocesar_errores', methods=['POST', 'GET'])
def reprocesar_errores():

    try:
        resultado = reprocesar_filas()
        return jsonify(resultado), 200
    except Exception as e:
        logging.error(f"Excepción en /reprocesar_errores: {str(e)}")
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    finally:
        pass


@app.route('/subir_pdf', methods=['POST'])
def subir_pdf():
    logging.info("Flask: Solicitud POST recibida en /subir_pdf.")
    try:
        datos_pdf = request.get_json()
        logging.info(f"Flask: Datos recibidos en /subir_pdf: {datos_pdf}")
        

        resultado = procesar_documento(datos_pdf)

        if resultado.get("status_code") in [200,201]:
            return jsonify({"mensaje": "Documento procesado correctamente"}), 200
        else:
            logging.error(f"Flask: procesar_documento falló. Resultado: {resultado}")
            return jsonify({"error": resultado.get("mensaje", "Error al procesar documento")}), 500
        
    except Exception as e:
        logging.error("Excepción al procesar PDF: %s", str(e))
        return jsonify({"error": f"Excepción: {str(e)}"}), 500
    finally:
        pass


# Iniciar el servidor
if __name__ == '__main__':
    app.run(debug=True, port=4000, host='0.0.0.0')
