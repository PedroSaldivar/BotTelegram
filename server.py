import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application

from bot import main as bot_main  # importa tu lógica del bot

app = Flask(__name__)
TOKEN = os.getenv("BOT_TOKEN")

# Inicializa la app de telegram
application = Application.builder().token(TOKEN).build()

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "OK"

@app.route("/")
def index():
    return "Bot de Aguas de Lourdes corriendo en Render 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
