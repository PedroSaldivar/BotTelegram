import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, filters
)

# Importa todas tus funciones del bot
from bot import (
    start, handle_menu, handle_seleccion_producto, handle_cantidad,
    handle_datos_envio, handle_metodo_pago, handle_confirmacion,
    handle_estado_pedido, handle_contacto, handle_configuracion,
    cancel, error_handler, handle_pagar
)

# Estados de conversación
(
    MENU, COMPRA, SELECCION_PRODUCTO, CANTIDAD,
    DATOS_ENVIO, METODO_PAGO, CONFIRMACION,
    ESTADO_PEDIDO, CONTACTO, CONFIGURACION
) = range(10)

# Flask app
app = Flask(__name__)
TOKEN = os.getenv("BOT_TOKEN")

# Crea la aplicación de Telegram
application = Application.builder().token(TOKEN).build()

# ----- Handlers -----
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu)],
        SELECCION_PRODUCTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_seleccion_producto)],
        CANTIDAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_cantidad)],
        DATOS_ENVIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_datos_envio)],
        METODO_PAGO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_metodo_pago)],
        CONFIRMACION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confirmacion)],
        ESTADO_PEDIDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_estado_pedido)],
        CONTACTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contacto)],
        CONFIGURACION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_configuracion)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

application.add_handler(conv_handler)
application.add_handler(MessageHandler(filters.Regex(r"(?i)pagar"), handle_pagar))
application.add_error_handler(error_handler)

# ----- Inicializar Application al arrancar -----
loop = asyncio.get_event_loop()
loop.run_until_complete(application.initialize())
loop.run_until_complete(application.start())

# ----- Rutas de Flask -----
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    loop.create_task(application.process_update(update))
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot de Aguas de Lourdes corriendo en Render 🚀", 200

# Arranque
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
