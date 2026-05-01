import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# ===================== SOZLAMALAR =====================
BOT_TOKEN = "8238326806:AAFoGsbFM9OrG45Nz-3S-s4WMYGNSxeaxus"
CHANNEL_USERNAME = "@UZEF_ONLIY"
ADMIN_CHANNEL_ID = -1003839474463  # Admin kanalingiz ID si (raqam bo'lishi kerak)
ADMINS = ["@xayd6rov"]

# Conversation states
(
    ASK_PHOTO, ASK_PRICE, ASK_OBMEN, ASK_HOLAT, ASK_BATAFSIL
) = range(5)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===================== OBUNA TEKSHIRISH =====================
async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# ===================== ASOSIY TUGMALAR =====================
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Elon berish", callback_data="elon_berish")],
        [InlineKeyboardButton("👑 Adminlar", callback_data="adminlar")],
        [InlineKeyboardButton("💰 Elon narxi", callback_data="elon_narxi")],
    ])

# ===================== /start =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    subscribed = await check_subscription(user_id, context)

    if subscribed:
        await update.message.reply_text(
            "✅ Raxmat, obuna tasdiqlandi!\n\nQuyidagi bo'limlardan birini tanlang:",
            reply_markup=main_menu_keyboard()
        )
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("✅ Tekshirish", callback_data="tekshirish")],
        ])
        await update.message.reply_text(
            f"⚠️ Botdan foydalanish uchun avval kanalga obuna bo'ling:\n{CHANNEL_USERNAME}",
            reply_markup=keyboard
        )

# ===================== TEKSHIRISH TUGMASI =====================
async def tekshirish_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    subscribed = await check_subscription(user_id, context)

    if subscribed:
        await query.edit_message_text(
            "✅ Raxmat, obuna tasdiqlandi!\n\nQuyidagi bo'limlardan birini tanlang:",
            reply_markup=main_menu_keyboard()
        )
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("✅ Tekshirish", callback_data="tekshirish")],
        ])
        await query.edit_message_text(
            f"❌ Siz hali obuna bo'lmagansiz!\n\nAvval kanalga obuna bo'ling:\n{CHANNEL_USERNAME}",
            reply_markup=keyboard
        )

# ===================== ADMINLAR =====================
async def adminlar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    admins_text = "\n".join([f"👤 {admin}" for admin in ADMINS])
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Orqaga", callback_data="orqaga")]
    ])
    await query.edit_message_text(
        f"👑 <b>Adminlar:</b>\n\n{admins_text}",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# ===================== ELON NARXI =====================
async def elon_narxi_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Orqaga", callback_data="orqaga")]
    ])
    await query.edit_message_text(
        "💰 <b>Elon narxi:</b>\n\n🎉 Hozircha <b>TEKIN!</b>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# ===================== ELON BERISH - MENU =====================
async def elon_berish_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Sotish eloni", callback_data="sotish_eloni")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="orqaga")],
    ])
    await query.edit_message_text(
        "📢 <b>Qanday elon joylashtiramiz?</b>\n\nElon turini tanlang:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# ===================== ORQAGA =====================
async def orqaga_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "✅ Asosiy menyu:\n\nQuyidagi bo'limlardan birini tanlang:",
        reply_markup=main_menu_keyboard()
    )

# ===================== SOTISH ELONI - CONVERSATION =====================
async def sotish_eloni_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.edit_message_text(
        "🛒 <b>Sotish eloni</b>\n\n📸 Akkaunt rasmini yuboring:",
        parse_mode="HTML"
    )
    return ASK_PHOTO

async def ask_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data["photo"] = update.message.photo[-1].file_id
    elif update.message.document:
        context.user_data["photo"] = update.message.document.file_id
    else:
        await update.message.reply_text("❗ Iltimos, rasm yuboring.")
        return ASK_PHOTO

    await update.message.reply_text("💵 Narxini yozing (masalan: 50$):")
    return ASK_PRICE

async def ask_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["price"] = update.message.text
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Ha", callback_data="obmen_ha"),
         InlineKeyboardButton("❌ Yo'q", callback_data="obmen_yoq")],
    ])
    await update.message.reply_text("🔄 Obmen bormmi?", reply_markup=keyboard)
    return ASK_OBMEN

