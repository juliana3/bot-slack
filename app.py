#punto de entrada
from flask import Flask, jsonify, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import requests
import logging 



from handlers.ingreso_handler import procesar_ingreso
from handlers.reproceso_handler import reprocesar_filas
from handlers.documento_handler import procesar_documento

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

app = Flask(__name__)




print("Flask arrancó", flush=True)
@app.route('/agregar_persona', methods=['POST'])
def agregar_persona():
    datos = request.json
    if not datos:
        return jsonify({"error": "No se recibieron datos JSON"}), 400
    
    fila = datos.get("fila")
    resultado = procesar_ingreso(datos, fila)

    http_status_code = 200
    if resultado.get("status") == "failed":
        http_status_code = 500
    return jsonify({"mensaje": "Recibido correctamente", "datos": datos, "status":resultado}), http_status_code





@app.route('/reprocesar_errores', methods=['POST', 'GET'])
def reprocesar_errores():
    resultado = reprocesar_filas()
    return jsonify(resultado), 200


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


# Iniciar el servidor
if __name__ == '__main__':
    app.run(debug=True, port=4000, host='0.0.0.0')
