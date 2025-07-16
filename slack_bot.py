from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import os
from db_queries import responder_con_gemini

load_dotenv()

# Configurar la app de Slack con el token de bot
app = App(token=os.getenv("SLACK_TOKEN"))
handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))

# Evento: cuando mencionan al bot
@app.event("app_mention")
def responder_mencion(event, say):
    texto = event.get("text", "")
    user = event.get("user", "")

    # Intentar extraer la pregunta quitando la mención al bot
    pregunta = texto
    if ">" in texto:
        partes = texto.split(">", 1)
        pregunta = partes[1].strip() if len(partes) > 1 else texto

    # Validar que haya una pregunta para evitar enviar texto vacío
    if not pregunta:
        say(f"<@{user}> No entendí tu pregunta, ¿podrías reformularla?")
        return

    # Obtener respuesta desde Gemini
    respuesta = responder_con_gemini(pregunta)

    # Enviar respuesta al canal, manejando posibles errores en la respuesta
    if not respuesta or respuesta.startswith("Error"):
        respuesta = "Lo siento, tuve un problema al obtener la respuesta. Intentá de nuevo más tarde."

    say(f"<@{user}> {respuesta}")

if __name__ == "__main__":
    print("Bot de Slack con Gemini iniciado")
    handler.start()
