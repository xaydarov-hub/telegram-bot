import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# ===================== CONFIG =====================
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_CHANNEL_ID = -1003839474463

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# STATES
ASK_PHOTO, ASK_PRICE, ASK_STATUS, ASK_TEXT = range(4)

# ===================== MENU =====================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Elon berish", callback_data="elon")],
        [InlineKeyboardButton("👑 Adminlar", callback_data="admins")],
        [InlineKeyboardButton("💰 Narx", callback_data="price")]
    ])

# ===================== START =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏠 Asosiy menu:",
        reply_markup=main_menu()
    )

# ===================== CALLBACKS =====================
async def admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    await q.edit_message_text(
        "👑 Admin: @Abdulbosit_3454",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="back")]
        ])
    )

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    await q.edit_message_text(
        "💰 Elon narxi: TEKIN",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="back")]
        ])
    )

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("🏠 Menu:", reply_markup=main_menu())

# ===================== ELON START =====================
async def elon_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    context.user_data.clear()
    await q.edit_message_text("📸 Rasm yuboring:")
    return ASK_PHOTO

# ===================== PHOTO =====================
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data["photo"] = update.message.photo[-1].file_id
        await update.message.reply_text("💵 Narx yozing:")
        return ASK_PRICE

    await update.message.reply_text("❗ Rasm yuboring")
    return ASK_PHOTO

# ===================== PRICE =====================
async def price_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["price"] = update.message.text

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔵 Google + Konami ulangan", callback_data="ok"),
            InlineKeyboardButton("⚫ Ulanmagan", callback_data="no")
        ]
    ])

    await update.message.reply_text("🔐 Holatni tanlang:", reply_markup=keyboard)
    return ASK_STATUS

# ===================== STATUS =====================
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "ok":
        context.user_data["status"] = "🔵 Google + Konami ulangan"
    else:
        context.user_data["status"] = "⚫ Ulanmagan"

    await q.edit_message_text("📝 Batafsil yozing:")
    return ASK_TEXT

# ===================== FINAL =====================
async def final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["text"] = update.message.text
    data = context.user_data

    caption = f"""
🔥 YANGI ELON

💵 Narx: {data['price']}
🔐 Status: {data['status']}
📝 {data['text']}
"""

    try:
        if "photo" in data:
            await context.bot.send_photo(
                ADMIN_CHANNEL_ID,
                data["photo"],
                caption=caption
            )
        else:
            await context.bot.send_message(
                ADMIN_CHANNEL_ID,
                caption
            )

        await update.message.reply_text("✅ Yuborildi!", reply_markup=main_menu())

    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ Xatolik")

    return ConversationHandler.END

# ===================== CANCEL =====================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi", reply_markup=main_menu())
    return ConversationHandler.END

# ===================== MAIN =====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(elon_start, pattern="^elon$")],
        states={
            ASK_PHOTO: [MessageHandler(filters.PHOTO, photo)],
            ASK_PRICE: [MessageHandler(filters.TEXT, price_input)],
            ASK_STATUS: [CallbackQueryHandler(status)],
            ASK_TEXT: [MessageHandler(filters.TEXT, final)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=True
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)

    app.add_handler(CallbackQueryHandler(admins, pattern="admins"))
    app.add_handler(CallbackQueryHandler(price, pattern="price"))
    app.add_handler(CallbackQueryHandler(back, pattern="back"))

    print("Bot ishladi 🚀")
    app.run_polling()

# ===================== RUN =====================
if __name__ == "__main__":
    asyncio.run(main())