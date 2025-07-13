#punto de entrada
from flask import Flask, jsonify, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import requests
import logging 



from handlers.ingreso_handler import procesar_ingreso
from handlers.reproceso_handler import reprocesar_filas

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
    
    resultado = procesar_ingreso(datos)
    return jsonify({"mensaje": "Recibido correctamente", "datos": datos, "status":resultado}), 200





@app.route('/reprocesar_errores', methods=['POST', 'GET'])
def reprocesar_errores():
    resultado = reprocesar_filas()
    return jsonify(resultado), 200



# Iniciar el servidor
if __name__ == '__main__':
    app.run(debug=True, port=4000, host='0.0.0.0')
