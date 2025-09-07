import os
import telebot
import logging
import random

# === BOT TOKEN (Railway Environment Variable dan) ===
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable topilmadi!")

bot = telebot.TeleBot(TOKEN)

# === ADMIN ID ===
ADMIN_ID = 7850048970

# === LOGGING ===
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# === Foydalanuvchilarni saqlash ===
registered_users = set()
user_ids = {}

# === MENYU ===
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📝 Ro'yxatdan o'tish", "▶️ Davom etish")
    markup.row("🔔 Signal olish", "📊 Statistika")
    return markup

# === /START ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 Hurmatli foydalanuvchi!\n\n"
        "Quyidagi tugmalardan foydalaning 👇\n\n"
        "❗️ Diqqat! Bot to'g'ri ishlashi uchun (Linebet uchun ishlaydi):\n"
        "1) 📝 Ro'yxatdan o'tish tugmasini bosing va sayt orqali ro'yxatdan o'ting.\n"
        "2) Promokod joyiga albatta: **FOYDA50** yozing.\n"
        "3) ID raqamingizni botga kiriting.\n"
        "⚠️ Aks holda bot sizga noto‘g‘ri signal ko‘rsatadi!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

# === Matnli xabarlar ===
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = message.chat.id

    if message.text == "📝 Ro'yxatdan o'tish":
        bot.send_message(
            user_id,
            "📝 Ro'yxatdan o'tish uchun havolalar:\n"
            "👉 https://lb-aff.com/L?tag=d_4617949m_22611c_site&site=4617949&ad=22611&r=registration\n"
            "👉 https://lb-aff.com/L?tag=d_4617949m_66803c_apk1&site=4617949&ad=66803\n\n"
            "❗️ Diqqat! Promokod joyiga **FOYDA50** yozib ro‘yxatdan o‘ting.\n"
            "⚠️ Aks holda bot aniq signal ko‘rsatmaydi!"
        )

    elif message.text == "▶️ Davom etish":
        msg = bot.send_message(user_id, "🔑 ID raqamingizni kiriting:")
        bot.register_next_step_handler(msg, get_id)

    elif message.text == "🔔 Signal olish":
        if user_id in user_ids:
            random_number = random.randint(1, 5)
            bot.send_message(user_id, f"📡 Signal: 🍎 {random_number}")
        else:
            bot.send_message(user_id, "❌ Avval ID raqamingizni kiriting!")

    elif message.text == "📊 Statistika":
        if user_id == ADMIN_ID:
            bot.send_message(user_id, f"📊 Hozirgi foydalanuvchilar soni: {len(registered_users)} ta")
        else:
            bot.send_message(user_id, "❌ Bu bo‘lim faqat admin uchun!")

    elif message.text == "🔙 Orqaga":
        bot.send_message(user_id, "Asosiy menyuga qaytdingiz.", reply_markup=main_menu())

# === ID QABUL QILISH ===
def get_id(message):
    user_id = message.chat.id
    entered_id = message.text
    user_ids[user_id] = entered_id
    registered_users.add(user_id)
    bot.send_message(user_id, f"✅ ID qabul qilindi: {entered_id}\n\nEndi \"🔔 Signal olish\" tugmasidan foydalanishingiz mumkin!")

# === BOTNI ISHGA TUSHURISH ===
if __name__ == "__main__":
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Botni ishga tushirishda xatolik yuz berdi: {e}")





