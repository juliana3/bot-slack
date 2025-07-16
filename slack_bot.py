from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import os
from db_queries import responder_con_gemini

load_dotenv()

# Configurar la app de Slack
app = App(token=os.getenv("SLACK_TOKEN"))
handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")) 

# Evento: cuando mencionan al bot
@app.event("app_mention")
def responder_mencion(event, say):
    texto = event.get("text", "")
    user = event.get("user", "")

    # Limpiar la mención para extraer solo la pregunta
    partes = texto.split(">", 1)
    pregunta = partes[1].strip() if len(partes) > 1 else texto

    # Obtener respuesta desde Gemini
    respuesta = responder_con_gemini(pregunta)

    # Enviar respuesta al canal
    say(f"<@{user}> {respuesta}")

if __name__ == "__main__":
    print("Bot de Slack con Gemini iniciado")
    handler.start()
