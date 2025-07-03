#punto de entrada
from flask import Flask, jsonify, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import requests

from handlers.ingreso_handler import procesar_ingreso

app = Flask(__name__)

#DEFINIMOS LAS 2 RUTAS
#PEOPLEFORCE_API_URL = "http://localhost:5001/mock_peopleforce" aca hay que cambiarlo por la url de la api de PF
#PEOPLEFORCE_API_TOKEN = "token_falso_para_test"

print("Flask arrancó", flush=True)
@app.route('/agregar_persona', methods=['POST'])
def agregar_persona():
    datos = request.json
    if not datos:
        return jsonify({"error": "No se recibieron datos JSON"}), 400
    
    resultado = procesar_ingreso(datos)
    print("datos recibidos:", datos, flush=True)
    return jsonify({"mensaje": "Recibido correctamente", "datos": datos}), 200
    
# Iniciar el servidor
if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')
