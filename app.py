#punto de entrada
#punto de entrada

import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from slackeventsapi import SlackEventAdapter
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'],'/slack/events', app)

# Configuración del cliente de Slack
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

client.chat_postMessage(channel='#test', text='Hello world!')

@app.route('/slack/events', methods=['POST']) #esto no se que hace, ni si anda
def slack_events():
    data = request.get_json()
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})
    return "", 200


if __name__ == '__main__':
    app.run(debug=True)