from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

@app.route("/bot", methods=["POST"])
def bot():
    msg = request.values.get("Body", "").lower()

    resp = MessagingResponse()

    if msg == "oi":
        resp.message("Bot funcionando 🚀")

    elif msg == "saldo":
        resp.message("Seu saldo é R$ 0")

    else:
        resp.message("Teste OK. Comandos: oi, saldo")

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)