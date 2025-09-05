import os
import json
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

# Estados de conversación
(
    MENU, COMPRA, SELECCION_PRODUCTO, CANTIDAD, 
    DATOS_ENVIO, METODO_PAGO, CONFIRMACION,
    ESTADO_PEDIDO, CONTACTO, CONFIGURACION
) = range(10)

# Simulación de productos (mientras creamos los archivos)
PRODUCTOS = {
    "1": {
        "id": "1",
        "nombre": "Agua Mineral 355ml",
        "precio": 10.00,
        "stock": 100,
        "descripcion": "Botella PET 355ml"
    },
    "2": {
        "id": "2", 
        "nombre": "Agua Mineral 600ml",
        "precio": 15.00,
        "stock": 80,
        "descripcion": "Botella PET 600ml"
    },
    "3": {
        "id": "3",
        "nombre": "Agua Mineral de Vidrio",
        "precio": 25.00,
        "stock": 50,
        "descripcion": "Botella de vidrio 500ml"
    }
}

# Simulación de base de datos
carritos = {}
pedidos = {}

# Teclados
def main_keyboard():
    return ReplyKeyboardMarkup([
        ["💧 Comprar Agua", "🎯 Promociones"],
        ["📦 Estado de Pedido", "🕐 Horarios"],
        ["⚙️ Configuración", "❓ Preguntas Frecuentes"],
        ["👨‍💼 Contacto Humano"]
    ], resize_keyboard=True)

def back_keyboard():
    return ReplyKeyboardMarkup([["🔙 Menú Principal"]], resize_keyboard=True)

