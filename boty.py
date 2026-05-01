import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# ===================== SOZLAMALAR =====================
BOT_TOKEN = "8238326806:AAFoGsbFM9OrG45Nz-3S-s4WMYGNSxeaxus"
CHANNEL_USERNAME = "@UZEF_ONLIY"
ADMIN_CHANNEL_ID = -1003839474463

ADMINS = ["@xayd6rov"]

(ASK_PHOTO, ASK_PRICE, ASK_OBMEN, ASK_HOLAT, ASK_BATAFSIL) = range(5)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ===================== SAFE CALLBACK =====================
async def safe_answer(query):
    try:
        await query.answer()
    except:
        pass


# ===================== MENYU =====================
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Elon berish", callback_data="elon_berish")],
        [InlineKeyboardButton("👑 Adminlar", callback_data="adminlar")],
        [InlineKeyboardButton("💰 Elon narxi", callback_data="elon_narxi")],
    ])


# ===================== START =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏠 Asosiy menu:",
        reply_markup=main_menu_keyboard()
    )


# ===================== ADMIN =====================
async def adminlar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await safe_answer(query)

    text = "\n".join(ADMINS)

    await query.edit_message_text(
        f"👑 ADMINLAR:\n{text}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Orqaga", callback_data="orqaga")]
        ])
    )


# ===================== ELON NARX =====================
async def elon_narxi_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await safe_answer(query)

    await query.edit_message_text(
        "💰 Elon narxi: TEKIN",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Orqaga", callback_data="orqaga")]
        ])
    )


# ===================== ELON MENU =====================
async def elon_berish_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await safe_answer(query)

    await query.edit_message_text(
        "📢 Elon turi:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 Sotish eloni", callback_data="sotish_eloni")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="orqaga")]
        ])
    )


# ===================== ORQAGA =====================
async def orqaga_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await safe_answer(query)

    await query.edit_message_text("🏠 Menu:", reply_markup=main_menu_keyboard())


# ===================== SOTISH ELON =====================
async def sotish_eloni_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await safe_answer(query)

    context.user_data.clear()

    await query.edit_message_text("📸 Rasm yuboring:")
    return ASK_PHOTO


async def ask_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data["photo"] = update.message.photo[-1].file_id
    else:
        await update.message.reply_text("❗ Rasm yubor")
        return ASK_PHOTO

    await update.message.reply_text("💵 Narx yozing:")
    return ASK_PRICE


async def ask_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["price"] = update.message.text

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔵 Google va Konami Idga ulangan toza", callback_data="obmen_google"),
            InlineKeyboardButton("⚫ Ulanmagan", callback_data="obmen_none")
        ]
    ])

    await update.message.reply_text("🔐 Holat tanlang:", reply_markup=keyboard)
    return ASK_OBMEN


# ===================== HOLAT =====================
async def obmen_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await safe_answer(query)

    if query.data == "obmen_google":
        context.user_data["obmen"] = "🔵 Google ulangan"
    else:
        context.user_data["obmen"] = "⚫ Ulanmagan"

    await query.edit_message_text("📝 Batafsil yozing:")
    return ASK_HOLAT


async def ask_batafsil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["batafsil"] = update.message.text

    data = context.user_data

    caption = f"""
🔥 YANGI ELON

💰 Narx: {data['price']}
🔐 Status: {data['obmen']}
📝 {data['batafsil']}
"""

    try:
        if "photo" in data:
            await context.bot.send_photo(ADMIN_CHANNEL_ID, data["photo"], caption=caption)
        else:
            await context.bot.send_message(ADMIN_CHANNEL_ID, caption)

        await update.message.reply_text(
            "✅ Yuborildi",
            reply_markup=main_menu_keyboard()
        )

    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ Xatolik")

    return ConversationHandler.END


# ===================== MAIN =====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(sotish_eloni_start, pattern="^sotish_eloni$")],
        states={
            ASK_PHOTO: [MessageHandler(filters.PHOTO, ask_photo)],
            ASK_PRICE: [MessageHandler(filters.TEXT, ask_price)],
            ASK_OBMEN: [CallbackQueryHandler(obmen_callback)],
            ASK_HOLAT: [MessageHandler(filters.TEXT, ask_batafsil)],
        },
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)

    app.add_handler(CallbackQueryHandler(adminlar_callback, pattern="adminlar"))
    app.add_handler(CallbackQueryHandler(elon_narxi_callback, pattern="elon_narxi"))
    app.add_handler(CallbackQueryHandler(elon_berish_callback, pattern="elon_berish"))
    app.add_handler(CallbackQueryHandler(orqaga_callback, pattern="orqaga"))

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()