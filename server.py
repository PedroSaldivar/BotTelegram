import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application

from bot import main  # importa tu lógica de handlers, pero sin run_polling()

app = Flask(__name__)
TOKEN = os.getenv("BOT_TOKEN")

# Crea la aplicación global
application = Application.builder().token(TOKEN).build()

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    # En lugar de Updater, ahora en v20 usamos la cola de updates
    application.update_queue.put(update)
    return "OK"

@app.route("/")
def index():
    return "Bot de Aguas de Lourdes corriendo en Render 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

