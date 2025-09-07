import telebot
import logging

# === BOT TOKEN ===
TOKEN = "7959935946:AAHbVDAMxCO-VjjZzkz50xrorvKpiga0QcI"
bot = telebot.TeleBot(TOKEN)

# === LOGGING sozlamalari ===
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# === MENYU TUGMALARI ===
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📝 Ro'yxatdan o'tish", "▶️ Davom etish")
    return markup

def signal_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.row("🔔 Signal olish", "🔙 Orqaga")
    return markup

# === /START BUYRUG'I ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 Hurmatli foydalanuvchi!\n\n"
        "Eslatma! Bot to'g'ri ishlashi uchun:\n"
        "1) 🟢 Vzlom ilovalarni yuklab oling\n"
        "2) Promokod: **FOYDA50**\n"
        "3) Hisobni to‘ldiring (200.000 so‘m yoki ko‘proq)\n"
        "4) ID raqamingizni botga yuboring\n"
        "5) Soxta ID yuborilsa signal ishlamaydi\n\n"
        "Quyidagi tugmalardan foydalaning 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

# === Matnli xabarlar ===
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    if message.text == "📝 Ro'yxatdan o'tish":
        bot.send_message(
            message.chat.id,
            "📝 Ro'yxatdan o'tish uchun havola:\n👉 https://lb-aff.com/L?tag=d_4617949m_22611c_site&site=4617949&ad=22611&r=registration"
        )

    elif message.text == "▶️ Davom etish":
        msg = bot.send_message(message.chat.id, "🔑 ID raqamingizni kiriting:")
        bot.register_next_step_handler(msg, get_id)

    elif message.text == "🔔 Signal olish":
        # Random signal olish logikasi
        pass

    elif message.text == "🔙 Orqaga":
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz.", reply_markup=main_menu())

# === ID OLIB, VAQT TANLASH ===
def get_id(message):
    user_id = message.text
    # vaqtni tanlash logikasi

def get_time(message):
    # vaqt tanlashni davom ettirish

# === BOTNI ISHGA TUSHURISH ===
try:
    bot.polling(none_stop=True)
except Exception as e:
    logger.error(f"Botni ishga tushirishda xatolik yuz berdi: {e}")