async def obmen_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["obmen"] = "✅ Ha" if query.data == "obmen_ha" else "❌ Yo'q"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🟢 Yaxshi", callback_data="holat_yaxshi"),
         InlineKeyboardButton("🟡 O'rtacha", callback_data="holat_ortacha")],
        [InlineKeyboardButton("🔴 Yomon", callback_data="holat_yomon")],
    ])
    await query.edit_message_text("📊 Akkaunt holati qanday?", reply_markup=keyboard)
    return ASK_HOLAT

async def holat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    holat_map = {
        "holat_yaxshi": "🟢 Yaxshi",
        "holat_ortacha": "🟡 O'rtacha",
        "holat_yomon": "🔴 Yomon",
    }
    context.user_data["holat"] = holat_map.get(query.data, "Noma'lum")
    await query.edit_message_text("📝 Batafsil ma'lumot yozing (akkaunt haqida qo'shimcha):")
    return ASK_BATAFSIL

async def ask_batafsil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["batafsil"] = update.message.text
    data = context.user_data
    user = update.effective_user
    username = f"@{user.username}" if user.username else f"ID: {user.id}"

    caption = (
    f"🔥 <b>YANGI SOTISH ELONI</b>\n"
    f"━━━━━━━━━━━━━━━━━━\n\n"

    f"💰 <b>Narx:</b> <code>{data.get('price')}</code>\n"
    f"🔄 <b>Obmen:</b> {data.get('obmen')}\n"
    f"📊 <b>Holati:</b> {data.get('holat')}\n\n"

    f"📝 <b>Batafsil:</b>\n"
    f"{data.get('batafsil')}\n\n"

    f"━━━━━━━━━━━━━━━━━━\n"
    f"👤 <b>Sotuvchi:</b> {username}\n\n"

    f"🛡 <b>GARANT ADMINLAR:</b>\n"
    f"• @abdulbosit_3454\n"
    f"• @uzef_shop_admin\n\n"

    f"🤖 <b>Elon berish uchun bot:</b>\n"
    f"👉 @uzef_shop_bot\n\n"

    f"⚠️ <i>Ishonchli savdo uchun faqat garant orqali ishlang!</i>"
)

    try:
        if data.get("photo"):
            await context.bot.send_photo(
                chat_id=ADMIN_CHANNEL_ID,
                photo=data["photo"],
                caption=caption,
                parse_mode="HTML"
            )
        else:
            await context.bot.send_message(
                chat_id=ADMIN_CHANNEL_ID,
                text=caption,
                parse_mode="HTML"
            )
        await update.message.reply_text(
            "✅ <b>Elon yuklandi!</b>\n\nAsosiy menyuga qaytdingiz:",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Admin kanalga yuborishda xato: {e}")
        await update.message.reply_text(
            "❌ Xatolik yuz berdi. Admin kanal ID sini tekshiring.\n\nAsosiy menyu:",
            reply_markup=main_menu_keyboard()
        )

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

# ===================== MAIN =====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Conversation handler for sotish eloni
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(sotish_eloni_start, pattern="^sotish_eloni$")],
        states={
            ASK_PHOTO: [MessageHandler(filters.PHOTO | filters.Document.ALL, ask_photo)],
            ASK_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_price)],
            ASK_OBMEN: [CallbackQueryHandler(obmen_callback, pattern="^obmen_")],
            ASK_HOLAT: [CallbackQueryHandler(holat_callback, pattern="^holat_")],
            ASK_BATAFSIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_batafsil)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(tekshirish_callback, pattern="^tekshirish$"))
    app.add_handler(CallbackQueryHandler(adminlar_callback, pattern="^adminlar$"))
    app.add_handler(CallbackQueryHandler(elon_narxi_callback, pattern="^elon_narxi$"))
    app.add_handler(CallbackQueryHandler(elon_berish_callback, pattern="^elon_berish$"))
    app.add_handler(CallbackQueryHandler(orqaga_callback, pattern="^orqaga$"))

    print("✅ Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()