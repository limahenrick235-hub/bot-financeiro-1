from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json
import os
from openai import OpenAI

app = Flask(__name__)

# 🔑 SUA API KEY DA IA
client = OpenAI(api_key="SUA_API_KEY_AQUI")

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

def criar_usuario():
    return {
        "saldo": 0,
        "recebido": 0,
        "gasto": 0,
        "limite": 130,
        "divida": 120,
        "meta": False,
        "categorias": {}
    }

@app.route("/bot", methods=["POST"])
def bot():
    msg = request.values.get("Body", "").lower()
    numero = request.values.get("From")

    dados = carregar()

    if numero not in dados:
        dados[numero] = criar_usuario()

    user = dados[numero]
    resp = MessagingResponse()

    # 💵 GANHOS
    if "ganhei" in msg:
        try:
            valor = int(msg.split("ganhei")[1])
            user["saldo"] += valor
            user["recebido"] += valor
            salvar(dados)
            resp.message(f"💵 +R$ {valor} adicionado")
        except:
            resp.message("Use: ganhei 100")

    # 💸 GASTOS
    elif "gastei" in msg:
        try:
            partes = msg.split()
            valor = int(partes[1])
            categoria = partes[2] if len(partes) > 2 else "outros"

            user["saldo"] -= valor
            user["gasto"] += valor

            if categoria not in user["categorias"]:
                user["categorias"][categoria] = 0

            user["categorias"][categoria] += valor

            salvar(dados)
            resp.message(f"💸 -R$ {valor} ({categoria})")
        except:
            resp.message("Use: gastei 50 comida")

    # 🏍️ META
    elif "meta sim" in msg:
        user["meta"] = True
        salvar(dados)
        resp.message("🏍️ Meta ativada")

    elif "meta nao" in msg:
        user["meta"] = False
        salvar(dados)
        resp.message("❌ Meta desativada")

    # 💳 DÍVIDA
    elif "divida" in msg:
        try:
            valor = int(msg.split("divida")[1])
            user["divida"] = valor
            salvar(dados)
            resp.message(f"💳 Dívida atualizada: R$ {valor}")
        except:
            resp.message("Use: divida 120")

    # 💰 SALDO
    elif "saldo" in msg:
        resp.message(f"💰 Saldo: R$ {user['saldo']}")

    # 📊 PAINEL
    elif "painel" in msg:
        restante = user["recebido"] - user["gasto"]
        limite_disp = user["limite"] - user["gasto"]

        resumo = "Semana controlada"
        if user["gasto"] > user["recebido"]:
            resumo = "Semana apertada"
        elif user["gasto"] < user["recebido"]:
            resumo = "Semana excelente"

        painel = f"""
💼📊 PAINEL FINANCEIRO

💰 Saldo: R$ {user['saldo']}

📅 Semana
Recebido: R$ {user['recebido']}
Gasto: R$ {user['gasto']}
Restante: R$ {restante}

💳 Limite: R$ {user['limite']}
Disponível: R$ {limite_disp}

🏍️ Meta: {"ATIVA ✔" if user["meta"] else "DESLIGADA"}

💳 Dívida: R$ {user['divida']}

📈 Resumo: {resumo}
"""
        resp.message(painel)

    # 🧠 IA (CONVERSA INTELIGENTE)
    elif "chat" in msg:
        try:
            pergunta = msg.replace("chat", "")

            resposta_ia = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um assistente financeiro inteligente que ajuda a controlar gastos e dar dicas."},
                    {"role": "user", "content": pergunta}
                ]
            )

            texto = resposta_ia.choices[0].message.content
            resp.message(texto)

        except:
            resp.message("Erro na IA. Verifique sua API key.")

    else:
        resp.message("Comandos: saldo | painel | ganhei X | gastei X categoria | chat pergunta")

    return str(resp)

# rodar no render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
