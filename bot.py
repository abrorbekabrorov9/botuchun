import os
import telebot
import logging
import random

# === BOT TOKEN (Railway Environment Variable dan) ===
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable topilmadi!")

bot = telebot.TeleBot(TOKEN)

# === ADMIN ID (sen o'zingni Telegram ID'ingni yoz) ===
ADMIN_ID = 7850048970   # buni o'z ID'ing bilan almashtir

# === LOGGING ===
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# === Foydalanuvchilar ro'yxati ===
users = set()

# === MENYU TUGMALARI ===
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📝 Ro'yxatdan o'tish", "▶️ Davom etish")
    return markup

def signal_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🍎 Signal olish", "🔙 Orqaga")
    return markup

# === /START BUYRUG'I ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    users.add(message.chat.id)  # foydalanuvchini ro'yxatga qo'shamiz

    welcome_text = (
        "👋 Hurmatli foydalanuvchi!\n\n"
        "Quyidagi tugmalardan foydalaning 👇\n\n"
        "❗️ Diqqat! Bot to'g'ri ishlashi uchun:\n"
        "1) Ro'yxatdan o'tish tugmasini bosing va LINEBET saytida ro'yxatdan o'ting.\n"
        "2) Promokod joyiga albatta: **FOYDA50** yozing.\n"
        "3) ID raqamingizni botga kiriting.\n\n"
        "⚠️ Aks holda bot sizga noto‘g‘ri signal ko‘rsatadi!\n\n"
        "📌 Ushbu bot faqat **LINEBET** uchun ishlaydi, iltimos Linebetdan foydalaning!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

# === MATNLI XABARLAR ===
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    if message.text == "📝 Ro'yxatdan o'tish":
        bot.send_message(
            message.chat.id,
            "📝 Ro'yxatdan o'tish uchun havolalar:\n\n"
            "👉 https://lb-aff.com/L?tag=d_4617949m_22611c_site&site=4617949&ad=22611&r=registration\n"
            "👉 https://lb-aff.com/L?tag=d_4617949m_66803c_apk1&site=4617949&ad=66803\n\n"
            "⚠️ Diqqat! Promokod joyiga albatta **FOYDA50** yozing. "
            "Aks holda bot sizga to‘g‘ri signal bermaydi!"
        )

    elif message.text == "▶️ Davom etish":
        msg = bot.send_message(message.chat.id, "🔑 ID raqamingizni kiriting:")
        bot.register_next_step_handler(msg, get_id)

    elif message.text == "🍎 Signal olish":
        random_number = random.randint(1, 5)
        bot.send_message(message.chat.id, f"🍎 Signal: {random_number}")

    elif message.text == "🔙 Orqaga":
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz.", reply_markup=main_menu())

# === ID OLIB SIGNAL MENYUGA O'TKAZISH ===
def get_id(message):
    user_id = message.text
    bot.send_message(
        message.chat.id,
        f"✅ ID qabul qilindi: {user_id}\n\n"
        "📡 Endi signal olish tugmasidan foydalanishingiz mumkin!",
        reply_markup=signal_menu()
    )

# === ADMIN UCHUN FOYDALANUVCHILAR SONINI KO'RISH ===
@bot.message_handler(commands=['users'])
def get_users_count(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, f"👥 Botdan foydalanganlar soni: {len(users)} ta")
    else:
        bot.send_message(message.chat.id, "⛔ Bu buyruq faqat admin uchun!")

# === BOTNI ISHGA TUSHURISH ===
if __name__ == "__main__":
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Botni ishga tushirishda xatolik yuz berdi: {e}")




