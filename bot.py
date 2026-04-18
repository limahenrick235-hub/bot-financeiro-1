from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json
import os

app = Flask(__name__)

# carregar dados
def carregar():
    try:
        with open("dados.json", "r") as f:
            return json.load(f)
    except:
        return {}

# salvar dados
def salvar(dados):
    with open("dados.json", "w") as f:
        json.dump(dados, f)

@app.route("/bot", methods=["POST"])
def bot():
    msg = request.values.get("Body", "").lower()
    numero = request.values.get("From")

    dados = carregar()

    if numero not in dados:
        dados[numero] = {"saldo": 0}

    resp = MessagingResponse()

    # COMANDOS
    if "saldo" in msg:
        saldo = dados[numero]["saldo"]
        resp.message(f"💰 Seu saldo é R$ {saldo}")

    elif "ganhei" in msg:
        try:
            valor = int(msg.split("ganhei")[1])
            dados[numero]["saldo"] += valor
            salvar(dados)
            resp.message(f"✅ Adicionado R$ {valor}")
        except:
            resp.message("Use: ganhei 100")

    elif "gastei" in msg:
        try:
            valor = int(msg.split("gastei")[1])
            dados[numero]["saldo"] -= valor
            salvar(dados)
            resp.message(f"❌ Gasto de R$ {valor}")
        except:
            resp.message("Use: gastei 50")

    elif "painel" in msg:
        saldo = dados[numero]["saldo"]
        resp.message(f"📊 Painel\nSaldo: R$ {saldo}")

    else:
        resp.message("Comandos: saldo | ganhei X | gastei X | painel")

    return str(resp)

# rodar no render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