def productos_keyboard():
    keyboard = []
    for id, prod in PRODUCTOS.items():
        keyboard.append([f"{prod['nombre']} - ${prod['precio']}"])
    keyboard.append(["🔙 Menú Principal"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def metodos_pago_keyboard():
    return ReplyKeyboardMarkup([
        ["💳 Tarjeta de Crédito/Débito"],
        ["💰 Pago contra Entrega"],
        ["🏦 Transferencia Bancaria"],
        ["🔙 Atrás"]
    ], resize_keyboard=True)

def confirmacion_keyboard():
    return ReplyKeyboardMarkup([
        ["✅ Sí, confirmar pedido"],
        ["❌ No, cancelar compra"],
        ["🔙 Atrás"]
    ], resize_keyboard=True)

# --- FUNCIONES DE BASE DE DATOS SIMULADAS ---
def guardar_carrito(user_id, carrito):
    carritos[user_id] = carrito

def obtener_carrito(user_id):
    return carritos.get(user_id, {"productos": [], "total": 0.0})

def limpiar_carrito(user_id):
    carritos[user_id] = {"productos": [], "total": 0.0}

def crear_pedido(user_id, carrito, datos_envio, metodo_pago):
    from datetime import datetime
    pedido_id = f"P{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    pedido = {
        "id": pedido_id,
        "user_id": user_id,
        "productos": carrito["productos"],
        "total": carrito["total"],
        "datos_envio": datos_envio,
        "metodo_pago": metodo_pago,
        "estado": "pendiente",
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tiempo_entrega": "2-3 horas"
    }
    
    pedidos[pedido_id] = pedido
    return pedido_id

# --- PALABRAS CLAVE UNIVERSALES ---
async def check_volver_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verificar si el usuario quiere volver al menú"""
    text = update.message.text.lower()
    
    palabras_volver = [
        "menu", "menú", "principal", "volver", "atrás", "atras", 
        "inicio", "home", "regresar", "back", "cancelar"
    ]
    
    if any(palabra in text for palabra in palabras_volver):
        await update.message.reply_text(
            "🏠 Volviendo al menú principal...",
            reply_markup=main_keyboard()
        )
        return MENU
    
    return None

# --- FLUJOS PRINCIPALES ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mensaje de bienvenida y menú principal"""
    welcome_text = """
    💧 ¡Bienvenido a Aguas de Lourdes! 💧

    Elige una opción para continuar:
    
    💡 **Tips:**
    - Usa el teclado para navegar
    - Escribe "menu" en cualquier momento para volver
    """
    await update.message.reply_text(welcome_text, reply_markup=main_keyboard())
    return MENU

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar selección del menú"""
    # Primero verificar si quiere volver al menú
    volver = await check_volver_menu(update, context)
    if volver is not None:
        return volver
        
    text = update.message.text
    
    if "comprar" in text.lower():
        await iniciar_compra(update, context)
        return SELECCION_PRODUCTO
        
    elif "estado" in text.lower():
        await update.message.reply_text(
            "📦 Por favor, ingresa tu número de pedido:\n\n💡 Escribe 'menu' para volver",
            reply_markup=back_keyboard()
        )
        return ESTADO_PEDIDO
        
    elif "horarios" in text.lower():
        await show_horarios(update, context)
        return MENU
        
    elif "preguntas" in text.lower():
        await show_faq(update, context)
        return MENU
        
    elif "contacto" in text.lower():
        await show_contacto(update, context)
        return CONTACTO
        
    elif "configuración" in text.lower() or "configuracion" in text.lower():
        await show_configuracion(update, context)
        return CONFIGURACION
        
    elif "promociones" in text.lower():
        await show_promociones(update, context)
        return MENU
    
    return MENU

# --- SISTEMA DE COMPRAS ---
async def iniciar_compra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Iniciar flujo de compra"""
    user_id = update.message.from_user.id
    guardar_carrito(user_id, {"productos": [], "total": 0.0})
    
    await update.message.reply_text(
        "🛍️ **SISTEMA DE COMPRAS**\n\n💡 ¿Qué tipo de agua deseas comprar?",
        reply_markup=productos_keyboard()
    )
    return SELECCION_PRODUCTO

async def handle_seleccion_producto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar selección de producto"""
    volver = await check_volver_menu(update, context)
    if volver is not None:
        return volver
    
    text = update.message.text
    user_id = update.message.from_user.id
    
    # Buscar producto seleccionado
    producto_seleccionado = None
    for id, prod in PRODUCTOS.items():
        if prod['nombre'] in text:
            producto_seleccionado = prod
            break
    
    if producto_seleccionado:
        context.user_data['producto_actual'] = producto_seleccionado
        
        await update.message.reply_text(
            f"✅ Seleccionaste: {producto_seleccionado['nombre']}\n"
            f"💰 Precio: ${producto_seleccionado['precio']}\n"
            f"📦 Stock disponible: {producto_seleccionado['stock']} unidades\n\n"
            "💡 ¿Cuántas botellas deseas agregar al carrito?",
            reply_markup=back_keyboard()
        )
        return CANTIDAD
    else:
        await update.message.reply_text(
            "❌ Producto no reconocido. Por favor selecciona una opción del teclado.",
            reply_markup=productos_keyboard()
        )
        return SELECCION_PRODUCTO

async def handle_cantidad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar cantidad de producto"""
    volver = await check_volver_menu(update, context)
    if volver is not None:
        return volver
    
    text = update.message.text
    user_id = update.message.from_user.id
    producto = context.user_data.get('producto_actual')
    
    try:
        cantidad = int(text)
        
        if cantidad <= 0:
            await update.message.reply_text("❌ La cantidad debe ser mayor a 0. Intenta de nuevo:", reply_markup=back_keyboard())
            return CANTIDAD
        
        if cantidad > producto['stock']:
            await update.message.reply_text(
                f"😔 Lo sentimos, stock insuficiente.\n📦 Stock actual: {producto['stock']} unidades\n💡 Intenta con menos:",
                reply_markup=back_keyboard()
            )
            return CANTIDAD
        
        # Agregar al carrito
        carrito = obtener_carrito(user_id)
        item_carrito = {
            "producto_id": producto['id'],
            "nombre": producto['nombre'],
            "precio_unitario": producto['precio'],
            "cantidad": cantidad,
            "subtotal": producto['precio'] * cantidad
        }
        
        carrito['productos'].append(item_carrito)
        carrito['total'] += item_carrito['subtotal']
        guardar_carrito(user_id, carrito)
        
        await update.message.reply_text(
            f"✅ ¡Perfecto! Agregado {cantidad} {producto['nombre']} al carrito.\n"
            f"💰 Subtotal: ${item_carrito['subtotal']:.2f}\n"
            f"🛒 Total carrito: ${carrito['total']:.2f}\n\n"
            "💡 Escribe 'pagar' para continuar o selecciona otro producto:",
            reply_markup=productos_keyboard()
        )
        return SELECCION_PRODUCTO
        
    except ValueError:
        await update.message.reply_text("❌ Por favor ingresa un número válido:", reply_markup=back_keyboard())
        return CANTIDAD

async def handle_pagar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detectar cuando el usuario escribe 'pagar'"""
    text = update.message.text.lower()
    
    if "pagar" in text:
        user_id = update.message.from_user.id
        carrito = obtener_carrito(user_id)
        
        if not carrito['productos']:
            await update.message.reply_text("🛒 Tu carrito está vacío. Agrega productos primero.", reply_markup=productos_keyboard())
            return SELECCION_PRODUCTO
        
        await update.message.reply_text(
            "📦 **DATOS DE ENVÍO**\n\nPor favor proporciona:\n• Nombre completo\n• Dirección\n• Teléfono\n• Referencias\n\n💡 Ejemplo:\nJuan Pérez\nCalle Principal #123\n555-123-4567",
            reply_markup=back_keyboard()
        )
        return DATOS_ENVIO
    else:
        return await handle_seleccion_producto(update, context)

async def handle_datos_envio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar datos de envío"""
    volver = await check_volver_menu(update, context)
    if volver is not None:
        return volver
    
    datos_envio = update.message.text
    context.user_data['datos_envio'] = datos_envio
    
    await update.message.reply_text(
        "💳 **MÉTODO DE PAGO**\n\nElige tu método de pago:",
        reply_markup=metodos_pago_keyboard()
    )
    return METODO_PAGO

async def handle_metodo_pago(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar método de pago"""
    text = update.message.text
    
    if "atrás" in text.lower():
        await update.message.reply_text("📦 Ingresa tus datos de envío:", reply_markup=back_keyboard())
        return DATOS_ENVIO
    
    volver = await check_volver_menu(update, context)
    if volver is not None:
        return volver
    
    context.user_data['metodo_pago'] = text
    user_id = update.message.from_user.id
    carrito = obtener_carrito(user_id)
    datos_envio = context.user_data.get('datos_envio', '')
    
    # Mostrar resumen del pedido
    resumen = "🛒 **RESUMEN DE TU PEDIDO**\n\n"
    for item in carrito['productos']:
        resumen += f"• {item['cantidad']}x {item['nombre']} - ${item['subtotal']:.2f}\n"
    
    resumen += f"\n💰 **Total: ${carrito['total']:.2f}**\n"
    resumen += f"📦 **Envío a:**\n{datos_envio}\n"
    resumen += f"💳 **Método de pago:** {text}\n\n"
    resumen += "✅ ¿Confirmas tu pedido?"
    
    await update.message.reply_text(resumen, reply_markup=confirmacion_keyboard())
    return CONFIRMACION

async def handle_confirmacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar confirmación de pedido"""
    text = update.message.text
    user_id = update.message.from_user.id
    
    if "sí" in text.lower() or "confirmar" in text.lower():
        carrito = obtener_carrito(user_id)
        datos_envio = context.user_data.get('datos_envio', '')
        metodo_pago = context.user_data.get('metodo_pago', '')
        
        pedido_id = crear_pedido(user_id, carrito, datos_envio, metodo_pago)
        limpiar_carrito(user_id)
        
        await update.message.reply_text(
            f"🎉 **¡PEDIDO CONFIRMADO!**\n\n"
            f"📦 Número de pedido: {pedido_id}\n"
            f"💰 Total: ${carrito['total']:.2f}\n"
            f"⏰ Tiempo estimado: 2-3 horas\n"
            f"🚚 Estado: En preparación\n\n"
            f"💡 Usa /estado para consultar tu pedido\n\n"
            f"¡Gracias por tu compra! 😊",
            reply_markup=main_keyboard()
        )
        return MENU
        
    elif "no" in text.lower() or "cancelar" in text.lower():
        limpiar_carrito(user_id)
        await update.message.reply_text("❌ Pedido cancelado.", reply_markup=main_keyboard())
        return MENU
    
    else:
        await update.message.reply_text("❌ Opción no reconocida. ¿Confirmas?", reply_markup=confirmacion_keyboard())
        return CONFIRMACION

# --- FLUJO ESTADO PEDIDO ---
async def handle_estado_pedido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Consultar estado de pedido"""
    volver = await check_volver_menu(update, context)
    if volver is not None:
        return volver
    
    num_pedido = update.message.text
    
    # Simular consulta
    await update.message.reply_text(
        f"📦 **Pedido #{num_pedido}**\n"
        f"✅ Estado: En proceso\n"
        f"⏰ Tiempo estimado: 2 horas\n"
        f"🚚 Repartidor: Juan Pérez\n\n"
        f"💡 Escribe 'menu' para volver",
        reply_markup=back_keyboard()
    )
    return ESTADO_PEDIDO

# --- FLUJO CONTACTO ---
async def show_contacto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_text = """
    👨‍💼 **CONTACTO Y SOPORTE**
    
    📞 Teléfono: +52 444 812 3132
    📧 Email: ventas@aguasdelourdes.com.mx
    🌐 Website: https://aguasdelourdes.com.mx/
    
    💡 Escribe 'menu' para volver
    """
    await update.message.reply_text(contact_text, reply_markup=back_keyboard())

async def handle_contacto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    volver = await check_volver_menu(update, context)
    if volver is not None:
        return volver
    
    await update.message.reply_text(
        "📩 **Mensaje recibido**\n\nUn agente te contactará pronto.\n💡 Escribe 'menu' para volver",
        reply_markup=back_keyboard()
    )
    return CONTACTO

# --- CONFIGURACIÓN ---
async def show_configuracion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config_text = """
    ⚙️ **CONFIGURACIÓN DE USUARIO**
    
    📝 Datos personales
    🏠 Direcciones de envío  
    💳 Métodos de pago
    🔔 Notificaciones
    
    💡 Escribe 'menu' para volver
    """
    await update.message.reply_text(config_text, reply_markup=back_keyboard())

async def handle_configuracion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    volver = await check_volver_menu(update, context)
    if volver is not None:
        return volver
    
    await update.message.reply_text(
        "🔧 **Configuración en desarrollo**\n💡 Escribe 'menu' para volver",
        reply_markup=back_keyboard()
    )
    return CONFIGURACION

# --- FUNCIONES AUXILIARES ---
async def show_horarios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    horario_text = """
    🕐 **HORARIOS DE ATENCIÓN**
    
    Lunes a Viernes: 9:00 - 18:00 hrs
    Sábados: 9:00 - 14:00 hrs  
    Domingos: Cerrado
    
    💡 Escribe 'menu' para volver
    """
    await update.message.reply_text(horario_text, reply_markup=main_keyboard())

async def show_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    faq_text = """
    ❓ **PREGUNTAS FRECUENTES**
    
    1. ¿Cuánto tarda el envío? → 24-48 horas
    2. ¿A qué lugares hacen entregas? → Área metropolitana
    3. ¿Qué métodos de pago aceptan? → Tarjeta, transferencia, efectivo
    4. ¿El agua es de manantial? → ¡Sí! 100% natural
    5. ¿Políticas de devolución? → 3 días hábiles con ticket
    
    💡 Escribe 'menu' para volver
    """
    await update.message.reply_text(faq_text, reply_markup=main_keyboard())

async def show_promociones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    promo_text = """
    🎯 **PROMOCIONES ACTUALES**
    
    🔥 OFERTA ESPECIAL:
    • Pack 12 botellas 600ml: 10% descuento
    • Combo 6 vidrio + 6 PET: $199
    • 🚚 Envío gratis en compras > $500
    
    💡 Escribe 'menu' para volver
    """
    await update.message.reply_text(promo_text, reply_markup=main_keyboard())

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 ¡Gracias por visitar!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")
    await update.message.reply_text("⚠️ Error. Escribe 'menu' para volver", reply_markup=main_keyboard())

def main():
    print("🚀 Iniciando Bot de Aguas de Lourdes...")
    
    app = Application.builder().token(TOKEN).build()
    
    # Conversación principal
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu)],
            SELECCION_PRODUCTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_seleccion_producto)],
            CANTIDAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_cantidad)],
            DATOS_ENVIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_datos_envio)],
            METODO_PAGO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_metodo_pago)],
            CONFIRMACION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confirmacion)],
            ESTADO_PEDIDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_estado_pedido)],
            CONTACTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contacto)],
            CONFIGURACION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_configuracion)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    app.add_handler(conv_handler)
    app.add_error_handler(error_handler)
    
    # Handler para detectar "pagar"
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)pagar'), handle_pagar))
    
    print("✅ Bot iniciado correctamente!")
    app.run_polling()

if __name__ == '__main__':
    main()
